# TASK-072. GET /tasks/{task_id} 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`에 단일 태스크 조회 `GET /api/v1/tasks/{task_id}`를 추가했다. `TaskService(db).get(task_id, current_user.id)` 한 줄로 위임 — 소유권 검증과 404 처리는 T068의 `TaskService._get_owned_or_404`가 이미 담당한다. `ProjectResponse`/`get_project`와 완전히 동일한 패턴(`Projects API`의 `GET /{project_id}`를 그대로 미러링).

## 변경 파일
- `backend/src/api/tasks.py` (수정 — `get_task` 핸들러 추가)
- `backend/tests/integration/test_tasks_api.py` (수정 — T072용 테스트 4개)
- `specs/001-ai-code-learning-platform/tasks.md` (T072 체크)

## TDD 결과
- RED 커밋: 7530a25 (test: GET /tasks/{task_id} endpoint - RED (T072))
- GREEN 커밋: 3309e89 (feat: GET /tasks/{task_id} endpoint - GREEN (T072))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 100%. 전체 백엔드 스위트 273 passed, 회귀 없음.

## 기술 결정
- 별도 기술 결정 없음 — Projects API의 기존 패턴을 그대로 적용.

## 비고
- 이 라우트는 Task 라우터에 고정 prefix가 없는 설계(T070 보고서 참조) 덕분에 `/tasks/{task_id}` 경로를 그대로 쓸 수 있었다.
