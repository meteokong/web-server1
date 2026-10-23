# TASK-067. 파일 저장 서비스 구현 (업로드 파일 디스크 저장)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/code_analysis/file_storage.py`에 업로드된 코드 파일 내용을 디스크에 저장하는 `save_uploaded_file(user_id, task_id, relative_path, content, *, upload_root=None)` 함수를 구현했다.

- 저장 경로: `{upload_root}/{user_id}/{task_id}/{relative_path}` (프로젝트 루트 기준 `storage/uploads`가 기본값, `.env.example`의 `UPLOAD_DIR`).
- 필요한 중간 디렉토리는 `Path.mkdir(parents=True, exist_ok=True)`로 자동 생성 — 폴더 업로드의 하위 경로도 그대로 지원.
- 반환값은 실제로 기록된 파일의 절대 경로(문자열) — `CodeFile.storage_path`에 그대로 저장될 값.
- **보안(Path Traversal 방지)**: `relative_path`는 멀티파트 업로드 요청에서 오는 사용자 입력이므로, `_validate_relative_path`가 다음을 모두 거부한다(`ValidationAppError`):
  - 빈 문자열/공백만 있는 경로
  - `..` 세그먼트를 포함하는 경로 (상위 디렉토리 탈출)
  - POSIX 절대 경로(`/etc/passwd`)
  - Windows 드라이브 절대 경로(`C:/...`, `C:\...`)
  - 백슬래시(`\`)는 슬래시(`/`)로 정규화한 뒤 검사하므로 Windows 스타일 경로도 동일하게 걸러짐.

설정은 `src/config.py`에 `DatabaseSettings`와 동일한 패턴(`BaseSettings` + `lru_cache`)으로 `StorageSettings`(`upload_dir` 환경변수, 기본값 `./storage/uploads`)를 추가했고, `upload_root` 프로퍼티가 상대 경로를 프로젝트 루트 기준 절대 경로로 변환한다.

## 변경 파일
- `backend/src/services/code_analysis/file_storage.py` (신규)
- `backend/src/config.py` (수정 — `StorageSettings`/`get_storage_settings` 추가)
- `backend/tests/unit/test_file_storage.py` (신규, 11개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T067 체크)

## TDD 결과
- RED 커밋: d230e8d (test: file storage service (T067) - RED (T067))
- GREEN 커밋: 48fcaa6 (feat: file storage service (path-traversal safe upload save) - GREEN (T067))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `src/services/code_analysis/file_storage.py` 100%. 전체 백엔드 스위트 223 passed, 회귀 없음.

## 기술 결정
- **경로 안전성은 `resolve()` 후 재검증이 아니라 경로 파싱 단계에서만 검증**: 처음에는 `task_dir.resolve()`와 `target.resolve()`를 비교하는 방어적 2차 검증도 넣었으나, `_validate_relative_path`가 이미 `..` 세그먼트와 절대 경로를 전부 차단하므로 그 2차 검증은 테스트로 도달 불가능한 데드 코드였다. "최소한의 코드로 테스트를 통과시킨다"는 Green 단계 원칙에 따라 제거하고, 경로 파싱 단계의 검증 하나로 100% 커버리지를 달성했다.
- **테스트는 전부 `upload_root`를 명시적으로 주입**(pytest `tmp_path`): 실제 `storage/uploads`를 오염시키지 않기 위함. 운영 코드에서는 `upload_root`를 생략하면 `get_storage_settings().upload_root`(환경변수 `UPLOAD_DIR` 기반)가 기본값으로 쓰인다 — 한 테스트(`test_save_uploaded_file_defaults_to_configured_upload_root`)에서만 `monkeypatch.setenv` + `get_storage_settings.cache_clear()`로 이 기본 경로 로직도 검증했다.
- `StorageSettings`를 `AppSettings`/`DatabaseSettings`와 같은 파일(`src/config.py`)에 둠 — 별도 모듈로 분리할 만큼 복잡하지 않고, 기존 설정 클래스들과 같은 `_PROJECT_ROOT`/`_ENV_FILE` 상수를 재사용하기 위함.

## 비고
- 이 서비스를 실제로 호출하는 지점은 T069(CodeUploadService)에서 연결된다 — 이번 task는 순수 파일 I/O 함수 단위로만 구현.
- `CodeUploadService`가 테스트에서 실제 디스크를 오염시키지 않도록, `save_uploaded_file`의 `upload_root` 키워드 인자를 그대로 상위 서비스 생성자에 흘려보낼 수 있도록 시그니처를 설계했다.
