# TASK-078. PasteCode 컴포넌트 구현 (텍스트 영역 + 언어 선택)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/upload/PasteCode.tsx`에 CreateTaskModal(T081)의 "코드 붙여넣기" 방식에서 쓰일 컴포넌트를 구현했다.
- `<textarea>`(코드)와 `<select>`(언어) — 언어 옵션은 백엔드 `language_detector.EXTENSION_TO_LANGUAGE`가 지원하는 값(python/javascript/typescript/java/cpp/c/html/css/text/markdown)과 정확히 일치.
- `onChange: ({ code, language }) => void` — 코드나 언어 중 하나가 바뀔 때마다 최신 조합 전체를 전달. 컴포넌트는 로컬 상태만 가지고, 제출 시점의 값은 부모(CreateTaskModal)가 들고 있음.

## 변경 파일
- `frontend/src/components/upload/PasteCode.tsx` (신규)
- `frontend/src/components/upload/PasteCode.test.tsx` (신규, 3개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T078 체크)

## TDD 결과
- RED 커밋: 7230a38 (test: PasteCode textarea + language selector - RED (T078))
- GREEN 커밋: 1642690 (feat: PasteCode textarea + language selector - GREEN (T078))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 3/3 테스트 통과

## 기술 결정
- 언어 옵션 목록은 `backend/src/services/code_analysis/language_detector.py`의 `EXTENSION_TO_LANGUAGE` 값들을 그대로 가져와, 백엔드가 인식하는 언어와 프론트 선택지가 어긋나지 않도록 함.
- 기본 선택 언어는 목록의 첫 값인 "python"으로 고정 — 별도 "선택 안 함" 옵션은 테스트가 요구하지 않아 추가하지 않음.

## 비고
- CreateTaskModal(T081)에서 업로드 방식 탭 중 "코드 붙여넣기" 선택 시 이 컴포넌트를 그대로 사용할 예정.
