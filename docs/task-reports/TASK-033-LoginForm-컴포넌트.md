# TASK-033. LoginForm 컴포넌트

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
로그인 화면의 입력 창구인 `LoginForm` 컴포넌트를 만들었습니다. T032의 `RegisterForm`과 설계 철학이 동일합니다 — 은행 창구 신청서가 "계좌 개설 신청서"든 "출금 신청서"든 양식 자체는 입력을 받아 담당자에게 넘기기만 하는 것처럼, 이 폼도 이메일/비밀번호를 모아 `onSubmit` prop으로 넘기기만 하고 실제 `POST /auth/login` 호출은 전혀 알지 못합니다. API 연결은 T034(auth-service)와 T036(Login 페이지)이 담당합니다.

**구현 내용 (`frontend/src/components/auth/LoginForm.tsx`)**:
- 이메일/비밀번호 입력 필드, `label htmlFor` 연결로 접근성 확보
- 제출 시 `onSubmit({email, password})` 호출
- `onSubmit`이 reject되면 에러 메시지를 `role="alert"`로 표시 (계약서상 로그인 실패는 "이메일 또는 비밀번호가 올바르지 않습니다" 같은 동일 메시지를 이메일/비밀번호 구분 없이 반환하므로, 폼은 그 메시지를 그대로 보여주기만 하면 됨)
- 제출 중 버튼 비활성화로 중복 제출 방지

RegisterForm과 거의 동일한 구조이지만 일부러 공유 컴포넌트로 추출하지 않았습니다 — 현재 두 폼의 필드 구성이 우연히 같을 뿐(회원가입에 비밀번호 확인 등이 추가될 수 있음) 의미적으로는 다른 폼이고, 테스트가 공유 추출을 요구하지 않았습니다 (YAGNI).

## 변경 파일
- `frontend/src/components/auth/LoginForm.tsx` (신규)
- `frontend/src/components/auth/LoginForm.test.tsx` (신규)

## TDD 결과
- RED 커밋: `d9cc4ed` (test: LoginForm - RED) — `LoginForm` 모듈 부재로 import 실패 확인
- GREEN 커밋: `ff47026` (feat: LoginForm - GREEN) — 4개 테스트(필드/버튼 렌더링, onSubmit 호출, 에러 표시, 제출 중 비활성화) 통과. `npm run test`(2 files, 8 tests 통과)/`lint`/`build` 모두 클린
- REFACTOR 커밋: 해당 없음 — RegisterForm과 구조를 의도적으로 통일했을 뿐 추가로 줄일 중복이 없음 (위 "공유 추출 보류" 결정 참고)

## 기술 결정 (해당 시)
- RegisterForm과 동일하게 "바보 컴포넌트" 패턴 유지 — API 계층과의 결합을 페이지(T036)로 미룸
- 로그인 실패 메시지를 폼이 가공하지 않고 그대로 노출 — 보안상 "이메일이 존재하지 않음"과 "비밀번호가 틀림"을 구분하지 않는 계약(`auth-api.md`의 401 UnauthorizedError, "same message for both")을 프론트엔드가 다시 분기하지 않도록 함

## 비고
- T034(auth-service) 완료 후 T036(Login 페이지)에서 `login()` 서비스 함수를 이 폼에 연결할 예정
