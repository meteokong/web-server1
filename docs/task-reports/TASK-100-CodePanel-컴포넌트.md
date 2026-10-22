# TASK-100. CodePanel 컴포넌트

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/document/CodePanel.tsx`에 업로드된 코드를 읽기 전용 Monaco Editor로 보여주는 컴포넌트를 구현했다.
- props: `code`(코드 내용), `language`(감지된 언어). `language`가 빈 문자열이면 Monaco의 `"plaintext"`로 폴백.
- `options={{ readOnly: true, minimap: { enabled: false } }}`로 읽기 전용 + 미니맵 비활성화(사이드 패널에서 공간을 아끼기 위함, 테스트 요구사항은 아니지만 2컬럼 레이아웃(T105)을 염두에 둔 최소한의 판단).
- jsdom에는 Monaco가 필요로 하는 canvas/worker 환경이 없어, 테스트에서 `@monaco-editor/react`를 `vi.mock`으로 대체(`value`/`language`/`options.readOnly`를 속성으로 노출하는 `<div data-testid="monaco-editor">`) — 실제 브라우저 렌더링은 이후 "Manual browser test" 태스크의 몫.

## 변경 파일
- `frontend/src/components/document/CodePanel.tsx` (신규)
- `frontend/src/components/document/CodePanel.test.tsx` (신규, 4개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T100 체크)

## TDD 결과
- RED 커밋: c241211 (test: CodePanel read-only Monaco code viewer - RED (T100))
- GREEN 커밋: 561d0ae (feat: add CodePanel read-only Monaco code viewer - GREEN (T100))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 4/4 테스트 통과

## 기술 결정
- 언어 미지정(빈 문자열) 시 `"plaintext"`로 폴백 — 백엔드의 `detected_language`가 비어있는 극단적 케이스에서도 Monaco가 에러 없이 렌더링되게 함.
- 파일이 여러 개인 업로드(folder)의 처리(탭/셀렉터)는 이 컴포넌트의 책임 범위 밖으로 두고, 어떤 파일을 보여줄지 결정하는 것은 호출자(DocumentViewer, T105)의 몫으로 설계 — CodePanel은 "주어진 코드 문자열 하나를 보여준다"는 단일 책임만 가짐.

## 비고
- 실제 여러 파일 중 어떤 걸 보여줄지(첫 파일만 MVP로 보여줄지, 탭으로 전환 가능하게 할지)는 T105(DocumentViewer)에서 결정.
