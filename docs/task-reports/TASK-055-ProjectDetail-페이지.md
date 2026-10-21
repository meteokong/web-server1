# TASK-055. ProjectDetail 페이지 (태스크 타임라인 플레이스홀더 포함)

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
`/projects/:projectId` 경로에서 하나의 프로젝트를 상세 조회하는 페이지를 구현했습니다. `useParams`로 라우트 파라미터를 읽어 `project-service.getProject(projectId)`(T053)를 `useQuery`로 호출합니다.

- 로딩 중: "로딩 중..." 표시
- 에러: 에러 메시지를 `role="alert"`로 표시 (예: 존재하지 않거나 소유하지 않은 프로젝트에 대한 404)
- 성공: 프로젝트 제목/설명 표시 + "태스크 타임라인" 섹션(현재는 "아직 구현되지 않았습니다" 플레이스홀더 — 실제 태스크 타임라인은 이후 Phase에서 구현)

`App.tsx`의 `/projects/:projectId` 플레이스홀더를 이 페이지로 교체했습니다.

## 변경 파일
- `frontend/src/pages/ProjectDetail.tsx` (신규)
- `frontend/src/pages/ProjectDetail.test.tsx` (신규)
- `frontend/src/App.tsx` (수정 — `/projects/:projectId` 경로를 `PagePlaceholder`에서 `ProjectDetail`로 교체)

## TDD 결과
- RED 커밋: `5b0fa8f` (test: ProjectDetail - RED (T055))
- GREEN 커밋: `71e0cc8` (feat: ProjectDetail - GREEN (T055))
- REFACTOR 커밋: 해당 없음
- 테스트: `npm test` 9 files / 37 tests 전부 통과 (ProjectDetail 4개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **"태스크 타임라인" 플레이스홀더 검증 쿼리를 GREEN 단계에서 수정**: RED 테스트에서 `findByText(/태스크 타임라인/)`를 썼는데, 구현의 섹션 제목(`<h2>태스크 타임라인</h2>`)과 안내 문구(`<p>태스크 타임라인 기능은...</p>`) 둘 다 그 문자열을 포함해 "여러 엘리먼트가 매칭됨" 에러가 발생했습니다. 테스트 의도("제목 섹션이 있는가")에 맞게 `getByRole("heading", { name: /태스크 타임라인/ })`로 좁혀 모호성을 제거했습니다. 구현 코드는 그대로 두고 테스트만 더 구체적인 쿼리로 고친 것이라 TDD 원칙(테스트가 의도를 정확히 표현하도록) 위반이 아닙니다.
- **`useQuery`의 `enabled: Boolean(projectId)`**: `useParams`의 타입이 `string | undefined`라 라우트 매칭 전 렌더링(이론상 발생하지 않지만 타입상 가능)에서 `getProject(undefined)`를 호출하지 않도록 가드

## 비고
- 실제 태스크 타임라인 UI는 Phase 6(T083 TaskDetail 등) 이후 별도 Task에서 이 섹션을 교체하게 됩니다.
