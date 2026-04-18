# IMPLEMENTATION STATUS AUDIT

## Audit Date
- 2026-04-18

## Current Status
- 전체 상태: `부분 구현 + 문서 과장 상태`
- 백엔드 코어: 기본 구조와 단위 테스트는 통과
- 웹 프론트엔드: 소스는 존재하지만 현재 빌드 실패
- 문서 상태: `IMPLEMENTATION_COMPLETE.md`, `IMPLEMENTATION_SUMMARY.md`, `README.md` 일부 내용이 실제 코드와 불일치

## What Was Checked

### 문서
- `README.md`
- `IMPLEMENTATION_COMPLETE.md`
- `IMPLEMENTATION_SUMMARY.md`
- `PROJECT_HANDOFF_detailed.md`
- `frontend/README.md`

### 백엔드
- `app/agent.py`
- `app/tool_registry.py`
- `app/tools/workspace_tools.py`
- `app/api/main.py`
- `app/api/services.py`
- `app/conversation_state.py`
- `app/memory_manager.py`
- `app/long_term_memory.py`
- `app/cli.py`
- `app/main.py`

### 프론트엔드
- `frontend/src/App.tsx`
- `frontend/src/api.ts`
- `frontend/src/types.ts`
- `frontend/src/index.css`
- `frontend/tsconfig.app.json`
- `frontend/tsconfig.node.json`

## Validation Result

### Verified
- `uv run pytest -q tests` 통과
- 결과: `9 passed, 3 warnings`
- `.venv/bin/python -m app.cli doctor` 정상 실행

### Not Fully Verified
- 실제 LLM provider 연동 end-to-end
- 브라우저에서의 실제 웹 UI 동작
- 실제 승인 workflow의 프론트엔드 상호작용

### Failed Validation
- `uv run pytest -q`
  - `model-test-space/` 아래의 실험용 스크립트가 pytest 수집 대상에 포함되어 실패
  - `test_implementation.py` 가 현재 코드와 맞지 않는 오래된 단정문을 포함
- 프론트엔드 `build`
  - TypeScript 설정과 설치 상태가 맞지 않아 `tsc -b` 단계에서 실패

## Docs vs Implementation Mismatch

### 1. 완료 선언 문서가 실제 상태를 과장함
- 기존 문서는 프로젝트가 “fully implemented and ready for use” 라고 적고 있음
- 실제로는 프론트엔드 빌드가 실패하고, 전체 pytest 도 실패함

### 2. 노출 툴 개수 불일치
- 실제 노출 툴은 4개
- 현재 노출: `read_file`, `request_write_file`, `search_memory_notes`, `list_recent_memory_notes`
- 일부 문서는 5개라고 적고 있고 `request_batch_operations` 까지 노출된 것으로 서술함

### 3. README 실행 가이드 불일치
- `README.md` 는 `python3 main.py` 를 메인 애플리케이션 실행으로 안내
- 실제 `main.py` 는 `Hello from free-model-test!` 만 출력
- 실제 사용 가능한 CLI 진입점은 `app.cli` 와 `ouroboros` 스크립트

### 4. README 테스트 설명 불일치
- `README.md` 는 `tests/` 가 비어 있다고 적음
- 실제로는 `tests/test_agent.py`, `tests/test_tools.py`, `tests/test_memory.py`, `tests/test_model.py` 가 존재

## Implementation Findings

### Backend
- 장점
  - 세션 관리, 승인 워크플로우, 장기 기억, tool trace 구조는 일관됨
  - API 레이어와 CLI가 같은 코어를 공유함
  - 단위 테스트 범위는 좁지만 핵심 함수 smoke test 수준은 존재

- 문제
  - `app/agent.py` 의 시스템 프롬프트는 `calculator`, `search_notes`, `read_note`, `list_dir`, `request_batch_operations` 등을 사용하라고 지시하지만 실제 노출 툴과 맞지 않음
  - `plan_tasks()` 가 모든 요청에 대해 추가 LLM 호출을 수행함
  - `test_implementation.py` 는 현재 상태를 반영하지 못하는 오래된 검증 스크립트임

### Frontend
- 장점
  - 세션, 채팅, 승인, 메모리, 작업 상태, tool log 를 한 화면에서 보려는 정보 구조는 명확함
  - 3-column 레이아웃과 섹션 접기 패턴은 데스크톱 사용성 기준으로는 이해 가능함

- 문제
  - 현재 빌드 실패
  - `frontend/src/App.tsx` 에 선언되지 않은 `setSelectedApprovalId`, `setApprovalModalOpen` 호출이 남아 있음
  - 승인 요청을 임시로 추가할 때 `action_type` 을 무조건 `batch_operations` 로 하드코딩함
  - `toolPanel` 은 노트 검색/읽기 결과를 보여주지만 해당 툴은 현재 agent 에 노출되지 않아 UI 일부가 사실상 죽어 있음
  - `App.tsx` 가 과도하게 비대하고 상태/로직/UI가 한 파일에 밀집되어 유지보수성이 낮음
  - 초기 진입 시 기존 세션을 자동 선택하지 않아 연속성이 떨어짐
  - `window.prompt`, `window.confirm` 의존이 많아 UX가 거칠고 일관되지 않음

## Agent Design Evaluation

### 목적 적합한 점
- 로컬 워크스페이스 대상 승인형 에이전트라는 목적에는 맞는 구조다
- 세션 상태, 기억, 승인, 로그가 분리되어 있어 확장 방향은 괜찮다

### 목적과 어긋나는 점
- “파일 탐색/노트 탐색/배치 작업” 중심 에이전트처럼 설계되어 있으나 실제로는 그 툴들이 대부분 숨겨져 있다
- 프롬프트와 실제 capability 가 다르기 때문에 응답 품질과 안정성이 흔들릴 수 있다
- 항상 planner 를 먼저 태우는 구조는 로컬 실용 에이전트 관점에서 비용과 지연을 키운다

## Frontend UX Evaluation

### 괜찮은 점
- 정보 패널의 분류는 이해 가능하다
- 채팅, 승인, 메모리, 작업 상태를 동시에 보려는 설계 의도는 프로젝트 목적과 맞는다

### 부족한 점
- 빌드가 안 되므로 현재는 “사용 편의성” 이전에 전달 가능 상태가 아니다
- 사용자가 바로 이해해야 하는 승인 정보가 summary 문자열 파싱에 과도하게 의존한다
- 모바일 대응은 레이아웃이 한 열로 바뀌는 수준이고, 상호작용 설계가 충분히 다듬어지지 않았다
- 시각 디자인은 무난하지만 밀도가 높고, 우선순위 대비 강조 체계가 약하다

## Priority Tasks

### P0. 실행 가능 상태 복구
1. 프론트엔드 toolchain 정합성 복구
   - 실제 설치된 TypeScript 버전과 `tsconfig` 옵션을 맞춘다
   - 필요하면 `node_modules` 재설치 또는 lockfile 기준 재동기화
2. `App.tsx` 빌드 에러 제거
   - 미정의 state 제거 또는 실제 modal state 구현
   - 임시 approval 객체의 `action_type` 하드코딩 제거

### P1. 에이전트 capability 정합성 복구
1. 프롬프트와 노출 툴을 일치시킨다
   - 방법 A: 실제 필요한 툴을 노출
   - 방법 B: 숨겨진 툴 언급을 프롬프트와 UI에서 제거
2. `toolPanel` 과 우측 사이드바 항목을 실제 사용 가능한 툴 기준으로 재정의한다

### P2. 검증 체계 정리
1. `pytest` 기본 수집 범위에서 `model-test-space/` 를 제외한다
2. `test_implementation.py` 를 삭제 또는 최신 상태 기준으로 갱신한다
3. 최소 smoke test를 추가한다
   - API health
   - approval request/approve cycle
   - session create/select

### P3. 문서 정합성 복구
1. `README.md` 실행/테스트 가이드 수정
2. handoff 문서의 “현재 상태” 섹션을 audit 결과에 맞게 갱신
3. “완료” 표현 대신 “검증 완료 범위 / 미검증 범위” 로 나눈다

### P4. 프론트엔드 구조 개선
1. `App.tsx` 분리
   - `SessionSidebar`
   - `ChatPanel`
   - `ApprovalPanel`
   - `MemoryPanel`
   - `WorkspacePanel`
2. `window.prompt/confirm` 제거
3. 입력 UX 개선
   - Enter/Ctrl+Enter 정책
   - 실패 시 optimistic message 롤백 또는 재시도 UX

## Recommended Working Order
1. P0 프론트엔드 빌드 복구
2. P1 에이전트 capability 정합성 복구
3. P2 테스트 경계 정리
4. P3 문서 수정
5. P4 프론트엔드 리팩터링

## Practical Conclusion
- 이 프로젝트는 “구조가 없는 상태”는 아니다
- 하지만 현재 기준으로는 “완료”가 아니라 “핵심 백엔드 구조는 있고, 프론트엔드/검증/문서 정합성이 무너진 상태”에 가깝다
- 다음 작업은 새로운 기능 추가보다 `빌드 복구 → capability 정합성 → 검증 체계 정리` 순서가 맞다
