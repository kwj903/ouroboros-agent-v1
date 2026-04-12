from __future__ import annotations

from app.agent import run_agent
from app.settings import DEFAULT_OUTPUT_MODE, DEFAULT_RESPONSE_LANGUAGE


def main() -> None:
    print("Mini Agent CLI")
    print("종료하려면 exit 또는 quit 입력")
    print("-" * 40)

    debug_mode = True
    output_mode = DEFAULT_OUTPUT_MODE
    response_language = DEFAULT_RESPONSE_LANGUAGE

    while True:
        user_input = input("\n질문 > ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("종료합니다.")
            break

        if not user_input:
            continue

        answer = run_agent(
            user_input,
            debug=debug_mode,
            output_mode=output_mode,
            response_language=response_language,
        )
        print(f"\n응답 > {answer}")


if __name__ == "__main__":
    main()