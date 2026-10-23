# TASK-071. POST /projects/{project_id}/tasks (멀티파트 업로드) 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`에 `POST /api/v1/projects/{project_id}/tasks`를 구현했다. `multipart/form-data`로 `title`, `description`(선택), `upload_method`(`file`/`folder`/`paste`), `files`(파일 업로드용 복수), `pasted_code`(붙여넣기용)를 받는다.

처리 순서:
1. `TaskService(db).create(...)`로 Task 생성(프로젝트 소유권 확인 + 제목 검증 + `task_number` 부여는 T068이 이미 처리).
2. `upload_method`가 `file`/`folder`면, 각 `UploadFile`에서 `(file_name, relative_path, content)` 튜플을 만든다 — `folder`일 때만 `relative_path`를 실제 경로로 채우고(`file`은 항상 `None`), `file_name`은 항상 경로의 마지막 요소(`Path(...).name`)만 사용.
3. `CodeUploadService(db, upload_root=...).upload(task.id, user.id, upload_method, files=..., pasted_code=...)`로 검증/저장/분석(T069) 수행.
4. 생성된 Task를 201로 반환.

**테스트 격리를 위한 `get_upload_root` 의존성**: `CodeUploadService`는 라우트 핸들러 안에서 직접 생성되므로(서비스이지 FastAPI dependency가 아님), 테스트가 실제 `storage/uploads`를 오염시키지 않도록 `upload_root: Path | None = Depends(get_upload_root)`라는 작은 dependency를 추가했다. 기본값은 `None`(운영 코드에서는 T067의 설정된 `UPLOAD_DIR` 사용)이고, 테스트는 `app.dependency_overrides[get_upload_root] = lambda: tmp_path`로 오버라이드한다.

## 변경 파일
- `backend/src/api/tasks.py` (수정 — `get_upload_root` dependency, `create_task` 핸들러 추가)
- `backend/tests/integration/test_tasks_api.py` (수정 — T071용 테스트 8개 + `_isolate_upload_root` autouse fixture)
- `backend/pyproject.toml` (수정 — `[tool.coverage.run] concurrency = ["greenlet", "thread"]` 추가)
- `specs/001-ai-code-learning-platform/tasks.md` (T071 체크)

## TDD 결과
- RED 커밋: 9ced9f0 (test: POST /projects/{id}/tasks multipart upload endpoint - RED (T071))
- GREEN 커밋: c6c6b9b (feat: POST /projects/{id}/tasks multipart upload endpoint - GREEN (T071))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 100%. 전체 백엔드 스위트 269 passed, 회귀 없음.

## 기술 결정
- **커버리지 측정 버그 발견 및 수정(`pyproject.toml`)**: 이 task를 구현하며 처음엔 `src/api/tasks.py`가 76%로 측정됐는데, 실제로는 모든 분기가 테스트로 실행되고 있었다. 원인은 SQLAlchemy의 async 엔진이 동기 DBAPI를 호출할 때 `greenlet_spawn`으로 스택을 전환하는데, `coverage.py`의 기본 추적기(`sys.settrace`)가 그 전환 전후의 동일 함수 안 동기 코드(두 `await db...` 호출 사이의 for 루프 등)를 누락 집계하는 것이었다. `[tool.coverage.run] concurrency = ["greenlet", "thread"]`를 추가해 해결 — 이 설정이 없었다면 이 코드베이스의 **다른 API 레이어 커버리지도 전부 실제보다 낮게 보고되고 있었을 것** (서비스 레이어 테스트들은 awaits 사이에 거의 동기 코드가 없어 우연히 영향이 작았음).
- **폴더 업로드의 `relative_path`는 `upload_method == "folder"`일 때만 설정**: 브라우저의 `webkitdirectory` 업로드는 멀티파트 `filename` 필드 자체에 풀 경로(`"src/main.py"`)를 담아 보내는 것이 일반적인 패턴이므로, API 레이어가 그 경로에서 디스플레이용 파일명(`Path(...).name`)과 저장용 상대 경로를 분리한다. `file` 업로드는 항상 평면 구조로 간주해 `relative_path=None`.
- `CodeUploadService`를 FastAPI dependency가 아니라 핸들러 안에서 직접 생성(`ProjectService`/`TaskService`와 동일한 패턴) — 유일하게 다른 점은 `upload_root`를 테스트에서 주입할 수 있도록 그 값만 별도 dependency로 분리한 것.

## 비고
- `description`의 500자 제한은 T068과 동일하게 이번 범위에서 검증하지 않음.
- 업로드 실패(`ValidationAppError`) 시 Task는 이미 생성된 상태로 남는다(Task 생성과 업로드 처리가 하나의 DB 트랜잭션으로 묶여 있지 않음) — MVP 범위에서는 사용자가 실패한 업로드를 다시 시도하면 되므로 허용 가능한 단순화로 판단했으나, 추후 "업로드 실패 시 Task도 함께 롤백"이 요구되면 두 단계를 하나의 서비스 메서드로 합치는 리팩토링이 필요하다.
