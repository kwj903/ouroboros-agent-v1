# ARCHITECTURE

## 상위 수준 시스템 구조
현재 저장소는 `single-agent core + interface adapters` 구조로 보는 것이 가장 가깝다.

상위 구조:
- `app/`: agent core, state, approval, memory, logging, evaluation
- `app/api/`: FastAPI 기반 Web adapter
- `frontend/`: React 기반 Web client
- `tests/`, `evals/`: 최소 단위 테스트와 eval 케이스
- `logs/`, `~/.ouroboros/*`: trace, eval 결과, 상태 저장 위치

개념 흐름:
1. 사용자가 CLI 또는 Web에서 요청한다.
2. core 가 session state 와 memory context 를 조합한다.
3. model abstraction 이 LLM 호출을 수행한다.
4. model 이 tool call 을 반환하면 registry 기반으로 Python 함수가 실행된다.
5. 승인 필요 작업이면 pending approval 상태로 중단한다.
6. 결과는 history, workspace state, tool trace, memory suggestion 으로 반영된다.

## 주요 모듈과 책임
### Agent Core
- `app/agent.py`
  - system prompt 구성
  - 조건부 planner 호출 판단 (`should_plan_request`)
  - planning helper (`plan_tasks`)
  - planner 결과 정규화와 trace metadata 생성
  - model 호출 루프
  - tool dispatch
  - pending approval 감지
  - trace record 생성

### Model Abstraction
- `app/model.py`
  - `create_response()` 로 OpenAI-compatible API 호출을 래핑
  - provider 교체는 주로 환경 변수 (`ALL_API_KEY`, `ALL_BASE_URL`, `ALL_MODEL`) 수준에서 수행

### Tool Layer
- `app/tool_registry.py`
  - 전체 툴 등록
  - tool schema 정의
  - 현재 노출 툴 필터링
- `app/tools/workspace_tools.py`
  - workspace 읽기/쓰기 요청
  - approval payload 생성
  - 승인 후 실제 파일 작업 실행
- `app/tools/search_notes.py`, `read_note.py`, `calculator.py`
  - 보조 툴 구현
- `app/long_term_memory.py`
  - 장기 기억 CRUD, 검색, suggestion 생성용 helper/tool

### State / Memory / Approval
- `app/conversation_state.py`
  - 세션 디렉터리 구조
  - history / rolling summary / workspace state / meta / tool log 저장
- `app/memory_manager.py`
  - memory context 조립
  - history compaction
  - workspace state 반영
- `app/approvals.py`
  - pending action 저장 및 상태 전이
- `app/runtime_context.py`
  - 현재 session id 전달

### Web Adapter
- `app/api/main.py`
  - FastAPI 엔드포인트 정의
  - CORS 및 static serving
- `app/api/services.py`
  - chat/session/memory/approval/tool panel orchestration
- `app/api/schemas.py`
  - request/response schema
- `frontend/src/App.tsx`
  - Web client 의 상위 상태 container
  - session snapshot 로딩과 적용
  - execution state 와 global sidebar state 갱신 분리
  - polling 범위 조정
- `frontend/src/components/*`
  - session, chat, operations sidebar 렌더링
  - 현재 App orchestration slice 에서는 component props contract 를 변경하지 않았다.

### CLI Adapter
- `app/cli.py`
  - `doctor`, `api`, `web`, `tui` 진입점
  - dev 모드에서 backend/frontend 프로세스 조합
- `app/main.py`
  - legacy CLI/TUI 성격의 대화 루프

### Observability / Evaluation
- `app/logger.py`
  - agent trace JSONL 기록
- `app/tool_trace_manager.py`
  - 세션별 tool log 저장
  - tool panel 용 데이터 파생
  - planner / latest execution / pending approval 요약 파생
- `app/eval_runner.py`
  - 일반 tool-calling eval
- `app/memory_eval_runner.py`
  - memory 동작 eval
- `app/analyze_traces.py`
  - trace 요약/최근 실행 분석

## 모델 추상화 계층
현재 모델 추상화는 얇은 wrapper 수준이다.
- `create_response(messages, tools=None)` 가 핵심 인터페이스다.
- provider 차이는 adapter class 가 아니라 환경 변수 기반 endpoint/model 설정으로 다룬다.
- 장점
  - 단순하다.
  - OpenAI-compatible endpoint 를 바꾸기 쉽다.
- 한계
  - 모델별 capability policy, retry 전략, structured tool behavior 차이는 아직 별도 계층으로 분리되어 있지 않다.
  - 무료 endpoint 한도 초과 시 자동 전환, local fallback, paid escalation 같은 실행 정책은 아직 없다.

향후 이 계층에서 분리될 수 있는 후보:
- 모델별 tool-calling capability profile
- provider-specific fallback / retry
- tool choice policy
- evaluation-aware model selection

사용자 방향성 기준의 다음 목표:
- 현재 18개 툴은 공통 baseline 으로 유지
- free API endpoint 우선 사용
- 한도 또는 실패 시 local model 로 fallback
- 고급 작업 또는 명시적 선택 시 paid endpoint 사용
- 사용자 override 와 자동 routing 을 함께 지원

이 방향은 아직 구현이 아니라 설계 목표다. 현재 저장소에는 이를 위한 별도 router, budget policy, provider health state 저장 계층이 없다.

## tool registry 및 tool-calling 흐름
현재 흐름은 아래와 같다.
1. `tool_registry.py` 가 툴 함수와 JSON schema 를 등록한다.
2. `EXPOSED_TOOL_NAMES` 로 현재 모델에 보여줄 툴 집합을 제한한다.
3. `agent.py` 가 `should_plan_request()` 로 planner 필요 여부를 판단한다.
4. 복합/다단계 요청이면 `plan_tasks()` 를 호출하고, 단순 요청이나 단일 작업이면 `planner.status="skipped"` 로 직접 실행한다.
5. planner 결과는 정규화되어 `trace_record["planner"]` 에 metadata 로 남는다.
6. `agent.py` 가 `create_response(..., tools=TOOL_SCHEMAS)` 를 호출한다.
7. model 이 tool call 을 반환하면 `agent.py` 가 registry 에서 Python 함수를 찾는다.
8. 함수 실행 결과가 일반 문자열이면 다음 model step 에 tool result 로 전달된다.
9. 결과가 `__PENDING_APPROVAL__` 형식이면 agent는 `awaiting_approval` 로 종료한다.
10. 승인/거부는 `approvals.py` 와 `workspace_tools.py` 의 실행 함수가 처리한다.
11. 결과는 history, workspace state, tool trace 에 반영된다.
12. `tool_trace_manager.py` 는 planner metadata 를 `__planner__` synthetic log 로 남기고, tool panel 에 `plan_summary`, `latest_execution`, `pending_approval` 를 파생한다.

현재 확인된 중요한 사실:
- 전체 등록 툴은 18개다.
- 현재 노출 툴은 18개다.
- 현재는 등록된 툴 전체가 노출되어 있고, 이후에는 모델별 capability policy 로 다시 분리될 가능성이 있다.

## planning / execution / review 경계
현재 코드는 planning / execution / review 가 완전히 분리된 구조는 아니다.

### 현재 존재하는 것
- planning:
  - `agent.py` 의 `should_plan_request()` 가 복합/다단계 요청만 planner 대상으로 분류
  - planner 대상 요청은 `plan_tasks()` 가 task list 로 분해
  - planner 생략 요청은 `planner.status="skipped"` 로 기록하고 직접 실행
  - planner 가 1개 task 만 반환하면 `planner.status="planned_single"` 로 기록하고 직접 실행
  - planner fallback / invalid 결과는 기존처럼 `used=false` 로 기록하고 직접 실행
  - planner 결과는 정규화되어 `trace_record["planner"]` 로 남는다.
- execution:
  - `run_agent()` 내부의 model 호출, tool dispatch, approval handling
- review 보조:
  - `eval_runner.py`
  - `memory_eval_runner.py`
  - `analyze_traces.py`
  - `tool_trace_manager.py`

### 현재 없는 것
- 명시적 reviewer agent layer
- 독립된 execution policy engine
- 별도 planning service / planner model 분리
- 승인 전후 품질 gate
- 조건부 planner heuristic 의 장기 eval / tuning 체계

### 향후 분리 필요 영역
- planner 호출 조건의 회귀 평가와 비용 통제
- execution policy 와 exposed tools 정합성
- review 결과를 TASKS / CURRENT_SCOPE 로 다시 연결하는 운영 루프

## 상태 저장과 데이터 흐름
### 세션 상태
세션별 저장은 `conversation_state.py` 기준으로 파일 기반이다.
- `history.jsonl`
- `rolling_summary.md`
- `workspace_state.json`
- `meta.json`
- `tool_log.jsonl`

### 전역/공용 상태
- approval 상태: `pending_actions.json`
- trace 로그: `agent_trace.jsonl`
- eval 결과: `logs/eval_results.jsonl`, `logs/memory_eval_results.jsonl`
- memory store: 장기 기억 파일 및 suggestion 파일

### 데이터 흐름
1. 요청 수신
2. 세션 생성/로드
3. 최근 history + summary + relevant memories 조합
4. model/tool execution
5. pending approval 또는 final answer 반환
6. trace / session history / workspace state / memory suggestion 반영
7. Web 또는 CLI 에 결과 표시

### Web client 상태 흐름
현재 `frontend/src/App.tsx` 는 아직 상위 orchestration container 역할을 하지만, 최근 slice 에서 아래 경계가 추가됐다.
- `loadSessionSnapshot(sessionId)`: session history, workspace state, tool logs, tool panel 을 한 번에 로드한다.
- `applySessionSnapshot(sessionId, snapshot)`: 현재 활성 session 과 일치하는 snapshot 만 UI state 에 적용한다.
- `clearSessionSnapshot()`: 선택된 session 이 없을 때 session-bound state 를 비운다.
- `activeSessionRequestRef`: 늦게 도착한 이전 session snapshot 이 현재 session UI 에 섞이는 것을 막는다.
- `refreshExecutionState(sessionId)`: approvals, workspace state, tool logs, tool panel 을 갱신한다.
- `refreshGlobalSidebarState()`: memories 와 memory suggestions 를 갱신한다.

`refreshSessionView()` 는 session snapshot 로딩과 execution/global refresh 경계를 함께 사용한다. polling 은 더 이상 memory/suggestions 를 포함한 넓은 sidebar refresh 를 돌지 않고, loading 중이거나 approvals 가 있을 때 `refreshExecutionState(currentSessionId)` 중심으로만 동작한다.

이번 App orchestration slice 는 `frontend/src/api.ts`, `frontend/src/types.ts`, `ChatPanel`, `OperationsSidebar` 의 public contract 를 변경하지 않았다.

## 로깅 / 관찰성 / 평가 / 테스트 전략
### 로깅 / 관찰성
- 전역 trace: `logger.py` 가 JSONL 로 저장
- 세션별 tool logs: `tool_trace_manager.py`
- planner summary: `tool_trace_manager.py` 가 `__planner__` synthetic log 로 저장
- planner 상태: `planned`, `skipped`, `planned_single`, `fallback`, `invalid`
- tool panel: `plan_summary`, `latest_execution`, `pending_approval`, note/file read 요약 제공
- workspace state: 최근 읽기/쓰기/요청 상태 추적
- Web UI 는 tool panel / workspace state / approvals 를 통해 계획, 최근 실행, 승인 대기 상태 일부를 보여준다.

### 평가
- `eval_runner.py` 가 tool usage, status, answer fragment 기준 eval 수행
- `memory_eval_runner.py` 가 memory search/update/delete/suggestion 동작 평가
- `analyze_traces.py` 가 최근 trace 요약과 도구 사용 분포를 제공

### 테스트
- 현재 `tests/` 는 최소 unit test 중심이다.
- 기본 `pytest` 수집 범위는 `pyproject.toml` 에서 `tests/` 로 제한되어 있다.
- 실제 확인된 기본 검증:
  - `uv run pytest -q` 통과
  - `uv run pytest -q tests/test_agent.py` 통과
  - frontend production build 통과. 현재 실행 환경에서는 explicit Node PATH 로 확인했다.
  - `.venv/bin/python test_implementation.py` 통과
- `test_implementation.py` 는 기본 테스트 스위트가 아니라 수동 smoke check 스크립트로 유지된다.

## CLI와 Web 계층의 분리 방식
CLI와 Web은 같은 core 를 공유하고, 입출력 adapter 만 다르다.

### 공통 core
- `agent.py`
- `model.py`
- `tool_registry.py`
- `workspace_tools.py`
- `approvals.py`
- `conversation_state.py`
- `memory_manager.py`

### CLI 계층
- `app/main.py`: 대화 루프와 로컬 명령 처리
- `app/cli.py`: 실행/서빙 진입점

### Web 계층
- `app/api/main.py`, `app/api/services.py`: HTTP interface
- `frontend/src/api.ts`: HTTP client
- `frontend/src/App.tsx`: 전체 상태 orchestration container. 현재 session snapshot helper 와 execution/global refresh helper 를 갖고 있으며, polling 은 execution state 중심으로 축소되어 있다.
- `frontend/src/components/SessionSidebar.tsx`: 세션 관련 UI
- `frontend/src/components/ChatPanel.tsx`: 채팅, planner summary, pending approval banner, 툴 로그 UI
- `frontend/src/components/OperationsSidebar.tsx`: 계획/실행 요약, 승인, 작업 상태, memory, tool panel UI

이 구조 덕분에 기능 자체는 공통이고, 최근에는 build, capability 정합성, planner/execution summary 표시, Web session/execution refresh 경계를 우선 정리했다. 다만 `App.tsx` 는 여전히 상위 container 이며, planner metadata 는 아직 workspace state 에 직접 반영되지 않는다.

## 향후 subagent가 개입할 수 있는 지점
현재 저장소에는 subagent orchestration 이 구현되어 있지 않다.
다만 운영 관점에서 아래 지점은 향후 subagent 개입 후보로 적합하다.
- code review
- test failure triage
- trace/log analysis
- architecture critique
- eval failure clustering

주의:
- 이것은 현재 구현된 기능이 아니라 향후 운영 확장 지점이다.
- 사람 승인과 실행 환경 허용이 없는 상태에서 기본 동작으로 도입하지 않는다.
