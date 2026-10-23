# TASK-062. UploadedCode SQLAlchemy 모델 생성

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`backend/src/models/uploaded_code.py`에 UploadedCode SQLAlchemy 모델을 구현했다. T009 마이그레이션(`backend/alembic/versions/001_initial_schema.py`)의 `uploaded_code` 테이블 및 `data-model.md` 정의와 정확히 일치시켰다 (id, task_id, detected_language, complexity_level, total_lines, total_files, upload_size_bytes, created_at). `task_id`는 Task와 1:1 관계이므로 `unique=True`로 선언했다. `Task` 모델에 `uploaded_code` relationship(`uselist=False`, `back_populates`, `cascade="all, delete-orphan"`)도 함께 연결했다.

## 변경 파일
- `backend/src/models/uploaded_code.py` (신규)
- `backend/src/models/task.py` (uploaded_code relationship 추가)
- `backend/tests/unit/test_uploaded_code_model.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T062 체크)

## TDD 결과
- RED 커밋: 574671a (test: UploadedCode model - RED (T062))
- GREEN 커밋: ee96357 (feat: UploadedCode SQLAlchemy model - GREEN (T062))
- REFACTOR 커밋: 해당 없음 (기존 모델들과 동일한 패턴을 그대로 따라 구현해 추가 개선 불필요)
- 테스트 커버리지: 전체 백엔드 스위트 135 passed, src/models/uploaded_code.py 95% (미커버 라인은 `__repr__`, 다른 모델들과 동일하게 테스트 대상에서 제외)

## 기술 결정
- Task:UploadedCode = 1:1 관계를 `relationship(..., uselist=False)`로 표현 — 리스트가 아닌 단일 객체(또는 None)로 접근 가능하도록 함.
- `complexity_level IN ('beginner','intermediate','advanced')`, `upload_size_bytes <= 10485760`(10MB) CHECK 제약은 마이그레이션에 이미 선언되어 있으므로 모델에는 재선언하지 않음 (기존 모델들과 동일 — DB 레벨 제약은 마이그레이션이 단일 진실 공급원).
- `detected_language`/`complexity_level`/`total_lines`/`total_files`/`upload_size_bytes`는 코드 업로드 직후가 아니라 언어 감지(T065)·복잡도 분석(T066) 서비스가 실행된 뒤 채워지는 필드이므로 전부 nullable로 매핑.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일한 환경 이슈).
