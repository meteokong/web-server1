# TASK-068. TaskService 구현 (생성/조회/수정/소프트 삭제 + task_number 자동 증가)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/task_service.py`에 `ProjectService`와 동일한 구조로 `TaskService`를 구현했다. Task는 `user_id` 컬럼이 없으므로(소유자 정보는 부모 Project에만 있음), 모든 조회/수정 메서드가 Task → Project 관계를 거쳐 소유권을 검증한다.

- `create(project_id, user_id, title, description=None, upload_method=None)`: 프로젝트 소유권 확인 → 제목 검증(5자 이상) → 해당 프로젝트의 현재 최대 `task_number`에 +1 한 값을 부여하여 생성.
- `get(task_id, user_id)`: Task를 가져오고, 그 Task가 속한 Project의 소유자와 `user_id`가 일치하는지 확인.
- `list_by_project(project_id, user_id)`: 프로젝트 소유권 확인 후, `deletion_status='active'`인 Task들을 `task_number` 오름차순으로 반환.
- `update(task_id, user_id, *, title=None, description=None)`: 주어진 필드만 부분 수정 (`ProjectService.update`와 동일 패턴).
- `soft_delete(task_id, user_id)`: `deletion_status='trashed'`, `trashed_at`/`scheduled_deletion_at`(+30일) 설정 — `ProjectService`와 동일한 휴지통 정책.

모든 "존재하지 않음"과 "존재하지만 내 것이 아님"은 동일하게 `NotFoundError`로 처리해 다른 사용자의 task_id 존재 여부를 추측할 수 없게 했다(`ProjectService`와 동일한 설계 근거).

## 변경 파일
- `backend/src/services/task_service.py` (신규)
- `backend/tests/integration/test_task_service.py` (신규, 20개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T068 체크)

## TDD 결과
- RED 커밋: ebf1528 (test: TaskService (create/get/list/update/soft-delete) - RED (T068))
- GREEN 커밋: b33c469 (feat: TaskService (create/get/list/update/soft-delete, task_number auto-increment) - GREEN (T068))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/services/task_service.py` 100%. 전체 백엔드 스위트 243 passed, 회귀 없음.

## 기술 결정
- **`task_number` 계산은 `SELECT MAX(task_number) WHERE project_id = ?` + 1**: data-model.md의 "Sequential number within project (immutable once assigned)" 요구사항을 가장 단순하게 만족. 동시 생성 시 경쟁 조건(race condition) 가능성이 있으나, 현재 스펙(단일 사용자가 자신의 프로젝트에 태스크를 순차 생성)에서는 발생 빈도가 매우 낮고, DB의 `unique_task_number_per_project` 제약이 있어 설령 경쟁이 발생해도 중복 삽입은 `IntegrityError`로 막힌다. 더 엄격한 직렬화(예: `SELECT ... FOR UPDATE`)는 과설계로 판단해 생략.
- **SQLAlchemy 매퍼 초기화 순서 이슈 수정**: `Task` 모델의 `uploaded_code` relationship은 문자열 이름(`"UploadedCode"`)으로 선언되어 있고(순환 임포트 방지를 위해 `TYPE_CHECKING`에서만 import), 이 이름은 SQLAlchemy가 매퍼를 구성(configure_mappers)하는 시점—즉 Task를 처음 쿼리하는 시점—에 해석된다. `TaskService`가 Task를 쿼리하는 첫 모듈이므로, `UploadedCode`/`CodeFile` 클래스가 그 시점까지 어디에서도 import되지 않으면 `InvalidRequestError`가 발생했다(실제로 GREEN 1차 구현에서 재현됨). `task_service.py` 상단에 두 모델을 `# noqa: F401`로 명시적으로 import해 매퍼 레지스트리에 등록시켜 해결했다.
- `list_by_project`에서도 자체적으로 소유권을 재검증하도록 구현(T070 API 레이어가 `ProjectService.get()`으로 먼저 검증하더라도) — 서비스 레이어 자체가 독립적으로 안전해야 한다는 `ProjectService`의 기존 설계 원칙을 그대로 따름.

## 비고
- `description`의 500자 제한(`description_max_length` CHECK)은 이번 task 범위에 포함하지 않음 — 브리프가 명시한 검증 범위(제목 5자 이상)만 구현했고, 초과 시 DB의 raw `IntegrityError`로 걸릴 수 있음. 추후 별도 task에서 `ProjectService`/`TaskService` 공통으로 길이 검증을 추가할 수 있음.
- 이 서비스는 T070-T074(Tasks API)와 T069(CodeUploadService)에서 바로 사용된다.
