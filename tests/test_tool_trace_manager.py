from app import tool_trace_manager


class FakeSession:
    def __init__(self, logs):
        self._logs = logs

    def load_tool_logs(self, limit=100):
        return self._logs[-limit:]


def _pending_log(action_id: str = "a1"):
    return {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "step_index": 1,
        "tool_name": "request_write_file",
        "arguments": {"path": "x.txt"},
        "result_preview": "승인 필요",
        "result_raw": (
            "__PENDING_APPROVAL__\n"
            f"action_id={action_id}\n"
            "summary=파일 쓰기 요청\n"
            "message=승인이 필요합니다."
        ),
    }


def test_build_tool_panel_keeps_pending_only_when_action_is_pending(monkeypatch):
    monkeypatch.setattr(
        tool_trace_manager,
        "get_action",
        lambda action_id: {"action_id": action_id, "status": "pending"},
    )

    panel = tool_trace_manager.build_tool_panel(FakeSession([_pending_log()]))

    assert panel["pending_approval"]["action_id"] == "a1"
    assert panel["latest_execution"]["result_kind"] == "pending_approval"


def test_build_tool_panel_drops_stale_pending_when_action_is_executed(monkeypatch):
    monkeypatch.setattr(
        tool_trace_manager,
        "get_action",
        lambda action_id: {"action_id": action_id, "status": "executed"},
    )

    panel = tool_trace_manager.build_tool_panel(FakeSession([_pending_log()]))

    assert panel["pending_approval"] is None
    assert panel["latest_execution"]["result_kind"] == "executed"
