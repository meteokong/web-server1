import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "./api-client";
import { documentStatusPollIntervalMs, getDocument, getDocumentStatus } from "./document-service";

vi.mock("./api-client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockedGet = apiClient.get as unknown as ReturnType<typeof vi.fn>;

const statusResponseBody = {
  task_id: "task-1",
  generation_status: "in_progress",
  generation_error: null,
  generation_started_at: "2026-10-22T00:00:00+00:00",
  generation_completed_at: null,
};

const expectedStatus = {
  taskId: "task-1",
  generationStatus: "in_progress",
  generationError: null,
  generationStartedAt: "2026-10-22T00:00:00+00:00",
  generationCompletedAt: null,
};

const chapterContentBody = {
  chapter1: { title: "What This Code Does", summary: "배열을 정렬한다." },
  chapter2: {
    title: "Prerequisites Knowledge",
    concepts: [
      {
        name: "재귀함수",
        explanation: "자기 자신을 호출하는 함수",
        analogy: "러시안 인형",
        example: "f(n) = f(n-1)",
        use_cases: "분할정복",
      },
    ],
  },
  chapter3: {
    title: "Code Structure Overview",
    flowchart: "main -> sort",
    file_breakdown: { "main.py": "엔트리 포인트" },
  },
  chapter4: {
    title: "Line-by-Line Explanation",
    explanations: [
      {
        line: 1,
        code: "def sort(arr):",
        explanation: "정렬 함수를 정의한다.",
        analogy: "요리 레시피",
        alternative_example: "def noop(): pass",
        notes: "주의사항 없음",
      },
    ],
  },
  chapter5: { title: "Execution Flow Simulation", steps: [{ step: 1, description: "입력받는다." }] },
  chapter6: {
    title: "Core Concepts Summary",
    concepts: [
      {
        name: "재귀함수",
        what_it_is: "자기 호출",
        why_its_used: "반복을 간결하게 표현",
        where_its_applied: "트리 순회",
      },
    ],
  },
  chapter7: {
    title: "Common Mistakes",
    mistakes: [
      { wrong: "종료 조건 없음", right: "종료 조건 명시", why: "무한 재귀", fix: "base case 추가" },
    ],
  },
};

const documentResponseBody = {
  task_id: "task-1",
  generation_status: "completed",
  generation_error: null,
  content: chapterContentBody,
};

describe("document-service", () => {
  beforeEach(() => {
    mockedGet.mockReset();
  });

  describe("getDocumentStatus", () => {
    it("GETs /tasks/{id}/document/status and maps snake_case to camelCase", async () => {
      mockedGet.mockResolvedValue({ data: statusResponseBody });

      const status = await getDocumentStatus("task-1");

      expect(mockedGet).toHaveBeenCalledWith("/tasks/task-1/document/status");
      expect(status).toEqual(expectedStatus);
    });
  });

  describe("getDocument", () => {
    it("GETs /tasks/{id}/document and maps the envelope + 7-chapter content to camelCase", async () => {
      mockedGet.mockResolvedValue({ data: documentResponseBody });

      const document = await getDocument("task-1");

      expect(mockedGet).toHaveBeenCalledWith("/tasks/task-1/document");
      expect(document.taskId).toBe("task-1");
      expect(document.generationStatus).toBe("completed");
      expect(document.generationError).toBeNull();
      expect(document.content?.chapter1).toEqual({
        title: "What This Code Does",
        summary: "배열을 정렬한다.",
      });
      expect(document.content?.chapter2.concepts[0]).toEqual({
        name: "재귀함수",
        explanation: "자기 자신을 호출하는 함수",
        analogy: "러시안 인형",
        example: "f(n) = f(n-1)",
        useCases: "분할정복",
      });
      expect(document.content?.chapter3).toEqual({
        title: "Code Structure Overview",
        flowchart: "main -> sort",
        fileBreakdown: { "main.py": "엔트리 포인트" },
      });
      expect(document.content?.chapter4.explanations[0]).toEqual({
        line: 1,
        code: "def sort(arr):",
        explanation: "정렬 함수를 정의한다.",
        analogy: "요리 레시피",
        alternativeExample: "def noop(): pass",
        notes: "주의사항 없음",
      });
      expect(document.content?.chapter6.concepts[0]).toEqual({
        name: "재귀함수",
        whatItIs: "자기 호출",
        whyItsUsed: "반복을 간결하게 표현",
        whereItsApplied: "트리 순회",
      });
    });

    it("returns null content when generation isn't completed", async () => {
      mockedGet.mockResolvedValue({
        data: {
          task_id: "task-1",
          generation_status: "pending",
          generation_error: null,
          content: null,
        },
      });

      const document = await getDocument("task-1");

      expect(document.content).toBeNull();
    });
  });

  describe("documentStatusPollIntervalMs", () => {
    it("returns a poll interval while generation is pending or in progress", () => {
      expect(documentStatusPollIntervalMs("pending")).toBe(4000);
      expect(documentStatusPollIntervalMs("in_progress")).toBe(4000);
    });

    it("returns false (stop polling) once generation reaches a terminal state", () => {
      expect(documentStatusPollIntervalMs("completed")).toBe(false);
      expect(documentStatusPollIntervalMs("failed")).toBe(false);
    });

    it("returns false before the first status fetch resolves", () => {
      expect(documentStatusPollIntervalMs(undefined)).toBe(false);
    });
  });
});
