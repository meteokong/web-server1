# TASK-003. 프론트엔드 React 프로젝트 초기화

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
plan.md/research.md에서 정한 프론트엔드 스택(React 18+, TypeScript, Vite)에 맞춰 `frontend/`에 Vite 기반 React+TypeScript 프로젝트를 초기화했습니다. 비유하자면, 자동차를 만들 때 차체(프레임)와 기본 엔진을 먼저 조립해두는 것과 같습니다. 아직 좌석(UI 컴포넌트)이나 내비게이션(라우팅)은 없지만, 시동을 걸고 달릴 수 있는 최소한의 뼈대는 완성되었습니다.

**진행 과정**:
1. `frontend/` 안에 이미 T001에서 만들어 둔 빈 디렉토리(`src/components/*`, `src/pages`, `src/services`, `src/hooks`, `src/utils`, `tests/*`)가 있어, `npm create vite@latest .`를 바로 실행하면 "디렉토리가 비어있지 않음" 프롬프트에서 비대화형 셸이 멈추는 문제가 발생함
2. 임시 디렉토리에 `npx create-vite@latest app --template react-ts`로 깨끗하게 스캐폴딩한 뒤, 생성된 파일들을 `frontend/`로 복사하여 기존 빈 디렉토리 구조를 보존함
3. `package.json`의 이름을 임시 폴더명(`app`)에서 `code-study-frontend`로 수정
4. `npm install` → `npm run build` 실행하여 정상적으로 빌드되는지 확인 (TypeScript 컴파일 + Vite 빌드 성공, `dist/` 생성 확인 후 삭제)

**생성된 주요 파일**:
- `package.json` (React 19, TypeScript ~6.0, Vite 8)
- `vite.config.ts`, `tsconfig.json`/`tsconfig.app.json`/`tsconfig.node.json`
- `index.html`, `src/main.tsx`, `src/App.tsx`, `src/App.css`, `src/index.css`, `src/assets/`
- `public/favicon.svg`, `public/icons.svg`
- `.gitignore` (Vite 기본 템플릿 제공), `.oxlintrc.json` (Vite 8 기본 린터)

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (신규)
- `frontend/vite.config.ts`, `frontend/tsconfig*.json` (신규)
- `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/assets/*` (신규)
- `frontend/public/*` (신규)
- `frontend/.gitignore`, `frontend/.oxlintrc.json`, `frontend/README.md` (신규)
- `frontend/node_modules/` (설치된 의존성, 로컬에만 존재 — 커밋 대상 아님)

## TDD 결과
해당 없음 (프로젝트 스캐폴딩은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 `npm run build` 성공 여부로 "정상 동작"을 검증함.

## 기술 결정 (해당 시)
- Vite 최신 템플릿(react-ts)을 그대로 사용 → React 19 + TypeScript 6 + Vite 8 조합 (plan.md의 "React 18+" 요구사항을 충족하는 상위 버전)
- 최신 Vite 템플릿은 기본 린터로 ESLint 대신 `oxlint`를 포함하지만, plan.md/tasks.md(T006)에서 ESLint+Prettier를 명시적으로 요구하므로 **T006에서 ESLint/Prettier로 교체 또는 추가할 예정** — 이번 Task 범위는 Vite/React/TS 초기화로 한정함
- 빈 서브디렉토리가 이미 존재하는 상태에서 `create-vite`를 직접 실행하면 비대화형 환경에서 멈추는 문제가 있어, 임시 디렉토리에서 스캐폴딩 후 복사하는 방식을 선택함 (기존 디렉토리 구조 보존 목적)

## 비고
- 아직 git 저장소가 초기화되지 않아 커밋은 생성하지 않음
- ESLint/Prettier 설정(T006), Tailwind/shadcn-ui 설정(T022) 등은 이후 Task에서 별도로 진행
- 다음 Task(T004: Docker Compose 설정, [P]) 또는 T006/T007로 이어갈 수 있음
