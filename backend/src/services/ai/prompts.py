"""Prompt templates for 7-chapter learning-document generation (T092).

Pure string-building: no network calls, no filesystem/DB access. Produces
the system instruction + user prompt that DocumentGenerationService (T093)
sends via GeminiClient.generate_content(..., response_mime_type="application/json")
to get the `content` JSONB value stored on LearningDocument (T090).

Chapter structure/rules below come straight from spec.md's FR-026..FR-039
and data-model.md's documented `content` JSON shape.
"""

from dataclasses import dataclass

# research.md ("Prompt Engineering Strategy" > "Document Generation"):
# "System instruction: You are an expert teacher explaining code to
# complete beginners with zero programming knowledge".
SYSTEM_INSTRUCTION = (
    "You are an expert teacher explaining code to complete beginners with "
    "zero programming knowledge. Every explanation must avoid unexplained "
    "jargon (FR-036), use a real-life analogy for every abstract concept "
    "(FR-037), and assume the reader has never written a line of code "
    "before (FR-035)."
)

CHAPTER_TITLES = {
    "chapter1": "What This Code Does",
    "chapter2": "Prerequisites Knowledge",
    "chapter3": "Code Structure Overview",
    "chapter4": "Line-by-Line Explanation",
    "chapter5": "Execution Flow Simulation",
    "chapter6": "Core Concepts Summary",
    "chapter7": "Common Mistakes",
}


@dataclass(frozen=True)
class CodeFileInput:
    """One uploaded file's name + text content.

    The caller (DocumentGenerationService, T093) reads this from
    storage_path on disk (CodeFile is metadata-only, see T009/code_file.py)
    — this module never touches the filesystem itself.
    """

    file_name: str
    content: str


def _format_files(files: list[CodeFileInput]) -> str:
    return "\n\n".join(f"--- File: {f.file_name} ---\n{f.content}" for f in files)


def build_document_generation_prompt(
    *,
    files: list[CodeFileInput],
    language: str | None = None,
    complexity_level: str | None = None,
) -> str:
    """Build the user-turn prompt for generating the 7-chapter document.

    Send this together with SYSTEM_INSTRUCTION and
    response_mime_type="application/json" (see GeminiClient.generate_content,
    T091) so Gemini's JSON mode returns a single `content` JSON object
    matching LearningDocument's `valid_content_structure` CHECK constraint
    (chapter1..chapter7 all present).
    """
    if not files:
        raise ValueError("files must contain at least one file")

    context_lines = []
    if language:
        context_lines.append(f"Detected language: {language}")
    if complexity_level:
        context_lines.append(f"Complexity level: {complexity_level}")
    context = "\n".join(context_lines)

    return f"""{context}

Below is the code to explain:

{_format_files(files)}

Generate a 7-chapter learning document as a single JSON object with keys
"chapter1" through "chapter7". Follow this structure and these rules
exactly:

- chapter1 ({CHAPTER_TITLES["chapter1"]}): {{"title": str, "summary": str}}
  - summary: ONE sentence, plain language, no jargon (FR-027).

- chapter2 ({CHAPTER_TITLES["chapter2"]}): {{"title": str, "concepts": [...]}}
  - At most 5 concept cards (FR-029).
  - Each concept: {{"name": str, "explanation": str, "analogy": str, "example": str, "use_cases": str}} (FR-028).

- chapter3 ({CHAPTER_TITLES["chapter3"]}): {{"title": str, "flowchart": str, "file_breakdown": object}}
  - flowchart: an ASCII or Mermaid diagram of the execution flow.
  - file_breakdown: one entry per file describing its role (FR-030).

- chapter4 ({CHAPTER_TITLES["chapter4"]}): {{"title": str, "explanations": [...]}}
  - One entry per meaningful line/block: {{"line": int, "code": str, "explanation": str, "analogy": str, "alternative_example": str, "notes": str}} (FR-031).

- chapter5 ({CHAPTER_TITLES["chapter5"]}): {{"title": str, "steps": [...]}}
  - Step-by-step simulation of how data flows through the program: {{"step": int, "description": str}} (FR-032).

- chapter6 ({CHAPTER_TITLES["chapter6"]}): {{"title": str, "concepts": [...]}}
  - Core concepts learned, each: {{"name": str, "what_it_is": str, "why_its_used": str, "where_its_applied": str}} (FR-033).

- chapter7 ({CHAPTER_TITLES["chapter7"]}): {{"title": str, "mistakes": [...]}}
  - Between 3 and 5 common mistakes, each: {{"wrong": str, "right": str, "why": str, "fix": str}} (FR-034).

Rules:
- Every technical term must be explained in everyday language (no unexplained jargon).
- Every abstract concept must include a real-life analogy.
- Output ONLY the JSON object — no markdown fences, no commentary before or after it.
""".strip()
