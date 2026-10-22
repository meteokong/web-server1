# TASK-080. Task 서비스 구현 (CRUD + 업로드 API 호출)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/services/task-service.ts`에 `project-service.ts`(T053)와 동일한 `ResponseBody` → `toTask()` 매핑 패턴으로 태스크 CRUD 함수들을 구현했다.
- `listTasks(projectId)`: `GET /projects/{id}/tasks` → `{tasks: [...]}` 언래핑.
- `createTask(projectId, fields)`: `POST /projects/{id}/tasks`를 `multipart/form-data`로 전송 — `title`/`description`/`upload_method`는 항상, `file`/`folder` 방식이면 `files[]`를, `paste` 방식이면 `pasted_code`를 FormData에 담음.
- `getTask(taskId)` / `updateTask(taskId, fields)` / `deleteTask(taskId)`: 각각 `GET`/`PATCH`/`DELETE /tasks/{id}`.
- `getTaskCode(taskId)`: `GET /tasks/{id}/code` → `{ uploadedCode, files }` camelCase 매핑.

이와 함께 `frontend/src/types/task.ts`에 `UploadedCode`, `CodeFile` 타입을 추가했다(T079에서 만든 `Task` 타입에 이어서).

## 변경 파일
- `frontend/src/services/task-service.ts` (신규)
- `frontend/src/services/task-service.test.ts` (신규, 7개 테스트)
- `frontend/src/types/task.ts` (수정 — `UploadedCode`, `CodeFile` 타입 추가)
- `specs/001-ai-code-learning-platform/tasks.md` (T080 체크)

## TDD 결과
- RED 커밋: 5c5fdef (test: task service CRUD + upload API calls - RED (T080))
- GREEN 커밋: f8c59b7 (feat: task service CRUD + upload API calls - GREEN (T080))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 7/7 테스트 통과, TaskCard(T079) 포함 전체 재실행 9/9 통과

## 기술 결정
- `project-service.test.ts`가 `vi.mock("./api-client", ...)`로 axios 전체를 모킹하는 패턴을 그대로 사용 — 백엔드 서버 없이도 요청 형태(URL, FormData 내용, 헤더)와 매핑 결과를 둘 다 검증.
- multipart 요청은 `Content-Type: multipart/form-data`를 명시적으로 지정 — axios가 FormData를 보낼 때 boundary를 자동으로 채워주더라도, 테스트에서 헤더 존재를 확인할 수 있도록 명시했다.
- `createTask`의 `files`/`pastedCode`는 업로드 방식에 따라 옵셔널로 둬서, CreateTaskModal(T081)이 활성 탭에 맞는 값만 채워 호출할 수 있게 함.

## 비고
- `getTaskCode`는 이번 태스크 범위에서 서비스 함수만 구현 — 실제로 호출하는 UI(코드 보기 화면)는 이후 태스크.
