# CHANGELOG

이 파일에는 실제로 수행된 변경만 기록한다.
과거 이력은 추정해서 추가하지 않는다.

## Unreleased
- Initial documentation bootstrap
  - Added `docs/PRODUCT.md`
  - Added `docs/ARCHITECTURE.md`
  - Added `docs/CURRENT_SCOPE.md`
  - Added `docs/TASKS.md`
  - Added `docs/CHANGELOG.md`
  - Added repository `AGENTS.md`
  - Updated `README.md` to point to `docs/` and `AGENTS.md` as operational source-of-truth
- Tool-calling alignment and baseline stability update
  - Expanded `EXPOSED_TOOL_NAMES` to match the currently registered tool surface
  - Updated `app/agent.py` prompt rules to align with the exposed tool set
  - Removed broken optimistic approval modal calls from `frontend/src/App.tsx`
  - Updated Web workspace state display to reflect more of the current agent state
  - Restored frontend production build by making `frontend/tsconfig.*` compatible with the installed TypeScript toolchain
  - Constrained default pytest discovery to `tests/` via `pyproject.toml`
- Web UI stabilization and validation cleanup
  - Split the Web UI into `SessionSidebar`, `ChatPanel`, `OperationsSidebar`, and `CollapsibleSection`
  - Improved Web session bootstrap to auto-load the latest session state instead of starting from an empty shell
  - Replaced UTC timestamp generation in `app/logger.py` with timezone-aware code to remove deprecation warnings
  - Reworked `test_implementation.py` into a manual smoke check that matches the current 18-tool baseline
  - Updated `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/CURRENT_SCOPE.md`, and `docs/TASKS.md` to reflect the approved baseline-tool and future routing direction
- Planner/execution summary data path update
  - Added structured planner metadata to agent traces
  - Added `__planner__` synthetic tool log entries for plan summaries
  - Extended tool panel data with `plan_summary`, `latest_execution`, and `pending_approval`
  - Updated ChatPanel to separate planner logs from raw tool logs
  - Added an OperationsSidebar 계획/실행 요약 section
  - Did not implement model/provider routing, App orchestration refactor, or workspace-state planner reflection in this slice
- Conditional planner invocation slice
  - Added `should_plan_request()` so planner calls are skipped for simple requests and direct single-action requests
  - Kept complex / multi-step requests on the existing `plan_tasks()` path
  - Recorded skipped direct execution as `planner.status="skipped"` while preserving `trace_record["planner"]`
  - Recorded single-task planner output as `planner.status="planned_single"` and kept fallback / invalid planner output on direct execution
  - Preserved the `__planner__` synthetic log and `tool_panel` summary path
  - Added focused tests for planner trigger rules, skipped execution, complex planning, fallback, and single-task planning
  - Verified with `uv run pytest -q tests/test_agent.py`
  - Verified with `uv run pytest -q`
  - Verified with `.venv/bin/python test_implementation.py`
  - Verified frontend build with explicit Node PATH
  - Did not implement model/provider routing, provider/router layers, App orchestration refactor, workspace-state planner reflection, or UI structure changes in this slice
- App.tsx orchestration stabilization slices
  - Unified session snapshot loading inside `frontend/src/App.tsx` with `loadSessionSnapshot`, `applySessionSnapshot`, and `clearSessionSnapshot`
  - Added `activeSessionRequestRef` guard so stale session snapshots do not overwrite the current session view
  - Added `refreshExecutionState(sessionId)` for approvals, workspace state, tool logs, and tool panel refresh
  - Added `refreshGlobalSidebarState()` for memories and memory suggestions refresh
  - Reduced polling so it no longer refreshes memories or memory suggestions on the broad sidebar path
  - Kept the existing API contract and UI props contract unchanged
  - Verified frontend build with explicit Node PATH
  - Verified with `uv run pytest -q`
  - Did not modify `api.ts`, `types.ts`, `ChatPanel`, `OperationsSidebar`, `memory_manager.py`, provider routing, Graphify outputs, or UI structure in these slices
