# TASK-030. 로그아웃 엔드포인트 (POST /auth/logout)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`/auth/me`가 "검사대를 통과해서 내 정보를 읽어오기"였다면, 이번 `/auth/logout`은 "검사대를 통과해서 출입증 전부를 무효화하기"입니다. 중요한 점은 **지금 로그아웃을 요청한 그 기기의 세션만 끝내는 게 아니라, 이 계정으로 발급된 모든 출입증(여러 기기/브라우저에서 로그인했던 모든 refresh token)을 한꺼번에 무효화**한다는 것입니다 — 이미 T025에서 `UserService.logout()`이 그렇게 구현돼 있고, 이번 Task는 그걸 실제 HTTP 문으로 연결하는 작업입니다. 성공하면 두 쿠키(access_token, refresh_token)를 전부 지우고(`delete_cookie` → `Max-Age=0`으로 재설정) `{"message": "logged out"}`을 돌려줍니다.

## 변경 파일
- `backend/src/api/auth.py` (수정) — `logout` 라우트, `_clear_auth_cookies` 헬퍼, `MessageResponse` 스키마 추가
- `backend/tests/integration/test_auth_logout.py` (신규)

## TDD 결과
- RED 커밋: `a681b23`
- GREEN 커밋: `76577d0`
- REFACTOR 커밋: 해당 없음

## 기술 결정 (해당 시)
- 테스트에서 "모든 세션이 종료됐는지"를 검증하기 위해 같은 사용자에게 **두 번** `issue_tokens()`를 호출해 두 개의 refresh_token 행을 만든 뒤, 로그아웃 요청은 그중 **첫 번째** access_token으로만 보내고, DB를 조회해 **두 행 모두** `revoked=True`인지 확인 — "로그아웃을 요청한 세션만 끝나는 버그"를 잡아낼 수 있도록 의도적으로 설계.
- 쿠키 삭제 검증은 `Max-Age=0`이 실제 `Set-Cookie` 헤더에 박혀 있는지로 확인 — FastAPI의 `response.delete_cookie()`가 내부적으로 쿠키를 빈 값 + `Max-Age=0`으로 재설정하는 방식이기 때문에, 이 특성을 직접 헤더에서 검증.

## 비고
- 다음 Task(T031: `POST /auth/refresh`)는 유일하게 `Depends(get_current_user)`를 쓰지 않는 라우트 — access token이 이미 만료된 상태에서 호출되는 게 정상 시나리오이기 때문에, refresh_token 쿠키를 직접 읽어 처리.
