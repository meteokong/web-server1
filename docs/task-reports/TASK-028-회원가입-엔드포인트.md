# TASK-028. 회원가입 엔드포인트 (POST /auth/register)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
지금까지 `UserService`는 내부 로직으로만 존재했고, 외부(프론트엔드/클라이언트)에서 실제로 호출할 수 있는 문을 달아주는 작업입니다. 비유하자면, T025에서 "회원가입을 처리하는 직원"을 이미 고용해 뒀는데, 이번 Task는 그 직원이 앉아 있는 사무실 앞에 "회원가입 접수처" 간판과 출입문(HTTP 엔드포인트)을 다는 작업입니다.

`POST /api/v1/auth/register`는 요청 본문(`email`, `password`)을 받아 `UserService.register()`를 호출하고, 성공하면 `201 Created`와 함께 `UserResponse`(비밀번호 해시는 절대 노출하지 않음)를 반환합니다. 계약서(`contracts/auth-api.md`)에 명시된 대로, 회원가입은 **로그인까지 자동으로 처리하지 않습니다** — 쿠키를 전혀 설정하지 않습니다. 약한 비밀번호(`ValidationAppError` → 400)나 중복 이메일(`ConflictError` → 409)은 라우트 핸들러가 직접 처리하지 않고, 이미 구축된 전역 예외 핸들러(`src/api/exceptions.py`)가 그대로 처리하도록 그냥 흘려보냅니다(let it propagate).

## 변경 파일
- `backend/src/api/auth.py` (신규) — `register` 라우트, `AuthRequest`/`UserResponse` 스키마
- `backend/src/api/router.py` (수정) — `auth_router`를 `/auth` prefix로 `api_router`에 등록
- `backend/tests/integration/conftest.py` (신규) — `auth_client` fixture: 실제 `src.main.app`을 `httpx.AsyncClient` + `httpx.ASGITransport`로 구동하고, `get_db`를 테스트의 `db_session`으로 오버라이드 (T028~T031 모든 auth API 테스트가 공유)
- `backend/tests/integration/test_auth_register.py` (신규)

## TDD 결과
- RED 커밋: `1e2bcec`
- GREEN 커밋: `e9156f3`
- REFACTOR 커밋: 해당 없음 — 구현이 이미 최소 형태라 더 줄일 코드가 없었음

## 기술 결정 (해당 시)
- **실제 앱(`src.main.app`)을 직접 띄워서 테스트** — T027까지는 테스트 전용 미니 FastAPI 앱을 만들어 썼지만, 이번부터는 라우터 등록(`router.py`) 자체도 검증 대상이므로 `src.main.app`을 그대로 사용. `get_db`만 `app.dependency_overrides`로 테스트의 `db_session`으로 바꿔 끼우고, 테스트가 끝나면 `pop`으로 원복해서 다른 테스트(TestClient 기반 `test_main.py` 등)에 영향이 새지 않도록 함.
- `UserResponse`에 `model_config = {"from_attributes": True}`를 설정해 SQLAlchemy `User` ORM 객체를 그대로 반환값으로 써도 Pydantic이 속성 접근으로 직렬화하도록 함 — 서비스가 돌려주는 `User`를 또 dict로 변환하는 불필요한 매핑 코드를 안 만들어도 됨.
- 라우터 파일(`auth.py`)은 이후 T029~T031에서 로그인/me/로그아웃/refresh 라우트가 같은 파일에 추가될 것을 감안해 구조를 설계했지만, 이번 Task 범위는 `/register` 하나만 — 아직 작성되지 않은 테스트가 없는 코드를 미리 넣지 않기 위해 다른 라우트는 다음 Task들에서 각자의 RED 테스트 이후에 추가함.

## 비고
- 다음 Task(T029: `POST /auth/login`)부터 `TokenService.issue_tokens()`와 쿠키 설정(`access_token`/`refresh_token`, httponly/samesite=strict/secure)이 실제로 쓰이기 시작함.
- `tests/integration/conftest.py`의 `auth_client` fixture는 T029~T031에서도 그대로 재사용.
