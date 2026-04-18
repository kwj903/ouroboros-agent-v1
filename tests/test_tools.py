import pytest
from app.tools.calculator import calculate


def test_calculate_simple():
    """간단한 계산 테스트"""
    result = calculate("2 + 3")
    assert result == "5"


def test_calculate_complex():
    """복잡한 계산 테스트"""
    result = calculate("2 * (3 + 4)")
    assert result == "14"


def test_calculate_error():
    """에러 케이스 테스트"""
    result = calculate("invalid")
    assert "ERROR" in result