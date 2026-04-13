from __future__ import annotations

import os
from pathlib import Path


def _expand(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _default_home_dir() -> Path:
    return _expand("~/.ouroboros")


def _default_workspace_root() -> Path:
    # 작업 대상은 "현재 실행한 디렉터리"를 유지
    return Path.cwd().resolve()


OUROBOROS_HOME = _expand(
    os.getenv("OUROBOROS_HOME", str(_default_home_dir()))
)

STATE_DIR = _expand(
    os.getenv("OUROBOROS_STATE_DIR", str(OUROBOROS_HOME / "state"))
)

LOGS_DIR = _expand(
    os.getenv("OUROBOROS_LOGS_DIR", str(OUROBOROS_HOME / "logs"))
)

NOTES_DIR = _expand(
    os.getenv("OUROBOROS_NOTES_DIR", str(OUROBOROS_HOME / "notes"))
)

CACHE_DIR = _expand(
    os.getenv("OUROBOROS_CACHE_DIR", str(OUROBOROS_HOME / "cache"))
)

WORKSPACE_ROOT = _expand(
    os.getenv("WORKSPACE_ROOT", str(_default_workspace_root()))
)


def ensure_ouroboros_dirs() -> None:
    OUROBOROS_HOME.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)