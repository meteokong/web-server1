# TASK-076. FileUpload 컴포넌트 구현 (드래그앤드롭/파일 선택)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/upload/FileUpload.tsx`에 CreateTaskModal(T081)의 "파일 업로드" 방식에서 쓰일 FileUpload 컴포넌트를 구현했다.
- 드래그앤드롭 영역(`onDrop`/`onDragOver`, 둘 다 `preventDefault`)과 숨겨진 `<input type="file" multiple>`을 버튼 뒤에 배치.
- `onFilesSelected: (files: File[]) => void` prop 하나만 받으며, 드롭된 파일 또는 파일 선택 다이얼로그로 고른 파일을 그대로 부모에게 전달. 업로드/검증 로직은 포함하지 않음(해당 책임은 CreateTaskModal/task-service 쪽).

## 변경 파일
- `frontend/src/components/upload/FileUpload.tsx` (신규)
- `frontend/src/components/upload/FileUpload.test.tsx` (신규, 3개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T076 체크)

## TDD 결과
- RED 커밋: 3ef9a3f (test: FileUpload drag-and-drop/file picker - RED (T076))
- GREEN 커밋: 58c4781 (feat: FileUpload drag-and-drop/file picker - GREEN (T076))
- REFACTOR 커밋: 해당 없음 (GREEN 커밋에 라벨 숨김 스타일 정리 포함)
- 테스트 커버리지: 신규 파일 3/3 테스트 통과

## 기술 결정
- `webkitRelativePath` 등 폴더 전용 속성은 다루지 않음 — 그 책임은 FolderUpload(T077)로 분리.
- 드롭 이벤트 테스트는 jsdom에서 `DragEvent`가 완전히 지원되지 않아 `dispatchEvent`로 직접 `dataTransfer`를 주입하는 방식을 사용.

## 비고
- CreateTaskModal(T081)에서 업로드 방식 탭 중 "파일 업로드" 선택 시 이 컴포넌트를 그대로 사용할 예정.
