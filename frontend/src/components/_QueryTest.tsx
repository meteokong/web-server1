import { useQuery } from "@tanstack/react-query";

// TEMPORARY manual-testing component for the T019 TanStack Query setup.
// Not part of any tasks.md task — remove once query usage has been
// exercised through a real feature (e.g. T034 auth-service).

interface DummyUser {
  id: number;
  name: string;
  fetchedAt: string;
}

function fetchDummyUser(): Promise<DummyUser> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (Math.random() < 0.3) {
        reject(new Error("더미 API 호출 실패 (의도적으로 30% 확률로 실패하게 만듦)"));
        return;
      }
      resolve({
        id: 1,
        name: "테스트 사용자",
        fetchedAt: new Date().toLocaleTimeString("ko-KR"),
      });
    }, 1500);
  });
}

export function QueryTest() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["dummy-user"],
    queryFn: fetchDummyUser,
  });

  return (
    <div style={{ padding: "1rem", border: "1px solid #ccc", maxWidth: 400 }}>
      <h2>TanStack Query 테스트</h2>

      {isLoading && <p>⏳ 로딩 중...</p>}

      {isError && (
        <div>
          <p style={{ color: "red" }}>❌ 에러 발생: {error.message}</p>
          <button onClick={() => refetch()}>다시 시도</button>
        </div>
      )}

      {data && (
        <div>
          <p style={{ color: "green" }}>✅ 성공!</p>
          <p>사용자 ID: {data.id}</p>
          <p>이름: {data.name}</p>
          <p>조회 시각: {data.fetchedAt}</p>
          <button onClick={() => refetch()} disabled={isFetching}>
            {isFetching ? "다시 불러오는 중..." : "다시 불러오기"}
          </button>
        </div>
      )}
    </div>
  );
}
