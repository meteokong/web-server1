# TASK-073. PATCH /tasks/{task_id} 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`에 태스크 부분 수정 `PATCH /api/v1/tasks/{task_id}`를 추가했다. `TaskUpdateRequest`(`title`/`description` 모두 선택)를 받아 `TaskService(db).update(...)`에 그대로 위임 — 주어진 필드만 변경되는 부분 업데이트, 제목 5자 미만 검증, 소유권 확인/404는 모두 T068의 `TaskService.update`가 담당. `ProjectUpdateRequest`/`update_project`와 동일한 패턴(Projects API의 `PATCH /{project_id}` 미러링).

## 변경 파일
- `backend/src/api/tasks.py` (수정 — `TaskUpdateRequest` 모델, `update_task` 핸들러 추가)
- `backend/tests/integration/test_tasks_api.py` (수정 — T073용 테스트 5개)
- `specs/001-ai-code-learning-platform/tasks.md` (T073 체크)

## TDD 결과
- RED 커밋: df48d1f (test: PATCH /tasks/{task_id} endpoint - RED (T073))
- GREEN 커밋: 05bb5b3 (feat: PATCH /tasks/{task_id} endpoint - GREEN (T073))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 100%. 전체 백엔드 스위트 278 passed, 회귀 없음.

## 기술 결정
- 별도 기술 결정 없음 — Projects API의 기존 패턴을 그대로 적용.

## 비고
- `task_number`는 이 엔드포인트로 변경할 수 없음(요청 바디에 포함되지 않음) — data-model.md의 "immutable once assigned" 요구사항을 API 레이어에서도 자연스럽게 지킴.
