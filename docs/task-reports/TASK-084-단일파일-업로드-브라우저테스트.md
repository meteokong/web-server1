# TASK-084. 수동 브라우저 테스트: 단일 파일 업로드

## 상태
완료 (PASS)

## 날짜
2026-10-22

## 작업 요약
Chrome 브라우저 자동화(claude-in-chrome — 프로젝트에 별도의 Playwright MCP 서버는 설정되어 있지 않아, 동일한 목적의 수동 브라우저 테스트 보조 도구로 대체 사용)로 실제 앱을 구동해 테스트했다.

1. 백엔드(uvicorn, `DATABASE_URL`/`REDIS_URL`을 localhost로 오버라이드)와 프론트엔드(Vite) 개발 서버를 로컬로 기동.
2. 신규 사용자 회원가입 → 로그인 → 프로젝트 생성 → "새 태스크" 모달에서 파일 업로드 방식으로 `single_upload.py`(간단한 Python 파일) 업로드.
3. 결과: 태스크가 "Task 1"로 생성됨. 네트워크 탭 확인 결과 `POST /api/v1/projects/{id}/tasks` → 201, 이어지는 `GET .../tasks` → 200.

이 과정에서 과거 세션에서 발견되지 않았던 기존 버그(`get_db()`가 커밋을 하지 않아 실제 운영에서 모든 쓰기가 유실되는 문제, T067-075 Task Report에 기록됨)가 이미 수정되어 있었음을 회원가입→로그인 성공으로 간접 확인했다.

## 변경 파일
없음 (순수 검증 테스트, 코드 변경 없음)

## TDD 결과
해당 없음 (구현이 아닌 수동 검증 태스크)

## 기술 결정
- 프로젝트 constitution은 "Playwright MCP"를 명시하지만 현재 세션에는 별도 Playwright MCP 서버가 연결되어 있지 않아, 동등한 역할의 claude-in-chrome 브라우저 자동화로 대체했다.

## 비고
- 테스트 계정: `browsertest@example.com` / 프로젝트: "Task Upload 테스트 프로젝트" (후속 T085/T086/T089 테스트에도 동일 프로젝트 재사용).
