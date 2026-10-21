# TASK-012. JWT 토큰 유틸리티 (생성/검증/디코딩)

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
로그인한 사용자를 "이 사람이 맞다"고 확인해주는 신분증(JWT 토큰)을 발급하고 검사하는 기능을 만들었습니다. 비유하자면, 놀이공원의 입장 손목밴드와 비슷합니다 — 짧게 유효한 "오늘 하루용 밴드"(access token, 15분)와 길게 유효한 "연간회원증"(refresh token, 7일)을 따로 만들고, 각각 다른 도장(비밀키)으로 위조를 막습니다.

**`backend/src/utils/jwt.py` 구현 내용**:
- `JWTSettings`: `.env.example`의 `JWT_SECRET_KEY`/`JWT_REFRESH_SECRET`을 읽는 pydantic-settings 클래스. Access/Refresh 토큰은 **서로 다른 비밀키**로 서명함 — 하나가 유출돼도 다른 토큰 종류를 위조할 수 없도록 함 (research.md의 보안 설계와 일치)
- `create_access_token(subject, extra_claims=None)`: 15분짜리 access 토큰 발급 (만료 시간은 설정으로 조절 가능)
- `create_refresh_token(subject)`: 7일짜리 refresh 토큰 발급
- 모든 토큰에 `type` 클레임(`"access"` 또는 `"refresh"`)을 심어, 토큰이 유효하더라도 "엉뚱한 용도로" 쓰이는 것을 막음 (예: refresh 토큰을 access 토큰처럼 사용하는 공격 방지)
- `decode_token(token, expected_type)` / `decode_access_token()` / `decode_refresh_token()`: 서명·만료·타입을 모두 검사하고, PyJWT의 저수준 예외를 감싼 자체 예외(`TokenExpiredError`, `InvalidTokenError`)로 변환해 호출하는 쪽이 PyJWT에 직접 의존하지 않도록 함

**테스트** (`backend/tests/unit/test_jwt.py`, 8개, 모두 통과):
1. access 토큰 발급→디코딩 왕복 정상 동작
2. refresh 토큰 발급→디코딩 왕복 정상 동작
3. access 토큰을 refresh로 디코딩 시도 → 거부됨
4. refresh 토큰을 access로 디코딩 시도 → 거부됨
5. 토큰 끝 문자를 조작(변조)하면 서명 검증에서 거부됨
6. JWT 형식이 아닌 문자열은 거부됨
7. 만료 시간을 0분으로 설정하고 1.1초 대기 후 디코딩 → `TokenExpiredError` 발생 확인
8. 추가 클레임(`extra_claims`)이 토큰에 정상 포함되는지 확인

이와 함께 `backend/pyproject.toml`에 `[tool.pytest.ini_options]`를 추가해 `testpaths`, `asyncio_mode`, `asyncio_default_fixture_loop_scope`를 명시하고 pytest-asyncio의 deprecation 경고를 제거함.

## 변경 파일
- `backend/src/utils/jwt.py` (신규)
- `backend/src/utils/__init__.py` (신규, 패키지 인식용)
- `backend/tests/unit/test_jwt.py` (신규)
- `backend/tests/__init__.py`, `backend/tests/unit/__init__.py` (신규)
- `backend/tests/integration/`, `backend/tests/contract/` 디렉토리 생성 (T001에서 만든 구조 확정, 아직 비어있음)
- `backend/pyproject.toml` (`[tool.pytest.ini_options]` 추가)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 JWT 로직은 보안과 직결된 핵심 로직이라 판단해, 설정 범위를 넘어 실제 pytest 단위 테스트 8개를 작성하고 전부 통과를 확인함(`pytest tests/unit/test_jwt.py` → 8 passed). 향후 T207(백엔드 단위 테스트, 80% 커버리지)에서 재사용 가능.

## 기술 결정 (해당 시)
- Access/Refresh에 서로 다른 시크릿 사용 — research.md "Best Practices: Implement dependency injection... rotate refresh tokens on use"와 일반적인 JWT 보안 권장사항을 따름
- `type` 클레임 추가는 data-model.md/research.md에 명시되지 않은 결정이지만, "refresh 토큰 탈취 시 access 토큰처럼 오용" 공격을 막기 위한 표준적인 방어 기법이라 추가함
- PyJWT의 예외를 그대로 노출하지 않고 자체 예외로 감쌈 — 추후 T026(TokenService), T027(인증 의존성)에서 PyJWT 세부 구현에 의존하지 않고 `except TokenExpiredError`처럼 명확하게 처리할 수 있게 함
- `datetime.now(UTC)` 사용 (Python 3.11+에서 `datetime.UTC` 별칭 사용 가능 — plan.md의 "Python 3.11+" 요구사항과 일치, deprecated된 `datetime.utcnow()` 대신 사용)

## 비고
- 실제 로그인 플로우(T025 UserService, T026 TokenService, T028~T031 인증 엔드포인트)에서 이 유틸리티를 사용할 예정 — 이번 Task는 순수 유틸 함수까지만 범위로 함
- `JWT_SECRET_KEY`/`JWT_REFRESH_SECRET`의 기본값은 "개발용 안전하지 않은" 플레이스홀더로 두었으며, 실제 배포 시 `.env`에서 반드시 `openssl rand -hex 32`로 생성한 값으로 교체해야 함(quickstart.md에 이미 안내되어 있음)
