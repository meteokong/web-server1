# TASK-052. CreateProjectModal 컴포넌트

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
새 프로젝트를 생성하는 모달 폼을 구현했습니다. `RegisterForm`(T032)과 동일한 상호작용 패턴(`isSubmitting`/`error` 로컬 상태, `onSubmit` prop에 위임, `role="alert"`로 에러 표시)을 따르면서, 열림/닫힘은 radix-ui의 `Dialog` 프리미티브로 처리합니다.

- `open={false}`이면 `role="dialog"` 자체가 DOM에 없음
- `open={true}`이면 제목/설명 입력 필드 + "생성"/"취소" 버튼 렌더링
- 제출 시 `onSubmit({ title, description })` 호출
- `onSubmit`이 reject하면 에러 메시지를 `role="alert"`로 표시(제출 버튼은 다시 활성화)
- "취소" 클릭 시 `onClose` 호출 (Dialog의 `onOpenChange(false)`로도 동일하게 연결)

## 변경 파일
- `frontend/src/components/project/CreateProjectModal.tsx` (신규)
- `frontend/src/components/project/CreateProjectModal.test.tsx` (신규)

## TDD 결과
- RED 커밋: `c019528` (test: CreateProjectModal - RED (T052))
- GREEN 커밋: `3d554bd` (feat: CreateProjectModal - GREEN (T052))
- REFACTOR 커밋: 해당 없음
- 테스트: `npm test` 6 files / 23 tests 전부 통과 (CreateProjectModal 5개 포함), `npm run lint` 클린(기존 button.tsx 경고 1건은 본 Task와 무관)

## 기술 결정 (해당 시)
- **모달 구현에 `radix-ui`의 `Dialog` 프리미티브 사용**: 프로젝트에 아직 shadcn `dialog.tsx` 래퍼가 없지만, `button.tsx`가 이미 `radix-ui`의 `Slot`을 직접 쓰는 것과 같은 방식으로 `Dialog` 네임스페이스를 직접 import해 사용 — 새 의존성 추가 없이 기존 패키지로 접근성(포커스 트랩, `role="dialog"`, ESC 닫힘 등)을 확보
- `title`/`description`은 string으로만 다루고 빈 문자열 → `null` 변환 등은 project-service(T053)/Dashboard(T056) 쪽 책임으로 남김 — 이 컴포넌트는 "입력값을 그대로 전달"만 담당

## 비고
- T056에서 Dashboard가 이 컴포넌트의 `onSubmit`을 `project-service.createProject`로 연결합니다.
