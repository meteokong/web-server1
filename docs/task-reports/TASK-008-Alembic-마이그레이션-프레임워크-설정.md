# TASK-008. Alembic 마이그레이션 프레임워크 설정

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
데이터베이스 구조를 "버전 관리"할 수 있는 도구인 Alembic을 백엔드에 설정했습니다. 비유하자면, 코드를 git으로 버전 관리하듯, 데이터베이스 테이블 구조도 "어떤 순서로 어떻게 변해왔는지" 기록을 남기는 것입니다. 나중에 테이블을 추가하거나 바꿀 때마다 그 변경 내역이 `alembic/versions/`에 하나씩 쌓이게 됩니다.

**진행 과정**:
1. `alembic init -t async alembic` 실행 → `backend/alembic.ini`, `backend/alembic/{env.py, script.py.mako, README}`, `backend/alembic/versions/` 생성 (research.md에서 결정한 "SQLAlchemy 2.0 async" 방식에 맞춰 async 템플릿 사용)
2. `alembic/env.py` 수정:
   - `.env.example`(T005)에 정의된 `DATABASE_URL` 환경 변수를 읽어와 `sqlalchemy.url`을 덮어쓰도록 구성 (`postgresql://` → `postgresql+asyncpg://`로 드라이버 스킴 자동 변환)
   - `python-dotenv`로 프로젝트 루트의 `.env` 파일을 자동으로 읽도록 설정 (매번 환경변수를 수동으로 export하지 않아도 되게 함)
   - `target_metadata`는 아직 `None`으로 두고, T009에서 Base 모델 생성 후 연결할 주석을 남김
3. `alembic.ini`의 하드코딩된 `sqlalchemy.url = driver://user:pass@localhost/dbname` 플레이스홀더를 실제 프로젝트 DB 이름(`codelearning`)에 맞춘 값으로 교체하고, 실제로는 `env.py`가 `DATABASE_URL`로 덮어쓴다는 점을 주석으로 명시
4. `backend/requirements.txt`에 `python-dotenv==1.2.4` 명시적으로 추가 (기존에는 `pydantic-settings`의 간접 의존성으로만 설치되어 있었음)

**검증** (실제 DB 연결까지 확인):
- T004에서 띄워둔 PostgreSQL 컨테이너(`localhost:5432/codelearning`)가 계속 실행 중인 것을 확인
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/codelearning alembic current` 실행 → 에러 없이 "Context impl PostgresqlImpl, Will assume transactional DDL" 출력 (연결 성공, 아직 마이그레이션 없음은 정상)
- `alembic revision -m "smoke_test"` 실행 → `versions/` 디렉토리에 리비전 파일이 정상 생성되는 것을 확인 → 실제 마이그레이션이 아니므로 테스트 후 삭제

## 변경 파일
- `backend/alembic.ini` (신규)
- `backend/alembic/env.py` (신규, DATABASE_URL 연동 및 dotenv 로딩 추가)
- `backend/alembic/script.py.mako`, `backend/alembic/README` (신규, Alembic 기본 생성)
- `backend/alembic/versions/.gitkeep` (신규, 빈 디렉토리 구조 보존용)
- `backend/requirements.txt` (`python-dotenv==1.2.4` 명시적 추가)

## TDD 결과
해당 없음 (마이그레이션 프레임워크 설정 자체는 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 실제 PostgreSQL 컨테이너에 `alembic current`/`alembic revision`을 실행해 "설정이 유효하게 동작하는가"를 검증함.

## 기술 결정 (해당 시)
- `alembic init -t async`를 사용해 처음부터 async SQLAlchemy 엔진(`async_engine_from_config`)으로 동작하도록 구성 — research.md의 "SQLAlchemy 2.0+ (async)" 결정과 일치
- `DATABASE_URL`은 표준 `postgresql://` 스킴으로 `.env.example`에 정의되어 있어, async 드라이버(`asyncpg`)가 필요로 하는 `postgresql+asyncpg://`로 `env.py`에서 자동 변환하도록 처리 — 사용자가 `.env`에서 드라이버 스킴을 신경 쓰지 않아도 되게 함
- `target_metadata`는 아직 연결하지 않음: T009에서 `backend/src/models/base.py`의 `Base`를 만든 뒤 연결할 예정이며, 지금 연결하면 존재하지 않는 모듈을 import하게 되어 순서가 뒤바뀜

## 비고
- 실제 테이블 스키마가 포함된 첫 마이그레이션(`001_initial_schema.py`)은 T009에서 작성 예정 — 이번 Task는 프레임워크 설정까지만 범위로 함
- 검증용으로 생성했던 `smoke_test` 리비전 파일은 실제 스키마가 없는 빈 리비전이라 삭제함 (다음 Task에서 진짜 초기 마이그레이션 작성)
- PostgreSQL 컨테이너는 이전 세션에서 이미 기동된 상태를 그대로 사용했으며, 이번 Task에서 별도로 끄지 않음
