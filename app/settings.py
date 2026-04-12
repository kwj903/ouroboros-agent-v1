from __future__ import annotations

import os

from dotenv import load_dotenv


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


# LLM provider settings
GROQ_API_KEY = _get_env("GROQ_API_KEY")
GROQ_BASE_URL = _get_env("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = _get_env("GROQ_MODEL", "openai/gpt-oss-120b")

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