from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from app.logger import utc_now_iso
from app.runtime_context import get_current_session_id


DEFAULT_MEMORY_FILE = Path(".agent_state") / "memory_notes.jsonl"
DEFAULT_SUGGESTIONS_FILE = Path(".agent_state") / "memory_suggestions.json"

_MEMORY_FILE_OVERRIDE: Path | None = None
_SUGGESTIONS_FILE_OVERRIDE: Path | None = None


def configure_memory_store(
    memory_file: str | Path | None = None,
    suggestions_file: str | Path | None = None,
) -> None:
    global _MEMORY_FILE_OVERRIDE, _SUGGESTIONS_FILE_OVERRIDE

    _MEMORY_FILE_OVERRIDE = Path(memory_file) if memory_file is not None else None
    _SUGGESTIONS_FILE_OVERRIDE = (
        Path(suggestions_file) if suggestions_file is not None else None
    )


def reset_memory_store_config() -> None:
    global _MEMORY_FILE_OVERRIDE, _SUGGESTIONS_FILE_OVERRIDE
    _MEMORY_FILE_OVERRIDE = None
    _SUGGESTIONS_FILE_OVERRIDE = None


def _get_memory_file() -> Path:
    return _MEMORY_FILE_OVERRIDE or DEFAULT_MEMORY_FILE


def _get_suggestions_file() -> Path:
    return _SUGGESTIONS_FILE_OVERRIDE or DEFAULT_SUGGESTIONS_FILE


def _ensure_state_files() -> None:
    memory_file = _get_memory_file()
    suggestions_file = _get_suggestions_file()

    memory_file.parent.mkdir(parents=True, exist_ok=True)

    if not memory_file.exists():
        memory_file.write_text("", encoding="utf-8")

    if not suggestions_file.exists():
        suggestions_file.write_text("[]", encoding="utf-8")


def clear_memory_store() -> None:
    _ensure_state_files()
    _get_memory_file().write_text("", encoding="utf-8")
    _get_suggestions_file().write_text("[]", encoding="utf-8")


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[가-힣A-Za-z0-9_./-]+", text.lower())


def _load_all_memory_records() -> list[dict[str, Any]]:
    _ensure_state_files()

    records: list[dict[str, Any]] = []
    with _get_memory_file().open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _write_all_memory_records(records: list[dict[str, Any]]) -> None:
    _ensure_state_files()
    with _get_memory_file().open("w", encoding="utf-8") as f:
        for record in records:
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")


def _append_record(record: dict[str, Any]) -> None:
    _ensure_state_files()
    with _get_memory_file().open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")


def _load_suggestions() -> list[dict[str, Any]]:
    _ensure_state_files()
    try:
        return json.loads(_get_suggestions_file().read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_suggestions(items: list[dict[str, Any]]) -> None:
    _ensure_state_files()
    _get_suggestions_file().write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_memory_note(
    content: str,
    tags: list[str] | None = None,
    importance: int = 3,
    note_type: str = "general",
    source_session_id: str | None = None,
) -> dict[str, Any]:
    content = content.strip()
    if not content:
        raise ValueError("기억 내용은 비어 있을 수 없습니다.")

    if tags is None:
        tags = []

    cleaned_tags = [tag.strip() for tag in tags if tag.strip()]
    importance = max(1, min(5, int(importance)))

    record = {
        "memory_id": uuid.uuid4().hex[:10],
        "timestamp": utc_now_iso(),
        "content": content,
        "tags": cleaned_tags,
        "importance": importance,
        "note_type": note_type,
        "source_session_id": source_session_id or get_current_session_id(),
    }
    _append_record(record)
    return record


def list_recent_memory_notes(limit: int = 10) -> list[dict[str, Any]]:
    records = _load_all_memory_records()
    records.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return records[:limit]


def get_memory_record(memory_id: str) -> dict[str, Any] | None:
    records = _load_all_memory_records()
    for record in records:
        if record.get("memory_id") == memory_id:
            return record
    return None


def delete_memory_note(memory_id: str) -> bool:
    records = _load_all_memory_records()
    new_records = [record for record in records if record.get("memory_id") != memory_id]

    if len(new_records) == len(records):
        return False

    _write_all_memory_records(new_records)
    return True


def update_memory_note(
    memory_id: str,
    new_content: str | None = None,
    new_tags: list[str] | None = None,
    new_importance: int | None = None,
    new_note_type: str | None = None,
) -> dict[str, Any] | None:
    records = _load_all_memory_records()
    updated: dict[str, Any] | None = None

    for record in records:
        if record.get("memory_id") != memory_id:
            continue

        if new_content is not None:
            cleaned = new_content.strip()
            if not cleaned:
                raise ValueError("새 기억 내용은 비어 있을 수 없습니다.")
            record["content"] = cleaned

        if new_tags is not None:
            record["tags"] = [tag.strip() for tag in new_tags if tag.strip()]

        if new_importance is not None:
            record["importance"] = max(1, min(5, int(new_importance)))

        if new_note_type is not None and new_note_type.strip():
            record["note_type"] = new_note_type.strip()

        updated = record
        break

    if updated is None:
        return None

    _write_all_memory_records(records)
    return updated


def _score_memory_record(record: dict[str, Any], query: str) -> float:
    query = query.strip()
    if not query:
        return 0.0

    query_tokens = _tokenize(query)
    if not query_tokens:
        return 0.0

    content = record.get("content", "")
    tags = record.get("tags", [])
    full_text = f"{content} {' '.join(tags)}".lower()

    lexical_score = 0.0

    lower_tags = [tag.lower() for tag in tags]

    for token in query_tokens:
        lexical_score += full_text.count(token) * 2
        if token in lower_tags:
            lexical_score += 2

    if query.lower() in full_text:
        lexical_score += 4

    # 핵심: 텍스트 관련도가 0이면 importance / recency를 더하지 않고 바로 제외
    if lexical_score <= 0:
        return 0.0

    score = lexical_score

    importance = int(record.get("importance", 3))
    score += importance * 0.5

    timestamp = record.get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            days_old = max((datetime.now(dt.tzinfo) - dt).days, 0)
            score += max(0.0, 2.0 - (days_old * 0.05))
        except Exception:
            pass

    return score


def search_memory_records(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    records = _load_all_memory_records()

    scored: list[tuple[float, dict[str, Any]]] = []
    for record in records:
        score = _score_memory_record(record, query)
        if score > 0:
            scored.append((score, record))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [record for _, record in scored[:max_results]]


def format_memory_records(records: list[dict[str, Any]]) -> str:
    if not records:
        return "장기 기억이 없습니다."

    lines = []
    for index, record in enumerate(records, start=1):
        tags = ", ".join(record.get("tags", [])) or "-"
        lines.append(
            f"{index}. id={record.get('memory_id')} | "
            f"type={record.get('note_type')} | "
            f"importance={record.get('importance')} | "
            f"tags={tags}\n"
            f"   {record.get('content', '')}"
        )
    return "\n".join(lines)


def save_memory_note_tool(
    content: str,
    tags: str = "",
    importance: int = 3,
    note_type: str = "general",
) -> str:
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    record = add_memory_note(
        content=content,
        tags=tag_list,
        importance=importance,
        note_type=note_type,
    )
    return (
        f"장기 기억 저장 완료\n"
        f"memory_id: {record['memory_id']}\n"
        f"type: {record['note_type']}\n"
        f"importance: {record['importance']}\n"
        f"content: {record['content']}"
    )


def search_memory_notes_tool(query: str, max_results: int = 5) -> str:
    records = search_memory_records(query, max_results=max_results)
    if not records:
        return f"관련 장기 기억을 찾지 못했습니다. query={query!r}"

    return (
        f"장기 기억 검색 결과 - query={query!r}\n"
        f"{format_memory_records(records)}"
    )


def list_recent_memory_notes_tool(limit: int = 10) -> str:
    records = list_recent_memory_notes(limit=limit)
    return format_memory_records(records)


def update_memory_note_tool(
    memory_id: str,
    new_content: str,
    new_tags: str = "",
    new_importance: int | None = None,
    new_note_type: str | None = None,
) -> str:
    tag_list = [tag.strip() for tag in new_tags.split(",") if tag.strip()]
    updated = update_memory_note(
        memory_id=memory_id,
        new_content=new_content,
        new_tags=tag_list if new_tags != "" else None,
        new_importance=new_importance,
        new_note_type=new_note_type,
    )
    if updated is None:
        return f"ERROR: memory_id를 찾지 못했습니다: {memory_id}"

    return (
        f"장기 기억 수정 완료\n"
        f"id: {updated['memory_id']}\n"
        f"type: {updated['note_type']}\n"
        f"importance: {updated['importance']}\n"
        f"content: {updated['content']}"
    )


def delete_memory_note_tool(memory_id: str) -> str:
    deleted = delete_memory_note(memory_id)
    if not deleted:
        return f"ERROR: memory_id를 찾지 못했습니다: {memory_id}"
    return f"장기 기억 삭제 완료\nid: {memory_id}"


def _extract_candidate_sentences(text: str) -> list[str]:
    chunks = re.split(r"[.\n!?]+", text)
    sentences: list[str] = []

    for chunk in chunks:
        sentence = " ".join(chunk.split()).strip()
        if 8 <= len(sentence) <= 120:
            sentences.append(sentence)

    return sentences


def _normalize_for_similarity(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w가-힣./ -]+", " ", text)
    text = " ".join(text.split())
    return text


def _token_set(text: str) -> set[str]:
    return set(_tokenize(_normalize_for_similarity(text)))


def _jaccard_similarity(a: str, b: str) -> float:
    a_tokens = _token_set(a)
    b_tokens = _token_set(b)

    if not a_tokens or not b_tokens:
        return 0.0

    intersection = len(a_tokens & b_tokens)
    union = len(a_tokens | b_tokens)
    if union == 0:
        return 0.0

    return intersection / union


def _is_low_value_assistant_sentence(sentence: str) -> bool:
    lowered = sentence.lower().strip()

    low_value_patterns = [
        "알겠습니다",
        "진행하겠습니다",
        "도와드리겠습니다",
        "확인했습니다",
        "저장되었습니다",
        "기억하겠습니다",
        "처리하겠습니다",
        "진행할게요",
        "하겠습니다",
    ]

    if any(pattern in sentence for pattern in low_value_patterns):
        return True

    # 지나치게 짧은 assistant 문장은 보통 후보 가치가 낮음
    if len(sentence) < 15:
        return True

    return False


def _infer_note_type_and_tags(sentence: str) -> tuple[str, list[str], int]:
    lowered = sentence.lower()
    tags: list[str] = []
    note_type = "general"
    importance = 3

    if "기본" in sentence and ("언어" in sentence or "응답" in sentence):
        note_type = "preference"
        tags.extend(["language", "default"])
        importance = 5

    if "세션" in sentence and ("동작" in sentence or "기반" in sentence):
        note_type = "project_rule"
        tags.extend(["session", "architecture"])
        importance = max(importance, 4)

    if "규칙" in sentence or "항상" in sentence or "반드시" in sentence:
        note_type = "project_rule"
        tags.extend(["rule"])
        importance = max(importance, 4)

    if ".md" in lowered or ".py" in lowered or "/" in sentence:
        tags.extend(["path"])
        importance = max(importance, 4)

    if "readme" in lowered:
        tags.extend(["readme", "document"])
        importance = max(importance, 4)

    if "프로젝트" in sentence:
        tags.extend(["project"])

    deduped_tags = list(dict.fromkeys(tags))
    return note_type, deduped_tags, importance


def _looks_memory_worthy(sentence: str) -> bool:
    keywords = [
        "기본",
        "항상",
        "규칙",
        "반드시",
        "세션",
        "프로젝트",
        "응답 언어",
        "README",
        ".md",
        ".py",
        "문서",
    ]
    return any(keyword.lower() in sentence.lower() for keyword in keywords)


def _trace_contains_memory_write(trace_record: dict[str, Any]) -> bool:
    for step in trace_record.get("steps", []):
        for tool_call in step.get("tool_calls", []):
            if tool_call.get("tool_name") in {
                "save_memory_note",
                "update_memory_note",
                "delete_memory_note",
            }:
                return True
    return False


def generate_memory_suggestions(
    user_input: str,
    answer: str,
    trace_record: dict[str, Any],
    session_id: str,
) -> list[dict[str, Any]]:
    if _trace_contains_memory_write(trace_record):
        return []

    lowered_input = user_input.strip().lower()
    local_commands = {
        "remember",
        "memories",
        "search_memory",
        "forget",
        "update_memory",
        "memory_suggestions",
        "save_suggestion",
        "drop_suggestion",
    }
    if any(lowered_input.startswith(cmd + " ") or lowered_input == cmd for cmd in local_commands):
        return []

    existing_memory_contents = {
        record.get("content", "").strip()
        for record in _load_all_memory_records()
    }
    suggestions = _load_suggestions()
    existing_suggestion_contents = {
        item.get("content", "").strip()
        for item in suggestions
        if item.get("status") == "pending"
    }

    candidates: list[dict[str, Any]] = []
    seen_contents: set[str] = set()

    user_sentences = [
        sentence
        for sentence in _extract_candidate_sentences(user_input)
        if _looks_memory_worthy(sentence)
    ]

    assistant_sentences = [
        sentence
        for sentence in _extract_candidate_sentences(answer)
        if _looks_memory_worthy(sentence)
    ]

    # 1) 사용자 문장 우선 후보화
    for sentence in user_sentences:
        if sentence in existing_memory_contents:
            continue
        if sentence in existing_suggestion_contents:
            continue
        if sentence in seen_contents:
            continue

        note_type, tags, importance = _infer_note_type_and_tags(sentence)
        candidates.append(
            {
                "suggestion_id": uuid.uuid4().hex[:8],
                "timestamp": utc_now_iso(),
                "source_session_id": session_id,
                "source_role": "user",
                "content": sentence,
                "tags": tags,
                "importance": importance,
                "note_type": note_type,
                "status": "pending",
            }
        )
        seen_contents.add(sentence)

    # 2) assistant 문장은 더 엄격하게 필터링
    for sentence in assistant_sentences:
        if _is_low_value_assistant_sentence(sentence):
            continue

        # 사용자 문장과 너무 비슷하면 제외
        too_similar_to_user = any(
            _jaccard_similarity(sentence, user_sentence) >= 0.55
            for user_sentence in user_sentences
        )
        if too_similar_to_user:
            continue

        # 이미 뽑힌 후보와 너무 비슷하면 제외
        too_similar_to_candidate = any(
            _jaccard_similarity(sentence, existing_candidate["content"]) >= 0.60
            for existing_candidate in candidates
        )
        if too_similar_to_candidate:
            continue

        if sentence in existing_memory_contents:
            continue
        if sentence in existing_suggestion_contents:
            continue
        if sentence in seen_contents:
            continue

        note_type, tags, importance = _infer_note_type_and_tags(sentence)

        # assistant 후보는 기본적으로 importance를 조금 낮게 시작
        importance = max(1, importance - 1)

        candidates.append(
            {
                "suggestion_id": uuid.uuid4().hex[:8],
                "timestamp": utc_now_iso(),
                "source_session_id": session_id,
                "source_role": "assistant",
                "content": sentence,
                "tags": tags,
                "importance": importance,
                "note_type": note_type,
                "status": "pending",
            }
        )
        seen_contents.add(sentence)

    if not candidates:
        return []

    suggestions.extend(candidates)
    _save_suggestions(suggestions)
    return candidates


def list_memory_suggestions() -> list[dict[str, Any]]:
    items = _load_suggestions()
    pending = [item for item in items if item.get("status") == "pending"]
    pending.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return pending


def format_memory_suggestions(items: list[dict[str, Any]]) -> str:
    if not items:
        return "저장 제안된 장기 기억이 없습니다."

    lines = ["장기 기억 저장 후보:"]
    for index, item in enumerate(items, start=1):
        tags = ", ".join(item.get("tags", [])) or "-"
        lines.append(
            f"{index}. suggestion_id={item.get('suggestion_id')} | "
            f"type={item.get('note_type')} | "
            f"importance={item.get('importance')} | "
            f"tags={tags}\n"
            f"   {item.get('content')}"
        )
    return "\n".join(lines)


def _resolve_suggestion_choice(choice: str) -> dict[str, Any] | None:
    items = list_memory_suggestions()
    if not items:
        return None

    choice = choice.strip()
    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(items):
            return items[index]
        return None

    for item in items:
        if item.get("suggestion_id") == choice:
            return item

    return None


def accept_memory_suggestion(choice: str) -> dict[str, Any] | None:
    target = _resolve_suggestion_choice(choice)
    if target is None:
        return None

    record = add_memory_note(
        content=target["content"],
        tags=target.get("tags", []),
        importance=target.get("importance", 3),
        note_type=target.get("note_type", "general"),
        source_session_id=target.get("source_session_id"),
    )

    items = _load_suggestions()
    for item in items:
        if item.get("suggestion_id") == target.get("suggestion_id"):
            item["status"] = "accepted"
            item["accepted_memory_id"] = record["memory_id"]

    _save_suggestions(items)
    return record


def dismiss_memory_suggestion(choice: str) -> dict[str, Any] | None:
    target = _resolve_suggestion_choice(choice)
    if target is None:
        return None

    items = _load_suggestions()
    for item in items:
        if item.get("suggestion_id") == target.get("suggestion_id"):
            item["status"] = "dismissed"

    _save_suggestions(items)
    return target