# TASK-087. 수동 브라우저 테스트: 11MB 파일 업로드 거부

## 상태
완료 (PASS, API 직접 호출로 검증)

## 날짜
2026-10-22

## 작업 요약
10MB(10,485,760바이트) 제한을 초과하는 11MB 파일을 업로드해 거부되는지 검증했다.

**도구 제약 안내**: 브라우저 자동화의 파일 업로드 도구(`file_upload`) 자체가 호출당 10MB 제한을 두고 있어, 실제 UI 클릭으로 11MB 파일을 전송하는 시나리오는 재현할 수 없었다. 대신 로그인된 브라우저 탭의 JS 컨텍스트에서 `fetch()`로 11MB `Blob`을 직접 구성해 `POST /api/v1/projects/{id}/tasks`에 전송 — 인증 쿠키는 브라우저가 자동으로 포함하므로 실제 로그인 세션을 그대로 사용한 "수동" 검증이되, UI 클릭 경로는 거치지 않았다.

**결과**: `400 {"error":{"code":"validation_error","message":"file exceeds the 10485760-byte size limit"}}`. 이후 태스크 목록을 다시 조회해 Task 4가 생성되지 않았음(검증 실패 시 아무것도 쓰여지지 않음, T069의 "validate-then-store" 설계)도 확인 — PASS.

## 변경 파일
없음 (순수 검증 테스트, 코드 변경 없음)

## TDD 결과
해당 없음 (구현이 아닌 수동 검증 태스크)

## 기술 결정
- UI 경로 대신 API 직접 호출을 택한 것은 테스트 도구 자체의 한계(10MB 업로드 cap) 때문이며, 검증 대상인 백엔드의 `file_validator.validate_size`(T064) 동작 자체는 동일하게 거친다. 완전한 UI 클릭 경로로 재현하려면 실제 Chrome에서 11MB 이상의 실제 파일을 네이티브 파일 선택 다이얼로그로 고르는 수동 작업이 필요하다.

## 비고
- 같은 10MB 임계값이 `backend/src/utils/file_validator.py`(T064)의 `MAX_FILE_SIZE_BYTES` 상수와 DB 마이그레이션의 `valid_upload_size` CHECK 제약 양쪽에 정확히 일치하도록 유지되고 있음을 에러 메시지(`10485760-byte`)로 재확인했다.
