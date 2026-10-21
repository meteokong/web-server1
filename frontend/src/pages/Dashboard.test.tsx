import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Dashboard from "./Dashboard";
import { listProjects } from "@/services/project-service";
import type { Project } from "@/types/project";

vi.mock("@/services/project-service", () => ({
  listProjects: vi.fn(),
}));

const mockedListProjects = listProjects as unknown as ReturnType<typeof vi.fn>;

const projects: Project[] = [
  {
    id: "project-1",
    title: "React 학습",
    description: "React 기초부터 심화까지",
    createdAt: "2026-10-01T00:00:00+00:00",
    updatedAt: "2026-10-01T00:00:00+00:00",
    lastActivityAt: "2026-10-20T06:00:00+00:00",
    deletionStatus: "active",
  },
];

function renderDashboard() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Dashboard", () => {
  it("shows a loading state while projects are being fetched", () => {
    mockedListProjects.mockReturnValue(new Promise(() => {}));

    renderDashboard();

    expect(screen.getByText(/로딩/)).toBeInTheDocument();
  });

  it("renders a ProjectCard for each fetched project", async () => {
    mockedListProjects.mockResolvedValue(projects);

    renderDashboard();

    expect(await screen.findByText("React 학습")).toBeInTheDocument();
  });

  it("shows an empty-state message when there are no projects", async () => {
    mockedListProjects.mockResolvedValue([]);

    renderDashboard();

    expect(await screen.findByText(/아직 프로젝트가 없습니다/)).toBeInTheDocument();
  });

  it("shows an error message when the fetch fails", async () => {
    mockedListProjects.mockRejectedValue(new Error("네트워크 오류"));

    renderDashboard();

    expect(await screen.findByText(/네트워크 오류/)).toBeInTheDocument();
  });

  it("renders a button to open the create-project modal", async () => {
    mockedListProjects.mockResolvedValue([]);

    renderDashboard();

    expect(
      await screen.findByRole("button", { name: /새 프로젝트/i }),
    ).toBeInTheDocument();
  });
});
