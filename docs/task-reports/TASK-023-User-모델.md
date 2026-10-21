# TASK-023. User SQLAlchemy 모델

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
T009에서 SQL로 만들어둔 `users` 테이블을, Python 코드로 다룰 수 있는 "번역기"(SQLAlchemy ORM 모델)로 만들었습니다. 비유하자면, 이미 지어진 건물(DB 테이블)의 설계도를 프로그램이 읽을 수 있는 언어로 다시 옮겨 적은 것입니다 — 건물 자체는 그대로지만, 이제 Python 코드에서 `User(email=..., password_hash=...)`처럼 자연스럽게 다룰 수 있게 됩니다.

이번 Task부터는 **Phase 3(Authentication Slice)**에 속해, tasks.md/constitution이 명시한 TDD(RED-GREEN-REFACTOR) + 단계별 git 커밋이 의무입니다. 이를 위해 **이번 세션에서 처음으로 git 저장소를 초기화**했습니다(사용자 승인 후 진행) — Phase 1~2의 기존 산출물은 `chore: initial commit of Phase 1-2 scaffolding`으로 먼저 베이스라인 커밋을 만들고, 저장소 루트에 섞여 있던 정체불명의 마커/스크래치 파일(`speckit-implement-task-*.txt` 등 20여 개)은 사용자 확인 후 커밋에서 제외함.

**TDD 사이클**:
- 🔴 **RED** (`50044f2`): `backend/tests/unit/test_user_model.py` 작성 — `src.models.user.User`를 import하는 테스트 6개. 아직 모델이 없어 `ModuleNotFoundError`로 전부 실패함을 확인 후 커밋
- 🟢 **GREEN** (`1e00954`): `backend/src/models/user.py` 작성 — T009 마이그레이션의 `users` 테이블 컬럼(`id`, `email`, `password_hash`, `skill_level`, `created_at`, `updated_at`, `last_login_at`)을 그대로 매핑. 6개 테스트 전부 통과 확인 후 커밋 (Black 포맷팅까지 반영된 상태로 커밋되어, 별도 REFACTOR 디프가 남지 않음 — "비고" 참고)

**실제 DB 검증** (단위 테스트 범위를 넘어서, 라이브 PostgreSQL에 대해):
- `skill_level`을 지정하지 않고 INSERT → DB의 `server_default` 값 `'Complete Beginner'`가 정확히 적용됨을 확인
- 같은 이메일로 두 번째 INSERT 시도 → `IntegrityError`로 정상 거부됨(유니크 제약 확인)
- 검증 후 트랜잭션 롤백으로 테스트 데이터 제거

전체 백엔드 테스트 스위트 재실행 → 35개 전부 통과(기존 29개 + 이번 6개). Ruff/Black 통과.

## 변경 파일
- `backend/src/models/user.py` (신규)
- `backend/tests/unit/test_user_model.py` (신규)
- (git 초기화 관련) `.git/` 신규 생성, 루트 커밋 1건 + 이번 Task 커밋 2건

## TDD 결과
- RED 커밋: `50044f2`
- GREEN 커밋: `1e00954`
- REFACTOR 커밋: 해당 없음 — GREEN 구현 직후 `black .`을 실행해 포맷을 맞췄는데, 이를 GREEN 커밋 전에 적용해버려 별도로 커밋할 변경 사항이 남지 않음. 모델이 이미 최소 구현 그대로 깔끔해 추가로 개선할 품질 이슈도 발견되지 않음

## 기술 결정 (해당 시)
- 이번 모델에는 **관계(relationship)를 추가하지 않음** — `User`는 `Project`(1:N, T043에서 생성), `RefreshToken`(1:N, T024에서 생성)과 관계가 있지만, 아직 그 모델들이 존재하지 않는 시점에 `relationship()`을 걸면 SQLAlchemy의 매퍼 구성(configure_mappers) 시점에 "클래스를 찾을 수 없음" 에러가 날 수 있음. data-model.md가 요구하는 것은 테이블 컬럼 수준의 일치이므로, 이번 Task는 컬럼까지만 구현하고 관계는 관련 모델이 생성되는 후속 Task(T024, T043)에서 양쪽에 추가하기로 함
- `skill_level`의 Python 쪽 기본값을 지정하지 않음(DB의 `server_default`에만 의존) — Python 객체 생성 시점과 실제 INSERT 시점의 기본값 적용 주체를 하나로 통일해, "Python 기본값과 DB 기본값이 서로 다르게 설정되어 불일치가 생기는" 흔한 함정을 피함
- git 초기화 범위를 Phase 1~2 전체를 아우르는 단일 베이스라인 커밋으로 정함 — Task별로 거슬러 올라가 재구성하는 대신, 지금부터(Phase 3)의 작업만 TDD 커밋 단위로 추적하는 실용적 접근

## 비고
- `RefreshToken`(T024)이 다음 Task — User와 1:N 관계이므로, 두 모델이 모두 준비되면 `relationship(back_populates=...)`을 양쪽에 추가하는 작업이 뒤따를 수 있음
- 저장소 루트의 마커/스크래치 파일들은 사용자 요청에 따라 이번 커밋에서 의도적으로 제외됨 — 여전히 untracked 상태로 남아있으며, 삭제나 커밋 여부는 사용자가 추후 직접 결정할 사항
