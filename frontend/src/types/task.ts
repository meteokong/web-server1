/**
 * Frontend-shape of a task, as returned by task-service.ts (T080) after
 * mapping the backend's snake_case TaskResponse (see data-model.md's Task
 * entity).
 */
export interface Task {
  id: string;
  projectId: string;
  taskNumber: number;
  title: string;
  description: string | null;
  uploadMethod: "file" | "folder" | "paste";
  createdAt: string;
  updatedAt: string;
  deletionStatus: "active" | "trashed";
  trashedAt: string | null;
  scheduledDeletionAt: string | null;
}
