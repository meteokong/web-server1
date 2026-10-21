# TASK-026. TokenService (create/verify/rotate)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
T012에서 만든 "출입증 발급기"(JWT 유틸)와 T024의 "출입 기록부"(refresh_tokens 테이블)를 실제로 연결하는 서비스를 만들었습니다. 비유하자면, 손목밴드(JWT) 자체는 이미 만들 수 있었지만, 이번에 "누가 어떤 밴드를 받았는지 기록하고, 밴드를 새로 바꿔줄 때 예전 밴드를 확실히 무효화하는" 관리 체계를 세운 것입니다.

**`backend/src/services/auth/token_service.py` 구현 내용**:
- `issue_tokens(user)`: access + refresh 토큰 한 쌍을 발급하고, **refresh 토큰의 SHA-256 해시만** `refresh_tokens` 테이블에 저장 (원본 토큰 문자열은 저장하지 않음 — data-model.md 요구사항)
- `verify_access_token(access_token)`: access 토큰을 검증하고 payload 반환, 실패 시 PyJWT의 저수준 예외 대신 `UnauthorizedError`로 통일
- `rotate_refresh_token(refresh_token)`: refresh 토큰을 검증 → DB에서 해당 해시 조회 → **이미 폐기된 토큰이면 거부** → 이번 토큰을 폐기(`revoked=True`) → 새 access+refresh 쌍 발급 (research.md "Rotate refresh tokens on use" 요구사항)

**TDD 사이클**:
- 🔴 **RED** (`8c19e2d`): `backend/tests/integration/test_token_service.py` 작성 (8개 테스트: 발급 시 해시만 저장되는지, access 토큰 검증, refresh를 access로 쓰면 거부되는지, 회전 시 새 쌍 발급과 기존 토큰 폐기, **회전된 토큰 재사용 거부**, 가짜 토큰/발급 기록 없는 토큰 거부). 모듈이 없어 전부 실패 확인 후 커밋
- 🟢 **GREEN** (`ff16d3c`): `TokenService` 구현 → 테스트 과정에서 **JWT 자체의 숨은 버그**를 발견하고 함께 수정(아래 참고). 8개 테스트 + 전체 백엔드 스위트 61개 전부 통과 확인 후 커밋
- 🔵 REFACTOR: 별도 커밋 없음 — 버그 수정이 GREEN에 포함됨

**검증 중 발견한 버그 2건**:
1. **JWT에 `jti`(고유 식별자) 클레임이 없었음**: 같은 사용자에게 같은 초(秒) 안에 토큰을 두 번 발급하면(`iat`/`exp`가 정수 초 단위라 구분이 안 됨), **완전히 동일한 토큰 문자열**이 만들어짐. refresh 토큰은 해시값에 UNIQUE 제약이 걸려있어, "발급 직후 바로 회전"하는 테스트에서 `UniqueViolationError`로 실패함을 실제로 재현 → `src/utils/jwt.py`(T012)에 모든 토큰에 `jti: uuid4()` 클레임을 추가해 해결. 이는 비단 회전 시나리오뿐 아니라, 같은 초 안에 로그인 두 번 하는 등 일반적인 상황에서도 실제로 발생할 수 있었던 문제임
2. **(부수적, 테스트 품질)** 기존 `test_tampered_token_is_rejected`(T012) 테스트가 "토큰 마지막 글자를 뒤집기" 방식으로 변조를 테스트했는데, jti 추가로 서명 바이트가 바뀌면서 **base64url 인코딩의 경계 특성**(32바이트 HMAC 서명을 인코딩한 마지막 문자는 유효 비트가 2개뿐이라, 특정 조합으로 바꿔도 디코딩된 실제 서명 바이트가 동일할 수 있음)에 우연히 걸려 테스트가 실패함 — 실제 보안 취약점이 아니라 테스트의 변조 방식이 결정론적이지 않았던 것임을 직접 재현해 확인. payload 영역을 변조하는 방식으로 테스트를 수정해 해결

## 변경 파일
- `backend/src/services/auth/token_service.py` (신규)
- `backend/src/utils/jwt.py` (버그 수정: 모든 토큰에 `jti` 클레임 추가)
- `backend/tests/unit/test_jwt.py` (변조 테스트를 payload 영역 변조 방식으로 수정)
- `backend/tests/integration/test_token_service.py` (신규)

## TDD 결과
- RED 커밋: `8c19e2d`
- GREEN 커밋: `ff16d3c`
- REFACTOR 커밋: 해당 없음 (버그 수정이 GREEN에 포함됨)

## 기술 결정 (해당 시)
- refresh 토큰 자체를 JWT로 만들되(만료 시각을 자체적으로 검증 가능), **DB에도 해시를 저장**하는 이중 구조를 택함 — JWT만으로는 "이미 회전된 토큰"을 거부할 방법이 없음(서명과 만료 시각만으로는 유효해 보이므로). DB 조회를 추가해야 "탈취된 refresh 토큰이 정상적으로 회전된 후에도 계속 쓰일 수 있는" 보안 문제를 막을 수 있음(research.md "Rotate refresh tokens on use")
- `rotate_refresh_token`은 "이미 폐기된 토큰"과 "존재하지 않는 토큰"을 구분하지 않고 동일한 `UnauthorizedError`로 응답 — T025의 로그인 실패 처리와 같은 원칙(정보 노출 최소화)을 일관되게 적용
- `jti` 추가는 data-model.md/research.md에 명시되지 않았지만, JWT 표준(RFC 7519)의 권장 클레임이자 이번에 실제로 재현된 버그의 직접적인 해결책이라 적용함

## 비고
- `issue_tokens`를 호출하려면 `user.id`가 이미 채워져 있어야 함(즉 `register()`나 DB 조회로 가져온 User) — 이는 T025의 `UserService.register()`/`login()`이 반환하는 User와 자연스럽게 연결됨
- 다음 Task는 **T027(인증 의존성: 라우트 보호용 FastAPI dependency)** — `verify_access_token`을 실제 API 라우트에서 쓰기 위한 FastAPI `Depends()` 래퍼가 필요함
