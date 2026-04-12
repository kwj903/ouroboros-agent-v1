from __future__ import annotations

from app.agent import run_agent
from app.settings import DEFAULT_RESPONSE_LANGUAGE


def main() -> None:
    question = "내 노트에서 RAG 관련 내용을 자세히 요약해줘"
    answer = run_agent(
        question,
        debug=True,
        output_mode="markdown",
        response_language=DEFAULT_RESPONSE_LANGUAGE,
    )

    print("\n===== MARKDOWN OUTPUT =====\n")
    print(answer)


if __name__ == "__main__":
    main()