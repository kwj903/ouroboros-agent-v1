from __future__ import annotations

from contextvars import ContextVar


_CURRENT_SESSION_ID: ContextVar[str] = ContextVar(
    "_CURRENT_SESSION_ID",
    default="default",
)


def set_current_session_id(session_id: str) -> None:
    _CURRENT_SESSION_ID.set(session_id)


def get_current_session_id() -> str:
    return _CURRENT_SESSION_ID.get()