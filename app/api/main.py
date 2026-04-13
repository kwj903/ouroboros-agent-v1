from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    CreateSessionResponse,
    MemoryCreateRequest,
    MemoryUpdateRequest,
    RenameSessionRequest,
)
from app.api.services import (
    approve_action_api,
    create_memory_api,
    create_session_api,
    delete_memory_api,
    delete_session_api,
    drop_memory_suggestion_api,
    list_approvals_api,
    list_memories_api,
    list_memory_suggestions_api,
    list_sessions_api,
    reject_action_api,
    rename_session_api,
    run_chat_turn,
    save_memory_suggestion_api,
    search_memories_api,
    update_memory_api,
    get_session_history_api,
    get_session_workspace_state_api,
    get_session_tool_logs_api,
    get_session_tool_panel_api,
)


app = FastAPI(
    title="Free Model Test API",
    version="0.1.0",
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> dict:
    return run_chat_turn(
        message=payload.message,
        session_id=payload.session_id,
        output_mode=payload.output_mode,
        response_language=payload.response_language,
    )


@app.get("/sessions")
def list_sessions() -> list[dict]:
    return list_sessions_api()


@app.post("/sessions", response_model=CreateSessionResponse)
def create_session() -> dict:
    return create_session_api()


@app.patch("/sessions/{session_id}")
def rename_session(session_id: str, payload: RenameSessionRequest) -> dict:
    return rename_session_api(session_id, payload.title)


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str) -> dict:
    return delete_session_api(session_id)


@app.get("/sessions/{session_id}/history")
def get_session_history(session_id: str) -> list[dict]:
    return get_session_history_api(session_id)


@app.get("/sessions/{session_id}/workspace-state")
def get_session_workspace_state(session_id: str) -> dict:
    return get_session_workspace_state_api(session_id)


@app.get("/sessions/{session_id}/tool-logs")
def get_session_tool_logs(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict]:
    return get_session_tool_logs_api(session_id, limit=limit)


@app.get("/sessions/{session_id}/tool-panel")
def get_session_tool_panel(session_id: str) -> dict:
    return get_session_tool_panel_api(session_id)


@app.get("/memories")
def list_memories(limit: int = Query(default=10, ge=1, le=100)) -> list[dict]:
    return list_memories_api(limit=limit)


@app.get("/memories/search")
def search_memories(
    query: str,
    max_results: int = Query(default=5, ge=1, le=20),
) -> list[dict]:
    return search_memories_api(query, max_results=max_results)


@app.post("/memories")
def create_memory(payload: MemoryCreateRequest) -> dict:
    return create_memory_api(
        content=payload.content,
        tags=payload.tags,
        importance=payload.importance,
        note_type=payload.note_type,
        source_session_id=payload.source_session_id,
    )


@app.patch("/memories/{memory_id}")
def update_memory(memory_id: str, payload: MemoryUpdateRequest) -> dict:
    return update_memory_api(
        memory_id=memory_id,
        new_content=payload.new_content,
        new_tags=payload.new_tags,
        new_importance=payload.new_importance,
        new_note_type=payload.new_note_type,
    )


@app.delete("/memories/{memory_id}")
def delete_memory(memory_id: str) -> dict:
    return delete_memory_api(memory_id)


@app.get("/memory-suggestions")
def list_memory_suggestions() -> list[dict]:
    return list_memory_suggestions_api()


@app.post("/memory-suggestions/{choice}/save")
def save_memory_suggestion(choice: str) -> dict:
    return save_memory_suggestion_api(choice)


@app.post("/memory-suggestions/{choice}/drop")
def drop_memory_suggestion(choice: str) -> dict:
    return drop_memory_suggestion_api(choice)


@app.get("/approvals")
def list_approvals() -> list[dict]:
    return list_approvals_api()


@app.post("/approvals/{action_id}/approve")
def approve_action(action_id: str) -> dict:
    return approve_action_api(action_id)


@app.post("/approvals/{action_id}/reject")
def reject_action(action_id: str) -> dict:
    return reject_action_api(action_id)

if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST_DIR, html=True),
        name="frontend",
    )