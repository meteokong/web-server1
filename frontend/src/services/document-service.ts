import { apiClient } from "./api-client";
import type {
  Chapter2Concept,
  Chapter4Explanation,
  Chapter6Concept,
  DocumentContent,
  DocumentGenerationStatus,
  DocumentStatus,
  TaskDocument,
} from "@/types/document";

interface DocumentStatusResponseBody {
  task_id: string;
  generation_status: DocumentGenerationStatus;
  generation_error: string | null;
  generation_started_at: string | null;
  generation_completed_at: string | null;
}

interface Chapter2ConceptResponseBody {
  name: string;
  explanation: string;
  analogy: string;
  example: string;
  use_cases: string;
}

interface Chapter4ExplanationResponseBody {
  line: number;
  code: string;
  explanation: string;
  analogy: string;
  alternative_example: string;
  notes: string;
}

interface Chapter6ConceptResponseBody {
  name: string;
  what_it_is: string;
  why_its_used: string;
  where_its_applied: string;
}

interface DocumentContentResponseBody {
  chapter1: { title: string; summary: string };
  chapter2: { title: string; concepts: Chapter2ConceptResponseBody[] };
  chapter3: { title: string; flowchart: string; file_breakdown: Record<string, string> };
  chapter4: { title: string; explanations: Chapter4ExplanationResponseBody[] };
  chapter5: { title: string; steps: { step: number; description: string }[] };
  chapter6: { title: string; concepts: Chapter6ConceptResponseBody[] };
  chapter7: {
    title: string;
    mistakes: { wrong: string; right: string; why: string; fix: string }[];
  };
}

interface DocumentResponseBody {
  task_id: string;
  generation_status: DocumentGenerationStatus;
  generation_error: string | null;
  content: DocumentContentResponseBody | null;
}

function toChapter2Concept(body: Chapter2ConceptResponseBody): Chapter2Concept {
  return {
    name: body.name,
    explanation: body.explanation,
    analogy: body.analogy,
    example: body.example,
    useCases: body.use_cases,
  };
}

function toChapter4Explanation(body: Chapter4ExplanationResponseBody): Chapter4Explanation {
  return {
    line: body.line,
    code: body.code,
    explanation: body.explanation,
    analogy: body.analogy,
    alternativeExample: body.alternative_example,
    notes: body.notes,
  };
}

function toChapter6Concept(body: Chapter6ConceptResponseBody): Chapter6Concept {
  return {
    name: body.name,
    whatItIs: body.what_it_is,
    whyItsUsed: body.why_its_used,
    whereItsApplied: body.where_its_applied,
  };
}

function toDocumentContent(body: DocumentContentResponseBody): DocumentContent {
  return {
    chapter1: { title: body.chapter1.title, summary: body.chapter1.summary },
    chapter2: {
      title: body.chapter2.title,
      concepts: body.chapter2.concepts.map(toChapter2Concept),
    },
    chapter3: {
      title: body.chapter3.title,
      flowchart: body.chapter3.flowchart,
      fileBreakdown: body.chapter3.file_breakdown,
    },
    chapter4: {
      title: body.chapter4.title,
      explanations: body.chapter4.explanations.map(toChapter4Explanation),
    },
    chapter5: {
      title: body.chapter5.title,
      steps: body.chapter5.steps,
    },
    chapter6: {
      title: body.chapter6.title,
      concepts: body.chapter6.concepts.map(toChapter6Concept),
    },
    chapter7: {
      title: body.chapter7.title,
      mistakes: body.chapter7.mistakes,
    },
  };
}

/**
 * GET /tasks/{id}/document/status. Intended to be polled with TanStack
 * Query's `refetchInterval` (e.g. 3-5s) until generationStatus reaches
 * "completed" or "failed" (T107 stops polling at that point).
 */
export async function getDocumentStatus(taskId: string): Promise<DocumentStatus> {
  const response = await apiClient.get<DocumentStatusResponseBody>(
    `/tasks/${taskId}/document/status`,
  );
  const body = response.data;
  return {
    taskId: body.task_id,
    generationStatus: body.generation_status,
    generationError: body.generation_error,
    generationStartedAt: body.generation_started_at,
    generationCompletedAt: body.generation_completed_at,
  };
}

/** GET /tasks/{id}/document. `content` is null unless generationStatus is "completed". */
export async function getDocument(taskId: string): Promise<TaskDocument> {
  const response = await apiClient.get<DocumentResponseBody>(`/tasks/${taskId}/document`);
  const body = response.data;
  return {
    taskId: body.task_id,
    generationStatus: body.generation_status,
    generationError: body.generation_error,
    content: body.content ? toDocumentContent(body.content) : null,
  };
}

const TERMINAL_GENERATION_STATUSES: DocumentGenerationStatus[] = ["completed", "failed"];

/**
 * How long (ms) a TanStack Query `refetchInterval` should wait before
 * re-polling GET .../document/status (T107), given the status's last
 * known value. Returns `false` once generation is in a terminal state
 * ("completed"/"failed") so polling stops, or before the first fetch has
 * resolved (nothing to poll yet).
 */
export function documentStatusPollIntervalMs(
  status: DocumentGenerationStatus | undefined,
): number | false {
  if (!status || TERMINAL_GENERATION_STATUSES.includes(status)) return false;
  return 4000;
}
