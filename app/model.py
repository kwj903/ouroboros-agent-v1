from __future__ import annotations

import json

from openai import APIStatusError, BadRequestError, OpenAI

from app.settings import ALL_API_KEY, ALL_BASE_URL, ALL_MODEL


client = OpenAI(
    api_key=ALL_API_KEY,
    base_url=ALL_BASE_URL,
)

REQUEST_TOO_LARGE_MESSAGE = (
    "요청 컨텍스트가 너무 커서 모델 호출에 실패했습니다. "
    "요청 범위를 줄이거나 파일/줄 범위를 좁혀 다시 시도하세요."
)
PROVIDER_BAD_REQUEST_MESSAGE = (
    "모델 요청이 provider에서 거부되었습니다. "
    "요청 내용을 줄이거나 형식을 단순화해 다시 시도하세요."
)

_REQUEST_TOO_LARGE_PATTERNS = (
    "context length",
    "context window",
    "maximum context",
    "max context",
    "token limit",
    "too many tokens",
    "tokens exceed",
    "request too large",
    "prompt is too long",
    "input is too long",
    "maximum prompt",
)


class ModelRequestError(RuntimeError):
    """Safe wrapper for provider request errors that should not leak raw details."""

    def __init__(
        self,
        public_message: str,
        *,
        kind: str,
        status_code: int | None = None,
        provider_message: str | None = None,
    ) -> None:
        super().__init__(public_message)
        self.public_message = public_message
        self.kind = kind
        self.status_code = status_code
        self.provider_message = provider_message


def get_model_name() -> str:
    return ALL_MODEL


def _error_text(exc: Exception) -> str:
    body = getattr(exc, "body", None)
    if body is not None:
        try:
            return json.dumps(body, ensure_ascii=False)
        except TypeError:
            return str(body)
    return str(exc)


def _status_code(exc: Exception) -> int | None:
    status = getattr(exc, "status_code", None)
    if isinstance(status, int):
        return status

    response = getattr(exc, "response", None)
    response_status = getattr(response, "status_code", None)
    if isinstance(response_status, int):
        return response_status

    return None


def _is_request_too_large(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in _REQUEST_TOO_LARGE_PATTERNS)


def _to_model_request_error(exc: Exception) -> ModelRequestError:
    provider_message = _error_text(exc)
    status_code = _status_code(exc)

    if _is_request_too_large(provider_message):
        return ModelRequestError(
            REQUEST_TOO_LARGE_MESSAGE,
            kind="request_too_large",
            status_code=status_code,
            provider_message=provider_message,
        )

    return ModelRequestError(
        PROVIDER_BAD_REQUEST_MESSAGE,
        kind="provider_bad_request",
        status_code=status_code,
        provider_message=provider_message,
    )


def create_response(messages: list[dict], tools: list[dict] | None = None):
    """
    ALL의 OpenAI-compatible chat completion 호출
    """
    kwargs = {
        "model": ALL_MODEL,
        "messages": messages,
    }

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    try:
        return client.chat.completions.create(**kwargs)
    except BadRequestError as exc:
        raise _to_model_request_error(exc) from exc
    except APIStatusError as exc:
        status_code = _status_code(exc)
        provider_message = _error_text(exc)
        if status_code in {400, 413} or _is_request_too_large(provider_message):
            raise _to_model_request_error(exc) from exc
        raise
