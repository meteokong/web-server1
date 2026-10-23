# TASK-BUGFIX. Celery 워커 SQLAlchemy mapper 설정 오류 수정

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
전체 플로우 E2E 테스트(backend uvicorn + Celery worker + frontend 로컬 실행) 중, 실제 코드 업로드 → 문서 생성 트리거 단계에서 Celery 워커가 매 태스크마다 `sqlalchemy.exc.InvalidRequestError: ... expression 'User' failed to locate a name ('User')`로 죽는 것을 발견했다. 원인은 `Task.project → Project.user` 관계가 문자열(`Mapped["User"]`)로 선언되어 있는데, 실제 `celery -A src.tasks.celery_app worker` 프로세스는 `src.tasks.document_generation` → `DocumentGenerationService` → `TaskService`(Project/CodeFile/UploadedCode만 import)까지만 import하고 `User` 모델은 그 체인에서 전혀 import되지 않아, SQLAlchemy가 최초로 mapper를 구성하는 시점(최초 쿼리)에 `User`라는 이름을 찾지 못해 터지는 것이었다. pytest 전체 스위트에서는 수백 개 테스트 파일이 누적으로 모든 모델을 import해두기 때문에 이 버그가 가려져 있었다 — 즉 **기존 테스트로는 잡을 수 없는 버그**였고, 실제 서비스를 띄워서 E2E 테스트를 해봐야만 드러나는 문제였다. `backend/src/models/__init__.py`(기존에 비어 있던 파일)에 7개 모델 클래스를 전부 import하도록 채워서, `src.models.*` 아래 어떤 서브모듈이든 한 번만 import되면(Python이 서브모듈 import 전에 항상 패키지 `__init__.py`를 먼저 실행하므로) 그 시점에 모든 모델이 레지스트리에 등록되도록 중앙에서 해결했다.

## 변경 파일
- `backend/src/models/__init__.py` (빈 파일 → 7개 모델 전부 import)
- `backend/tests/unit/test_celery_worker_import_isolation.py` (신규, 회귀 테스트)

## TDD 결과
- RED 커밋: 776ba30 (test: Celery worker's isolated import graph must configure mappers cleanly - RED)
- GREEN 커밋: 6348d1f (fix: register all model classes on package import so mapper config survives a narrow import graph - GREEN)
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 345 passed (기존 344 + 신규 회귀 테스트 1개), ruff clean. 신규 테스트는 pytest 프로세스 내부에서 재현되지 않는 버그 특성상 **서브프로세스를 띄워** 실제 Celery 워커와 동일한(좁은) import 그래프를 재현하는 방식으로 작성 — `subprocess.run([sys.executable, "-c", "import src.tasks.document_generation; ...configure_mappers()"])`의 returncode를 검증.
- 수정 후 실제 Celery 워커를 재시작해 실제 문서 생성 태스크가 에러 없이 처리되는 것으로 재확인(아래 비고).

## 기술 결정
- **중앙 집중식 수정(`src/models/__init__.py`)을 선택**, `document_generation.py`에 `# noqa: F401` import들을 추가하는 방식(T090/T093 당시 수동 검증 스크립트에서 썼던 임시 우회법)은 선택하지 않음 — 그 방식은 이번에 터진 지점만 막을 뿐, Celery에 새 태스크 모듈이 추가될 때마다(T118 practice, T172 trash 등) 똑같은 버그가 다시 생길 수 있는 구조적 문제를 전혀 해결하지 못함. `src/models/__init__.py`를 고치면 **어떤 진입점(FastAPI, Celery, 스크립트, 새 태스크)이든 모델을 하나라도 import하는 순간 전부 등록**되므로 근본 원인을 없앤다.
- 회귀 테스트를 pytest 프로세스 안에서 직접 재현하지 않고 **서브프로세스로 격리**한 이유: 같은 pytest 프로세스 안에서는 다른 테스트 파일들이 이미 모든 모델을 import해둔 상태라 버그가 재현되지 않는다(이게 애초에 이 버그가 기존 테스트망을 통과했던 이유). 실제 Celery 워커의 "좁은 import" 조건을 그대로 재현하려면 신선한 프로세스가 필요했다.

## 비고
- 이 버그는 코드 리뷰나 유닛/통합 테스트만으로는 발견되지 않았고, **실제로 uvicorn+Celery worker+frontend를 모두 띄워 브라우저로 전체 플로우를 타보는 E2E 테스트** 중에 Celery 워커 로그를 확인하다가 발견했다 — 왜 E2E 테스트가 필요한지 보여주는 사례.
- 같은 이유로, 이전 태스크(T090/T093)에서 로컬 스크립트로 수동 검증할 때도 동일한 증상을 겪어 그때는 스크립트에 임시로 `# noqa: F401` import를 추가해 우회했는데, 이번에 근본 원인을 고쳤으므로 앞으로는 그런 우회가 필요 없다.
