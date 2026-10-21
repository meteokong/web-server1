import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "./api-client";
import {
  createProject,
  deleteProject,
  getProject,
  listProjects,
  updateProject,
} from "./project-service";

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

const projectResponseBody = {
  id: "project-1",
  user_id: "user-1",
  title: "React 학습",
  description: "React 기초부터 심화까지",
  created_at: "2026-10-01T00:00:00+00:00",
  updated_at: "2026-10-01T00:00:00+00:00",
  last_activity_at: "2026-10-20T06:00:00+00:00",
  deletion_status: "active",
  trashed_at: null,
  scheduled_deletion_at: null,
};

const expectedProject = {
  id: "project-1",
  title: "React 학습",
  description: "React 기초부터 심화까지",
  createdAt: "2026-10-01T00:00:00+00:00",
  updatedAt: "2026-10-01T00:00:00+00:00",
  lastActivityAt: "2026-10-20T06:00:00+00:00",
  deletionStatus: "active",
};

describe("project-service", () => {
  beforeEach(() => {
    mockedGet.mockReset();
    mockedPost.mockReset();
    mockedPatch.mockReset();
    mockedDelete.mockReset();
  });

  describe("listProjects", () => {
    it("GETs /projects and unwraps the {projects: [...]} envelope", async () => {
      mockedGet.mockResolvedValue({ data: { projects: [projectResponseBody] } });

      const projects = await listProjects();

      expect(mockedGet).toHaveBeenCalledWith("/projects");
      expect(projects).toEqual([expectedProject]);
    });
  });

  describe("createProject", () => {
    it("POSTs title/description to /projects and returns the created project", async () => {
      mockedPost.mockResolvedValue({ data: projectResponseBody });

      const project = await createProject("React 학습", "React 기초부터 심화까지");

      expect(mockedPost).toHaveBeenCalledWith("/projects", {
        title: "React 학습",
        description: "React 기초부터 심화까지",
      });
      expect(project).toEqual(expectedProject);
    });
  });

  describe("getProject", () => {
    it("GETs /projects/{id} and returns the project", async () => {
      mockedGet.mockResolvedValue({ data: projectResponseBody });

      const project = await getProject("project-1");

      expect(mockedGet).toHaveBeenCalledWith("/projects/project-1");
      expect(project).toEqual(expectedProject);
    });
  });

  describe("updateProject", () => {
    it("PATCHes only the provided fields to /projects/{id}", async () => {
      mockedPatch.mockResolvedValue({ data: projectResponseBody });

      const project = await updateProject("project-1", { title: "React 심화" });

      expect(mockedPatch).toHaveBeenCalledWith("/projects/project-1", { title: "React 심화" });
      expect(project).toEqual(expectedProject);
    });
  });

  describe("deleteProject", () => {
    it("DELETEs /projects/{id} and returns the trashed project", async () => {
      const trashedBody = { ...projectResponseBody, deletion_status: "trashed" };
      mockedDelete.mockResolvedValue({ data: trashedBody });

      const project = await deleteProject("project-1");

      expect(mockedDelete).toHaveBeenCalledWith("/projects/project-1");
      expect(project).toEqual({ ...expectedProject, deletionStatus: "trashed" });
    });
  });
});
