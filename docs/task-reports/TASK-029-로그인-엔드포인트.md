# TASK-029. 로그인 엔드포인트 (POST /auth/login)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
회원가입(T028)은 "계정을 만드는 것"까지만 하고 끝났습니다. 이번 Task는 그 계정으로 실제로 "출입증(토큰)"을 발급받는 창구를 만드는 작업입니다. 건물 비유를 이어가면, 회원가입 접수처 바로 옆에 "출입증 발급 창구"를 추가로 연 것과 같습니다 — 신분증(이메일/비밀번호)을 보여주면, 직원(`UserService.login`)이 신분을 확인하고, 그 다음 다른 직원(`TokenService.issue_tokens`)이 실제 출입증 두 장(access/refresh 쿠키)을 발급해줍니다.

`POST /api/v1/auth/login`은 이메일/비밀번호를 검증(`UserService.login`, 틀리면 401 — 계정이 없는 경우와 비밀번호가 틀린 경우 **동일한 에러 메시지**라 공격자가 "이 이메일이 가입되어 있는지"를 알아낼 수 없음)한 뒤, 성공하면 `TokenService.issue_tokens(user)`로 access/refresh 토큰 쌍을 발급받아 **HTTPOnly 쿠키**로 심어줍니다(JSON 바디에는 토큰이 절대 들어가지 않음). 쿠키 플래그는 계약서대로 `httponly=True`, `samesite="strict"`, `secure`는 `ENVIRONMENT=development`가 아닐 때만 True.

## 변경 파일
- `backend/src/api/auth.py` (수정) — `login` 라우트 추가, 쿠키 설정 헬퍼(`_cookie_flags`, `_set_auth_cookies`) 신규
- `backend/tests/integration/test_auth_login.py` (신규)

## TDD 결과
- RED 커밋: `47c3630`
- GREEN 커밋: `6bee709`
- REFACTOR 커밋: 해당 없음 — 쿠키 설정 헬퍼를 처음부터 함수로 분리해 작성했고, 더 줄일 중복이 없었음

## 기술 결정 (해당 시)
- **쿠키 플래그를 `_cookie_flags()` 헬퍼로 분리** — T031(refresh)에서도 access/refresh 쿠키를 동일한 플래그로 다시 설정해야 하므로, login에서부터 재사용 가능한 형태로 만들어 둠. `max_age`는 `JWTSettings`(분/일 단위)를 초 단위로 환산해서 전달.
- 쿠키 검증 테스트는 `response.cookies`(쿠키가 "설정되었는지")와 `response.headers.get_list("set-cookie")`(실제 `Set-Cookie` 헤더에 `HttpOnly`/`SameSite=strict` 플래그가 박혀 있는지)를 둘 다 확인 — httpx의 `response.cookies`만으로는 `HttpOnly`/`SameSite` 플래그 자체를 검증할 수 없기 때문에, 원본 헤더 문자열을 직접 들여다봄.
- "계정 없음"과 "비밀번호 틀림"에 대해 동일한 401 메시지인지까지 API 레벨에서 다시 검증 — `UserService.login`이 이미 보장하는 속성이지만, 라우트 레벨에서 메시지가 그대로 전달되는지(가령 라우트에서 실수로 에러를 가로채 다른 메시지로 바꿔버리는 등의 버그)까지 한 번 더 확인하는 의미.

## 비고
- 다음 Task(T029A: `GET /auth/me`)는 쿠키가 아니라 `Depends(get_current_user)`로 보호되는 첫 auth 라우트 — T027에서 만든 의존성이 실제로 라우트에 연결됨.
