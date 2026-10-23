import { Link } from "react-router-dom";
import type { Project } from "@/types/project";

export interface ProjectCardProps {
  project: Project;
}

/**
 * Presentational card for one project, used by the Dashboard's project
 * list (T054). Knows nothing about fetching/mutating projects — just
 * renders what it's given and links through to ProjectDetail (T055).
 */
export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <article>
      <h2>
        <Link to={`/projects/${project.id}`}>{project.title}</Link>
      </h2>
      <p>{project.description ?? "설명이 없습니다."}</p>
    </article>
  );
}
