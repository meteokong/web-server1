# TASK-019. TanStack Query 클라이언트 설정

## 상태
완료

## 날짜
2026-10-21

## 작업 요약
프론트엔드가 백엔드 API에서 데이터를 가져올 때, 매번 새로 요청하지 않고 "방금 받아온 데이터를 잠시 기억해두는" 캐시 시스템(TanStack Query)을 설정했습니다. 비유하자면, 매번 도서관(서버)에 가서 책을 빌려오는 대신, 자주 보는 책은 책상 위(캐시)에 잠깐 올려두고 재사용하다가, 시간이 좀 지나면 "혹시 바뀐 내용 없나" 조용히 다시 확인(stale-while-revalidate)하는 방식입니다.

**구현 내용**:
- `@tanstack/react-query` 설치 (research.md "API Client: TanStack Query (React Query) for caching and optimistic updates" 결정에 따름)
- `frontend/src/lib/queryClient.ts`: `QueryClient` 인스턴스를 전역 기본 옵션과 함께 생성
  - `staleTime: 30_000`(30초) — 데이터가 "신선"하다고 간주되는 시간, 그 안에는 재요청 없이 캐시 사용
  - `gcTime: 5 * 60_000`(5분) — 화면을 벗어나도 캐시를 바로 버리지 않고 5분간 보관 (예: 프로젝트 상세 → 대시보드로 돌아올 때 즉시 표시)
  - `retry: 1` — 네트워크 일시 오류는 1회 재시도, 서버가 완전히 죽었을 때 무한 재시도하지 않도록 제한
  - `refetchOnWindowFocus: false` — 창 전환마다 재요청하지 않도록 (불필요한 서버 부하 방지)
  - `mutations.retry: 0` — 생성/수정/삭제(POST/PATCH/DELETE) 요청은 재시도하지 않음(자동 재시도로 중복 생성되는 사고 방지)
- `frontend/src/main.tsx`: `QueryClientProvider`로 `<App />`을 감싸 앱 전체에서 이 캐시를 쓸 수 있게 연결

**검증**:
1. `npm run build` → TypeScript 컴파일 + Vite 빌드 성공 (70개 모듈 정상 변환, 타입 에러 없음)
2. `npm run lint`, `npm run format:check` 모두 통과
3. `npm run dev`로 실제 개발 서버 기동 → `GET /`와 `GET /src/main.tsx` 모두 `200 OK` 확인 (QueryClientProvider가 포함된 진입점 모듈이 에러 없이 서빙됨)
4. `npm audit` → 0 vulnerabilities (TanStack Query 설치 후에도 취약점 없음)

## 변경 파일
- `frontend/package.json`, `frontend/package-lock.json` (`@tanstack/react-query` 추가)
- `frontend/src/lib/queryClient.ts` (신규)
- `frontend/src/main.tsx` (`QueryClientProvider`로 `App` 래핑)

## TDD 결과
tasks.md의 TDD Workflow는 "MANDATORY for ALL implementation tasks (Phases 3-10)"로 범위를 명시해 Phase 2(Foundational)인 이번 Task는 RED-GREEN-REFACTOR 커밋 의무 대상은 아님. 아직 실제로 데이터를 가져올 API 엔드포인트가 없어(T028+에서 구현) 쿼리 훅 단위 테스트는 작성하지 않았고, 빌드/린트/개발 서버 기동으로 "설정이 앱을 깨뜨리지 않는가"를 검증함. 실제 `useQuery`/`useMutation` 동작 테스트는 이 캐시를 사용하는 첫 feature(T034 인증 서비스 등)에서 자연스럽게 이루어질 것.

## 기술 결정 (해당 시)
- `staleTime`/`gcTime` 수치는 data-model.md/research.md에 명시된 값이 없어 React Query 공식 권장 패턴(TanStack 문서의 일반적인 기본값보다 약간 긴 staleTime)을 참고해 임의로 설정함 — 추후 실제 사용 패턴에 따라 T197(API 응답 캐싱 최적화, Polish 단계)에서 세부 조정 가능
- `mutations.retry: 0`은 명시된 요구사항은 아니지만, POST 요청의 자동 재시도가 "같은 프로젝트/태스크를 두 번 생성"하는 사고로 이어질 수 있어 안전한 기본값으로 선택함

## 비고
- React Query Devtools는 설치하지 않음 — tasks.md에 명시된 요구사항이 아니며, 필요 시 별도로 추가 가능
- 다음 Task(T020: axios 기반 API client, T021: Zustand auth store)가 완성되면 이 `queryClient`를 사용하는 실제 `useQuery`/`useMutation` 훅들이 서비스 레이어(T034 등)에 작성될 예정
