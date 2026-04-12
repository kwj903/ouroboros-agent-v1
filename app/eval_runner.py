from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.agent import run_agent
from app.logger import ensure_log_dir, utc_now_iso


EVAL_CASES_FILE = Path("evals/cases.json")
EVAL_RESULTS_FILE = Path("logs/eval_results.jsonl")


def load_eval_cases() -> list[dict[str, Any]]:
    if not EVAL_CASES_FILE.exists():
        raise FileNotFoundError(f"eval 케이스 파일이 없습니다: {EVAL_CASES_FILE}")

    with EVAL_CASES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_used_tools(trace_record: dict[str, Any]) -> list[str]:
    tools: list[str] = []

    for step in trace_record.get("steps", []):
        for tool_call in step.get("tool_calls", []):
            tool_name = tool_call.get("tool_name")
            if tool_name:
                tools.append(tool_name)

    return tools


def check_tool_match(
    actual_tools: list[str],
    expected_tools: list[str],
    mode: str = "exact",
) -> tuple[bool, str]:
    if mode == "exact":
        passed = actual_tools == expected_tools
        reason = f"expected={expected_tools}, actual={actual_tools}"
        return passed, reason

    if mode == "contains_in_order":
        pointer = 0
        for tool in actual_tools:
            if pointer < len(expected_tools) and tool == expected_tools[pointer]:
                pointer += 1

        passed = pointer == len(expected_tools)
        reason = f"expected ordered subset={expected_tools}, actual={actual_tools}"
        return passed, reason

    if mode == "contains_any":
        passed = all(tool in actual_tools for tool in expected_tools)
        reason = f"expected included={expected_tools}, actual={actual_tools}"
        return passed, reason

    return False, f"지원하지 않는 tool_match_mode: {mode}"


def check_contains(text: str, expected_fragments: list[str]) -> tuple[bool, list[str]]:
    missing = [fragment for fragment in expected_fragments if fragment not in text]
    return len(missing) == 0, missing


def check_forbidden(text: str, forbidden_fragments: list[str]) -> tuple[bool, list[str]]:
    found = [fragment for fragment in forbidden_fragments if fragment in text]
    return len(found) == 0, found


def run_single_eval(case: dict[str, Any]) -> dict[str, Any]:
    question = case["question"]
    output_mode = case.get("output_mode", "cli")
    response_language = case.get("response_language", "ko")

    answer, trace = run_agent(
        question,
        debug=False,
        output_mode=output_mode,
        response_language=response_language,
        return_trace=True,
    )

    actual_tools = extract_used_tools(trace)
    expected_tools = case.get("expected_tools", [])
    tool_match_mode = case.get("tool_match_mode", "exact")

    tool_pass, tool_reason = check_tool_match(
        actual_tools=actual_tools,
        expected_tools=expected_tools,
        mode=tool_match_mode,
    )

    expected_status = case.get("expected_status", "completed")
    actual_status = trace.get("status", "unknown")
    status_pass = actual_status == expected_status

    contains_pass, missing_fragments = check_contains(
        answer,
        case.get("expected_answer_contains", []),
    )

    forbidden_pass, found_forbidden = check_forbidden(
        answer,
        case.get("forbidden_answer_contains", []),
    )

    passed = all([tool_pass, status_pass, contains_pass, forbidden_pass])

    return {
        "id": case.get("id", "unknown"),
        "description": case.get("description", ""),
        "question": question,
        "passed": passed,
        "answer": answer,
        "actual_tools": actual_tools,
        "expected_tools": expected_tools,
        "tool_pass": tool_pass,
        "tool_reason": tool_reason,
        "status_pass": status_pass,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "contains_pass": contains_pass,
        "missing_fragments": missing_fragments,
        "forbidden_pass": forbidden_pass,
        "found_forbidden": found_forbidden,
    }


def print_result(result: dict[str, Any]) -> None:
    status_text = "PASS" if result["passed"] else "FAIL"
    print("=" * 60)
    print(f"[{status_text}] {result['id']}")
    print(result["description"])
    print(f"질문: {result['question']}")
    print(f"사용 툴: {result['actual_tools']}")
    print(f"툴 검사: {result['tool_pass']} ({result['tool_reason']})")
    print(
        f"상태 검사: {result['status_pass']} "
        f"(expected={result['expected_status']}, actual={result['actual_status']})"
    )
    print(f"필수 내용 검사: {result['contains_pass']}")
    if result["missing_fragments"]:
        print(f"  누락: {result['missing_fragments']}")
    print(f"금지 내용 검사: {result['forbidden_pass']}")
    if result["found_forbidden"]:
        print(f"  발견됨: {result['found_forbidden']}")

    shortened_answer = " ".join(result["answer"].split())
    if len(shortened_answer) > 160:
        shortened_answer = shortened_answer[:160] + "..."
    print(f"최종 답변: {shortened_answer}")


def main() -> None:
    cases = load_eval_cases()
    results = [run_single_eval(case) for case in cases]

    total = len(results)
    passed_count = sum(1 for result in results if result["passed"])
    failed_count = total - passed_count

    print("\n" + "#" * 60)
    print("EVAL RUN START")
    print("#" * 60)

    for result in results:
        print_result(result)

    print("\n" + "#" * 60)
    print("EVAL SUMMARY")
    print("#" * 60)
    print(f"총 케이스: {total}")
    print(f"PASS: {passed_count}")
    print(f"FAIL: {failed_count}")

    if failed_count > 0:
        failed_ids = [result["id"] for result in results if not result["passed"]]
        print(f"실패 케이스: {failed_ids}")

    save_eval_run(results)
    print(f"\n저장 완료: {EVAL_RESULTS_FILE.as_posix()}")

def save_eval_run(results: list[dict[str, Any]]) -> None:
    ensure_log_dir()

    total = len(results)
    passed_count = sum(1 for result in results if result["passed"])
    failed_count = total - passed_count
    failed_ids = [result["id"] for result in results if not result["passed"]]

    record = {
        "timestamp": utc_now_iso(),
        "total": total,
        "passed": passed_count,
        "failed": failed_count,
        "failed_ids": failed_ids,
        "results": results,
    }

    with EVAL_RESULTS_FILE.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")

if __name__ == "__main__":
    main()