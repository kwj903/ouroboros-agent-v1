# Ouroboros - 로컬 AI 에이전트

## 개요

이 프로젝트는 메모리 관리, 작업 승인 워크플로우, CLI 인터페이스를 갖춘 파이썬 기반 로컬 AI 에이전트입니다.

## 프로젝트 구조

```
free-model-test/
├── app/                    # 메인 애플리케이션 패키지
│   ├── agent.py           # 핵심 에이전트 로직
│   ├── api/               # API 엔드포인트
│   ├── approvals.py       # 작업 승인 관리
│   ├── cli.py             # 명령줄 인터페이스
│   ├── compare_eval_runs.py
│   ├── compare_memory_eval_runs.py
│   ├── conversation_state.py  # 세션 상태 관리
│   ├── eval_runner.py     # 평가 실행기
│   ├── logger.py          # 로깅 유틸리티
│   ├── long_term_memory.py # 메모리 관리
│   ├── main.py            # 진입점 (최소한의 CLI 설정)
│   ├── memory_eval_runner.py
│   ├── memory_manager.py  # 메모리 작업
│   ├── model.py           # 모델 상호작용
│   ├── paths.py           # 경로 구성
│   ├── preview_markdown.py
│   ├── runtime_context.py
│   ├── settings.py        # 애플리케이션 설정
│   ├── tool_registry.py
│   ├── tool_trace_manager.py
│   ├── tools/
│   │   └── workspace_tools.py  # 워크스페이스 작업 도구
│   └── __pycache__/
├── tests/                  # 테스트 디렉토리 (현재 비어있음)
├── .venv/                 # 가상 환경
├── pyproject.toml         # 프로젝트 구성
├── README.md              # 이 파일
└── .gitignore
```

## 빌드/릴/테스트 명령

### Python 환경
- **Python 버전**: 3.12+ (pyproject.toml에 지정)
- **패키지 관리자**: hatchling 빌드 백엔드 사용
- **의존성**: pyproject.toml 및 uv.lock을 통해 관리

### 테스트 실행
테스트가 없는 경우 다음 명령을 사용:
```bash
# 모든 테스트 실행 (있는 경우)
python3 -m pytest tests/ -v

# 특정 테스트 이름으로 실행
python3 -m pytest tests/ -k "test_name" -v

# 상세 출력으로 테스트 실행
python3 -m pytest tests/ -v

# 특정 테스트 파일 실행
python3 -m pytest tests/test_file.py -v

# 커버리지 포함 테스트 실행 (설정된 경우)
python3 -m pytest --cov=app tests/
```

### 린팅 및 포맷팅
표준 Python 규칙을 사용합니다. 일반 린팅 도구는 다음과 같습니다:
```bash
# ruff 사용 가능하다면
ruff check .
ruff format .

# black 사용 가능하다면
black .

# flake8 사용
flake8 .
```

### 코드 실행
```bash
# 메인 애플리케이션 실행
python3 main.py

# CLI 실행
ouroboros

# 특정 모듈 실행
python3 -m app.cli
```

## 코드 스타일 가이드라인

### 1. 임포트 규칙
- 모든 파일 맨 위에 `from __future__ import annotations` 사용
- 임포트 순서:
  1. 표준 라이브러리 임포트
  2. 서드파티 임포트
  3. 로컬 애플리케이션 임포트
- 절대 임포트 사용 (예: `from app.logger import utc_now_iso`)
와일드카드 임포트 사용 금지 (`from module import *`)

### 2. 타입 주석
- 모든 함수에 타입 주석 필수
- 합집합 타입: `|` 구문 사용 (Python 3.10+): `str | None`
- 선택적 반환형: `Optional[T]` 사용 (적절한 경우)
- 제네릭 타입: 대괄호 사용: `list[dict[str, Any]]`

### 3. 명명 규칙
- **변수**: snake_case (예: `user_input`, `session_state`)
- **함수**: snake_case (예: `_ensure_state_dir`, `_get_env`)
- **클래스**: PascalCase (현재 코드베이스에는 없음)
- **상수**: UPPER_SNAKE_CASE (예: `PENDING_ACTIONS_FILE`, `TRACE_FILE`)
- **프라이빗 함수**: `_` 접두사 (예: `_load_state`, `_save_state`)

### 4. 문자열 및 출력
- 사용자Facing 메시지에는 한국어 사용 (예: "사용법:", "실패:")
- 기술 용어 및 명령어 이름은 영어 사용
- 에러 메시지는 설명적이고 실제 값 포함
- 문자열 포맷팅에는 f-문자열 사용

### 5. 에러 처리
- 에러 조건에는 예외 사용
- 누락된 작업 ID에는 `KeyError` 발생
- 구성/검증 오류에는 `RuntimeError` 발생
- 에러 메시지는 컨텍스트 정보 포함
- 외부 작업 (파일 I/O, API 호출)에는 try-except 블록 사용

### 6. 파일 작업
- 명시적 인코딩 지정: `open(..., encoding="utf-8")`
- 파일 경로에는 `pathlib.Path` 사용
- 쓰기 전에 디렉토리 존재 확인: `mkdir(parents=True, exist_ok=True)`
- 파일 작업에는 컨텍스트 관리자 (`with` 문) 사용

### 7. 함수 설계
- 함수는 단일 책임 가져야 함
- 가능한 한 짧고 집중적 (50줄 이하 권장)
- 복잡한 로직은 도우미 함수 사용
- 반환 값은 일관된 타입 유지

### 8. 상태 관리
- 세션 상태는 `SessionState` 클래스를 통해 관리
- 애플리케이션 상태는 JSON 파일에 저장 (예: `pending_actions.json`)
- 상태 파일은 `app/state/` 디렉토리에 저장
- 읽기/쓰기 전에 상태 디렉토리 존재 확인

### 9. API 키 및 비밀
- API 키는 `.env` 파일에서 로드
- 민감 정보는 절대로 하드코딩하지 않음
- 환경 변수 사용: `os.getenv("KEY_NAME")`
- 적절한 기본값 제공
- 필수 환경 변수에 대한 검증 포함

### 10. 로깅 및 디버깅
- 로그에는 UTC 타임스탬프 사용: `datetime.utcnow().isoformat()`
- 에이전트 트레이스는 JSONL 형식으로 저장: `app/logs/agent_trace.jsonl`
- 입력 및 출력 모두 로깅하여 디버깅
- 추적 가능성을 위해 로그 항목에 세션 ID 포함

### 11. 한국어 지원
- 애플리케이션은 기본적으로 한국어 인터페이스 지원
- 사용자 프롬프트와 메시지에는 한글 문자 사용
- 모든 곳에서 UTF-8 인코딩 사용
- 모든 출력 함수에서 한국어 텍스트 처리 테스트

## 테스트 가이드라인

### 테스트 위치
- 테스트는 `tests/` 디렉토리에 배치
- 테스트 파일 명명: `test_<기능>.py`

### 테스트 패턴
```python
# 예제 테스트 구조 (미정)
def test_function_name():
    # Arrange
    # Act
    # Assert
    pass

# 에러 케이스 테스트
def test_function_name_error_case():
    # 에러 처리 테스트
    pass
```

### 테스트 커버리지
- 모든 공개 함수 테스트
- 에러 조건 테스트
- 경계 조건 테스트
- 상태 지속성 테스트

## 디버깅 팁

1. **로그 확인**: `app/logs/agent_trace.jsonl`
2. **상태 파일 확인**: `app/state/pending_actions.json`
3. **디버그 모드 활성화**: main.py에서 `debug_mode = True` 설정
4. **환경 변수 확인**: `.env` 파일이 적절히 구성되었는지 확인
5. **실행 경로 추적**: 트레이스 로그에서 실행 경로 확인

## 메모리 관리

- 메모리는 구조화된 JSON 형식으로 저장
- 메모리 제안은 대화에 따라 자동 생성
- 오래된 메모리는 검색 및 복원 가능
- 메모리 중요도 점수 (1-5 척도)
- 사용자 지정 태그로 수동 메모리 표시 가능

## 작업 워크플로우

1. 사용자가 명령/메시지 입력
2. 로컬 명령 먼저 확인 (`pending`, `memories`, `remember`, `search_memory` 등)
3. 로컬 명령이 아니면 에이전트가 요청 처리
4. 에이전트가 답변 및 트레이스 생성
5. action_id 감지 시 승인 워크플로우 트리거
6. 승인된 작업 실행
7. 결과를 히스토리 및 메모리에 저장

## 경로 구성

`app/paths.py`에 정의된 주요 경로:
- `STATE_DIR`: 상태 파일 디렉토리
- `LOGS_DIR`: 로그 파일 디렉토리
- `WORKSPACE_ROOT`: 워크스페이스 루트 디렉토리
- `OUROBOROS_HOME`: ouroboros 구성 디렉토리

## 환경 변수

필수 환경 변수:
- `ALL_API_KEY`: LLM 제공자 API 키
- `ALL_BASE_URL`: LLM API 기본 URL
- `ALL_MODEL`: 사용할 모델 (기본: "openai/gpt-oss-20b")

선택적 환경 변수:
- `DEFAULT_OUTPUT_MODE`: "cli" 또는 "markdown"
- `DEFAULT_RESPONSE_LANGUAGE`: "ko" 또는 "en"

## 최선의 실무

1. **항상 입력 검증**: 처리 전에 유형과 값 확인
2. **에러를 친절하게 처리**: 명확한 에러 메시지 제공
3. **형식 지정 사용**: 코드를 더 유지 관리 가능하게 함
4. **함수를 순수하게**: 가능한 한 부작용 최소화
5. **가정을 문서화**: 특정 결정 이유 주석 처리
6. **상태 지속성 테스트**: 재시작 후 데이터 확인
7. **비동기 패턴 사용**: I/O 작업의 경우 async/await 고려
8. **메모리 사용량 모니터링**: 대형 상태가 성능에 영향
9. **API 키 보안**: .env 파일은 절대로 커밋하지 않음
10. **기존 패턴 준수**: 기존 코드와 일관성 유지

## 향후 개선 사항

- 포괄적인 테스트 스위트 추가
- 비동기 연산 구현
- 메트릭 및 모니터링 추가
- 여러 LLM 공급자 지원
- 구성 유효성 검사 추가
- 백업/복구 기능 구현