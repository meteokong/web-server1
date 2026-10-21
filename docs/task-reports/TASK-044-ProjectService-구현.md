# TASK-044. ProjectService 구현 (create/get/update/soft delete)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`backend/src/services/project_service.py`에 ProjectService를 구현했다. T009 Project 모델(T043)을 대상으로 `create`, `get`, `update`, `soft_delete` 4개 메서드를 제공한다.
- `create`: 제목이 빈 문자열(공백 포함)이면 `ValidationAppError`, 아니면 Project row를 생성해 flush 후 반환.
- `get`: `project_id`로 조회, 없으면 `NotFoundError`.
- `update`: 전달된 필드(title/description)만 갱신, title이 주어졌는데 공백이면 `ValidationAppError`, `updated_at` 갱신.
- `soft_delete`: `deletion_status='trashed'`, `trashed_at=now`, `scheduled_deletion_at=trashed_at+30일`로 설정 (data-model.md의 30일 보존 정책).

소유권 검증(project.user_id와 요청자 일치 여부)은 범위에 포함하지 않았다 — T045에서 별도로 구현한다.

## 변경 파일
- `backend/src/services/project_service.py` (신규)
- `backend/tests/integration/test_project_service.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T044 체크)

## TDD 결과
- RED 커밋: 45cf9e4 (test: ProjectService (create/get/update/soft-delete) - RED (T044))
- GREEN 커밋: a5742b8 (feat: ProjectService (create/get/update/soft-delete) - GREEN (T044))
- REFACTOR 커밋: 해당 없음 (UserService와 동일한 패턴으로 이미 단순/명료)
- 테스트 커버리지: 전체 백엔드 스위트 98 passed, src/services/project_service.py 100%

## 기술 결정
- 조회 실패를 `NotFoundError`(404)로 통일 — 존재하지 않는 project_id와 (추후 T045에서 다룰) 소유자가 다른 project_id를 동일하게 취급해 리소스 존재 여부를 노출하지 않는 기존 auth 서비스들의 패턴을 그대로 따름.
- `get`/`update`/`soft_delete`는 내부적으로 `self.db.get(Project, project_id)`를 사용하는 `_get_or_404` 헬퍼로 중복 제거.
- Trash 목록 조회·복원·영구 삭제는 Phase 10(`trash_service.py`, T170-T172)에서 별도로 다루므로 이번 task 범위에 포함하지 않음.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일한 환경 이슈, docker-compose db/redis는 정상).
- 브라우저 수동 테스트(T039-T042)는 Claude Chrome 확장 연결 대기 중. 백엔드/프론트엔드 개발 서버는 계속 실행 중.
