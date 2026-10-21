# TASK-018. React Router 구조 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
프론트엔드 앱이 URL 주소에 따라 다른 화면을 보여줄 수 있도록 "길 안내판"(라우터)을 설치했습니다. 비유하자면, 지금까지는 건물에 문(`App.tsx`)이 하나뿐이라 어떤 주소로 와도 똑같은 로비(Vite 기본 데모 화면)만 보였는데, 이제 주소별로 다른 방으로 안내하는 표지판 체계를 세운 것입니다. 각 방(실제 페이지 컴포넌트)은 아직 비어있지만(placeholder), 어느 방으로 가야 하는지 길만큼은 정확히 뚫려 있습니다.

**구현 내용**:
- `react-router-dom` 설치 (plan.md/research.md "React Router v6" 결정에 따름 — 단, 아래 "기술 결정" 참고)
- `frontend/src/App.tsx`를 Vite 기본 데모(카운터 버튼 등)에서 실제 라우트 구조로 교체:
  - `/login`, `/register` — 인증 페이지
  - `/` — 대시보드(프로젝트 목록)
  - `/projects/:projectId` — 프로젝트 상세
  - `/projects/:projectId/tasks/:taskId` — 태스크 상세
  - `/trash` — 휴지통
  - `*` — 존재하지 않는 경로는 `/`로 리다이렉트
- plan.md의 "Source Code" 섹션에 명시된 페이지 목록(dashboard, project, task, login, register, trash)과 data-model.md의 User→Project→Task 계층 구조를 그대로 URL 경로에 반영
- 각 페이지는 아직 실제 컴포넌트가 없으므로(T035/T036/T054/T055/T083/T181에서 작성 예정) `PagePlaceholder`라는 임시 컴포넌트로 대체, 어떤 Task에서 실제 페이지로 교체될지 주석으로 명시
- 더 이상 쓰이지 않는 Vite 기본 데모 리소스(`App.css`, `src/assets/`의 `hero.png`/`react.svg`/`vite.svg`) 삭제

**검증**:
1. `npm run build` → TypeScript 컴파일 + Vite 빌드 성공 (타입 에러 없음 — `useParams` 등 라우트 파라미터 타입도 포함)
2. `npm run lint`, `npm run format:check` 모두 통과
3. `npm run dev`로 실제 Vite 개발 서버를 띄워 `curl`로 `GET /` → `200 OK` 확인 (라우터가 렌더링하는 실제 콘텐츠는 클라이언트 사이드 JS 실행 후에 나타나므로 `curl`로는 HTML 셸만 확인 가능 — Vitest/React Testing Library는 아직 별도 Task로 설치되지 않아 이번 범위에는 포함하지 않음)

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (`react-router-dom` 추가)
- `frontend/src/App.tsx` (전체 교체)
- `frontend/src/App.css` (삭제, Vite 데모 전용 스타일)
- `frontend/src/assets/` (삭제, Vite 데모 전용 이미지)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 빌드/린트/개발 서버 기동으로 "라우팅 구조가 깨지지 않았는가"를 검증함.

## 기술 결정 (해당 시)
- **보안 이슈로 인해 v6 대신 v7.18.4를 설치함**: research.md는 "React Router v6"를 명시했으나, `npm install react-router-dom@6`을 실행한 직후 `npm audit`에서 `react-router 6.0.0~7.17.0` 전체 범위에 영향을 미치는 moderate 등급 취약점 2건을 발견함 — (1) `<Link>`/`useNavigate`의 백슬래시를 이용한 Open Redirect, (2) SSR 하이드레이션 중 `deserializeErrors()`를 통한 임의 생성자 injection. **v6 계열에는 패치된 버전이 존재하지 않고**, 수정은 7.18.4부터 적용됨을 `npm view react-router-dom versions`로 확인함. 이 프로젝트는 SSR을 쓰지 않고 선언적 `<Routes>/<Route>` API만 사용하므로 v6→v7 업그레이드는 API 호환성 문제가 없었고, 빌드/타입체크가 정상 통과함을 확인한 뒤 7.18.4로 설치함 (`npm audit` 결과 0 vulnerabilities로 해결)
- Login/Register를 보호되지 않은 라우트로, 나머지(대시보드/프로젝트/태스크/휴지통)는 인증이 필요한 라우트로 분류 — 다만 T037(ProtectedRoute 컴포넌트)이 아직 없어 이번 Task에서는 실제 인증 가드를 걸지 않음
- 플레이스홀더 방식(실제 페이지 대신 임시 컴포넌트)을 택해, 라우팅 구조와 실제 페이지 구현을 분리 — 이후 각 페이지 Task에서 `PagePlaceholder` 호출부만 실제 컴포넌트 import로 교체하면 됨

## 비고
- T037(ProtectedRoute)이 완성되면 대시보드/프로젝트/태스크/휴지통 라우트를 감싸 미인증 사용자를 `/login`으로 리다이렉트해야 함
- 프론트엔드 컴포넌트 테스트(Vitest + Testing Library) 설치는 이번 Task 범위 밖 — 실제 설치 시점은 첫 컴포넌트 테스트가 필요한 Task(T032/T033 등) 또는 T208에서 결정될 것으로 보임
