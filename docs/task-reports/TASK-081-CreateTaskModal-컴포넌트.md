# TASK-081. CreateTaskModal 구현 (3가지 업로드 방식)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/task/CreateTaskModal.tsx`에 `CreateProjectModal`(T052)과 동일한 `open`/`onClose`/`onSubmit` dialog 패턴으로 태스크 생성 모달을 구현했다.
- 제목/설명 입력 + 업로드 방식 라디오 3개(파일 업로드/폴더 업로드/코드 붙여넣기)로 구성.
- 선택된 방식에 따라 FileUpload(T076)/FolderUpload(T077)/PasteCode(T078) 중 하나를 조건부로 렌더링. FolderUpload가 돌려주는 `{file, relativePath}[]`는 `file`만 뽑아 공통 `files: File[]` 상태로 합침.
- 제목이 5자 미만이면(백엔드 규칙과 동일) `onSubmit` 호출 전에 `role="alert"`로 에러를 보여주고 제출을 막음.
- 제출 시 `{ title, description, uploadMethod, files? | pastedCode? }`를 onSubmit으로 전달 — paste 방식일 때만 `pastedCode`를, 그 외에는 `files`를 포함.

## 변경 파일
- `frontend/src/components/task/CreateTaskModal.tsx` (신규)
- `frontend/src/components/task/CreateTaskModal.test.tsx` (신규, 7개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T081 체크)

## TDD 결과
- RED 커밋: c5fbc6e (test: CreateTaskModal 3 upload methods - RED (T081))
- GREEN 커밋: 91abaf4 (feat: CreateTaskModal 3 upload methods - GREEN (T081))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 7/7 테스트 통과

## 기술 결정
- 업로드 방식 선택 UI는 radix `Tabs` 대신 네이티브 `<input type="radio">` 3개를 사용 — 테스트가 `role="radio"`만 요구하고, 라디오 그룹이 "하나만 선택 가능한 3개 옵션"이라는 의미를 가장 단순하게 표현하기 때문. radix Tabs는 T083(TaskDetail)에서 쓸 예정이라 여기서는 과한 선택.
- 제목 최소 5자 검증은 브리프 지시대로 클라이언트에서도 선제적으로 수행 — 백엔드가 5자 미만을 거부할 것이므로, 불필요한 왕복 요청을 막기 위함.
- `CreateProjectModal`과 달리 업로드 방식을 바꾸면 해당 방식에서 모은 `files`/`pastedCode`를 초기화(`handleUploadMethodChange`) — 방식을 바꿨다가 되돌렸을 때 이전 방식의 잔여 데이터가 실수로 함께 제출되는 것을 방지.

## 비고
- ProjectDetail(T082)에서 "새 태스크" 버튼으로 이 모달을 열고, `createTask` 뮤테이션의 `mutateAsync`를 `onSubmit`에 연결할 예정.
