# TASK-038. 자동 토큰 갱신(auto refresh) 로직

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
이 Task는 두 가지를 합친 것입니다. 비유하면 (1) 건물에 들어올 때 "출입증이 아직 유효한지 미리 한 번 확인해주는 안내 데스크"(`useAuth` 훅, 앱이 처음 켜질 때)와 (2) "엘리베이터를 타려는데 출입증이 만료됐다고 뜨면, 자동으로 한 번 재발급을 시도하고 다시 태그해주는 자동 게이트"(axios 응답 인터셉터, 모든 API 호출에 공통 적용)입니다.

### (1) `frontend/src/hooks/useAuth.ts` — 앱 부팅 시 세션 확인
- `App.tsx` 최상단에서 `useAuth()`를 1회 호출
- `useEffect`(마운트 시 1회) 안에서 `GET /auth/me`(`auth-service.getCurrentUser()`) 호출
  - 성공 → `useAuthStore.setUser(user)` — 쿠키가 아직 유효해 "이미 로그인됨"으로 판명
  - 실패(쿠키 없음/만료, 그리고 아래 (2)의 refresh 시도까지 실패한 경우) → `clearUser()`
  - 어느 쪽이든 마지막에 `finishInitializing()` 호출 — 이게 있어야 T037 `ProtectedRoute`가 "아직 판단 중(null 렌더링)" 상태를 벗어나 실제 리다이렉트/렌더링 결정을 내릴 수 있음
- 언마운트 시 `cancelled` 플래그로 레이스 컨디션(응답이 늦게 와서 이미 사라진 컴포넌트의 상태를 건드리는 것) 방지

### (2) `frontend/src/services/api-client.ts` — 401 발생 시 자동 재발급 + 재시도
기존 응답 인터셉터(에러를 `ApiError`로 변환하는 로직)를 **그대로 유지**하면서, 그 앞단에 refresh-and-retry 로직을 추가했습니다:
- 어떤 요청이든 `401`을 받으면: (a) 그 요청이 `/auth/refresh` 자신이 아니고, (b) 아직 이 요청에서 재시도를 한 적이 없으면(`_retriedAfterRefresh` 플래그로 추적)
- `POST /auth/refresh`를 "정확히 1번만" 호출 (동시에 여러 요청이 401을 받아도 `inFlightRefresh` 변수로 하나의 refresh 호출만 실제로 나가고, 나머지는 그 결과를 기다림 — Promise dedup)
- refresh 성공 → 원래 요청을 그대로 재시도(`apiClient(originalRequest)`), 그 결과를 호출자에게 그대로 돌려줌 (호출자는 토큰이 갱신됐다는 사실조차 몰라도 됨)
- refresh도 실패 → `useAuthStore.getState().clearUser()` 호출 후, 기존 에러 변환 로직으로 흘러가 평소처럼 `ApiError`를 던짐. 이후 `ProtectedRoute`가 다음 렌더링에서 `isAuthenticated=false`를 보고 `/login`으로 보냄

## 변경 파일
- `frontend/src/hooks/useAuth.ts` (신규)
- `frontend/src/services/api-client.ts` (수정 — refresh-and-retry 인터셉터 로직 추가, 기존 `ApiError` 변환 로직은 그대로 유지)
- `frontend/src/services/auth-service.ts` (수정 — `getCurrentUser()` 추가, T034의 register/login/logout은 그대로)
- `frontend/src/App.tsx` (수정 — 최상단에서 `useAuth()` 호출)

## TDD 결과
- RED/GREEN/REFACTOR 커밋: 해당 없음 (경량 검증 — tasks.md 가이드가 명시한 대로, 이 Task는 실제로 동작하는 백엔드 없이는 "401 → refresh → 재시도"라는 실제 HTTP 왕복을 의미 있게 재현하기 어려움. axios 인터셉터 체인을 모킹하는 단위 테스트는 실제 로직보다 모킹 자체의 정확성을 검증하는 쪽에 가까워질 위험이 있어, 이 Task는 과제 설명에 따라 아래 "수동 추론"으로 검증)
- 커밋: `e1a13b2` (feat: useAuth hook + auto token-refresh interceptor (T038))
- 검증: `npm run test`(4 files, 15 tests, 기존 테스트 전부 유지 통과) / `npm run lint` / `npm run build` 모두 클린

### 수동 추론(코드 경로 검증)
- **정상 흐름**: `GET /auth/me` 200 → `setUser` → `finishInitializing` → `ProtectedRoute`가 `isAuthenticated=true`로 자식 렌더링
- **비로그인 상태로 새로고침**: `GET /auth/me` 401 → 인터셉터가 refresh 시도 → refresh도 401(리프레시 쿠키 자체가 없으므로) → `clearUser()` → `useAuth`의 catch 블록에서도 `clearUser()` (중복이지만 상태는 이미 동일하므로 무해) → `finishInitializing()` → `ProtectedRoute`가 `/login`으로 리다이렉트
- **액세스 토큰만 만료, 리프레시 토큰은 유효**(일반적인 "15분 지남" 시나리오): 아무 API 호출(`GET /auth/me` 포함)이 401 → 인터셉터가 `POST /auth/refresh` 1회 호출 → 성공(새 쿠키 2개 설정) → 원래 요청 재시도 → 200 → 호출자는 에러를 보지 못하고 정상 응답만 받음
- **동시 다발 401**(여러 TanStack Query 쿼리가 동시에 만료된 토큰으로 요청): `inFlightRefresh`가 이미 진행 중인 refresh Promise를 공유하므로, `POST /auth/refresh`는 정확히 1번만 나가고 나머지 요청들은 그 완료를 기다렸다가 각자 재시도함 — 리프레시 토큰이 "1회용 로테이션"(`rotate_refresh_token`, T026)이라는 백엔드 설계상, 이 dedup이 없으면 두 번째 refresh 호출이 이미 회전되어 사라진 토큰으로 401을 받아 전체 세션이 불필요하게 날아갈 수 있음 — 이 dedup은 사실상 필수 설계
- **무한 루프 방지**: `_retriedAfterRefresh` 플래그로 "이 요청은 이미 한 번 refresh 후 재시도했다"를 기록해, 재시도한 요청이 또 401을 받아도 다시 refresh를 시도하지 않고 바로 에러로 떨어짐. `isRefreshRequest` 체크로 `/auth/refresh` 자신의 401은 아예 refresh 재귀를 시도하지 않음 (둘 다 없으면 refresh 요청의 401이 또 refresh를 유발하는 무한 루프 위험)

## 기술 결정 (해당 시)
- **api-client.ts를 수정함** — 과제 지시사항에서 명시적으로 허용된 유일한 예외 상황("T038의 refresh-and-retry 로직을 위해 필요하면"). 이 인터셉터는 "모든 API 호출"에 공통으로 걸려야 하므로, 개별 서비스 파일(auth-service.ts)에 둘 수 없고 axios 인스턴스 자체에 둬야 함. 기존 `ApiError` 변환 로직(및 그 동작)은 한 글자도 바꾸지 않고, 그 앞에 refresh 시도를 끼워 넣는 방식으로 설계해 기존 계약을 깨지 않음
- **`useAuthStore`를 `api-client.ts`에서 정적 import**: 처음에는 "순환 의존성을 피하기 위해" 동적 import(`await import(...)`)를 시도했으나, `vite build`가 `INEFFECTIVE_DYNAMIC_IMPORT` 경고를 띄움 — 실제로는 `auth-store.ts`가 `api-client.ts`를 전혀 참조하지 않아 순환이 존재하지 않았으므로, 불필요한 동적 import를 걷어내고 정적 import로 정리함 (불필요한 복잡도 제거)
- **refresh 1회 제한을 "요청 단위" 플래그로 구현**: 전역 플래그(예: "최근 N초 내 refresh 시도했음")보다 `originalRequest._retriedAfterRefresh`처럼 요청별로 추적하는 방식을 택함 — 이렇게 해야 "방금 refresh에 실패한 직후에 들어온 새 요청"도 (지금 refresh가 다시 필요한 상황이라면) 한 번은 재시도할 기회를 얻음. 전역 쿨다운 방식은 정상적인 재로그인 이후에도 불필요하게 refresh를 건너뛸 위험이 있음
- **`getCurrentUser()`는 스토어를 건드리지 않음**: T034의 `register()`와 동일한 패턴 유지 — "API 호출"과 "그 결과를 스토어에 어떻게 반영할지 결정"을 분리해, 호출하는 쪽(`useAuth`)이 맥락에 맞게 처리

## 비고
- 이로써 T032~T038(Phase 3 인증 UI 섹션) 전체 완료. 다음 섹션(T039 이후, 수동 브라우저 테스트 및 그 이후 기능)은 이 Task들이 만든 `auth-service`/`useAuthStore`/`ProtectedRoute`를 그대로 재사용하면 됨
- 백엔드(`POST /auth/refresh`)가 다른 워크트리에서 동시에 구현 중이었기 때문에 실제 왕복 테스트는 불가능했음 — 위 "수동 추론" 절의 네 가지 시나리오가 실제 백엔드 완성 후 수동 브라우저 테스트(T039류 작업)로 재검증되어야 함
