# TASK-101. ExplanationPanel 컴포넌트

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/ExplanationPanel.tsx`에 7개 챕터를 탐색하는 네비게이션과 현재 선택된 챕터의 콘텐츠를 보여주는 컴포넌트를 구현했다.
- props: `content: DocumentContent`(7챕터 전체).
- 내부 `useState<ChapterKey>`로 현재 챕터를 관리(기본값 `"chapter1"`). 네비게이션은 `<nav>` 안에 챕터마다 `<button>`을 두고, 버튼 레이블은 해당 챕터의 `title`(백엔드가 생성한 영문 제목, 예: "What This Code Does") 사용. 클릭 시 `aria-current`로 현재 활성 챕터 표시.
- 챕터1/2/4는 기존 전용 컴포넌트(Chapter1/Chapter2/Chapter4, T102~T104)로 위임해 렌더링.
- 챕터3/5/6/7은 tasks.md가 전용 컴포넌트를 요구하지 않아 `renderChapter()` 내부에서 범용 렌더링:
  - 챕터3: `<pre>`로 flowchart 문자열 + `<dl>`로 fileBreakdown(파일명→설명) 맵 순회.
  - 챕터5: steps를 `<ol><li>`로 순서대로.
  - 챕터6: concepts를 카드(`<article>`)로, name/whatItIs/whyItsUsed/whereItsApplied 표시.
  - 챕터7: mistakes를 카드로, wrong/right/why/fix 표시.

## 변경 파일
- `frontend/src/components/document/ExplanationPanel.tsx` (신규)
- `frontend/src/components/document/ExplanationPanel.test.tsx` (신규, 6개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T101 체크)

## TDD 결과
- RED 커밋: 43f628c (test: ExplanationPanel chapter navigation + content switching - RED (T101))
- GREEN 커밋: 9f36bd6 (feat: add ExplanationPanel with chapter nav + generic ch3/5/6/7 rendering - GREEN (T101))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 6/6 테스트 통과, 프론트엔드 전체 재실행 22 파일 98/98 테스트 통과(회귀 없음)

## 기술 결정
- 네비게이션을 radix `Tabs` 대신 평범한 `<button>` 목록 + 로컬 state로 구현 — TaskDetail의 문서/연습/Q&A 탭(바깥 탭)과 안쪽 챕터 네비게이션이 이중 `Tabs.Root`로 중첩되는 걸 피하고(TaskDetail이 이미 radix Tabs를 쓰고 있어 ARIA `role="tablist"` 중첩 문제가 생길 수 있음), 테스트가 요구하는 수준(버튼 클릭으로 콘텐츠 전환)에는 평범한 버튼이면 충분하다고 판단.
- 챕터3/5/6/7의 "합리적인 범용 렌더링"은 브리프가 명시한 대로 전용 컴포넌트 없이 `ExplanationPanel` 내부 `renderChapter()` 함수로 처리 — 제목 + 구조화된 필드 표시 정도로 최소화.

## 비고
- 챕터 전환 시 CodePanel과의 스크롤 동기화는 이 컴포넌트의 책임이 아니라 T105(DocumentViewer)에서 처리.
