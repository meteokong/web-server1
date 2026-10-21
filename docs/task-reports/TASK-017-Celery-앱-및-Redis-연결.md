# TASK-017. Celery 앱 및 Redis 연결 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
AI 문서 생성처럼 "시간이 오래 걸리는 작업"을 사용자를 기다리게 하지 않고 뒤에서 처리할 수 있도록, 작업 대기열 시스템(Celery)을 Redis에 연결했습니다. 비유하자면, 식당에서 복잡한 요리를 주방(백그라운드 워커)에 주문서(태스크)로 넘기고, 손님(API 응답)은 기다리지 않고 "접수했습니다, 완료되면 알려드릴게요"라고 바로 안내받는 구조입니다. Redis는 그 주문서를 전달하는 접수대(브로커)이자, 완성된 요리가 몇 번 테이블로 나갔는지 기록하는 보드(결과 백엔드) 역할을 동시에 합니다.

**`backend/src/tasks/celery_app.py` 구현 내용**:
- `CelerySettings`: `.env.example`의 `REDIS_URL`을 읽는 pydantic-settings 클래스
- `celery_app = Celery("code_study", broker=..., backend=...)`: Redis를 브로커와 결과 백엔드로 동시에 사용 (research.md "Redis chosen for: Fast message broker, Result backend for task status" 결정과 일치)
- `task_serializer`/`result_serializer`/`accept_content`를 모두 `json`으로 고정 (Python 전용 pickle 직렬화 대신 — 보안 및 디버깅 용이성)
- `task_track_started=True`: 긴 AI 생성 작업(T094/T118)이 "대기 중"이 아니라 "시작됨" 상태를 보여줄 수 있게 함
- `task_time_limit=300`(5분): plan.md의 "문서 생성 3분 목표"를 넘는 작업이 영원히 멈춰있지 않도록 강제 종료 시간을 둠
- `include=[...]`: 아직 존재하지 않는 미래의 태스크 모듈(T094 문서생성, T118 연습문제생성, T172 휴지통정리)을 등록할 자리를 주석으로 남겨둠

**검증 (실제 Redis·워커로 왕복 테스트)**:
1. 구조/설정 테스트(`backend/tests/unit/test_celery_app.py`, 3개): broker/backend URL이 설정값과 일치, JSON 직렬화 설정, `task_track_started`/`task_time_limit` 값 확인 — 모두 통과
2. **실제 End-to-End 테스트**: T004의 Redis 컨테이너(호스트에 `localhost:6379`로 매핑됨)를 대상으로
   - 임시 태스크(`smoke_test_add`)를 정의하고, `celery -A ... worker --pool=solo`로 **진짜 Celery 워커 프로세스**를 기동 → Redis에 정상 연결(`Connected to redis://localhost:6379/0`) 확인
   - 별도 프로세스에서 `add.delay(3, 4)`로 태스크를 브로커에 제출
   - `.get(timeout=10)`으로 결과 백엔드에서 결과를 조회 → `result=7`, `state=SUCCESS` 확인 — **제출→실행→결과조회 전체 흐름이 실제로 동작**함을 확인
   - 검증 후 워커 프로세스 종료, 임시 태스크 파일 삭제
3. 전체 테스트 스위트 재실행 → 29개 전부 통과(이전 26개 + 이번 3개), Ruff/Black 통과

## 변경 파일
- `backend/src/tasks/celery_app.py` (신규)
- `backend/src/tasks/__init__.py` (신규, 패키지 인식용)
- `backend/tests/unit/test_celery_app.py` (신규)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 "설정은 맞는데 실제로 워커가 못 뜨거나 연결이 안 되는" 흔한 실수를 잡기 위해, 구조적 단위 테스트에 더해 실제 Redis·워커·태스크 제출까지 포함한 종단 간(End-to-End) 검증을 수행함.

## 기술 결정 (해당 시)
- 처음에 Celery의 `autodiscover_tasks(["src.tasks"])`를 사용하려 했으나, 이 메서드는 기본적으로 각 패키지 안의 `<package>.tasks` 서브모듈을 찾는 방식(Django 스타일)이라, 태스크 모듈이 `tasks` 패키지 "안에" 직접 위치하는 이번 프로젝트 구조와는 맞지 않음을 검증 과정에서 발견 → 이 호출은 실제로 아무것도 찾지 못하는 **죽은 코드**였음을 확인하고 제거, 대신 `Celery()` 생성자의 `include=[...]` 파라미터에 향후 추가될 태스크 모듈 경로를 주석으로 남겨 명확하게 함
- 로컬(Docker 밖)에서 워커를 띄울 때는 `.env`의 `REDIS_URL=redis://redis:6379/0`(Docker 네트워크 내부 호스트명)이 해석되지 않아 `getaddrinfo failed` 에러가 발생함을 실제로 확인 — 이는 버그가 아니라 환경 차이(Docker 내부 실행 vs 로컬 실행)이며, 로컬 개발 시에는 `REDIS_URL=redis://localhost:6379/0`로 오버라이드해야 함을 테스트 중 직접 재현해 확인함 (quickstart.md의 안내와 일치)
- Windows에서는 Celery의 기본 prefork pool이 아닌 `--pool=solo`를 사용해야 함을 확인 (Windows는 다중 프로세스 포크를 지원하지 않음) — 추후 프로덕션 배포 시 Linux 환경에서는 기본 pool 사용 가능

## 비고
- 실제 태스크(문서 생성, 연습문제 생성, 휴지통 정리)는 아직 작성되지 않음 — T094, T118, T172에서 각각 작성되며, 작성 시 `celery_app.py`의 `include` 리스트에 모듈 경로를 추가해야 함
- 로컬에서 워커를 수동으로 띄우려면 `cd backend && REDIS_URL=redis://localhost:6379/0 celery -A src.tasks.celery_app worker --pool=solo` 형태로 실행 (Docker Compose로 백엔드/워커 서비스까지 구성하는 것은 T211+ 배포 준비 단계에서 다룰 범위)
- 이로써 Phase 2(Foundational)의 "Database & Migrations" + "Base Infrastructure" 섹션(T008~T017)이 모두 완료됨
