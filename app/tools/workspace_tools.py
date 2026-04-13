from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from app.runtime_context import get_current_session_id

from app.approvals import (
    create_pending_action,
    get_action,
    list_pending_actions,
    mark_executed,
    mark_failed,
    mark_rejected,
)
from app.settings import WORKSPACE_ROOT


EXCLUDED_DIR_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".agent_state",
}
READ_FALLBACK_ENCODINGS = ("utf-8", "utf-8-sig", "cp949")


def _format_rel(path: Path) -> str:
    try:
        rel = path.relative_to(WORKSPACE_ROOT)
        text = rel.as_posix()
        return text if text else "."
    except ValueError:
        return path.as_posix()


def _resolve_workspace_path(path: str) -> Path:
    raw = Path(path).expanduser()

    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        resolved = (WORKSPACE_ROOT / raw).resolve()

    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as e:
        raise ValueError(
            f"WORKSPACE_ROOT 바깥 경로에는 접근할 수 없습니다: {path}"
        ) from e

    return resolved


def _is_hidden(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _read_text_file(path: Path) -> str:
    last_error: Exception | None = None

    for encoding in READ_FALLBACK_ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except Exception as e:
            last_error = e

    raise ValueError(f"텍스트 파일로 읽을 수 없습니다: {path} ({last_error})")


def list_dir(path: str = ".", show_hidden: bool = False, max_entries: int = 100) -> str:
    target = _resolve_workspace_path(path)

    if not target.exists():
        return f"ERROR: 경로가 존재하지 않습니다: {path}"
    if not target.is_dir():
        return f"ERROR: 디렉터리가 아닙니다: {path}"

    entries = sorted(
        target.iterdir(),
        key=lambda p: (not p.is_dir(), p.name.lower()),
    )

    lines = [f"디렉터리: {_format_rel(target)}"]
    count = 0

    for entry in entries:
        if entry.name in EXCLUDED_DIR_NAMES:
            continue
        if not show_hidden and _is_hidden(entry.relative_to(WORKSPACE_ROOT)):
            continue

        suffix = "/" if entry.is_dir() else ""
        label = "[DIR]" if entry.is_dir() else "[FILE]"
        lines.append(f"{label} {entry.name}{suffix}")
        count += 1

        if count >= max_entries:
            lines.append("... (entry 수가 많아 일부 생략)")
            break

    if count == 0:
        lines.append("(비어 있음)")

    return "\n".join(lines)


def tree_view(
    path: str = ".",
    max_depth: int = 3,
    show_hidden: bool = False,
    max_entries: int = 200,
) -> str:
    target = _resolve_workspace_path(path)

    if not target.exists():
        return f"ERROR: 경로가 존재하지 않습니다: {path}"
    if not target.is_dir():
        return f"ERROR: 디렉터리가 아닙니다: {path}"

    lines = [f"{_format_rel(target)}/"]
    counter = {"count": 0, "truncated": False}

    def walk(current: Path, prefix: str, depth: int) -> None:
        if depth > max_depth or counter["truncated"]:
            return

        entries = sorted(
            current.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )

        filtered: list[Path] = []
        for entry in entries:
            if entry.name in EXCLUDED_DIR_NAMES:
                continue
            rel = entry.relative_to(WORKSPACE_ROOT)
            if not show_hidden and _is_hidden(rel):
                continue
            filtered.append(entry)

        for index, entry in enumerate(filtered):
            if counter["count"] >= max_entries:
                lines.append(prefix + "... (tree 출력 생략)")
                counter["truncated"] = True
                return

            is_last = index == len(filtered) - 1
            connector = "└── " if is_last else "├── "
            name = entry.name + ("/" if entry.is_dir() else "")
            lines.append(prefix + connector + name)
            counter["count"] += 1

            if entry.is_dir() and depth < max_depth:
                child_prefix = prefix + ("    " if is_last else "│   ")
                walk(entry, child_prefix, depth + 1)

    walk(target, "", 1)
    return "\n".join(lines)


def read_file(path: str, start_line: int = 1, end_line: int = 200) -> str:
    target = _resolve_workspace_path(path)

    if not target.exists():
        return f"ERROR: 파일이 존재하지 않습니다: {path}"
    if not target.is_file():
        return f"ERROR: 파일이 아닙니다: {path}"
    if start_line < 1 or end_line < start_line:
        return "ERROR: start_line / end_line 범위가 올바르지 않습니다."

    try:
        content = _read_text_file(target)
    except Exception as e:
        return f"ERROR: 파일 읽기 실패: {e}"

    lines = content.splitlines()

    if not lines:
        return f"파일: {_format_rel(target)}\n(빈 파일)"

    selected = lines[start_line - 1 : end_line]
    if not selected:
        return f"파일: {_format_rel(target)}\n지정한 줄 범위에 내용이 없습니다."

    rendered = [f"파일: {_format_rel(target)}"]
    for index, line in enumerate(selected, start=start_line):
        rendered.append(f"{index:>4}: {line}")

    return "\n".join(rendered)


def request_search_files(
    query: str,
    path: str = ".",
    case_sensitive: bool = False,
    max_matches: int = 20,
) -> str:
    summary = (
        f"파일 검색 요청 - query={query!r}, path={path!r}, "
        f"case_sensitive={case_sensitive}, max_matches={max_matches}"
    )
    payload = {
        "query": query,
        "path": path,
        "case_sensitive": case_sensitive,
        "max_matches": max_matches,
    }
    action_id = create_pending_action(
        "search_files",
        payload,
        summary,
        session_id=get_current_session_id(),
    )
    return _format_approval_response(action_id, summary)


def request_write_file(
    path: str,
    content: str,
    mode: str = "overwrite",
    create_parents: bool = True,
) -> str:
    summary = (
        f"파일 쓰기 요청 - path={path!r}, mode={mode!r}, "
        f"content_length={len(content)}, create_parents={create_parents}"
    )
    payload = {
        "path": path,
        "content": content,
        "mode": mode,
        "create_parents": create_parents,
    }
    action_id = create_pending_action(
    "write_file",
    payload,
    summary,
    session_id=get_current_session_id(),
    )
    return _format_approval_response(action_id, summary)

def request_create_file(
    path: str,
    create_parents: bool = True,
    overwrite: bool = False,
) -> str:
    payload = {
        "path": path,
        "create_parents": create_parents,
        "overwrite": overwrite,
    }
    summary = (
        f"빈 파일 생성 요청 - path={path!r}, "
        f"overwrite={overwrite}, create_parents={create_parents}"
    )

    action_id = create_pending_action(
        "create_file",
        payload,
        summary,
        session_id=get_current_session_id(),
    )
    return _format_approval_response(action_id, summary)

def request_replace_text_in_file(
    path: str,
    old_text: str,
    new_text: str,
    replace_all: bool = False,
) -> str:
    summary = (
        f"파일 수정 요청 - path={path!r}, replace_all={replace_all}, "
        f"old_length={len(old_text)}, new_length={len(new_text)}"
    )
    payload = {
        "path": path,
        "old_text": old_text,
        "new_text": new_text,
        "replace_all": replace_all,
    }
    action_id = create_pending_action(
        "replace_text_in_file",
        payload,
        summary,
        session_id=get_current_session_id(),
    )
    return _format_approval_response(action_id, summary)


def request_delete_path(path: str, recursive: bool = False) -> str:
    summary = f"삭제 요청 - path={path!r}, recursive={recursive}"
    payload = {
        "path": path,
        "recursive": recursive,
    }
    action_id = create_pending_action(
        "delete_path",
        payload,
        summary,
        session_id=get_current_session_id(),
    )
    return _format_approval_response(action_id, summary)





def _search_files(
    query: str,
    path: str = ".",
    case_sensitive: bool = False,
    max_matches: int = 20,
) -> str:
    if not query.strip():
        return "ERROR: query가 비어 있습니다."

    target = _resolve_workspace_path(path)
    if not target.exists():
        return f"ERROR: 경로가 존재하지 않습니다: {path}"

    files: list[Path] = []
    if target.is_file():
        files = [target]
    else:
        for candidate in target.rglob("*"):
            if not candidate.is_file():
                continue
            if any(part in EXCLUDED_DIR_NAMES for part in candidate.parts):
                continue
            files.append(candidate)

    needle = query if case_sensitive else query.lower()
    matches: list[str] = []

    for file_path in files:
        try:
            content = _read_text_file(file_path)
        except Exception:
            continue

        for line_no, line in enumerate(content.splitlines(), start=1):
            haystack = line if case_sensitive else line.lower()
            if needle in haystack:
                rel = _format_rel(file_path)
                preview = " ".join(line.strip().split())
                matches.append(f"{rel}:{line_no}: {preview[:180]}")
                if len(matches) >= max_matches:
                    break

        if len(matches) >= max_matches:
            break

    if not matches:
        return f"검색 결과가 없습니다. query={query!r}"

    lines = [f"검색 결과 - query={query!r}"]
    lines.extend(matches)
    return "\n".join(lines)


def _write_file(
    path: str,
    content: str,
    mode: str = "overwrite",
    create_parents: bool = True,
) -> str:
    target = _resolve_workspace_path(path)

    if create_parents:
        target.parent.mkdir(parents=True, exist_ok=True)

    if mode not in {"overwrite", "append", "create_only"}:
        return f"ERROR: 지원하지 않는 mode입니다: {mode}"

    if mode == "create_only" and target.exists():
        return f"ERROR: 파일이 이미 존재합니다: {_format_rel(target)}"

    if mode == "append":
        target.write_text("", encoding="utf-8") if not target.exists() else None
        with target.open("a", encoding="utf-8") as f:
            f.write(content)
    else:
        target.write_text(content, encoding="utf-8")

    return f"파일 쓰기 완료: {_format_rel(target)}"

def _execute_create_file(
    path: str,
    create_parents: bool = True,
    overwrite: bool = False,
) -> str:
    target = _resolve_workspace_path(path)

    if target.exists() and target.is_dir():
        return f"ERROR: 디렉터리가 이미 존재합니다: {path}"

    if create_parents:
        target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() and not overwrite:
        return f"ERROR: 파일이 이미 존재합니다: {path}"

    target.write_text("", encoding="utf-8")
    return f"빈 파일 생성 완료: {path}"

def _replace_text_in_file(
    path: str,
    old_text: str,
    new_text: str,
    replace_all: bool = False,
) -> str:
    target = _resolve_workspace_path(path)

    if not target.exists():
        return f"ERROR: 파일이 존재하지 않습니다: {path}"
    if not target.is_file():
        return f"ERROR: 파일이 아닙니다: {path}"

    try:
        content = _read_text_file(target)
    except Exception as e:
        return f"ERROR: 파일 읽기 실패: {e}"

    if old_text not in content:
        return "ERROR: old_text를 파일에서 찾지 못했습니다."

    if replace_all:
        new_content = content.replace(old_text, new_text)
    else:
        new_content = content.replace(old_text, new_text, 1)

    target.write_text(new_content, encoding="utf-8")
    return f"파일 수정 완료: {_format_rel(target)}"


def _delete_path(path: str, recursive: bool = False) -> str:
    target = _resolve_workspace_path(path)

    if target == WORKSPACE_ROOT:
        return "ERROR: WORKSPACE_ROOT 자체는 삭제할 수 없습니다."
    if not target.exists():
        return f"ERROR: 경로가 존재하지 않습니다: {path}"

    protected_names = {".git", ".venv", ".agent_state"}
    if target.name in protected_names:
        return f"ERROR: 보호된 경로는 삭제할 수 없습니다: {_format_rel(target)}"

    if target.is_dir():
        if not recursive:
            return (
                "ERROR: 디렉터리 삭제에는 recursive=True가 필요합니다. "
                f"path={_format_rel(target)}"
            )
        shutil.rmtree(target)
        return f"디렉터리 삭제 완료: {_format_rel(target)}"

    target.unlink()
    return f"파일 삭제 완료: {_format_rel(target)}"


def execute_pending_action(action_id: str) -> str:
    action = get_action(action_id)
    if action is None:
        return f"ERROR: 존재하지 않는 action_id입니다: {action_id}"

    if action.get("status") != "pending":
        return (
            f"ERROR: 이미 처리된 action입니다. "
            f"status={action.get('status')}, action_id={action_id}"
        )

    action_type = action["action_type"]
    payload = action["payload"]

    try:
        if action_type == "search_files":
            result = _search_files(**payload)
        elif action_type == "write_file":
            result = _write_file(**payload)
        elif action_type == "replace_text_in_file":
            result = _replace_text_in_file(**payload)
        elif action_type == "delete_path":
            result = _delete_path(**payload)
        elif action_type == "create_file":
            result = _execute_create_file(**payload)
        else:
            raise ValueError(f"지원하지 않는 action_type입니다: {action_type}")
    except Exception as e:
        mark_failed(action_id, str(e))
        return f"실행 실패: action_id={action_id}\n에러: {e}"

    mark_executed(action_id, result)
    return f"실행 완료: action_id={action_id}\n{result}"


def reject_pending_action(action_id: str) -> str:
    action = get_action(action_id)
    if action is None:
        return f"ERROR: 존재하지 않는 action_id입니다: {action_id}"

    if action.get("status") != "pending":
        return (
            f"ERROR: 이미 처리된 action입니다. "
            f"status={action.get('status')}, action_id={action_id}"
        )

    mark_rejected(action_id)
    return f"거부 완료: action_id={action_id}"


def format_pending_actions() -> str:
    pending = list_pending_actions()
    if not pending:
        return "대기 중인 승인 요청이 없습니다."

    lines = ["대기 중인 승인 요청:"]
    for item in pending:
        lines.append(
            f"- action_id={item['action_id']} | "
            f"type={item['action_type']} | "
            f"summary={item['summary']}"
        )
    return "\n".join(lines)

def _format_approval_response(action_id: str, summary: str) -> str:
    return (
        f"__PENDING_APPROVAL__\n"
        f"action_id={action_id}\n"
        f"summary={summary}\n"
        f"message=이 작업은 사용자 승인이 필요합니다."
    )