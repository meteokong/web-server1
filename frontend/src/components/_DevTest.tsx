import { useState } from "react";
import { apiClient, ApiError } from "../services/api-client";

// TEMPORARY manual-testing component for the T020 axios API client.
// Not part of any tasks.md task — remove once a real feature uses apiClient.

export function DevTest() {
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [response, setResponse] = useState<unknown>(null);

  async function handleCallApi() {
    setStatus("loading");
    setResponse(null);
    try {
      const res = await apiClient.get("/health");
      setStatus("success");
      setResponse(res.data);
    } catch (err) {
      setStatus("error");
      if (err instanceof ApiError) {
        setResponse({ status: err.status, code: err.code, message: err.message });
      } else {
        setResponse({ message: String(err) });
      }
    }
  }

  return (
    <div style={{ padding: "1rem", border: "1px solid #ccc", maxWidth: 400 }}>
      <h2>API 클라이언트 테스트 (/dev-test)</h2>
      <p>버튼을 누르면 apiClient.get(&quot;/health&quot;) → 실제 경로 GET /api/v1/health 호출</p>
      <button onClick={handleCallApi} disabled={status === "loading"}>
        {status === "loading" ? "호출 중..." : "API 호출"}
      </button>

      <div style={{ marginTop: "1rem" }}>
        <strong>상태: </strong>
        {status === "idle" && "대기 중"}
        {status === "loading" && "⏳ 요청 중..."}
        {status === "success" && "✅ 성공"}
        {status === "error" && "❌ 에러"}
      </div>

      {response !== null && (
        <pre
          style={{
            marginTop: "0.5rem",
            background: "#f5f5f5",
            padding: "0.5rem",
            whiteSpace: "pre-wrap",
          }}
        >
          {JSON.stringify(response, null, 2)}
        </pre>
      )}
    </div>
  );
}
