# TASK-021. Zustand 인증 스토어 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
"지금 로그인한 사람이 누구인지"를 앱 전체의 어느 컴포넌트에서든 바로 알 수 있게 해주는 전역 저장소(Zustand 스토어)를 만들었습니다. 비유하자면, 회사 로비의 전자 게시판 같은 것입니다 — 누가 출근했는지(`user`), 지금 근무 중인지(`isAuthenticated`), 출입 기록을 아직 조회 중인지(`isInitializing`)를 한 곳에 표시해두면, 어느 층(컴포넌트)에서든 게시판만 보면 바로 알 수 있습니다.

**`frontend/src/stores/auth-store.ts` 구현 내용**:
- `AuthUser` 타입: `id`, `email`, `skillLevel` — **민감하지 않은** 사용자 식별 정보만 포함
- `AuthState`: `user`, `isAuthenticated`, `isInitializing` 상태값 + `setUser`/`clearUser`/`finishInitializing` 액션
- `isInitializing`: 앱이 처음 켜졌을 때 "로그인 상태인지 아직 확인 중"을 나타내는 플래그. 이게 없으면 새로고침 직후 잠깐 "로그아웃 상태"로 오인해 `/login`으로 리다이렉트해버릴 수 있음 — T037(ProtectedRoute)에서 이 값을 활용할 예정
- **중요한 설계 결정**: 이 스토어는 JWT 토큰 문자열 자체를 절대 담지 않음. research.md의 인증 설계(access/refresh 토큰을 HTTPOnly 쿠키로 관리)에 따라 토큰은 JS가 아예 접근할 수 없는 쿠키에만 존재하고, 이 스토어는 "로그인 여부와 누구인지"라는 **파생 상태**만 보관함

**검증 (실제 런타임 동작 확인)**:
Zustand 스토어는 React 없이도 `getState()`/`setState()`로 직접 조작 가능한 점을 활용해, TypeScript 파일을 임시로 순수 JS로 변환(`tsc --outDir ... --ignoreConfig`)한 뒤 Node에서 직접 실행하여 실제 상태 전이를 검증함 (10개 assertion 모두 통과):
- 초기 상태: `user=null`, `isAuthenticated=false`, `isInitializing=true`
- `setUser(...)` 호출 → `user`에 전달한 값 반영, `isAuthenticated=true`, `isInitializing=false`로 함께 전환
- `clearUser()` 호출(로그아웃 시뮬레이션) → `user=null`, `isAuthenticated=false`로 복귀
- `finishInitializing()` 단독 호출 → `isInitializing`만 `false`로 바뀌고 `isAuthenticated`는 건드리지 않음 (비로그인 상태로 초기화 완료되는 시나리오)
검증 후 임시 변환 파일/스크립트 삭제.

추가로 `npm run build`(TypeScript 컴파일 포함)/`lint`/`format:check` 모두 통과.

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (`zustand` 추가)
- `frontend/src/stores/auth-store.ts` (신규)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 아직 프론트엔드에 정식 테스트 러너(Vitest)가 설치되지 않아, TypeScript를 임시로 JS로 변환해 Node에서 직접 상태 전이를 실행/검증하는 방식으로 실질적인 동작 검증을 수행함.

## 기술 결정 (해당 시)
- **토큰을 스토어에 저장하지 않음** — JS로 접근 가능한 저장소(Zustand 스토어든 localStorage든)에 JWT를 두면 XSS 공격 시 토큰이 탈취될 수 있음. research.md가 HTTPOnly 쿠키를 택한 이유(XSS로부터 보호)와 일치시키기 위해, 이 스토어는 애초에 토큰을 담을 필드조차 두지 않음
- `isInitializing` 플래그는 data-model.md/research.md에 명시되지 않은 결정이지만, SPA에서 "새로고침 시 로그인 상태 깜빡임(flash of unauthenticated content)"을 막는 일반적인 패턴이라 추가함
- `persist` 미들웨어(localStorage에 상태 저장)는 사용하지 않음 — 실제 인증 진실은 서버의 쿠키에 있으므로, 새로고침 시마다 T038의 `useAuth` 훅이 `GET /auth/me`로 다시 확인하는 것이 로컬 캐시보다 안전하고 일관적임

## 비고
- 이 스토어를 실제로 채우는 로직(`setUser`/`clearUser` 호출)은 T034(auth-service)와 T038(useAuth 훅)에서 작성될 예정
- T037(ProtectedRoute)에서 `isAuthenticated`/`isInitializing`을 읽어 인증 가드를 구현할 예정
- 이로써 Frontend Foundation 섹션(T018~T022) 중 T018~T021이 완료됨, 남은 것은 T022(Tailwind CSS + shadcn/ui 설정)
