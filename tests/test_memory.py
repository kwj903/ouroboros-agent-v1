import pytest
from unittest.mock import patch, MagicMock
from app import memory_manager
from app.long_term_memory import save_memory_note_tool, search_memory_notes_tool
from app.model import ModelRequestError


def test_save_memory_note_tool():
    """메모리 저장 테스트"""
    with patch("app.long_term_memory._append_record") as mock_append:
        result = save_memory_note_tool("Test content", tags="test", importance=3)

        assert "장기 기억 저장 완료" in result
        mock_append.assert_called_once()


def test_search_memory_notes_tool():
    """메모리 검색 테스트"""
    with patch("app.long_term_memory._load_all_memory_records") as mock_load:
        mock_load.return_value = [
            {"content": "test memory", "importance": 3, "tags": ["test"], "timestamp": "2023-01-01", "note_type": "general"}
        ]

        result = search_memory_notes_tool("test")

        assert isinstance(result, str)
        assert "test memory" in result


def test_build_memory_context_trims_request_view_only(monkeypatch):
    class FakeSession:
        def load_summary(self):
            return "s" * (memory_manager.SUMMARY_CONTEXT_CHAR_LIMIT + 500)

        def load_workspace_state(self):
            return {
                "large_state": "w"
                * (memory_manager.WORKSPACE_STATE_CONTEXT_CHAR_LIMIT + 500)
            }

    monkeypatch.setattr(
        memory_manager,
        "search_memory_records",
        lambda query, max_results: [
            {
                "memory_id": "m1",
                "content": "m"
                * (memory_manager.MEMORY_RECORD_CONTENT_CHAR_LIMIT + 500),
                "importance": 3,
                "tags": ["test"],
                "timestamp": "2026-01-01T00:00:00+00:00",
                "note_type": "general",
            }
        ],
    )

    context = memory_manager.build_memory_context(
        FakeSession(),
        user_input="test",
    )

    assert len(context) <= memory_manager.MEMORY_CONTEXT_CHAR_LIMIT
    assert "model request view trimmed" in context


def test_build_recent_history_view_trims_without_rewriting_source():
    source_records = [
        {
            "role": "user" if index % 2 == 0 else "assistant",
            "content": f"{index}-" + ("x" * 2500),
        }
        for index in range(8)
    ]
    original_records = [record.copy() for record in source_records]

    class FakeSession:
        def get_recent_history(self, limit_messages):
            return source_records[-limit_messages:]

    history_view = memory_manager.build_recent_history_view(FakeSession())

    assert source_records == original_records
    assert sum(len(message["content"]) for message in history_view) <= (
        memory_manager.HISTORY_TOTAL_CHAR_LIMIT
    )
    assert all(
        len(message["content"]) <= memory_manager.HISTORY_MESSAGE_CHAR_LIMIT
        for message in history_view
    )
    assert any(
        "model request view trimmed" in message["content"]
        for message in history_view
    )


def test_compact_history_model_failure_skips_compaction(monkeypatch):
    saved: list[str] = []
    overwritten: list[list[dict]] = []

    class FakeSession:
        def read_history_records(self):
            return [
                {
                    "role": "user" if index % 2 == 0 else "assistant",
                    "content": f"message {index}",
                }
                for index in range(memory_manager.COMPACT_THRESHOLD + 1)
            ]

        def load_summary(self):
            return "existing summary"

        def save_summary(self, text):
            saved.append(text)

        def overwrite_history(self, records):
            overwritten.append(records)

    def fail_create_response(messages):
        raise ModelRequestError(
            "요청 컨텍스트가 너무 커서 모델 호출에 실패했습니다.",
            kind="request_too_large",
            status_code=400,
            provider_message="maximum context length exceeded",
        )

    monkeypatch.setattr(memory_manager, "create_response", fail_create_response)

    memory_manager.compact_history_if_needed(FakeSession())

    assert saved == []
    assert overwritten == []


def test_memory_suggestions_default_off_does_not_generate(monkeypatch):
    from app.api import services

    called = False

    def fake_generate_memory_suggestions(**kwargs):
        nonlocal called
        called = True
        return [{"suggestion_id": "s1"}]

    monkeypatch.setattr(services, "AUTO_MEMORY_SUGGESTIONS", False)
    monkeypatch.setattr(
        "app.long_term_memory.generate_memory_suggestions",
        fake_generate_memory_suggestions,
    )

    result = services._maybe_generate_memory_suggestions(
        user_input="이 프로젝트 규칙을 기억해",
        answer="알겠습니다.",
        trace_record={"steps": []},
        session_id="test-session",
    )

    assert result == []
    assert called is False


def test_list_memory_suggestions_api_default_off_returns_empty(monkeypatch):
    from app.api import services

    monkeypatch.setattr(services, "AUTO_MEMORY_SUGGESTIONS", False)
    monkeypatch.setattr(
        services,
        "list_memory_suggestions",
        lambda: [{"suggestion_id": "s1", "status": "pending"}],
    )

    assert services.list_memory_suggestions_api() == []
