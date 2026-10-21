/**
 * Frontend-shape of a project, as returned by project-service.ts (T053)
 * after mapping the backend's snake_case ProjectResponse (see
 * specs/001-ai-code-learning-platform/contracts/projects-api.md).
 *
 * Lives in its own module (rather than inside project-service.ts) so
 * presentational components like ProjectCard (T051) and
 * CreateProjectModal (T052) can depend on the shape without depending
 * on the service module itself.
 */
export interface Project {
  id: string;
  title: string;
  description: string | null;
  createdAt: string;
  updatedAt: string;
  lastActivityAt: string;
  deletionStatus: "active" | "trashed";
}
