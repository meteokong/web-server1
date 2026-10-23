# TASK-066. 코드 복잡도 분석기 구현

## 상태
완료

## 날짜
2026-10-22

## 작업 요약
`backend/src/services/code_analysis/complexity_analyzer.py`에 업로드된 코드의 복잡도를 평가하는 서비스를 구현했다. research.md가 명시한 "Line count, nesting depth, function count" 세 지표를 측정해 `uploaded_code.complexity_level` CHECK 제약이 요구하는 `beginner`/`intermediate`/`advanced` 중 하나로 매핑한다.

- `count_lines(content)`: 공백 전용 줄을 제외한 실질 코드 줄 수.
- `max_nesting_depth(content)`: 들여쓰기 폭(2-space/4-space/tab)에 무관하게 동작하는 인덴트 스택 기반 깊이 측정. Python은 들여쓰기가 곧 스코프이고, JS/TS/Java/C/C++는 중괄호가 스코프를 결정하지만 실무상 거의 항상 중첩에 맞춰 들여쓰기되므로, 언어별 파서 없이 하나의 휴리스틱으로 커버했다.
- `count_functions(content)`: Python(`def`), JavaScript/TypeScript(`function`, 화살표 함수 대입), Java/C++(`public`/`private`/`protected`/`static` 메서드) 선언을 정규식 4종으로 카운트.
- `assess_complexity_level(total_lines, nesting_depth, function_count)`: 세 지표를 임계값과 비교해 레벨 결정.
- `analyze_file_complexity(content)` / `analyze_project_complexity(file_contents)`: 단일 파일 / 업로드 전체(줄 수·함수 수는 합산, 중첩 깊이는 파일 중 최댓값)에 대한 `ComplexityMetrics` 결과를 반환.

## 변경 파일
- `backend/src/services/code_analysis/complexity_analyzer.py` (신규)
- `backend/tests/unit/test_complexity_analyzer.py` (신규, 20개 테스트)
- `specs/001-ai-code-learning-platform/tasks.md` (T066 체크)

## TDD 결과
- RED 커밋: 793340d (test: code complexity analyzer (spec.md FR-021) - RED (T066))
- GREEN 커밋: 98c489d (feat: code complexity analyzer (line/nesting/function count) - GREEN (T066))
- REFACTOR 커밋: 해당 없음
- 테스트 커버리지: `backend/tests/unit` 전체 137 passed, `src/services/code_analysis/complexity_analyzer.py` 100%

## 기술 결정
- **임계값은 spec.md/research.md에 명시되지 않아 자체 보정**: `beginner`는 50줄 이하 + 중첩 깊이 2 이하 + 함수 3개 이하(한 번에 읽을 수 있는 작은 스크립트 기준), `advanced`는 300줄 이상 또는 중첩 깊이 5 이상 또는 함수 16개 이상 중 하나라도 해당(세 조건 중 하나만 과해도 "advanced") — 나머지는 `intermediate`. 추후 실제 업로드 데이터로 재보정이 필요할 수 있음을 비고에 남긴다.
- **중첩 깊이는 들여쓰기 스택 기반, AST 파싱 없음**: T065의 교훈(Pygments 같은 범용 도구의 언어별 이질성)을 반영해, 언어마다 다른 파서/AST 라이브러리를 두지 않고 모든 지원 언어에 공통으로 적용되는 들여쓰기 패턴 하나로 단순화했다. 트레이드오프: 들여쓰기가 일관되지 않은(포맷팅이 엉망인) 파일은 실제 구조적 복잡도보다 낮게 측정될 수 있음.
- **함수 카운트 정규식은 100% 정확도를 목표로 하지 않음**: 예를 들어 Java/C++ 패턴은 `public`/`private`/`protected`/`static` 접두사가 없는 함수(기본 접근 제어자)는 세지 못한다. 세 지표를 "복잡도 등급" 산정의 신호로만 쓰고 정밀한 메트릭으로는 쓰지 않는다는 전제하에 허용 가능한 단순화로 판단했다.
- **`analyze_project_complexity`가 빈 리스트를 받으면 `beginner`를 반환**: 파일이 없는 업로드는 존재할 수 없지만(T064의 `validate_file_count` 등으로 이미 막힘), 호출부에서 방어적으로 호출해도 예외 없이 안전한 기본값을 돌려주도록 했다.

## 비고
- T065(언어 감지)와 마찬가지로 이 서비스를 실제로 호출하는 지점은 T069(CodeUploadService)에서 연결될 예정 — 순수 함수 단위로만 구현했다.
- 임계값 보정은 실제 사용자 업로드가 쌓인 뒤 조정 여지가 있다. 필요 시 `BEGINNER_MAX_*`/`ADVANCED_MIN_*` 상수만 바꾸면 되도록 모듈 상단에 노출해 두었다.
