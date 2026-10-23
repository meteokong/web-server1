# TASK-107. DocumentViewer 로딩 상태 + 진행 표시기

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`DocumentViewer`가 더 이상 `code`/`language`/`content`를 외부에서 주입받는 순수 표시 컴포넌트가 아니라, `taskId` 하나만 받아 문서 생성 상태를 폴링하고 완료되면 코드+문서를 직접 조회해 보여주도록 범위를 확장했다(브리프가 "document-service의 status 폴링을 활용해라"를 DocumentViewer의 책임으로 명시).
- `GET .../document/status`를 TanStack Query `useQuery`로 호출하고 `refetchInterval`에 새로 만든 `documentStatusPollIntervalMs(status)` 헬퍼(`document-service.ts`)를 연결: `pending`/`in_progress`면 4000ms마다 재호출, `completed`/`failed`(또는 아직 첫 응답 전인 `undefined`)면 `false`를 반환해 폴링을 멈춘다.
- 상태별 렌더링: `pending`/`in_progress` → `role="status"`로 "문서를 생성하는 중입니다..." 로딩 표시, `failed` → `role="alert"`로 `generationError` 메시지, `completed`가 되면 `GET .../document`(콘텐츠)와 `GET .../code`(업로드된 코드 메타데이터)를 각각 `useQuery`로 조회해 둘 다 준비되면 기존 T105의 2컬럼 + 스크롤 동기화 레이아웃(`TwoColumnDocument` 내부 컴포넌트로 보존)을 렌더링.
- **알려진 제약**: 백엔드의 `GET /tasks/{id}/code` 응답(`CodeFileResponse`)에는 파일명/경로/크기만 있고 실제 코드 본문(content) 필드가 없다(`backend/src/api/tasks.py:60-67` 확인). 원본 코드를 가져오는 별도 엔드포인트도 없어, CodePanel에는 실제 소스 대신 업로드된 파일명 목록(`files.map(f => f.fileName).join("\n")`)을 표시하도록 임시 처리했다 — 백엔드가 코드 본문을 내려주게 되면 이 부분만 교체하면 된다.

## 변경 파일
- `frontend/src/services/document-service.ts` (수정 — `documentStatusPollIntervalMs` 헬퍼 추가)
- `frontend/src/services/document-service.test.ts` (수정 — 헬퍼 테스트 3개 추가)
- `frontend/src/components/document/DocumentViewer.tsx` (수정 — `taskId` prop 기반 자체 데이터 조회 + 로딩/에러/진행 상태로 재설계)
- `frontend/src/components/document/DocumentViewer.test.tsx` (전면 재작성 — `taskId` 기반 통합 테스트 5개: pending/in_progress 로딩, failed 에러, completed 렌더링, 완료 후 스크롤 동기화)
- `specs/001-ai-code-learning-platform/tasks.md` (T107 체크)

## TDD 결과
- RED 커밋: d1baee6 (test: DocumentViewer loading/error/progress states + status poll interval - RED (T107))
- GREEN 커밋: d8ebe1c (feat: add DocumentViewer loading/error/progress states with status polling - GREEN (T107))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 수정 파일 전체 11/11(DocumentViewer 5 + document-service 추가분 3 + 기존분) 테스트 통과, 프론트엔드 전체 재실행 24 파일 109/109 테스트 통과(회귀 없음). `npx tsc -b`는 이 작업과 무관한 기존 `Dashboard.tsx`의 타입 에러 1건만 보고(내가 만든 파일들은 전부 타입 에러 없음).

## 기술 결정
- **DocumentViewer의 prop 계약을 T105(`code`/`language`/`content` 직접 전달)에서 T107(`taskId`만 전달, 내부에서 조회)로 바꾼 이유**: tasks.md가 "document-service의 status 폴링을 활용해라"를 DocumentViewer 자체의 요구사항으로 명시했고, 폴링 시작/중단과 완료 후 콘텐츠 로드는 한 군데(컴포넌트 내부)에서 응집력 있게 관리하는 게 TaskDetail(T108)을 단순한 `<DocumentViewer taskId={taskId} />` 호출 한 줄로 유지하는 데 유리하다고 판단. 기존 T105 테스트는 새 계약에 맞춰 재작성(순수 표시 테스트 → `taskId` 기반 통합 테스트)했고, 2컬럼 레이아웃/스크롤 동기화 로직 자체는 `TwoColumnDocument` 내부 컴포넌트로 그대로 보존해 동일한 비율 동기화 테스트를 완료 상태 이후 시나리오로 다시 검증했다.
- `documentStatusPollIntervalMs`를 순수 함수로 분리한 이유: `refetchInterval`에 들어가는 폴링 중단 조건(터미널 상태 판정)을 실제 타이머/네트워크 없이 단위 테스트로 검증하기 위함 — 컴포넌트 렌더링 테스트만으로는 "4초 뒤 재호출되는지"를 안정적으로 검증하기 어렵다.

## 비고
- 코드 본문 미제공 문제는 백엔드 영역이라 이번 작업에서 해결하지 않음 — 추후 `GET /tasks/{id}/code`가 파일 내용을 포함하게 되면 `DocumentViewer.tsx`의 `code` 계산 부분만 교체.
