import { useAuthStore } from "../stores/auth-store";

// TEMPORARY manual-testing component for the T021 Zustand auth store.
// Not part of any tasks.md task — remove once a real feature uses useAuthStore.

/** Subscribes ONLY to `user` via selector — re-renders only when `user` changes. */
function UserDisplay() {
  const user = useAuthStore((state) => state.user);
  // Computed fresh on every render (no hook needed) — if this timestamp
  // changes when a button is clicked, this component just re-rendered.
  const renderedAt = new Date().toLocaleTimeString("ko-KR", { hour12: false });

  return (
    <div style={{ border: "1px solid #999", padding: "0.5rem", marginBottom: "0.5rem" }}>
      <strong>컴포넌트 A: user</strong> (마지막 렌더링: {renderedAt})
      <pre style={{ background: "#f5f5f5", padding: "0.5rem" }}>
        {user ? JSON.stringify(user, null, 2) : "null (로그인 안 됨)"}
      </pre>
    </div>
  );
}

/** Subscribes ONLY to `isAuthenticated` via selector — re-renders only when that changes. */
function AuthStatusDisplay() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const renderedAt = new Date().toLocaleTimeString("ko-KR", { hour12: false });

  return (
    <div style={{ border: "1px solid #999", padding: "0.5rem", marginBottom: "0.5rem" }}>
      <strong>컴포넌트 B: isAuthenticated</strong> (마지막 렌더링: {renderedAt})
      <pre style={{ background: "#f5f5f5", padding: "0.5rem" }}>
        {isAuthenticated ? "true (로그인 됨)" : "false (로그인 안 됨)"}
      </pre>
    </div>
  );
}

export function AuthStoreTest() {
  const setUser = useAuthStore((state) => state.setUser);
  const clearUser = useAuthStore((state) => state.clearUser);

  function handleSetUser() {
    setUser({
      id: "test-user-1",
      email: "student@example.com",
      skillLevel: "Complete Beginner",
    });
  }

  function handleClearAuth() {
    clearUser();
  }

  return (
    <div style={{ padding: "1rem", border: "1px solid #ccc", maxWidth: 400, marginTop: "1rem" }}>
      <h2>Zustand 인증 스토어 테스트</h2>
      <p>버튼을 누르면 두 컴포넌트(A, B)가 서로 독립적으로, 동시에 업데이트되는지 확인합니다.</p>

      <UserDisplay />
      <AuthStatusDisplay />

      <button onClick={handleSetUser} style={{ marginRight: "0.5rem" }}>
        사용자 설정
      </button>
      <button onClick={handleClearAuth}>인증 초기화</button>
    </div>
  );
}
