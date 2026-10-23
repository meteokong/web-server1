"""Code complexity analyzer (T066): line count, indentation nesting depth,
and function count, combined into the 'beginner' | 'intermediate' |
'advanced' level stored in `uploaded_code.complexity_level` (research.md's
"Complexity assessment: Line count, nesting depth, function count").

Language-agnostic by design — every extension `file_validator.
ALLOWED_EXTENSIONS` accepts is either indentation-significant (Python) or
conventionally indented to mirror its brace nesting (JS/TS/Java/C/C++), so
a single indentation-stack heuristic covers nesting depth without a
per-language parser. Function counting is a small set of regexes covering
each supported language's declaration syntax.
"""

import re
from dataclasses import dataclass

COMPLEXITY_LEVELS = ("beginner", "intermediate", "advanced")

# A file at or under all three of these is "beginner"; thresholds chosen
# to roughly track a single small function/script a first-time reader can
# hold in their head at once (spec.md/research.md don't specify exact
# numbers, so these are this service's own calibration).
BEGINNER_MAX_LINES = 50
BEGINNER_MAX_NESTING_DEPTH = 2
BEGINNER_MAX_FUNCTION_COUNT = 3

# A file at or over any one of these is "advanced"; everything in between
# is "intermediate".
ADVANCED_MIN_LINES = 300
ADVANCED_MIN_NESTING_DEPTH = 5
ADVANCED_MIN_FUNCTION_COUNT = 16

_FUNCTION_PATTERNS = (
    r"\bdef\s+\w+\s*\(",  # Python
    r"\bfunction\s+\w+\s*\(",  # JavaScript/TypeScript named function
    r"\b\w+\s*=\s*(?:\([^)]*\)|\w+)\s*=>",  # JS/TS arrow function assignment
    r"\b(?:public|private|protected|static)\s+[\w<>\[\],\s]+?\s+\w+\s*\([^)]*\)\s*\{",  # Java/C++ method
)


@dataclass(frozen=True)
class ComplexityMetrics:
    total_lines: int
    max_nesting_depth: int
    function_count: int
    level: str


def count_lines(content: str) -> int:
    """Count non-blank lines (blank/whitespace-only lines don't add to
    perceived complexity)."""
    return sum(1 for line in content.splitlines() if line.strip())


def max_nesting_depth(content: str) -> int:
    """Deepest indentation level, tracked as a stack of indent widths so
    it works regardless of whether the file uses 2-space, 4-space, or tab
    indentation."""
    indent_stack = [0]
    deepest = 0
    for line in content.splitlines():
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        while indent < indent_stack[-1]:
            indent_stack.pop()
        if indent > indent_stack[-1]:
            indent_stack.append(indent)
        deepest = max(deepest, len(indent_stack) - 1)
    return deepest


def count_functions(content: str) -> int:
    """Count function/method declarations via a small set of regexes
    covering Python, JavaScript/TypeScript, and Java/C++ syntax."""
    return sum(len(re.findall(pattern, content)) for pattern in _FUNCTION_PATTERNS)


def assess_complexity_level(total_lines: int, nesting_depth: int, function_count: int) -> str:
    """Combine the three metrics into one of COMPLEXITY_LEVELS."""
    if (
        total_lines <= BEGINNER_MAX_LINES
        and nesting_depth <= BEGINNER_MAX_NESTING_DEPTH
        and function_count <= BEGINNER_MAX_FUNCTION_COUNT
    ):
        return "beginner"
    if (
        total_lines >= ADVANCED_MIN_LINES
        or nesting_depth >= ADVANCED_MIN_NESTING_DEPTH
        or function_count >= ADVANCED_MIN_FUNCTION_COUNT
    ):
        return "advanced"
    return "intermediate"


def analyze_file_complexity(content: str) -> ComplexityMetrics:
    """Compute all three metrics and the resulting level for one file."""
    lines = count_lines(content)
    nesting = max_nesting_depth(content)
    functions = count_functions(content)
    return ComplexityMetrics(
        total_lines=lines,
        max_nesting_depth=nesting,
        function_count=functions,
        level=assess_complexity_level(lines, nesting, functions),
    )


def analyze_project_complexity(file_contents: list[str]) -> ComplexityMetrics:
    """Aggregate metrics across every file in an upload: lines and
    function count sum, nesting depth takes the deepest file."""
    if not file_contents:
        return ComplexityMetrics(
            total_lines=0, max_nesting_depth=0, function_count=0, level="beginner"
        )
    per_file = [analyze_file_complexity(content) for content in file_contents]
    total_lines = sum(m.total_lines for m in per_file)
    deepest_nesting = max(m.max_nesting_depth for m in per_file)
    total_functions = sum(m.function_count for m in per_file)
    return ComplexityMetrics(
        total_lines=total_lines,
        max_nesting_depth=deepest_nesting,
        function_count=total_functions,
        level=assess_complexity_level(total_lines, deepest_nesting, total_functions),
    )
