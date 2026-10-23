# TASK-043. Project SQLAlchemy 모델 생성

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
Soft delete 필드를 포함한 Project SQLAlchemy 모델을 `backend/src/models/project.py`에 구현했다. 컬럼은 T009 마이그레이션(`backend/alembic/versions/001_initial_schema.py`)의 `projects` 테이블 및 `data-model.md`의 Project 엔티티 정의와 정확히 일치시켰다 (id, user_id, title, description, created_at, updated_at, last_activity_at, deletion_status, trashed_at, scheduled_deletion_at). User 모델에 비어 있던 `projects` relationship(back_populates, cascade="all, delete-orphan")도 함께 연결했다.

## 변경 파일
- `backend/src/models/project.py` (신규)
- `backend/src/models/user.py` (projects relationship 추가)
- `backend/tests/unit/test_project_model.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T043 체크)

## TDD 결과
- RED 커밋: 270421c (test: Project model - RED (T043))
- GREEN 커밋: 358bc21 (feat: Project SQLAlchemy model - GREEN (T043))
- REFACTOR 커밋: 해당 없음 (User/RefreshToken 모델과 동일한 패턴을 그대로 따라 구현해 추가 개선 불필요)
- 테스트 커버리지: 전체 백엔드 스위트 89 passed, src/models/project.py 100%

## 기술 결정
- 기존 User/RefreshToken 모델의 컨벤션(서버 사이드 default에 `server_default=text(...)` 사용, UUID는 `postgresql.UUID(as_uuid=True)`)을 그대로 따름.
- `ownership validation`(T045)과 서비스 레이어(T044)는 다음 태스크로 분리.

## 비고
- 테스트 실행 시 로컬(venv) 환경에서는 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드해야 한다 (루트 `.env`는 Docker 네트워크의 `db`/`redis` 호스트명을 사용하므로 venv에서 직접 실행 시 `getaddrinfo failed` 발생). docker-compose의 db/redis 컨테이너는 정상 기동 확인함.
- 브라우저 수동 테스트(T039-T042)는 Claude Chrome 확장 미연결로 보류 중 — 사용자가 확장 설치/로그인 후 재시도 예정. 백엔드(http://127.0.0.1:8000)와 프론트엔드(http://localhost:5173) 개발 서버는 계속 실행 중.
