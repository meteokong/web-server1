# TASK-027. 인증 의존성 (라우트 보호용)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
API 엔드포인트마다 "이 사람이 로그인했는지"를 일일이 확인하는 코드를 반복해서 쓰지 않도록, FastAPI의 `Depends()`로 끼워 넣을 수 있는 공통 보안 검사관을 만들었습니다. 비유하자면, 건물의 각 방(API 엔드포인트) 입구에 각자 다른 경비원을 세우는 대신, 입구마다 "이 카드(쿠키)를 보여주세요"라고 요구하는 똑같은 검사대 하나를 설치해 공유하는 것입니다.

**`backend/src/api/dependencies.py` 구현 내용**:
- `get_current_user(access_token: Cookie, db: Depends)`: HTTPOnly 쿠키(`access_token`)에서 토큰을 읽어 `TokenService.verify_access_token()`으로 검증 → payload의 `sub`(사용자 ID)로 실제 `User`를 DB에서 조회 → 반환
- 쿠키 자체가 없음 / 토큰이 깨짐 / 만료됨 / refresh 토큰을 access로 잘못 보냄 / 토큰은 유효하지만 가리키는 사용자가 DB에 없음(이미 삭제된 유령 사용자) — 이 **5가지 실패 케이스 모두 동일하게 `UnauthorizedError`(401)**로 처리

**TDD 사이클**:
- 🔴 **RED** (`9a72ee1`): `backend/tests/integration/test_dependencies.py` 작성 (5개 테스트, 실제 FastAPI 앱 + 실제 DB로 전체 체인 검증). 모듈이 없어 전부 실패 확인 후 커밋
- 🟢 **GREEN** (`0561ab0`): `get_current_user` 구현 → **테스트 인프라 자체의 중요한 문제를 발견하고 해결**(아래 참고). 5개 테스트 + 전체 백엔드 스위트 66개 전부 통과 확인 후 커밋
- 🔵 REFACTOR: 별도 커밋 없음 — 인프라 수정이 GREEN에 포함됨

**검증 중 발견한 문제** (이번 Task부터 처음으로 "실제 FastAPI 앱 + 실제 DB"를 함께 테스트하면서 드러남):
`fastapi.testclient.TestClient`는 ASGI 앱을 **별도 스레드의 별도 이벤트 루프**에서 실행합니다. 그런데 asyncpg(PostgreSQL 비동기 드라이버)의 연결은 "그 연결을 만든 이벤트 루프"에 묶여 있어서, `TestClient`로 요청을 보내는 동안 테스트 픽스처가 만든 DB 연결을 사용하면 `RuntimeError: Event loop is closed` 또는 `attached to a different loop` 에러가 간헐적으로 발생함을 실제로 재현했습니다. → **`httpx.AsyncClient` + `httpx.ASGITransport`**로 교체 — 이 방식은 ASGI 앱을 별도 스레드 없이 **테스트와 같은 이벤트 루프 안에서** 직접 호출하므로, 이 문제가 근본적으로 발생하지 않음을 확인함 (5개 테스트 전부 경고 없이 깨끗하게 통과)

## 변경 파일
- `backend/src/api/dependencies.py` (신규)
- `backend/tests/integration/test_dependencies.py` (신규, `httpx.AsyncClient`+`ASGITransport` 기반)
- `backend/tests/conftest.py` (주석 보강: TestClient 대신 ASGITransport를 써야 하는 이유 명시)
- `backend/pyproject.toml` (ruff `B008` 규칙을 ignore 목록에 추가 — FastAPI의 `Depends(...)`를 기본값으로 쓰는 표준 패턴을 오탐으로 잡아내는 문제 해결)

## TDD 결과
- RED 커밋: `9a72ee1`
- GREEN 커밋: `0561ab0`
- REFACTOR 커밋: 해당 없음 (테스트 인프라 수정이 GREEN에 포함됨)

## 기술 결정 (해당 시)
- **`TestClient` 대신 `httpx.AsyncClient` + `ASGITransport`를 이 프로젝트의 "실제 앱 + 실제 DB" 통합 테스트 표준 방식으로 채택** — 향후 T028(인증 API 엔드포인트) 이후의 모든 FastAPI 라우트 통합 테스트에서도 이 패턴을 그대로 따라야 함 (`TestClient`를 쓰면 같은 "Event loop is closed" 문제가 재발할 것)
- 5가지 실패 케이스(쿠키 없음/가짜 토큰/만료/타입 혼동/유령 사용자)를 모두 구분하지 않고 동일한 401로 응답 — T025/T026에서 일관되게 적용한 "정보 노출 최소화" 원칙을 그대로 유지
- `ruff`의 `B008`(함수 호출을 기본값으로 쓰지 말라는 규칙)은 일반적으로 유용하지만 FastAPI의 `Depends()` 패턴과는 근본적으로 상충함 — 개별 라인마다 `# noqa`를 붙이는 대신 프로젝트 설정에서 이 규칙 자체를 끔 (앞으로 모든 라우트 파일에서 반복될 패턴이므로)

## 비고
- 다음 Task(T028: `POST /auth/register` 엔드포인트)부터 실제 HTTP API를 만들기 시작하며, 이번에 정립한 `httpx.AsyncClient`+`ASGITransport` 테스트 패턴을 계속 사용할 예정
- `get_current_user`는 아직 어떤 라우트에도 연결되지 않음 — T029 이후 보호가 필요한 엔드포인트(`GET /auth/me` 등)에서 `Depends(get_current_user)`로 실제 사용될 예정
