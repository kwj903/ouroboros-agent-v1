from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.logger import utc_now_iso
from app.paths import STATE_DIR

STATE_ROOT = STATE_DIR

def _now_local_session_prefix() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _shorten(text: str, max_length: int = 50) -> str:
    text = " ".join(text.split())
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def generate_session_id() -> str:
    return f"{_now_local_session_prefix()}_{uuid.uuid4().hex[:6]}"


@dataclass
class SessionState:
    session_id: str
    state_root: Path = field(default=STATE_ROOT)

    session_dir: Path = field(init=False)
    history_file: Path = field(init=False)
    summary_file: Path = field(init=False)
    workspace_state_file: Path = field(init=False)
    meta_file: Path = field(init=False)
    tool_log_file: Path = field(init=False)

    def __post_init__(self) -> None:
        self.session_dir = self.state_root / "sessions" / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.session_dir / "history.jsonl"
        self.summary_file = self.session_dir / "rolling_summary.md"
        self.workspace_state_file = self.session_dir / "workspace_state.json"
        self.meta_file = self.session_dir / "meta.json"
        self.tool_log_file = self.session_dir / "tool_log.jsonl"

        if not self.workspace_state_file.exists():
            self.workspace_state_file.write_text("{}", encoding="utf-8")

        if not self.meta_file.exists():
            self._save_meta(
                {
                    "session_id": self.session_id,
                    "created_at": utc_now_iso(),
                    "updated_at": utc_now_iso(),
                    "title": "(new session)",
                }
            )

    def _load_meta(self) -> dict[str, Any]:
        try:
            return json.loads(self.meta_file.read_text(encoding="utf-8"))
        except Exception:
            return {
                "session_id": self.session_id,
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "title": "(new session)",
            }

    def _save_meta(self, meta: dict[str, Any]) -> None:
        self.meta_file.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def touch_meta(self) -> None:
        meta = self._load_meta()
        meta["updated_at"] = utc_now_iso()
        self._save_meta(meta)

    def set_title_if_missing(self, text: str) -> None:
        meta = self._load_meta()
        current_title = meta.get("title", "").strip()

        if current_title and current_title != "(new session)":
            return

        candidate = _shorten(text.strip(), max_length=60)
        if candidate:
            meta["title"] = candidate
            meta["updated_at"] = utc_now_iso()
            self._save_meta(meta)
            
    def set_title(self, text: str) -> str:
        new_title = text.strip()
        if not new_title:
            raise ValueError("세션 이름은 비어 있을 수 없습니다.")

        meta = self._load_meta()
        meta["title"] = _shorten(new_title, max_length=80)
        meta["updated_at"] = utc_now_iso()
        self._save_meta(meta)
        return meta["title"]

    def get_meta(self) -> dict[str, Any]:
        return self._load_meta()

    def read_history_records(self) -> list[dict[str, Any]]:
        if not self.history_file.exists():
            return []

        records: list[dict[str, Any]] = []
        with self.history_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
        return records

    def append_history(self, role: str, content: str) -> None:
        record = {
            "timestamp": utc_now_iso(),
            "role": role,
            "content": content,
        }
        with self.history_file.open("a", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")

        if role == "user":
            self.set_title_if_missing(content)

        self.touch_meta()

    def overwrite_history(self, records: list[dict[str, Any]]) -> None:
        with self.history_file.open("w", encoding="utf-8") as f:
            for record in records:
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")
        self.touch_meta()

    def get_recent_history(self, limit_messages: int = 8) -> list[dict[str, str]]:
        records = self.read_history_records()[-limit_messages:]
        return [
            {
                "role": record["role"],
                "content": record["content"],
            }
            for record in records
            if record.get("role") in {"user", "assistant"}
        ]

    def load_summary(self) -> str:
        if not self.summary_file.exists():
            return ""
        return self.summary_file.read_text(encoding="utf-8").strip()

    def save_summary(self, text: str) -> None:
        self.summary_file.write_text(text.strip(), encoding="utf-8")
        self.touch_meta()

    def load_workspace_state(self) -> dict[str, Any]:
        if not self.workspace_state_file.exists():
            return {}

        try:
            return json.loads(self.workspace_state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def update_workspace_state(self, **changes: Any) -> dict[str, Any]:
        state = self.load_workspace_state()

        for key, value in changes.items():
            state[key] = value

        self.workspace_state_file.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.touch_meta()
        return state
    
    def append_tool_log(self, entry: dict[str, Any]) -> None:
        with self.tool_log_file.open("a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
        self.touch_meta()

    def load_tool_logs(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self.tool_log_file.exists():
            return []

        rows: list[dict[str, Any]] = []
        with self.tool_log_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        if limit <= 0:
            return rows

        return rows[-limit:]


def create_new_session() -> SessionState:
    return SessionState(session_id=generate_session_id())


def list_sessions() -> list[dict[str, Any]]:
    sessions_root = STATE_ROOT / "sessions"
    sessions_root.mkdir(parents=True, exist_ok=True)

    items: list[dict[str, Any]] = []

    for session_dir in sessions_root.iterdir():
        if not session_dir.is_dir():
            continue

        meta_file = session_dir / "meta.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                meta = {}
        else:
            meta = {}

        items.append(
            {
                "session_id": session_dir.name,
                "created_at": meta.get("created_at", ""),
                "updated_at": meta.get("updated_at", ""),
                "title": meta.get("title", "(untitled)"),
            }
        )

    items.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return items


def resolve_session_choice(choice: str) -> str | None:
    choice = choice.strip()
    if not choice:
        return None

    sessions = list_sessions()

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(sessions):
            return sessions[index]["session_id"]
        return None

    candidate_dir = STATE_ROOT / "sessions" / choice
    if candidate_dir.exists() and candidate_dir.is_dir():
        return choice

    return None


def format_session_list(current_session_id: str | None = None) -> str:
    sessions = list_sessions()
    if not sessions:
        return "세션이 없습니다."

    lines = ["세션 목록:"]
    for index, item in enumerate(sessions, start=1):
        marker = " *" if item["session_id"] == current_session_id else ""
        lines.append(
            f"{index}. {item['session_id']}{marker}\n"
            f"   title: {item.get('title', '(untitled)')}\n"
            f"   updated_at: {item.get('updated_at', '')}"
        )

    lines.append("")
    lines.append("전환 방법: switch <번호> 또는 switch <session_id>")
    return "\n".join(lines)


def delete_session_by_id(session_id: str) -> bool:
    session_dir = STATE_ROOT / "sessions" / session_id
    if not session_dir.exists() or not session_dir.is_dir():
        return False

    shutil.rmtree(session_dir)
    return True


def delete_session_choice(choice: str) -> str | None:
    session_id = resolve_session_choice(choice)
    if session_id is None:
        return None

    deleted = delete_session_by_id(session_id)
    if not deleted:
        return None

    return session_id


def rename_session_by_id(session_id: str, new_title: str) -> str | None:
    session_dir = STATE_ROOT / "sessions" / session_id
    if not session_dir.exists() or not session_dir.is_dir():
        return None

    session = SessionState(session_id=session_id)
    return session.set_title(new_title)


def rename_session_choice(choice: str, new_title: str) -> str | None:
    session_id = resolve_session_choice(choice)
    if session_id is None:
        return None

    return rename_session_by_id(session_id, new_title)