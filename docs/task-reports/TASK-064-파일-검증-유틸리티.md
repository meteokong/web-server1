# TASK-064. 파일 검증 유틸리티 구현 (확장자/크기/바이너리)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/utils/file_validator.py`에 코드 업로드용 파일 검증 유틸리티 3종을 구현했다.
- `validate_extension(filename)`: 허용 확장자 화이트리스트(.py, .js, .ts, .jsx, .tsx, .html, .css, .java, .cpp, .c, .txt, .md) 검사. 대소문자 무관(`.JS` → `.js`로 정규화), 허용되지 않으면 `ValidationAppError`.
- `validate_size(size_bytes)`: 10MB(10,485,760바이트) 초과 시 `ValidationAppError`. 정확히 10MB는 허용(마이그레이션의 `<=` 제약과 일치).
- `is_binary(content)` / `validate_not_binary(content)`: null byte(`\x00`) 존재 여부로 바이너리 여부 판별. 실제 텍스트 소스 파일에는 null byte가 나타나지 않는다는 점을 이용한 저비용 휴리스틱.

세 함수 모두 `code_files`/`uploaded_code` 테이블의 `supported_extension`, `valid_upload_size` CHECK 제약(T009 마이그레이션)과 정확히 일치하도록 설계해, 잘못된 업로드가 DB의 raw `IntegrityError`가 아니라 서비스/API 레이어에서 명확한 400 에러로 먼저 걸러지도록 했다.

## 변경 파일
- `backend/src/utils/file_validator.py` (신규)
- `backend/tests/unit/test_file_validator.py` (신규, 21개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T064 체크)

## TDD 결과
- RED 커밋: 28266aa (test: file validation utilities - RED (T064))
- GREEN 커밋: e8af1d6 (feat: file validation utilities (extension/size/binary) - GREEN (T064))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 스위트 163 passed, src/utils/file_validator.py 100%

## 기술 결정
- 기존 서비스들(UserService, ProjectService)과 동일하게 `src.api.exceptions.ValidationAppError`를 재사용 — 파일 검증 실패도 비즈니스 규칙 위반의 일종이므로 전역 예외 핸들러가 동일한 `{"error": {...}}` 포맷으로 응답하게 됨. 별도의 전용 예외 클래스를 새로 만들지 않음.
- 바이너리 감지는 "magic number 기반 완전한 검증" 대신 null byte 휴리스틱을 선택 — research.md가 요구하는 수준(매직 넘버 감지)보다는 단순하지만, 허용 확장자가 모두 텍스트 기반 소스 코드(.py/.js/.html 등)이므로 이 휴리스틱으로 충분하고 외부 의존성이 없음. 추후 더 엄격한 검증이 필요해지면 `python-magic` 등으로 교체 가능하도록 함수 시그니처(`bytes` 입력)를 유지함.

## 비고
- 실제 멀티파트 업로드 요청에서 이 유틸리티들을 호출하는 지점은 T069(CodeUploadService)/T071(POST /projects/{id}/tasks 업로드 엔드포인트)에서 연결 예정 — 이번 task는 순수 함수 단위로만 구현.
- 로컬 venv 실행 시 `DATABASE_URL`/`REDIS_URL`을 `localhost` 기준으로 오버라이드 필요 (기존 비고와 동일한 환경 이슈 — 이 task 자체는 DB를 쓰지 않지만 전체 스위트 실행 시 필요).
