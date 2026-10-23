import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { TaskCard } from "./TaskCard";
import type { Task } from "@/types/task";

const task: Task = {
  id: "task-1",
  projectId: "project-1",
  taskNumber: 1,
  title: "배열 정렬 연습",
  description: "버블 정렬 구현",
  uploadMethod: "file",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  deletionStatus: "active",
  trashedAt: null,
  scheduledDeletionAt: null,
};

function renderCard(overrides: Partial<Task> = {}) {
  return render(
    <MemoryRouter>
      <TaskCard task={{ ...task, ...overrides }} />
    </MemoryRouter>,
  );
}

describe("TaskCard", () => {
  it("renders the task title and task number label", () => {
    renderCard();

    expect(screen.getByText("배열 정렬 연습")).toBeInTheDocument();
    expect(screen.getByText(/Task 1/)).toBeInTheDocument();
  });

  it("links to the task detail page", () => {
    renderCard();

    expect(screen.getByRole("link", { name: /배열 정렬 연습/i })).toHaveAttribute(
      "href",
      "/projects/project-1/tasks/task-1",
    );
  });
});
