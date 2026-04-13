from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean

from app.paths import LOGS_DIR


TRACE_FILE = LOGS_DIR / "agent_trace.jsonl"


def load_traces() -> list[dict]:
    if not TRACE_FILE.exists():
        return []

    records: list[dict] = []

    with TRACE_FILE.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print(f"[WARN] {line_number}번째 줄 JSON 파싱 실패")
                continue

            records.append(record)

    return records


def summarize_traces(records: list[dict]) -> None:
    if not records:
        print("분석할 로그가 없습니다. 먼저 에이전트를 몇 번 실행해보세요.")
        return

    total_runs = len(records)
    status_counter = Counter(record.get("status", "unknown") for record in records)
    output_mode_counter = Counter(record.get("output_mode", "unknown") for record in records)
    language_counter = Counter(record.get("response_language", "unknown") for record in records)

    step_counts = [len(record.get("steps", [])) for record in records]
    avg_steps = mean(step_counts) if step_counts else 0.0

    tool_counter = Counter()
    tool_error_counter = Counter()

    for record in records:
        for step in record.get("steps", []):
            for tool_call in step.get("tool_calls", []):
                tool_name = tool_call.get("tool_name", "unknown")
                tool_counter[tool_name] += 1

                if tool_call.get("error"):
                    tool_error_counter[tool_name] += 1

    print("=" * 50)
    print("Agent Trace Summary")
    print("=" * 50)

    print(f"총 실행 수: {total_runs}")
    print(f"평균 step 수: {avg_steps:.2f}")

    print("\n상태 분포:")
    for status, count in status_counter.most_common():
        print(f"- {status}: {count}")

    print("\n출력 모드 분포:")
    for mode, count in output_mode_counter.most_common():
        print(f"- {mode}: {count}")

    print("\n응답 언어 분포:")
    for language, count in language_counter.most_common():
        print(f"- {language}: {count}")

    print("\n툴 사용 횟수:")
    if tool_counter:
        for tool_name, count in tool_counter.most_common():
            print(f"- {tool_name}: {count}")
    else:
        print("- 툴 사용 기록 없음")

    print("\n툴 에러 횟수:")
    if tool_error_counter:
        for tool_name, count in tool_error_counter.most_common():
            print(f"- {tool_name}: {count}")
    else:
        print("- 에러 없음")


def print_recent_runs(records: list[dict], limit: int = 5) -> None:
    if not records:
        return

    print("\n" + "=" * 50)
    print(f"최근 실행 {min(limit, len(records))}건")
    print("=" * 50)

    recent_records = records[-limit:]

    for index, record in enumerate(recent_records, start=1):
        timestamp = record.get("timestamp", "unknown")
        status = record.get("status", "unknown")
        output_mode = record.get("output_mode", "unknown")
        response_language = record.get("response_language", "unknown")
        user_input = record.get("user_input", "")
        final_answer = record.get("final_answer", "") or ""
        steps = record.get("steps", [])

        used_tools: list[str] = []
        for step in steps:
            for tool_call in step.get("tool_calls", []):
                tool_name = tool_call.get("tool_name", "unknown")
                used_tools.append(tool_name)

        deduped_tools = list(dict.fromkeys(used_tools))

        print(f"\n[{index}] {timestamp}")
        print(f"상태: {status}")
        print(f"출력 모드 / 언어: {output_mode} / {response_language}")
        print(f"질문: {user_input}")
        print(f"사용 툴: {', '.join(deduped_tools) if deduped_tools else '(없음)'}")

        shortened_answer = " ".join(final_answer.split())
        if len(shortened_answer) > 120:
            shortened_answer = shortened_answer[:120] + "..."
        print(f"최종 답변: {shortened_answer}")


def main() -> None:
    records = load_traces()
    summarize_traces(records)
    print_recent_runs(records, limit=5)


if __name__ == "__main__":
    main()