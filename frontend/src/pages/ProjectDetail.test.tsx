import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ProjectDetail from "./ProjectDetail";
import { deleteProject, getProject, updateProject } from "@/services/project-service";
import { createTask, listTasks } from "@/services/task-service";
import type { Project } from "@/types/project";
import type { Task } from "@/types/task";

vi.mock("@/services/project-service", () => ({
  getProject: vi.fn(),
  updateProject: vi.fn(),
  deleteProject: vi.fn(),
}));

vi.mock("@/services/task-service", () => ({
  listTasks: vi.fn(),
  createTask: vi.fn(),
}));

const mockedGetProject = getProject as unknown as ReturnType<typeof vi.fn>;
const mockedUpdateProject = updateProject as unknown as ReturnType<typeof vi.fn>;
const mockedDeleteProject = deleteProject as unknown as ReturnType<typeof vi.fn>;
const mockedListTasks = listTasks as unknown as ReturnType<typeof vi.fn>;
const mockedCreateTask = createTask as unknown as ReturnType<typeof vi.fn>;

const project: Project = {
  id: "project-1",
  title: "React 학습",
  description: "React 기초부터 심화까지",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  lastActivityAt: "2026-10-20T06:00:00+00:00",
  deletionStatus: "active",
};

const tasks: Task[] = [
  {
    id: "task-1",
    projectId: "project-1",
    taskNumber: 1,
    title: "배열 정렬 연습",
    description: "버블 정렬 구현",
    uploadMethod: "paste",
    createdAt: "2026-10-02T00:00:00+00:00",
    updatedAt: "2026-10-02T00:00:00+00:00",
    deletionStatus: "active",
    trashedAt: null,
    scheduledDeletionAt: null,
  },
];

const newTask: Task = {
  id: "task-2",
  projectId: "project-1",
  taskNumber: 2,
  title: "링크드리스트 연습",
  description: null,
  uploadMethod: "paste",
  createdAt: "2026-10-22T00:00:00+00:00",
  updatedAt: "2026-10-22T00:00:00+00:00",
  deletionStatus: "active",
  trashedAt: null,
  scheduledDeletionAt: null,
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
  beforeEach(() => {
    mockedListTasks.mockReset();
    mockedCreateTask.mockReset();
    mockedListTasks.mockResolvedValue([]);
  });

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

  it("renders a TaskCard for each fetched task", async () => {
    mockedGetProject.mockResolvedValue(project);
    mockedListTasks.mockResolvedValue(tasks);

    renderProjectDetail();

    expect(await screen.findByText("배열 정렬 연습")).toBeInTheDocument();
    expect(mockedListTasks).toHaveBeenCalledWith("project-1");
  });

  it("shows an empty-state message when the project has no tasks", async () => {
    mockedGetProject.mockResolvedValue(project);
    mockedListTasks.mockResolvedValue([]);

    renderProjectDetail();

    expect(await screen.findByText(/아직 태스크가 없습니다/)).toBeInTheDocument();
  });

  it("renders a button to open the create-task modal", async () => {
    mockedGetProject.mockResolvedValue(project);

    renderProjectDetail();

    expect(await screen.findByRole("button", { name: /새 태스크/i })).toBeInTheDocument();
  });

  it("opens the create-task modal when the button is clicked", async () => {
    mockedGetProject.mockResolvedValue(project);
    const user = userEvent.setup();

    renderProjectDetail();

    await user.click(await screen.findByRole("button", { name: /새 태스크/i }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("creates a task via task-service and shows it in the list without a manual reload", async () => {
    mockedGetProject.mockResolvedValue(project);
    mockedListTasks.mockResolvedValueOnce(tasks).mockResolvedValueOnce([...tasks, newTask]);
    mockedCreateTask.mockResolvedValue(newTask);
    const user = userEvent.setup();

    renderProjectDetail();

    await user.click(await screen.findByRole("button", { name: /새 태스크/i }));
    await user.type(screen.getByLabelText(/제목/i), "링크드리스트 연습");
    await user.click(screen.getByRole("radio", { name: /코드 붙여넣기/i }));
    await user.type(screen.getByLabelText(/^코드$/i), "print(1)");
    await user.click(screen.getByRole("button", { name: /생성/i }));

    expect(await screen.findByText("링크드리스트 연습")).toBeInTheDocument();
    expect(mockedCreateTask).toHaveBeenCalledWith(
      "project-1",
      expect.objectContaining({ title: "링크드리스트 연습", uploadMethod: "paste" }),
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
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
