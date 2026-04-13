from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.logger import utc_now_iso
from app.paths import STATE_DIR


PENDING_ACTIONS_FILE = STATE_DIR / "pending_actions.json"

def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def _load_state() -> dict[str, Any]:
    _ensure_state_dir()

    if not PENDING_ACTIONS_FILE.exists():
        return {"actions": {}}

    with PENDING_ACTIONS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(state: dict[str, Any]) -> None:
    _ensure_state_dir()

    with PENDING_ACTIONS_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def create_pending_action(
    action_type: str,
    payload: dict[str, Any],
    summary: str,
    session_id: str | None = None,
) -> str:
    state = _load_state()
    action_id = uuid.uuid4().hex[:8]

    state["actions"][action_id] = {
        "action_id": action_id,
        "action_type": action_type,
        "payload": payload,
        "summary": summary,
        "session_id": session_id,
        "status": "pending",
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "result": None,
        "error": None,
    }

    _save_state(state)
    return action_id


def get_action(action_id: str) -> dict[str, Any] | None:
    state = _load_state()
    return state.get("actions", {}).get(action_id)


def update_action(action_id: str, **changes: Any) -> dict[str, Any]:
    state = _load_state()
    action = state.get("actions", {}).get(action_id)

    if action is None:
        raise KeyError(f"존재하지 않는 action_id입니다: {action_id}")

    action.update(changes)
    action["updated_at"] = utc_now_iso()

    _save_state(state)
    return action


def mark_executed(action_id: str, result: str) -> dict[str, Any]:
    return update_action(
        action_id,
        status="executed",
        result=result,
        error=None,
    )


def mark_rejected(action_id: str) -> dict[str, Any]:
    return update_action(
        action_id,
        status="rejected",
        result=None,
        error=None,
    )


def mark_failed(action_id: str, error: str) -> dict[str, Any]:
    return update_action(
        action_id,
        status="failed",
        result=None,
        error=error,
    )


def list_pending_actions() -> list[dict[str, Any]]:
    state = _load_state()
    actions = state.get("actions", {})

    pending = [
        action
        for action in actions.values()
        if action.get("status") == "pending"
    ]
    pending.sort(key=lambda item: item.get("created_at", ""))
    return pending