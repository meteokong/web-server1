# TASK-036. Login 페이지

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
T033(`LoginForm`)과 T034(`auth-service.login`)를 연결하는 배선 작업으로, T035(Register 페이지)와 성격이 동일합니다.

**구현 내용 (`frontend/src/pages/Login.tsx`)**:
- `LoginForm`의 `onSubmit`에 `auth-service.login(email, password)` 호출을 연결
- `login()`이 성공하면 내부적으로 이미 `useAuthStore.setUser(...)`가 호출되어 있으므로(T034), 페이지는 단순히 대시보드(`/`)로 이동만 처리
- 계정이 없는 사용자를 위한 `/register` 링크 추가
- `App.tsx`의 `/login` placeholder 라우트를 이 페이지로 교체

## 변경 파일
- `frontend/src/pages/Login.tsx` (신규)
- `frontend/src/App.tsx` (placeholder → 실제 페이지로 교체, T035와 공통)

## TDD 결과
- RED/GREEN/REFACTOR 커밋: 해당 없음 (경량 검증, T035와 동일한 사유 — 이미 테스트된 LoginForm/auth-service를 조합만 하는 페이지)
- 커밋: `ad51562` (feat: Register and Login pages (T035, T036)) — T035와 동일 커밋
- 검증: `npm run build`/`lint`/`test`(12개 테스트 유지) 모두 클린

## 기술 결정 (해당 시)
- 로그인 성공 후 이동 대상을 `/`(대시보드)로 고정 — 추후 "원래 가려던 페이지로 되돌아가기(redirect state)"가 필요해지면 T037 ProtectedRoute와 함께 `location.state.from` 패턴으로 확장 가능하지만, 현재 테스트/요구사항 범위에는 없어 추가하지 않음(YAGNI)
- 페이지에서 에러를 다시 잡지 않음 — `LoginForm`이 이미 `onSubmit` reject 시 에러 메시지를 자체적으로 표시하므로, 페이지는 성공 경로(네비게이션)만 책임지면 충분

## 비고
- T037(ProtectedRoute)이 `isAuthenticated=false`일 때 리다이렉트할 대상이 바로 이 페이지(`/login`)
