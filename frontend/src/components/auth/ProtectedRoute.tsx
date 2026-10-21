import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";

/**
 * Auth guard for nested routes (used as a layout route: <Route
 * element={<ProtectedRoute />}>...child routes...</Route>). While the
 * app's first GET /auth/me (T038's useAuth hook) hasn't resolved yet,
 * isInitializing is true and we render nothing rather than redirecting
 * — redirecting too early would bounce an already-logged-in user to
 * /login for a flash before their session is confirmed.
 */
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitializing = useAuthStore((state) => state.isInitializing);

  if (isInitializing) {
    return null;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
