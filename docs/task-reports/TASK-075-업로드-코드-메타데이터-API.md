# TASK-075. GET /tasks/{task_id}/code 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`에 태스크의 업로드 코드 메타데이터 조회 `GET /api/v1/tasks/{task_id}/code`를 추가했다. T069에서 구현해 둔 `CodeUploadService.get_for_task(task_id, user_id)`에 그대로 위임 — 소유권 확인(Task → Project), 404 처리(업로드가 아직 없는 경우 포함), `code_files` eager load는 전부 서비스 레이어가 담당한다.

응답 모델 2종을 신설했다:
- `CodeFileResponse`: `id`, `file_name`, `file_path`, `file_extension`, `file_size_bytes` — 실제 파일 바이트는 포함하지 않는다(브리프가 명시한 "메타데이터만으로 충분" 범위).
- `UploadedCodeResponse`: `id`, `task_id`, `detected_language`, `complexity_level`, `total_lines`, `total_files`, `upload_size_bytes`, `code_files: list[CodeFileResponse]`.

둘 다 기존 패턴과 동일하게 `model_config = {"from_attributes": True}`로 ORM 객체를 그대로 직렬화한다.

## 변경 파일
- `backend/src/api/tasks.py` (수정 — `CodeFileResponse`/`UploadedCodeResponse` 모델, `get_task_code` 핸들러 추가)
- `backend/tests/integration/test_tasks_api.py` (수정 — T075용 테스트 4개)
- `specs/001-ai-code-learning-platform/tasks.md` (T075 체크)

## TDD 결과
- RED 커밋: 37a929a (test: GET /tasks/{task_id}/code endpoint - RED (T075))
- GREEN 커밋: 7235835 (feat: GET /tasks/{task_id}/code endpoint - GREEN (T075))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 100%(T070~T075 전체 82 statements). 전체 백엔드 스위트 285 passed, 회귀 없음.

## 기술 결정
- **파일 원본 바이트는 반환하지 않음**: 브리프가 "메타데이터만으로 충분하다면 복잡도를 더하지 않는다"고 명시했고, `storage_path`로부터 실제 파일을 읽어 반환하는 것은 별도 엔드포인트(예: 다운로드/원문 보기 API)로 분리하는 편이 책임이 더 명확하다고 판단해 이번 task 범위에서는 제외했다. `CodeFileResponse`에도 `storage_path`를 노출하지 않음(내부 파일시스템 경로를 클라이언트에 노출하지 않기 위함 — `code_files.py` 모델 주석의 "not user-facing"과 동일한 이유).
- 테스트 하나(`test_get_task_code_returns_uploaded_code_metadata`)는 T071(생성+업로드)과 T070(목록)을 실제로 호출해 task_id를 얻은 뒤 이 엔드포인트를 검증 — 여러 task의 엔드포인트가 실제로 맞물려 동작하는지 확인하는 작은 통합 시나리오로 추가함.

## 비고
- 이로써 T067~T075(파일 저장 서비스, TaskService, CodeUploadService, Tasks API 6개 엔드포인트) 전체가 완료됨.
