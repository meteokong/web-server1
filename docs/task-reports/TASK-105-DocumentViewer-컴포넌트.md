# TASK-105. DocumentViewer 컴포넌트 (2컬럼 레이아웃 + 스크롤 동기화)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/DocumentViewer.tsx`에 왼쪽 CodePanel(업로드된 코드) + 오른쪽 ExplanationPanel(생성된 문서)의 2컬럼 레이아웃과, 한쪽을 스크롤하면 다른 쪽도 같은 비율만큼 스크롤되는 동기화를 구현했다.
- props: `code`, `language`(CodePanel로 전달), `content: DocumentContent`(ExplanationPanel로 전달).
- 두 컬럼을 각각 `overflow: auto`인 `<div>`로 감싸고 `onScroll` 핸들러를 달았다. 스크롤 비율 계산: `ratio = sourceEl.scrollTop / (sourceEl.scrollHeight - sourceEl.clientHeight)`, 그 비율을 상대편의 `(scrollHeight - clientHeight)`에 곱해 `targetEl.scrollTop`에 대입 — 줄 단위 매핑이 아니라 "전체 스크롤 가능 범위 중 몇 %"를 맞추는 수준(브리프가 명시한 "과설계하지 말 것" 지침에 맞춤).
- 무한 루프 방지: `targetEl.scrollTop`을 프로그램적으로 바꾸면 그 쪽의 `onScroll`도 다시 발생하는데, 이를 다시 반대쪽으로 동기화하면 핑퐁이 생긴다. `suppressNextScrollOn` ref에 "다음에 무시할 소스"를 기록해뒀다가 그 한 번만 건너뛰는 방식으로 막았다.

## 변경 파일
- `frontend/src/components/document/DocumentViewer.tsx` (신규)
- `frontend/src/components/document/DocumentViewer.test.tsx` (신규, 4개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T105 체크)

## TDD 결과
- RED 커밋: 6e06cfd (test: DocumentViewer 2-column layout + proportional scroll sync - RED (T105))
- GREEN 커밋: d5c7de8 (feat: add DocumentViewer 2-column layout + proportional scroll sync - GREEN (T105))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 4/4 테스트 통과

## 기술 결정
- jsdom은 실제 레이아웃을 계산하지 않아 `scrollHeight`/`clientHeight`가 항상 0이므로, 테스트에서 `Object.defineProperty`로 두 패널 요소에 스크롤 지표(scrollTop/scrollHeight/clientHeight)를 직접 주입한 뒤 `fireEvent.scroll()`로 핸들러를 트리거해 비율 계산 로직만 검증 — 실제 브라우저에서의 매끄러운 스크롤 체감은 "Manual browser test" 태스크의 몫.
- 두 패널 모두 `flex: 1`로 동일 너비 2컬럼 — 반응형/리사이즈 가능한 분할바(resizable split) 같은 추가 기능은 테스트가 요구하지 않아 구현하지 않음.

## 비고
- 로딩/에러/생성중 상태 UI는 다음 태스크(T107)에서 이 컴포넌트에 추가.
