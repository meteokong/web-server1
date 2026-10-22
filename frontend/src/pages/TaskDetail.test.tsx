import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import TaskDetail from "./TaskDetail";
import { getTask } from "@/services/task-service";
import type { Task } from "@/types/task";

vi.mock("@/services/task-service", () => ({
  getTask: vi.fn(),
}));

// DocumentViewer (T105/T107) does its own data-fetching (document-service,
// task-service, Monaco) — TaskDetail only needs to pass it the taskId, so
// it's stubbed here to keep this file focused on the tab wiring.
vi.mock("@/components/document/DocumentViewer", () => ({
  default: ({ taskId }: { taskId: string }) => (
    <div data-testid="document-viewer">{taskId}</div>
  ),
}));

const mockedGetTask = getTask as unknown as ReturnType<typeof vi.fn>;

const task: Task = {
  id: "task-1",
  projectId: "project-1",
  taskNumber: 1,
  title: "배열 정렬 연습",
  description: "버블 정렬 구현",
  uploadMethod: "paste",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  deletionStatus: "active",
  trashedAt: null,
  scheduledDeletionAt: null,
};

function renderTaskDetail() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/projects/project-1/tasks/task-1"]}>
        <Routes>
          <Route path="/projects/:projectId/tasks/:taskId" element={<TaskDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("TaskDetail", () => {
  it("shows a loading state while the task is being fetched", () => {
    mockedGetTask.mockReturnValue(new Promise(() => {}));

    renderTaskDetail();

    expect(screen.getByText(/로딩/)).toBeInTheDocument();
  });

  it("fetches the task by the :taskId route param and renders its title", async () => {
    mockedGetTask.mockResolvedValue(task);

    renderTaskDetail();

    expect(await screen.findByText("배열 정렬 연습")).toBeInTheDocument();
    expect(mockedGetTask).toHaveBeenCalledWith("task-1");
  });

  it("shows an error message when the fetch fails", async () => {
    mockedGetTask.mockRejectedValue(new Error("태스크를 찾을 수 없습니다."));

    renderTaskDetail();

    expect(await screen.findByText("태스크를 찾을 수 없습니다.")).toBeInTheDocument();
  });

  it("renders Document/Practice/Q&A tabs, defaulting to the DocumentViewer for this task", async () => {
    mockedGetTask.mockResolvedValue(task);

    renderTaskDetail();
    await screen.findByText("배열 정렬 연습");

    expect(screen.getByRole("tab", { name: /문서/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /연습/i })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: /질의응답|Q&A/i })).toBeInTheDocument();
    expect(screen.getByTestId("document-viewer")).toHaveTextContent("task-1");
  });

  it("switches to the Practice tab's placeholder when clicked", async () => {
    mockedGetTask.mockResolvedValue(task);
    const user = userEvent.setup();

    renderTaskDetail();
    await screen.findByText("배열 정렬 연습");

    await user.click(screen.getByRole("tab", { name: /연습/i }));

    expect(screen.getByRole("tabpanel")).toHaveTextContent(/아직 구현되지 않았습니다/);
  });
});
