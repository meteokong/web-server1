/**
 * Frontend-shape of a task's generated learning document (GET
 * /tasks/{id}/document, T106), after document-service.ts maps the
 * backend's snake_case chapter JSON (data-model.md's LearningDocument
 * entity / Gemini's 7-chapter output) into camelCase.
 */

export interface Chapter1Content {
  title: string;
  summary: string;
}

export interface Chapter2Concept {
  name: string;
  explanation: string;
  analogy: string;
  example: string;
  useCases: string;
}

export interface Chapter2Content {
  title: string;
  concepts: Chapter2Concept[];
}

export interface Chapter3Content {
  title: string;
  flowchart: string;
  fileBreakdown: Record<string, string>;
}

export interface Chapter4Explanation {
  line: number;
  code: string;
  explanation: string;
  analogy: string;
  alternativeExample: string;
  notes: string;
}

export interface Chapter4Content {
  title: string;
  explanations: Chapter4Explanation[];
}

export interface Chapter5Step {
  step: number;
  description: string;
}

export interface Chapter5Content {
  title: string;
  steps: Chapter5Step[];
}

export interface Chapter6Concept {
  name: string;
  whatItIs: string;
  whyItsUsed: string;
  whereItsApplied: string;
}

export interface Chapter6Content {
  title: string;
  concepts: Chapter6Concept[];
}

export interface Chapter7Mistake {
  wrong: string;
  right: string;
  why: string;
  fix: string;
}

export interface Chapter7Content {
  title: string;
  mistakes: Chapter7Mistake[];
}

export interface DocumentContent {
  chapter1: Chapter1Content;
  chapter2: Chapter2Content;
  chapter3: Chapter3Content;
  chapter4: Chapter4Content;
  chapter5: Chapter5Content;
  chapter6: Chapter6Content;
  chapter7: Chapter7Content;
}

export type DocumentGenerationStatus = "pending" | "in_progress" | "completed" | "failed";

/** Frontend-shape of GET /tasks/{id}/document/status. */
export interface DocumentStatus {
  taskId: string;
  generationStatus: DocumentGenerationStatus;
  generationError: string | null;
  generationStartedAt: string | null;
  generationCompletedAt: string | null;
}

/** Frontend-shape of GET /tasks/{id}/document. */
export interface TaskDocument {
  taskId: string;
  generationStatus: DocumentGenerationStatus;
  generationError: string | null;
  content: DocumentContent | null;
}
