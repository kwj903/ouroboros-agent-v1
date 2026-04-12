from __future__ import annotations

import ast
import operator as op
from typing import Any

# 허용할 연산자만 명시적으로 제한
_ALLOWED_OPERATORS: dict[type, Any] = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("숫자만 허용됩니다.")

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"허용되지 않은 연산자입니다: {operator_type.__name__}")

        return _ALLOWED_OPERATORS[operator_type](left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        operator_type = type(node.op)

        if operator_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"허용되지 않은 단항 연산자입니다: {operator_type.__name__}")

        return _ALLOWED_OPERATORS[operator_type](operand)

    raise ValueError(f"지원하지 않는 식입니다: {type(node).__name__}")


def calculate(expression: str) -> str:
    """
    안전한 사칙연산/거듭제곱 계산기.
    예: '2 + 3 * (4 - 1)'
    """
    try:
        parsed = ast.parse(expression, mode="eval")
        result = _eval_node(parsed.body)
        return str(result)
    except Exception as e:
        return f"ERROR: {e}"