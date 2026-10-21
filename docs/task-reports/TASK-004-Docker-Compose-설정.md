# TASK-004. Docker Compose 설정 (PostgreSQL, Redis)

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
개발 환경에서 PostgreSQL과 Redis를 손쉽게 띄울 수 있도록 루트 디렉토리에 `docker-compose.yml`을 작성했습니다. 비유하자면, 매번 벽돌을 하나씩 쌓아 창고(데이터베이스)와 우체통(메시지 큐)을 짓는 대신, "창고와 우체통을 설치해줘"라는 한 번의 명령으로 끝낼 수 있는 조립식 키트를 만든 것입니다.

**구성 내용**:
- `db` 서비스: `postgres:15-alpine` 이미지, 포트 5432, `postgres_data` 볼륨으로 데이터 영속화, `pg_isready` 헬스체크
- `redis` 서비스: `redis:7-alpine` 이미지, 포트 6379, `redis_data` 볼륨, `redis-cli ping` 헬스체크
- 환경 변수(`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`)는 quickstart.md에 명시된 `.env` 값(`postgres`/`postgres`/`codelearning`)을 기본값으로 사용하되, `.env` 파일로 오버라이드 가능하도록 `${VAR:-default}` 문법 사용

**범위 결정**: tasks.md T004는 "PostgreSQL, Redis"로 범위를 한정하고 있어, 백엔드/프론트엔드/Celery worker는 포함하지 않았습니다 (해당 서비스들은 아직 Dockerfile이 없고, quickstart.md의 "Quick Start with Docker" 섹션에 언급된 전체 스택 구성은 추후 Polish 단계(T211-T214, Nginx/운영 설정)나 별도 작업에서 확장 가능).

**검증**:
- `docker compose config`로 YAML 문법 및 변수 치환이 올바르게 해석되는지 확인 (정상)
- (최초 시도 시) Docker Desktop 데몬이 꺼져 있어 실제 기동 테스트 보류
- **재검증 (데몬 기동 후)**: `docker compose up -d` 실행 → `db`, `redis` 컨테이너 모두 정상 생성 및 "healthy" 상태로 전환 확인
  - `docker exec ... pg_isready -U postgres -d codelearning` → `accepting connections`
  - `docker exec ... redis-cli ping` → `PONG`
  - 확인 후 `docker compose down`으로 컨테이너 정리 (named volume은 보존됨)

## 변경 파일
- `docker-compose.yml` (신규)

## TDD 결과
해당 없음 (인프라 설정 파일 작성은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). `docker compose config`로 문법적 유효성만 검증함.

## 기술 결정 (해당 시)
- 이미지로 `-alpine` 태그를 사용해 다운로드/시작 속도 최적화
- 서비스명을 `db`, `redis`로 지정하여 quickstart.md의 `DATABASE_URL=postgresql://postgres:postgres@db:5432/codelearning`, `REDIS_URL=redis://redis:6379/0`과 호스트명이 일치하도록 함
- named volume을 사용해 컨테이너 재시작 시에도 데이터 보존

## 비고
- 2026-10-14 재검증 시 Docker Desktop 데몬이 기동되어 있어 실제 `up`/연결 테스트까지 완료함 (최초 작성 시점에는 데몬 미기동으로 보류했었음)
- `.env` 파일은 아직 생성되지 않음 (T005에서 `.env.example` 작성 예정) — 현재는 compose 파일의 기본값(`postgres`/`postgres`/`codelearning`)으로 동작
- 다음 Task(T005: `.env.example` 작성)에서 이 compose 파일이 참조하는 환경 변수를 문서화할 예정
