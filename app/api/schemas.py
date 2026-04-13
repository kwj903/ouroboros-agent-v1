from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str | None = None
    output_mode: Literal["cli", "markdown"] = "markdown"
    response_language: Literal["ko", "en"] = "ko"


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    status: str
    action_id: str | None = None
    action_required: bool = False
    action_summary: str | None = None
    suggestions_created: int = 0


class CreateSessionResponse(BaseModel):
    session_id: str
    title: str


class RenameSessionRequest(BaseModel):
    title: str = Field(..., min_length=1)


class MemoryCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    tags: list[str] = []
    importance: int = 3
    note_type: str = "general"
    source_session_id: str | None = None


class MemoryUpdateRequest(BaseModel):
    new_content: str = Field(..., min_length=1)
    new_tags: list[str] | None = None
    new_importance: int | None = None
    new_note_type: str | None = None