# TASK-051. ProjectCard 컴포넌트

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
프로젝트 목록(Dashboard, T054)에서 한 프로젝트를 표시하는 순수 프레젠테이셔널 컴포넌트를 구현했습니다. `RegisterForm`(T032)과 동일한 패턴으로, 데이터를 어떻게 가져오는지는 전혀 모르고 `project: Project` prop만 받아 렌더링합니다.

- 제목(`project.title`)을 프로젝트 상세 페이지(`/projects/:id`, T055)로 가는 링크로 렌더링
- `project.description`이 있으면 그대로, `null`이면 "설명이 없습니다." 플레이스홀더 표시

## 변경 파일
- `frontend/src/components/project/ProjectCard.tsx` (신규)
- `frontend/src/components/project/ProjectCard.test.tsx` (신규)
- `frontend/src/types/project.ts` (신규) — contracts/projects-api.md의 "Frontend consumption" 절이 제안하는 `Project` 타입을 별도 모듈로 분리

## TDD 결과
- RED 커밋: `077f875` (test: ProjectCard - RED (T051))
- GREEN 커밋: `ff49869` (feat: ProjectCard - GREEN (T051))
- REFACTOR 커밋: 해당 없음 (최소 구현이 이미 단순해 리팩토링 불필요)
- 테스트: `npm test` 5 files / 18 tests 전부 통과 (ProjectCard 3개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **`Project` 타입을 `frontend/src/types/project.ts`로 분리**: contracts 문서는 이 타입을 `project-service.ts`(T053)에 두도록 제안하지만, T051(ProjectCard)과 T053(project-service)은 tasks.md상 `[P]`(병렬) 관계로 서로를 선행 조건으로 두면 안 됩니다. ProjectCard가 프로젝트의 "모양"만 알고 그걸 어떻게 가져오는지는 몰라야 한다는 프레젠테이셔널 컴포넌트 원칙에도 맞아, 타입을 독립 모듈로 꺼내 두 Task가 서로 의존하지 않게 했습니다. T053에서 `project-service.ts`가 이 타입을 import해서 그대로 사용합니다.

## 비고
- CreateProjectModal(T052)도 동일하게 `@/types/project`의 `Project`를 사용할 수 있습니다.
