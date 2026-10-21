# TASK-034. 인증 서비스 (auth-service)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
RegisterForm/LoginForm이 수집한 입력값을 실제 백엔드 API로 보내고, 그 결과를 Zustand 인증 스토어에 반영하는 "담당자" 역할의 `auth-service.ts`를 만들었습니다. 비유하면, T032/T033에서 만든 폼이 "신청서"였다면 이 서비스는 그 신청서를 받아 실제로 은행 시스템(`apiClient`)에 전달하고, 처리 결과를 전자 게시판(`useAuthStore`)에 갱신해주는 창구 담당자입니다.

**구현 내용 (`frontend/src/services/auth-service.ts`)**:
- `register(email, password)`: `POST /auth/register` 호출 후 생성된 사용자를 반환. **스토어를 갱신하지 않음** — 계약서(`auth-api.md`)에 "회원가입은 로그인을 시키지 않는다(쿠키를 설정하지 않음)"고 명시되어 있어, 회원가입과 로그인을 분리된 단계로 유지
- `login(email, password)`: `POST /auth/login` 호출 후 받은 사용자 정보로 `useAuthStore.getState().setUser(...)` 호출 — 로그인 성공 시 앱 전체가 즉시 "로그인됨" 상태를 알게 됨
- `logout()`: `POST /auth/logout` 호출 후 `useAuthStore.getState().clearUser()` 호출
- 백엔드의 `snake_case` 응답(`skill_level` 등)을 프론트엔드 스토어가 쓰는 `camelCase`(`skillLevel`)로 변환하는 `toAuthUser()` 헬퍼 추가

## 변경 파일
- `frontend/src/services/auth-service.ts` (신규)
- `frontend/src/services/auth-service.test.ts` (신규)

## TDD 결과
- RED 커밋: `d2ef52a` (test: auth-service - RED) — `auth-service` 모듈 부재로 import 실패 확인
- GREEN 커밋: `89c8402` (feat: auth-service - GREEN) — 5개 테스트(register 성공 시 스토어 미변경, login 성공 시 스토어 갱신, login 실패 시 스토어 미변경, logout 시 스토어 초기화 등) 통과. `npm run test`(3 files, 12 tests)/`lint`/`build` 모두 클린
- REFACTOR 커밋: 해당 없음 — 세 함수가 이미 각 10줄 내외로 단순하고 중복이 거의 없음(공통된 `toAuthUser` 변환만 추출되어 있음)

## 기술 결정 (해당 시)
- **`apiClient`를 `vi.mock`으로 교체**: 실제 백엔드가 이 작업 시점에 동시에 개발 중이라 호출할 수 없으므로, `./api-client` 모듈 자체를 모킹해 "이 서비스가 어떤 엔드포인트를 어떤 바디로 호출하는지"와 "스토어를 올바르게 갱신하는지"만 검증하는 단위 테스트로 설계
- **Zustand 스토어는 실제 싱글톤을 그대로 사용**: `useAuthStore`를 모킹하지 않고 `useAuthStore.getState()`/`setState()`로 직접 읽고 초기화함 — 모킹하면 "실제로 스토어가 갱신되는지"를 검증할 수 없고, Zustand 스토어는 React 없이도 순수 JS로 조작 가능하므로 실제 동작을 검증하는 쪽을 택함
- `register`가 스토어를 건드리지 않는다는 계약을 테스트로 고정 — 추후 누군가 "회원가입하면 바로 로그인되게 하자"고 임의로 바꾸는 회귀를 막기 위함

## 비고
- `GET /auth/me`, `POST /auth/refresh` 호출은 이 파일에 아직 추가하지 않음 — T038(`useAuth` 훅, 자동 토큰 갱신)에서 추가할 예정이며, 해당 Task Report에서 설계를 설명함
- T035/T036(Register/Login 페이지)에서 이 서비스의 `register`/`login`을 각 폼의 `onSubmit`에 연결할 예정
