# TASK-074. DELETE /tasks/{task_id} (소프트 삭제) 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`에 태스크 소프트 삭제 `DELETE /api/v1/tasks/{task_id}`를 추가했다. `TaskService(db).soft_delete(task_id, current_user.id)`에 위임 — `deletion_status='trashed'`, `trashed_at`/`scheduled_deletion_at`(+30일) 설정과 소유권 확인/404는 T068이 이미 담당. 응답 형태는 `delete_project`와 동일하게 수정된 Task 전체(삭제 상태 포함)를 그대로 반환.

## 변경 파일
- `backend/src/api/tasks.py` (수정 — `delete_task` 핸들러 추가)
- `backend/tests/integration/test_tasks_api.py` (수정 — T074용 테스트 3개)
- `specs/001-ai-code-learning-platform/tasks.md` (T074 체크)

## TDD 결과
- RED 커밋: 1b3e6c8 (test: DELETE /tasks/{task_id} endpoint - RED (T074))
- GREEN 커밋: f38cc63 (feat: DELETE /tasks/{task_id} endpoint - GREEN (T074))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 100%. 전체 백엔드 스위트 281 passed, 회귀 없음.

## 기술 결정
- 별도 기술 결정 없음 — Projects API의 `delete_project`와 동일한 패턴.

## 비고
- 이 엔드포인트는 실제 파일(storage/uploads)이나 UploadedCode/CodeFile 행을 삭제하지 않는다 — 소프트 삭제이므로 30일 보관 정책(`scheduled_deletion_at`) 동안 데이터가 유지되며, 실제 영구 삭제(하드 삭제 + 파일 정리)는 별도의 휴지통(trash) 정리 작업(Celery `cleanup` 큐, 이 task 범위 밖)에서 처리될 예정이다.
