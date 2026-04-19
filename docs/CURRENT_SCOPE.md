# CURRENT_SCOPE

초안 문서다. 이 문서는 승인본이 아니며, 현재 저장소와 기존 문서를 바탕으로 정리한 현재 범위 초안이다.

## 이미 존재하는 것으로 보이는 것
현재 저장소 근거상 아래는 이미 존재하는 구현으로 보인다.
- Python 기반 agent core (`app/agent.py`)
- OpenAI-compatible model 호출 wrapper (`app/model.py`)
- tool registry 와 schema 기반 tool-calling 구조 (`app/tool_registry.py`)
- approval workflow 와 pending action 저장 (`app/approvals.py`, `app/tools/workspace_tools.py`)
- 세션 상태 저장과 rolling summary (`app/conversation_state.py`, `app/memory_manager.py`)
- 장기 기억 CRUD 와 suggestion 흐름 (`app/long_term_memory.py`)
- FastAPI 기반 Web API (`app/api/`)
- React 기반 Web UI 소스 (`frontend/src/`)
- CLI / web / api / tui 진입점 (`app/cli.py`)
- 기본 단위 테스트 (`tests/`)
- eval / memory eval / trace analysis 보조 스크립트 (`app/eval_runner.py`, `app/memory_eval_runner.py`, `app/analyze_traces.py`)
- 현재 등록된 18개 툴이 공통 baseline tool set 으로 노출된 상태
- planner metadata 가 trace 와 tool panel 경로로 구조화된 상태
- planner 가 모든 요청에서 호출되지 않고, `should_plan_request()` 기준으로 복합/다단계 요청에서만 호출되는 상태
- 단순 요청/단일 작업은 `planner.status="skipped"` 로 기록되고 직접 실행되는 상태
- Web UI 에서 plan summary / latest execution / pending approval 요약을 볼 수 있는 상태
- `frontend/src/App.tsx` 내부에 session snapshot 로딩 경로가 존재하는 상태 (`loadSessionSnapshot`, `applySessionSnapshot`, `clearSessionSnapshot`)
- `activeSessionRequestRef` 로 늦게 도착한 이전 session snapshot 이 현재 session state 에 적용되지 않도록 guard 하는 상태
- `frontend/src/App.tsx` 내부에서 execution state refresh 와 global sidebar refresh 가 분리된 상태 (`refreshExecutionState`, `refreshGlobalSidebarState`)

## 현재 실제로 만들고 있는 것
현재 코드와 문서 상태를 함께 보면, 이 저장소가 실제로 만들고 있는 것은 아래에 가깝다.
- 사람 승인 기반으로 동작하는 로컬 agent runtime
- CLI와 Web UI를 동시에 갖는 공용 agent core
- session / memory / trace / eval 을 포함한 반복 개선용 개발 환경
- 장기적으로는 모델별 tool-calling 안정성을 다룰 수 있는 운영 기반
- 향후 free-first / local fallback / paid escalation 방향의 model/provider 운영 기반
- 사용자가 요청한 작업의 plan / execution / approval 상태를 Web UI 에서 더 읽기 쉽게 보여주는 운영 화면
- Web client 에서 session snapshot, approval/execution state, memory/suggestion state 의 갱신 경계를 점진적으로 정리하는 상태

다만 아래는 아직 정리되지 않은 상태로 보인다.
- 공통 baseline 위에 모델별 capability policy 를 어떤 기준으로 추가할지
- free endpoint 한도와 실패를 어떤 신호로 감지하고 자동 전환할지
- 조건부 planner heuristic 을 어떤 eval 기준으로 튜닝할지
- `App.tsx` 에 남은 상위 orchestration 책임을 어디까지 더 분리할지

## 지금 인스코프인 것으로 보이는 것
현재 저장소 상태와 최근 감사 결과 기준으로 지금 인스코프 초안은 아래다.
- 문서 중심 운영 구조 정리
- CLI와 Web이 공유하는 agent core 안정화
- approval workflow 유지 및 개선
- session / memory / trace / eval 기반 반복 개발
- 공통 baseline tool set 과 prompt 정합성 유지
- 프론트엔드 build 복구와 Web UI 구조 안정화
- pytest 기본 수집 범위와 검증 기준 정리
- model/provider routing 정책 초안 정리
- planner/execution summary 를 trace/tool panel/Web UI 에서 읽기 쉽게 만드는 작업
- 조건부 planner 호출 정책의 검증과 튜닝
- Web session snapshot 과 execution/global sidebar refresh 경계 안정화

## 지금은 아웃오브스코프인 것으로 보이는 것
현재 단계에서 아래는 아웃오브스코프로 보는 것이 안전하다.
- 무승인 자동 파일 변경 agent
- 다중 사용자 협업 기능
- 완성된 multi-agent / subagent orchestration 제품화
- 완성된 multi-provider auto-router 제품화
- provider/router 계층 구현
- DB 도입이나 persistence 계층 전면 교체
- 프로덕션 배포/운영 체계 완성
- 문서 승인 없이 새 tool 대량 추가
- `memory_manager.py` 에 planner/execution summary 를 직접 반영하는 변경
- App orchestration 과 무관한 UI 구조 재작업

## 현재 확인된 known issues
아래는 실제 저장소 근거가 있는 현재 문제 또는 주의사항이다.
- `frontend/src/App.tsx` 는 session snapshot helper 와 execution/global refresh helper 를 갖게 됐지만, 상위 container 로서 session/data orchestration 로직은 여전히 많이 남아 있다.
- polling 은 memory/suggestions 까지 넓게 갱신하지 않고 execution state 중심으로 축소됐지만, polling interval 자체와 세부 정책은 아직 단순하다.
- 이번 App orchestration slice 는 API contract 와 UI props contract 를 유지했고, `api.ts`, `types.ts`, `ChatPanel`, `OperationsSidebar` 는 변경하지 않았다.
- `frontend/src/components/OperationsSidebar.tsx` 에 계획/실행 요약 섹션은 추가됐지만, approval/memory/observability UI 를 더 나눌 여지는 남아 있다.
- approval UX 는 동작하지만 여전히 `prompt` / `confirm` 기반 상호작용이 남아 있다.
- model/provider routing 은 아직 단일 `ALL_*` 환경변수 구조를 넘어서지 못했고, free/local/paid 자동 전환은 구현되지 않았다.
- `test_implementation.py` 는 이제 수동 smoke check 이지만, 정식 테스트 체계와는 별개로 유지된다.
- planner metadata 는 tool trace/tool panel 에는 반영되지만, 이번 slice 에서 `memory_manager.py` 를 바꾸지 않았으므로 workspace state 에는 직접 반영되지 않는다.
- `__planner__` synthetic log 는 ChatPanel 에서 raw tool log 와 분리해 표시하지만, 장기적으로 raw tool log 소비자가 늘어나면 이 convention 을 다시 점검해야 한다.
- 조건부 planner heuristic 은 구현됐지만, 아직 실제 사용 로그 기반 false positive / false negative 튜닝은 부족하다.
- 이번 planner 조건부 호출 slice 는 `routing`, `App.tsx` 정리, `memory_manager.py` workspace state 반영, UI 구조 재작업을 포함하지 않았다.
- 최근 App orchestration slice 는 `routing`, provider/router, `memory_manager.py` workspace state 반영, Graphify 재생성, UI 구조 재작업을 포함하지 않았다.

## 사람 확인이 필요한 열려 있는 결정사항
아래는 현재 저장소만으로 확정할 수 없고 사람 확인이 필요한 항목이다.
- 공통 baseline 18개 툴 위에 모델별 capability 제한을 언제 어떤 기준으로 추가할지
- free provider 들의 기본 우선순위와 자동 전환 조건을 어떻게 둘지
- 사용자가 provider/model/router 정책을 UI/CLI 에서 어디까지 직접 override 할지
- `should_plan_request()` 의 trigger 기준을 실제 사용 로그와 eval 로 어떻게 조정할지
- 루트의 기존 handoff / implementation 문서를 어느 수준까지 계속 유지할지

## 상태 판단 메모
현재 이 저장소를 “완료된 제품”으로 보기보다는, “핵심 구조와 공통 baseline tool set 은 존재하지만, provider routing 정책과 운영 UI 고도화가 남아 있는 agent 개발 저장소”로 보는 것이 더 정확해 보인다.
