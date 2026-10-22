"""Language detection service (T065): extension-based lookup backed by
Pygments content analysis for files without a recognizable extension.

Every file reaching this service already passed `file_validator.
validate_extension` (T064), so `EXTENSION_TO_LANGUAGE` only needs to cover
`file_validator.ALLOWED_EXTENSIONS` — the Pygments fallback exists for the
one case extension can't resolve: an extensionless pasted-code upload.
"""

from collections import Counter
from pathlib import Path

from pygments.lexers import (
    CLexer,
    CppLexer,
    CssLexer,
    HtmlLexer,
    JavaLexer,
    JavascriptLexer,
    PythonLexer,
    TypeScriptLexer,
)

# Normalized language name for each extension file_validator.ALLOWED_EXTENSIONS
# accepts (see data-model.md's uploaded_code.detected_language).
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".html": "html",
    ".css": "css",
    ".txt": "text",
    ".md": "markdown",
}

UNKNOWN_LANGUAGE = "unknown"

# Candidate lexers for content-based detection, scoped to the code
# languages we support (excludes .txt/.md, which extension already
# resolves unambiguously). Pygments' generic `guess_lexer` is too
# unreliable on short snippets; asking each candidate lexer to score the
# content directly via `analyse_text` is deterministic.
_CONTENT_FALLBACK_LEXERS = {
    "python": PythonLexer,
    "javascript": JavascriptLexer,
    "typescript": TypeScriptLexer,
    "java": JavaLexer,
    "cpp": CppLexer,
    "c": CLexer,
    "html": HtmlLexer,
    "css": CssLexer,
}

# Below this, a lexer's self-reported confidence is noise rather than a
# real signal (e.g. every lexer scores >0 on trivial/ambiguous content).
_CONFIDENCE_THRESHOLD = 0.1


def detect_file_language(filename: str, content: bytes | str = b"") -> str:
    """Detect a single file's language: by extension first, falling back
    to Pygments content analysis when the extension isn't recognized."""
    extension = Path(filename).suffix.lower()
    if extension in EXTENSION_TO_LANGUAGE:
        return EXTENSION_TO_LANGUAGE[extension]
    return _guess_from_content(content)


def detect_project_language(filenames: list[str]) -> str:
    """Detect the dominant language across an upload's files, by count of
    files per language. Returns "unknown" for an empty upload or one with
    no recognizable language."""
    languages = (detect_file_language(name) for name in filenames)
    counts = Counter(lang for lang in languages if lang != UNKNOWN_LANGUAGE)
    if not counts:
        return UNKNOWN_LANGUAGE
    return counts.most_common(1)[0][0]


def _guess_from_content(content: bytes | str) -> str:
    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            return UNKNOWN_LANGUAGE
    if not content.strip():
        return UNKNOWN_LANGUAGE
    scores = {lang: lexer.analyse_text(content) for lang, lexer in _CONTENT_FALLBACK_LEXERS.items()}
    best_language, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > _CONFIDENCE_THRESHOLD:
        return best_language
    return UNKNOWN_LANGUAGE
