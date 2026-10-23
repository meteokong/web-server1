# TASK-024. RefreshToken SQLAlchemy 모델

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
로그인 상태를 7일 동안 유지해주는 "연간회원증"(refresh token)을 DB에 저장/조회할 수 있게 해주는 ORM 모델을 만들었습니다. 실제 토큰 문자열이 아니라 **SHA-256 해시값**만 저장하므로(data-model.md 설계), DB가 유출되어도 토큰 자체를 역산해 로그인할 수는 없습니다.

**TDD 사이클**:
- 🔴 **RED** (`b186973`): `backend/tests/unit/test_refresh_token_model.py` 작성 — 테이블명, 컬럼, PK/FK/유니크/not-null 제약을 검증하는 테스트 7개. `src.models.refresh_token` 모듈이 없어 전부 실패 확인 후 커밋
- 🟢 **GREEN** (`555daf5`): `backend/src/models/refresh_token.py` 작성 — T009 마이그레이션의 `refresh_tokens` 테이블 컬럼(`id`, `user_id`, `token_hash`, `expires_at`, `created_at`, `revoked`, `revoked_at`)을 매핑, `user_id`는 `users.id`를 참조하는 FK(`ondelete="CASCADE"`). 7개 테스트 전부 통과
- 🔵 **REFACTOR** (`847424f`): T023에서 "관련 모델이 없어 보류"했던 `User` ↔ `RefreshToken` 관계(relationship)를 이제 양쪽에 연결 — `User.refresh_tokens`(`cascade="all, delete-orphan"`), `RefreshToken.user`(`back_populates="refresh_tokens"`). 매퍼 구성이 실제로 성공하는지(`configure_mappers()`), 관계가 양방향으로 탐색 가능한지(`user.refresh_tokens`에 추가하면 `token.user`로도 보이는지) 검증하는 테스트 2개 추가 — 통과 확인 후 커밋

**실제 DB 검증** (단위 테스트를 넘어 라이브 PostgreSQL에 대해):
- `revoked` 컬럼을 지정하지 않고 INSERT → DB `server_default` 값 `false`가 정확히 적용됨을 확인
- 같은 `token_hash`로 두 번째 INSERT 시도 → `IntegrityError`로 정상 거부(유니크 제약 확인)
- **CASCADE 삭제 검증**: 사용자를 가진 refresh_token을 만든 뒤, 해당 사용자를 `DELETE FROM users` → `refresh_tokens`의 해당 행도 함께 삭제됨(count=0)을 확인 — data-model.md의 "Tokens... store hash only... Revoke on logout" 요구사항과 더불어, 사용자 삭제 시 토큰이 고아 상태로 남지 않음을 실제로 증명

전체 백엔드 테스트 스위트 재실행 → **44개 전부 통과**(기존 35개 + 이번 9개). Ruff/Black 통과.

## 변경 파일
- `backend/src/models/refresh_token.py` (신규)
- `backend/tests/unit/test_refresh_token_model.py` (신규)
- `backend/src/models/user.py` (REFACTOR: `refresh_tokens` relationship 추가)
- `backend/tests/unit/test_user_refresh_token_relationship.py` (신규, REFACTOR 검증용)

## TDD 결과
- RED 커밋: `b186973`
- GREEN 커밋: `555daf5`
- REFACTOR 커밋: `847424f` (User↔RefreshToken 관계 연결)

## 기술 결정 (해당 시)
- `token_hash`는 "원본 토큰이 아닌 해시만 저장"이라는 data-model.md 요구사항을 컬럼 주석으로 명시 — 실제 해싱 로직(SHA-256)은 T026(TokenService)에서 구현될 예정이며, 이 모델은 저장소 역할만 담당
- `User.refresh_tokens`에 `cascade="all, delete-orphan"`을 추가 — DB 레벨에는 이미 `ON DELETE CASCADE`가 있지만, ORM 세션에서 `user.refresh_tokens`를 비우거나 User를 세션에서 delete할 때도 Python 레벨에서 일관되게 동작하도록 함(두 레벨이 서로 다르게 동작하면 "DB에서는 지워졌는데 세션 캐시에는 남아있는" 류의 버그가 생길 수 있음)
- 관계를 "존재하는 두 모델이 갖춰진 뒤에" 연결하는 방식을 택함 — T023에서 예고한 대로, 섣불리 미리 걸어두지 않고 안전하게 뒤에 추가함으로써 "클래스를 찾을 수 없음" 매퍼 오류를 원천적으로 피함

## 비고
- `Project` 모델(T043)이 생성되면 `User.projects` 관계도 같은 방식으로 추가될 예정
- 실제 리프레시 토큰 발급/검증/회전(rotate) 로직은 T026(TokenService)에서 구현 — 이번 Task는 저장 모델까지만 범위로 함
- 다음 Task는 **T025(UserService: register, login, logout)**로, 지금까지 만든 User/RefreshToken 모델과 T012(JWT)/T013(bcrypt) 유틸을 실제로 엮는 첫 서비스 로직임
