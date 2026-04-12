from __future__ import annotations

from pathlib import Path


NOTES_DIR = Path("notes").resolve()
ALLOWED_EXTENSIONS = {".md", ".txt"}


def _is_within_notes_dir(path: Path) -> bool:
    try:
        path.resolve().relative_to(NOTES_DIR)
        return True
    except ValueError:
        return False


def read_note(path: str, max_chars: int = 4000) -> str:
    """
    notes/ 폴더 아래의 특정 노트 파일 내용을 읽는다.
    path는 반드시 notes/ 하위 파일이어야 한다.
    """
    if not path.strip():
        return "ERROR: path가 비어 있습니다."

    target = Path(path)

    if not target.is_absolute():
        target = target.resolve()
    else:
        target = target.resolve()

    if not _is_within_notes_dir(target):
        return "ERROR: notes 폴더 바깥 파일은 읽을 수 없습니다."

    if not target.exists():
        return f"ERROR: 파일이 존재하지 않습니다: {path}"

    if not target.is_file():
        return f"ERROR: 파일이 아닙니다: {path}"

    if target.suffix.lower() not in ALLOWED_EXTENSIONS:
        return f"ERROR: 허용되지 않은 파일 형식입니다: {target.suffix}"

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            content = target.read_text(encoding="utf-8-sig")
        except Exception as e:
            return f"ERROR: 파일을 읽는 중 인코딩 오류가 발생했습니다: {e}"
    except Exception as e:
        return f"ERROR: 파일을 읽는 중 예외가 발생했습니다: {e}"

    content = content.strip()
    if not content:
        return f"파일: {target.as_posix()}\n내용이 비어 있습니다."

    if len(content) > max_chars:
        content = content[:max_chars] + "\n...(이하 생략)"

    return f"파일: {target.as_posix()}\n전체 내용:\n{content}"