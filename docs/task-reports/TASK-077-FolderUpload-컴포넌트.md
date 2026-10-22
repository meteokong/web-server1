# TASK-077. FolderUpload 컴포넌트 구현 (폴더 구조 유지)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/upload/FolderUpload.tsx`에 FileUpload(T076)와 동일한 형태로, 폴더 전체를 선택할 수 있는 컴포넌트를 구현했다.
- `<input type="file">`에 TS가 JSX prop으로 타이핑하지 않는 `webkitdirectory`/`directory` 속성을 `useEffect` + ref로 직접 설정.
- `onFilesSelected: ({ file, relativePath }[]) => void` — 각 파일의 `webkitRelativePath`(예: `myproject/sub/b.py`)를 보존해서 전달, 없으면 `file.name`으로 폴백.

## 변경 파일
- `frontend/src/components/upload/FolderUpload.tsx` (신규)
- `frontend/src/components/upload/FolderUpload.test.tsx` (신규, 2개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T077 체크)

## TDD 결과
- RED 커밋: 2c22cda (test: FolderUpload component preserving relativePath - RED (T077))
- GREEN 커밋: 958171b (feat: FolderUpload component preserving relativePath - GREEN (T077))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 2/2 테스트 통과

## 기술 결정
- `webkitdirectory`/`directory`는 표준 HTML 속성이 아니라 React의 `ComponentProps<"input">` 타입에 없으므로, JSX 속성 대신 `inputRef.current.setAttribute(...)`로 직접 DOM에 설정 — 브리프에서 지시한 방식.
- 테스트에서는 `Object.defineProperty`로 `files`와 `webkitRelativePath`를 모킹 — jsdom이 실제 폴더 선택 다이얼로그를 지원하지 않기 때문.

## 비고
- FileUpload(T076)와 거의 동일한 구조라 추후 공통 Dropzone 로직을 추출할 수 있으나, 현재 테스트가 요구하는 범위에서는 중복을 감수 — 과도한 추상화를 피함(TDD Green 단계 원칙).
