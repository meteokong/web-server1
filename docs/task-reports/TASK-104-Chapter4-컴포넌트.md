# TASK-104. Chapter4 컴포넌트 (Line-by-Line Explanation)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/chapters/Chapter4.tsx`에 생성 문서의 4번 챕터("줄별 설명")를 렌더링하는 컴포넌트를 구현했다.
- props: `content: Chapter4Content`(`{ title, explanations: Chapter4Explanation[] }`).
- `explanations` 배열을 순회하며 줄마다 블록(`<article>`)을 렌더링: 줄 번호(`data-testid="chapter4-line-number"`로 테스트에서 식별), 코드(`<pre>`), 설명, 비유, 대안 예시(`<pre>`), 참고사항(notes) 6개 필드 모두 표시.
- `key`는 `explanation.line`(줄 번호, 같은 문서 내에서 고유) 사용.

## 변경 파일
- `frontend/src/components/document/chapters/Chapter4.tsx` (신규)
- `frontend/src/components/document/chapters/Chapter4.test.tsx` (신규, 4개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T104 체크)

## TDD 결과
- RED 커밋: 6a70cc7 (test: Chapter4 line-by-line explanations rendering - RED (T104))
- GREEN 커밋: dc756b6 (feat: add Chapter4 line-by-line explanation component - GREEN (T104))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 4/4 테스트 통과

## 기술 결정
- 줄 번호를 검증하는 테스트에서 텍스트 매칭(`getByText(/1/)`)이 아니라 `data-testid="chapter4-line-number"`로 식별 — 코드/설명 텍스트 안에 숫자 "1"이 우연히 섞여 있어도(예: 코드에 `n == 0` 같은 숫자) 테스트가 깨지지 않게 하기 위함.
- 코드와 대안 예시 모두 `<pre>`로 감싸 들여쓰기/줄바꿈이 깨지지 않게 함 — Chapter2의 예시 코드 렌더링 방식과 동일한 컨벤션 유지.

## 비고
- 줄 수가 많아질 때의 가상 스크롤/페이지네이션은 요구되지 않아 구현하지 않음(Green 단계 최소 구현 원칙) — 필요해지면 이후 리팩터링 대상.
