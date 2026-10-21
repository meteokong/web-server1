# AI Code Learning Platform Constitution

## Core Principles

### I. TDD (Test-Driven Development) - NON-NEGOTIABLE

**Required TDD Cycle:**
1. RED: Write test first → Run tests (must fail)
2. GREEN: Write minimal code → Run tests (must pass)
3. REFACTOR: Improve code quality → Re-run tests (still pass)

**Enforcement:**
- REQUIRED: Ask "테스트를 먼저 작성할까요?" when receiving feature requests
- REQUIRED: Write tests before any implementation
  - Backend: `backend/tests/` directory (pytest)
  - Frontend: `frontend/tests/` or co-located `*.test.ts(x)` files (Vitest)
- REQUIRED: Confirm test failure before writing implementation
- REQUIRED: 80%+ test coverage (핵심 비즈니스 로직 100%)
- FORBIDDEN: Writing implementation before tests
- FORBIDDEN: Skipping test execution between steps

**Git Integration:**
- Each TDD phase MUST have its own commit:
  - RED: `git commit -m "test: {feature} - RED ({task-id})"`
  - GREEN: `git commit -m "feat: {feature} - GREEN ({task-id})"`
  - REFACTOR: `git commit -m "refactor: {feature} - REFACTOR ({task-id})"`

**Test Stack:**
- Backend: pytest + pytest-asyncio + pytest-cov
- Frontend: Vitest + React Testing Library
- Coverage: pytest-cov (backend), v8 (frontend)

---

### II. Context Engineering

**Task Report (작업 보고서) Mandatory:**
- 모든 Task 완료 시 Task Report 작성 필수
- Task Report 저장 위치: `docs/task-reports/`
- Task Report 파일 형식: `TASK-{NNN}-{short-title}.md` (예: `TASK-001-프로젝트-디렉토리-구조-생성.md`)

**Task Report Template:**
```markdown
# TASK-{NNN}. {제목}

## 상태
[진행중 | 완료 | 보류]

## 날짜
YYYY-MM-DD

## 작업 요약
[구현한 내용 요약]

## 변경 파일
[변경된 주요 파일 목록]

## TDD 결과
- RED 커밋: {커밋 해시}
- GREEN 커밋: {커밋 해시}
- REFACTOR 커밋: {커밋 해시} (해당 시)
- 테스트 커버리지: {XX}%

## 기술 결정 (해당 시)
[이 Task에서 내린 주요 기술 결정과 근거]

## 비고
[추가 참고 사항]
```

**Task 번호 규칙:**
- 3자리 숫자, 순차 증가 (001, 002, ...)
- Vertical Slice 순서대로 번호 부여 (Phase 구분 없이 일련번호)
- tasks.md의 태스크 ID(T001, T002, ...)가 Task Report의 TASK-{NNN}에 대응

**Documentation Standards:**
- 코드는 자체 설명적으로 작성
- 복잡한 비즈니스 로직에만 주석 추가
- API 문서는 FastAPI auto-generated `/docs` 활용

---

### III. Modular Monolith Architecture

**현재 아키텍처: 모놀리식 백엔드 + 비동기 태스크 프로세싱**

```
Frontend (React SPA)
    │ HTTPS/REST
    ▼
FastAPI Backend (Monolith)  [backend/src/]
    ├── api/        → API 라우터 (auth, projects, tasks, documents, practice, qa, progress, trash)
    ├── models/     → SQLAlchemy ORM 모델
    ├── services/   → 비즈니스 로직 (auth/, code_analysis/, document/, ai/, practice/, qa/, progress/)
    ├── tasks/      → Celery 비동기 태스크
    └── utils/      → 공통 유틸리티 (jwt, security, file_validator)
    │
    ├── PostgreSQL  → 단일 데이터베이스
    ├── Redis       → Celery 브로커 + 캐시
    └── Filesystem  → 코드 파일 저장 (storage/uploads/)
        │
        └── Celery Worker → 비동기 작업 처리
```

**모듈 분리 원칙:**
- [ ] 각 모듈(api, services, models)은 명확한 책임을 가지는가?
- [ ] 서비스 레이어가 비즈니스 로직을 캡슐화하는가?
- [ ] API 레이어는 요청/응답 처리만 담당하는가?
- [ ] 모델 레이어는 데이터 구조와 관계만 정의하는가?

**계층 구조 규칙:**
- API Router → Service → Model (단방향 의존)
- Service 간 직접 호출 최소화 (필요시 명시적 의존성 주입)
- 비즈니스 로직은 반드시 Service 레이어에 위치
- API Router에 비즈니스 로직 직접 작성 금지

**비동기 처리:**
- CPU 집약 작업은 Celery 태스크로 분리
- Celery 큐: default, document_generation, practice_generation, cleanup
- 태스크 타임아웃: 300초 (5분)

---

### IV. MCP Tool Usage Policy

**사용 가능한 MCP (3종):**

| MCP | 용도 | 승인 |
|-----|------|------|
| **Context7** | 기술 문서 검색, 라이브러리 API 확인, 최신 문서 참조 | Auto-Execute |
| **Serena MCP** | 코드 심볼 분석, 리팩토링, 코드베이스 탐색 | Auto-Execute |
| **Playwright MCP** | 수동 브라우저 테스트 보조, UI 검증 | Approval Required |

**사용 지침:**
- **Context7**: 새로운 라이브러리 도입 전, 공식 문서 확인 시 자동 사용
- **Serena MCP**: 코드 분석, 심볼 검색, 리팩토링 시 자동 사용
- **Playwright MCP**: 수동 브라우저 테스트 보조 시 사용자 승인 필요
  - E2E 검증은 수동 브라우저 테스트로 수행 (자동화된 Playwright E2E 스크립트 대신)
  - 승인 요청 형식: "브라우저 테스트 - 시나리오: X개. 진행? (y/n)"

---

### V. Code Quality Standards

**Readability:**
- 자체 설명적 코드 (변수/함수명으로 의도 표현)
- 주석 최소화 (복잡한 비즈니스 로직만)
- 코드 포맷팅 도구 준수

**Linting & Formatting:**

| Stack | Linter | Formatter | Config |
|-------|--------|-----------|--------|
| Backend (Python) | Ruff | Black | pyproject.toml |
| Frontend (TypeScript) | ESLint | Prettier | eslint.config.js |

**Type Safety:**
- Backend: MyPy strict mode
- Frontend: TypeScript strict mode
- 타입 안전성은 선택이 아닌 필수

**Testing:**
- 커버리지 최소 80% (핵심 로직 100%)
- Unit > Integration > E2E (테스트 피라미드)
- TDD 준수 (테스트 먼저)

**Performance:**
- API 응답 3초 이내
- Celery 태스크 타임아웃 300초
- 프론트엔드 번들 사이즈 최소화 (Vite 빌드 최적화)

**Security:**
- 민감 정보 하드코딩 금지 (.env 사용)
- .env 파일 Git 커밋 금지
- CORS 화이트리스트 관리
- JWT 토큰 만료 시간 적절히 설정

---

### VI. Git Workflow Strategy

**Branch Structure:**
```
main (production)
├─ {NNN}-{feature-name} (기능 개발 브랜치, 예: 001-ai-code-learning-platform)
└─ hotfix/{short-description} (긴급 수정)
```

**Branch Naming:**
- 기능 개발: `{NNN}-{feature-name}` (예: `001-ai-code-learning-platform`)
- 긴급 수정: `hotfix/{short-description}`
- 태스크별 브랜치는 생성하지 않음 — 하나의 Feature 브랜치에서 모든 태스크를 순차 커밋

**Commit Convention:**
```
{type}: {subject} - {TDD phase} ({task-id})
```
- test: 테스트 작성 - RED (TDD RED 단계)
- feat: 구현 완료 - GREEN (TDD GREEN 단계)
- refactor: 코드 개선 - REFACTOR (TDD REFACTOR 단계)
- feat: 새 기능 (TDD 외 작업)
- fix: 버그 수정
- docs: 문서 업데이트
- config: 설정 변경
- deploy: 배포 관련

**Push Strategy:**
- 각 Task 완료 시: Feature 브랜치에 커밋 (TDD Cycle 커밋 포함)
- Feature 완료 시: PR 생성 ({NNN}-{feature-name} → main)
- 릴리스 시: main에 태그 생성

**Merge Strategy:**
- Feature → Main: Squash and merge (또는 merge commit with tag)
- Hotfix → Main: Direct merge

---

### VII. Agent Roles

**단일 AI Agent (Claude) + 개발자 협업 구조:**

Claude Agent는 상황에 따라 아래 역할을 수행합니다:

| 역할 | 책임 | 사용 MCP |
|------|------|----------|
| **Architect** | 아키텍처 설계, 모듈 구조 리뷰, 기술 결정 | Serena, Context7 |
| **Implementer** | TDD 기반 코드 구현 (Backend + Frontend) | Serena, Context7 |
| **Tester** | 테스트 작성, 커버리지 관리, TDD Cycle 준수, 수동 브라우저 테스트 | Serena, Playwright |
| **Reviewer** | 코드 리뷰, 품질 검증, 리팩토링 제안 | Serena |
| **Writer** | Task Report 작성, README 업데이트, 문서화 | Context7 |

**역할 전환 규칙:**
- Feature 요청 → Tester (테스트 먼저) → Implementer → Reviewer → Writer (Task Report)
- 버그 리포트 → Tester (재현 테스트) → Implementer (수정) → Reviewer → Writer (Task Report)
- 아키텍처 질문 → Architect → Writer (기술 결정을 Task Report에 기록)
- "테스트를 먼저 작성할까요?" 질문은 모든 구현 작업 전 필수

---

### VIII. Development Workflow

**Phase 1: Analysis**
1. 요구사항 분석 및 기존 코드 파악 (Serena MCP)
2. 필요시 기술 문서 확인 (Context7 MCP)
3. Task 번호 부여 (현재 Feature 브랜치에서 작업)

**Phase 2: TDD Implementation**
1. RED: 테스트 작성 → 실패 확인 → commit
2. GREEN: 최소 구현 → 테스트 통과 → commit
3. REFACTOR: 코드 개선 → 테스트 재통과 → commit
4. 반복 (기능 완성까지)

**Phase 3: Review & Documentation**
1. 코드 리뷰 (Serena MCP)
2. 커버리지 확인 (80% 이상)
3. Task Report 작성 (`docs/task-reports/TASK-{NNN}-{title}.md`)
4. PR 생성

**Phase 4: Deployment**
1. Feature 브랜치 → main 머지
2. 태그 생성
3. 배포

---

### IX. Execution Checklists

**프로젝트 시작 전:**
- [ ] Context7으로 기술 스택 최신 문서 확인
- [ ] 기존 코드베이스 파악 (Serena MCP)
- [ ] TDD 전략 수립

**Task 시작 전:**
- [ ] Task 번호 부여 (TASK-{NNN})
- [ ] 현재 Feature 브랜치에서 작업 (`{NNN}-{feature-name}`)
- [ ] 최신 코드 pull 완료 (`git pull`)
- [ ] "테스트를 먼저 작성할까요?" 확인

**각 Task 개발 시:**
- [ ] RED: 테스트 작성 및 실패 확인 → commit
- [ ] GREEN: 최소 구현 및 통과 확인 → commit
- [ ] REFACTOR: 코드 개선 → commit
- [ ] GREEN: 재검증 (모든 테스트 통과)

**Task 완료 시:**
- [ ] 모든 TDD Cycle 커밋 완료
- [ ] 모든 테스트 통과
- [ ] 커버리지 80% 이상
- [ ] Task Report 작성 (`docs/task-reports/TASK-{NNN}-{title}.md`)
- [ ] Feature 브랜치에 Push

**배포 전:**
- [ ] Feature 브랜치 → main 머지
- [ ] 태그 생성 (Semantic Versioning)
- [ ] 모든 테스트 통과
- [ ] API 문서 확인 (/docs)
- [ ] 환경 변수 확인 (.env.example 동기화)

---

### X. Forbidden Practices

**절대 금지 (Immediate Rejection):**
1. 테스트 없는 구현 코드 작성
2. TDD Cycle 생략 (RED → GREEN → REFACTOR)
3. 테스트 실패 상태에서 다음 단계 진행
4. 코드 커버리지 80% 미만 배포
5. Task Report 없이 Task 완료 처리
6. 테스트 없이 Git Commit/Push
7. main 브랜치 직접 커밋 (PR 없이)
8. main 브랜치에 Force Push
9. 민감정보 Git 커밋 (.env, API Key 등)
10. Commit Message Convention 미준수
11. API Router에 비즈니스 로직 직접 작성
12. Service 레이어 우회하여 직접 DB 접근 (API Router에서)

---

### XI. Success Criteria

**Technical Success:**
- 테스트 커버리지 >= 80% (핵심 로직 100%)
- API 응답 < 3초
- 모든 테스트 통과
- 타입 안전성 확보 (MyPy + TypeScript strict)

**Process Success:**
- 100% TDD 개발 (테스트 먼저)
- Task Report로 모든 작업 이력 추적 가능
- 명확한 문서화로 온보딩 단축
- Git History로 완전한 추적 가능 (TDD Cycle 커밋)

**Quality Success:**
- Linting/Formatting 규칙 100% 준수
- 계층 구조 규칙 준수 (API → Service → Model)
- 민감 정보 노출 0건

---

## Governance

**Amendment Procedure:**
1. 수정 제안 작성 (변경 사유, 변경 내용)
2. 변경 사항을 Task Report에 기록
3. Version bump (Semantic Versioning)
4. Constitution 파일 업데이트

**Compliance Review:**
- 모든 PR에서 constitution 준수 확인
- TDD Cycle 커밋 히스토리 검증
- Task Report 존재 여부 확인
- 코드 리뷰 시 계층 구조 준수 확인

**Constitution Supremacy:**
- Constitution은 모든 개발 관행에 우선
- 예외 발생 시 해당 Task Report에 사유 기록
