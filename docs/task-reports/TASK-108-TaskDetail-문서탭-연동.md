# TASK-108. TaskDetail 문서 탭에 DocumentViewer 연동

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/pages/TaskDetail.tsx`의 "문서" 탭(`<Tabs.Content value="document">`) placeholder(`아직 구현되지 않았습니다.`)를 실제 `DocumentViewer`(T105/T107)로 교체했다.
- `<DocumentViewer taskId={task.id} />`로 교체 — `task`는 이미 `useQuery(getTask)`로 조회되어 있던 값이라 `task.id`만 넘기면 끝. DocumentViewer가 상태 폴링/문서 조회/코드 조회를 전부 자체적으로 처리하므로 TaskDetail은 다른 추가 로직이 필요 없다.
- "연습"/"질의응답" 탭은 여전히 이전 placeholder 그대로 유지(각각 이후 Phase의 별도 태스크).

## 변경 파일
- `frontend/src/pages/TaskDetail.tsx` (수정 — document 탭에 `DocumentViewer` 연동)
- `frontend/src/pages/TaskDetail.test.tsx` (수정 — `@/components/document/DocumentViewer`를 `vi.mock`으로 스텁하고, 기존 "Document placeholder" 테스트를 "DocumentViewer가 taskId와 함께 렌더링되는지" 검증으로 교체)
- `specs/001-ai-code-learning-platform/tasks.md` (T108 체크)

## TDD 결과
- RED 커밋: 17fd9a5 (test: TaskDetail Document tab renders DocumentViewer - RED (T108))
- GREEN 커밋: f299f4f (feat: wire DocumentViewer into TaskDetail's Document tab - GREEN (T108))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `TaskDetail.test.tsx` 5/5 테스트 통과, 프론트엔드 전체 재실행 24 파일 109/109 테스트 통과(회귀 없음)

## 기술 결정
- `TaskDetail.test.tsx`에서 `DocumentViewer`를 `vi.mock`으로 얕게 스텁 — DocumentViewer 자체의 폴링/조회/Monaco 렌더링은 이미 T100~T107에서 각자 충분히 테스트됐으므로, TaskDetail 테스트는 "문서 탭에 올바른 `taskId`로 DocumentViewer가 꽂혀 있는지"만 검증하면 충분(단위 테스트 간 책임 분리, 불필요한 중복 목 설정 방지).
- 기존 "renders Document/Practice/Q&A tabs, defaulting to a Document placeholder" 테스트의 document 탭 관련 단언만 교체(연습/질의응답 탭 존재 확인은 그대로 유지) — T108이 명시적으로 요구한 변경(placeholder → 실제 컴포넌트)에 따른 의도된 업데이트.

## 비고
- T099~T108 10개 태스크 전체 완료. 남은 알려진 제약(코드 본문을 백엔드가 아직 내려주지 않는 문제)은 TASK-107 보고서에 기록해둠 — 백엔드가 content 필드를 추가하면 DocumentViewer의 `code` 계산부만 손보면 된다.
