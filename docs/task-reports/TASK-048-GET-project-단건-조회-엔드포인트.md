# TASK-048. GET /projects/{project_id} 단건 조회 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`GET /api/v1/projects/{project_id}` 엔드포인트를 추가했다. `get_current_user`로 보호되며, `ProjectService.get(project_id, current_user.id)`를 호출한다. 프로젝트가 존재하지 않거나 다른 사용자 소유라면 서비스가 던지는 `NotFoundError`가 전역 핸들러에 의해 `404`로 변환되어, 두 경우가 응답에서 구분되지 않는다 (다른 사용자의 project_id 존재 여부를 추측할 수 없도록).

## 변경 파일
- `backend/src/api/projects.py` (`get_project` 핸들러 — T046과 같은 커밋)
- `backend/tests/integration/test_projects_api.py` (`test_get_project_success`, `test_get_project_rejects_missing_auth`, `test_get_project_404_for_unknown_id`, `test_get_project_404_for_another_users_project`)
- `specs/001-ai-code-learning-platform/tasks.md` (T048 체크)

## TDD 결과
- RED 커밋: a1147e3 (test: projects API endpoints - RED (T046-T050))
- GREEN 커밋: d9f7c44 (feat: projects API endpoints - GREEN (T046-T050))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 121 passed, `src/api/projects.py` 98%

## 기술 결정
- 소유권 검증 로직은 전혀 중복 구현하지 않음 — T045에서 이미 `ProjectService.get`에 구현된 `_get_owned_or_404`를 그대로 신뢰. 라우트 레이어는 "다른 사용자 프로젝트"와 "존재하지 않는 프로젝트"를 구분할 필요가 없어 보안적으로도 안전.

## 비고
- `test_get_project_404_for_another_users_project` 테스트로 ownership leak이 없는지 명시적으로 검증함.
