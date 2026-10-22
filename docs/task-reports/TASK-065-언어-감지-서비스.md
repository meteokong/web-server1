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

이를 `PythonLexer`, `JavascriptLexer`, `TypeScriptLexer`, `JavaLexer`, `CppLexer`, `CLexer`, `HtmlLexer`, `CssLexer` 8개로 후보를 우리가 지원하는 언어로 한정하고, 각 렉서의 `analyse_text(content)` 신뢼도 점수(0.0~1.0)를 직접 비교해 최고점이 임계값(0.1) 초과일 때만 채택하는 방식으로 교체했다. 이 방식은 결정적이며(동일 입력 → 항상 동일 출력), shebang/DOCTYPE 등 명확한 신호에는 높은 점수(1.0, 0.5)를, 모호한 텍스트에는 0점을 안정적으로 부여한다.

## 변경 파일
- `backend/src/services/code_analysis/language_detector.py` (신규)
- `backend/tests/unit/test_language_detector.py` (신규, 23개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T065 체크)

## TDD 결과
- RED 커밋: b258f81 (test: language detection service (spec.md, research.md) - RED (T065))
- GREEN 커밋: d7074b7 (feat: language detection service using Pygments - GREEN (T065))
- REFACTOR 커밋: 해당 없음 (GREEN 단계 중 `guess_lexer` → scoped `analyse_text` 방식으로 재설계를 완료한 뒤 커밋했으므로 별도 리팩토링 커밋 불필요)
- 테스트 커버리지: `backend/tests/unit` 전체 113 passed, `src/services/code_analysis/language_detector.py` 100%

## 기술 결정
- **범용 `guess_lexer` 대신 범위를 한정한 `analyse_text` 스코어링을 선택**: Pygments의 전역 추측 함수는 500개 이상의 렉서를 대상으로 하여 짧은 스니펫에서 비결정적 결과를 낳는다. 반면 우리가 실제로 지원하는 8개 언어로 후보를 좁히고 각 렉서의 자체 신뢼도 점수를 직접 비교하면 테스트 가능하고 재현 가능한 동작을 얻는다. 트레이드오프는 지원 언어 외의 콘텐츠(예: Go, Rust)는 애초에 `file_validator`의 확장자 화이트리스트를 통과하지 못하므로 범위를 넓힐 필요가 없다는 점에서 상쇄된다.
- **content 폴백은 확장자 없는 파일에만 사용**: `.txt`/`.md`는 확장자만으로 `text`/`markdown`으로 충분히 판별되므로 content 폴백 후보에서 제외했다. 이는 "paste code"처럼 확장자가 없는 업로드 엣지 케이스를 위한 보조 경로일 뿐, 1차 판별 경로는 항상 확장자 매핑이다.
- **`detect_project_language`는 파일별 언어의 다수결**: 폴더 업로드처럼 여러 언어가 섞일 수 있는 입력에서 가장 흔한 언어 하나를 대표값으로 선택하는 단순한 규칙을 적용했다. `unknown`으로 판별된 파일은 다수결 집계에서 제외해, 확장자 없는 파일 일부가 있어도 나머지 파일들로 정상 판별되게 했다.

## 비고
- 이 서비스를 실제로 호출하는 지점은 T069(CodeUploadService)에서 연결될 예정 — 이번 task는 순수 함수 단위로만 구현했다.
- Pygments 버전 차이(전역 설치 2.21.0 vs 프로젝트 venv 2.18.0)에서 `guess_lexer`의 결과가 서로 달랐다는 점이, 애초에 전역 추측 방식을 폐기하고 스코어링 방식으로 전환한 직접적인 계기였다.
