from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.paths import WORKSPACE_ROOT, ensure_ouroboros_dirs, OUROBOROS_HOME


# 1) 전역 기본 환경변수
load_dotenv(OUROBOROS_HOME / ".env")

# 2) 현재 디렉터리(프로젝트) 환경변수로 override 가능
load_dotenv()


def _get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name)
    if value is None:
        if default is None:
            raise RuntimeError(f"필수 환경변수가 없습니다: {name}")
        return default
    return value.strip()


def _validate_choice(name: str, value: str, allowed: set[str]) -> str:
    if value not in allowed:
        allowed_text = ", ".join(sorted(allowed))
        raise RuntimeError(
            f"{name} 값이 올바르지 않습니다: {value!r}. "
            f"허용값: {allowed_text}"
        )
    return value


ensure_ouroboros_dirs()

# LLM provider settings
GROQ_API_KEY = _get_env("GROQ_API_KEY")
GROQ_BASE_URL = _get_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = _get_env("GROQ_MODEL", "openai/gpt-oss-20b")

# App defaults
DEFAULT_OUTPUT_MODE = _validate_choice(
    "DEFAULT_OUTPUT_MODE",
    _get_env("DEFAULT_OUTPUT_MODE", "cli"),
    {"cli", "markdown"},
)

DEFAULT_RESPONSE_LANGUAGE = _validate_choice(
    "DEFAULT_RESPONSE_LANGUAGE",
    _get_env("DEFAULT_RESPONSE_LANGUAGE", "ko"),
    {"ko", "en"},
)

if not WORKSPACE_ROOT.exists():
    raise RuntimeError(f"WORKSPACE_ROOT 경로가 존재하지 않습니다: {WORKSPACE_ROOT}")
if not WORKSPACE_ROOT.is_dir():
    raise RuntimeError(f"WORKSPACE_ROOT는 디렉터리여야 합니다: {WORKSPACE_ROOT}")