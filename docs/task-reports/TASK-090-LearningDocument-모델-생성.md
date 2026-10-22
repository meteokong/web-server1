# TASK-090. LearningDocument SQLAlchemy 모델 생성

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/models/learning_document.py`에 LearningDocument SQLAlchemy 모델을 구현했다. T009 마이그레이션(`backend/alembic/versions/001_initial_schema.py`)의 `learning_documents` 테이블 및 `data-model.md` 정의와 정확히 일치시켰다 (id, task_id, content, generation_status, generation_started_at, generation_completed_at, generation_error, celery_task_id, created_at, updated_at). `content`는 7장 구조를 담는 JSONB 컬럼으로 `nullable=False` 매핑했다. `task_id`는 Task와 1:1 관계이므로 `unique=True`로 선언했다. `Task` 모델에 `learning_document` relationship(`uselist=False`, `back_populates`, `cascade="all, delete-orphan"`)도 함께 연결했다.

## 변경 파일
- `backend/src/models/learning_document.py` (신규)
- `backend/src/models/task.py` (learning_document relationship 추가)
- `backend/tests/unit/test_learning_document_model.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T090 체크)

## TDD 결과
- RED 커밋: 8c4d24d (test: LearningDocument SQLAlchemy model columns/constraints - RED (T090))
- GREEN 커밋: 4f90d9d (feat: add LearningDocument SQLAlchemy model with JSONB content - GREEN (T090))
- REFACTOR 커밋: 해당 없음 (기존 모델들(UploadedCode 등)과 동일한 패턴을 그대로 따라 구현해 추가 개선 불필요)
- 테스트 커버리지: 전체 백엔드 unit 스위트 154 passed (단독 실행 시 Task↔Project 매퍼 순환 참조로 인한 기존 이슈가 재현되나, 전체 스위트 기준으로는 정상 통과)

## 기술 결정
- Task:LearningDocument = 1:1 관계를 `relationship(..., uselist=False)`로 표현 — 리스트가 아닌 단일 객체(또는 None)로 접근 가능하도록 함.
- `generation_status IN ('pending','in_progress','completed','failed')`, `valid_content_structure`(7개 챕터 키 존재) CHECK 제약은 마이그레이션에 이미 선언되어 있으므로 모델에는 재선언하지 않음 (기존 모델들과 동일 — DB 레벨 제약은 마이그레이션이 단일 진실 공급원).
- `generation_status`/`generation_started_at`/`generation_completed_at`/`generation_error`/`celery_task_id`는 문서 생성 요청 이후 비동기 작업(T094 Celery task) 진행에 따라 채워지는 필드이므로 전부 nullable로 매핑.

## 비고
- 기존 `test_task_model.py`에서도 동일하게 나타나는 "단독 실행 시 매퍼 설정 실패" 현상은 이번 작업으로 새로 생긴 것이 아니라 모델 모듈을 전부 import하지 않고 단일 테스트 파일만 실행할 때 발생하는 기존 이슈이며, `pytest tests/unit/` 전체 실행 시에는 문제없이 통과함을 확인했다.
