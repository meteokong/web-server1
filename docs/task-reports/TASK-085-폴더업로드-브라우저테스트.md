# TASK-085. 수동 브라우저 테스트: 폴더 업로드 (구조 보존)

## 상태
완료 (최초 FAIL → 버그 수정 → 재검증 PASS)

## 날짜
2026-10-22

## 작업 요약
"폴더 업로드" 방식으로 2개 파일(`sample_project/main.py`, `sample_project/utils.py`)을 업로드해 폴더 구조(상대 경로)가 보존되는지 검증했다.

**1차 시도 — 실패 발견**: 브라우저 자동화 도구는 OS의 실제 폴더 선택 다이얼로그를 흉내낼 수 없어 `File.webkitRelativePath`가 항상 빈 문자열로 주입됐다. 이 상태로는 프론트엔드 로직 자체가 제대로 동작하는지 가려지므로, `GET /tasks/{id}/code`로 저장된 `code_files[].file_path`를 직접 확인한 결과 둘 다 `null`이었다. 원인을 추적한 결과, 자동화 도구의 한계가 아니라 **실제 프론트엔드 버그**였다:
- `FolderUpload.tsx`는 각 파일의 `relativePath`를 정확히 캡처하지만, `CreateTaskModal.tsx:141`에서 `setFiles(picked.map((p) => p.file))`로 **relativePath를 버린 채 `File` 객체만 보관**하고 있었다.
- `task-service.ts`도 `formData.append("files", file)`처럼 2-인자 형태로만 호출해, 전송되는 멀티파트 파일명이 항상 `file.name`(베이스네임)이었다 — 백엔드(`tasks.py`)는 파일명에 경로 구분자가 있는지로 `relative_path`를 판별하므로, 베이스네임만 오면 항상 평면 파일로 처리된다.
- 반면 백엔드 자체 로직은 이미 올바르게 동작했다(`test_create_task_with_folder_upload_sets_nested_relative_paths`가 httpx로 `"src/main.py"`라는 파일명을 직접 보내 이미 통과하고 있었음 — 다만 `file_path` 값 자체를 검증하는 assertion이 빠져 있어 이번에 보강함).

**수정**: `CreateTaskModal.tsx`가 `relativePaths` 상태를 별도로 추적해 `onSubmit`에 포함하도록, `task-service.ts`의 `createTask`가 `formData.append("files", file, relativePath ?? file.name)`(3-인자 폼)로 실제 경로를 파일명으로 전송하도록 수정. 자세한 TDD 사이클은 변경 파일 참고.

**재검증**: 브라우저 페이지 컨텍스트에서 JS로 `webkitRelativePath`를 설정한 `File` 객체를 만들어 `DataTransfer`에 담아 실제 폴더-선택 input에 주입한 뒤 UI로 제출(순수 단위 테스트로는 검증되지 않는, 실제 React 컴포넌트 경로를 통한 end-to-end 검증). 결과: `code_files[0].file_path == "verify_project/main.py"`, `code_files[1].file_path == "verify_project/utils.py"` — PASS.

## 변경 파일
- `backend/tests/integration/test_tasks_api.py` (folder 테스트에 `file_path` assertion 보강)
- `frontend/src/services/task-service.ts` (`relativePaths` 필드 추가, 3-인자 `formData.append`)
- `frontend/src/services/task-service.test.ts`
- `frontend/src/components/task/CreateTaskModal.tsx` (`relativePaths` 상태 추적 및 전달)
- `frontend/src/components/task/CreateTaskModal.test.tsx`
- `frontend/src/pages/ProjectDetail.tsx` (`relativePaths`를 `createTask` 호출에 전달)

## TDD 결과
- RED 커밋: 4a05ca8 (test: task-service sends relativePath as filename + language for paste - RED), 5be4fdc (test: CreateTaskModal forwards relativePath/language to onSubmit - RED)
- GREEN 커밋: ddb649c (fix: forward folder relativePath and paste language to the API - GREEN)
- REFACTOR 커밋: 해당 없음
- 테스트 결과: 프론트엔드 전체 77 passed, 0 regressions

## 기술 결정
- 백엔드는 변경하지 않았다 — 폴더 구조 보존 로직은 이미 `tasks.py`에 올바르게 구현되어 있었고(파일명에 `/`가 있으면 그 전체를 `relative_path`로 사용), 누락된 건 프론트엔드가 그 경로를 멀티파트 파일명으로 실어 보내는 부분뿐이었다.

## 비고
- 이 버그는 자동화된 유닛 테스트(FolderUpload.test.tsx, CreateTaskModal.test.tsx)만으로는 발견되지 않았다 — 각 컴포넌트를 독립적으로 테스트할 때는 `relativePath`가 올바르게 캡처/전달되는 것처럼 보였지만, 두 컴포넌트 사이의 배선(CreateTaskModal이 FolderUpload의 출력을 어떻게 소비하는지)에 결함이 있었다. 통합 수준의 수동 브라우저 테스트가 정확히 이런 종류의 결함을 잡기 위한 것임을 보여주는 사례.
