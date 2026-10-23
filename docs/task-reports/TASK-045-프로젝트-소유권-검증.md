# TASK-045. 프로젝트 소유권 검증 구현

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`ProjectService`의 `get`, `update`, `soft_delete`가 모두 `user_id`를 필수 파라미터로 받도록 변경하고, 내부 조회를 `_get_or_404` → `_get_owned_or_404`로 교체했다. 프로젝트가 존재하지 않는 경우와 존재하지만 다른 사용자 소유인 경우를 동일하게 `NotFoundError`로 처리해, 다른 사용자의 project_id 존재 여부를 응답으로 추측할 수 없도록 했다 (UserService의 로그인 에러 통일 패턴과 동일한 설계).

`create`와 `get_user_projects`는 이미 `user_id` 기준으로 동작하므로 변경하지 않았다.

## 변경 파일
- `backend/src/services/project_service.py` (get/update/soft_delete 시그니처에 user_id 추가, `_get_owned_or_404` 헬퍼로 교체)
- `backend/tests/integration/test_project_service.py` (기존 테스트에 user_id 인자 추가 + 소유자가 다른 경우 NotFoundError를 검증하는 3개 테스트 추가)
- `specs/001-ai-code-learning-platform/tasks.md` (T045 체크)

## TDD 결과
- RED 커밋: caf83e9 (test: ProjectService ownership validation - RED (T045))
- GREEN 커밋: b50a519 (feat: project ownership validation - GREEN (T045))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 104 passed, src/services/project_service.py 100%

## 기술 결정
- "존재하지 않음"과 "소유자가 다름"을 구분하지 않고 동일한 `NotFoundError`(404)로 응답 — 403 Forbidden을 쓰면 "이 id는 존재하지만 내 것이 아니다"라는 정보가 노출되어 다른 사용자의 project_id를 enumeration할 수 있게 되므로 의도적으로 피함.
- DB round-trip을 한 번만 하도록 `self.db.get(Project, project_id)` 후 `project.user_id != user_id`를 메모리에서 비교하는 방식 유지 (쿼리 필터에 user_id를 추가하는 대신). T044의 `_get_or_404`를 대체.

## 비고
- 이 변경으로 `get`/`update`/`soft_delete`의 시그니처가 바뀌었으나, 아직 이를 호출하는 API 엔드포인트(T046-T050)가 없어 하위 호환성 문제는 없음.
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일).
- 브라우저 수동 테스트(T039-T042)는 Claude Chrome 확장 연결 대기 중.
