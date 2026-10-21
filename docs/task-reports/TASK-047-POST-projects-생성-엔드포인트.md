# TASK-047. POST /projects 생성 엔드포인트 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`POST /api/v1/projects` 엔드포인트를 추가했다. `get_current_user`로 보호되며, 요청 본문(`ProjectCreateRequest`: `title`, `description` 선택)을 받아 `ProjectService.create(current_user.id, title, description)`을 호출한다. 성공 시 `201 Created`와 `ProjectResponse`를 반환하고, 제목이 공백이면 서비스가 던지는 `ValidationAppError`가 전역 핸들러에 의해 `400`으로 변환된다.

## 변경 파일
- `backend/src/api/projects.py` (`create_project` 핸들러, `ProjectCreateRequest` 모델 — T046과 같은 커밋)
- `backend/tests/integration/test_projects_api.py` (`test_create_project_success`, `test_create_project_rejects_blank_title`, `test_create_project_rejects_missing_auth`)
- `specs/001-ai-code-learning-platform/tasks.md` (T047 체크)

## TDD 결과
- RED 커밋: a1147e3 (test: projects API endpoints - RED (T046-T050))
- GREEN 커밋: d9f7c44 (feat: projects API endpoints - GREEN (T046-T050))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 121 passed, `src/api/projects.py` 98%

## 기술 결정
- 블랭크 제목 검증은 라우트에서 별도로 처리하지 않고 `ProjectService.create`가 던지는 `ValidationAppError`에 전적으로 위임 — 라우트는 호출/반환만 담당 (계약 문서가 명시한 "thin handler" 원칙).

## 비고
- T046-T050 공유 커밋 구조는 TASK-046 리포트의 "비고" 참고.
