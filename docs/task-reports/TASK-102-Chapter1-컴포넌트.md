# TASK-102. Chapter1 컴포넌트 (What This Code Does)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/chapters/Chapter1.tsx`에 생성 문서의 1번 챕터("이 코드가 하는 일")를 렌더링하는 컴포넌트를 구현했다.
- props: `content: Chapter1Content`(`{ title, summary }`).
- `<h2>{title}</h2>` + `<p>{summary}</p>`만 렌더링 — 테스트가 요구하는 수준(제목/요약 텍스트가 화면에 보이는지) 이상의 꾸밈은 추가하지 않음.
- 함께 `frontend/src/types/document.ts`를 신설해 7챕터 전체의 도메인 타입(`Chapter1Content`~`Chapter7Content`, `DocumentContent`, `DocumentStatus`, `TaskDocument`)을 미리 정의 — 이후 T101/T103/T104/T106이 같은 타입을 재사용.

## 변경 파일
- `frontend/src/types/document.ts` (신규 — 7챕터 + 문서 상태 타입)
- `frontend/src/components/document/chapters/Chapter1.tsx` (신규)
- `frontend/src/components/document/chapters/Chapter1.test.tsx` (신규, 2개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T102 체크)

## TDD 결과
- RED 커밋: f3ba9c6 (test: Chapter1 title/summary rendering - RED (T102))
- GREEN 커밋: 6fe5541 (feat: add Chapter1 (title + one-sentence summary) component - GREEN (T102))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 2/2 테스트 통과

## 기술 결정
- `document.ts` 타입을 백엔드 계약(`data-model.md`의 LearningDocument, Gemini 7챕터 JSON)에 맞춰 camelCase로 미리 전부 정의해둔 이유: T103/T104/T106이 같은 파일을 import할 때 타입이 깨지지 않게, 그리고 챕터 3/5/6/7(ExplanationPanel의 범용 렌더링 대상)의 필드명도 한 곳에 정리해두기 위함 — Chapter1만 쓰는 타입은 `Chapter1Content` 하나뿐이지만, 전체 설계를 한 번에 잡아두는 게 이후 태스크에서 타입 불일치로 재작업하는 비용보다 작다고 판단.

## 비고
- chapter2/4처럼 배열 필드를 가진 챕터는 전용 컴포넌트(T103/T104)에서 반복 렌더링 처리.
