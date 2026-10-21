# TASK-001. 프로젝트 디렉토리 구조 생성

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
plan.md에서 정의한 웹 애플리케이션 구조(백엔드 + 프론트엔드)에 맞춰 프로젝트 전체 디렉토리 뼈대를 생성했습니다. 비유하자면, 집을 짓기 전에 방마다 어떤 용도로 쓸지 미리 구획을 나눠두는 것과 같습니다. 아직 벽(코드)은 없지만, 어디에 무엇을 넣을지 자리는 다 마련된 상태입니다.

생성한 구조:
- `backend/src/`: `models`, `services/{auth, code_analysis, ai, document, practice, progress}`, `api`, `db`, `utils`
- `backend/tests/`: `contract`, `integration`, `unit`
- `frontend/src/`: `components/{auth, project, task, upload, document, practice, qa, progress}`, `pages`, `services`, `hooks`, `utils`
- `frontend/tests/`: `integration`, `unit`
- `storage/uploads/`: 업로드된 코드 파일 저장용 (기존에 있던 `storage/upload/`는 그대로 두고, spec에서 요구한 이름인 `uploads`를 새로 추가함)
- `docs/task-reports/`: 이미 존재하여 유지

## 변경 파일
- 신규 디렉토리만 생성 (코드 파일 없음, 빈 디렉토리이므로 git에는 아직 추적되지 않음)

## TDD 결과
해당 없음 (디렉토리 생성은 테스트 대상 로직이 없는 순수 구조 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음)

## 기술 결정 (해당 시)
- plan.md의 "Source Code (repository root)" 섹션에 명시된 구조를 그대로 따름
- 기존에 존재하던 `storage/upload/` (단수형, 빈 디렉토리)는 삭제하지 않고 `storage/uploads/` (복수형, spec 표준 명칭)를 별도로 생성함 — 추후 사용되지 않는 것이 확인되면 정리 가능

## 비고
- 저장소가 아직 git 저장소로 초기화되지 않은 상태라 커밋은 생성하지 않음
- 다음 Task(T002: 백엔드 Python 프로젝트 초기화)부터 실제 코드/설정 파일이 채워질 예정
