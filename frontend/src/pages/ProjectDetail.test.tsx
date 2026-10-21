import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProjectDetail from "./ProjectDetail";
import { deleteProject, getProject, updateProject } from "@/services/project-service";
import type { Project } from "@/types/project";

vi.mock("@/services/project-service", () => ({
  getProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
}));

const mockedGetProject = getProject as unknown as ReturnType<typeof vi.fn>;
const mockedUpdateProject = updateProject as unknown as ReturnType<typeof vi.fn>;
const mockedDeleteProject = deleteProject as unknown as ReturnType<typeof vi.fn>;

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

  it("lets the user edit the title and persists it via updateProject", async () => {
    const user = userEvent.setup();
    mockedGetProject.mockResolvedValue(project);
    mockedUpdateProject.mockResolvedValue({ ...project, title: "React 심화" });

    renderProjectDetail("project-1");
    await screen.findByText("React 학습");

    await user.click(screen.getByRole("button", { name: "제목 수정" }));
    const input = screen.getByRole("textbox", { name: "제목" });
    await user.clear(input);
    await user.type(input, "React 심화");
    await user.click(screen.getByRole("button", { name: "저장" }));

    expect(mockedUpdateProject).toHaveBeenCalledWith("project-1", { title: "React 심화" });
    expect(await screen.findByText("React 심화")).toBeInTheDocument();
  });

  it("deletes the project via deleteProject and navigates back to the dashboard", async () => {
    const user = userEvent.setup();
    mockedGetProject.mockResolvedValue(project);
    mockedDeleteProject.mockResolvedValue({ ...project, deletionStatus: "trashed" });

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/projects/project-1"]}>
          <Routes>
            <Route path="/projects/:projectId" element={<ProjectDetail />} />
            <Route path="/" element={<div>대시보드 페이지</div>} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
    await screen.findByText("React 학습");

    await user.click(screen.getByRole("button", { name: "삭제" }));

    expect(mockedDeleteProject).toHaveBeenCalledWith("project-1");
    expect(await screen.findByText("대시보드 페이지")).toBeInTheDocument();
  });
});
