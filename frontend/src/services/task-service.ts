import { apiClient } from "./api-client";
import type { CodeFile, Task, UploadedCode } from "@/types/task";

/** Shape returned by every tasks endpoint (data-model.md's Task entity). */
interface TaskResponseBody {
  id: string;
  project_id: string;
  task_number: number;
  title: string;
  description: string | null;
  upload_method: "file" | "folder" | "paste";
  created_at: string;
  updated_at: string;
  deletion_status: "active" | "trashed";
  trashed_at: string | null;
  scheduled_deletion_at: string | null;
}

interface TasksListResponseBody {
  tasks: TaskResponseBody[];
}

interface UploadedCodeResponseBody {
  detected_language: string;
  complexity_level: "beginner" | "intermediate" | "advanced";
  total_lines: number;
  total_files: number;
  upload_size_bytes: number;
}

interface CodeFileResponseBody {
  file_name: string;
  file_path: string | null;
  file_extension: string;
  file_size_bytes: number;
}

interface TaskCodeResponseBody {
  uploaded_code: UploadedCodeResponseBody;
  files: CodeFileResponseBody[];
}

export interface TaskCode {
  uploadedCode: UploadedCode;
  files: CodeFile[];
}

function toTask(body: TaskResponseBody): Task {
  return {
    id: body.id,
    projectId: body.project_id,
    taskNumber: body.task_number,
    title: body.title,
    description: body.description,
    uploadMethod: body.upload_method,
    createdAt: body.created_at,
    updatedAt: body.updated_at,
    deletionStatus: body.deletion_status,
    trashedAt: body.trashed_at,
    scheduledDeletionAt: body.scheduled_deletion_at,
  };
}

/** GET /projects/{projectId}/tasks. */
export async function listTasks(projectId: string): Promise<Task[]> {
  const response = await apiClient.get<TasksListResponseBody>(`/projects/${projectId}/tasks`);
  return response.data.tasks.map(toTask);
}

export interface CreateTaskFields {
  title: string;
  description?: string;
  uploadMethod: "file" | "folder" | "paste";
  /** For "file"/"folder" uploads. */
  files?: File[];
  /**
   * For "folder" uploads: each entry in `files` own folder-relative path
   * (e.g. "src/main.py"), same length/order as `files`. Sent as the
   * multipart filename — the backend (tasks.py) derives file_path from it
   * by checking whether the filename contains a path separator.
   */
  relativePaths?: (string | undefined)[];
  /** For "paste" uploads. */
  pastedCode?: string;
  /** For "paste" uploads: the language selected in PasteCode's <select>. */
  pastedLanguage?: string;
}

/** POST /projects/{projectId}/tasks, multipart/form-data. */
export async function createTask(projectId: string, fields: CreateTaskFields): Promise<Task> {
  const formData = new FormData();
  formData.append("title", fields.title);
  if (fields.description) formData.append("description", fields.description);
  formData.append("upload_method", fields.uploadMethod);
  if (fields.files) {
    fields.files.forEach((file, index) => {
      const relativePath = fields.relativePaths?.[index];
      formData.append("files", file, relativePath ?? file.name);
    });
  }
  if (fields.pastedCode !== undefined) {
    formData.append("pasted_code", fields.pastedCode);
  }
  if (fields.pastedLanguage !== undefined) {
    formData.append("language", fields.pastedLanguage);
  }

  const response = await apiClient.post<TaskResponseBody>(
    `/projects/${projectId}/tasks`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return toTask(response.data);
}

/** GET /tasks/{id}. */
export async function getTask(taskId: string): Promise<Task> {
  const response = await apiClient.get<TaskResponseBody>(`/tasks/${taskId}`);
  return toTask(response.data);
}

export interface UpdateTaskFields {
  title?: string;
  description?: string | null;
}

/** PATCH /tasks/{id}. Only the fields present on `fields` are sent (partial update). */
export async function updateTask(taskId: string, fields: UpdateTaskFields): Promise<Task> {
  const response = await apiClient.patch<TaskResponseBody>(`/tasks/${taskId}`, fields);
  return toTask(response.data);
}

/** DELETE /tasks/{id}. Soft-deletes (moves to trash); returns the updated task. */
export async function deleteTask(taskId: string): Promise<Task> {
  const response = await apiClient.delete<TaskResponseBody>(`/tasks/${taskId}`);
  return toTask(response.data);
}

/** GET /tasks/{id}/code. */
export async function getTaskCode(taskId: string): Promise<TaskCode> {
  const response = await apiClient.get<TaskCodeResponseBody>(`/tasks/${taskId}/code`);
  const { uploaded_code, files } = response.data;
  return {
    uploadedCode: {
      detectedLanguage: uploaded_code.detected_language,
      complexityLevel: uploaded_code.complexity_level,
      totalLines: uploaded_code.total_lines,
      totalFiles: uploaded_code.total_files,
      uploadSizeBytes: uploaded_code.upload_size_bytes,
    },
    files: files.map((file) => ({
      fileName: file.file_name,
      filePath: file.file_path,
      fileExtension: file.file_extension,
      fileSizeBytes: file.file_size_bytes,
    })),
  };
}
