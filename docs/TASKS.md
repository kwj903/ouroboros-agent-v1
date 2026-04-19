# TASKS

이 문서는 현재 저장소 상태를 바탕으로 작성한 우선순위 초안이다.
승인 전 초안이며, 각 작업은 사람 검토 후 실행 범위를 확정해야 한다.

## Now
### 1. request budget / provider graceful handling 회귀 검증과 튜닝
- 왜 중요한지: request view trimming 과 provider graceful handling 은 1차 구현됐지만, 현재 cap 은 char-based 이므로 실제 provider/model token budget 과 실패 패턴에 맞춘 튜닝이 필요하다.
- 선행조건 / 의존성: 현재 `build_memory_context()` cap, `build_recent_history_view()`, tool result request-view trim, `ModelRequestError` 경로 유지
- 기대 결과물: 실제 trace/provider failure 기준 cap 조정안, oversized request 회귀 fixture, 사용자 안내 메시지 개선 필요 여부 판단
- 검증 방법: `uv run pytest -q tests/test_agent.py`, `uv run pytest -q tests/test_model.py`, `uv run pytest -q tests/test_memory.py`, 실제 oversized request 수동 시나리오 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 2. planner 조건부 호출 정책 검증 / 튜닝
- 왜 중요한지: `should_plan_request()` 기준의 조건부 planner 호출은 구현됐지만, 실제 사용 로그 기반 false positive / false negative 튜닝은 아직 부족하다.
- 선행조건 / 의존성: 현재 `trace_record["planner"]`, `__planner__` synthetic log, `skipped` / `planned_single` 상태 유지
- 기대 결과물: 단순 요청, 단일 승인 요청, 복합 요청, fallback/invalid/1-task 케이스에 대한 더 명확한 eval 또는 fixture 기준
- 검증 방법: `uv run pytest -q tests/test_agent.py`, 실제 trace 샘플에서 planner 상태 분포 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 3. Graphify 갱신 실행
- 왜 중요한지: 최근 memory suggestion default-off 와 request budget / provider graceful handling slices 는 여러 core 파일과 테스트를 바꿨지만 Graphify 재생성은 포함하지 않았다.
- 선행조건 / 의존성: 관련 문서 동기화 완료, Graphify 재생성 실행에 대한 사람 승인
- 기대 결과물: `AUTO_MEMORY_SUGGESTIONS`, request-view trim, `build_recent_history_view()`, `ModelRequestError`, planner fallback handling 이 반영된 최신 Graphify 산출물
- 검증 방법: 갱신 후 `graphify-out/GRAPH_REPORT.md` 에 관련 허브/노드가 반영됐는지 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 4. Web UI 상태 orchestration 남은 경계 점검
- 왜 중요한지: `App.tsx` 에 session snapshot helper 와 execution/global refresh helper 는 추가됐지만, 상위 container 의 데이터 동기화 책임은 아직 남아 있다.
- 선행조건 / 의존성: 현재 build 통과 상태 유지, session/approval/memory API contract 유지, `loadSessionSnapshot` / `refreshExecutionState` / `refreshGlobalSidebarState` 경로 유지
- 기대 결과물: 이미 분리된 session snapshot, execution state, global sidebar refresh 경계가 실제 사용자 흐름에서 충분한지 확인하고, 남은 개선이 필요하면 더 작은 slice 로 재정의
- 검증 방법: frontend build 통과, `uv run pytest -q`, 세션 선택/생성/삭제, 채팅, 승인/거부, memory suggestion 흐름 수동 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 5. planner/execution summary 와 workspace state 연결 검토
- 왜 중요한지: 현재 planner/execution summary 는 tool panel 에는 반영되지만 workspace state 에는 직접 반영되지 않는다.
- 선행조건 / 의존성: 현재 `tool_trace_manager.py`, `memory_manager.py`, session workspace state 구조 확인
- 기대 결과물: workspace state 에 plan/execution summary 를 반영할지 여부와 최소 구현 범위 확정
- 검증 방법: 승인 대기, tool result, workspace state, tool panel 이 서로 충돌하지 않는지 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

## Next
### 6. model/provider routing 정책 초안 구체화
- 왜 중요한지: 사용자의 실제 운영 목표가 free API endpoint 우선, local fallback, paid escalation 이므로 현재 단일 `ALL_*` 설정만으로는 장기 방향을 담을 수 없다.
- 선행조건 / 의존성: 현재 `app/model.py`, `app/settings.py`, 공통 baseline 18개 툴 정책 이해
- 기대 결과물: provider 우선순위, fallback 조건, user override 방식, 추적/로그 요구사항이 정리된 설계 초안
- 검증 방법: `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/CURRENT_SCOPE.md` 와 충돌 없는지 검토
- 실행 전에 사람 승인이 필요한지 여부: 예

### 7. approval UX 재정의
- 왜 중요한지: 이 프로젝트의 핵심 가치가 사람 승인 기반 운영이므로 승인 경험이 명확해야 한다.
- 선행조건 / 의존성: 현재 approval workflow 와 Web UI 상태 확인
- 기대 결과물: 승인 요청 노출, 상세 정보 표시, approve/reject 흐름이 더 명확한 UI/CLI 정책
- 검증 방법: 승인 요청 생성부터 승인/거부 반영까지 end-to-end 점검
- 실행 전에 사람 승인이 필요한지 여부: 예

### 8. tool panel / observability 패널 재설계
- 왜 중요한지: 1차 요약은 추가됐지만, 장기적으로는 tool panel / tool log / workspace state 의 역할 경계를 더 명확히 해야 한다.
- 선행조건 / 의존성: 현재 expanded tool set 과 운영 패널 구조 검토
- 기대 결과물: 실제 agent가 사용하는 정보만 보여주는 Web 운영 패널
- 검증 방법: tool logs, workspace state, panel 데이터가 실제 실행 결과와 맞는지 비교
- 실행 전에 사람 승인이 필요한지 여부: 예

### 9. memory suggestion optional mode / eval 경계 정리
- 왜 중요한지: 자동 memory suggestion 은 default-off 가 됐지만 helper/eval/UI 경로는 남아 있으므로, 언제 다시 켤지와 어떤 검증을 통과해야 하는지 기준이 필요하다.
- 선행조건 / 의존성: `AUTO_MEMORY_SUGGESTIONS=false` 기본값 유지, 수동 장기기억 추가와 명시적 `save_memory_note` 흐름 보존
- 기대 결과물: optional 재활성화 기준, stale suggestion 상태 처리 기준, memory eval 범위 정리
- 검증 방법: `uv run pytest -q tests/test_memory.py`, 수동 장기기억 추가와 explicit memory tool 요청 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

## Later
### 10. 모델별 capability policy 도입
- 왜 중요한지: 장기 목표가 모델별 안정적 tool-calling 이므로, 모델 차이를 정책으로 다루는 계층이 필요하다.
- 선행조건 / 의존성: baseline/확장 tool 구분 규칙, provider router 1차 도입, eval 체계 정리
- 기대 결과물: 모델별 tool exposure / planning policy / failure handling 기준 초안
- 검증 방법: 정책 문서화, 최소 eval 케이스 설계
- 실행 전에 사람 승인이 필요한지 여부: 예

### 11. provider router 구현 시작
- 왜 중요한지: free/local/paid 정책은 제품 목표의 핵심 운영 가치와 연결되므로 결국 실행 계층에 반영되어야 한다.
- 선행조건 / 의존성: routing 정책 초안 승인, 설정 인터페이스 합의, trace/log 요구사항 합의
- 기대 결과물: 현재 단일 `ALL_*` 설정 위에 최소한의 provider/model 선택 계층 추가
- 검증 방법: 설정별 경로 선택 단위 테스트 또는 수동 검증, 기존 chat 흐름 회귀 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 12. evaluation 체계 확장
- 왜 중요한지: 회귀와 품질 변화를 더 체계적으로 감지해야 반복 개발이 안정적이다.
- 선행조건 / 의존성: 기본 테스트 경계 정리, current capability 확정
- 기대 결과물: 더 명확한 eval 케이스 분류와 결과 해석 기준
- 검증 방법: eval 실행 결과 비교, 실패 유형 분류 가능 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 13. subagent 개입 설계 초안
- 왜 중요한지: review, test triage, log analysis 를 분리하면 장기적으로 운영 효율이 좋아질 수 있다.
- 선행조건 / 의존성: core execution flow 와 observability 정리
- 기대 결과물: subagent 를 어디에, 어떤 조건에서, 어떤 권한으로 쓸지에 대한 아키텍처 초안
- 검증 방법: 문서 검토, 운영 규칙과의 충돌 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예
