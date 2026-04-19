from unittest.mock import patch, MagicMock

from app.agent import run_agent, should_plan_request


def _mock_response(content: str, tool_calls=None):
    response = MagicMock()
    response.choices = [MagicMock()]
    response.choices[0].message.content = content
    response.choices[0].message.tool_calls = tool_calls
    return response


def test_should_plan_request_rules():
    assert should_plan_request("Hello") is False
    assert should_plan_request("2+2 계산해줘") is False
    assert should_plan_request("foo.txt 삭제해줘") is False
    assert should_plan_request(
        "README.md를 읽고 핵심 내용을 요약한 뒤 summary.md 파일로 저장 요청을 만들어줘"
    ) is True


def test_run_agent_basic():
    """run_agent 기본 동작 테스트"""
    user_input = "Hello"

    with patch("app.agent.create_response") as mock_create_response:
        mock_create_response.return_value = _mock_response("Hi there!")

        result, trace_record = run_agent(user_input, max_steps=1, return_trace=True)

        assert "Hi there!" in result
        assert mock_create_response.call_count == 1
        assert trace_record["planner"] == {
            "used": False,
            "status": "skipped",
            "tasks": [],
        }


def test_run_agent_with_tools():
    """툴 호출 포함 테스트"""
    user_input = "Calculate 2+2"

    with patch("app.agent.create_response") as mock_create_response, \
         patch("app.agent.TOOLS") as mock_tools:

        # 첫 응답: 툴 호출
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call1"
        mock_tool_call.type = "function"
        mock_tool_call.function.name = "calculator"
        mock_tool_call.function.arguments = '{"expression": "2+2"}'
        mock_response1 = _mock_response("", tool_calls=[mock_tool_call])

        # 두 번째 응답: 최종 답변
        mock_response2 = _mock_response("Result: 4")

        mock_create_response.side_effect = [mock_response1, mock_response2]

        mock_tools.get.return_value = lambda expression: f"Result: {eval(expression)}"

        result, trace_record = run_agent(user_input, max_steps=2, return_trace=True)

        assert "Result: 4" in result
        assert mock_create_response.call_count == 2
        assert trace_record["planner"]["status"] == "skipped"


def test_run_agent_uses_planner_for_complex_requests():
    user_input = "README.md를 읽고 핵심 내용을 요약한 뒤 summary.md 파일로 저장 요청을 만들어줘"

    with patch("app.agent.create_response") as mock_create_response:
        mock_create_response.side_effect = [
            _mock_response(
                '["README.md 파일을 읽는다", "핵심 내용을 요약한다", "summary.md 저장 요청을 만든다"]'
            ),
            _mock_response("요약 준비 완료"),
        ]

        result, trace_record = run_agent(user_input, max_steps=1, return_trace=True)

        assert "요약 준비 완료" in result
        assert mock_create_response.call_count == 2
        assert mock_create_response.call_args_list[0].kwargs["tools"] == []
        assert trace_record["planner"]["used"] is True
        assert trace_record["planner"]["status"] == "planned"
        assert trace_record["planner"]["tasks"] == [
            "README.md 파일을 읽는다",
            "핵심 내용을 요약한다",
            "summary.md 저장 요청을 만든다",
        ]


def test_run_agent_keeps_direct_execution_on_planner_fallback():
    user_input = "README.md를 읽고 핵심 내용을 요약한 뒤 summary.md 파일로 저장 요청을 만들어줘"

    with patch("app.agent.create_response") as mock_create_response:
        mock_create_response.side_effect = [
            _mock_response("not json"),
            _mock_response("직접 실행 완료"),
        ]

        result, trace_record = run_agent(user_input, max_steps=1, return_trace=True)

        assert "직접 실행 완료" in result
        assert trace_record["planner"]["used"] is False
        assert trace_record["planner"]["status"] == "fallback"
        assert trace_record["planner"]["tasks"] == [f"사용자 요청 처리: {user_input}"]


def test_run_agent_does_not_use_single_planner_task_as_plan():
    user_input = "README.md를 읽고 핵심 내용을 요약한 뒤 summary.md 파일로 저장 요청을 만들어줘"

    with patch("app.agent.create_response") as mock_create_response:
        mock_create_response.side_effect = [
            _mock_response('["사용자 요청을 직접 처리한다"]'),
            _mock_response("단일 단계 처리 완료"),
        ]

        result, trace_record = run_agent(user_input, max_steps=1, return_trace=True)

        assert "단일 단계 처리 완료" in result
        assert trace_record["planner"]["used"] is False
        assert trace_record["planner"]["status"] == "planned_single"
        assert trace_record["planner"]["tasks"] == ["사용자 요청을 직접 처리한다"]
