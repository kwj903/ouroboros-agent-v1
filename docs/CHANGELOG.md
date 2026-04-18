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
