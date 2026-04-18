import pytest
from unittest.mock import patch, MagicMock
from app.model import create_response


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