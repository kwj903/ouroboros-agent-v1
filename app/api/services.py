from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from app.agent import run_agent
from app.approvals import get_action, list_pending_actions
from app.conversation_state import (
    SessionState,
    create_new_session,
    delete_session_by_id,
    list_sessions,
    rename_session_by_id,
)
from app.long_term_memory import (
    accept_memory_suggestion,
    add_memory_note,
    delete_memory_note,
    dismiss_memory_suggestion,
    format_memory_suggestions,
    list_memory_suggestions,
    list_recent_memory_notes,
    search_memory_records,
    update_memory_note,
)
from app.memory_manager import (
    build_recent_history_view,
    build_memory_context,
    compact_history_if_needed,
    update_workspace_state_from_approval,
    update_workspace_state_from_trace,
)
from app.runtime_context import set_current_session_id
from app.settings import AUTO_MEMORY_SUGGESTIONS
from app.tools.workspace_tools import execute_pending_action, reject_pending_action
from app.tool_trace_manager import build_tool_panel, persist_tool_trace


def _extract_action_id_from_answer(answer: str) -> str | None:
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("action_id:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _parse_pending_approval_payload(text: str) -> dict[str, str] | None:
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


def _extract_pending_approval_from_trace(
    trace_record: dict[str, Any],
) -> dict[str, str] | None:
    for step in reversed(trace_record.get("steps", [])):
        for tool_result in reversed(step.get("tool_results", [])):
            raw_result = tool_result.get("result", "")
            pending = _parse_pending_approval_payload(raw_result)
            if pending is not None:
                return pending
    return None


def _is_action_required(status: str, action_id: str | None) -> bool:
    return status == "awaiting_approval" and action_id is not None


def _extract_action_summary(answer: str) -> str | None:
    for line in answer.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("요청 내용:"):
            return stripped.split(":", 1)[1].strip()
    return None


def _is_action_required(status: str, action_id: str | None) -> bool:
    return status == "awaiting_approval" and action_id is not None


def _maybe_generate_memory_suggestions(
    *,
    user_input: str,
    answer: str,
    trace_record: dict[str, Any],
    session_id: str,
) -> list[dict[str, Any]]:
    if not AUTO_MEMORY_SUGGESTIONS:
        return []

    from app.long_term_memory import generate_memory_suggestions

    return generate_memory_suggestions(
        user_input=user_input,
        answer=answer,
        trace_record=trace_record,
        session_id=session_id,
    )


def run_chat_turn(
    *,
    message: str,
    session_id: str | None,
    output_mode: str,
    response_language: str,
) -> dict[str, Any]:
    session_state = SessionState(session_id=session_id) if session_id else create_new_session()
    set_current_session_id(session_state.session_id)

    recent_history = build_recent_history_view(session_state)
    memory_context = build_memory_context(
        session_state,
        user_input=message,
    )

    answer, trace_record = run_agent(
        message,
        debug=False,
        output_mode=output_mode,
        response_language=response_language,
        return_trace=True,
        chat_history=recent_history,
        memory_context=memory_context,
        interaction_mode="web",
    )

    session_state.append_history("user", message)
    session_state.append_history("assistant", answer)
    update_workspace_state_from_trace(session_state, trace_record)
    persist_tool_trace(session_state, trace_record)

    new_suggestions = _maybe_generate_memory_suggestions(
        user_input=message,
        answer=answer,
        trace_record=trace_record,
        session_id=session_state.session_id,
    )

    compact_history_if_needed(session_state)

    status = trace_record.get("status", "completed")
    pending = _extract_pending_approval_from_trace(trace_record)

    action_id = pending.get("action_id") if pending else None
    action_summary = pending.get("summary") if pending else None

    return {
        "session_id": session_state.session_id,
        "answer": answer,
        "status": status,
        "action_id": action_id,
        "action_required": _is_action_required(status, action_id),
        "action_summary": action_summary,
        "suggestions_created": len(new_suggestions),
    }


def list_sessions_api() -> list[dict[str, Any]]:
    return list_sessions()


def create_session_api() -> dict[str, Any]:
    session = create_new_session()
    meta = session.get_meta()
    return {
        "session_id": session.session_id,
        "title": meta.get("title", "(new session)"),
    }


def rename_session_api(session_id: str, title: str) -> dict[str, Any]:
    updated_title = rename_session_by_id(session_id, title)
    if updated_title is None:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "session_id": session_id,
        "title": updated_title,
    }


def delete_session_api(session_id: str) -> dict[str, Any]:
    deleted = delete_session_by_id(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="session not found")

    return {
        "deleted": True,
        "session_id": session_id,
    }


def list_memories_api(limit: int = 10) -> list[dict[str, Any]]:
    return list_recent_memory_notes(limit=limit)


def search_memories_api(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    return search_memory_records(query, max_results=max_results)


def create_memory_api(
    *,
    content: str,
    tags: list[str],
    importance: int,
    note_type: str,
    source_session_id: str | None,
) -> dict[str, Any]:
    return add_memory_note(
        content=content,
        tags=tags,
        importance=importance,
        note_type=note_type,
        source_session_id=source_session_id,
    )


def update_memory_api(
    *,
    memory_id: str,
    new_content: str,
    new_tags: list[str] | None,
    new_importance: int | None,
    new_note_type: str | None,
) -> dict[str, Any]:
    updated = update_memory_note(
        memory_id=memory_id,
        new_content=new_content,
        new_tags=new_tags,
        new_importance=new_importance,
        new_note_type=new_note_type,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="memory not found")
    return updated


def delete_memory_api(memory_id: str) -> dict[str, Any]:
    deleted = delete_memory_note(memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="memory not found")
    return {
        "deleted": True,
        "memory_id": memory_id,
    }


def list_memory_suggestions_api() -> list[dict[str, Any]]:
    if not AUTO_MEMORY_SUGGESTIONS:
        return []

    return list_memory_suggestions()


def save_memory_suggestion_api(choice: str) -> dict[str, Any]:
    record = accept_memory_suggestion(choice)
    if record is None:
        raise HTTPException(status_code=404, detail="suggestion not found")
    return record


def drop_memory_suggestion_api(choice: str) -> dict[str, Any]:
    suggestion = dismiss_memory_suggestion(choice)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="suggestion not found")
    return {
        "dismissed": True,
        "suggestion_id": suggestion["suggestion_id"],
        "content": suggestion["content"],
    }


def list_approvals_api() -> list[dict[str, Any]]:
    return list_pending_actions()


def approve_action_api(action_id: str) -> dict[str, Any]:
    action = get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="action not found")

    result = execute_pending_action(action_id)

    target_session_id = action.get("session_id")
    if not target_session_id:
        raise HTTPException(
            status_code=500,
            detail=f"action {action_id} is missing session_id",
        )

    target_session = SessionState(session_id=target_session_id)
    target_session.append_history("assistant", f"승인 처리 결과: {result}")
    update_workspace_state_from_approval(target_session, action_id)
    compact_history_if_needed(target_session)

    return {
        "action_id": action_id,
        "session_id": target_session_id,
        "result": result,
        "status": get_action(action_id).get("status"),
    }


def reject_action_api(action_id: str) -> dict[str, Any]:
    action = get_action(action_id)
    if action is None:
        raise HTTPException(status_code=404, detail="action not found")

    result = reject_pending_action(action_id)

    target_session_id = action.get("session_id") or "default"
    target_session = SessionState(session_id=target_session_id)
    target_session.append_history("assistant", f"승인 처리 결과: {result}")
    update_workspace_state_from_approval(target_session, action_id)
    compact_history_if_needed(target_session)

    return {
        "action_id": action_id,
        "session_id": target_session_id,
        "result": result,
        "status": get_action(action_id).get("status"),
    }
    
    
def get_session_history_api(session_id: str) -> list[dict[str, str]]:
    session = SessionState(session_id=session_id)
    records = session.read_history_records()

    messages: list[dict[str, str]] = []
    for record in records:
        role = record.get("role")
        content = record.get("content", "")

        if role not in {"user", "assistant"}:
            continue

        messages.append(
            {
                "role": role,
                "content": content,
            }
        )

    return messages


def get_session_workspace_state_api(session_id: str) -> dict[str, Any]:
    session = SessionState(session_id=session_id)
    return session.load_workspace_state()


def get_session_tool_logs_api(session_id: str, limit: int = 50) -> list[dict[str, Any]]:
    session = SessionState(session_id=session_id)
    return session.load_tool_logs(limit=limit)


def get_session_tool_panel_api(session_id: str) -> dict[str, Any]:
    session = SessionState(session_id=session_id)
    return build_tool_panel(session)
