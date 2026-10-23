# TASK-096. 코드 업로드 후 문서 생성 트리거 연결

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/code_analysis/code_upload_service.py`의 `CodeUploadService.upload()` 끝부분에 T095 `DocumentQueueService.enqueue(task_id, user_id)` 호출을 연결했다. `CodeUploadService.__init__`가 `enqueue_document_generation` 콜러블을 선택적으로 주입받게 했고(기본값은 `DocumentQueueService(self.db).enqueue`를 감싼 `_default_enqueue`), `upload()`는 검증 실패 없이 `_store_and_analyze`가 성공적으로 끝난 뒤에만(업로드가 실제로 저장된 뒤에만) 이 콜러블을 호출한다. 검증 실패(`ValidationAppError`) 시에는 이 트리거가 절대 호출되지 않도록 `_store_and_analyze` 호출 뒤에 배치했다.

## 변경 파일
- `backend/src/services/code_analysis/code_upload_service.py` (`enqueue_document_generation` 생성자 파라미터 + `upload()` 끝에서 호출)
- `backend/tests/integration/test_code_upload_document_trigger.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T096 체크)

## TDD 결과
- RED 커밋: ab44cc0 (test: CodeUploadService triggers document generation after upload - RED (T096))
- GREEN 커밋: e0bbf10 (feat: trigger async document generation after a successful code upload - GREEN (T096))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 통합 테스트 3개(주입한 fake enqueue 콜러블이 업로드 성공 후 `task_id`/`user_id`로 정확히 1회 호출됨, 검증 실패 시에는 호출되지 않음, 아무것도 주입하지 않았을 때 기본값인 실제 `DocumentQueueService`가 동작해 `LearningDocument` 행이 `pending` 상태 + `celery_task_id`로 생성됨) + 기존 `test_code_upload_service.py`의 upload 관련 테스트 전부(13개) 수정 없이 그대로 통과. `DATABASE_URL`/`REDIS_URL`을 localhost로 override해 전체 스위트 332 passed, ruff 통과.

## 기술 결정
- **TaskService가 아니라 CodeUploadService에 연결**: tasks.md 원문은 "TaskService"라고 쓰여 있지만, 실제로 업로드 성공 여부를 아는 쪽은 `CodeUploadService.upload()`뿐이다. `TaskService`는 Task 행의 CRUD만 담당하고 업로드/코드 파일에 대해 전혀 모른다(`backend/src/services/task_service.py`에 업로드 관련 코드가 없음). "방금 업로드가 끝났다"는 사실을 가장 먼저, 가장 정확하게 아는 지점에 트리거를 두는 것이 책임 소재상 맞다고 판단했다.
- **`enqueue_document_generation`을 생성자에서 주입 가능하게 설계**: 기본값(실제 `DocumentQueueService(db).enqueue`)을 쓰면 실제 Celery `.delay()`가 로컬 Redis로 메시지를 보내지만, 워커가 떠 있지 않은 테스트 환경에서는 그 메시지를 아무도 소비하지 않으므로 실제 Gemini 호출이 절대 일어나지 않는다(확인: `test_upload_without_injected_enqueue_uses_real_document_queue_service`). 그래도 "진짜 디스패치 로직"과 "업로드 자체의 저장/검증 로직"을 테스트에서 독립적으로 검증하고 싶을 때를 위해 fake 콜러블 주입 경로를 열어뒀다 — 기존 `test_code_upload_service.py`의 13개 테스트가 이 파라미터 없이도 전혀 수정 없이 통과하는 것으로, 기본 동작이 하위 호환됨을 확인했다.
- **트리거 호출 위치는 `_store_and_analyze` 성공 이후, `upload()` 반환 직전**: 검증(확장자/크기/바이너리/파일 개수)이 전부 끝나고 DB에 `UploadedCode`/`CodeFile`이 실제로 flush된 뒤에만 호출되도록 배치해, "검증 실패한 업로드에 대해 문서 생성이 큐에 잡히는" 상황을 원천적으로 막았다.
- **순환 임포트 없음**: `code_upload_service.py` → `document_queue_service.py` → `src/tasks/document_generation.py` → `document_generation_service.py` 방향으로만 의존하고, 반대 방향 의존이 없어 모듈 임포트 시점 문제가 없음을 확인했다.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 localhost 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈).
- 실제 운영 환경에서는 Celery 워커가 떠 있어야 큐에 쌓인 `generate_document_task`가 실제로 실행되어 `LearningDocument.content`가 채워진다 — 이 태스크 범위에서는 디스패치(큐에 넣는 것)까지만 다루고, 워커 기동/모니터링은 범위 밖이다.
