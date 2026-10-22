# TASK-097. GET /tasks/{task_id}/document 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/documents.py`(신규)에 `GET /api/v1/tasks/{task_id}/document`를 구현했다. `get_current_user` 의존성으로 인증을 요구하고, `DocumentQueueService(db).get_document(task_id, current_user.id)`(T095 서비스에 새로 추가한 메서드)를 호출해 `{"task_id", "generation_status", "generation_error", "content"}` 모양의 `DocumentResponse`를 반환한다. `content`는 `generation_status == "completed"`일 때만 실제 값이고, 그 외(`pending`/`in_progress`/`failed`)에는 항상 `null`이다. `LearningDocument` 행이 아예 없으면(아직 생성이 트리거되지 않음) 404 대신 `pending` + `content: null`을 반환한다. `src/api/router.py`에 `documents_router`를 prefix 없이 등록했다(tasks.py와 동일한 패턴 — 각 라우트가 `/tasks/{task_id}/...` 전체 경로를 직접 명시).

## 변경 파일
- `backend/src/api/documents.py` (신규 — T098과 같은 파일에 함께 구현)
- `backend/src/api/router.py` (`documents_router` 등록)
- `backend/src/services/document/document_queue_service.py` (`get_document(task_id, user_id)` 메서드 추가)
- `backend/tests/integration/test_documents_api.py` (신규 — T097/T098 공통)
- `specs/001-ai-code-learning-platform/tasks.md` (T097 체크)

## TDD 결과
- RED 커밋: 123bfe5 (test: Documents API status/content endpoints and contract shape - RED (T097/T098))
- GREEN 커밋: f6b8637 (feat: add GET document and document/status endpoints - GREEN (T097/T098))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `/document` 관련 신규 통합 테스트 6개(문서 없을 때 pending+null content, `completed`일 때 content 포함, `in_progress`일 때 content 숨김, `failed`일 때 `generation_error` 노출 + content 숨김, 인증 없으면 401, 존재하지 않거나 소유자가 아닌 task면 404 `{"error":{"code":"not_found",...}}`). `DATABASE_URL`/`REDIS_URL`을 localhost로 override해 전체 스위트 344 passed, ruff 통과.

## 기술 결정
- **T097/T098을 같은 파일/같은 테스트 파일로 구현**: tasks.md 원문이 둘 다 `backend/src/api/documents.py`를 지정하고 있고, 두 엔드포인트가 같은 리소스(Task의 LearningDocument)를 서로 다른 모양으로 노출하는 것일 뿐이라 자연스럽게 함께 구현했다 — 커밋/체크박스/Task Report는 각각 분리해 두 태스크의 완료를 독립적으로 추적할 수 있게 했다.
- **`DocumentQueueService`에 `get_document` 메서드 추가(기존 `get_status`를 건드리지 않음)**: `get_status`(T095)는 이미 테스트/커밋이 끝난 안정적인 메서드라 수정하지 않고, 같은 "소유권 확인 → 행 조회 → 없으면 pending" 패턴을 공유하는 새 메서드를 추가하는 쪽을 선택했다. 서비스 레이어가 "완료 상태가 아니면 content를 절대 노출하지 않는다"는 보안/일관성 규칙을 갖고 있어, 라우터가 그 규칙을 다시 구현할 필요가 없다.
- **라우터는 얇게**: `src/api/tasks.py`와 동일한 패턴으로, 핸들러는 서비스 호출 + Pydantic 응답 모델 매핑만 하고, 404/401 등 에러 변환은 전역 예외 핸들러(`src/api/exceptions.py`)에 위임했다.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 localhost 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈).
- 프론트엔드 에이전트가 동시에 이 응답 계약으로 UI를 만들고 있어, 필드명/타입(특히 `content`가 `completed`가 아닐 때 항상 `null`이어야 한다는 점)을 CLAUDE 지시사항의 계약과 정확히 맞췄다.
