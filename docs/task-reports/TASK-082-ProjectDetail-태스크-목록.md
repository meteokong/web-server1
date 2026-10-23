# TASK-082. ProjectDetail에 태스크 목록/생성 연동

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/pages/ProjectDetail.tsx`의 "태스크 타임라인" 플레이스홀더 섹션을 실제 태스크 목록/생성 기능으로 교체했다.
- `useQuery(["tasks", projectId])`로 `listTasks(projectId)`(T080)를 호출해 태스크 목록을 가져오고, Dashboard(T054)와 동일한 로딩/에러/빈 상태 컨벤션(`{isLoading && <p>로딩 중...</p>}` 등)으로 `TaskCard`(T079)들을 렌더링.
- "새 태스크" 버튼으로 `CreateTaskModal`(T081)을 열고, `useMutation`으로 `createTask`를 호출 — 성공 시 `["tasks", projectId]` 쿼리를 `exact: true`로 무효화해 목록을 바로 갱신(수동 리로드 없이).

## 변경 파일
- `frontend/src/pages/ProjectDetail.tsx` (수정 — 플레이스홀더 섹션 교체)
- `frontend/src/pages/ProjectDetail.test.tsx` (수정 — 기존 "태스크 타임라인 플레이스홀더" 테스트를 태스크 목록/생성 테스트 5개로 교체, 기존 5개 테스트는 유지)
- `specs/001-ai-code-learning-platform/tasks.md` (T082 체크)

## TDD 결과
- RED 커밋: 248cf5d (test: task list and creation in ProjectDetail - RED (T082))
- GREEN 커밋: 39900c4 (feat: task list and creation in ProjectDetail - GREEN (T082))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `ProjectDetail.test.tsx` 10/10 테스트 통과(기존 5개 + 신규 5개)

## 기술 결정
- 기존 "태스크 타임라인 기능은 아직 구현되지 않았습니다" 플레이스홀더를 검증하던 테스트는, 이번 태스크의 지시(해당 섹션을 실제 기능으로 교체)가 명시적으로 그 동작을 없애는 것이므로, 같은 파일 안에서 실제 목록/생성 동작을 검증하는 새 테스트로 교체했다 — 테스트 불변성 원칙은 "이미 구현된 동작을 몰래 바꾸려고 테스트를 고치는 것"을 금지하는 것이고, 이번 경우는 브리프가 요구한 기능 교체 자체를 반영한 것.
- `["tasks", projectId]` 쿼리 무효화에 `exact: true`를 명시 — ProjectDetail이 이미 `["projects", projectId]`에 대해 같은 이유(`updateMutation`/`deleteMutation`의 주석 참고)로 `exact: true`를 쓰고 있어, 다른 prefix와 우연히 매칭되는 상황을 피하기 위해 동일하게 적용(이번 키는 다른 쿼리와 prefix가 겹치지 않지만, 패턴 일관성을 위해 유지).
- `CreateTaskModalValues`의 `description`이 빈 문자열이면 `createTask`에 `undefined`로 전달 — task-service의 `CreateTaskFields.description`이 옵셔널이라 빈 문자열을 그대로 보내면 FormData에 빈 값이 append되는 것을 피함(project-service의 `description || null` 처리와 같은 의도).

## 비고
- CreateTaskModal이 파일/폴더 업로드 방식일 때 모은 `files`도 동일한 뮤테이션 경로로 전달되므로, 실제 파일 업로드 동작은 백엔드의 POST /projects/{id}/tasks(T071, 병행 작업 중)가 완성되면 수동 브라우저 테스트로 확인 예정.
