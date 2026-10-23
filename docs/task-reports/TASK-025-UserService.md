# TASK-025. UserService (register, login, logout)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
지금까지 따로따로 만들어둔 부품들(User 모델, bcrypt 해싱, 에러 스키마)을 실제로 엮어서 "회원가입/로그인/로그아웃"이라는 진짜 기능으로 만들었습니다. 비유하자면, 벽돌(모델)과 시멘트(유틸)는 준비됐으니 이제 그걸로 실제 방(서비스 로직)을 쌓은 것입니다.

**`backend/src/services/auth/user_service.py` 구현 내용**:
- `register(email, password)`: 비밀번호 강도 검사(8자 이상 + 영문/숫자 혼합) → 이메일 중복 확인(`ConflictError`) → bcrypt 해싱 → User 생성
- `login(email, password)`: 이메일로 사용자 조회 + 비밀번호 검증, 실패 시 `UnauthorizedError` — **"이메일 없음"과 "비밀번호 틀림"에 동일한 에러·동일한 메시지**를 사용해, 공격자가 어떤 이메일이 가입되어 있는지 알아내는 것(user enumeration)을 막음. 성공 시 `last_login_at` 갱신
- `logout(user_id)`: 해당 사용자의 활성 refresh token을 전부 `revoked=True`로 변경 (모든 기기에서의 로그아웃을 의미)

**TDD 사이클**:
- 🔴 **RED** (`a4fceab`): `backend/tests/integration/test_user_service.py` 작성 (9개 테스트 케이스) + `backend/tests/conftest.py`에 실제 DB를 쓰는 `db_session` 픽스처 추가. 모듈이 없어 전부 실패 확인 후 커밋
- 🟢 **GREEN** (`1866f8b`): `UserService` 구현 → **테스트 과정에서 기존 모델(T023/T024)의 숨은 버그 2가지를 발견하고 함께 수정**(아래 참고). 9개 테스트 전부 통과 + 전체 백엔드 스위트 53개 전부 통과 확인 후 커밋
- 🔵 REFACTOR: 별도 커밋 없음 — 버그 수정이 GREEN에 포함되었고, 추가로 개선할 품질 이슈는 발견되지 않음

**검증 중 발견한 버그 2건** (T023/T024 당시엔 raw SQL로 검증해 드러나지 않았던 문제):
1. **`id` 컬럼 불일치**: `User.id`/`RefreshToken.id`는 DB에 `gen_random_uuid()` 기본값이 있지만, ORM 모델에는 이 기본값이 선언되어 있지 않아, ORM으로 INSERT하면 SQLAlchemy가 `id`를 `NULL`로 보내려다 `FlushError`(NULL identity key)로 즉시 실패함. → `server_default=text("gen_random_uuid()")` 추가로 해결
2. **다른 기본값들도 동일한 문제**: `User.skill_level`/`created_at`/`updated_at`, `RefreshToken.created_at`/`revoked`도 마찬가지로 ORM에는 기본값이 없어, ORM INSERT 시 `NULL`이 그대로 들어가 버림(DB 기본값이 적용되는 게 아니라 **조용히 무시됨**). 특히 `revoked`가 `NULL`로 들어가면, `logout()`의 `WHERE revoked IS false` 조건이 `NULL`을 걸러내지 못해 로그아웃이 전혀 동작하지 않는 실제 버그로 이어짐 — 테스트로 직접 재현한 뒤 두 모델 모두에 누락된 `server_default`를 전부 추가해 해결
3. (부수적) `tests/conftest.py`의 `db_session` 픽스처가 `src/db/session.py`의 전역 `engine` 싱글턴을 재사용하다가, pytest-asyncio가 테스트마다 다른 이벤트 루프를 쓰는 것과 충돌해 "Event loop is closed" 에러가 간헐적으로 발생 → 픽스처가 테스트마다 자체 엔진을 만들고 끝나면 정리하도록 변경해 해결

## 변경 파일
- `backend/src/services/auth/user_service.py` (신규)
- `backend/src/services/__init__.py`, `backend/src/services/auth/__init__.py` (신규)
- `backend/src/models/user.py` (버그 수정: `id`/`skill_level`/`created_at`/`updated_at`에 `server_default` 추가)
- `backend/src/models/refresh_token.py` (버그 수정: `id`/`created_at`/`revoked`에 `server_default` 추가)
- `backend/tests/conftest.py` (신규, `db_session` 픽스처를 테스트별 독립 엔진으로 재작성)
- `backend/tests/integration/test_user_service.py` (신규)

## TDD 결과
- RED 커밋: `a4fceab`
- GREEN 커밋: `1866f8b`
- REFACTOR 커밋: 해당 없음 (버그 수정이 GREEN에 포함됨, 사유 상기 참고)

## 기술 결정 (해당 시)
- 비밀번호 정책을 "8자 이상 + 영문·숫자 혼합"으로 구체화함 — research.md의 "min 8 chars, complexity rules"가 "complexity"를 구체적으로 정의하지 않아, 가장 일반적인 해석(영문+숫자 혼합)을 택함. 더 엄격한 규칙(특수문자 필수 등)이 필요하면 추후 조정 가능
- 로그인 실패 시 "이메일이 없음"과 "비밀번호가 틀림"을 **구분하지 않고 동일하게** 응답 — 이는 data-model.md/research.md에 명시되지 않았지만, OWASP가 권고하는 표준적인 user enumeration 방지 기법이라 적용함
- `logout()`을 "모든 활성 토큰을 폐기"로 구현 — data-model.md에는 "Revoke on logout"이라고만 되어 있어 단일 기기 로그아웃 방식도 가능했지만, UserService 레벨의 "로그아웃"은 통상 모든 세션 종료를 의미한다고 보고 이렇게 결정함 (만약 "현재 기기만 로그아웃"이 필요하면 TokenService(T026)에서 특정 토큰만 폐기하는 별도 메서드를 추가할 수 있음)
- 테스트를 `tests/unit/`이 아닌 `tests/integration/`에 배치 — 실제 DB 제약(유니크, FK)과 bcrypt 해싱이 핵심 검증 대상이라 모킹하지 않고 실제 DB로 검증하는 것이 더 신뢰할 수 있다고 판단함

## 비고
- 발견된 두 가지 버그는 **T023/T024 Task Report의 "실제 DB 검증"이 raw SQL INSERT로 이뤄졌기 때문에 당시엔 드러나지 않았던 맹점**임 — raw SQL INSERT는 컬럼을 생략하면 자연스럽게 DB 기본값이 적용되지만, ORM은 애트리뷰트가 설정되지 않아도 명시적으로 NULL을 보낼 수 있어 이 차이가 숨어있었음. 앞으로 새 모델을 만들 때는 **ORM을 통한 실제 INSERT 테스트**(이번처럼)까지 포함해야 이런 류의 문제를 조기에 발견할 수 있음
- T026(TokenService)에서 이 `UserService`가 반환하는 `User` 객체를 받아 실제 JWT access/refresh 토큰을 발급하는 로직이 이어질 예정
