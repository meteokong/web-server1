import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProjectDetail from "./ProjectDetail";
import { getProject } from "@/services/project-service";
import type { Project } from "@/types/project";

vi.mock("@/services/project-service", () => ({
  getProject: vi.fn(),
}));

const mockedGetProject = getProject as unknown as ReturnType<typeof vi.fn>;

const project: Project = {
  id: "project-1",
  title: "React 학습",
  description: "React 기초부터 심화까지",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  lastActivityAt: "2026-10-20T06:00:00+00:00",
  deletionStatus: "active",
};

function renderProjectDetail(projectId = "project-1") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/projects/${projectId}`]}>
        <Routes>
          <Route path="/projects/:projectId" element={<ProjectDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("ProjectDetail", () => {
  it("shows a loading state while the project is being fetched", () => {
    mockedGetProject.mockReturnValue(new Promise(() => {}));

    renderProjectDetail();

    expect(screen.getByText(/로딩/)).toBeInTheDocument();
  });

  it("fetches the project by the :projectId route param and renders its title/description", async () => {
    mockedGetProject.mockResolvedValue(project);

    renderProjectDetail("project-1");

    expect(await screen.findByText("React 학습")).toBeInTheDocument();
    expect(mockedGetProject).toHaveBeenCalledWith("project-1");
    expect(screen.getByText("React 기초부터 심화까지")).toBeInTheDocument();
  });

  it("renders a task-timeline placeholder", async () => {
    mockedGetProject.mockResolvedValue(project);

    renderProjectDetail();

    expect(
      await screen.findByRole("heading", { name: /태스크 타임라인/ }),
    ).toBeInTheDocument();
  });

  it("shows an error message when the fetch fails", async () => {
    mockedGetProject.mockRejectedValue(new Error("프로젝트를 찾을 수 없습니다."));

    renderProjectDetail();

    expect(await screen.findByText("프로젝트를 찾을 수 없습니다.")).toBeInTheDocument();
  });
});
