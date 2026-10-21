# TASK-014. FastAPI 앱 초기화 및 CORS 설정

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
지금까지 만든 부품들(DB 연결, JWT, 비밀번호 해싱)을 실제로 동작시킬 "건물 본체"인 FastAPI 앱을 만들었습니다. 비유하자면, 이제까지는 전기 배선(DB), 출입증 발급기(JWT), 금고(비밀번호 해싱)를 각각 준비했고, 이번에 그것들이 들어갈 건물의 현관문과 안내데스크(앱 인스턴스 + CORS)를 세운 것입니다. CORS는 "어느 주소에서 온 손님만 들여보낼지" 정하는 출입 규칙입니다 — 프론트엔드(`localhost:5173`)가 아닌 낯선 사이트가 이 API를 몰래 호출하지 못하게 막아줍니다.

**`backend/src/config.py` (신규, 앱 전역 설정)**:
- `AppSettings`: `.env.example`의 `ENVIRONMENT`, `DEBUG`, `ALLOWED_ORIGINS`를 읽는 pydantic-settings 클래스
- `cors_origins` 프로퍼티: `ALLOWED_ORIGINS="http://a.com,http://b.com"` 형태의 콤마 구분 문자열을 리스트로 변환 (공백/빈 값 제거)

**`backend/src/main.py` (신규, 앱 진입점)**:
- `FastAPI()` 앱 인스턴스 생성 (`debug` 플래그는 `AppSettings`에서 가져옴)
- `CORSMiddleware` 추가: `allow_origins`는 설정된 origin만, `allow_credentials=True`(쿠키 기반 인증을 쓸 예정이므로 필요), `allow_methods`/`allow_headers`는 전체 허용
- `GET /health`: 아직 라우터(T015)가 없는 상태에서 "앱이 정상적으로 떴는가"를 바로 확인할 수 있는 최소한의 엔드포인트

**검증**:
1. `fastapi.testclient.TestClient`로 작성한 통합 테스트 4개(`backend/tests/integration/test_main.py`):
   - `/health` 호출 → `{"status": "ok", "environment": "development"}` 정상 응답
   - 허용된 origin(`http://localhost:5173`)으로 요청 → `access-control-allow-origin` 헤더에 그대로 반영됨
   - 허용되지 않은 origin(`http://evil.example.com`)으로 요청 → CORS 헤더가 응답에 포함되지 않음(브라우저가 차단하게 됨)
   - Preflight(OPTIONS) 요청 → `access-control-allow-credentials: true` 확인
2. **실제 `uvicorn` 서버로 기동 테스트** (TestClient가 아닌 진짜 HTTP 서버): `uvicorn src.main:app --port 8123`로 백그라운드 구동 후 `curl`로 `/health` 호출 → 정상 응답 및 CORS 헤더 확인, 이후 프로세스 종료
3. 전체 테스트 스위트 재실행 → T012(8) + T013(7) + T014(4) = 19개 전부 통과
4. Ruff/Black 통과 확인

## 변경 파일
- `backend/src/config.py` (신규)
- `backend/src/main.py` (신규)
- `backend/tests/integration/test_main.py` (신규)
- `backend/tests/integration/__init__.py` (신규, 패키지 인식용)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 다만 CORS는 설정을 잘못하면 조용히 실패하거나 과도하게 허용되는 보안 민감 영역이라 판단해, `TestClient` 기반 통합 테스트 4개와 실제 `uvicorn` 기동 테스트까지 수행함.

## 기술 결정 (해당 시)
- `allow_credentials=True`로 설정 — research.md의 "JWT 토큰을 HTTPOnly 쿠키로 관리" 결정(access/refresh 토큰을 쿠키에 저장)과 맞물려, 브라우저가 쿠키를 포함한 요청을 보내려면 이 설정이 필요함
- 라우터(T015)와 전역 예외 처리(T016)는 아직 연결하지 않음 — 이번 Task 범위는 "앱 초기화 + CORS"로 한정하고, `/health`만 임시로 둠 (라우터가 생기면 유지하거나 `/api/v1/health`로 옮길 수 있음)
- `ENVIRONMENT`/`DEBUG`/`ALLOWED_ORIGINS`는 DB 설정(T011의 `db/config.py`)과 분리해 `src/config.py`에 둠 — 관심사를 DB 연결 설정과 앱 전역 설정으로 나눠 추후 혼동을 줄임

## 비고
- T015(API 라우터 구조)에서 실제 feature 라우터들을 이 `app`에 `include_router()`로 연결할 예정
- T016(에러 핸들링 미들웨어)에서 전역 예외 핸들러를 추가할 예정 — 지금은 FastAPI 기본 에러 응답만 동작함
- T193(Polish 단계, 요청 로깅 미들웨어)은 이번 Task 범위에 포함하지 않음 — tasks.md에 별도 Task로 명시되어 있어 중복을 피함
