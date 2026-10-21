# TASK-059. 수동 브라우저 테스트: 프로젝트 제목 수정 → 저장 확인

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
테스트 진행 전 확인해 보니 `ProjectDetail` 페이지에는 제목 수정/삭제 UI가 전혀 없었다 (T051-T056 작업 범위에 "수정/삭제 UI 연결"이 포함되어 있지 않았음 — `project-service.ts`의 `updateProject`/`deleteProject` 함수(T053)만 있고 호출하는 화면이 없는 간극). 사용자 확인을 받아 TDD로 최소 UI(인라인 제목 수정 폼 + 삭제 버튼)를 `ProjectDetail.tsx`에 추가한 뒤 테스트를 진행했다.

브라우저에서 "제목 수정" 버튼 클릭 → 입력 필드에 "React 심화"로 교체 → "저장" 클릭까지 수행했고, 화면에 즉시 반영됨을 확인했다. 이어서 페이지를 새로고침해 서버에 실제로 저장되었는지(클라이언트 상태만 바뀐 게 아닌지) 검증했고, 새로고침 후에도 "React 심화"가 유지됨을 확인했다.

구현 중 추가로 발견한 버그: `onSuccess`에서 `queryClient.setQueryData(["projects", projectId], updated)`로 캐시를 갱신한 직후 `invalidateQueries({queryKey: ["projects"]})`를 호출했는데, 이 키가 prefix-match로 `["projects", projectId]`도 함께 무효화시켜 재조회를 유발 — 당시 테스트에서는 getProject 목이 옛 데이터를 반환하도록 되어 있어 방금 설정한 새 캐시를 덮어써 버렸다. `exact: true`를 주어 목록 쿼리(`["projects"]`)만 정확히 무효화하도록 수정했다.

## 변경 파일
- `frontend/src/pages/ProjectDetail.tsx` (인라인 제목 수정 폼 + 삭제 버튼 추가)
- `frontend/src/pages/ProjectDetail.test.tsx` (제목 수정/삭제 테스트 추가)
- `specs/001-ai-code-learning-platform/tasks.md` (T059 체크)

## TDD 결과
- RED 커밋: fd91a49 (test: ProjectDetail edit title / delete project - RED)
- GREEN 커밋: 7acee9f (feat: ProjectDetail edit title / delete project - GREEN)
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 프론트엔드 전체 스위트 41 passed, lint 클린 (기존 무관 warning 1개 제외)

## 기술 결정
- 새로운 전용 Edit 페이지 대신 상세 페이지 내 인라인 폼으로 최소 구현 — 범위를 "T059/T060 테스트를 수행할 수 있는 최소 UI"로 한정.
- `invalidateQueries`는 TanStack Query v5에서 기본적으로 prefix match이므로, 특정 쿼리 키만 정확히 겨냥할 때는 `exact: true`가 필요하다는 점을 코드 주석으로 남김.

## 비고
- UI 간극(수정/삭제 버튼 부재)은 별도 task 번호 없이 이번 task 수행 중 필요에 의해 추가한 것으로, tasks.md에 새 항목을 만들지 않고 T059/T060 완료의 전제 조건으로 처리했다.
