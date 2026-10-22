# TASK-065. 언어 감지 서비스 구현 (Pygments 기반)

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/code_analysis/language_detector.py`에 업로드된 코드 파일의 프로그래밍 언어를 감지하는 서비스를 구현했다.

- `detect_file_language(filename, content=b"")`: 파일 확장자 기반 1차 판별이 주 경로. `EXTENSION_TO_LANGUAGE`가 `file_validator.ALLOWED_EXTENSIONS`의 모든 확장자(.py/.js/.jsx/.ts/.tsx/.java/.cpp/.c/.html/.css/.txt/.md)를 `python`/`javascript`/`typescript`/`java`/`cpp`/`c`/`html`/`css`/`text`/`markdown`으로 정규화해 매핑한다. 확장자가 없거나 인식되지 않을 때만 Pygments 기반 content 분석으로 폴백한다.
- `detect_project_language(filenames)`: 업로드(폴더/다중 파일) 전체에서 가장 많이 등장한 언어를 다수결로 반환. `uploaded_code.detected_language` 컬럼에 저장될 값.
- `UNKNOWN_LANGUAGE = "unknown"`: 감지 실패 시 공통 반환값.

**Pygments 적용 방식 — 설계 변경 과정:** 처음에는 `pygments.lexers.guess_lexer(content)`(전체 500+ 렉서 대상 범용 추측)로 폴백을 구현했으나, 실제 실행 중 짧은 코드 스니펫에 대해 완전히 비결정적인 결과가 나오는 것을 확인했다 (예: 동일한 Python shebang 콘텐츠가 설치된 Pygments 버전에 따라 `Mojo`, `Tera Term macro` 등 무관한 렉서로 추측됨). 이는 단위 테스트를 플레이키하게 만들 뿐 아니라 운영 환경에서도 신뢰할 수 없는 동작이었다.

이를 `PythonLexer`, `JavascriptLexer`, `TypeScriptLexer`, `JavaLexer`, `CppLexer`, `CLexer`, `HtmlLexer`, `CssLexer` 8개로 후보를 우리가 지원하는 언어로 한정하고, 각 렉서의 `analyse_text(content)` 신뢼도 점수(0.0~1.0)를 직접 비교해 최고점이 임계값(0.1) 초과일 때만 채택하는 방식으로 교체했다.

**후속 수정 — 수동 검증 중 발견한 두 가지 결함:** Task 완료 후 사용자가 직접 확장자 없는 Python/JavaScript 샘플로 content 폴백을 테스트했고, JavaScript가 `unknown`으로 잘못 판별되는 것을 발견했다. 조사 결과 두 가지 근본 원인이 있었다:
1. `JavascriptLexer`/`TypeScriptLexer`/`JavaLexer`/`CssLexer`는 Pygments에 커스텀 `analyse_text`가 구현되어 있지 않아 **항상 0.0을 반환** — 애초에 이 4개 언어는 scoped 스코어링 방식으로도 절대 선택될 수 없었다.
2. `PythonLexer.analyse_text`는 `'import ' in text[:1000]`이라는 매우 광범위한 자체 휴리스틱을 가지고 있어, Java의 `import java.util.List;`처럼 "import "만 포함된 어떤 콘텐츠에도 **1.0을 반환**(거짓 양성).

해결: `javascript`/`typescript`/`java`/`css` 4개 언어에 대한 키워드 마커(정규식 패턴, 언어당 2개 이상 매칭 시 채택)를 추가하고, **키워드 마커 검사를 Pygments 스코어링보다 먼저 실행**하도록 순서를 바꿨다. TypeScript는 `interface`/타입 애너테이션 등 더 구체적인 패턴을 가지므로 JavaScript보다 먼저 검사한다.

## 변경 파일
- `backend/src/services/code_analysis/language_detector.py` (신규, 이후 키워드 폴백 추가로 수정)
- `backend/tests/unit/test_language_detector.py` (신규 23개 + 키워드 폴백 4개 테스트 추가, 총 27개)
- `specs/001-ai-code-learning-platform/tasks.md` (T065 체크)

## TDD 결과
- RED 커밋: b258f81 (test: language detection service (spec.md, research.md) - RED (T065))
- GREEN 커밋: d7074b7 (feat: language detection service using Pygments - GREEN (T065))
- RED 커밋(후속): f961a0c (test: javascript/typescript/java/css content-fallback detection - RED (T065))
- GREEN 커밋(후속): ec75b2b (fix: keyword-marker fallback for lexers without analyse_text - GREEN (T065))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `backend/tests/unit` 전체 117 passed, `src/services/code_analysis/language_detector.py` 100%

## 기술 결정
- **범용 `guess_lexer` 대신 범위를 한정한 `analyse_text` 스코어링을 선택**: Pygments의 전역 추측 함수는 500개 이상의 렉서를 대상으로 하여 짧은 스니펫에서 비결정적 결과를 낳는다. 반면 우리가 실제로 지원하는 8개 언어로 후보를 좁히고 각 렉서의 자체 신뢼도 점수를 직접 비교하면 테스트 가능하고 재현 가능한 동작을 얻는다.
- **키워드 마커를 Pygments 스코어링보다 먼저 검사**: `PythonLexer.analyse_text`의 "import " 전체 매칭 휴리스틱이 Java/JS 콘텐츠에 거짓 양성을 내므로, 더 구체적인 자체 키워드 패턴(언어별 2개 이상 매칭)을 먼저 확인해 Python의 과도하게 넓은 신호에 선점되지 않도록 했다.
- **content 폴백은 확장자 없는 파일에만 사용**: `.txt`/`.md`는 확장자만으로 `text`/`markdown`으로 충분히 판별되므로 content 폴백 후보에서 제외했다.
- **`detect_project_language`는 파일별 언어의 다수결**: 폴더 업로드처럼 여러 언어가 섞일 수 있는 입력에서 가장 흔한 언어 하나를 대표값으로 선택하는 단순한 규칙을 적용했다. `unknown`으로 판별된 파일은 다수결 집계에서 제외했다.

## 비고
- 이 서비스를 실제로 호출하는 지점은 T069(CodeUploadService)에서 연결될 예정 — 이번 task는 순수 함수 단위로만 구현했다.
- Pygments 버전 차이(전역 설치 2.21.0 vs 프로젝트 venv 2.18.0)에서 `guess_lexer`의 결과가 서로 달랐다는 점이, 애초에 전역 추측 방식을 폐기하고 스코어링 방식으로 전환한 직접적인 계기였다.
- 키워드 폴백 결함은 사용자가 요청한 수동 content 분석 테스트(확장자 없는 Python/JS 샘플) 중 발견됨 — 자동화된 단위 테스트만으로는 놓쳤던 실제 동작 차이였다.
