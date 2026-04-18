import pytest
from unittest.mock import patch, MagicMock
from app.agent import run_agent


def test_run_agent_basic():
    """run_agent 기본 동작 테스트"""
    user_input = "Hello"

    with patch("app.agent.create_response") as mock_create_response:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hi there!"
        mock_response.choices[0].message.tool_calls = None
        mock_create_response.return_value = mock_response

        result = run_agent(user_input, max_steps=1)

        assert "Hi there!" in result
        assert mock_create_response.call_count >= 1


def test_run_agent_with_tools():
    """툴 호출 포함 테스트"""
    user_input = "Calculate 2+2"

    with patch("app.agent.create_response") as mock_create_response, \
         patch("app.agent.TOOLS") as mock_tools:

        # 첫 응답: 툴 호출
        mock_response1 = MagicMock()
        mock_response1.choices = [MagicMock()]
        mock_response1.choices[0].message.content = ""
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call1"
        mock_tool_call.function.name = "calculator"
        mock_tool_call.function.arguments = '{"expression": "2+2"}'
        mock_response1.choices[0].message.tool_calls = [mock_tool_call]

        # 두 번째 응답: 최종 답변
        mock_response2 = MagicMock()
        mock_response2.choices = [MagicMock()]
        mock_response2.choices[0].message.content = "Result: 4"
        mock_response2.choices[0].message.tool_calls = None

        mock_create_response.side_effect = [mock_response1, mock_response2]

        mock_tools.__getitem__.return_value = lambda expression: f"Result: {eval(expression)}"

        result = run_agent(user_input, max_steps=2)

        assert "Result: 4" in result