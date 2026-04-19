import pytest
import httpx
from openai import BadRequestError
from unittest.mock import patch, MagicMock
from app.model import ModelRequestError, create_response


def _bad_request_error(message: str) -> BadRequestError:
    request = httpx.Request("POST", "https://example.test/chat/completions")
    response = httpx.Response(400, request=request)
    return BadRequestError(message, response=response, body={"error": message})


def test_create_response_basic():
    """create_response 기본 동작 테스트"""
    messages = [{"role": "user", "content": "Hello"}]

    with patch("app.model.client.chat.completions.create") as mock_create, \
         patch("app.model.ALL_MODEL", "test_model"):
        mock_response = MagicMock()
        mock_create.return_value = mock_response

        result = create_response(messages)

        assert result == mock_response
        mock_create.assert_called_once_with(
            model="test_model",
            messages=messages
        )


def test_create_response_with_tools():
    """툴 포함 테스트"""
    messages = [{"role": "user", "content": "Calculate"}]
    tools = [{"type": "function", "function": {"name": "calc"}}]

    with patch("app.model.client.chat.completions.create") as mock_create, \
         patch("app.model.ALL_MODEL", "test_model"):
        mock_response = MagicMock()
        mock_create.return_value = mock_response

        result = create_response(messages, tools)

        assert result == mock_response
        mock_create.assert_called_once_with(
            model="test_model",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )


def test_create_response_wraps_context_too_large_error():
    messages = [{"role": "user", "content": "Hello"}]
    provider_error = _bad_request_error("maximum context length exceeded")

    with patch("app.model.client.chat.completions.create") as mock_create:
        mock_create.side_effect = provider_error

        with pytest.raises(ModelRequestError) as exc_info:
            create_response(messages)

    error = exc_info.value
    assert error.kind == "request_too_large"
    assert error.status_code == 400
    assert "요청 컨텍스트가 너무 커서" in error.public_message
    assert "maximum context length exceeded" in (error.provider_message or "")


def test_create_response_wraps_provider_bad_request_error():
    messages = [{"role": "user", "content": "Hello"}]
    provider_error = _bad_request_error("invalid request payload")

    with patch("app.model.client.chat.completions.create") as mock_create:
        mock_create.side_effect = provider_error

        with pytest.raises(ModelRequestError) as exc_info:
            create_response(messages)

    error = exc_info.value
    assert error.kind == "provider_bad_request"
    assert error.status_code == 400
    assert "provider에서 거부" in error.public_message
