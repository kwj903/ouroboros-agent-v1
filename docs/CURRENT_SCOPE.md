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
- `AUTO_MEMORY_SUGGESTIONS=false` 기본값으로 Web/CLI 자동 memory suggestion 생성이 비활성화된 상태
- 수동 장기기억 추가 UI/API와 명시적 `save_memory_note` tool 흐름은 유지되는 상태
- default-off 상태에서 `list_memory_suggestions_api()` 는 기존 suggestion 파일을 삭제하지 않고 `[]` 를 반환하는 상태
- Web UI 는 `memorySuggestions.length > 0` 일 때만 "기억 후보" 섹션을 렌더링하는 상태
- model request view 에 대한 request budget 1차 방어가 들어간 상태
- `build_memory_context()` 가 summary 3000, workspace state JSON 3000, individual memory content 1000, total memory context 8000 chars 기준으로 trim 하는 상태
- `build_recent_history_view()` 가 Web/CLI 공통으로 per message 2000, recent history total 10000 chars 기준 request history view 를 만드는 상태
- tool result 는 trace/tool log 에 raw 로 남고, 다음 model request 의 `role="tool"` content 만 6000 chars 로 trim 되는 상태
- `ModelRequestError` 로 provider 400/context/token/request-too-large 계열 오류를 safe wrapper 로 변환하는 상태
- planner 호출 실패는 새 planner status 없이 기존 `fallback` 으로 direct execution 을 유지하는 상태
- main model call 실패는 raw provider error 대신 복구 가능한 한국어 메시지를 반환하는 상태
- `compact_history_if_needed()` 실패는 compaction 만 skip 하고 chat 흐름은 유지하는 상태
- `build_system_prompt()` 가 구체적인 변경 요청에서 별도 "승인" 발화를 기다리지 않고 `request_` tool 로 approval pending 을 만들도록 유도하는 상태
- `should_hint_immediate_batch_approval()` 가 여러 concrete path 와 변경 의도가 있는 요청에만 동적 batch approval hint 를 붙이는 상태
- 읽기/분석/요약 결과에 의존하는 요청이나 "계획만/구현하지 마" 요청에는 batch approval hint 를 붙이지 않는 상태
- planner prompt / execution message 와 `request_batch_operations` schema description 에 구체적 복수 변경 요청은 첫 턴 approval pending 생성에 사용하고, 모호할 때만 질문한다는 정책이 반영된 상태
- `request_batch_operations` 가 `create_directory` operation type 을 지원하는 상태
- `_execute_create_directory(path, create_parents=True, exist_ok=False)` 가 추가되어 승인 후 실제 디렉터리를 생성하는 상태
- `create_directory` 는 `exist_ok=False` 기본값에서 existing directory 와 existing file path 를 실패 처리하는 상태
- `create_parents=True` 일 때 nested directory 생성을 허용하는 상태
- 단일 빈 폴더 생성도 단일 `create_directory` operation batch 로 approval pending 을 만들 수 있는 상태

## 현재 실제로 만들고 있는 것
현재 코드와 문서 상태를 함께 보면, 이 저장소가 실제로 만들고 있는 것은 아래에 가깝다.
- 사람 승인 기반으로 동작하는 로컬 agent runtime
- CLI와 Web UI를 동시에 갖는 공용 agent core
- session / memory / trace / eval 을 포함한 반복 개선용 개발 환경
- 장기적으로는 모델별 tool-calling 안정성을 다룰 수 있는 운영 기반
- 향후 free-first / local fallback / paid escalation 방향의 model/provider 운영 기반
- 사용자가 요청한 작업의 plan / execution / approval 상태를 Web UI 에서 더 읽기 쉽게 보여주는 운영 화면
- Web client 에서 session snapshot, approval/execution state, memory/suggestion state 의 갱신 경계를 점진적으로 정리하는 상태
- 자동 suggestion 보다는 수동 장기기억과 명시적 기억 저장 요청을 우선하는 memory 운영 방식
- 복합 요청의 model request 크기와 provider 오류 노출을 줄이는 안정화 작업
- 구체적인 복수 파일 변경 요청에서 첫 턴에 batch approval pending 을 생성하도록 tool-calling 정책을 조정하는 작업
- approval workflow 안에서 빈 폴더 생성을 batch operation 으로 지원하는 작업

다만 아래는 아직 정리되지 않은 상태로 보인다.
- 공통 baseline 위에 모델별 capability policy 를 어떤 기준으로 추가할지
- free endpoint 한도와 실패를 어떤 신호로 감지하고 자동 전환할지
- 조건부 planner heuristic 을 어떤 eval 기준으로 튜닝할지
- `App.tsx` 에 남은 상위 orchestration 책임을 어디까지 더 분리할지
- 자동 memory suggestion 을 언제 어떤 기준으로 다시 켤지
- char-based request budget cap 을 실제 provider/model별 token budget 에 맞게 어떻게 조정할지
- batch approval first-turn 정책을 실제 모델별 tool-calling 로그로 얼마나 튜닝해야 할지
- 빈 폴더 생성 요청에서 모델이 `create_directory` operation 을 얼마나 안정적으로 선택하는지

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
- request budget cap 과 provider graceful handling 의 검증과 튜닝
- 구체적인 batch 변경 요청의 첫 턴 approval pending 생성 정책 검증과 튜닝
- batch operation 기반 빈 폴더 생성 지원과 검증

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
- 자연어 요청에서 batch operation payload 를 Python 코드가 직접 생성하는 우회 로직
- top-level `request_create_directory` tool 추가
- 빈 폴더 추적을 위한 `.gitkeep` 자동 생성 정책
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
- 자동 memory suggestion 생성은 default-off 이지만 generator/helper/eval 경로는 남아 있어 향후 optional 재활성화 기준이 필요하다.
- request budget guard / context trimming / provider error graceful handling 은 1차 구현됐지만, char-based cap 이라 provider/model별 token budget 과 정확히 일치하지는 않는다.
- 구체적 batch 요청의 첫 턴 approval 정책은 prompt/schema/hint 기반 유도이며, Python 이 payload 를 직접 생성하지 않으므로 실제 모델별 준수율 확인이 필요하다.
- 빈 폴더 생성은 `create_directory` batch operation 으로 가능하지만, Git 에서 빈 폴더는 추적되지 않으므로 `.gitkeep` 자동 생성 여부는 별도 정책 결정이 필요하다.
- 새 top-level `request_create_directory` tool 은 추가하지 않았고, 단일 빈 폴더 생성도 `request_batch_operations` 의 단일 operation 으로 처리하는 방향이다.
- 최근 memory suggestion default-off slice 는 Graphify 재생성을 포함하지 않았다.
- 최근 request budget / provider graceful handling slices 는 문서 동기화 전 구현됐고, Graphify 재생성은 포함하지 않았다.

## 사람 확인이 필요한 열려 있는 결정사항
아래는 현재 저장소만으로 확정할 수 없고 사람 확인이 필요한 항목이다.
- 공통 baseline 18개 툴 위에 모델별 capability 제한을 언제 어떤 기준으로 추가할지
- free provider 들의 기본 우선순위와 자동 전환 조건을 어떻게 둘지
- 사용자가 provider/model/router 정책을 UI/CLI 에서 어디까지 직접 override 할지
- `should_plan_request()` 의 trigger 기준을 실제 사용 로그와 eval 로 어떻게 조정할지
- `AUTO_MEMORY_SUGGESTIONS` 를 언제 어떤 기준으로 다시 켤지
- request budget cap 값을 실제 로그와 provider 실패 패턴 기준으로 어떻게 튜닝할지
- 구체적 batch approval first-turn 정책이 모델별로 충분히 작동하는지, 필요하면 deterministic policy 계층을 도입할지
- 빈 폴더를 Git 추적 대상으로 만들기 위한 `.gitkeep` 생성 정책을 둘지
- 루트의 기존 handoff / implementation 문서를 어느 수준까지 계속 유지할지

## 상태 판단 메모
현재 이 저장소를 “완료된 제품”으로 보기보다는, “핵심 구조와 공통 baseline tool set 은 존재하지만, provider routing 정책과 운영 UI 고도화가 남아 있는 agent 개발 저장소”로 보는 것이 더 정확해 보인다.
