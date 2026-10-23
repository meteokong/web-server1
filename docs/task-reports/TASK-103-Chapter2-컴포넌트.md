# TASK-103. Chapter2 컴포넌트 (Prerequisites Knowledge)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/chapters/Chapter2.tsx`에 생성 문서의 2번 챕터("선행 지식")를 렌더링하는 컴포넌트를 구현했다.
- props: `content: Chapter2Content`(`{ title, concepts: Chapter2Concept[] }`).
- `concepts` 배열을 `.map()`으로 순회하며 개념마다 카드(`<article>`)를 렌더링: 이름(`<h3>`), 설명, 비유(analogy), 예시(`<pre>`로 코드 느낌 유지), 활용 사례(useCases) 5개 필드 모두 표시.
- `key`는 `concept.name` 사용 — 백엔드가 개념 이름을 중복 없이 생성한다고 가정(최대 5개, data-model.md 기준)한 최소 구현.

## 변경 파일
- `frontend/src/components/document/chapters/Chapter2.tsx` (신규)
- `frontend/src/components/document/chapters/Chapter2.test.tsx` (신규, 3개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T103 체크)

## TDD 결과
- RED 커밋: 30a2a65 (test: Chapter2 concept cards rendering - RED (T103))
- GREEN 커밋: 2b81b37 (feat: add Chapter2 concept cards component - GREEN (T103))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 3/3 테스트 통과

## 기술 결정
- 카드 레이아웃을 CSS 그리드/Tailwind로 꾸미지 않고 시맨틱 `<article>`만 사용 — 테스트가 요구하는 건 "각 개념의 5개 필드가 화면에 보이는지"뿐이라 시각적 스타일링은 Green 단계 범위 밖으로 둠(필요하면 이후 리팩터 단계에서 추가).

## 비고
- 개념 2개 모두(첫 번째뿐 아니라 리스트 전체) 렌더링되는지 별도 테스트로 확인해 `.map()` 누락 같은 실수를 방지.
