#!/usr/bin/env python3
"""Manual smoke check for local repository sanity.

This script is intentionally not part of default pytest collection.
Use it when you want a quick import/registry/session sanity check from the repo root.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent import run_agent
from app.approvals import create_pending_action
from app.conversation_state import generate_session_id
from app.logger import utc_now_iso
from app.memory_manager import build_memory_context
from app.paths import LOGS_DIR, NOTES_DIR, OUROBOROS_HOME, STATE_DIR, WORKSPACE_ROOT
from app.tool_registry import EXPOSED_TOOL_NAMES, TOOLS, TOOL_SCHEMAS
from app.tool_trace_manager import persist_tool_trace


EXPECTED_BASELINE_TOOLS = {
    "calculator",
    "search_notes",
    "read_note",
    "get_workspace_info",
    "list_dir",
    "tree_view",
    "read_file",
    "request_search_files",
    "request_create_file",
    "request_write_file",
    "request_replace_text_in_file",
    "request_delete_path",
    "request_batch_operations",
    "save_memory_note",
    "search_memory_notes",
    "list_recent_memory_notes",
    "update_memory_note",
    "delete_memory_note",
}


def main() -> None:
    print("Running manual smoke check...")

    print("\nChecking core callables...")
    assert callable(run_agent), "run_agent should be callable"
    assert callable(create_pending_action), "create_pending_action should be callable"
    assert callable(build_memory_context), "build_memory_context should be callable"
    assert callable(persist_tool_trace), "persist_tool_trace should be callable"
    print("✓ Core callables available")

    print("\nChecking tool registry...")
    schema_names = {
        schema.get("function", {}).get("name")
        for schema in TOOL_SCHEMAS
        if isinstance(schema, dict)
    }
    assert set(TOOLS) == EXPECTED_BASELINE_TOOLS, "Registered tools differ from expected baseline"
    assert EXPOSED_TOOL_NAMES == EXPECTED_BASELINE_TOOLS, "Exposed tool set differs from baseline"
    assert schema_names == EXPECTED_BASELINE_TOOLS, "Tool schemas differ from baseline"
    print(f"✓ Registered tools: {len(TOOLS)}")
    print(f"✓ Exposed tools: {len(EXPOSED_TOOL_NAMES)}")

    print("\nChecking paths and timestamp formatting...")
    assert WORKSPACE_ROOT.exists(), "WORKSPACE_ROOT should exist"
    assert utc_now_iso().endswith("Z"), "utc_now_iso should return a UTC Z suffix"
    print(f"  OUROBOROS_HOME: {OUROBOROS_HOME}")
    print(f"  STATE_DIR: {STATE_DIR}")
    print(f"  LOGS_DIR: {LOGS_DIR}")
    print(f"  NOTES_DIR: {NOTES_DIR}")
    print(f"  WORKSPACE_ROOT: {WORKSPACE_ROOT}")
    print("✓ Paths and timestamp formatting look sane")

    print("\nChecking session id generation...")
    session_id = generate_session_id()
    assert session_id, "Session id should not be empty"
    print(f"✓ Generated session id: {session_id}")

    print("\nManual smoke check passed.")


if __name__ == "__main__":
    main()
