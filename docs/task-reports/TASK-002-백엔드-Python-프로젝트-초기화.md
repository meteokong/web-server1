# TASK-002. 백엔드 Python 프로젝트 초기화

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
plan.md와 research.md에서 정한 기술 스택(FastAPI, SQLAlchemy 2.0, PostgreSQL, Celery, Redis, Gemini API 등)에 맞춰 `backend/requirements.txt`를 작성했습니다. 비유하자면, 요리를 시작하기 전에 레시피에 필요한 모든 재료 목록을 장바구니 목록으로 정리해 둔 것과 같습니다. 이 목록 하나만 있으면 누구든 똑같은 "주방"(개발 환경)을 그대로 재현할 수 있습니다.

포함된 주요 패키지:
- 웹 프레임워크: `fastapi`, `uvicorn[standard]`
- 데이터베이스: `sqlalchemy`, `asyncpg`, `alembic`
- 검증/설정: `pydantic`, `pydantic-settings`
- 인증/보안: `pyjwt`, `bcrypt`, `python-multipart`
- 백그라운드 작업: `celery`, `redis`
- AI 연동: `google-genai`, `httpx`
- 코드 분석: `pygments`
- 테스트: `pytest`, `pytest-asyncio`, `pytest-cov`
- 품질 도구: `ruff`, `black`

작성 후, 실제로 설치가 되는지 확인하기 위해 `backend/.venv`에 가상환경을 만들고 `pip install -r requirements.txt`를 실행했습니다. 모든 패키지가 충돌 없이 설치되었고, FastAPI/SQLAlchemy/Celery/Redis/Gemini 클라이언트 등 핵심 모듈이 정상적으로 import 되는 것을 확인했습니다.

## 변경 파일
- `backend/requirements.txt` (신규)
- `backend/.venv/` (검증용 가상환경, 로컬에만 존재 — 커밋 대상 아님)

## TDD 결과
해당 없음 (의존성 목록 작성 및 설치 검증은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 `pip install` 성공 + `import` 성공 여부로 "설치 가능성"을 검증함.

## 기술 결정 (해당 시)
- SQLAlchemy 비동기 드라이버로 `asyncpg`를 선택 (research.md 권장안)
- JWT 라이브러리로 `pyjwt` 선택 (경량, 표준 RFC 7519 구현)
- Gemini API 클라이언트로 공식 `google-genai` SDK 사용
- 버전은 2026-10 기준 안정적으로 설치 가능한 최신 패치 버전으로 고정(pin)하여 재현성 확보

## 비고
- 아직 git 저장소가 초기화되지 않아 커밋은 생성하지 않음
- `.gitignore`(T007)가 아직 없으므로, 추후 git 초기화 시 `.venv/`, `__pycache__/` 등을 반드시 무시 패턴에 포함해야 함
- 다음 Task(T003: 프론트엔드 Vite/React 초기화)로 이어감
