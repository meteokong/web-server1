# TASK-079. TaskCard 컴포넌트 구현 (태스크 타임라인 표시)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/components/task/TaskCard.tsx`에 ProjectDetail의 태스크 타임라인(T082)에서 쓰일 TaskCard를 구현했다. `ProjectCard.tsx`(T051)와 동일한 구조 — 데이터 패칭 없이 `{ task: Task }` prop만 받아 제목과 "Task {번호}" 라벨을 렌더링하고, `/projects/{projectId}/tasks/{id}`로 링크한다.

TaskCard가 의존하는 `Task` 프론트엔드 타입도 이번에 `frontend/src/types/task.ts`에 함께 정의했다(ProjectCard가 `types/project.ts`를 참조하는 것과 동일한 패턴) — task-service(T080)가 이 타입으로 매핑하는 서비스 레이어를 다음 태스크에서 완성할 예정.

## 변경 파일
- `frontend/src/types/task.ts` (신규)
- `frontend/src/components/task/TaskCard.tsx` (신규)
- `frontend/src/components/task/TaskCard.test.tsx` (신규, 2개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T079 체크)

## TDD 결과
- RED 커밋: a190b23 (test: TaskCard task display component - RED (T079))
- GREEN 커밋: 5d82979 (feat: TaskCard task display component - GREEN (T079))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 2/2 테스트 통과

## 기술 결정
- `Task` 타입은 data-model.md의 Task 엔티티(`id, project_id, task_number, title, description, upload_method, created_at, updated_at, deletion_status, trashed_at, scheduled_deletion_at`)를 camelCase로 그대로 옮긴 것 — ProjectCard/Project 타입과 동일한 분리 원칙(타입은 서비스 모듈과 독립된 파일에 둔다)을 따름.
- TaskCard 자체는 `description`, `uploadMethod` 등 나머지 필드를 사용하지 않음 — 현재 테스트가 제목과 태스크 번호만 요구하므로 과도한 렌더링을 추가하지 않음.

## 비고
- ProjectDetail(T082)에서 태스크 목록을 `listTasks(projectId)`로 받아 TaskCard로 매핑해 렌더링할 예정.
