# TASK-022. Tailwind CSS 및 shadcn/ui 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
프론트엔드에 디자인 시스템 기반을 깔았습니다. 비유하자면, 지금까지는 집을 지을 때 벽돌을 하나하나 직접 구워야 했는데(순수 CSS), 이제는 표준 규격 벽돌(Tailwind 유틸리티 클래스)과 미리 만들어진 문·창문 세트(shadcn/ui 컴포넌트)를 가져다 쓸 수 있게 된 것입니다. 색상·둥근 정도·그림자 같은 디자인 값들도 한 곳(`index.css`의 CSS 변수)에서 관리되어, 나중에 다크모드나 테마를 바꿀 때 변수 값만 바꾸면 전체에 반영됩니다.

**구현 내용**:
1. **Tailwind CSS v4** 설치: `tailwindcss`, `@tailwindcss/vite` — v4는 별도의 `tailwind.config.js`/PostCSS 설정 없이 Vite 플러그인 하나로 동작 (research.md 작성 시점보다 이후 등장한 아키텍처라, 최신 버전 기준으로 설정함)
2. `vite.config.ts`에 `tailwindcss()` 플러그인 추가, `@` → `./src` 경로 별칭 추가 (shadcn/ui 컴포넌트가 `@/components/...` 형태로 import하기 때문에 필수)
3. `tsconfig.json`/`tsconfig.app.json`에도 동일한 `@/*` 경로 매핑 추가 (TypeScript가 별칭을 이해하도록)
4. `src/index.css`를 Vite 기본 데모 전용 스타일(카운터 버튼, 고정폭 `#root` 등)에서 **Tailwind + shadcn/ui 테마 변수**로 전면 교체 — `oklch` 색상 기반의 라이트/다크 테마 변수(`--background`, `--primary`, `--border` 등)와 `@theme inline`으로 Tailwind 토큰에 매핑
5. `components.json` 생성 (shadcn CLI 설정: style=new-york, alias=`@/components` 등)
6. `src/lib/utils.ts`: `cn()` 헬퍼 (clsx + tailwind-merge) — 다만 최신 shadcn CLI(4.22.1)가 생성한 컴포넌트는 자체적으로 `cn` npm 패키지(`import { cn } from "cn"`)를 쓰는 새로운 방식이라, 이 로컬 유틸은 향후 직접 작성할 컴포넌트를 위해 남겨둠
7. **shadcn/ui 컴포넌트 2개 설치**: `npx shadcn@latest add button input` → `Button`(default/outline/destructive 등 variant), `Input` 컴포넌트를 `src/components/ui/`에 생성

**진행 중 발견/수정한 문제**:
- 최초 `npx shadcn@latest add button` 실행 시, CLI가 `@/components` 별칭을 해석하지 못해 **`frontend/@/components/ui/button.tsx`라는 리터럴 디렉토리**를 만들어버림 — 원인은 경로 별칭이 `tsconfig.app.json`에만 있고 루트 `tsconfig.json`(CLI가 먼저 읽는 파일)에는 없었기 때문. 루트 `tsconfig.json`에도 `baseUrl`/`paths`를 추가해 해결하고, 두 번째 컴포넌트(`input`)부터는 정상적으로 `src/components/ui/`에 생성됨을 확인
- `baseUrl` 추가 직후 `tsc -b` 빌드 시 `TS5101: Option 'baseUrl' is deprecated` 에러 발생 — TypeScript 6부터 `moduleResolution: "bundler"`에서는 `baseUrl` 없이 `paths`만으로 동작하므로, `baseUrl`을 제거해 해결
- `vite.config.ts`에서 `path.resolve(__dirname, ...)` 사용 시 Vite 8의 네이티브 설정 로더가 "`__dirname`은 더 이상 지원되지 않을 예정, `import.meta.dirname` 사용 권장" 경고 → `import.meta.dirname`으로 교체해 해결
- shadcn CLI가 생성한 파일(`button.tsx`, `input.tsx`)이 이 프로젝트의 Prettier 설정(세미콜론 사용 등)과 포맷이 달라 `format:check` 실패 → shadcn 공식 문서상 "추가된 컴포넌트는 이제 당신의 코드"라는 원칙에 따라 `prettier --write`로 프로젝트 스타일에 맞춰 재포맷

**검증**:
1. `npm run build`(TypeScript 컴파일 포함) → 242개 모듈 정상 변환, 타입 에러 없음
2. `npm run lint` → 에러 없음 (shadcn `button.tsx`의 `react-refresh/only-export-components` 경고 1건만 남음 — `buttonVariants`를 `Button`과 같은 파일에서 함께 export하는 shadcn 표준 패턴이라 CLI 생성 코드를 그대로 둠, 기능에는 영향 없음)
3. `npm run format:check` → 통과
4. **실제 컴파일된 CSS 검증**: `dist/assets/*.css`에서 `.rounded-lg{border-radius:var(--radius)}`, `.bg-primary{background-color:var(--primary)}` 같은 **실제로 생성된 Tailwind 유틸리티 규칙**을 직접 확인 — Tailwind가 단순히 소스를 통과시키는 게 아니라 실제로 JIT 컴파일하고 있음을 증명
5. `npm run dev`로 실제 개발 서버 기동 → `/dev-test`(Button/Input을 사용하는 임시 테스트 컴포넌트 추가) `200 OK` 확인

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (`tailwindcss`, `@tailwindcss/vite`, `clsx`, `tailwind-merge`, `class-variance-authority`, `cn`, `radix-ui` 추가)
- `frontend/vite.config.ts` (`tailwindcss()` 플러그인, `@` 경로 별칭 추가, `import.meta.dirname` 사용)
- `frontend/tsconfig.json`, `frontend/tsconfig.app.json` (`@/*` 경로 매핑 추가)
- `frontend/src/index.css` (전면 교체: Tailwind + shadcn 테마 변수)
- `frontend/components.json` (신규, shadcn CLI 설정)
- `frontend/src/lib/utils.ts` (신규, `cn()` 헬퍼)
- `frontend/src/components/ui/button.tsx`, `frontend/src/components/ui/input.tsx` (신규, shadcn CLI 생성)
- `frontend/src/components/_ShadcnTest.tsx` (신규, 임시 검증용)
- `frontend/src/App.tsx` (`/dev-test`에 `ShadcnTest` 추가)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 빌드/린트/포맷 통과에 더해, 컴파일된 CSS 산출물을 직접 열어 Tailwind 유틸리티가 실제로 생성됐는지까지 확인함.

## 기술 결정 (해당 시)
- research.md는 "Tailwind CSS + shadcn/ui"만 명시하고 버전을 특정하지 않아, 현재(2026-10) 기준 최신 메이저 버전인 **Tailwind v4**를 사용함 — v3와 달리 `tailwind.config.js`/PostCSS 플러그인 체인이 필요 없고 Vite 플러그인 하나로 동작해 설정이 더 단순함
- shadcn CLI(4.22.1)가 기본적으로 개별 `@radix-ui/react-*` 패키지 대신 통합 `radix-ui` 패키지와, 로컬 `lib/utils.ts` 대신 `cn` npm 패키지를 사용하는 최신 컨벤션으로 코드를 생성함 — CLI가 만들어준 그대로 받아들임 (수동으로 구버전 패턴으로 되돌리지 않음)
- `baseColor: "neutral"`(components.json)과 `style: "new-york"`을 선택 — 특별한 브랜드 가이드가 없는 프로젝트 초기 단계에서 무난한 기본값

## 비고
- 설치된 컴포넌트는 `Button`, `Input` 2개뿐 — 이후 각 UI Task(T032 RegisterForm, T051 ProjectCard 등)에서 필요한 shadcn 컴포넌트(Dialog, Card, Badge 등)를 그때그때 `npx shadcn add <component>`로 추가하면 됨
- `_ShadcnTest.tsx`는 T019/T020/T021의 임시 테스트 컴포넌트들과 마찬가지로 사용자 확인 후 일괄 정리 대상
- 이로써 **Phase 2 Foundational 전체(T008~T022)가 완료**됨
