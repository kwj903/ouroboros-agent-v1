from __future__ import annotations

from typing import Callable

from app.tools.calculator import calculate
from app.tools.read_note import read_note
from app.tools.search_notes import search_notes
from app.tools.workspace_tools import (
    get_workspace_info,
    list_dir,
    read_file,
    request_batch_operations,
    request_delete_path,
    request_replace_text_in_file,
    request_search_files,
    request_create_file,
    request_write_file,
    tree_view,
)
from app.long_term_memory import (
    delete_memory_note_tool,
    list_recent_memory_notes_tool,
    save_memory_note_tool,
    search_memory_notes_tool,
    update_memory_note_tool,
)


ToolFunc = Callable[..., str]


TOOLS: dict[str, ToolFunc] = {
    "calculator": calculate,
    "search_notes": search_notes,
    "read_note": read_note,
    "get_workspace_info": get_workspace_info,
    "list_dir": list_dir,
    "tree_view": tree_view,
    "read_file": read_file,
    "request_search_files": request_search_files,
    "request_create_file": request_create_file,
    "request_write_file": request_write_file,
    "request_replace_text_in_file": request_replace_text_in_file,
    "request_delete_path": request_delete_path,
    "request_batch_operations": request_batch_operations,
    "save_memory_note": save_memory_note_tool,
    "search_memory_notes": search_memory_notes_tool,
    "list_recent_memory_notes": list_recent_memory_notes_tool,
    "update_memory_note": update_memory_note_tool,
    "delete_memory_note": delete_memory_note_tool,
}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "수학 계산이 필요할 때 사용한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "계산할 수식"
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
            "description": "로컬 notes 폴더에서 사용자의 노트를 검색한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 주제나 키워드"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "최대 결과 수",
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
            "description": "search_notes로 찾은 notes 안의 파일을 실제로 읽는다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "읽을 notes 하위 파일 경로"
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "최대 읽기 길이",
                        "default": 4000
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_workspace_info",
            "description": (
                "현재 작업 디렉터리와 WORKSPACE_ROOT의 절대경로 및 디렉터리 이름을 "
                "읽기 전용으로 확인한다. 현재 디렉터리 이름, 루트 폴더 이름, "
                "절대경로를 묻는 질문에 사용한다."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "WORKSPACE_ROOT 안의 디렉터리 내용을 읽기 전용으로 본다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "디렉터리 경로"
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "숨김 파일 표시 여부",
                        "default": False
                    },
                    "max_entries": {
                        "type": "integer",
                        "description": "최대 항목 수",
                        "default": 100
                    }
                },
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tree_view",
            "description": "WORKSPACE_ROOT 안의 디렉터리 트리 구조를 읽기 전용으로 본다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "디렉터리 경로"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "최대 깊이",
                        "default": 3
                    },
                    "show_hidden": {
                        "type": "boolean",
                        "description": "숨김 파일 표시 여부",
                        "default": False
                    },
                    "max_entries": {
                        "type": "integer",
                        "description": "최대 출력 수",
                        "default": 200
                    }
                },
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "WORKSPACE_ROOT 안의 텍스트 파일을 읽기 전용으로 본다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "읽을 파일 경로"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "시작 줄 번호",
                        "default": 1
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "끝 줄 번호",
                        "default": 200
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_search_files",
            "description": "WORKSPACE_ROOT 안에서 파일 내용 검색을 요청한다. 이 작업은 즉시 실행되지 않고 사용자 승인 후 실행된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 문자열"
                    },
                    "path": {
                        "type": "string",
                        "description": "검색 시작 경로",
                        "default": "."
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "대소문자 구분 여부",
                        "default": False
                    },
                    "max_matches": {
                        "type": "integer",
                        "description": "최대 매치 수",
                        "default": 20
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
            "name": "request_create_file",
            "description": "파일 내용이 지정되지 않은 새 파일 생성 요청이다. 빈 파일을 만들 때 사용한다. 즉시 실행되지 않고 사용자 승인 후 실행된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "생성할 파일 경로"
                    },
                    "create_parents": {
                        "type": "boolean",
                        "description": "상위 폴더가 없으면 함께 생성할지 여부",
                        "default": True
                    },
                    "overwrite": {
                        "type": "boolean",
                        "description": "같은 파일이 이미 있을 때 빈 파일로 덮어쓸지 여부",
                        "default": False
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_write_file",
            "description": "파일 생성 또는 덮어쓰기를 요청한다. 파일 내용이 명시된 경우에만 사용한다. 내용이 지정되지 않은 단순 파일 생성 요청이면 request_create_file을 사용해야 한다. 즉시 실행되지 않고 사용자 승인 후 실행된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "쓸 파일 경로"
                    },
                    "content": {
                        "type": "string",
                        "description": "파일에 쓸 전체 내용"
                    },
                    "mode": {
                        "type": "string",
                        "description": "overwrite, append, create_only 중 하나",
                        "default": "overwrite"
                    },
                    "create_parents": {
                        "type": "boolean",
                        "description": "상위 폴더 자동 생성 여부",
                        "default": True
                    }
                },
                "required": ["path", "content"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_replace_text_in_file",
            "description": "파일 안의 특정 텍스트를 교체하는 수정을 요청한다. 즉시 실행되지 않고 사용자 승인 후 실행된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "수정할 파일 경로"
                    },
                    "old_text": {
                        "type": "string",
                        "description": "기존 텍스트"
                    },
                    "new_text": {
                        "type": "string",
                        "description": "새 텍스트"
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "전체 교체 여부",
                        "default": False
                    }
                },
                "required": ["path", "old_text", "new_text"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_delete_path",
            "description": "파일 또는 디렉터리 삭제를 요청한다. 즉시 실행되지 않고 사용자 승인 후 실행된다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "삭제할 경로"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "디렉터리 재귀 삭제 여부",
                        "default": False
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_batch_operations",
            "description": (
                "여러 개의 파일/폴더 변경 작업을 하나의 승인 요청으로 묶는다. "
                "사용자가 복수 단계의 파일 생성/수정/삭제를 한 번에 지시했을 때 사용한다. "
                "즉시 실행되지 않고 사용자 승인 후 순서대로 실행된다."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operations": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["create_file"]
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "생성할 파일 경로"
                                        },
                                        "create_parents": {
                                            "type": "boolean",
                                            "description": "상위 폴더 자동 생성 여부"
                                        },
                                        "overwrite": {
                                            "type": "boolean",
                                            "description": "기존 파일 덮어쓰기 여부"
                                        }
                                    },
                                    "required": ["type", "path"],
                                    "additionalProperties": False
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["write_file"]
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "쓸 파일 경로"
                                        },
                                        "content": {
                                            "type": "string",
                                            "description": "파일에 쓸 전체 내용"
                                        },
                                        "mode": {
                                            "type": "string",
                                            "description": "overwrite, append, create_only 중 하나"
                                        },
                                        "create_parents": {
                                            "type": "boolean",
                                            "description": "상위 폴더 자동 생성 여부"
                                        }
                                    },
                                    "required": ["type", "path", "content"],
                                    "additionalProperties": False
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["replace_text_in_file"]
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "수정할 파일 경로"
                                        },
                                        "old_text": {
                                            "type": "string",
                                            "description": "기존 텍스트"
                                        },
                                        "new_text": {
                                            "type": "string",
                                            "description": "새 텍스트"
                                        },
                                        "replace_all": {
                                            "type": "boolean",
                                            "description": "전체 교체 여부"
                                        }
                                    },
                                    "required": ["type", "path", "old_text", "new_text"],
                                    "additionalProperties": False
                                },
                                {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["delete_path"]
                                        },
                                        "path": {
                                            "type": "string",
                                            "description": "삭제할 경로"
                                        },
                                        "recursive": {
                                            "type": "boolean",
                                            "description": "디렉터리 재귀 삭제 여부"
                                        }
                                    },
                                    "required": ["type", "path"],
                                    "additionalProperties": False
                                }
                            ]
                        }
                    },
                    "continue_on_error": {
                        "type": "boolean",
                        "description": "중간 작업 실패 시 다음 작업 계속 여부",
                        "default": False
                    }
                },
                "required": ["operations"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_memory_note",
            "description": "세션을 넘어 유지할 중요한 기억을 저장한다. 사용자가 기억해달라고 명시적으로 요청했거나, 프로젝트 규칙/결정사항/반복적으로 유용한 정보일 때 사용한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "저장할 기억 내용"
                    },
                    "tags": {
                        "type": "string",
                        "description": "쉼표로 구분한 태그 문자열. 예: project,rule,readme",
                        "default": ""
                    },
                    "importance": {
                        "type": "integer",
                        "description": "중요도 1~5",
                        "default": 3
                    },
                    "note_type": {
                        "type": "string",
                        "description": "기억 종류. 예: preference, project_rule, decision, path, general",
                        "default": "general"
                    }
                },
                "required": ["content"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_memory_notes",
            "description": "세션을 넘어 저장된 장기 기억을 검색한다. 사용자의 이전 선호, 반복 결정사항, 자주 쓰는 파일/규칙, 과거 프로젝트 맥락이 현재 질문에 중요할 때 사용한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 주제나 키워드"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "최대 결과 수",
                        "default": 5
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
            "name": "list_recent_memory_notes",
            "description": "최근 저장된 장기 기억 목록을 본다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "최대 개수",
                        "default": 10
                    }
                },
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_memory_note",
            "description": "기존 장기 기억의 내용을 수정한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "수정할 memory_id"
                    },
                    "new_content": {
                        "type": "string",
                        "description": "새 기억 내용"
                    },
                    "new_tags": {
                        "type": "string",
                        "description": "새 태그 문자열. 쉼표 구분",
                        "default": ""
                    },
                    "new_importance": {
                        "type": "integer",
                        "description": "새 중요도 1~5"
                    },
                    "new_note_type": {
                        "type": "string",
                        "description": "새 note_type"
                    }
                },
                "required": ["memory_id", "new_content"],
                "additionalProperties": False
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_memory_note",
            "description": "기존 장기 기억을 삭제한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "삭제할 memory_id"
                    }
                },
                "required": ["memory_id"],
                "additionalProperties": False
            },
        },
    },
]

EXPOSED_TOOL_NAMES = {
    "read_file",
    "request_write_file",
    "search_memory_notes",
    "list_recent_memory_notes",
}

TOOL_SCHEMAS = [
    schema
    for schema in TOOL_SCHEMAS
    if schema["function"]["name"] in EXPOSED_TOOL_NAMES
]