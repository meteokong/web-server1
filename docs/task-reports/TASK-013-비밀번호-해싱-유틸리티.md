# TASK-013. 비밀번호 해싱 유틸리티 (bcrypt)

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
사용자 비밀번호를 데이터베이스에 그대로 저장하지 않고, 안전하게 "섞어서" 저장·확인하는 기능을 만들었습니다. 비유하자면, 비밀번호를 금고에 그대로 넣는 대신 믹서기로 완전히 갈아버린 뒤(해싱), 나중에 비밀번호를 다시 입력받으면 똑같이 갈아서 "갈린 모양"이 일치하는지만 비교하는 방식입니다 — 원래 비밀번호는 저장된 적도, 복원될 수도 없습니다.

**`backend/src/utils/security.py` 구현 내용**:
- `hash_password(plain_password)`: bcrypt로 비밀번호를 해싱 (cost factor 12 — research.md에서 결정한 값, 매 해싱마다 랜덤 salt가 들어가 같은 비밀번호도 매번 다른 결과가 나옴)
- `verify_password(plain_password, password_hash)`: 입력한 비밀번호가 저장된 해시와 일치하는지 확인
- `PasswordTooLongError`: bcrypt는 72바이트(UTF-8 인코딩 기준)를 넘는 입력은 **조용히 잘라서** 처리하는 특성이 있어, 이를 모르고 쓰면 "앞부분만 같으면 통과되는" 보안 구멍이 생길 수 있음 → 72바이트 초과 시 해싱 단계에서 명시적으로 예외를 던지고, 검증 단계에서는 (해시를 만들 수 없는 입력이므로) 조용히 `False`를 반환하도록 함

**테스트** (`backend/tests/unit/test_security.py`, 7개, 모두 통과):
1. 해싱→검증 왕복 정상 동작
2. 틀린 비밀번호는 거부됨
3. 해시 결과가 원문과 절대 같지 않음
4. 같은 비밀번호라도 매번 다른 해시가 생성됨(랜덤 salt) — 그리고 둘 다 원래 비밀번호로 검증 가능
5. 해시 문자열에서 cost factor를 파싱해 실제로 12가 쓰였는지 확인
6. 73바이트짜리 비밀번호는 해싱 시 `PasswordTooLongError` 발생
7. 73바이트짜리 비밀번호는 검증 시 (잘려서 통과되는 게 아니라) `False` 반환됨을 확인

전체 테스트 스위트(`pytest`) 재실행 → T012(JWT, 8개) + T013(보안, 7개) = 15개 전부 통과. Ruff/Black도 통과.

## 변경 파일
- `backend/src/utils/security.py` (신규)
- `backend/tests/unit/test_security.py` (신규)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 T012와 동일하게, 비밀번호 보안은 핵심 로직이라 판단해 실제 pytest 단위 테스트 7개를 작성하고 전부 통과를 확인함.

## 기술 결정 (해당 시)
- cost factor 12는 research.md "Password hashing: bcrypt (cost factor 12)" 결정을 그대로 반영
- bcrypt의 72바이트 제한은 data-model.md/research.md에 명시되지 않았지만, bcrypt 라이브러리 자체의 잘 알려진 함정(긴 비밀번호를 조용히 잘라서 처리)이라 이번 Task 범위에서 명시적으로 방어 코드를 추가함 — 추후 T025(UserService)의 비밀번호 유효성 검사(FR 관련)에서 길이 제한 UX를 추가할 때 이 예외를 활용할 수 있음
- `password_hash`는 bcrypt 표준 포맷(`$2b$<cost>$<salt+hash>`) 그대로 문자열로 반환 — data-model.md의 `users.password_hash VARCHAR(255)` 컬럼에 맞춰 바로 저장 가능 (bcrypt 해시는 항상 60자이므로 255자 제한에 충분히 여유 있음)

## 비고
- 이 유틸리티는 T025(UserService)의 회원가입/로그인 로직에서 실제로 사용될 예정 — 이번 Task는 순수 유틸 함수까지만 범위로 함
- 이로써 "Base Infrastructure" 섹션의 인증 기반 유틸(T012 JWT, T013 비밀번호 해싱)이 모두 준비됨
