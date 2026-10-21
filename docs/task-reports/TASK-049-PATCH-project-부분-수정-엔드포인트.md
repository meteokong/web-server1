# TASK-049. PATCH /projects/{project_id} 부분 수정 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`PATCH /api/v1/projects/{project_id}` 엔드포인트를 추가했다. `get_current_user`로 보호되며, 요청 본문(`ProjectUpdateRequest`: `title`, `description` 모두 선택, 기본값 `None`)을 받아 `ProjectService.update(project_id, current_user.id, title=..., description=...)`를 호출한다. 서비스가 `None`인 필드는 건드리지 않으므로 부분 업데이트가 그대로 동작한다. 존재하지 않거나 소유자가 아니면 `NotFoundError`(404), 빈 제목이면 `ValidationAppError`(400).

## 변경 파일
- `backend/src/api/projects.py` (`update_project` 핸들러, `ProjectUpdateRequest` 모델 — T046과 같은 커밋)
- `backend/tests/integration/test_projects_api.py` (`test_patch_project_updates_title_and_description`, `test_patch_project_partial_update_keeps_other_field`, `test_patch_project_rejects_blank_title`, `test_patch_project_rejects_missing_auth`, `test_patch_project_404_for_another_users_project`)
- `specs/001-ai-code-learning-platform/tasks.md` (T049 체크)

## TDD 결과
- RED 커밋: a1147e3 (test: projects API endpoints - RED (T046-T050))
- GREEN 커밋: d9f7c44 (feat: projects API endpoints - GREEN (T046-T050))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 121 passed, `src/api/projects.py` 98%

## 기술 결정
- `ProjectUpdateRequest`의 두 필드 모두 기본값 `None`으로 두어, "필드 생략"과 "서비스가 해당 필드를 건드리지 않음"을 그대로 매핑. `ProjectService.update`가 `description=None`을 "건드리지 않음"으로 해석하므로 description을 명시적으로 `null`로 지워 지우는 기능은 현재 지원되지 않음 — 이는 서비스 레이어의 기존 동작이며 이번 태스크 범위에서 변경하지 않음 (계약 문서에도 해당 엣지케이스는 명시되어 있지 않음).

## 비고
- `test_patch_project_partial_update_keeps_other_field`로 title을 보내지 않았을 때 기존 title이 유지되는지 검증함.
