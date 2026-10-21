import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProjectCard } from "./ProjectCard";
import type { Project } from "@/types/project";

const project: Project = {
  id: "project-1",
  title: "React 학습",
  description: "React 기초부터 심화까지",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  lastActivityAt: "2026-10-20T06:00:00+00:00",
  deletionStatus: "active",
};

function renderCard(overrides: Partial<Project> = {}) {
  return render(
    <MemoryRouter>
      <ProjectCard project={{ ...project, ...overrides }} />
    </MemoryRouter>,
  );
}

describe("ProjectCard", () => {
  it("renders the project title and description", () => {
    renderCard();

    expect(screen.getByText("React 학습")).toBeInTheDocument();
    expect(screen.getByText("React 기초부터 심화까지")).toBeInTheDocument();
  });

  it("renders a fallback when description is null", () => {
    renderCard({ description: null });

    expect(screen.getByText("설명이 없습니다.")).toBeInTheDocument();
  });

  it("links to the project detail page", () => {
    renderCard();

    expect(screen.getByRole("link", { name: /React 학습/i })).toHaveAttribute(
      "href",
      "/projects/project-1",
    );
  });
});
