# TASK-061. Task SQLAlchemy 모델 생성

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`backend/src/models/task.py`에 Task SQLAlchemy 모델을 구현했다. T009 마이그레이션(`backend/alembic/versions/001_initial_schema.py`)의 `tasks` 테이블 및 `data-model.md`의 Task 엔티티 정의와 정확히 일치시켰다 (id, project_id, task_number, title, description, upload_method, created_at, updated_at, deletion_status, trashed_at, scheduled_deletion_at). `Project` 모델에 비어 있던 `tasks` relationship(back_populates, cascade="all, delete-orphan")도 함께 연결했다. `task_number`의 "프로젝트 내 순차 증가, 한번 부여되면 불변" 보장과 실제 자동 증가 로직은 TaskService(T068)에서 다룬다 — 이 task는 모델 스키마 매핑만 범위로 한다.

## 변경 파일
- `backend/src/models/task.py` (신규)
- `backend/src/models/project.py` (tasks relationship 추가)
- `backend/tests/unit/test_task_model.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T061 체크)

## TDD 결과
- RED 커밋: 87e8b6b (test: Task model - RED (T061))
- GREEN 커밋: cbbf60c (feat: Task SQLAlchemy model - GREEN (T061))
- REFACTOR 커밋: 해당 없음 (User/Project/RefreshToken 모델과 동일한 패턴을 그대로 따라 구현해 추가 개선 불필요)
- 테스트 커버리지: 전체 백엔드 스위트 130 passed, src/models/task.py 96% (미커버 라인은 `__repr__`, 다른 모델들과 동일하게 테스트 대상에서 제외)

## 기술 결정
- 기존 User/Project/RefreshToken 모델의 컨벤션(`server_default=text(...)`, `postgresql.UUID(as_uuid=True)`, TYPE_CHECKING 하에서만 순환 참조될 관계 타입 import)을 그대로 따름.
- `unique_task_number_per_project` UNIQUE 제약과 `title_min_length`(5자 이상)/`description_max_length`(500자 이하) CHECK 제약은 마이그레이션에 이미 선언되어 있으므로 모델에는 별도로 재선언하지 않음 (User/Project 모델도 동일한 방식 — DB 레벨 제약은 마이그레이션이 단일 진실 공급원).

## 비고
- `test_task_model.py`만 단독 실행하면 `Project` 심볼이 아직 SQLAlchemy 매퍼 레지스트리에 없어 `InvalidRequestError`가 발생하지만(지연 관계 설정 특성상), 전체 스위트(`pytest tests/`)로 실행하면 수집 순서상 다른 모델들이 먼저 import되어 정상 통과한다 — 기존 User/RefreshToken 모델 테스트에서도 동일하게 나타나는 패턴이며 실제 버그는 아니다.
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일한 환경 이슈).
