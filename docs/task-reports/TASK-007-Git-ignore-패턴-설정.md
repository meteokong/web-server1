# TASK-007. Git ignore 패턴 설정

## 상태
완료

## 날짜
2026-10-18

## 작업 요약
루트 디렉토리에 `.gitignore`를 작성했습니다. 비유하자면, 이사할 때 "이 상자들은 나중에 다시 채울 임시 보관함이니 트럭에 안 실어도 돼요"라고 표시해 두는 것과 같습니다. 가상환경, 설치된 패키지, 비밀키가 담긴 `.env`, 사용자가 업로드한 코드 파일처럼 "다시 만들어낼 수 있거나 민감한" 것들은 git 추적 대상에서 제외했습니다.

**포함 패턴**:
- 환경변수: `.env`, `.env.local`, `.env.*.local`
- Python(백엔드): `__pycache__/`, `*.py[cod]`, `.venv/`, `venv/`, `.pytest_cache/`, `.ruff_cache/`, `.coverage` 등
- Node.js(프론트엔드): `node_modules/`, `dist/`, `dist-ssr/`, `coverage/`
- 업로드된 사용자 코드: `storage/uploads/*`와 `storage/upload/*` (내용은 무시하되 디렉토리 구조 보존을 위해 `.gitkeep`만 예외 처리)
- 로그, 에디터(`.vscode/`, `.idea/`), OS 파일(`.DS_Store`, `Thumbs.db`)

T001에서 만들어 둔 빈 디렉토리 `storage/uploads/`, `storage/upload/`가 `git add` 시 그냥 사라지지 않도록 각각에 `.gitkeep` 빈 파일을 추가하고, `.gitignore`에서 `!storage/uploads/.gitkeep` 식으로 예외 처리했습니다.

**검증**: 이 프로젝트는 아직 git 저장소로 초기화되지 않아, 실제 변경 없이 검증하기 위해 임시 디렉토리에 동일한 `.gitignore`를 복사하고 `git init` 후 대표적인 파일/폴더 조합(`.env`, `backend/.venv/`, `frontend/node_modules/`, `frontend/dist/`, `storage/uploads/user1/task1/code.py`, `__pycache__/`, `.idea/`, `*.log`, 그리고 정상 소스 파일들과 `.gitkeep`)을 만들어 `git add -A` 후 `git status --short`로 확인했습니다. 결과: 소스 파일과 `.gitkeep`만 추적(`A`)되고 나머지는 모두 올바르게 무시됨을 확인함.

## 변경 파일
- `.gitignore` (신규, 루트)
- `storage/uploads/.gitkeep` (신규)
- `storage/upload/.gitkeep` (신규)

## TDD 결과
해당 없음 (ignore 패턴 작성은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). 대신 임시 git 저장소에서 `git add -A` + `git status --short`로 "의도대로 무시/추적되는가"를 실제로 검증함.

## 기술 결정 (해당 시)
- 이 저장소 자체는 아직 git 저장소로 초기화되지 않은 상태라, 실제 리포에 영향 주지 않기 위해 별도의 임시 디렉토리(`mktemp -d`)에서 검증 후 바로 삭제함
- `storage/uploads/*`처럼 디렉토리 내용 전체를 무시하되 `!storage/uploads/.gitkeep`로 플레이스홀더만 예외 처리하여, 빈 디렉토리 구조가 git에서도 유지되도록 함
- `frontend/.gitignore`(Vite 템플릿이 자동 생성한 것)는 그대로 유지 — 중첩된 `.gitignore`는 루트 패턴과 충돌 없이 추가 규칙으로 동작함

## 비고
- git 저장소 초기화(`git init`) 자체는 이번 Task 범위에 포함하지 않음 (범위를 넘어서는 결정이라 판단, 필요 시 별도 요청으로 진행)
- 다음 Setup 단계 완료 후, Phase 2(Foundational)로 진행 가능
