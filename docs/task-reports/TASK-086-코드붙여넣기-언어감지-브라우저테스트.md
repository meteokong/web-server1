# TASK-086. 수동 브라우저 테스트: 코드 붙여넣기 → 언어 감지

## 상태
완료 (최초 FAIL → 버그 수정 → 재검증 PASS)

## 날짜
2026-10-22

## 작업 요약
"코드 붙여넣기" 방식으로 JavaScript 코드(`function add(a, b) { return a + b; }` 등)를 입력하고 언어 선택 드롭다운에서 "JavaScript"를 선택한 뒤 제출, `GET /tasks/{id}/code`의 `detected_language`가 `"javascript"`인지 검증했다.

**1차 시도 — 실패 발견**: 결과는 `detected_language == "text"`였다. 원인은 두 가지가 겹쳐 있었다:
1. `PasteCode.tsx`는 `{code, language}`를 모두 `onChange`로 올려보내지만, `CreateTaskModal.tsx:146`은 `onChange={({ code }) => setPastedCode(code)}`로 **`language`를 그대로 버리고** 있었다 — 선택 UI는 동작하지만 실제로는 전송되지 않는 "장식용" 컨트롤이었다.
2. 설사 전송됐더라도 백엔드가 받을 방법이 없었다 — 붙여넣기 업로드는 고정 파일명 `pasted_code.txt`로 저장되고, `CodeUploadService`는 항상 `detect_project_language(filenames)`로 확장자(`".txt"` → `"text"`) 기반 판별만 수행했다 — 콘텐츠 기반 판별로 넘어갈 일이 없었다(T069 당시 작성된 테스트 주석에 "확장자 힌트 없는 스니펫에서 실제 언어를 감지하는 것은 이 태스크의 범위 밖"이라고 명시돼 있었으나, 사용자가 드롭다운으로 직접 알려주는 값을 무시한다는 전제가 애초에 잘못되어 있었다).

**수정**:
- 백엔드: `CodeUploadService.upload()`/`POST /projects/{id}/tasks`에 선택적 `language` 파라미터 추가. 주어지면 `detect_project_language()` 대신 그 값을 그대로 `detected_language`로 사용(`language_detector.EXTENSION_TO_LANGUAGE`의 값 집합에 속하지 않으면 `ValidationAppError`).
- 프론트엔드: `CreateTaskModal.tsx`가 `pastedLanguage` 상태를 추적해 `onSubmit`에 포함, `task-service.ts`가 `language` form 필드로 전송.

**재검증**: 실제 UI로 JavaScript 코드 + "JavaScript" 선택 → 제출 → `GET /tasks/{id}/code`의 `detected_language == "javascript"` 확인 — PASS.

디버깅 중 한 가지 추가로 발견한 함정: 백엔드 서버를 `--reload` 없이 기동해 두었던 탓에, 코드 수정 후 첫 재검증에서는 여전히 `"text"`가 나와 한동안 "프론트엔드 수정이 안 먹힌 줄" 혼동했다 — `FormData.prototype.append`를 몽키패치해 실제 전송 payload에 `language: "javascript"`가 정확히 담겨 있음을 확인한 뒤에야 원인이 "서버 프로세스가 구 코드를 물고 있다"는 것임을 알아내고 서버를 재기동해 해결했다.

## 변경 파일
- `backend/src/services/code_analysis/code_upload_service.py` (`language` 파라미터, `_SUPPORTED_LANGUAGES` 검증)
- `backend/src/api/tasks.py` (`language: str | None = Form(None)` 추가)
- `backend/tests/integration/test_code_upload_service.py`
- `backend/tests/integration/test_tasks_api.py`
- `frontend/src/components/task/CreateTaskModal.tsx` (`pastedLanguage` 상태 추적)
- `frontend/src/components/task/CreateTaskModal.test.tsx`
- `frontend/src/services/task-service.ts` (`pastedLanguage` → `language` form 필드)
- `frontend/src/services/task-service.test.ts`
- `frontend/src/pages/ProjectDetail.tsx`

## TDD 결과
- RED 커밋: dbeb790 (test: explicit paste-language override + folder file_path assertion - RED), 4a05ca8, 5be4fdc
- GREEN 커밋: 880b8c2 (fix: respect explicit paste-code language instead of always "text" - GREEN), ddb649c
- REFACTOR 커밋: 해당 없음
- 테스트 결과: 백엔드 288 passed / 프론트엔드 77 passed, 0 regressions, 모든 신규 모듈/수정 함수 100% 커버리지 유지

## 기술 결정
- 콘텐츠 기반 언어 추측(Pygments 등, T065 참고)으로 확장하는 대신, **사용자가 드롭다운으로 명시한 값을 그대로 신뢰**하는 방식을 선택했다 — 사람이 직접 알려준 정보가 휴리스틱 추측보다 항상 더 정확하고, PasteCode UI가 이미 그 입력을 받고 있었으므로 "감지"가 아니라 "전달"의 문제였다.
- 설명을 신뢰하되 검증은 한다: `language`가 주어지면 `EXTENSION_TO_LANGUAGE`의 값 집합에 속하는지 확인해, 임의 문자열이 DB에 그대로 저장되는 것은 막았다.

## 비고
- 자동화된 백엔드/프론트엔드 유닛·통합 테스트가 이미 많이 존재했음에도(T069, T078, T080, T081 각각), 이 버그는 "모듈 간 배선"에 있었기 때문에 어느 한 모듈의 단위 테스트도 잡아내지 못했다 — 전체 플로우를 실제로 클릭해보는 수동 브라우저 테스트의 가치를 보여주는 두 번째 사례(T085와 동일한 패턴).
