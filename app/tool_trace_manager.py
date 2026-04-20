from __future__ import annotations

import json
from typing import Any

from app.approvals import get_action
from app.conversation_state import SessionState
from app.logger import utc_now_iso


PLANNER_TOOL_NAME = "__planner__"


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


def _normalize_planner_tasks(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    tasks: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = " ".join(item.split()).strip()
        if cleaned:
            tasks.append(cleaned)
    return tasks


def _build_planner_log_entry(planner: dict[str, Any]) -> dict[str, Any]:
    used = bool(planner.get("used"))
    status = str(planner.get("status") or "unknown")
    tasks = _normalize_planner_tasks(planner.get("tasks"))

    if used and tasks:
        preview = f"계획 생성 완료 · {len(tasks)}단계"
    elif status == "skipped":
        preview = "계획 없이 직접 실행"
    elif status == "planned_single":
        preview = "단일 단계로 직접 실행"
    elif status == "fallback":
        preview = "계획 요약 없이 직접 실행"
    else:
        preview = f"planner 상태: {status}"

    raw = json.dumps(
        {
            "used": used,
            "status": status,
            "tasks": tasks,
        },
        ensure_ascii=False,
    )

    return {
        "timestamp": utc_now_iso(),
        "step_index": 0,
        "tool_name": PLANNER_TOOL_NAME,
        "arguments": {
            "used": used,
            "status": status,
            "tasks": tasks,
        },
        "result_preview": preview,
        "result_raw": raw,
    }


def _parse_pending_approval(raw_text: str) -> dict[str, Any] | None:
    if not raw_text.startswith("__PENDING_APPROVAL__"):
        return None

    data: dict[str, Any] = {}
    for line in raw_text.splitlines()[1:]:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

    if not data:
        return None

    return {
        "action_id": data.get("action_id"),
        "summary": data.get("summary"),
        "message": data.get("message"),
    }


def _pending_approval_status(raw_text: str) -> str | None:
    pending = _parse_pending_approval(raw_text)
    if pending is None:
        return None

    action_id = pending.get("action_id")
    if not action_id:
        return "processed_approval"

    action = get_action(str(action_id))
    status = action.get("status") if action else None
    if status == "pending":
        return "pending_approval"
    if status in {"executed", "rejected", "failed"}:
        return str(status)
    return "processed_approval"


def _classify_result_kind(raw_text: str) -> str:
    approval_status = _pending_approval_status(raw_text)
    if approval_status is not None:
        return approval_status
    if raw_text.strip().startswith("ERROR:"):
        return "error"
    return "ok"


def _parse_plan_summary(entry: dict[str, Any]) -> dict[str, Any]:
    arguments = entry.get("arguments")
    if not isinstance(arguments, dict):
        return {
            "used": False,
            "status": "unknown",
            "tasks": [],
        }

    return {
        "used": bool(arguments.get("used")),
        "status": str(arguments.get("status") or "unknown"),
        "tasks": _normalize_planner_tasks(arguments.get("tasks")),
    }


def _build_latest_execution(entry: dict[str, Any]) -> dict[str, Any]:
    raw_text = str(entry.get("result_raw", ""))
    return {
        "tool_name": str(entry.get("tool_name") or "unknown_tool"),
        "step_index": int(entry.get("step_index") or 0),
        "result_kind": _classify_result_kind(raw_text),
        "result_preview": str(entry.get("result_preview") or _safe_preview(raw_text)),
    }


def persist_tool_trace(session_state: SessionState, trace_record: dict[str, Any]) -> None:
    steps = trace_record.get("steps", [])
    planner = trace_record.get("planner")

    if isinstance(planner, dict):
        session_state.append_tool_log(_build_planner_log_entry(planner))

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
        "plan_summary": None,
        "latest_execution": None,
        "pending_approval": None,
    }

    for entry in reversed(logs):
        tool_name = entry.get("tool_name")
        raw = entry.get("result_raw", "")

        if tool_name == PLANNER_TOOL_NAME and panel["plan_summary"] is None:
            panel["plan_summary"] = _parse_plan_summary(entry)
            continue

        if tool_name != PLANNER_TOOL_NAME and panel["latest_execution"] is None:
            panel["latest_execution"] = _build_latest_execution(entry)
            pending = _parse_pending_approval(raw)
            if pending is not None and _pending_approval_status(raw) == "pending_approval":
                panel["pending_approval"] = pending

        if tool_name == "search_notes" and panel["last_note_search"] is None:
            panel["last_note_search"] = _parse_search_notes_result(raw)

        elif tool_name == "read_note" and panel["last_note_read"] is None:
            panel["last_note_read"] = _parse_read_text_result(raw)

        elif tool_name == "read_file" and panel["last_file_read"] is None:
            panel["last_file_read"] = _parse_read_text_result(raw)

    return panel
