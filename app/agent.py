from __future__ import annotations

import json
import re
from typing import Any

from app.logger import append_trace, utc_now_iso
from app.model import create_response
from app.tool_registry import TOOLS, TOOL_SCHEMAS


def build_system_prompt(
    output_mode: str = "cli",
    response_language: str = "ko",
) -> str:
    base = """
너는 도구를 사용할 수 있는 실용적인 AI 어시스턴트다.

공통 규칙:
1. 계산이 필요한 질문이면 calculator 툴을 사용한다.
2. 사용자의 로컬 노트, 메모, 정리한 내용, 기록한 지식을 찾는 질문이면 search_notes 툴을 사용한다.
3. search_notes 결과에서 적절한 파일을 찾았고, 사용자가 자세한 설명, 요약, 내용 확인을 원하면 read_note 툴로 그 파일을 실제로 읽는다.
4. 계산이 필요 없고 노트 검색도 필요 없으면 바로 자연스럽게 답한다.
5. 노트 기반 질문의 최종 답변은 tool 결과에서 확인된 내용만 사용한다.
6. tool 결과에 없는 사실을 일반 지식으로 보충하지 않는다.
7. search_notes 결과만으로 충분하지 않으면 성급히 답하지 말고 read_note를 사용해 확인한 뒤 답한다.
8. 최종 답변에서는 파일명과 핵심 내용을 짧고 분명하게 정리한다.
9. 추론이 필요한 경우에는 추론이라고 짧게 밝힌다.
""".strip()

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

    return f"{base}\n\n{language_rules}\n\n{mode_rules}"


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


def run_agent(
    user_input: str,
    max_steps: int = 5,
    debug: bool = False,
    output_mode: str = "cli",
    response_language: str = "ko",
    return_trace: bool = False,
) -> str | tuple[str, dict[str, Any]]:
    system_prompt = build_system_prompt(
        output_mode=output_mode,
        response_language=response_language,
    )

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    trace_record: dict[str, Any] = {
        "timestamp": utc_now_iso(),
        "user_input": user_input,
        "output_mode": output_mode,
        "response_language": response_language,
        "max_steps": max_steps,
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