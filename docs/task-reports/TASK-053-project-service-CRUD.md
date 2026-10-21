# TASK-053. project-service (CRUD API calls)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`specs/001-ai-code-learning-platform/contracts/projects-api.md`에 문서화된 5개 엔드포인트(`GET /projects`, `POST /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}`)에 대한 얇은 래퍼를 `auth-service.ts`(T034)와 동일한 패턴으로 구현했습니다.

- `listProjects()` — `GET /projects` 호출 후 `{projects: [...]}` 래퍼를 벗겨 `Project[]`로 매핑 (contract의 "GET /projects response is wrapped, not a bare array" 주의사항 반영)
- `createProject(title, description)` — `POST /projects`
- `getProject(projectId)` — `GET /projects/{id}`
- `updateProject(projectId, fields)` — `PATCH /projects/{id}`, `fields`에 담긴 키만 전송(부분 업데이트)
- `deleteProject(projectId)` — `DELETE /projects/{id}` (soft delete, trash로 이동된 프로젝트를 반환)

백엔드(T046-T050)가 다른 워크트리에서 동시 구현 중이라 실제 서버 없이, `apiClient`를 모킹해 contract 문서의 snake_case 응답 바디를 가정하고 테스트했습니다.

## 변경 파일
- `frontend/src/services/project-service.ts` (신규)
- `frontend/src/services/project-service.test.ts` (신규)

## TDD 결과
- RED 커밋: `f3bb46c` (test: project-service - RED (T053))
- GREEN 커밋: `6e15e7c` (feat: project-service - GREEN (T053))
- REFACTOR 커밋: 해당 없음
- 테스트: `npm test` 7 files / 28 tests 전부 통과 (project-service 5개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **`Project` 타입은 `frontend/src/types/project.ts`를 재사용**: T051에서 이미 분리해둔 공유 타입을 그대로 import — contract 문서가 제안한 모양과 동일하되, 중복 정의를 피함
- **`createProject`의 `description` 기본값을 `null`로**: contract 상 `description`은 `"..." | null`이라, CreateProjectModal(T052)이 빈 문자열을 보내든 Dashboard(T056)가 그걸 `null`로 변환해 보내든 어느 쪽이든 받을 수 있게 시그니처에 기본값을 둠

## 비고
- 백엔드 구현이 끝나면 실제 응답 바디가 contract 문서와 정확히 일치하는지(특히 `deletion_status`/`trashed_at`/`scheduled_deletion_at` 필드명) 한 번 더 확인이 필요합니다.
