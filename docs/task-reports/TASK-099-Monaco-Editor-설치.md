# TASK-099. Monaco Editor 설치/설정

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/`에 `@monaco-editor/react`(^4.7.0)를 설치했다. 이후 T100(CodePanel)이 이 패키지의 `Editor` 컴포넌트로 읽기 전용 코드 뷰어를 구현할 예정이다.
- 패키지가 Vite/Vitest의 ESM 모듈 그래프에 정상적으로 들어오는지(설치/의존성 해석 문제가 없는지) 확인하는 스모크 테스트만 작성 — 실제 브라우저에서의 Monaco worker 로딩/렌더링 검증은 브리프 지시대로 이후 "Manual browser test" 태스크의 몫으로 남겨둠.
- 테스트는 `Editor`가 `React.memo`로 감싸진 객체로 export되는 것, `loader.init`이 함수로 노출되는 것(이후 CDN 대신 로컬 번들을 쓰도록 `loader.config`로 구성할 때 사용)만 확인.

## 변경 파일
- `frontend/package.json` (수정 — `@monaco-editor/react` 의존성 추가)
- `frontend/package-lock.json` (수정)
- `frontend/src/components/document/monaco-setup.test.ts` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T099 체크)

## TDD 결과
- RED 커밋: 651a685 (test: Monaco Editor package smoke test - RED (T099))
- GREEN 커밋: 6c6e55c (feat: install @monaco-editor/react for the document viewer - GREEN (T099))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 2/2 테스트 통과

## 기술 결정
- **`@monaco-editor/react`를 선택한 이유**: 브리프가 권장한 패키지 그대로 채택. React 19 함수형 컴포넌트로 Monaco를 감싸 `<Editor value={...} language={...} options={{readOnly: true}} />` 형태로 바로 쓸 수 있고, CDN에서 Monaco 코어를 지연 로드하는 `loader`를 함께 제공해 Vite 번들에 Monaco 전체를 직접 끌어오지 않아도 된다(코드 분할에 유리). 대안으로 검토한 `monaco-editor` 저수준 패키지를 직접 ref/useEffect로 마운트하는 방식은 React 라이프사이클 관리(마운트/언마운트, 리사이즈)를 직접 해야 해서 불필요하게 코드가 늘어남.
- RED 단계 검증 방식: 이미 `npm install`로 `node_modules`에 패키지가 설치된 상태라 `package.json`만 되돌려서는 import 자체가 실패하지 않았다(모듈 파일은 그대로 디스크에 있음). 대신 `Editor`의 실제 타입(`object`, `React.memo` 래핑)을 테스트가 틀리게 가정(`function`)하게 작성해 실제로 실패하는 테스트로 RED를 확인한 뒤, GREEN에서 올바른 타입 단언으로 수정하고 `package.json`/`package-lock.json` 변경을 커밋에 포함시켰다.

## 비고
- 다음 태스크(T100, CodePanel)에서 `loader.config`로 Monaco CDN 경로를 번들 내 로컬 경로로 바꿀지 여부를 판단할 것 — 당장은 기본(CDN) 설정으로 충분.
