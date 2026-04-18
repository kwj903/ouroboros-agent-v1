# TASKS

이 문서는 현재 저장소 상태를 바탕으로 작성한 우선순위 초안이다.
승인 전 초안이며, 각 작업은 사람 검토 후 실행 범위를 확정해야 한다.

## Now
### 1. model/provider routing 정책 초안 구체화
- 왜 중요한지: 사용자의 실제 운영 목표가 free API endpoint 우선, local fallback, paid escalation 이므로 현재 단일 `ALL_*` 설정만으로는 장기 방향을 담을 수 없다.
- 선행조건 / 의존성: 현재 `app/model.py`, `app/settings.py`, 공통 baseline 18개 툴 정책 이해
- 기대 결과물: provider 우선순위, fallback 조건, user override 방식, 추적/로그 요구사항이 정리된 설계 초안
- 검증 방법: `docs/PRODUCT.md`, `docs/ARCHITECTURE.md`, `docs/CURRENT_SCOPE.md` 와 충돌 없는지 검토
- 실행 전에 사람 승인이 필요한지 여부: 예

### 2. Web UI 상태 orchestration 추가 안정화
- 왜 중요한지: component 분리는 시작됐지만, `App.tsx` 와 `OperationsSidebar.tsx` 에 데이터 동기화와 운영 UI 책임이 아직 많이 남아 있다.
- 선행조건 / 의존성: 현재 build 통과 상태 유지, session/approval/memory API 동작 유지
- 기대 결과물: 세션 동기화, approval 반영, 운영 패널 갱신 로직이 더 작고 예측 가능한 경계로 정리됨
- 검증 방법: frontend build 통과, 세션 선택/생성/삭제, 채팅, 승인 흐름 수동 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 3. 공통 baseline tool set 의 모델별 확장 규칙 정의
- 왜 중요한지: 현재 18개 툴은 공통 baseline 으로 유지하지만, 향후 더 많은 툴이 추가될 때는 모델별 제한/확장이 필요하다.
- 선행조건 / 의존성: 현재 `EXPOSED_TOOL_NAMES`, trace/eval 근거, model/provider routing 정책 초안
- 기대 결과물: baseline tool 과 확장 tool 을 구분하는 기준, 모델 티어별 추가 capability 정책 초안
- 검증 방법: tool registry 와 prompt 구조에 적용 가능성이 있는지 문서 검토
- 실행 전에 사람 승인이 필요한지 여부: 예

## Next
### 4. provider router 구현 시작
- 왜 중요한지: free/local/paid 정책은 제품 목표의 핵심 운영 가치와 연결되므로 결국 실행 계층에 반영되어야 한다.
- 선행조건 / 의존성: routing 정책 초안 승인, 설정 인터페이스 합의, trace/log 요구사항 합의
- 기대 결과물: 현재 단일 `ALL_*` 설정 위에 최소한의 provider/model 선택 계층 추가
- 검증 방법: 설정별 경로 선택 단위 테스트 또는 수동 검증, 기존 chat 흐름 회귀 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 5. approval UX 재정의
- 왜 중요한지: 이 프로젝트의 핵심 가치가 사람 승인 기반 운영이므로 승인 경험이 명확해야 한다.
- 선행조건 / 의존성: 현재 approval workflow 와 Web UI 상태 확인
- 기대 결과물: 승인 요청 노출, 상세 정보 표시, approve/reject 흐름이 더 명확한 UI/CLI 정책
- 검증 방법: 승인 요청 생성부터 승인/거부 반영까지 end-to-end 점검
- 실행 전에 사람 승인이 필요한지 여부: 예

### 6. tool panel / observability 패널 재설계
- 왜 중요한지: 지금은 일부 패널이 실제 capability 와 맞지 않아 운영 지표로 신뢰하기 어렵다.
- 선행조건 / 의존성: 현재 expanded tool set 과 운영 패널 구조 검토
- 기대 결과물: 실제 agent가 사용하는 정보만 보여주는 Web 운영 패널
- 검증 방법: tool logs, workspace state, panel 데이터가 실제 실행 결과와 맞는지 비교
- 실행 전에 사람 승인이 필요한지 여부: 예

## Later
### 7. 모델별 capability policy 도입
- 왜 중요한지: 장기 목표가 모델별 안정적 tool-calling 이므로, 모델 차이를 정책으로 다루는 계층이 필요하다.
- 선행조건 / 의존성: baseline/확장 tool 구분 규칙, provider router 1차 도입, eval 체계 정리
- 기대 결과물: 모델별 tool exposure / planning policy / failure handling 기준 초안
- 검증 방법: 정책 문서화, 최소 eval 케이스 설계
- 실행 전에 사람 승인이 필요한지 여부: 예

### 8. evaluation 체계 확장
- 왜 중요한지: 회귀와 품질 변화를 더 체계적으로 감지해야 반복 개발이 안정적이다.
- 선행조건 / 의존성: 기본 테스트 경계 정리, current capability 확정
- 기대 결과물: 더 명확한 eval 케이스 분류와 결과 해석 기준
- 검증 방법: eval 실행 결과 비교, 실패 유형 분류 가능 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예

### 9. subagent 개입 설계 초안
- 왜 중요한지: review, test triage, log analysis 를 분리하면 장기적으로 운영 효율이 좋아질 수 있다.
- 선행조건 / 의존성: core execution flow 와 observability 정리
- 기대 결과물: subagent 를 어디에, 어떤 조건에서, 어떤 권한으로 쓸지에 대한 아키텍처 초안
- 검증 방법: 문서 검토, 운영 규칙과의 충돌 여부 확인
- 실행 전에 사람 승인이 필요한지 여부: 예
