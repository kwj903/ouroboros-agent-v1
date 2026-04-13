from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.logger import ensure_log_dir, utc_now_iso
from app.long_term_memory import (
    add_memory_note,
    clear_memory_store,
    configure_memory_store,
    delete_memory_note,
    generate_memory_suggestions,
    get_memory_record,
    list_memory_suggestions,
    reset_memory_store_config,
    search_memory_records,
    update_memory_note,
)


MEMORY_EVAL_CASES_FILE = Path("evals/memory_cases.json")
MEMORY_EVAL_RESULTS_FILE = Path("logs/memory_eval_results.jsonl")

EVAL_MEMORY_FILE = Path(".agent_state") / "eval_memory_notes.jsonl"
EVAL_SUGGESTIONS_FILE = Path(".agent_state") / "eval_memory_suggestions.json"


def load_cases() -> list[dict[str, Any]]:
    if not MEMORY_EVAL_CASES_FILE.exists():
        raise FileNotFoundError(f"파일이 없습니다: {MEMORY_EVAL_CASES_FILE}")

    with MEMORY_EVAL_CASES_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _contains_all(text: str, fragments: list[str]) -> tuple[bool, list[str]]:
    missing = [frag for frag in fragments if frag not in text]
    return len(missing) == 0, missing


def _contains_none(text: str, fragments: list[str]) -> tuple[bool, list[str]]:
    found = [frag for frag in fragments if frag in text]
    return len(found) == 0, found


def _seed_memories(items: list[dict[str, Any]]) -> dict[str, str]:
    alias_map: dict[str, str] = {}

    for item in items:
        record = add_memory_note(
            content=item["content"],
            tags=item.get("tags", []),
            importance=item.get("importance", 3),
            note_type=item.get("note_type", "general"),
            source_session_id="memory_eval",
        )
        alias = item.get("alias")
        if alias:
            alias_map[alias] = record["memory_id"]

    return alias_map


def _run_search_case(case: dict[str, Any]) -> dict[str, Any]:
    operation = case["operation"]
    results = search_memory_records(
        operation["query"],
        max_results=operation.get("max_results", 5),
    )
    joined = "\n".join(record.get("content", "") for record in results)

    min_results = case.get("min_results", 0)
    count_pass = len(results) >= min_results

    include_pass, missing = _contains_all(joined, case.get("must_include_contents", []))
    forbid_pass, found = _contains_none(joined, case.get("forbidden_contents", []))

    passed = count_pass and include_pass and forbid_pass

    return {
        "operation_type": "search",
        "passed": passed,
        "result_count": len(results),
        "count_pass": count_pass,
        "include_pass": include_pass,
        "forbid_pass": forbid_pass,
        "missing": missing,
        "found_forbidden": found,
        "joined_result_text": joined,
    }


def _run_update_case(case: dict[str, Any], alias_map: dict[str, str]) -> dict[str, Any]:
    operation = case["operation"]
    target_id = alias_map[operation["target_alias"]]

    updated = update_memory_note(
        memory_id=target_id,
        new_content=operation["new_content"],
    )

    verify_query = operation.get("verify_query", operation["new_content"])
    results = search_memory_records(verify_query, max_results=5)
    joined = "\n".join(record.get("content", "") for record in results)

    include_pass, missing = _contains_all(joined, case.get("must_include_contents", []))
    forbid_pass, found = _contains_none(joined, case.get("forbidden_contents", []))
    update_pass = updated is not None and updated.get("content") == operation["new_content"]

    passed = update_pass and include_pass and forbid_pass

    return {
        "operation_type": "update",
        "passed": passed,
        "update_pass": update_pass,
        "include_pass": include_pass,
        "forbid_pass": forbid_pass,
        "missing": missing,
        "found_forbidden": found,
        "updated_content": updated.get("content") if updated else None,
        "joined_result_text": joined,
    }


def _run_delete_case(case: dict[str, Any], alias_map: dict[str, str]) -> dict[str, Any]:
    operation = case["operation"]
    target_id = alias_map[operation["target_alias"]]

    deleted = delete_memory_note(target_id)
    record_after = get_memory_record(target_id)

    verify_query = operation.get("verify_query", "")
    results = search_memory_records(verify_query, max_results=5) if verify_query else []
    joined = "\n".join(record.get("content", "") for record in results)

    expected_deleted = case.get("expected_deleted", True)
    delete_pass = (deleted is True) and (record_after is None) == expected_deleted
    include_pass, missing = _contains_all(joined, case.get("must_include_contents", []))
    forbid_pass, found = _contains_none(joined, case.get("forbidden_contents", []))

    passed = delete_pass and include_pass and forbid_pass

    return {
        "operation_type": "delete",
        "passed": passed,
        "delete_pass": delete_pass,
        "include_pass": include_pass,
        "forbid_pass": forbid_pass,
        "missing": missing,
        "found_forbidden": found,
        "deleted": deleted,
        "record_after": record_after,
        "joined_result_text": joined,
    }


def _run_suggest_case(case: dict[str, Any]) -> dict[str, Any]:
    operation = case["operation"]

    suggestions = generate_memory_suggestions(
        user_input=operation["user_input"],
        answer=operation["answer"],
        trace_record=operation.get("trace_record", {"steps": []}),
        session_id="memory_eval",
    )

    pending = list_memory_suggestions()
    joined = "\n".join(item.get("content", "") for item in pending)

    min_suggestions = case.get("min_suggestions", 0)
    max_suggestions = case.get("max_suggestions")

    count_pass = len(pending) >= min_suggestions
    if max_suggestions is not None:
        count_pass = count_pass and (len(pending) <= max_suggestions)

    include_pass, missing = _contains_all(joined, case.get("must_include_suggestions", []))
    forbid_pass, found = _contains_none(joined, case.get("forbidden_suggestions", []))

    passed = count_pass and include_pass and forbid_pass

    return {
        "operation_type": "suggest",
        "passed": passed,
        "generated_count": len(suggestions),
        "pending_count": len(pending),
        "count_pass": count_pass,
        "include_pass": include_pass,
        "forbid_pass": forbid_pass,
        "missing": missing,
        "found_forbidden": found,
        "joined_suggestion_text": joined,
    }


def run_case(case: dict[str, Any]) -> dict[str, Any]:
    clear_memory_store()
    alias_map = _seed_memories(case.get("setup_memories", []))

    op_type = case["operation"]["type"]

    if op_type == "search":
        op_result = _run_search_case(case)
    elif op_type == "update":
        op_result = _run_update_case(case, alias_map)
    elif op_type == "delete":
        op_result = _run_delete_case(case, alias_map)
    elif op_type == "suggest":
        op_result = _run_suggest_case(case)
    else:
        raise ValueError(f"지원하지 않는 memory eval operation type: {op_type}")

    return {
        "id": case["id"],
        "description": case.get("description", ""),
        "passed": op_result["passed"],
        "details": op_result,
    }


def save_eval_run(results: list[dict[str, Any]]) -> None:
    ensure_log_dir()

    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    failed = total - passed
    failed_ids = [item["id"] for item in results if not item["passed"]]

    record = {
        "timestamp": utc_now_iso(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "failed_ids": failed_ids,
        "results": results,
    }

    with MEMORY_EVAL_RESULTS_FILE.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False)
        f.write("\n")


def print_case_result(result: dict[str, Any]) -> None:
    status = "PASS" if result["passed"] else "FAIL"
    details = result["details"]

    print("=" * 60)
    print(f"[{status}] {result['id']}")
    print(result["description"])
    print(f"operation: {details.get('operation_type')}")

    for key, value in details.items():
        if key in {"operation_type", "joined_result_text", "joined_suggestion_text"}:
            continue
        print(f"- {key}: {value}")

    preview = details.get("joined_result_text") or details.get("joined_suggestion_text") or ""
    preview = " ".join(str(preview).split())
    if len(preview) > 140:
        preview = preview[:140] + "..."
    if preview:
        print(f"- preview: {preview}")


def main() -> None:
    configure_memory_store(
        memory_file=EVAL_MEMORY_FILE,
        suggestions_file=EVAL_SUGGESTIONS_FILE,
    )

    try:
        cases = load_cases()
        results = [run_case(case) for case in cases]

        print("\n" + "#" * 60)
        print("MEMORY EVAL RUN START")
        print("#" * 60)

        for result in results:
            print_case_result(result)

        total = len(results)
        passed = sum(1 for item in results if item["passed"])
        failed = total - passed

        print("\n" + "#" * 60)
        print("MEMORY EVAL SUMMARY")
        print("#" * 60)
        print(f"총 케이스: {total}")
        print(f"PASS: {passed}")
        print(f"FAIL: {failed}")

        if failed:
            failed_ids = [item["id"] for item in results if not item["passed"]]
            print(f"실패 케이스: {failed_ids}")

        save_eval_run(results)
        print(f"\n저장 완료: {MEMORY_EVAL_RESULTS_FILE.as_posix()}")

    finally:
        reset_memory_store_config()


if __name__ == "__main__":
    main()