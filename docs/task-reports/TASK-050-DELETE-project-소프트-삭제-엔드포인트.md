# TASK-050. DELETE /projects/{project_id} (소프트 삭제) 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`DELETE /api/v1/projects/{project_id}` 엔드포인트를 추가했다. `get_current_user`로 보호되며, `ProjectService.soft_delete(project_id, current_user.id)`를 호출한다. 성공 시 `200 OK`와 `deletion_status: "trashed"`, `trashed_at`, `scheduled_deletion_at`(30일 후)가 채워진 `ProjectResponse`를 반환한다. 영구 삭제가 아니라 트래시로 이동만 하며, 영구 삭제는 Phase 10의 `trash_service.py`에서 별도로 처리될 예정이라 이번 범위에 포함하지 않았다.

## 변경 파일
- `backend/src/api/projects.py` (`delete_project` 핸들러 — T046과 같은 커밋)
- `backend/tests/integration/test_projects_api.py` (`test_delete_project_moves_to_trash`, `test_delete_project_rejects_missing_auth`, `test_delete_project_404_for_another_users_project`)
- `specs/001-ai-code-learning-platform/tasks.md` (T050 체크)

## TDD 결과
- RED 커밋: a1147e3 (test: projects API endpoints - RED (T046-T050))
- GREEN 커밋: d9f7c44 (feat: projects API endpoints - GREEN (T046-T050))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 121 passed, `src/api/projects.py` 98%

## 기술 결정
- HTTP 메서드는 `DELETE`이지만 상태 코드는 `200 OK`(계약 명시)로 — 실제로 리소스를 삭제하는 것이 아니라 상태를 변경하고 변경된 리소스를 응답으로 돌려주기 때문에 `204 No Content`가 아닌 `200`을 사용.

## 비고
- T046-T050, 5개 엔드포인트 전부 구현 완료. 전체 백엔드 스위트 121 passed, `ruff check src/ tests/` clean.
