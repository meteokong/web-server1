# TASK-057. 수동 브라우저 테스트: 프로젝트 생성 → 대시보드 표시 확인

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
Claude-in-Chrome 확장을 통해 Playwright MCP 대체 수단으로 실제 브라우저에서 회원가입 → 로그인 → "새 프로젝트" 모달로 "React 학습" 프로젝트 생성까지 수행했다. 생성 직후 대시보드에 카드로 즉시 표시됨을 확인했다 (TanStack Query의 `invalidateQueries(["projects"])`에 의한 즉시 반영).

**테스트 중 치명적인 백엔드 버그를 발견 및 수정했다.** 신규 가입한 계정으로 즉시 로그인이 401로 실패하는 현상을 발견했고, 원인을 추적한 결과 `backend/src/db/session.py`의 `get_db()` FastAPI 의존성이 세션을 **한 번도 commit하지 않고** 닫기만 하는 버그였다. 모든 서비스 레이어(`UserService`, `TokenService`, `ProjectService` 등)는 테스트에서의 트랜잭션 격리를 위해 `flush()`만 호출하도록 설계되어 있었는데, 실제 운영/개발 서버에서는 이 flush가 요청이 끝나면 커밋 없이 롤백되어 **모든 쓰기 요청이 조용히 유실**되고 있었다. 기존 통합 테스트는 전부 `get_db`를 자체 `db_session` 픽스처로 오버라이드해서 호출하므로 이 버그를 한 번도 실행하지 않았다 (`src/db/session.py`의 get_db 본문 커버리지 0%로 확인).

## 변경 파일
- `backend/src/db/session.py` (get_db가 성공 시 commit, 예외 시 rollback하도록 수정)
- `backend/tests/integration/test_db_session.py` (신규 — get_db를 오버라이드하지 않고 실제 앱을 통해 register 후, 별도의 독립 커넥션으로 실제 커밋 여부를 검증하는 회귀 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T057 체크)

## TDD 결과
- RED 커밋: 321046f (test: get_db never commits, writes are lost outside tests - RED (bugfix))
- GREEN 커밋: 502deb5 (fix: get_db() never committed the session... (bugfix))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 122 passed. 이 수정으로 `src/db/session.py`의 get_db 본문도 처음으로 실행/커버됨.

## 기술 결정
- `get_db`를 `try/except`로 감싸 성공 시 `await session.commit()`, 예외 발생 시 `await session.rollback()` 후 재전파하도록 구현 — FastAPI 의존성의 표준 패턴.
- 회귀 테스트는 기존 `auth_client`/`db_session` 픽스처(의도적으로 `get_db`를 오버라이드함)를 쓰지 않고, 실제 `get_db`가 걸린 앱을 ASGITransport로 호출한 뒤 **완전히 독립된** 엔진/세션으로 결과를 검증하도록 작성 — 그래야 "커밋이 실제로 DB에 반영되었는가"를 제대로 증명할 수 있음.

## 비고
- 이 버그는 Projects 기능뿐 아니라 Phase 3에서 구현된 회원가입/로그인/로그아웃/토큰 재발급 등 **모든 쓰기 작업에 동일하게 영향**을 주고 있었다. 이전 Task Report들의 "GREEN/테스트 통과"는 모두 테스트 전용 픽스처 기준으로는 사실이었지만, 실제 서버 기동 시의 동작과는 달랐다.
- 버그 수정 후 로컬에서 실행 중이던 uvicorn 프로세스(코드 변경이 반영되지 않는 상태)를 재시작해 수정 사항을 반영했다.
- 테스트에 사용한 계정/프로젝트 데이터는 테스트 종료 후 DB에서 직접 정리했다.
