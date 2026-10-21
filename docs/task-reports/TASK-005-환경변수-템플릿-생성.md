# TASK-005. 환경변수 템플릿(.env.example) 생성

## 상태
완료

## 날짜
2026-10-14

## 작업 요약
프로젝트 루트에 `.env.example`을 작성했습니다. 비유하자면, 집에 입주할 때 "수도, 전기, 가스 계량기 설정값을 이렇게 맞춰두세요"라고 알려주는 안내문과 같습니다. 실제 비밀번호(`.env`)는 각자 알아서 채우고 git에 올리지 않지만, 어떤 항목이 필요한지 미리 보여주는 템플릿입니다.

**포함 항목** (quickstart.md의 "Environment Configuration" 섹션 기준):
- `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — T004에서 만든 `docker-compose.yml`의 `db` 서비스와 일치
- `REDIS_URL` — `docker-compose.yml`의 `redis` 서비스와 일치
- `GOOGLE_API_KEY` — Gemini API 연동용 (플레이스홀더)
- `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET` — 인증 토큰 서명용 (플레이스홀더, 실제 값은 `openssl rand -hex 32`로 생성)
- `ENVIRONMENT`, `DEBUG`, `ALLOWED_ORIGINS` — 실행 환경 및 CORS 설정
- `UPLOAD_DIR`, `MAX_UPLOAD_SIZE_MB` — 파일 업로드 저장 경로 및 용량 제한

**검증**: `.env.example`을 임시로 `.env`로 복사한 뒤 `docker compose config`를 실행해, T004의 `docker-compose.yml`이 이 값들을 정상적으로 치환하는지 확인했습니다 (`POSTGRES_DB: codelearning` 등 정확히 반영됨). 확인 후 테스트용 `.env`는 즉시 삭제했습니다 (아직 `.gitignore`가 없는 상태이므로 민감 정보로 오인될 파일을 남기지 않기 위함).

## 변경 파일
- `.env.example` (신규)

## TDD 결과
해당 없음 (환경변수 템플릿 작성은 비즈니스 로직이 없는 순수 설정 작업이므로 RED-GREEN-REFACTOR 사이클을 적용하지 않음). `docker compose config`로 실제 compose 파일과의 호환성만 검증함.

## 기술 결정 (해당 시)
- quickstart.md에 이미 명시된 값/키 이름을 그대로 사용하여 문서와 실제 설정 간 불일치를 방지함
- 비밀키류(`JWT_SECRET_KEY` 등)는 실제 값이 아닌 플레이스홀더 문자열로 두고, 생성 방법(openssl 명령)을 주석으로 안내함

## 비고
- `.env` 자체는 아직 생성하지 않음 (각 개발자가 `.env.example`을 복사해 로컬에서 생성)
- `.gitignore`(T007)에서 `.env`를 반드시 무시 패턴에 포함해야 함 — 다음 Task에서 처리
