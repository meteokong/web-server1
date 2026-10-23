# TASK-098. GET /tasks/{task_id}/document/status 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/documents.py`(T097과 같은 파일)에 `GET /api/v1/tasks/{task_id}/document/status`를 구현했다. `get_current_user` 의존성으로 인증을 요구하고, `DocumentQueueService(db).get_status(task_id, current_user.id)`(T095에서 이미 구현된 메서드)를 호출해 `{"task_id", "generation_status", "generation_error", "generation_started_at", "generation_completed_at"}` 모양의 `DocumentStatusResponse`를 반환한다. `LearningDocument` 행이 아예 없으면 404 대신 `generation_status: "pending"` + 나머지 필드 `null`을 반환하고, 존재하지 않거나 소유자가 아닌 task에는 404 `{"error": {"code": "not_found", ...}}`를 반환한다.

## 변경 파일
- `backend/src/api/documents.py` (T097과 함께 구현, `get_document_status` 핸들러)
- `backend/src/api/router.py` (T097에서 등록 완료)
- `backend/tests/integration/test_documents_api.py` (T097과 공통 파일, `/document/status` 관련 테스트 포함)
- `specs/001-ai-code-learning-platform/tasks.md` (T098 체크)

## TDD 결과
- RED 커밋: 123bfe5 (test: Documents API status/content endpoints and contract shape - RED (T097/T098))
- GREEN 커밋: f6b8637 (feat: add GET document and document/status endpoints - GREEN (T097/T098))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `/document/status` 관련 신규 통합 테스트 5개(문서 없을 때 pending+null 응답, `completed` 문서의 타임스탬프/상태 필드 반환, 인증 없으면 401, 존재하지 않는 task 404, 소유자가 아닌 task 404). `DATABASE_URL`/`REDIS_URL`을 localhost로 override해 전체 스위트 344 passed, ruff 통과.

## 기술 결정
- **`get_status`는 T095에서 이미 구현된 메서드를 그대로 재사용**: 이번 태스크는 그 위에 얇은 FastAPI 라우트 하나만 얹는 것으로 충분했다 — 서비스 레이어가 이미 "행 없으면 pending+null" 규칙과 소유권 확인(`TaskService.get`을 통한 404)을 책임지고 있어 핸들러 코드가 최소화됐다.
- **응답 모델(`DocumentStatusResponse`)의 필드 타입을 ORM 컬럼과 그대로 맞춤**: `generation_status`/`generation_error`를 전부 `str | None`으로, 타임스탬프는 `datetime | None`으로 선언해 Pydantic이 `LearningDocument`의 실제 nullable 컬럼 구조(T090)와 서비스가 반환하는 dict를 그대로 직렬화할 수 있게 했다 — 별도 변환/매핑 로직이 필요 없었다.
- **status와 document(T097) 두 라우트의 등록 순서가 충돌하지 않음을 확인**: `/tasks/{task_id}/document`와 `/tasks/{task_id}/document/status`는 세그먼트 개수가 달라 FastAPI/Starlette 라우팅에서 서로를 가리는 문제가 없다(어느 순서로 등록해도 동작) — 실제 통합 테스트로도 두 경로 모두 독립적으로 올바르게 매칭됨을 확인했다.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 localhost 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈).
- 이것으로 T094~T098(비동기 문서 생성 파이프라인: Celery 태스크 → 큐/상태 서비스 → 업로드 트리거 → 조회 API) 전체가 완료됐다.
