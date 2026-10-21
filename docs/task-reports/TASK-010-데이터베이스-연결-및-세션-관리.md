# TASK-010. 데이터베이스 연결 및 세션 관리

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
`backend/src/db/session.py`를 작성했습니다. 비유하자면, 식당 주방(DB)에 들어갈 때마다 "출입증"을 하나씩 발급받고, 일을 마치면 자동으로 반납하는 시스템과 같습니다. API 요청 하나가 들어올 때마다 `get_db()`가 DB 연결(세션)을 하나 발급해주고, 요청이 끝나면 자동으로 정리(반납)합니다.

**구현 내용**:
- `get_async_database_url()`: `.env`/환경변수의 `DATABASE_URL`(`postgresql://...`)을 비동기 드라이버가 필요로 하는 `postgresql+asyncpg://...`로 변환 (T008의 `alembic/env.py`에서 쓴 것과 동일한 방식, 중복이지만 아직 공유 설정 모듈(T011)이 없어 독립적으로 구현)
- `engine`: `create_async_engine()`으로 생성한 전역 비동기 엔진, `pool_pre_ping=True`로 끊긴 연결을 자동 감지하도록 설정
- `AsyncSessionLocal`: `async_sessionmaker()`로 만든 세션 팩토리 (`expire_on_commit=False`로 커밋 후에도 객체 속성 접근 가능하게 함)
- `get_db()`: FastAPI 의존성으로 쓸 async generator — `async with` 블록으로 세션을 열고, 요청 처리가 끝나면(또는 예외가 나도) 자동으로 세션을 닫음
- 프로젝트 루트의 `.env`를 자동으로 읽도록 `python-dotenv` 적용 (alembic과 동일한 패턴)

**검증 (실제 DB 연결)**:
1. T004의 PostgreSQL 컨테이너가 실행 중인 상태에서 임시 스크립트로 두 가지를 확인:
   - `engine.connect()`로 직접 연결 후 `SELECT 1` 실행 → 정상 응답
   - `get_db()`를 FastAPI가 쓰는 방식 그대로(`__anext__()` 호출)로 세션을 받아 `SELECT count(*) FROM users` 실행 → 정상 응답(0건, T009에서 테이블만 만들고 데이터는 아직 없음)
   - 제너레이터를 한 번 더 진행시켜 `StopAsyncIteration`이 발생하는지 확인 → 세션이 정상적으로 "한 번 열고 한 번 닫히는" 생명주기를 따름을 확인
2. Ruff/Black(T006) 통과 확인
3. 검증용 임시 스크립트는 삭제 (scratchpad에서 실행, 실제 코드베이스에는 포함되지 않음)

## 변경 파일
- `backend/src/db/session.py` (신규)
- `backend/src/db/__init__.py` (신규, 패키지 인식용)

## TDD 결과
tasks.md의 TDD Workflow 섹션은 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시하고 있으며, 이번 Task는 Phase 2(Foundational)에 속해 RED-GREEN-REFACTOR 사이클 의무 대상이 아님. 대신 실제 PostgreSQL 컨테이너에 연결해 엔진/세션/의존성 제너레이터가 모두 의도대로 동작하는지 수동으로 검증함(위 "검증" 항목 참고).

## 기술 결정 (해당 시)
- SQLAlchemy 2.0의 `async_sessionmaker` + `AsyncSession`을 사용 — research.md의 "SQLAlchemy 2.0+ (async)" 결정과 일치
- `pool_pre_ping=True`: 개발 환경에서 DB 컨테이너가 재시작되거나 연결이 끊겼을 때 죽은 커넥션을 자동으로 걸러내도록 함 (운영 안정성 확보)
- `DATABASE_URL` 변환 로직(`postgresql://` → `postgresql+asyncpg://`)은 `alembic/env.py`(T008)와 중복 구현됨 — 이는 아직 공통 설정 모듈이 없기 때문이며, T011(`backend/src/db/config.py`)에서 `pydantic-settings` 기반 공통 `Settings`를 만들 때 두 곳 모두 그 설정을 참조하도록 리팩토링할 수 있음

## 비고
- T011(데이터베이스 설정 및 커넥션 풀링)에서 커넥션 풀 크기(`pool_size`, `max_overflow` 등) 같은 세부 튜닝 옵션을 담당할 예정 — 현재는 SQLAlchemy 기본값으로 동작
- 이 모듈은 아직 어떤 API 엔드포인트에도 연결되지 않음 — T028 이후 인증 API 등에서 `Depends(get_db)` 형태로 실제 사용될 예정
