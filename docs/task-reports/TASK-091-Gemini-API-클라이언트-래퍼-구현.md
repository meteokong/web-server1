# TASK-091. Gemini API 클라이언트 래퍼 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/ai/gemini_client.py`에 `google-genai` SDK(0.3.0, `google.genai.Client`)를 감싸는 `GeminiClient` 래퍼를 구현했다. `GOOGLE_API_KEY`/`gemini_model`(기본값 `gemini-3-flash-preview`, research.md 결정사항)은 `GeminiSettings`(pydantic-settings, 프로젝트 루트 `.env` 로드)로 관리하며, 기존 `JWTSettings`/`DatabaseSettings` 패턴을 그대로 따랐다. `generate_content(prompt, *, system_instruction=None, response_mime_type=None)` 단일 호출 지점만 외부에 노출하고, `system_instruction`/`response_mime_type="application/json"`(T092/T093의 7챕터 구조화 출력용 JSON 모드)을 설정하면 `types.GenerateContentConfig`를 구성해 전달한다. SDK의 `google.genai.errors.APIError`는 `GeminiAPIError`(code/message 보존)로, API 키 누락은 `GeminiConfigError`로 번역해 호출자가 SDK를 직접 import하지 않도록 했다.

## 변경 파일
- `backend/src/services/ai/gemini_client.py` (신규)
- `backend/tests/unit/test_gemini_client.py` (신규)
- `specs/001-ai-code-learning-platform/tasks.md` (T091 체크)

## TDD 결과
- RED 커밋: 0e29724 (test: Gemini API client wrapper config/request/error handling - RED (T091))
- GREEN 커밋: 3e4e3cb (feat: add Gemini API client wrapper with config/JSON-mode/error handling - GREEN (T091))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: 전체 백엔드 unit 스위트 159 passed (신규 5개 테스트는 실제 네트워크 호출 없이 `google.genai.Client`를 fake 객체로 주입해 검증). 추가로 `.env`의 실제 `GOOGLE_API_KEY`로 `GeminiClient().generate_content(...)`를 1회 호출해 실제 Gemini API 연동도 수동으로 확인함 (응답: "OK").

## 기술 결정
- **재시도(backoff) 로직은 이 래퍼에 두지 않음**: research.md는 "Exponential backoff up to 3 retries"를 요구하지만, 이는 호출자(T093 DocumentGenerationService)마다 다른 정책이 필요하므로(문서 생성은 최대 3회 재시도, Q&A는 빠른 실패가 나을 수 있음) 래퍼는 `GeminiAPIError`만 던지고 재시도 정책은 상위 서비스가 결정하도록 분리했다.
- **요청 단위 timeout 미구현**: research.md는 "20s for Q&A, 3min for documents" 타임아웃을 요구하지만, 설치된 `google-genai==0.3.0`(preview SDK)의 `HttpOptions`에는 `base_url`/`api_version`/`headers`/`response_payload`만 있고 timeout 필드가 없어 이번 버전에서는 지원 불가. 추후 SDK 업그레이드 시 추가 필요 (비고에도 기록).
- 테스트에서 `GeminiClient(client=...)` 생성자 파라미터로 실제 SDK 클라이언트를 주입할 수 있게 해, monkeypatch 없이도 네트워크 호출 없는 단위 테스트가 가능하도록 설계.
- `GOOGLE_API_KEY`가 비어있으면 `genai.Client` 생성 시점이 아니라 `GeminiClient.__init__`에서 즉시 `GeminiConfigError`를 던져 fail-fast 하도록 함.

## 비고
- `google-genai==0.3.0`은 `requirements.txt`에 이미 포함되어 있었고 venv에도 설치되어 있어 별도 설치 작업은 불필요했음.
- `.env`의 `GOOGLE_API_KEY`가 유효하며 실제 `gemini-3-flash-preview` 모델 호출이 정상 동작함을 확인함 (사용자 요청에 따라 수동 스모크 테스트 수행).
- SDK 버전이 timeout을 지원하게 되면 `generate_content`에 `timeout_seconds` 파라미터를 추가해야 함 — 지금은 추가하지 않음(미지원 기능을 흉내 내는 코드를 만들지 않기 위함).
