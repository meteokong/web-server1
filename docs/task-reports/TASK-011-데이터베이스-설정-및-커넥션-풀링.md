# TASK-011. 데이터베이스 설정 및 커넥션 풀링

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
`backend/src/db/config.py`를 작성해 DB 연결 관련 설정을 한 곳에 모았습니다. 비유하자면, 지금까지는 "주방 출입 규칙"(DB 연결 URL 변환)을 식당 문마다(alembic, session.py) 따로 써붙여 놨었는데, 이제 본사 규정집 하나(`config.py`)로 통합하고 각 문은 그 규정집을 참조하도록 바꾼 것입니다.

**구현 내용**:
- `DatabaseSettings` (pydantic-settings `BaseSettings`): `.env.example`(T005)의 `DATABASE_URL`을 읽고, 커넥션 풀 크기 관련 값들을 환경변수로 오버라이드 가능하게 함
  - `db_pool_size=10`, `db_max_overflow=5`, `db_pool_timeout=30`, `db_pool_recycle_seconds=1800`
  - `async_database_url` 프로퍼티: `postgresql://` → `postgresql+asyncpg://` 변환을 이 한 곳에서만 수행
- `get_database_settings()`: `@lru_cache`로 감싸 애플리케이션 전체에서 설정 객체를 한 번만 생성/재사용

**T010/T008과의 통합 (중복 제거)**:
- `backend/src/db/session.py`를 수정해 자체적으로 하던 `DATABASE_URL` 변환 로직을 제거하고, `get_database_settings()`에서 가져온 `async_database_url`과 풀 설정값(`pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`)으로 엔진을 생성하도록 변경 — T010 Task Report에 남겨둔 "중복 구현" 개선 사항을 이번에 실제로 반영함
- `backend/alembic/env.py`도 동일하게 수정해 자체 `os.environ.get("DATABASE_URL")` + 수동 변환 코드를 제거하고 `get_database_settings().async_database_url`을 사용하도록 통일

**검증 (실제 DB 연결)**:
- `get_database_settings()` 호출 결과 확인: `database_url`/`async_database_url`이 올바르게 변환되고, `db_pool_size=10`이 설정값에서 읽힌 그대로 반영되는지 확인
- `engine.pool.size() == settings.db_pool_size` 로 엔진이 실제로 이 설정을 사용해 생성됐는지 확인 (10으로 일치)
- T004의 PostgreSQL 컨테이너에 `engine.connect()` → `SELECT 1`, `get_db()` 의존성으로 `SELECT count(*) FROM users` 실행 → 모두 정상 응답
- `alembic current` 재실행 → 리팩토링 후에도 `001 (head)`로 정상 연결 확인
- Ruff/Black 통과 확인

## 변경 파일
- `backend/src/db/config.py` (신규)
- `backend/src/db/session.py` (config.py를 사용하도록 리팩토링, 중복 URL 변환 로직 제거)
- `backend/alembic/env.py` (config.py를 사용하도록 리팩토링, 중복 URL 변환 로직 제거)

## TDD 결과
tasks.md의 TDD Workflow 섹션은 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시하며, 이번 Task는 Phase 2(Foundational)에 속해 RED-GREEN-REFACTOR 사이클 의무 대상이 아님. 대신 실제 PostgreSQL 컨테이너 연결과 `engine.pool.size()` 값 비교를 통해 "설정값이 실제로 적용되는가"를 검증함.

## 기술 결정 (해당 시)
- 커넥션 풀 기본값(`pool_size=10`, `max_overflow=5`)은 plan.md의 "Support 3 concurrent document generations per user"와 일반 API 트래픽을 함께 고려해, PostgreSQL 기본 `max_connections`(100)를 넘지 않는 선에서 넉넉하게 설정함
- `pydantic-settings`의 `env_file` 옵션에 프로젝트 루트 `.env`의 절대 경로를 지정 — `python-dotenv`를 별도로 호출하지 않아도 되므로, T010/T008에서 각각 하던 `load_dotenv()` 호출도 자연스럽게 제거됨
- `@lru_cache`로 설정 객체를 캐싱 — 매 요청마다 `.env`를 다시 읽지 않도록 함 (FastAPI 공식 권장 패턴)

## 비고
- 이 리팩토링으로 "DATABASE_URL을 postgresql+asyncpg로 바꾸는 코드"가 이제 `config.py` 단 한 곳에만 존재함 — 이후 드라이버를 바꾸거나 연결 방식이 바뀌어도 한 곳만 수정하면 됨
- `GOOGLE_API_KEY`, `JWT_SECRET_KEY` 등 DB와 무관한 다른 환경변수는 이번 Task 범위에 포함하지 않음 (각 기능 구현 시점에 해당 서비스별 Settings로 분리해 추가할 예정)
