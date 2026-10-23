# TASK-046. GET /projects 목록 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`backend/src/api/projects.py`에 `GET /api/v1/projects` 엔드포인트를 추가했다. `get_current_user`로 보호되며, `ProjectService.get_user_projects(current_user.id)`를 호출해 현재 사용자의 활성(trashed가 아닌) 프로젝트만 최신순으로 반환한다. 응답은 계약(`projects-api.md`)대로 `{"projects": [...]}` 형태로 감싸며, bare array가 아니다. `ProjectResponse`/`ProjectListResponse` Pydantic 모델을 함께 정의했고, `src/api/router.py`에 `projects_router`를 `/projects` prefix, `["projects"]` tag로 등록했다.

T046-T050 다섯 엔드포인트는 같은 파일/같은 라우터에 함께 구현되어 RED/GREEN 커밋을 공유한다 (아래 TDD 결과 참고).

## 변경 파일
- `backend/src/api/projects.py` (신규 — list_projects 포함 5개 엔드포인트, ProjectResponse/ProjectListResponse/ProjectCreateRequest/ProjectUpdateRequest)
- `backend/src/api/router.py` (projects_router 등록)
- `backend/tests/integration/test_projects_api.py` (신규 — 5개 엔드포인트 통합 테스트, auth_client 픽스처 재사용)
- `specs/001-ai-code-learning-platform/tasks.md` (T046 체크)

## TDD 결과
- RED 커밋: a1147e3 (test: projects API endpoints - RED (T046-T050))
- GREEN 커밋: d9f7c44 (feat: projects API endpoints - GREEN (T046-T050))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 121 passed (기존 104 + 신규 17), `src/api/projects.py` 98%

## 기술 결정
- 라우트 핸들러는 얇게 유지: `ProjectService.get_user_projects`를 그대로 호출하고 반환값을 `ProjectListResponse`로 감싸는 것 외의 로직 없음.
- 기존 `tests/integration/conftest.py`의 `auth_client` 픽스처(`src.main.app` 전체를 ASGITransport로 구동, `get_db`만 오버라이드)를 그대로 재사용 — projects 라우터가 `api_router`에 등록되는 즉시 같은 픽스처로 테스트 가능해짐.

## 비고
- T047-T050은 같은 파일에서 함께 구현되어 동일한 RED/GREEN 커밋을 참조한다. 각 태스크 리포트는 해당 엔드포인트에 집중된 내용을 담되 공유 커밋 해시를 명시한다.
