import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "./api-client";
import {
  createTask,
  deleteTask,
  getTask,
  getTaskCode,
  listTasks,
  updateTask,
} from "./task-service";

vi.mock("./api-client", () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

const mockedGet = apiClient.get as unknown as ReturnType<typeof vi.fn>;
const mockedPost = apiClient.post as unknown as ReturnType<typeof vi.fn>;
const mockedPatch = apiClient.patch as unknown as ReturnType<typeof vi.fn>;
const mockedDelete = apiClient.delete as unknown as ReturnType<typeof vi.fn>;

const taskResponseBody = {
  id: "task-1",
  project_id: "project-1",
  task_number: 1,
  title: "배열 정렬 연습",
  description: "버블 정렬 구현",
  upload_method: "file",
  created_at: "2026-10-01T00:00:00+00:00",
  updated_at: "2026-10-01T00:00:00+00:00",
  deletion_status: "active",
  trashed_at: null,
  scheduled_deletion_at: null,
};

const expectedTask = {
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

describe("task-service", () => {
  beforeEach(() => {
    mockedGet.mockReset();
    mockedPost.mockReset();
    mockedPatch.mockReset();
    mockedDelete.mockReset();
  });

  describe("listTasks", () => {
    it("GETs /projects/{id}/tasks and unwraps the {tasks: [...]} envelope", async () => {
      mockedGet.mockResolvedValue({ data: { tasks: [taskResponseBody] } });

      const tasks = await listTasks("project-1");

      expect(mockedGet).toHaveBeenCalledWith("/projects/project-1/tasks");
      expect(tasks).toEqual([expectedTask]);
    });
  });

  describe("createTask", () => {
    it("POSTs multipart form-data with title/description/uploadMethod/files for a file upload", async () => {
      mockedPost.mockResolvedValue({ data: taskResponseBody });
      const file = new File(["code"], "a.py", { type: "text/plain" });

      const task = await createTask("project-1", {
        title: "배열 정렬 연습",
        description: "버블 정렬 구현",
        uploadMethod: "file",
        files: [file],
      });

      expect(mockedPost).toHaveBeenCalledWith(
        "/projects/project-1/tasks",
        expect.any(FormData),
        expect.objectContaining({ headers: { "Content-Type": "multipart/form-data" } }),
      );
      const formData = mockedPost.mock.calls[0][1] as FormData;
      expect(formData.get("title")).toBe("배열 정렬 연습");
      expect(formData.get("description")).toBe("버블 정렬 구현");
      expect(formData.get("upload_method")).toBe("file");
      expect(formData.getAll("files").length).toBe(1);
      expect(task).toEqual(expectedTask);
    });

    it("sends pasted_code for a paste upload", async () => {
      mockedPost.mockResolvedValue({ data: taskResponseBody });

      await createTask("project-1", {
        title: "배열 정렬 연습",
        uploadMethod: "paste",
        pastedCode: "print(1)",
      });

      const formData = mockedPost.mock.calls[0][1] as FormData;
      expect(formData.get("upload_method")).toBe("paste");
      expect(formData.get("pasted_code")).toBe("print(1)");
    });
  });

  describe("getTask", () => {
    it("GETs /tasks/{id} and returns the task", async () => {
      mockedGet.mockResolvedValue({ data: taskResponseBody });

      const task = await getTask("task-1");

      expect(mockedGet).toHaveBeenCalledWith("/tasks/task-1");
      expect(task).toEqual(expectedTask);
    });
  });

  describe("updateTask", () => {
    it("PATCHes only the provided fields to /tasks/{id}", async () => {
      mockedPatch.mockResolvedValue({ data: taskResponseBody });

      const task = await updateTask("task-1", { title: "배열 정렬 연습 (수정)" });

      expect(mockedPatch).toHaveBeenCalledWith("/tasks/task-1", {
        title: "배열 정렬 연습 (수정)",
      });
      expect(task).toEqual(expectedTask);
    });
  });

  describe("deleteTask", () => {
    it("DELETEs /tasks/{id} and returns the trashed task", async () => {
      const trashedBody = { ...taskResponseBody, deletion_status: "trashed" };
      mockedDelete.mockResolvedValue({ data: trashedBody });

      const task = await deleteTask("task-1");

      expect(mockedDelete).toHaveBeenCalledWith("/tasks/task-1");
      expect(task).toEqual({ ...expectedTask, deletionStatus: "trashed" });
    });
  });

  describe("getTaskCode", () => {
    it("GETs /tasks/{id}/code and maps uploadedCode + files to camelCase", async () => {
      mockedGet.mockResolvedValue({
        data: {
          uploaded_code: {
            detected_language: "python",
            complexity_level: "beginner",
            total_lines: 42,
            total_files: 1,
            upload_size_bytes: 1024,
          },
          files: [
            {
              file_name: "a.py",
              file_path: "a.py",
              file_extension: ".py",
              file_size_bytes: 1024,
            },
          ],
        },
      });

      const code = await getTaskCode("task-1");

      expect(mockedGet).toHaveBeenCalledWith("/tasks/task-1/code");
      expect(code).toEqual({
        uploadedCode: {
          detectedLanguage: "python",
          complexityLevel: "beginner",
          totalLines: 42,
          totalFiles: 1,
          uploadSizeBytes: 1024,
        },
        files: [
          {
            fileName: "a.py",
            filePath: "a.py",
            fileExtension: ".py",
            fileSizeBytes: 1024,
          },
        ],
      });
    });
  });
});
