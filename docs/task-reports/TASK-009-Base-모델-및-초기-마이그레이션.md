# TASK-009. Base 모델 클래스 및 초기 데이터베이스 마이그레이션

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
data-model.md에 정의된 10개 테이블(users, refresh_tokens, projects, tasks, uploaded_code, code_files, learning_documents, practice_problems, questions, progress) 전체를 실제 데이터베이스에 만드는 "건축 설계도"를 작성했습니다. 비유하자면, 집의 각 방(테이블)을 어떤 순서로, 어떤 재료(컬럼 타입)로, 어떤 규칙(제약조건)을 지키며 지을지 적어둔 시공 문서입니다.

**1. `backend/src/models/base.py` (Base 모델 클래스)**:
- 모든 SQLAlchemy ORM 모델(User, Project, Task 등, T023~T151에서 개별적으로 생성될 예정)이 상속할 `Base` 클래스 정의
- 제약조건/인덱스 이름을 일관되게 생성하는 `naming_convention` 지정 (예: `ck_users_valid_email`, `fk_progress_user_id_users`) — 추후 Alembic autogenerate가 스키마 변경을 감지할 때 이름이 흔들리지 않도록 함

**2. `backend/alembic/versions/001_initial_schema.py` (초기 마이그레이션)**:
- data-model.md의 SQL DDL을 그대로 옮긴 Alembic `op.create_table()`/`op.create_index()` 호출로 수동 작성 (`alembic revision --autogenerate`를 쓰지 않음 — 아직 ORM 모델 클래스가 없고, CHECK 제약조건·부분 인덱스처럼 autogenerate가 안정적으로 잡아내지 못하는 요소가 많기 때문)
- 의존성 순서대로 테이블 생성: users → refresh_tokens → projects → tasks → uploaded_code → code_files → learning_documents → practice_problems → questions → progress
- data-model.md의 모든 CHECK 제약(이메일 형식, 제목 길이, JSONB 구조, 범위 체크 등), UNIQUE 제약, 부분 인덱스(`WHERE deletion_status = 'active'`)까지 그대로 반영
- `downgrade()`는 역순으로 전체 테이블 삭제

**3. `backend/alembic/env.py` 업데이트**:
- T008에서 `target_metadata = None`으로 남겨뒀던 부분을 `from src.models.base import Base; target_metadata = Base.metadata`로 연결 (이제 `alembic revision --autogenerate`도 향후 정상 동작 가능)

**검증 (실제 PostgreSQL에 적용)**:
- `gen_random_uuid()`가 이 프로젝트의 `postgres:15-alpine` 이미지에서 별도 익스텐션 없이 기본 동작하는지 먼저 확인
- `alembic upgrade head` 실행 → 11개 테이블(10개 엔티티 + `alembic_version`) 정상 생성 확인 (`\dt`)
- `users`, `progress` 테이블의 실제 컬럼/제약조건/인덱스를 `\d`로 확인 → data-model.md와 정확히 일치 (naming convention에 따라 `ck_users_valid_email`, `fk_progress_user_id_users` 등으로 명명됨)
- **롤백 왕복 테스트**: `alembic downgrade base` → 테이블 전부 삭제(`alembic_version`만 남음) 확인 → `alembic upgrade head` 재실행 → 11개 테이블 다시 정상 생성 확인
- Ruff/Black(T006) 적용: import 정렬 및 라인 길이 이슈 2건 발견 → `--fix`/재포맷 후 재검사 통과, 포맷팅 후에도 마이그레이션이 동일하게 동작하는지 재확인

## 변경 파일
- `backend/src/models/base.py` (신규)
- `backend/src/__init__.py`, `backend/src/models/__init__.py` (신규, 패키지 인식용)
- `backend/alembic/versions/001_initial_schema.py` (신규)
- `backend/alembic/env.py` (target_metadata를 Base.metadata로 연결)

## TDD 결과
해당 없음 (마이그레이션 스키마 작성은 애플리케이션 비즈니스 로직이 아니므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 실제 PostgreSQL 컨테이너에 적용/롤백/재적용하는 왕복 테스트로 "스키마가 정확히 재현 가능한가"를 검증함.

## 기술 결정 (해당 시)
- "manual SQL, no autogenerate" 요구사항은 `alembic revision --autogenerate`(기존 모델과 DB 스키마를 비교해 자동 생성)를 사용하지 않고 사람이 직접 작성한다는 의미로 해석함. 다만 실제 SQL 문자열을 그대로 쓰는 대신 Alembic의 `op.create_table()` Python API를 사용해 타입 안전성과 가독성을 확보함 (data-model.md 자체도 "Migration Strategy" 섹션에서 `op.create_table(...)` 패턴을 예시로 들고 있어 일치함)
- UUID 기본값은 `gen_random_uuid()`를 그대로 사용 — 이 프로젝트가 쓰는 `postgres:15-alpine` 이미지에서는 별도 `pgcrypto` 익스텐션 설치 없이 기본 동작함을 직접 확인함
- `base.py`에 `naming_convention`을 추가한 것은 data-model.md에 명시되지 않은 결정이지만, SQLAlchemy/Alembic 생태계의 표준 권장사항이며 향후 스키마 변경 시 제약조건 추적을 쉽게 하기 위함

## 비고
- 실제 ORM 모델 클래스(`User`, `Project`, `Task` 등)는 아직 작성하지 않음 — T023(User), T024(RefreshToken), T043(Project), T061~063(Task/UploadedCode/CodeFile), T090(LearningDocument), T115(PracticeProblem), T132(Question), T151(Progress)에서 각각 `base.py`의 `Base`를 상속해 만들 예정이며, 반드시 이번 Task의 마이그레이션 스키마와 일치해야 함(각 Task 설명에 "must match T009 migration schema" 명시됨)
- 검증에 사용한 PostgreSQL 컨테이너는 T004에서 띄운 것을 그대로 사용했으며, 최종적으로 스키마가 적용된 상태로 남겨둠
