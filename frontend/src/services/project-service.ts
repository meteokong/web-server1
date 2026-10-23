import { apiClient } from "./api-client";
import type { Project } from "@/types/project";

/** Shape returned by every projects endpoint (projects-api.md's ProjectResponse). */
interface ProjectResponseBody {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  deletion_status: "active" | "trashed";
  trashed_at: string | null;
  scheduled_deletion_at: string | null;
}

interface ProjectsListResponseBody {
  projects: ProjectResponseBody[];
}

function toProject(body: ProjectResponseBody): Project {
  return {
    id: body.id,
    title: body.title,
    description: body.description,
    createdAt: body.created_at,
    updatedAt: body.updated_at,
    lastActivityAt: body.last_activity_at,
    deletionStatus: body.deletion_status,
  };
}

/** GET /projects. Returns active projects only, newest first (per contract). */
export async function listProjects(): Promise<Project[]> {
  const response = await apiClient.get<ProjectsListResponseBody>("/projects");
  return response.data.projects.map(toProject);
}

/** POST /projects. */
export async function createProject(
  title: string,
  description: string | null = null,
): Promise<Project> {
  const response = await apiClient.post<ProjectResponseBody>("/projects", {
    title,
    description,
  });
  return toProject(response.data);
}

/** GET /projects/{id}. */
export async function getProject(projectId: string): Promise<Project> {
  const response = await apiClient.get<ProjectResponseBody>(`/projects/${projectId}`);
  return toProject(response.data);
}

export interface UpdateProjectFields {
  title?: string;
  description?: string | null;
}

/** PATCH /projects/{id}. Only the fields present on `fields` are sent (partial update). */
export async function updateProject(
  projectId: string,
  fields: UpdateProjectFields,
): Promise<Project> {
  const response = await apiClient.patch<ProjectResponseBody>(`/projects/${projectId}`, fields);
  return toProject(response.data);
}

/** DELETE /projects/{id}. Soft-deletes (moves to trash); returns the updated project. */
export async function deleteProject(projectId: string): Promise<Project> {
  const response = await apiClient.delete<ProjectResponseBody>(`/projects/${projectId}`);
  return toProject(response.data);
}
