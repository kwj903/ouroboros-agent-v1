# PRODUCT

## 프로젝트 목적
이 프로젝트의 장기 목표는 작은 모델부터 큰 모델까지 각 모델의 성향과 한계에 맞게 툴을 정확하고 안정적으로 호출하고 사용할 수 있는 로컬 agent tool 을 만드는 것이다.

현재 저장소 근거상 이 프로젝트는 다음 요소를 이미 포함한 단일 사용자 중심 로컬 agent 실험 환경으로 보인다.
- Python 기반 agent core
- FastAPI 기반 API
- React 기반 Web UI
- CLI / TUI 진입점
- approval workflow
- session / memory / trace / eval 보조 기능

## 대상 사용자
현재 코드와 문서 기준으로 주요 대상 사용자는 아래 두 부류다.

### 1. 로컬 에이전트 실험/개발자
- `app/`, `tests/`, `evals/`, `analyze_traces.py` 를 이용해 tool-calling 동작을 실험하고 검증하려는 사용자
- CLI와 Web을 둘 다 다루면서 개발 및 반복 개선을 수행하는 사용자

### 2. 승인 기반으로 에이전트 실행을 통제하려는 사용자
- destructive change 전에 사람 승인을 요구하는 agent workflow 를 원하는 사용자
- 세션, 기억, 작업 상태, tool trace 를 보면서 agent를 운영하려는 사용자

## 해결하려는 문제
이 저장소가 해결하려는 문제는 “모델이 툴을 호출할 수 있다” 수준이 아니라, 아래를 반복 가능하게 만드는 것이다.
- 어떤 모델이 어떤 툴을 얼마나 안정적으로 호출하는지 비교하기 어렵다.
- agent가 파일 작업이나 상태 변경을 너무 쉽게 실행하면 운영이 불안정해진다.
- Web UI와 CLI가 따로 놀면 사용성과 개발 효율이 동시에 나빠진다.
- 로그, trace, eval 근거 없이 agent를 개선하면 회귀를 통제하기 어렵다.
- 문서 없이 즉흥적으로 구현이 진행되면 사람 승인 기반 운영이 무너진다.

## 제품 목표
- 안정적인 tool-calling
- 제어 가능한 실행 흐름
- 사람 승인 기반 운영
- Web UI와 CLI를 함께 제공하는 반복 개발 환경
- 세션, 기억, trace, eval 근거를 남기는 agent 운영 기반
- 문서 중심으로 범위와 태스크를 관리할 수 있는 저장소 운영 체계

## 비목표
현재 단계에서 아래는 목표로 두지 않는다.
- 완전 자율 실행 agent
- 무제한 툴 노출
- 사람 승인 없는 destructive change
- 다중 subagent orchestration 완성본
- 다중 사용자/권한 모델 완성
- 프로덕션 SaaS 수준 배포/운영 체계
- 저장소 근거 없는 provider 추상화 확장

## 핵심 사용자 흐름
### 1. CLI 대화와 승인 처리
1. 사용자가 CLI 또는 TUI에서 요청을 보낸다.
2. agent가 tool-calling 또는 일반 응답을 수행한다.
3. write/search/delete 계열 요청은 pending approval 로 반환된다.
4. 사람이 approve/reject 를 통해 실행을 통제한다.
5. 결과가 세션 기록과 작업 상태에 남는다.

### 2. Web 대화와 승인 처리
1. 사용자가 Web UI에서 대화를 보낸다.
2. backend API가 세션/메모리 컨텍스트를 조합해 agent를 호출한다.
3. 승인 필요 작업은 action metadata 와 함께 반환된다.
4. 사용자가 Web에서 승인/거부를 처리한다.
5. history, workspace state, tool logs, memory suggestions 를 다시 확인한다.

### 3. 세션과 메모리 운영
1. 사용자는 세션을 생성/전환/이름 변경/삭제한다.
2. 최근 대화와 rolling summary 가 다음 턴의 context 로 사용된다.
3. 장기 기억은 수동 저장 또는 suggestion 기반으로 관리한다.

### 4. 평가와 추적 기반 반복 개선
1. 개발자는 trace 로그와 tool logs 를 분석한다.
2. eval 케이스를 통해 특정 tool-calling 흐름과 memory 동작을 점검한다.
3. 문제를 문서와 태스크에 반영한 뒤 사람 승인 기반으로 다음 변경을 진행한다.

## 성공 기준
현재 저장소 단계에서의 현실적인 성공 기준은 아래와 같다.
- CLI와 Web이 같은 agent core 를 일관되게 사용한다.
- 승인형 파일 작업이 사람 개입 없이 바로 실행되지 않는다.
- 세션, 작업 상태, trace, memory 정보가 반복 개발에 쓸 수 있을 만큼 남는다.
- 최소 eval / test / trace 분석 루프가 존재한다.
- 문서가 구현보다 뒤처지지 않도록 운영 기준이 정리된다.

장기적으로는 아래가 더 중요하다.
- 모델별 tool-calling 안정성 비교 가능
- capability 노출과 실행 흐름 제어 정책이 명확함
- 반복 개발 시 회귀를 더 빨리 감지 가능

## 운영 방향 초안
아래 항목은 사용자 방향성이 확인된 내용이지만, 아직 현재 코드에 구현 완료된 사실은 아니다.

- 현재 구현된 18개 툴은 모델 크기와 무관하게 공통 baseline tool set 으로 본다.
- 장기적으로는 baseline 위에 모델별 capability policy 와 최적화가 추가될 수 있다.
- 기본 model/provider routing 방향은 free API endpoint 우선, 이후 local model fallback, 마지막으로 고급 작업에서 paid endpoint 를 쓰는 흐름을 지향한다.
- 사용자가 이 routing 정책을 override 할 수 있어야 한다.
- 이 정책은 현재 `app/model.py` 의 단일 `ALL_*` 환경변수 구조를 넘어서는 작업이므로, 별도 설계와 단계적 구현이 필요하다.

## Web UI와 CLI를 둘 다 제공하는 이유
현재 코드 구조상 Web과 CLI는 같은 core 를 공유하지만 목적이 다르다.

### Web UI가 필요한 이유
- 승인 대기, 세션, memory, tool logs, workspace state 를 한 화면에서 보기 쉽다.
- 상호작용 흐름과 사용자 경험을 검토하기 좋다.
- agent를 운영하는 사람 입장에서 상태 가시성이 높다.

### CLI가 필요한 이유
- 개발과 자동화에 더 적합하다.
- 빠른 실험, 스크립트 실행, 로컬 반복 확인에 유리하다.
- Web UI보다 더 직접적으로 core 동작을 추적하기 쉽다.

### 둘 다 필요한 이유
- Web은 운영 관점, CLI는 개발 관점을 보완한다.
- 최종 제품 목표가 “사용자가 쓰기 편한 UI” 와 “개발/자동화에 적합한 인터페이스” 를 동시에 요구한다.
- 두 계층이 같은 core 를 공유해야 tool-calling 안정성을 인터페이스별로 따로 구현하지 않아도 된다.
