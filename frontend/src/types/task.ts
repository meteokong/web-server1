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

/** Frontend-shape of a task's uploaded code summary (GET /tasks/{id}/code). */
export interface UploadedCode {
  detectedLanguage: string;
  complexityLevel: "beginner" | "intermediate" | "advanced";
  totalLines: number;
  totalFiles: number;
  uploadSizeBytes: number;
}

/** Frontend-shape of one file within a task's uploaded code. */
export interface CodeFile {
  fileName: string;
  filePath: string | null;
  fileExtension: string;
  fileSizeBytes: number;
}
