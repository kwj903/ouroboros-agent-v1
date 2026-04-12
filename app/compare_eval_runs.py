from __future__ import annotations

import json
from pathlib import Path
from typing import Any


EVAL_RESULTS_FILE = Path("logs/eval_results.jsonl")


def load_eval_runs() -> list[dict[str, Any]]:
    if not EVAL_RESULTS_FILE.exists():
        return []

    records: list[dict[str, Any]] = []

    with EVAL_RESULTS_FILE.open("r", encoding="utf-8") as f:
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


def build_result_map(run_record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result_map: dict[str, dict[str, Any]] = {}

    for result in run_record.get("results", []):
        case_id = result.get("id", "unknown")
        result_map[case_id] = result

    return result_map


def summarize_run(label: str, run_record: dict[str, Any]) -> None:
    print(f"\n[{label}]")
    print(f"timestamp: {run_record.get('timestamp', 'unknown')}")
    print(f"total: {run_record.get('total', 0)}")
    print(f"passed: {run_record.get('passed', 0)}")
    print(f"failed: {run_record.get('failed', 0)}")
    print(f"failed_ids: {run_record.get('failed_ids', [])}")


def compare_two_runs(
    previous_run: dict[str, Any],
    latest_run: dict[str, Any],
) -> None:
    prev_passed = previous_run.get("passed", 0)
    prev_failed = previous_run.get("failed", 0)

    latest_passed = latest_run.get("passed", 0)
    latest_failed = latest_run.get("failed", 0)

    passed_delta = latest_passed - prev_passed
    failed_delta = latest_failed - prev_failed

    prev_failed_ids = set(previous_run.get("failed_ids", []))
    latest_failed_ids = set(latest_run.get("failed_ids", []))

    newly_failed = sorted(latest_failed_ids - prev_failed_ids)
    recovered = sorted(prev_failed_ids - latest_failed_ids)
    still_failing = sorted(prev_failed_ids & latest_failed_ids)

    print("\n" + "=" * 60)
    print("EVAL RUN COMPARISON")
    print("=" * 60)

    summarize_run("PREVIOUS", previous_run)
    summarize_run("LATEST", latest_run)

    print("\n[DELTA]")
    print(f"passed 변화량: {passed_delta:+d}")
    print(f"failed 변화량: {failed_delta:+d}")

    print("\n[REGRESSION CHECK]")
    if newly_failed:
        print(f"새로 실패한 케이스: {newly_failed}")
    else:
        print("새로 실패한 케이스 없음")

    print("\n[RECOVERY CHECK]")
    if recovered:
        print(f"회복된 케이스: {recovered}")
    else:
        print("회복된 케이스 없음")

    print("\n[STILL FAILING]")
    if still_failing:
        print(f"계속 실패 중인 케이스: {still_failing}")
    else:
        print("계속 실패 중인 케이스 없음")

    prev_result_map = build_result_map(previous_run)
    latest_result_map = build_result_map(latest_run)

    interesting_case_ids = newly_failed + recovered + still_failing

    if interesting_case_ids:
        print("\n" + "=" * 60)
        print("CASE DETAILS")
        print("=" * 60)

        for case_id in interesting_case_ids:
            prev_result = prev_result_map.get(case_id)
            latest_result = latest_result_map.get(case_id)

            print(f"\ncase_id: {case_id}")

            if prev_result:
                print(f"- 이전 passed: {prev_result.get('passed')}")
                print(f"  이전 툴: {prev_result.get('actual_tools')}")
                print(f"  이전 missing: {prev_result.get('missing_fragments')}")
                print(f"  이전 forbidden: {prev_result.get('found_forbidden')}")

            if latest_result:
                print(f"- 최신 passed: {latest_result.get('passed')}")
                print(f"  최신 툴: {latest_result.get('actual_tools')}")
                print(f"  최신 missing: {latest_result.get('missing_fragments')}")
                print(f"  최신 forbidden: {latest_result.get('found_forbidden')}")


def main() -> None:
    runs = load_eval_runs()

    if not runs:
        print("비교할 eval 결과가 없습니다. 먼저 eval_runner를 실행하세요.")
        return

    if len(runs) < 2:
        print("비교하려면 최소 2개의 eval 실행 결과가 필요합니다.")
        print(f"현재 저장된 실행 수: {len(runs)}")
        return

    previous_run = runs[-2]
    latest_run = runs[-1]

    compare_two_runs(previous_run, latest_run)


if __name__ == "__main__":
    main()