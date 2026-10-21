# TASK-006. 린팅 및 포매팅 설정 (Ruff/Black, ESLint/Prettier)

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
코드 스타일을 자동으로 맞춰주는 "맞춤법 검사기"를 백엔드와 프론트엔드 양쪽에 설치했습니다. 사람이 매번 들여쓰기나 따옴표 스타일을 신경 쓰지 않아도, 도구가 알려주거나 자동으로 고쳐줍니다.

**백엔드 (Python)**:
- `backend/pyproject.toml`에 `[tool.black]`, `[tool.ruff]` 설정 추가
  - 줄 길이 100자, Python 3.11 타겟
  - Ruff 규칙: E(pycodestyle), F(pyflakes), I(import 정렬), W, UP(최신 문법 권장), B(버그 유발 패턴), C4, SIM(단순화 제안)
- `ruff check .`, `black --check .` 실행하여 정상 동작 확인 (현재 소스 코드가 없어 "검사할 파일 없음" 상태지만, 둘 다 에러 없이 종료됨을 확인)

**프론트엔드 (TypeScript/React)**:
- T003에서 Vite 기본 템플릿이 설치한 `oxlint`를 제거하고, plan.md/T003 보고서에서 예고한 대로 ESLint + Prettier로 교체
- 설치: `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`, `globals`, `prettier`, `eslint-config-prettier`
- `frontend/eslint.config.js` (Flat Config, ESLint 10): TypeScript 추천 규칙 + React Hooks 규칙 + React Refresh 규칙, Prettier와 충돌하는 규칙은 `eslint-config-prettier`로 비활성화
- `frontend/.prettierrc.json`: 세미콜론 사용, 더블쿼트, trailing comma, printWidth 100
- `frontend/.prettierignore`: `node_modules`, `dist`, `coverage`, `package-lock.json` 제외
- `package.json` 스크립트 변경: `lint` → `eslint .`, `format`/`format:check` 추가
- `npm run lint` (경고/에러 없음), `npm run format:check` → Vite 스캐폴드 파일들의 스타일 불일치 발견 → `npm run format`으로 일괄 정리 → 재검사 통과
- 포매팅 후 `npm run lint`와 `npm run build` 재실행하여 정상 동작(빌드 성공) 재확인

## 변경 파일
- `backend/pyproject.toml` (신규)
- `frontend/eslint.config.js` (신규)
- `frontend/.prettierrc.json`, `frontend/.prettierignore` (신규)
- `frontend/.oxlintrc.json` (삭제)
- `frontend/package.json`, `frontend/package-lock.json` (의존성 및 스크립트 변경)
- `frontend/src/App.tsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/main.tsx`, `frontend/tsconfig.json`, `frontend/vite.config.ts` (Prettier 자동 포맷팅 적용)

## TDD 결과
해당 없음 (린터/포매터 설정은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 각 도구의 실행 결과(통과/실패)로 "설정이 유효한가"를 검증함:
- `ruff check .` → All checks passed
- `black --check .` → 포맷 대상 없음(정상 종료)
- `eslint .` → 에러/경고 없음
- `prettier --check .` → All matched files use Prettier code style

## 기술 결정 (해당 시)
- 프론트엔드는 ESLint 10(Flat Config) 기준으로 설정 — Vite 8 템플릿이 기본 제공하는 `oxlint`는 plan.md/T006 요구사항(ESLint+Prettier)과 맞지 않아 완전히 교체함
- ESLint와 Prettier 규칙 충돌을 막기 위해 `eslint-config-prettier`로 포맷 관련 규칙을 ESLint에서 비활성화 (스타일은 Prettier가 전담, 로직/품질 검사는 ESLint가 전담)
- Ruff에 Black과 충돌할 수 있는 라인 길이 경고(E501)는 비활성화하여 두 도구의 책임을 분리 (포맷팅은 Black, 로직/스타일 검사는 Ruff)

## 비고
- 아직 실제 소스 코드가 없어 두 린터 모두 "빈 상태"에서의 통과만 확인함 — 향후 Phase 2+ 코드 작성 시 실질적인 검증이 이루어질 것
- `frontend/.gitignore`는 Vite 템플릿이 기본 제공한 것을 유지 (T007에서 루트 `.gitignore`와 함께 검토 예정)
