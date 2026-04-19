from __future__ import annotations

import json
from typing import Any

from app.approvals import get_action
from app.conversation_state import SessionState
from app.model import create_response
from app.long_term_memory import format_memory_records, search_memory_records

RECENT_HISTORY_LIMIT = 8
COMPACT_THRESHOLD = 12
HISTORY_MESSAGE_CHAR_LIMIT = 2000
HISTORY_TOTAL_CHAR_LIMIT = 10000
SUMMARY_CONTEXT_CHAR_LIMIT = 3000
WORKSPACE_STATE_CONTEXT_CHAR_LIMIT = 3000
MEMORY_RECORD_CONTENT_CHAR_LIMIT = 1000
MEMORY_CONTEXT_CHAR_LIMIT = 8000
TRIM_MARKER = "\n...(model request view trimmed; original data preserved)"


def _trim_text_for_model(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    if max_chars <= 0:
        return ""

    marker = TRIM_MARKER
    if max_chars <= len(marker):
        return text[:max_chars]

    return text[: max_chars - len(marker)] + marker


def _trim_memory_records_for_context(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    trimmed_records: list[dict[str, Any]] = []

    for record in records:
        trimmed = dict(record)
        content = str(trimmed.get("content", ""))
        trimmed["content"] = _trim_text_for_model(
            content,
            MEMORY_RECORD_CONTENT_CHAR_LIMIT,
        )
        trimmed_records.append(trimmed)

    return trimmed_records


def build_recent_history_view(
    session_state: SessionState,
    limit_messages: int = RECENT_HISTORY_LIMIT,
    per_message_char_limit: int = HISTORY_MESSAGE_CHAR_LIMIT,
    total_char_limit: int = HISTORY_TOTAL_CHAR_LIMIT,
) -> list[dict[str, str]]:
    """Return a bounded model-request view without rewriting stored history."""
    raw_messages = session_state.get_recent_history(limit_messages=limit_messages)
    trimmed_messages = [
        {
            "role": message["role"],
            "content": _trim_text_for_model(
                message["content"],
                per_message_char_limit,
            ),
        }
        for message in raw_messages
        if message.get("role") in {"user", "assistant"}
    ]

    if total_char_limit <= 0:
        return []

    selected_reversed: list[dict[str, str]] = []
    used_chars = 0

    for message in reversed(trimmed_messages):
        content = message["content"]
        remaining = total_char_limit - used_chars
        if remaining <= 0:
            break

        if len(content) > remaining:
            if remaining < 200:
                break
            content = _trim_text_for_model(content, remaining)

        selected_reversed.append(
            {
                "role": message["role"],
                "content": content,
            }
        )
        used_chars += len(content)

    return list(reversed(selected_reversed))


def _parse_pending_approval(text: str) -> dict[str, str] | None:
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


def _format_records_for_summary(records: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for record in records:
        role = record.get("role", "")
        content = record.get("content", "").strip()
        if not content:
            continue

        if role == "user":
            label = "사용자"
        elif role == "assistant":
            label = "에이전트"
        else:
            label = role

        lines.append(f"[{label}] {content}")

    return "\n".join(lines)


def build_memory_context(
    session_state: SessionState,
    user_input: str,
    max_memory_notes: int = 5,
) -> str:
    summary = session_state.load_summary()
    workspace_state = session_state.load_workspace_state()
    relevant_memories = search_memory_records(user_input, max_results=max_memory_notes)

    compact_state = {
        key: value
        for key, value in workspace_state.items()
        if value not in (None, "", [], {})
    }

    parts: list[str] = []

    if summary:
        parts.append(
            "[세션 요약]\n"
            + _trim_text_for_model(summary, SUMMARY_CONTEXT_CHAR_LIMIT)
        )

    if compact_state:
        workspace_state_json = json.dumps(
            compact_state,
            ensure_ascii=False,
            indent=2,
        )
        parts.append(
            "[현재 작업 상태]\n"
            + _trim_text_for_model(
                workspace_state_json,
                WORKSPACE_STATE_CONTEXT_CHAR_LIMIT,
            )
        )

    if relevant_memories:
        trimmed_memories = _trim_memory_records_for_context(relevant_memories)
        parts.append(
            "[관련 장기 기억]\n"
            + format_memory_records(trimmed_memories)
        )

    return _trim_text_for_model(
        "\n\n".join(parts).strip(),
        MEMORY_CONTEXT_CHAR_LIMIT,
    )


def compact_history_if_needed(session_state: SessionState) -> None:
    records = session_state.read_history_records()

    if len(records) <= COMPACT_THRESHOLD:
        return

    old_records = records[:-RECENT_HISTORY_LIMIT]
    recent_records = records[-RECENT_HISTORY_LIMIT:]

    transcript = _format_records_for_summary(old_records)
    existing_summary = session_state.load_summary()

    messages = [
        {
            "role": "system",
            "content": (
                "너는 에이전트 세션 메모리 압축기다.\n"
                "아래 대화를 다음 턴에 이어가기 좋도록 간결한 한국어 메모로 요약하라.\n"
                "형식:\n"
                "## 현재 목표\n"
                "- ...\n"
                "## 중요한 사실\n"
                "- ...\n"
                "## 최근 작업/파일 상태\n"
                "- ...\n"
                "## 열린 참조\n"
                "- ...\n"
                "note에 없는 추측은 넣지 마라.\n"
                "경로, 파일명, 승인 결과, 마지막 작업 대상은 보존하라."
            ),
        },
        {
            "role": "user",
            "content": (
                f"[기존 요약]\n{existing_summary or '(없음)'}\n\n"
                f"[새로 압축할 대화]\n{transcript}"
            ),
        },
    ]

    try:
        response = create_response(messages=messages)
    except Exception:
        return

    summary = (response.choices[0].message.content or "").strip()

    if summary:
        session_state.save_summary(summary)
        session_state.overwrite_history(recent_records)


def update_workspace_state_from_trace(
    session_state: SessionState,
    trace_record: dict[str, Any],
) -> None:
    updates: dict[str, Any] = {}

    for step in trace_record.get("steps", []):
        tool_calls = step.get("tool_calls", [])
        tool_results = step.get("tool_results", [])

        for index, tool_call in enumerate(tool_calls):
            tool_name = tool_call.get("tool_name")
            parsed_arguments = tool_call.get("parsed_arguments") or {}
            result_text = ""
            if index < len(tool_results):
                result_text = tool_results[index].get("result", "")

            if tool_name in {"list_dir", "tree_view"}:
                updates["last_browsed_path"] = parsed_arguments.get("path", ".")
            elif tool_name == "read_file":
                updates["last_read_path"] = parsed_arguments.get("path")
            elif tool_name == "request_search_files":
                updates["last_search_query"] = parsed_arguments.get("query")
                updates["last_search_path"] = parsed_arguments.get("path", ".")
            elif tool_name == "request_create_file":
                updates["last_requested_create_path"] = parsed_arguments.get("path")
            elif tool_name == "request_write_file":
                updates["last_requested_write_path"] = parsed_arguments.get("path")
            elif tool_name == "request_replace_text_in_file":
                updates["last_requested_modify_path"] = parsed_arguments.get("path")
            elif tool_name == "request_delete_path":
                updates["last_requested_delete_path"] = parsed_arguments.get("path")

            pending = _parse_pending_approval(result_text)
            if pending is not None:
                updates["last_pending_action_id"] = pending.get("action_id")
                updates["last_pending_summary"] = pending.get("summary")
                updates["last_action_status"] = "awaiting_approval"

    if updates:
        session_state.update_workspace_state(**updates)


def update_workspace_state_from_approval(
    session_state: SessionState,
    action_id: str,
) -> None:
    action = get_action(action_id)
    if action is None:
        return

    action_type = action.get("action_type")
    payload = action.get("payload", {})
    status = action.get("status")

    updates: dict[str, Any] = {
        "last_action_id": action_id,
        "last_action_type": action_type,
        "last_action_status": status,
        "last_pending_action_id": None,
        "last_pending_summary": None,
    }

    if action_type == "write_file" and status == "executed":
        updates["last_written_path"] = payload.get("path")
        updates["last_created_path"] = payload.get("path")
        
    elif action_type == "create_file" and status == "executed":
        updates["last_created_path"] = payload.get("path")

    elif action_type == "replace_text_in_file" and status == "executed":
        updates["last_modified_path"] = payload.get("path")

    elif action_type == "delete_path" and status == "executed":
        updates["last_deleted_path"] = payload.get("path")

    elif action_type == "search_files" and status == "executed":
        updates["last_search_query"] = payload.get("query")
        updates["last_search_path"] = payload.get("path", ".")

    session_state.update_workspace_state(**updates)
