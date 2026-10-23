# TASK-095. 문서 생성 큐/상태 조회 서비스 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/document/document_queue_service.py`에 `DocumentQueueService(db, dispatch=None)`를 구현했다. `async def enqueue(task_id, user_id) -> LearningDocument`는 (1) `TaskService.get`으로 소유권 확인, (2) 해당 Task의 `LearningDocument` 행을 찾거나(T093과 동일한 `_PLACEHOLDER_CONTENT`로) 새로 만들고, (3) `generation_status="pending"`으로 표시한 뒤, (4) `dispatch(task_id, user_id)`(기본값은 T094의 `generate_document_task.delay`)를 호출해 Celery에 디스패치하고, (5) 반환된 AsyncResult의 `.id`를 `celery_task_id`에 저장한다. `async def get_status(task_id, user_id) -> dict`는 소유권 확인 후, 해당 Task의 `LearningDocument.generation_status`/`generation_error`/`generation_started_at`/`generation_completed_at`을 담은 dict를 반환하며, 행이 아직 없으면(생성이 트리거되지 않음) 404 대신 `"pending"` + 나머지 필드 `null`을 반환한다(T097/T098 API 계약과 동일한 모양).

## 변경 파일
- `backend/src/services/document/document_queue_service.py` (신규)
- `backend/tests/integration/test_document_queue_service.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T095 체크)

## TDD 결과
- RED 커밋: 668ab91 (test: DocumentQueueService enqueue/status tracking - RED (T095))
- GREEN 커밋: 20f2968 (feat: add DocumentQueueService to enqueue generation and report status - GREEN (T095))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 통합 테스트 6개 — enqueue 성공(pending 상태 + celery_task_id 저장 + dispatch 호출 인자 확인), 재호출 시 중복 행 생성 안 됨(기존 행 재사용 + celery_task_id 갱신), 소유자 아닌 경우 NotFoundError, 문서 없을 때 get_status가 pending+null로 응답, 문서 있을 때 필드 반환, 소유자 아닌 경우 get_status에서도 NotFoundError. `DATABASE_URL`/`REDIS_URL`을 localhost로 override해 전체 스위트 329 passed, ruff 통과.

## 기술 결정
- **`dispatch`를 생성자 주입 가능하게 설계**: 기본값은 실제 T094 `generate_document_task.delay`이지만, 테스트에서는 fake dispatcher(AsyncResult처럼 `.id`만 가진 객체를 반환하는 callable)를 주입해 실제 Celery 브로커 왕복 없이 "디스패치 호출 + 반환된 id 저장" 로직만 검증했다. 이렇게 하면 T096에서 `CodeUploadService`가 이 서비스를 사용할 때도 업로드 테스트가 real Celery/Redis에 의존하지 않도록 만들 수 있다.
- **`get_status`가 행이 없을 때 404 대신 pending 반환**: tasks.md/CLAUDE 지시사항의 API 계약("LearningDocument row가 아예 없으면... 404를 던지지 말고 pending 상태로 응답하라")을 서비스 레이어에서부터 지켜, T098 API 핸들러가 별도 분기 없이 서비스 반환값을 그대로 응답 모델에 매핑할 수 있게 했다.
- **`_PLACEHOLDER_CONTENT`를 T093의 것과 동일하게 재사용(복제)**: `LearningDocument.content`가 NOT NULL + 7챕터 키 존재 CHECK라서 "아직 content 없는 pending 행"을 만들 때 동일한 플레이스홀더가 필요하다. 공유 상수로 더 깔끔하게 뺄 수도 있었지만, 두 서비스가 서로의 세부 구현에 의존하지 않도록(각자 독립적으로 리팩토링 가능하도록) 의도적으로 각자 정의했다.
- **`get_status`에서 Celery `AsyncResult(celery_task_id).state`는 참고하지 않음**: T098 API 응답 계약이 DB 컬럼(`generation_status`/`generation_error`/타임스탬프)만 요구하고, `DocumentGenerationService`/`generate_document_task`가 이미 그 컬럼들을 생성 과정 전체(시작/완료/실패)에서 정확히 갱신하므로 Celery 자체 상태를 추가로 조회할 필요가 없었다. DB 하나의 소스만 보면 되므로 더 단순하고 결정적이다.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 localhost 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈).
- T096에서 `CodeUploadService.upload()`가 이 서비스의 `enqueue()`를 호출하도록 연결할 예정이다.
