# TASK-035. Register 페이지

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
T032(`RegisterForm`)와 T034(`auth-service.register`)를 실제로 연결하는 "배선" 작업입니다. 비유하면, 신청서 양식(RegisterForm)과 창구 담당자(auth-service)는 이미 각자 따로 완성되어 있었고, 이번 작업은 "이 창구에서는 이 양식을 받는다"는 안내판을 세우고 둘을 실제로 연결한 것입니다.

**구현 내용 (`frontend/src/pages/Register.tsx`)**:
- `RegisterForm`의 `onSubmit`에 `auth-service.register(email, password)` 호출을 연결
- 계약서(`auth-api.md`)상 회원가입은 로그인을 시키지 않으므로(쿠키 미설정), 성공 시 `/login`으로 이동(`useNavigate`) — 대시보드(`/`)로 바로 보내지 않음
- 이미 계정이 있는 사용자를 위한 `/login` 링크 추가
- `App.tsx`의 `/register` placeholder 라우트를 이 페이지로 교체

## 변경 파일
- `frontend/src/pages/Register.tsx` (신규)
- `frontend/src/App.tsx` (placeholder → 실제 페이지로 교체)

## TDD 결과
- RED/GREEN/REFACTOR 커밋: 해당 없음 (경량 검증) — tasks.md 가이드에 따라 페이지(T035/T036)는 기존에 TDD로 검증된 컴포넌트(T032)/서비스(T034)를 단순히 조합(wiring)하는 수준이라 별도 RTL 테스트 없이 `npm run build`(tsc 포함) + `npm run lint` + 기존 `npm run test`(12개 전부 유지 통과)로 검증
- 커밋: `ad51562` (feat: Register and Login pages (T035, T036)) — Register/Login 두 페이지를 한 커밋으로 처리 (서로 거의 동일한 배선 작업이라 분리할 의미가 적음)

## 기술 결정 (해당 시)
- **회원가입 성공 후 `/login`으로 이동**: "성공하면 당연히 바로 로그인된 것처럼 보여야 하지 않나?"라고 생각할 수 있지만, 계약서가 명시적으로 "register와 login은 분리된 단계"라고 규정하고 있어 이를 그대로 반영. 쿠키가 실제로 설정되지 않았는데 프론트엔드만 "로그인된 것처럼" 보이면 다음 API 호출에서 401이 발생해 혼란을 야기함
- 페이지 자체는 매우 얇게(thin) 유지 — 폼/서비스가 이미 각자 테스트되어 있으므로, 페이지는 "둘을 연결 + 성공 시 어디로 이동할지"만 책임짐

## 비고
- T037(ProtectedRoute)에서 `/register`, `/login`은 보호 라우트에 포함시키지 않음 — 로그아웃 상태에서도 접근 가능해야 함
