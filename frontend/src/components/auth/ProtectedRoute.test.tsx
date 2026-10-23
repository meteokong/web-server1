import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { useAuthStore } from "../../stores/auth-store";
import { ProtectedRoute } from "./ProtectedRoute";

function renderProtected() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<div>대시보드 내용</div>} />
        </Route>
        <Route path="/login" element={<div>로그인 페이지</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ProtectedRoute", () => {
  it("renders nothing while auth status is still initializing", () => {
    useAuthStore.setState({ user: null, isAuthenticated: false, isInitializing: true });
    renderProtected();

    expect(screen.queryByText("대시보드 내용")).not.toBeInTheDocument();
    expect(screen.queryByText("로그인 페이지")).not.toBeInTheDocument();
  });

  it("redirects to /login once initialized and not authenticated", () => {
    useAuthStore.setState({ user: null, isAuthenticated: false, isInitializing: false });
    renderProtected();

    expect(screen.getByText("로그인 페이지")).toBeInTheDocument();
    expect(screen.queryByText("대시보드 내용")).not.toBeInTheDocument();
  });

  it("renders the protected content once initialized and authenticated", () => {
    useAuthStore.setState({
      user: { id: "1", email: "a@b.com", skillLevel: "Complete Beginner" },
      isAuthenticated: true,
      isInitializing: false,
    });
    renderProtected();

    expect(screen.getByText("대시보드 내용")).toBeInTheDocument();
    expect(screen.queryByText("로그인 페이지")).not.toBeInTheDocument();
  });
});
