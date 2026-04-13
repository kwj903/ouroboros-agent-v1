from __future__ import annotations

from typing import Any

from app.conversation_state import SessionState
from app.logger import utc_now_iso


def _safe_preview(value: Any, max_length: int = 400) -> str:
    text = str(value)
    text = " ".join(text.split())
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def _extract_result_text(tool_result: Any) -> str:
    if isinstance(tool_result, dict):
        if "result" in tool_result:
            return str(tool_result["result"])
        return str(tool_result)
    return str(tool_result)


def persist_tool_trace(session_state: SessionState, trace_record: dict[str, Any]) -> None:
    steps = trace_record.get("steps", [])

    for step_index, step in enumerate(steps, start=1):
        tool_calls = step.get("tool_calls", [])
        tool_results = step.get("tool_results", [])

        for idx, tool_call in enumerate(tool_calls):
            result_obj = tool_results[idx] if idx < len(tool_results) else {}
            tool_name = (
                tool_call.get("tool_name")
                or tool_call.get("name")
                or "unknown_tool"
            )
            parsed_arguments = (
                tool_call.get("parsed_arguments")
                or tool_call.get("arguments")
                or {}
            )
            raw_result = _extract_result_text(result_obj)

            entry = {
                "timestamp": utc_now_iso(),
                "step_index": step_index,
                "tool_name": tool_name,
                "arguments": parsed_arguments,
                "result_preview": _safe_preview(raw_result),
                "result_raw": raw_result,
            }
            session_state.append_tool_log(entry)


def _parse_search_notes_result(raw_text: str) -> dict[str, Any]:
    lines = raw_text.splitlines()
    items: list[dict[str, Any]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit():
            continue

        # 예시:
        # 1. 파일: notes/rag_intro.md | 점수: 3 | 내용 미리보기: ...
        item: dict[str, Any] = {"raw": stripped}

        if "파일:" in stripped:
            try:
                file_part = stripped.split("파일:", 1)[1].split("|", 1)[0].strip()
                item["path"] = file_part
            except Exception:
                pass

        if "점수:" in stripped:
            try:
                score_part = stripped.split("점수:", 1)[1].split("|", 1)[0].strip()
                item["score"] = score_part
            except Exception:
                pass

        if "내용 미리보기:" in stripped:
            try:
                preview_part = stripped.split("내용 미리보기:", 1)[1].strip()
                item["preview"] = preview_part
            except Exception:
                pass

        items.append(item)

    query = None
    for line in lines:
        if line.startswith("검색어:"):
            query = line.split(":", 1)[1].strip()
            break

    return {
        "query": query,
        "items": items,
        "raw": raw_text,
    }


def _parse_read_text_result(raw_text: str) -> dict[str, Any]:
    # 예시:
    # 파일: /path/to/file
    # 전체 내용:
    # ...
    path = None
    content = raw_text

    lines = raw_text.splitlines()
    if lines and lines[0].startswith("파일:"):
        path = lines[0].split(":", 1)[1].strip()

    if "전체 내용:" in raw_text:
        content = raw_text.split("전체 내용:", 1)[1].strip()
    elif "내용:" in raw_text:
        content = raw_text.split("내용:", 1)[1].strip()

    return {
        "path": path,
        "content_preview": _safe_preview(content, max_length=800),
        "raw": raw_text,
    }


def build_tool_panel(session_state: SessionState) -> dict[str, Any]:
    logs = session_state.load_tool_logs(limit=100)

    panel: dict[str, Any] = {
        "last_note_search": None,
        "last_note_read": None,
        "last_file_read": None,
    }

    for entry in reversed(logs):
        tool_name = entry.get("tool_name")
        raw = entry.get("result_raw", "")

        if tool_name == "search_notes" and panel["last_note_search"] is None:
            panel["last_note_search"] = _parse_search_notes_result(raw)

        elif tool_name == "read_note" and panel["last_note_read"] is None:
            panel["last_note_read"] = _parse_read_text_result(raw)

        elif tool_name == "read_file" and panel["last_file_read"] is None:
            panel["last_file_read"] = _parse_read_text_result(raw)

        if all(panel.values()):
            break

    return panel