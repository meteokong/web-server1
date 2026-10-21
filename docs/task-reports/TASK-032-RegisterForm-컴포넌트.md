# TASK-032. RegisterForm 컴포넌트

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
회원가입 화면에서 사용자가 이메일/비밀번호를 입력하고 제출하는 "입력 창구" 역할을 하는 `RegisterForm` 컴포넌트를 만들었습니다. 비유하자면 은행 창구의 신청서 양식 같은 것입니다 — 양식 자체는 "이 계좌를 실제로 개설할 수 있는지"는 모르고, 그냥 손님이 적은 내용을 받아서 담당자(페이지/서비스 계층)에게 넘겨주는 역할만 합니다. 이 컴포넌트도 마찬가지로 백엔드 API를 전혀 알지 못하고, `onSubmit` prop(약속된 콜백)에 `{email, password}`를 넘기기만 합니다. 실제 API 호출은 T034(auth-service)와 T035(Register 페이지)가 담당합니다.

**구현 내용 (`frontend/src/components/auth/RegisterForm.tsx`)**:
- 이메일 입력(`type="email"`), 비밀번호 입력(`type="password"`) — 둘 다 `<label htmlFor>`로 연결되어 접근성(스크린 리더) 확보
- 제출 시 `onSubmit({email, password})` 호출, 성공하면 끝 — 리다이렉트 등은 페이지 책임
- `onSubmit`이 reject되면 `err.message`를 `role="alert"`로 화면에 표시 (중복 이메일 등 서버 에러 메시지를 그대로 보여줄 수 있도록)
- 제출 처리 중(`isSubmitting`)에는 버튼을 비활성화해 중복 제출 방지
- shadcn/ui의 `Button`, `Input`을 그대로 사용 (요구사항: ui 컴포넌트 재구현 금지)

## 변경 파일
- `frontend/src/components/auth/RegisterForm.tsx` (신규)
- `frontend/src/components/auth/RegisterForm.test.tsx` (신규)

## TDD 결과
- RED 커밋: `e3c6c34` (test: RegisterForm - RED) — `RegisterForm` 모듈이 존재하지 않아 import 단계에서 실패하는 것을 확인
- GREEN 커밋: `f844105` (feat: RegisterForm - GREEN) — 4개 테스트(필드/버튼 렌더링, onSubmit 호출, 에러 메시지 표시, 제출 중 버튼 비활성화) 모두 통과. `npm run test`/`lint`/`build` 모두 클린
- REFACTOR 커밋: 해당 없음 — 최소 구현이 이미 단순하여 추가로 개선할 여지가 없었음

## 기술 결정 (해당 시)
- **폼이 API를 모르게 설계**: `onSubmit` prop을 받는 "바보(dumb) 컴포넌트"로 만들어, 백엔드 호출 로직(T034)이나 라우팅/리다이렉트 로직(T035)과 결합되지 않도록 함. 이렇게 하면 이 컴포넌트만 독립적으로 테스트할 수 있고, 추후 LoginForm과도 패턴을 통일할 수 있음
- **에러 표시는 `Error.message`를 그대로 사용**: `api-client.ts`의 `ApiError`도 `Error`를 상속하므로, 페이지 계층에서 `ApiError`를 던지든 일반 `Error`를 던지든 이 폼은 동일하게 처리 가능
- 비밀번호 확인(confirm password) 필드는 추가하지 않음 — 계약서(`auth-api.md`)의 register 요청 바디가 `{email, password}`뿐이고, 테스트에서도 요구하지 않아 "테스트가 요구하는 것만 구현" 원칙에 따라 생략

## 비고
- `useId()`를 사용해 label-input 연결용 id를 자동 생성 (여러 인스턴스가 동시에 렌더링되어도 id 충돌 없음)
- T034 완료 후 T035(Register 페이지)에서 이 컴포넌트에 실제 `register()` 서비스 함수를 연결할 예정
