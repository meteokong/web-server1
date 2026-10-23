# TASK-063. CodeFile SQLAlchemy 모델 생성

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`backend/src/models/code_file.py`에 CodeFile SQLAlchemy 모델을 구현했다. T009 마이그레이션(`backend/alembic/versions/001_initial_schema.py`)의 `code_files` 테이블 및 `data-model.md` 정의와 정확히 일치시켰다 (id, uploaded_code_id, file_name, file_path, file_extension, file_size_bytes, storage_path, mime_type, created_at). `UploadedCode` 모델에 비어 있던 `code_files` relationship(1:N, `back_populates`, `cascade="all, delete-orphan"`)도 함께 연결했다. 이것으로 Phase 5 "Backend: Task & Code Models"의 모델 3종(Task/UploadedCode/CodeFile, T061-T063)이 모두 완료됐다.

## 변경 파일
- `backend/src/models/code_file.py` (신규)
- `backend/src/models/uploaded_code.py` (code_files relationship 추가)
- `backend/tests/unit/test_code_file_model.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T063 체크)

## TDD 결과
- RED 커밋: 11c59d1 (test: CodeFile model - RED (T063))
- GREEN 커밋: cfe4a39 (feat: CodeFile SQLAlchemy model - GREEN (T063))
- REFACTOR 커밋: 해당 없음 (기존 모델들과 동일한 패턴을 그대로 따라 구현해 추가 개선 불필요)
- 테스트 커버리지: 전체 백엔드 스위트 142 passed, src/models/code_file.py 95% (미커버 라인은 `__repr__`, 다른 모델들과 동일하게 테스트 대상에서 제외)

## 기술 결정
- `file_path`는 폴더 업로드 시 구조 보존을 위한 상대 경로(없으면 단일 파일 업로드), `storage_path`는 실제 파일시스템 경로(`storage/uploads/{user_id}/{task_id}/...`, T067 FileStorageService에서 사용) — 둘의 역할을 주석으로 구분해 둠.
- `supported_extension` CHECK 제약(허용 확장자 12종)은 마이그레이션에 이미 선언되어 있으므로 모델에는 재선언하지 않음 (기존 모델들과 동일 — DB 레벨 제약은 마이그레이션이 단일 진실 공급원). 실제 업로드 시점의 확장자/크기/바이너리 검증 로직은 T064 file_validator에서 구현 예정.

## 비고
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일한 환경 이슈).
- Phase 5의 다음 단계는 T064(file_validator), T065(language_detector), T066(complexity_analyzer) — 모델이 아닌 유틸/서비스 레이어로 전환됨.
