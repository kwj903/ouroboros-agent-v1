# IMPLEMENTATION SUMMARY

## 2026-04-18 Audit Summary

- 현재 상태는 `COMPLETE` 가 아니라 `부분 구현 + 정합성 수정 필요` 입니다.
- 백엔드 코어와 단위 테스트는 기본적으로 동작합니다.
- 프론트엔드는 현재 빌드가 실패합니다.
- 문서 일부가 실제 구현보다 과장되어 있습니다.

## Quick Facts

- `uv run pytest -q tests`: 통과
- `.venv/bin/python -m app.cli doctor`: 통과
- `uv run pytest -q`: 실패
  - `model-test-space/` 실험 스크립트 수집
  - 오래된 `test_implementation.py`
- 프론트엔드 build: 실패
  - TypeScript toolchain / `tsconfig` 불일치
  - `App.tsx` 에 미정의 state 호출 잔존

## Main Mismatches

1. 문서는 “fully implemented” 라고 하지만 실제로는 build/test 경계가 깨져 있습니다.
2. 일부 문서는 노출 툴을 5개라고 적지만 실제 `EXPOSED_TOOL_NAMES` 는 4개입니다.
3. `README.md` 는 `python3 main.py` 실행을 안내하지만 실제 `main.py` 는 hello 출력만 합니다.
4. 프론트엔드는 노트 검색/읽기 패널을 제공하지만 해당 툴은 현재 agent 에 노출되지 않습니다.

## Priority

1. 프론트엔드 빌드 복구
2. 프롬프트, 실제 노출 툴, 우측 패널 UI 정합성 맞추기
3. `pytest` 기본 수집 범위 정리
4. README 및 handoff 문서 갱신
5. `App.tsx` 분리와 UX 개선

## Reference

- 상세 감사 결과와 작업 순서는 `IMPLEMENTATION_COMPLETE.md` 를 기준으로 진행합니다.
