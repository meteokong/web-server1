# TASK-031. 토큰 재발급 엔드포인트 (POST /auth/refresh)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
Access token은 15분짜리 단기 출입증이라 금방 만료됩니다. 그때마다 사용자에게 다시 로그인하라고 하면 너무 불편하니, "장기 출입증(refresh token, 7일)을 보여주면 단기 출입증을 새로 찍어주는" 재발급 창구를 만드는 작업입니다. 이 창구는 지금까지의 `/me`, `/logout`과 달리 **`Depends(get_current_user)`로 보호되지 않습니다** — access token이 이미 만료된 게 정상적인 호출 상황이기 때문에, access token 검사를 통과해야만 들어올 수 있는 문으로 막아두면 애초에 이 엔드포인트의 존재 이유가 사라집니다. 대신 refresh_token 쿠키를 직접 읽어 `TokenService.rotate_refresh_token()`으로 검증·회전(이미 T026에서 구현된 "한 번 쓴 토큰은 재사용 불가" 로직)하고, 성공하면 새 access/refresh 쿠키 한 쌍을 다시 발급합니다.

**구현 중 발견한 중요한 구조적 문제**: 처음에는 다른 라우트들처럼 실패 시 `raise UnauthorizedError(...)`로 던지고 그 전에 `response.delete_cookie()`를 호출하는 방식으로 짰는데, 테스트에서 실패 응답에 쿠키 삭제 헤더가 전혀 안 붙는 버그를 발견했습니다. 원인은 FastAPI의 동작 방식 자체에 있었습니다 — `Depends()`로 주입받은 `Response` 객체는 **라우트가 정상적으로 값을 반환할 때만** 최종 응답에 쓰이고, 예외가 발생해 전역 예외 핸들러가 새 `JSONResponse`를 만들어버리면 그 `Response` 객체는 통째로 버려집니다. 즉 "예외를 던지면서 동시에 그 쪽에 쿠키를 지운다"는 건 애초에 불가능한 조합이었습니다. 그래서 refresh 라우트만 예외적으로, 실패 시 예외를 던지는 대신 전역 핸들러와 **동일한 JSON 에러 모양**(`ErrorResponse`/`ErrorDetail` 재사용)을 가진 `JSONResponse`를 직접 만들어 쿠키를 지운 뒤 그것을 반환하도록 고쳤습니다.

## 변경 파일
- `backend/src/api/auth.py` (수정) — `refresh` 라우트, `_unauthorized_response_clearing_cookies` 헬퍼 추가; `MessageResponse` 위치 정리(REFACTOR)
- `backend/tests/integration/test_auth_refresh.py` (신규)

## TDD 결과
- RED 커밋: `7271a54`
- GREEN 커밋: `a76bd11`
- REFACTOR 커밋: `ef5f4c6` (스키마 클래스 위치 정리 — 동작 변화 없음)

## 기술 결정 (해당 시)
- **실패 시 raise 대신 직접 JSONResponse를 만들어 return** — 위 "작업 요약"에 적은 버그를 고치기 위한 유일한 방법. 전역 핸들러(`src/api/exceptions.py`의 `app_error_handler`)가 만드는 것과 동일한 `{"error": {"code", "message", "details"}}` 모양을 유지하기 위해 `ErrorResponse`/`ErrorDetail`을 그대로 재사용했고, 예외의 `status_code`/`code`/`message`/`details` 속성을 그대로 읽어서 채웠기 때문에 다른 라우트들이 받는 에러 응답과 모양이 완전히 동일합니다.
- 쿠키 누락/가짜 토큰/이미 회전된 토큰 재사용/유령 사용자(토큰은 유효하나 사용자가 DB에 없음) — 이 4가지를 하나의 `try/except UnauthorizedError` 블록으로 묶어서 처리 — "쿠키가 없으면 401, 토큰이 유효하지 않아도 401, 똑같은 모양으로" 라는 계약서의 지시를 코드 구조로도 그대로 드러냄(케이스별로 다른 코드 경로를 타지 않음).
- 테스트에서 "이미 회전된 토큰 재사용" 케이스를 검증할 때 `httpx.AsyncClient`의 영속 쿠키 저장소(jar) 대신 요청마다 `headers={"Cookie": ...}`를 직접 지정 — 처음에는 `auth_client.cookies.set()`으로 짰다가, 첫 호출 이후 jar에 새 refresh_token이 쌓인 상태에서 "원래 토큰"을 다시 `.set()`해도 테스트가 의도와 다르게 통과해버리는 문제(jar의 쿠키 중복/해석 방식 때문으로 추정)를 발견해, 매 요청에 보낼 쿠키를 명시적으로 고정하는 방식으로 바꿔 신뢰도를 높임.

## 비고
- 이것으로 T028~T031(및 T029A) 5개 Task, 즉 인증 API의 다섯 엔드포인트(`register`/`login`/`me`/`logout`/`refresh`)가 모두 구현 완료되었습니다. `backend/src/api/auth.py` 전체가 하나의 `APIRouter`로 `router.py`의 `api_router`에 `/auth` prefix로 등록되어 있습니다.
- 다음 단계(이 Task 범위 밖)는 프론트엔드에서 이 API들을 실제로 소비하는 인증 UI가 될 것으로 보입니다.
