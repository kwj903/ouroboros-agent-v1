from __future__ import annotations

import json
import re
from typing import Any

from app.logger import append_trace, utc_now_iso
from app.model import create_response
from app.tool_registry import TOOLS, TOOL_SCHEMAS


_EXPLICIT_PLANNING_PATTERNS = (
    r"계획\s*(을|를)?\s*(세워|짜|만들|정리)",
    r"단계별",
    r"작업\s*(을|를)?\s*(나눠|분해|쪼개)",
    r"태스크\s*(로|를)?\s*(나눠|분해|정리)",
    r"\b(step by step|make a plan|create a plan|break down|task list)\b",
)

_SEQUENCE_MARKERS = (
    "그 다음",
    "다음으로",
    "그리고 나서",
    "한 뒤",
    "한 다음",
    "후에",
    "이후",
    "읽고",
    "찾고",
    "분석하고",
    "분석해서",
    "검토하고",
    "검토해서",
    "수정하고",
    "수정해서",
    "작성하고",
    "작성해서",
    "정리하고",
    "정리해서",
    "저장하고",
    "저장해서",
    "실행하고",
    "테스트하고",
    " and then ",
    " then ",
    " after ",
    " before ",
)

_ACTION_CATEGORY_PATTERNS = (
    ("read", (r"읽", r"확인", r"살펴", r"조회", r"\b(read|inspect|check|list)\b")),
    ("search", (r"검색", r"찾", r"\b(search|find)\b")),
    ("analyze", (r"분석", r"검토", r"평가", r"파악", r"\b(analy[sz]e|review|audit)\b")),
    ("write", (r"작성", r"저장", r"생성", r"만들", r"추가", r"수정", r"변경", r"\b(write|save|create|update|edit|modify)\b")),
    ("delete", (r"삭제", r"제거", r"\b(delete|remove)\b")),
    ("test", (r"테스트", r"검증", r"빌드", r"실행", r"\b(test|verify|build|run)\b")),
    ("summarize", (r"요약", r"정리", r"문서화", r"\b(summari[sz]e|document)\b")),
)


def _normalize_planner_tasks(tasks: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for item in tasks:
        if not isinstance(item, str):
            continue

        cleaned = " ".join(item.split()).strip()
        if not cleaned or cleaned in seen:
            continue

        normalized.append(cleaned)
        seen.add(cleaned)

    return normalized


def _matches_any(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _count_action_categories(text: str) -> int:
    return sum(
        1
        for _, patterns in _ACTION_CATEGORY_PATTERNS
        if _matches_any(text, patterns)
    )


def _has_multiple_instruction_lines(user_input: str) -> bool:
    meaningful_lines = [
        line.strip(" \t-0123456789.)")
        for line in user_input.splitlines()
        if line.strip(" \t-0123456789.)")
    ]
    if len(meaningful_lines) < 2:
        return False
    return sum(1 for line in meaningful_lines if _count_action_categories(line) > 0) >= 2


def should_plan_request(user_input: str) -> bool:
    """복합/다단계 요청에서만 planner LLM 호출을 사용한다."""
    text = " ".join(user_input.split())
    if not text:
        return False

    if _matches_any(text, _EXPLICIT_PLANNING_PATTERNS):
        return True

    action_category_count = _count_action_categories(text)
    if _has_multiple_instruction_lines(user_input) and action_category_count >= 2:
        return True

    lower_text = f" {text.lower()} "
    sequence_marker_count = sum(1 for marker in _SEQUENCE_MARKERS if marker in lower_text)

    if sequence_marker_count >= 1 and action_category_count >= 2:
        return True
    if sequence_marker_count >= 2 and action_category_count >= 1:
        return True
    if action_category_count >= 3:
        return True
    if len(text) >= 120 and action_category_count >= 2:
        return True

    return False


def plan_tasks(
    user_input: str,
    memory_context: str | None = None,
) -> tuple[list[str], str]:
    """사용자의 요청을 분석해서 task list를 생성한다."""
    planning_prompt = """
너는 사용자의 복잡한 요청을 작은 실행 가능한 task들로 분해하는 planner다.

규칙:
1. 사용자의 요청을 분석해서 3-5개의 구체적인 task로 분해한다.
2. 각 task는 독립적으로 실행 가능해야 한다.
3. task는 순차적으로 실행되어야 한다 (이전 task의 결과가 다음에 필요할 수 있음).
4. 각 task는 "파일 읽기", "계산 수행", "메모리 검색" 등 구체적인 행동으로 시작한다.
5. 불필요한 task는 만들지 않는다.
6. 최종 출력은 JSON 배열로 task 리스트를 반환한다.

예시:
사용자: "프로젝트의 main.py 파일을 분석해서 함수 목록을 추출하고, 이를 문서로 저장해줘"

task 리스트:
["main.py 파일의 전체 내용을 읽는다", "코드에서 함수 정의들을 추출한다", "추출된 함수 목록을 functions.md 파일로 저장한다"]

응답 형식: ["task1", "task2", "task3"]
""".strip()

    messages = [
        {"role": "system", "content": planning_prompt},
    ]

    if memory_context:
        messages.append(
            {
                "role": "system",
                "content": f"메모리 컨텍스트: {memory_context}",
            }
        )

    messages.append({"role": "user", "content": user_input})

    response = create_response(messages=messages, tools=[])
    content = response.choices[0].message.content or ""

    try:
        tasks = json.loads(content.strip())
    except json.JSONDecodeError:
        tasks = None

    if isinstance(tasks, list) and all(isinstance(t, str) for t in tasks):
        normalized_tasks = _normalize_planner_tasks(tasks)
        if normalized_tasks:
            return normalized_tasks, "planned"
        return [f"사용자 요청 처리: {user_input}"], "invalid"

    # 파싱 실패 시 기본 task로 분해
    return [f"사용자 요청 처리: {user_input}"], "fallback"


def build_system_prompt(
    output_mode: str = "cli",
    response_language: str = "ko",
    interaction_mode: str = "cli",
) -> str:
    base = """
너는 도구를 사용할 수 있는 실용적인 AI 어시스턴트다.

공통 규칙:
1. 계산이 필요한 질문이면 calculator 툴을 사용한다.
2. 사용자의 로컬 notes 저장소에서 지식, 메모, 정리한 내용을 찾는 질문이면 search_notes 툴을 사용한다.
3. search_notes 결과만으로 충분하지 않으면 read_note 툴로 실제 파일 내용을 확인한 뒤 답한다.
4. 노트 기반 질문의 최종 답변은 tool 결과에서 확인된 내용만 사용한다.
5. tool 결과에 없는 사실을 일반 지식으로 보충하지 않는다.
6. WORKSPACE_ROOT 안의 현재 작업 디렉터리 이름, 절대경로를 확인할 때는 get_workspace_info를 사용한다.
7. WORKSPACE_ROOT 안의 디렉터리 구조를 볼 때는 list_dir 또는 tree_view를 사용한다.
8. WORKSPACE_ROOT 안의 파일 내용을 읽을 때는 read_file을 사용한다.
9. WORKSPACE_ROOT 안에서 파일 내용을 검색해야 할 때는 request_search_files를 사용한다.
10. request_ 로 시작하는 툴은 실제 실행이 아니라 승인 요청만 만든다.
11. 여러 파일/폴더 변경을 한 번에 처리하거나 하나의 승인으로 묶는 것이 자연스러우면 request_batch_operations를 우선 사용한다.
12. 단일 파일 생성이고 내용이 없으면 request_create_file을 사용한다.
13. 단일 파일 생성/덮어쓰기/append 처리가 필요하면 request_write_file을 사용한다.
14. 단일 파일의 특정 텍스트를 바꾸려면 request_replace_text_in_file을 사용한다.
15. 단일 파일 또는 폴더 삭제 요청은 request_delete_path를 사용한다.
16. 사용자가 파일이나 폴더를 만들어달라고만 했고 파일 내용은 명시하지 않았다면 내용을 추측해 쓰지 않는다.
17. README.md 같은 특별한 파일도 사용자가 초안이나 템플릿을 원한다고 명시하지 않으면 내용을 자동으로 넣지 않는다.
18. 세션을 넘어 유지해야 할 중요한 사실, 프로젝트 규칙, 반복적으로 유용한 결정사항, 사용자가 명시적으로 기억해달라고 한 내용은 save_memory_note를 사용할 수 있다.
19. 이전 세션의 선호, 과거 결정, 자주 쓰는 파일/규칙 등이 현재 질문에 중요하면 search_memory_notes를 사용할 수 있다.
20. 사용자가 장기 기억을 보여달라고 하면 list_recent_memory_notes 또는 search_memory_notes를 사용할 수 있다.
21. 사용자가 특정 장기 기억을 수정하거나 삭제해달라고 하면 update_memory_note, delete_memory_note를 사용할 수 있다.
22. 사소하거나 일시적인 정보는 장기 기억에 저장하지 않는다.
23. 장기 기억은 tool 결과로 확인된 내용 또는 사용자가 직접 말한 안정적인 정보만 저장한다.
24. 장기 기억 후보는 자동 저장하지 말고, 사용자가 확인 후 저장하는 흐름을 우선한다.
25. 복잡한 다단계 작업은 먼저 전체 계획을 세우고 단계별로 실행한다.
26. 각 단계가 끝나면 결과를 확인하고 다음 단계로 진행한다.
27. 추론이 필요한 경우에는 추론이라고 짧게 밝힌다.
    """.strip()

    if interaction_mode == "cli":
        interaction_rules = """
상호작용 규칙:
1. request_ 툴이 action_id를 반환하면 작업이 끝난 것처럼 말하지 않는다.
2. 승인 전에는 수정, 삭제, 검색이 실제 수행되었다고 말하면 안 된다.
3. 승인 필요 작업이면 approve <action_id> 또는 reject <action_id> 로 처리하라고 안내한다.
4. 승인 후에는 실제 수행된 결과를 알려준다.
""".strip()
    elif interaction_mode == "web":
        interaction_rules = """
상호작용 규칙:
1. request_ 툴이 action_id를 반환하면 작업이 끝난 것처럼 말하지 않는다.
2. 승인 전에는 수정, 삭제, 검색이 실제 수행되었다고 말하면 안 된다.
3. 승인 필요 작업이면 action_id와 요청 내용을 알려주고, 웹 UI 또는 approvals API로 승인/거부를 처리해야 한다고 안내한다.
4. CLI 명령어 y/n, approve, reject는 언급하지 않는다.
5. 승인 후에는 실제 수행된 결과를 알려준다.
""".strip()
    else:
        raise ValueError(f"지원하지 않는 interaction_mode입니다: {interaction_mode}")

    if response_language == "ko":
        language_rules = """
언어 규칙:
1. 최종 답변은 항상 한국어로 작성한다.
2. 사용자가 한국어로 질문하면 영어로 바꾸지 않는다.
3. 파일명, 경로, 코드, 라이브러리명, 고유명사만 필요할 때 원문 영어를 유지한다.
4. 노트 원문에 영어 용어가 있어도 설명은 한국어로 한다.
""".strip()
    elif response_language == "en":
        language_rules = """
Language rules:
1. Always answer in English.
2. Keep filenames, paths, code, and proper nouns as-is.
""".strip()
    else:
        raise ValueError(f"지원하지 않는 response_language입니다: {response_language}")

    if output_mode == "cli":
        mode_rules = """
출력 규칙:
1. CLI에서 읽기 쉽게 평문으로 답한다.
2. 마크다운 표, 굵게 표시, 인라인 코드, 코드 블록, LaTeX 수식 표기는 사용하지 않는다.
3. 필요한 경우 줄바꿈과 하이픈 목록 정도만 사용한다.
""".strip()
    elif output_mode == "markdown":
        mode_rules = """
출력 규칙:
1. 최종 답변은 읽기 좋은 Markdown으로 작성한다.
2. 필요하면 제목(##), 목록(-), 인라인 코드(`code`), 코드 블록을 사용할 수 있다.
3. 과한 꾸밈은 피하고, 간결하고 보기 좋게 정리한다.
4. 노트 기반 답변이면 가능하면 다음 순서를 따른다:
   - 제목
   - 출처 파일
   - 핵심 내용
   - 필요시 추가 설명
""".strip()
    else:
        raise ValueError(f"지원하지 않는 output_mode입니다: {output_mode}")

    return f"{base}\n\n{interaction_rules}\n\n{language_rules}\n\n{mode_rules}"


def _debug_print(enabled: bool, label: str, content: Any = "") -> None:
    if not enabled:
        return

    print(f"\n[DEBUG] {label}")
    if content != "":
        print(content)


def _safe_json_dumps(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception:
        return str(data)


def _normalize_cli_text(text: str) -> str:
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = re.sub(r"\\\((.*?)\\\)", r"\1", text)
    text = re.sub(r"\\\[(.*?)\\\]", r"\1", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _normalize_markdown_text(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _postprocess_output(text: str, output_mode: str) -> str:
    if output_mode == "cli":
        return _normalize_cli_text(text)
    if output_mode == "markdown":
        return _normalize_markdown_text(text)
    return text.strip()


def _extract_pending_approval(text: str) -> dict[str, str] | None:
    if not text.startswith("__PENDING_APPROVAL__"):
        return None

    data: dict[str, str] = {}
    for line in text.splitlines()[1:]:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    if "action_id" not in data:
        return None

    return data


def _format_pending_approval_message(
    data: dict[str, str],
    output_mode: str,
    interaction_mode: str = "cli",
) -> str:
    action_id = data.get("action_id", "")
    summary = data.get("summary", "")
    message = data.get("message", "이 작업은 사용자 승인이 필요합니다.")

    if interaction_mode == "web":
        if output_mode == "markdown":
            return (
                f"## 승인 필요\n\n"
                f"- action_id: `{action_id}`\n"
                f"- 요청 내용: {summary}\n"
                f"- 안내: {message}\n\n"
                f"웹 UI 또는 approvals API로 승인/거부를 진행하세요."
            )
        return (
            f"승인 필요\n"
            f"action_id: {action_id}\n"
            f"요청 내용: {summary}\n"
            f"안내: {message}\n"
            f"웹 UI 또는 approvals API로 승인/거부를 진행하세요."
        )

    if output_mode == "markdown":
        return (
            f"## 승인 필요\n\n"
            f"- action_id: `{action_id}`\n"
            f"- 요청 내용: {summary}\n"
            f"- 안내: {message}\n\n"
            f"CLI에서는 `approve {action_id}` / `reject {action_id}` 또는 y/n으로 처리할 수 있습니다."
        )

    return (
        f"승인 필요\n"
        f"action_id: {action_id}\n"
        f"요청 내용: {summary}\n"
        f"안내: {message}\n"
        f"CLI에서 y/n 또는 approve/reject로 처리하세요."
    )


def run_agent(
    user_input: str,
    max_steps: int = 5,
    debug: bool = False,
    output_mode: str = "cli",
    response_language: str = "ko",
    return_trace: bool = False,
    chat_history: list[dict[str, str]] | None = None,
    memory_context: str | None = None,
    interaction_mode: str = "cli",
) -> str | tuple[str, dict[str, Any]]:
    system_prompt = build_system_prompt(
        output_mode=output_mode,
        response_language=response_language,
        interaction_mode=interaction_mode,
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
    ]

    if memory_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "아래는 이전 대화와 작업 상태를 압축한 메모리다.\n"
                    "필요한 경우에만 참고하고, 현재 사용자 요청을 우선하라.\n\n"
                    f"{memory_context}"
                ),
            }
        )

    if chat_history:
        messages.extend(chat_history)

    messages.append({"role": "user", "content": user_input})

    # Planning 단계: 복잡한 요청만 task로 분해한다.
    if should_plan_request(user_input):
        tasks, planner_status = plan_tasks(user_input, memory_context)
    else:
        tasks, planner_status = [], "skipped"

    planner_used = planner_status == "planned" and len(tasks) > 1
    if planner_status == "planned" and not planner_used:
        planner_status = "planned_single"

    if planner_used:
        # 다단계 작업이면 task 리스트를 시스템 메시지에 추가
        task_list_text = "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
        messages.append({
            "role": "system",
            "content": f"이 요청을 다음과 같은 단계로 분해했습니다:\n{task_list_text}\n\n단계별로 순차적으로 실행하세요.",
        })

    trace_record: dict[str, Any] = {
        "timestamp": utc_now_iso(),
        "user_input": user_input,
        "output_mode": output_mode,
        "response_language": response_language,
        "max_steps": max_steps,
        "planner": {
            "used": planner_used,
            "status": planner_status,
            "tasks": tasks,
        },
        "tasks": tasks,
        "status": "running",
        "steps": [],
        "final_answer": None,
        "error": None,
    }

    _debug_print(debug, "OUTPUT MODE", output_mode)
    _debug_print(debug, "RESPONSE LANGUAGE", response_language)
    _debug_print(debug, "USER INPUT", user_input)

    try:
        for step in range(1, max_steps + 1):
            _debug_print(debug, f"STEP {step}", "모델 호출 시작")

            response = create_response(messages=messages, tools=TOOL_SCHEMAS)
            message = response.choices[0].message

            step_record: dict[str, Any] = {
                "step": step,
                "model_raw_content": message.content or "",
                "tool_calls": [],
                "tool_results": [],
            }

            _debug_print(debug, "MODEL RAW CONTENT", message.content or "(no content)")

            if not message.tool_calls:
                content = _postprocess_output((message.content or "").strip(), output_mode)
                trace_record["status"] = "completed"
                trace_record["final_answer"] = content
                trace_record["steps"].append(step_record)

                _debug_print(debug, "FINAL ANSWER", content)
                append_trace(trace_record)

                if return_trace:
                    return content, trace_record
                return content

            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [],
            }

            for tool_call in message.tool_calls:
                assistant_message["tool_calls"].append(
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                )

            messages.append(assistant_message)

            _debug_print(debug, "TOOL CALL COUNT", len(message.tool_calls))

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                raw_arguments = tool_call.function.arguments

                tool_call_record: dict[str, Any] = {
                    "tool_name": tool_name,
                    "raw_arguments": raw_arguments,
                    "parsed_arguments": None,
                }

                _debug_print(debug, "TOOL SELECTED", tool_name)
                _debug_print(debug, "TOOL RAW ARGS", raw_arguments)

                try:
                    arguments = json.loads(raw_arguments)
                    tool_call_record["parsed_arguments"] = arguments
                    _debug_print(debug, "TOOL PARSED ARGS", _safe_json_dumps(arguments))
                except json.JSONDecodeError:
                    tool_result = "ERROR: tool arguments가 올바른 JSON이 아닙니다."
                    tool_call_record["error"] = tool_result
                    _debug_print(debug, "TOOL ARG PARSE ERROR", tool_result)
                else:
                    tool_func = TOOLS.get(tool_name)

                    if tool_func is None:
                        tool_result = f"ERROR: 알 수 없는 툴입니다: {tool_name}"
                        tool_call_record["error"] = tool_result
                        _debug_print(debug, "TOOL LOOKUP ERROR", tool_result)
                    else:
                        try:
                            tool_result = tool_func(**arguments)
                        except Exception as e:
                            tool_result = f"ERROR: 툴 실행 중 예외 발생: {e}"
                            tool_call_record["error"] = tool_result
                            _debug_print(debug, "TOOL EXEC ERROR", tool_result)
                        else:
                            _debug_print(debug, "TOOL RESULT", tool_result)

                step_record["tool_calls"].append(tool_call_record)
                step_record["tool_results"].append(
                    {
                        "tool_name": tool_name,
                        "result": tool_result,
                    }
                )

                pending_data = _extract_pending_approval(tool_result)
                if pending_data is not None:
                    trace_record["steps"].append(step_record)

                    final_message = _format_pending_approval_message(
                        pending_data,
                        output_mode=output_mode,
                        interaction_mode=interaction_mode,
                    )
                    trace_record["status"] = "awaiting_approval"
                    trace_record["final_answer"] = final_message

                    _debug_print(debug, "PENDING APPROVAL", final_message)
                    append_trace(trace_record)

                    if return_trace:
                        return final_message, trace_record
                    return final_message

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                )

            trace_record["steps"].append(step_record)
            _debug_print(debug, f"STEP {step} END", "툴 결과를 모델에 다시 전달함")

        timeout_message = "에이전트가 제한된 step 수 안에 답을 끝내지 못했습니다."
        trace_record["status"] = "max_steps_reached"
        trace_record["final_answer"] = timeout_message

        _debug_print(debug, "MAX STEPS REACHED", timeout_message)
        append_trace(trace_record)
        if return_trace:
            return timeout_message, trace_record
        return timeout_message

    except Exception as e:
        error_message = f"에이전트 실행 중 예외 발생: {e}"
        trace_record["status"] = "failed"
        trace_record["error"] = str(e)

        _debug_print(debug, "AGENT ERROR", error_message)
        append_trace(trace_record)
        if return_trace:
            return error_message, trace_record
        return error_message
