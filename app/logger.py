from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.paths import LOGS_DIR


TRACE_FILE = LOGS_DIR / "agent_trace.jsonl"


def ensure_log_dir() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def append_trace(record: dict[str, Any]) -> None:
    ensure_log_dir()

    with TRACE_FILE.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")