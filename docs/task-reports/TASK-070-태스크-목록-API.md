# TASK-070. GET /projects/{project_id}/tasks 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/api/tasks.py`(신규)에 프로젝트의 태스크 목록을 조회하는 `GET /api/v1/projects/{project_id}/tasks`를 구현했다. `ProjectService(db).get(project_id, current_user.id)`로 프로젝트 소유권을 먼저 확인(없거나 내 것이 아니면 404)한 뒤, `TaskService(db).list_by_project(...)`로 활성 태스크 목록을 조회해 반환한다.

Tasks 라우터는 Projects 라우터와 달리 고정 prefix가 없다 — `/projects/{project_id}/tasks`(목록/생성)와 `/tasks/{task_id}`(단일 조회/수정/삭제/코드) 두 가지 경로 형태를 하나의 라우터가 섞어서 쓰기 때문에, `router = APIRouter()`(prefix 없음)로 선언하고 각 라우트가 전체 경로를 직접 명시한다. `src/api/router.py`에 `api_router.include_router(tasks_router, tags=["tasks"])`로 등록(이미 `/api/v1` prefix를 가진 `api_router`에 추가되므로 최종 경로가 정확히 맞음).

## 변경 파일
- `backend/src/api/tasks.py` (신규 — `TaskResponse`/`TaskListResponse` 모델, `list_tasks` 핸들러)
- `backend/src/api/router.py` (수정 — tasks 라우터 등록)
- `backend/tests/integration/test_tasks_api.py` (신규, 4개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T070 체크)

## TDD 결과
- RED 커밋: 8b26cd4 (test: GET /projects/{id}/tasks endpoint - RED (T070))
- GREEN 커밋: 93ca391 (feat: GET /projects/{id}/tasks endpoint - GREEN (T070))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/api/tasks.py` 97%(미도달 1줄은 이번 커밋에서 아직 쓰이지 않는 핸들러 본문 — 이후 T071~T075에서 모두 채워짐). 전체 백엔드 스위트 261 passed, 회귀 없음.

## 기술 결정
- **인증 누락 시 404가 아니라 401이 먼저 응답됨**: `Depends(get_current_user)`가 `Depends(get_db)`보다 먼저 평가되어, 인증되지 않은 요청은 프로젝트 존재 여부와 무관하게 401을 받는다 — `ProjectResponse`/Projects API와 동일한 기존 동작.
- `TaskResponse`는 `ProjectResponse`와 동일하게 `model_config = {"from_attributes": True}`로 ORM 객체를 그대로 직렬화 — DB 컬럼과 1:1 매핑.

## 비고
- `TaskListResponse`/`TaskResponse`는 T072(단일 태스크 조회)·T073(수정)·T074(삭제)에서도 그대로 재사용된다.
