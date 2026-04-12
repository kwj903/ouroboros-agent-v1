from __future__ import annotations

from pathlib import Path
from typing import Iterable


NOTES_DIR = Path("notes")
ALLOWED_EXTENSIONS = {".md", ".txt"}


def _tokenize(text: str) -> list[str]:
    return [token.strip().lower() for token in text.split() if token.strip()]


def _iter_note_files() -> Iterable[Path]:
    if not NOTES_DIR.exists():
        return []

    return [
        path
        for path in NOTES_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS
    ]


def _make_excerpt(content: str, keywords: list[str], max_length: int = 220) -> str:
    lowered = content.lower()

    best_index = -1
    for keyword in keywords:
        idx = lowered.find(keyword)
        if idx != -1:
            best_index = idx
            break

    if best_index == -1:
        excerpt = content[:max_length]
    else:
        start = max(0, best_index - 60)
        end = min(len(content), best_index + 160)
        excerpt = content[start:end]

    excerpt = " ".join(excerpt.split())
    return excerpt[:max_length]


def search_notes(query: str, max_results: int = 3) -> str:
    """
    notes/ 폴더 아래의 .md, .txt 파일에서
    query 키워드를 단순 검색해 관련도가 높은 파일을 반환한다.
    """
    query = query.strip()
    if not query:
        return "검색어가 비어 있습니다."

    keywords = _tokenize(query)
    if not keywords:
        return "유효한 검색어가 없습니다."

    files = list(_iter_note_files())
    if not files:
        return "notes 폴더에 검색할 파일이 없습니다."

    scored_results: list[tuple[int, Path, str]] = []

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding="utf-8-sig")
            except Exception:
                continue
        except Exception:
            continue

        lowered = content.lower()

        score = 0
        for keyword in keywords:
            score += lowered.count(keyword)

        # 파일명에 키워드가 있으면 가중치 조금 추가
        filename_lower = file_path.name.lower()
        for keyword in keywords:
            if keyword in filename_lower:
                score += 2

        if score > 0:
            excerpt = _make_excerpt(content, keywords)
            scored_results.append((score, file_path, excerpt))

    if not scored_results:
        return f"'{query}'와 관련된 노트를 찾지 못했습니다."

    scored_results.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_results[:max_results]

    lines: list[str] = []
    lines.append(f"검색어: {query}")
    lines.append("관련 노트 검색 결과:")

    for idx, (score, file_path, excerpt) in enumerate(top_results, start=1):
        lines.append(
            f"{idx}. 파일: {file_path.as_posix()} | 점수: {score} | 내용 미리보기: {excerpt}"
        )

    return "\n".join(lines)
