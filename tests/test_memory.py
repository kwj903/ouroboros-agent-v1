import pytest
from unittest.mock import patch, MagicMock
from app.long_term_memory import save_memory_note_tool, search_memory_notes_tool


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