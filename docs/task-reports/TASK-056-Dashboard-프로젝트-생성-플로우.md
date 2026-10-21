# TASK-056. Dashboard 프로젝트 생성 플로우 연결

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
T054에서 열리기만 하던 `CreateProjectModal`(T052)을 실제 생성 로직에 연결했습니다.

- `CreateProjectModal`의 `onSubmit`을 `useMutation`으로 감싼 `project-service.createProject`(T053) 호출로 교체
- 생성 성공 시: `queryClient.invalidateQueries({ queryKey: ["projects"] })`로 목록 쿼리를 무효화해 새 프로젝트가 수동 새로고침 없이 바로 보이게 하고, 모달을 닫음
- 모달에서 받은 `description`이 빈 문자열이면 `null`로 변환해 `createProject`에 전달(contract상 `description`은 `"..." | null`)

## 변경 파일
- `frontend/src/pages/Dashboard.tsx` (수정 — `useMutation`/`useQueryClient` 추가, `onSubmit` 스텁을 실제 mutation으로 교체)
- `frontend/src/pages/Dashboard.test.tsx` (수정 — 모달 오픈 확인 + "생성 → 목록에 반영 → 모달 닫힘" 전체 플로우 테스트 추가)

## TDD 결과
- RED 커밋: `341e469` (test: Dashboard project-creation flow - RED (T056))
- GREEN 커밋: `fe7e7e5` (feat: Dashboard project-creation flow - GREEN (T056))
- REFACTOR 커밋: 해당 없음
- 테스트: `npm test` 9 files / 39 tests 전부 통과 (Dashboard 7개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **`["projects"]`를 상수 `PROJECTS_QUERY_KEY`로 추출**: `useQuery`와 `invalidateQueries` 양쪽에서 똑같은 키 배열을 써야 하는데, 리터럴을 두 번 타이핑하면 나중에 한쪽만 바뀌는 실수가 날 수 있어 하나로 묶었습니다.
- **`onSubmit`이 `mutateAsync`를 그대로 반환**: `CreateProjectModal`은 `onSubmit`이 reject하면 에러를 보여주는 계약(T052)이므로, `mutateAsync`가 던지는 에러가 그대로 모달까지 전파되도록 감싸지 않고 그대로 반환했습니다. mutation 자체의 `retry: 0`은 `queryClient.ts`의 전역 설정을 그대로 따릅니다(중복 생성 방지).

## 비고
- 이로써 T051~T056(Phase 4 프로젝트 관리 UI 섹션) 전체 완료. `npm test` 9 files / 39 tests, `npm run lint` 클린 — 두 커맨드 모두 Task 완료 기준을 만족합니다.
