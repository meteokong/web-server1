# TASK-083. TaskDetail 페이지 스켈레톤 구현 (문서/연습/Q&A 탭)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/pages/TaskDetail.tsx`에 `:taskId` 라우트 파라미터로 태스크를 조회해 보여주는 페이지를 구현했다.
- `useQuery(["tasks", "detail", taskId])`로 `getTask(taskId)`(T080)를 호출. ProjectDetail(T055)과 동일한 로딩/에러 렌더링 컨벤션(`{isLoading && <p>로딩 중...</p>}`, `role="alert"`)을 사용.
- radix `Tabs`(`Tabs.Root`/`Tabs.List`/`Tabs.Trigger`/`Tabs.Content`)로 문서/연습/질의응답 3개 탭을 구성 — 각 탭은 "아직 구현되지 않았습니다." 플레이스홀더만 렌더링(실제 콘텐츠는 이후 태스크).
- `frontend/src/App.tsx`의 `/projects/:projectId/tasks/:taskId` 라우트가 가리키던 `PagePlaceholder`를 `<TaskDetail />`로 교체.

## 변경 파일
- `frontend/src/pages/TaskDetail.tsx` (신규)
- `frontend/src/pages/TaskDetail.test.tsx` (신규, 5개 테스트)
- `frontend/src/App.tsx` (수정 — PagePlaceholder를 TaskDetail로 교체)
- `specs/001-ai-code-learning-platform/tasks.md` (T083 체크)

## TDD 결과
- RED 커밋: d9c2e09 (test: TaskDetail page skeleton with tabs - RED (T083))
- GREEN 커밋: acf15e9 (feat: TaskDetail page skeleton with tabs - GREEN (T083))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 5/5 테스트 통과, 프론트엔드 전체 재실행 16 파일 74/74 테스트 통과(회귀 없음)

## 기술 결정
- `package.json`에 `radix-ui` 패키지가 이미 의존성으로 있고(CreateProjectModal/CreateTaskModal이 `Dialog` 네임스페이스로 사용 중), 동일 패키지의 `Tabs` 네임스페이스도 그대로 쓸 수 있어 별도 설치 없이 radix `Tabs`를 사용 — 브리프가 제시한 대안(로컬 state로 버튼 토글)보다 접근성(키보드 네비게이션, `role="tab"/"tabpanel"` 자동 부여)이 더 잘 갖춰짐.
- 3개 탭 모두 완전히 동일한 플레이스홀더 텍스트("아직 구현되지 않았습니다.")를 쓰도록 통일 — 테스트가 요구하는 수준(탭 전환 후 placeholder가 보이는지) 이상으로 탭별 문구를 차별화하지 않음(Green 단계 최소 구현 원칙).
- `getTask` 쿼리 키를 `["tasks", "detail", taskId]`로 둬서 ProjectDetail의 목록 쿼리 키(`["tasks", projectId]`)와 겹치지 않게 함 — 두 쿼리가 다른 프로젝트 ID/태스크 ID 조합을 캐시하면서 서로의 무효화 범위에 실수로 걸리지 않도록.

## 비고
- 문서/연습/Q&A 탭의 실제 데이터 연동(문서 생성 결과 조회, 연습 문제 풀이, Q&A 채팅)은 각각 이후 Phase의 별도 태스크 — 이번 작업은 레이아웃/라우팅 스켈레톤만 완성.
