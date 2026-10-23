# TASK-037. ProtectedRoute 래퍼 컴포넌트

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
로그인하지 않은 사람이 대시보드나 프로젝트 페이지에 들어오지 못하게 막는 "출입 게이트"인 `ProtectedRoute`를 만들었습니다. 비유하면 회사 건물 1층의 보안 게이트입니다 — 출입증 조회가 아직 끝나지 않았으면("isInitializing") 일단 아무것도 보여주지 않고 기다리고, 조회가 끝났는데 출입증이 없으면("!isAuthenticated") 로비(`/login`)로 돌려보내고, 출입증이 확인되면("isAuthenticated") 안으로 들여보냅니다(`<Outlet />`).

**구현 내용 (`frontend/src/components/auth/ProtectedRoute.tsx`)**:
- `useAuthStore`에서 `isAuthenticated`, `isInitializing`을 구독
- `isInitializing === true` → `null` 반환 (아직 `GET /auth/me` 응답 전이라 판단을 내릴 수 없음 — 성급하게 `/login`으로 보내면 이미 로그인된 사용자도 새로고침마다 깜빡이며 로그인 페이지로 튕겨나가는 버그가 생김)
- `!isAuthenticated` → `<Navigate to="/login" replace />`
- 그 외 → `<Outlet />` (중첩 라우트 패턴 — 레이아웃 라우트로 사용해 `/`, `/projects/*`, `/trash` 등 여러 보호 라우트를 한 번에 감쌀 수 있음)
- `App.tsx`에서 `<Route element={<ProtectedRoute />}>`로 `/`, `/projects/:projectId`, `/projects/:projectId/tasks/:taskId`, `/trash`를 감쌈. `/login`, `/register`, 그리고 임시 디버그 라우트(`/dev-test`, `/query-test`)는 보호 대상에서 제외

## 변경 파일
- `frontend/src/components/auth/ProtectedRoute.tsx` (신규)
- `frontend/src/components/auth/ProtectedRoute.test.tsx` (신규)
- `frontend/src/App.tsx` (보호 라우트 적용)

## TDD 결과
- RED 커밋: `1d90bba` (test: ProtectedRoute - RED) — 모듈 부재로 import 실패 확인
- GREEN 커밋: `4e76e01` (feat: ProtectedRoute - GREEN) — 3개 테스트(초기화 중 미표시, 비인증 시 /login 리다이렉트, 인증 시 자식 콘텐츠 렌더링) 통과. `MemoryRouter` + 실제 `useAuthStore.setState()`로 세 가지 상태를 직접 시뮬레이션. `npm run test`(4 files, 15 tests)/`lint`/`build` 모두 클린
- REFACTOR 커밋: 해당 없음 — 분기 3개짜리 단순 컴포넌트라 개선 여지가 없음

## 기술 결정 (해당 시)
- **children prop 대신 `<Outlet />` 레이아웃 라우트 패턴 채택**: React Router v7 컨벤션에 따라 `<Route element={<ProtectedRoute />}>`로 여러 자식 라우트를 한 번에 감쌀 수 있어, 보호가 필요한 라우트가 늘어나도(`/projects/*` 하위 라우트 등) `ProtectedRoute`를 각각 감싸는 보일러플레이트 없이 한 곳에서 관리 가능
- **`isInitializing` 중 `null` 반환 (스피너 없음)**: 테스트와 과제 설명 모두 "스피너 또는 아무것도 표시하지 않음"을 허용했고, `GET /auth/me`는 보통 수백 ms 내로 끝나는 호출이라 스피너를 깜빡이는 것보다 빈 화면이 UX상 더 자연스럽다고 판단. 추후 느껴질 정도로 느리면 스피너 추가는 쉬운 확장
- 테스트에서 `useAuthStore`를 모킹하지 않고 실제 싱글톤의 `setState`를 직접 호출 — T034와 동일한 이유(실제 상태 전이를 검증하기 위함)

## 비고
- T038(`useAuth` 훅)이 앱 최상단에서 `GET /auth/me`를 호출하고 `finishInitializing()`을 호출해야, 이 `isInitializing` 플래그가 실제로 `false`로 바뀜 — 이 둘은 반드시 함께 동작해야 하는 짝
