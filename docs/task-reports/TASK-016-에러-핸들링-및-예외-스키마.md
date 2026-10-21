# TASK-016. 에러 핸들링 미들웨어 및 예외 스키마

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
API가 에러를 응답할 때 "매번 다른 모양"으로 돌아오지 않도록, 모든 에러 응답이 동일한 틀에 담겨 나가게 만들었습니다. 비유하자면, 병원의 각 과(인증과, 접수과, 진료과)가 각자 다른 양식의 진단서를 발급하면 환자가 헷갈리듯, API도 어디서 에러가 나든 프론트엔드가 항상 똑같은 모양(`{"error": {"code", "message", "details"}}`)으로 읽을 수 있게 통일했습니다.

**`backend/src/api/exceptions.py` 구현 내용**:
- `ErrorDetail`/`ErrorResponse` (Pydantic): 모든 에러 응답이 공통으로 따르는 스키마
- `AppError` 및 하위 클래스(`NotFoundError`, `ValidationAppError`, `UnauthorizedError`, `ForbiddenError`, `ConflictError`): 앞으로 서비스 코드 어디서든 `raise NotFoundError("task not found")`처럼 던지면 자동으로 올바른 HTTP 상태코드와 통일된 JSON으로 변환됨
- 4종류의 핸들러를 등록:
  1. `app_error_handler`: 위 `AppError` 계열 → 각 클래스가 정의한 상태코드/코드로 응답
  2. `http_exception_handler`: FastAPI 표준 `HTTPException`(예: `raise HTTPException(403, "...")`)도 같은 스키마로 통일
  3. `validation_exception_handler`: 요청 바디가 Pydantic 모델과 안 맞을 때(422) → `details`에 어떤 필드가 왜 잘못됐는지 포함
  4. `unhandled_exception_handler`: 예상 못한 에러(500) → 내부 메시지/스택트레이스를 절대 클라이언트에 노출하지 않고 고정된 안전한 메시지만 반환 (로깅은 T193에서 추가될 예정)
- `register_exception_handlers(app)`: 위 4개를 한 번에 등록하는 함수 — `main.py`에서 한 줄로 호출

**`backend/src/main.py` 수정**: `register_exception_handlers(app)` 호출 추가

**검증** (`backend/tests/unit/test_exceptions.py`, 5개, 모두 통과):
1. `AppError`(`NotFoundError`) → 404 + `{"error": {"code": "not_found", "message": ..., "details": {...}}}`
2. `HTTPException(403, ...)` → 403 + 동일 스키마로 통일됨
3. 필수 필드(`price`) 빠진 요청 → 422 + `details`에 `loc: ["body", "price"]` 포함 확인
4. 처리되지 않은 `RuntimeError` → 500 + 고정 메시지, **원본 에러 메시지("kaboom...")가 응답 어디에도 포함되지 않음**을 명시적으로 확인
5. 실제 운영 앱(`src.main.app`)에 핸들러가 등록돼 있는지 배선 확인

**실 서버 검증**: `uvicorn`으로 실제 서버를 띄워 존재하지 않는 경로 호출 → FastAPI 기본 응답(`{"detail":"Not Found"}`)이 아니라 통일된 스키마(`{"error":{"code":"http_error","message":"Not Found"}}`)로 나오는 것을 확인. `/health`가 여전히 정상 동작하는 것도 재확인.

전체 테스트 스위트 재실행 → 26개 전부 통과(이전 21개 + 이번 5개). Ruff/Black 통과.

## 변경 파일
- `backend/src/api/exceptions.py` (신규)
- `backend/src/main.py` (`register_exception_handlers(app)` 호출 추가)
- `backend/tests/unit/test_exceptions.py` (신규)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 에러 응답이 내부 정보를 유출하지 않는지는 보안과 직결되므로, 격리된 테스트용 앱으로 4가지 에러 경로(앱 에러/HTTP 예외/검증 에러/미처리 예외) 전부를 실제로 트리거해 응답 내용을 검증함.

## 기술 결정 (해당 시)
- `AppError`를 두어 서비스 레이어(T025 UserService 등)가 FastAPI/HTTPException에 직접 의존하지 않고도 적절한 HTTP 에러를 일으킬 수 있게 함 — 관심사 분리(비즈니스 로직 ↔ HTTP 계층)
- 500 에러 핸들러는 테스트에서 원본 예외 메시지가 응답에 전혀 포함되지 않음을 명시적으로 assert — 민감 정보(스택 트레이스, DB 쿼리 내용 등) 유출을 방지하는 constitution의 "Sensitive Data" 보안 요구사항과 일치
- 검증 에러(422)의 `details`는 FastAPI가 기본 제공하는 `exc.errors()` 형식을 그대로 노출(단, `jsonable_encoder`로 JSON 직렬화 안전하게 처리) — 프론트엔드가 필드별 에러를 표시하기 쉽도록 함
- 테스트는 운영 라우터(`api_router`)를 건드리지 않고, 테스트 전용 격리된 `FastAPI()` 앱에 동일한 `register_exception_handlers()`를 적용해 검증 — 실제 코드와 동일한 핸들러를 쓰면서도 운영 앱에 디버그용 라우트를 남기지 않음

## 비고
- 실제 서비스 코드(T025 UserService, T044 ProjectService 등)에서 `NotFoundError`/`ConflictError` 등을 활용해 발생시킬 예정 — 지금은 미들웨어/스키마 자체만 준비된 상태
- 500 에러 발생 시 실제 로깅(추적용)은 T193(요청 로깅 미들웨어)에서 추가될 예정 — 현재는 "유출하지 않는다"까지만 범위로 함
- 이로써 "Base Infrastructure" 섹션(T012~T016)이 모두 완료됨
