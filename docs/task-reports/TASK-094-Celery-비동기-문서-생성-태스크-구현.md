# TASK-094. Celery 비동기 문서 생성 태스크 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/tasks/document_generation.py`에 `generate_document_task(task_id, user_id)` Celery 태스크를 구현했다. Celery 워커는 동기 컨텍스트이지만 T093 `DocumentGenerationService.generate()`는 async이므로, 태스크 함수는 얇은 동기 래퍼로만 두고 내부에서 `asyncio.run(_generate_document(...))`을 호출한다. `_generate_document`는 (1) `src/db/session.py`의 모듈 전역 엔진을 재사용하지 않고 자체 `AsyncEngine`/세션 팩토리를 새로 만들어, (2) `_run_generation(session, task_id, user_id, gemini_client)`을 호출해 실제 생성 로직(`DocumentGenerationService.generate()` 호출)을 수행하고, (3) 성공 시 `session.commit()`, (4) `finally`에서 `engine.dispose()`한다. `_run_generation`은 생성 로직만 분리해 둬서, 테스트에서 실제 DB 커밋 없이(기존 `db_session` fixture의 flush-only 패턴 그대로) 직접 검증할 수 있게 했다. 실패(`DocumentGenerationError`)는 삼키지 않고 그대로 전파해 Celery 태스크 자체가 FAILURE로 끝나며, `@celery_app.task(..., max_retries=0)`으로 Celery 레벨 재시도는 명시적으로 끈다(서비스가 이미 최대 3회 지수 백오프 재시도를 끝낸 뒤의 실패이기 때문). `celery_app.py`의 `include` 리스트에서 이 모듈 등록 주석을 해제했다.

## 변경 파일
- `backend/src/tasks/document_generation.py` (신규)
- `backend/src/tasks/celery_app.py` (`include` 리스트에서 T094 모듈 등록 주석 해제)
- `backend/tests/unit/test_document_generation_task.py` (신규)
- `backend/tests/integration/test_document_generation_task.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T094 체크)

## TDD 결과
- RED 커밋: 37e547f (test: Celery document-generation task dispatch + retry policy - RED (T094))
- GREEN 커밋: 48009c6 (feat: add Celery task wrapping DocumentGenerationService.generate - GREEN (T094))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 단위 테스트 3개(Celery 등록 여부, `max_retries == 0`, 동기 래�퍼가 `asyncio.run`을 통해 비동기 코어로 올바른 인자를 전달하는지를 monkeypatch로 검증 — 실제 DB/브로커 불필요) + 신규 통합 테스트 2개(`_run_generation`을 `db_session` fixture로 직접 호출해 fake Gemini client로 성공 시 `generation_status == "completed"`, 모든 재시도 소진 후 실패 시 `DocumentGenerationError`가 그대로 전파됨을 확인). `DATABASE_URL`/`REDIS_URL`을 localhost로 override해 전체 스위트 323 passed, ruff 통과.

## 기술 결정
- **태스크 전용 엔진/세션을 새로 생성**: `src/db/session.py`의 `AsyncSessionLocal`은 FastAPI 요청 루프에 바인딩된 asyncpg 커넥션 풀을 쓰는데, Celery 워커가 매 태스크 호출마다 `asyncio.run()`으로 새 이벤트 루프를 만들기 때문에 그 전역 엔진을 그대로 재사용하면 "다른 루프에서 만든 커넥션을 다른 루프에서 쓰는" 문제(`tests/conftest.py`의 `db_session` fixture 주석과 동일한 이유)가 생긴다. 따라서 `_generate_document`가 태스크 호출마다 자체 엔진을 만들고 끝나면 `dispose()`하는 방식을 택했다. 생성 빈도가 Task 1개당 1회 정도이고 문서 생성 자체가 최대 5분(`task_time_limit`)까지 걸릴 수 있는 작업이라, 매번 커넥션을 새로 맺는 오버헤드는 무시할 만하다고 판단했다.
- **`_run_generation`과 `_generate_document`를 분리**: Celery 전용 "자체 엔진 생성 + commit + dispose" 책임과 "DocumentGenerationService를 호출하는 실제 생성 로직"을 분리해, 통합 테스트가 기존 `db_session` fixture(flush만 하고 커밋하지 않아 테스트가 DB에 흔적을 남기지 않는 패턴)를 그대로 재사용해 생성 로직만 검증할 수 있게 했다. 만약 분리하지 않았다면 테스트가 자체 엔진으로 실제 커밋을 하게 되어 DB에 데이터가 영구적으로 남는 문제가 생겼을 것이다.
- **Celery 레벨 재시도 비활성화(`max_retries=0`)**: `DocumentGenerationService.generate()`가 이미 지수 백오프로 최대 3회 재시도한 뒤에 실패를 최종 확정(`generation_status="failed"` + `generation_error`)하므로, Celery가 그 위에 또 재시도를 얹으면 똑같이 실패할 작업을 반복 실행할 뿐이다(이중 재시도 방지).
- **예외를 삼키지 않음**: `generate_document_task` 내부에서 `DocumentGenerationError`를 catch하지 않고 그대로 전파되게 두어, Celery가 해당 태스크 실행을 FAILURE 상태로 인지할 수 있게 했다(`LearningDocument` 행 자체는 이미 "failed" 상태로 영속화되어 있으므로, 이 예외는 Celery/모니터링 쪽에 실패를 알리는 신호일 뿐).

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 localhost 기준으로 override해야 했음(기존 비고와 동일한 환경 이슈).
- 실제 Celery 워커를 띄워 `.delay()`로 디스패치하는 경로(브로커 왕복)는 이번 태스크 범위에서 테스트하지 않았다 — T095에서 `DocumentQueueService.enqueue()`가 `generate_document_task.delay(...)`를 호출할 때 다시 다룬다.
