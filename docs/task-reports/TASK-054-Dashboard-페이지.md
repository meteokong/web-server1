# TASK-054. Dashboard 페이지 (프로젝트 목록)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
로그인한 사용자의 프로젝트 목록을 보여주는 `/` 경로의 Dashboard 페이지를 구현했습니다. `project-service.listProjects()`(T053)를 TanStack Query의 `useQuery`로 호출해 4가지 상태를 처리합니다.

- 로딩 중: "로딩 중..." 표시
- 에러: 에러 메시지를 `role="alert"`로 표시
- 빈 목록: "아직 프로젝트가 없습니다." 안내
- 목록 있음: 프로젝트마다 `ProjectCard`(T051) 렌더링

"새 프로젝트" 버튼을 누르면 `CreateProjectModal`(T052)이 열립니다. 이 Task에서는 모달의 `onSubmit`을 임시로 모달을 닫기만 하는 스텁으로 연결했고, 실제 `createProject` 호출 + 목록 갱신은 T056에서 연결합니다.

`App.tsx`의 `/` 경로 플레이스홀더를 이 Dashboard로 교체했습니다.

## 변경 파일
- `frontend/src/pages/Dashboard.tsx` (신규)
- `frontend/src/pages/Dashboard.test.tsx` (신규)
- `frontend/src/App.tsx` (수정 — `/` 경로를 `PagePlaceholder`에서 `Dashboard`로 교체)

## TDD 결과
- RED 커밋: `bb5351b` (test: Dashboard - RED (T054))
- GREEN 커밋: `a256d78` (feat: Dashboard - GREEN (T054))
- REFACTOR 커밋: 해당 없음
- 테스트: `npm test` 8 files / 33 tests 전부 통과 (Dashboard 5개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **생성 버튼의 `onSubmit`을 T054에서는 스텁으로 둠**: tasks.md가 "프로젝트 생성 플로우 연결"을 T056으로 명시적으로 분리해 두었으므로, 이 Task는 "목록 조회" 책임만 지도록 범위를 제한했습니다. 버튼과 모달 자체는 이미 렌더링되므로 T056에서는 `useMutation` 연결과 목록 캐시 무효화만 추가하면 됩니다.
- **`useQuery`의 `queryKey`를 `["projects"]`로 고정**: T056에서 생성 성공 시 `queryClient.invalidateQueries({ queryKey: ["projects"] })`로 이 캐시를 갱신할 수 있도록 미리 합의된 키를 사용했습니다.

## 비고
- 백엔드(T046-T050)가 아직 실행 중이 아니므로 실제 왕복 테스트는 T057 이후 수동 브라우저 테스트에서 재검증 필요(이 작업 범위 밖, 과제 지시사항에 따라 스킵).
