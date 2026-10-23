# TASK-106. document-service (문서 조회 + 상태 폴링)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`frontend/src/services/document-service.ts`에 백엔드 문서 생성 API 2개를 호출하는 서비스를 구현했다.
- `getDocumentStatus(taskId)`: `GET /tasks/{id}/document/status`를 호출해 `{taskId, generationStatus, generationError, generationStartedAt, generationCompletedAt}`로 매핑. TanStack Query의 `refetchInterval`로 주기적으로 다시 호출하는 용도로 쓰도록 설계(실제 폴링 간격/중단 로직은 T107에서 `useQuery` 쪽에 둔다).
- `getDocument(taskId)`: `GET /tasks/{id}/document`를 호출해 `{taskId, generationStatus, generationError, content}`로 매핑. `content`는 7챕터 전체를 `task-service.ts` 패턴 그대로 snake_case → camelCase 변환(`toChapter2Concept`/`toChapter4Explanation`/`toChapter6Concept`/`toDocumentContent` 헬퍼). `generation_status`가 완료가 아니면 백엔드가 `content: null`을 주므로 그대로 `null`을 통과.
- 챕터3/5/7은 필드가 이미 단순(문자열/숫자/배열)하거나 변환이 필요한 필드가 없어 별도 헬퍼 없이 그대로 복사.

## 변경 파일
- `frontend/src/services/document-service.ts` (신규)
- `frontend/src/services/document-service.test.ts` (신규, 3개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T106 체크)

## TDD 결과
- RED 커밋: 016928e (test: document-service status/content fetch + snake_case mapping - RED (T106))
- GREEN 커밋: f19c2fb (feat: add document-service (status polling + 7-chapter document fetch) - GREEN (T106))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 신규 파일 3/3 테스트 통과, 프론트엔드 전체 재실행 24 파일 105/105 테스트 통과(회귀 없음)

## 기술 결정
- `task-service.ts`와 동일하게 `apiClient.get`을 `vi.mock`으로 대체해 네트워크 없이 매핑 로직만 검증 — 기존 서비스 테스트 컨벤션을 그대로 따름.
- `getDocumentStatus`/`getDocument`를 TanStack Query 훅으로 감싸지 않고 순수 비동기 함수로만 노출 — `task-service.ts`의 `getTask`/`listTasks`와 동일한 레이어 분리 원칙("서비스는 fetch만, useQuery 연결은 페이지/컴포넌트가 담당")을 유지. `refetchInterval` 기반 폴링은 T107에서 `DocumentViewer`나 `TaskDetail`이 `useQuery({queryFn: () => getDocumentStatus(taskId), refetchInterval: ...})` 형태로 직접 구성.

## 비고
- 폴링을 "completed/failed일 때 중단"하는 조건은 서비스 함수가 아니라 호출부(useQuery의 refetchInterval 콜백)의 책임 — T107에서 구현.
