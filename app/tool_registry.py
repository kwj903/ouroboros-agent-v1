from __future__ import annotations

from typing import Callable

from app.tools.calculator import calculate
from app.tools.search_notes import search_notes
from app.tools.read_note import read_note


ToolFunc = Callable[..., str]


TOOLS: dict[str, ToolFunc] = {
    "calculator": calculate,
    "search_notes": search_notes,
    "read_note": read_note,
}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "수학 계산이 필요할 때 사용한다. expression에는 숫자와 괄호, +, -, *, /, //, %, ** 만 넣는다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수식. 예: 2 + 3 * (4 - 1)"
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_notes",
            "description": "로컬 notes 폴더에서 사용자의 노트(.md, .txt)를 검색할 때 사용한다. 질문이 노트, 메모, 정리한 내용, 기록된 지식과 관련 있으면 이 도구를 우선 고려한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "노트에서 찾고 싶은 주제나 키워드. 예: RAG, 파이썬 리스트, Django ORM"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "최대 결과 개수. 보통 3이면 충분하다.",
                        "default": 3
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_note",
            "description": "search_notes로 찾은 notes 폴더 안의 특정 파일 내용을 자세히 읽을 때 사용한다. path에는 반드시 notes/로 시작하는 파일 경로를 넣는다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "읽을 파일 경로. 예: notes/rag_intro.md"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "최대 읽기 길이. 기본값은 4000 정도면 충분하다.",
                        "default": 4000
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            },
        },
    }
]