# TASK-093. DocumentGenerationService (재시도 로직 포함) 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/document/document_generation_service.py`에 `DocumentGenerationService`를 구현했다. `generate(task_id, user_id)`는 (1) TaskService로 소유권 확인, (2) UploadedCode+CodeFile을 조회해 `storage_path`의 실제 파일 내용을 읽어 T092 `CodeFileInput`으로 변환, (3) `detected_language`/`complexity_level`을 포함해 T092 `build_document_generation_prompt`로 프롬프트 생성, (4) T091 `GeminiClient.generate_content(..., response_mime_type="application/json")`를 **지수 백오프로 최대 3회(research.md) 재시도**, (5) 성공 시 JSON 파싱 + 7챕터 키 존재 검증 후 T090 `LearningDocument`에 저장, 실패 시 `generation_status="failed"` + `generation_error`를 남기고 `DocumentGenerationError`를 던진다.

## 변경 파일
- `backend/src/services/document/document_generation_service.py` (신규)
- `backend/tests/integration/test_document_generation_service.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T093 체크)

## TDD 결과
- RED 커밋: 0b79fae (test: DocumentGenerationService orchestration + retry logic - RED (T093))
- GREEN 커밋: 74808a7 (feat: add DocumentGenerationService with exponential-backoff retry - GREEN (T093))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 통합 테스트 9개 모두 통과(`DATABASE_URL`을 localhost로 override해 실제 Postgres에 대해 실행). 전체 unit+integration 스위트 318 passed(동일 override 적용 시) — 기존에 알려진 120개 integration 실패는 "db" 호스트명이 로컬 venv에서 DNS로 해석되지 않는 환경 문제였음을 이번에 재확인(override 시 전부 통과). 추가로 실제 DB + 실제 Gemini API로 end-to-end 스모크 테스트 수행: `greet.py` 코드 업로드 → `generate()` 호출 → `status=completed`, 7개 챕터 모두 정상 생성됨을 확인.

## 기술 결정
- **재시도는 서비스 레이어에 위치**: T091 Task Report에서 이미 결정한 대로, GeminiClient는 에러만 던지고 재시도 정책(지수 백오프, 최대 3회)은 이 서비스가 소유. 테스트에서는 `sleep` 콜백을 주입해(`sleep=lambda _: None`) 실제 대기 없이 재시도 로직만 검증.
- **`LearningDocument.content`는 NOT NULL + 7챕터 키 존재 CHECK 제약**이라 "아직 content 없는 pending 행"을 저장할 방법이 없음 → `in_progress`/`failed` 상태에서도 행이 존재할 수 있도록 `_PLACEHOLDER_CONTENT`(7개 챕터 키 전부 `null`)로 우선 생성한 뒤, 성공 시에만 실제 content로 덮어씀. CHECK 제약은 `content ? 'chapterN'`(키 존재 여부)만 검사하므로 값이 `null`이어도 통과함.
- **Gemini가 유효하지 않은 JSON을 반환하거나 7챕터 중 일부가 빠진 경우**도 `GeminiAPIError`로 통일해 재시도 대상에 포함시킴 (`json.JSONDecodeError`/`ValidationAppError` → `GeminiAPIError`로 변환) — "형식이 깨진 응답"과 "API 자체 에러"를 호출자 입장에서 구분할 필요가 없다고 판단.
- **재생성(regenerate) 정책은 이 서비스에서 제한하지 않음**: FR-038("저장된 문서는 재조회 시 재생성하지 않음")은 "뷰 조회 시 자동 재생성 금지"를 의미하므로 API 레이어(추후 작업)에서 지킬 정책이고, `generate()` 자체는 명시적으로 호출되면 기존 문서를 덮어쓰도록 구현(`_get_or_create_document`가 기존 행을 재사용) — 테스트로 멱등성(동일 task_id에 중복 행 생성 안 됨)을 확인.
- 코드 파일 내용을 프롬프트에 넣을 때 파일명은 `file_path or file_name`을 사용 — 폴더 업로드의 상대 경로(`src/utils/helpers.py`)가 있으면 그걸, 없으면(flat 업로드) `file_name`을 그대로 사용해 Chapter 3의 file_breakdown이 실제 폴더 구조를 반영하도록 함.

## 비고
- 로컬 venv 실행 시 이번에도 `DATABASE_URL`을 `localhost` 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈, docker-compose의 `db` 호스트명은 compose 네트워크 내부에서만 해석됨).
- T094(Celery 비동기 태스크)에서 이 서비스를 호출할 때는 `generate()`가 async이므로 Celery 워커 쪽에서 적절히 이벤트 루프를 돌려야 함 — 이번 태스크 범위 밖이라 별도 처리하지 않음.
