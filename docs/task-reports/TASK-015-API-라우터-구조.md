# TASK-015. API 라우터 구조 (/api/v1)

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
앞으로 만들어질 인증, 프로젝트, 태스크 등 모든 API 엔드포인트가 모일 "우편함"을 만들었습니다. 비유하자면, 건물(FastAPI 앱)에 아직 각 부서(인증과, 프로젝트과, ...)는 입주하지 않았지만, 모든 부서로 가는 우편물이 공통으로 거쳐가는 1층 중앙 우편실(`/api/v1`)을 먼저 만들어 둔 것입니다. 나중에 각 부서(T028 인증, T046 프로젝트 등)가 생기면 이 우편실에 자기 사서함만 등록하면 됩니다.

**구현 내용**:
- `backend/src/api/router.py`: `api_router = APIRouter(prefix="/api/v1")` — 아직 아무 feature 라우터도 등록되지 않은 빈 라우터. 주석으로 앞으로 각 feature 라우터(auth, projects, ...)를 어떻게 등록할지 예시를 남겨둠
- `backend/src/main.py` 수정: `app.include_router(api_router)` 추가 — T014에서 만든 앱에 이 라우터를 실제로 연결

**검증 (실제 동작 확인)**:
1. 구조 검증: `api_router`가 `APIRouter` 인스턴스이고 `prefix == "/api/v1"`인지 확인
2. **배선 검증** (`backend/tests/unit/test_router.py::test_app_mounts_api_router_at_v1_prefix`): `api_router.prefix`가 맞아도 `main.py`에서 `include_router()` 호출을 빠뜨리거나 오타가 나면 실제로는 연결이 안 될 수 있음 → 테스트 중에만 임시 라우트(`/_router_wiring_smoke_test`)를 `api_router`에 등록하고 `importlib.reload()`로 `main.py`를 재실행시켜, 실제로 `/api/v1/_router_wiring_smoke_test`에서 응답이 오는지 확인 → 테스트 종료 시 임시 라우트를 제거하고 `main.py`를 원상 복구
3. 전체 테스트 스위트 재실행 → 21개 전부 통과 (이전 19개 + 이번 2개), 임시 라우트 추가/제거가 다른 테스트에 영향을 주지 않는지도 확인됨
4. Ruff/Black 통과 확인

## 변경 파일
- `backend/src/api/router.py` (신규)
- `backend/src/api/__init__.py` (신규, 패키지 인식용)
- `backend/src/main.py` (`api_router` import 및 `include_router()` 호출 추가)
- `backend/tests/unit/test_router.py` (신규)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 "라우터 prefix는 맞는데 실제로는 연결 안 됨" 같은 흔한 실수를 잡기 위해, 라우터 객체의 정적 속성뿐 아니라 `main.py`와의 실제 배선까지 통합 테스트로 검증함.

## 기술 결정 (해당 시)
- 등록은 `router.py` 한 곳에서만 이뤄지도록 설계 — `main.py`는 `api_router` 하나만 알면 되고, 개별 feature 라우터의 존재는 몰라도 됨(관심사 분리). plan.md의 "api/ # REST/GraphQL API endpoints" 구조와 일치
- 테스트에서 실제 라우터 싱글턴에 임시 라우트를 추가하는 방식을 택함 — `include_router()`가 호출 시점의 라우트 목록을 복사하는 FastAPI의 동작 특성상, 이 방법이 "연결이 실제로 되는가"를 가장 직접적으로 검증할 수 있음. 테스트 종료 시 반드시 라우트를 제거하고 `main.py`를 재로드해 다른 테스트에 영향이 없도록 함(실제로 전체 스위트 재실행으로 확인함)

## 비고
- 아직 어떤 feature 라우터도 등록되지 않음 — T028(인증), T046(프로젝트), T070(태스크), T097(문서), T120(연습문제), T136(Q&A), T154(진행률), T173(휴지통) 등에서 각자의 `APIRouter`를 만들어 이 파일에 `include_router()`로 추가할 예정
- `/health`는 여전히 `/api/v1` 밖(`main.py`에 직접 정의됨)에 있음 — 헬스체크는 보통 버전 prefix 없이 노출하는 것이 일반적인 관례라 그대로 유지함
