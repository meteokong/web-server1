# TASK-069. CodeUploadService 구현 (파일/폴더/붙여넣기 업로드 통합 처리)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/code_analysis/code_upload_service.py`에 `CodeUploadService`를 구현했다. 하나의 Task에 대한 세 가지 업로드 방식(file/folder/paste, FR-005~FR-007)을 모두 처리하며, 앞서 구현된 T064(파일 검증)/T065(언어 감지)/T066(복잡도 분석)/T067(파일 저장) 유틸리티를 그대로 재사용한다(재구현 없음).

- `upload(task_id, user_id, upload_method, *, files=None, pasted_code=None)`: 단일 진입점.
  1. `TaskService(db).get(task_id, user_id)`로 소유권 확인 (404).
  2. `upload_method`에 따라 입력을 `(filename, relative_path, content)` 튜플 리스트로 정규화 — `paste`는 고정 파일명 `pasted_code.txt` 1개로 취급.
  3. **쓰기 전 전체 검증**: `validate_file_count` → 각 파일의 `validate_extension`/`validate_size`/`validate_not_binary`. 하나라도 실패하면 디스크/DB에 아무것도 쓰지 않고 `ValidationAppError` 발생(부분 상태 방지).
  4. 검증 통과 후에만 `file_storage.save_uploaded_file`로 실제 저장, `detect_project_language`/`analyze_project_complexity`로 분석, `UploadedCode` 1건 + `CodeFile` N건을 생성.
- `get_for_task(task_id, user_id)`: 소유권 확인 후 `UploadedCode`를 `code_files`까지 eager load(`selectinload`)해서 반환 — 업로드가 없으면 `NotFoundError`.

## 변경 파일
- `backend/src/services/code_analysis/code_upload_service.py` (신규)
- `backend/tests/integration/test_code_upload_service.py` (신규, 14개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T069 체크)

## TDD 결과
- RED 커밋: 5b17d6a (test: CodeUploadService (file/folder/paste upload) - RED (T069))
- GREEN 커밋: cb13626 (feat: CodeUploadService (file/folder/paste upload, validate-then-store) - GREEN (T069))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/services/code_analysis/code_upload_service.py` 100%. 전체 백엔드 스위트 257 passed, 회귀 없음.

## 기술 결정
- **입력 타입은 튜플, 별도 DTO/dataclass 미사용**: `(filename, relative_path, content)` 튜플 리스트를 그대로 받도록 설계 — T071(업로드 API)이 멀티파트 `UploadFile`에서 이 튜플을 만들어 넘기기만 하면 되므로 API ↔ 서비스 경계가 가장 단순해진다. `relative_path`가 `None`이면 평면 업로드(파일 자체가 곧 저장 대상), 값이 있으면 폴더 업로드의 하위 경로.
- **테스트에서 실제 `storage/uploads`를 건드리지 않도록 `upload_root`를 생성자 주입으로 노출**: `CodeUploadService(db, upload_root=tmp_path)`. 운영 코드는 생략하면 T067의 `get_storage_settings().upload_root` 기본값을 그대로 사용.
- **붙여넣기(paste) 업로드의 언어 감지는 확장자 기준으로만 동작**: 고정 파일명이 `pasted_code.txt`(`.txt`)이므로 `detect_project_language`가 확장자 매핑(`text`)으로 바로 해석되고, Pygments 콘텐츠 기반 폴백은 트리거되지 않는다. 테스트 작성 중 처음에는 "python 코드를 붙여넣으면 python으로 감지될 것"이라 잘못 가정했다가, 실제 동작(확장자 우선)을 확인하고 테스트 기대값을 `"text"`로 수정했다 — 구현을 테스트에 맞춰 억지로 바꾼 것이 아니라, 테스트의 잘못된 전제를 실제 동작에 맞게 고친 것. 확장자 없는 붙여넣기의 콘텐츠 기반 언어 추정은 이번 task 범위 밖(필요 시 추후 `pasted_code.txt` 대신 언어 힌트를 받아 확장자를 붙이는 방식으로 확장 가능).
- **SQLAlchemy 매퍼 초기화 이슈(T068에서 발견한 것과 동일 원인) 재사용**: `TaskService` import를 통해 이미 `CodeFile`/`UploadedCode`가 레지스트리에 등록되므로, 이 서비스에서 별도 조치가 필요 없었다.
- `await self.db.refresh(uploaded_code, attribute_names=["code_files"])`로 생성 직후 반환값에 `code_files` 관계를 즉시 채워 넣음 — 호출자가 추가 쿼리 없이 바로 `uploaded_code.code_files`를 쓸 수 있도록(T071의 응답 직렬화에서 필요).

## 비고
- `description`처럼 데이터 모델의 추가 CHECK 제약(예: CodeFile/UploadedCode 쪽 제약)은 이번 task에서 별도로 재검증하지 않음 — T064의 `file_validator`가 이미 DB CHECK 제약과 정확히 일치하도록 설계되어 있으므로 중복 검증 없이 그대로 재사용.
- 이 서비스는 T071(POST /projects/{id}/tasks 업로드)과 T075(GET /tasks/{id}/code)에서 바로 연결된다.
