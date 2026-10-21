# TASK-020. axios 기반 API 클라이언트 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
프론트엔드가 백엔드와 통신할 때마다 매번 "주소는 어디고, 쿠키는 보내야 하고, 에러는 이런 모양으로 와..."를 반복해서 설정하지 않도록, 공통 통신 창구(`apiClient`)를 하나 만들었습니다. 비유하자면, 매번 다른 번호로 전화를 걸어 처음부터 신원 확인하는 대신, 회사 대표 전화(axios 인스턴스)로 걸면 자동으로 사원증(쿠키)을 제시하고, 상담원이 뭐라고 답하든 항상 같은 양식의 메모(`ApiError`)로 정리해서 건네주는 시스템입니다.

**구현 내용**:
- `frontend/src/services/api-client.ts`:
  - `apiClient = axios.create(...)`: `baseURL`은 `VITE_API_BASE_URL` 환경변수(기본값 `http://localhost:8000/api/v1`)에서 읽음
  - `withCredentials: true` — research.md의 "JWT를 HTTPOnly 쿠키로 관리" 설계에 맞춰, 모든 요청에 쿠키가 자동으로 포함되도록 함
  - `ApiError` 클래스 + 응답 인터셉터: 백엔드(T016)의 통일된 에러 스키마(`{"error": {"code", "message", "details"}}`)를 그대로 `ApiError` 인스턴스로 변환 — 서비스 코드에서 `catch (err) { if (err instanceof ApiError) ... }` 형태로 일관되게 처리 가능
- `frontend/src/vite-env.d.ts` (신규): `VITE_API_BASE_URL`에 대한 타입 선언 추가 (자동완성/타입 안정성)
- `frontend/vite.config.ts`: `envDir: ".."` 추가 — Vite가 `frontend/.env`가 아니라 **프로젝트 루트의 `.env`**를 읽도록 설정 (quickstart.md가 전제하는 "프로젝트 루트에 단 하나의 `.env`" 구조와 일치시킴)
- `.env`/`.env.example`에 `VITE_API_BASE_URL=http://localhost:8000/api/v1` 추가

**검증 (실제 백엔드로 종단 간 테스트)**:
TypeScript 모듈이라 Node에서 직접 실행하기 어려워, `api-client.ts`와 동일한 인터셉터 로직을 임시 스크립트로 복제해 **실제로 띄운 백엔드 서버**(T014 FastAPI 앱, 포트 8000)에 대해 검증함:
1. `GET /health` → `baseURL` 설정이 올바르게 백엔드에 연결됨 확인 (`status: 200`)
2. `GET /this-does-not-exist` → 백엔드의 T016 전역 에러 핸들러가 반환한 `{"error":{"code":"http_error","message":"Not Found"}}`가 `ApiError` 인스턴스로 정확히 매핑됨 확인 (`err.status=404, err.code="http_error", err.message="Not Found"`)
3. `Origin: http://localhost:5173` 헤더로 요청 → `access-control-allow-origin`/`access-control-allow-credentials: true` 응답 헤더 확인 (T014 CORS 설정과 `withCredentials: true`가 실제로 호환됨)
검증 후 임시 스크립트 삭제, 백엔드 프로세스 종료.

추가로 `npm run build`(TypeScript 컴파일 포함)/`lint`/`format:check` 모두 통과 확인.

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (`axios` 추가)
- `frontend/src/services/api-client.ts` (신규)
- `frontend/src/vite-env.d.ts` (신규)
- `frontend/vite.config.ts` (`envDir: ".."` 추가)
- `.env`, `.env.example` (`VITE_API_BASE_URL` 추가)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 아직 프론트엔드에 Vitest 등 테스트 러너가 설치되지 않아(T018 보고서에서도 동일하게 명시) 정식 단위 테스트 파일은 작성하지 않았고, 대신 실제 백엔드 서버를 띄운 상태에서 동일한 로직을 재현해 end-to-end로 검증함.

## 기술 결정 (해당 시)
- `envDir: ".."`를 설정해 백엔드와 프론트엔드가 **하나의 `.env` 파일**을 공유하도록 함 — quickstart.md의 "Create `.env` file in project root" 안내와 일치시키기 위한 결정 (각 앱마다 별도 `.env`를 두면 문서와 실제 구조가 어긋남)
- 에러를 `Promise.reject(new ApiError(...))`로 변환해 axios의 원본 `AxiosError`를 서비스 코드에 그대로 노출하지 않음 — 프론트엔드 서비스 레이어가 axios의 세부 구현(어느 필드가 에러 응답을 담는지 등)에 의존하지 않고, 백엔드가 보내는 `code`/`message`/`details`에만 집중할 수 있게 함
- 아직 401 응답 시 자동 토큰 갱신 로직은 넣지 않음 — 그건 T038("Implement auto token refresh logic in frontend/src/hooks/useAuth.ts")의 명시적 범위이며, 이번 Task는 "기본 axios 설정"까지로 한정함

## 비고
- `baseURL` 기본값(`http://localhost:8000/api/v1`)은 quickstart.md의 "Backend on port 8000" 안내와 백엔드 T015의 `/api/v1` prefix에 맞춤
- 이 클라이언트를 사용하는 실제 서비스 함수들(`auth-service.ts`, `project-service.ts` 등)은 T034, T053 등에서 작성될 예정
- T019에서 추가했던 TanStack Query 테스트용 임시 컴포넌트(`_QueryTest.tsx`)와 `/query-test` 라우트는 사용자 확인 대기 중이며 이번 Task에서는 건드리지 않음
