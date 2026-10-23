"""Unit tests for the code complexity analyzer (T066).

Metrics (line count, nesting depth, function count) and the resulting
complexity_level feed `uploaded_code.complexity_level`, whose CHECK
constraint (T009 migration) only allows 'beginner' | 'intermediate' |
'advanced' — see data-model.md.
"""

from src.services.code_analysis.complexity_analyzer import (
    ComplexityMetrics,
    analyze_file_complexity,
    analyze_project_complexity,
    assess_complexity_level,
    count_functions,
    count_lines,
    max_nesting_depth,
)


def test_count_lines_ignores_blank_and_whitespace_only_lines():
    content = "a\n\nb\n   \nc\n"
    assert count_lines(content) == 3


def test_count_lines_empty_content_is_zero():
    assert count_lines("") == 0


def test_max_nesting_depth_increases_with_indentation():
    content = "def f():\n    if True:\n        for i in range(3):\n            print(i)\n"
    assert max_nesting_depth(content) == 3


def test_max_nesting_depth_is_zero_for_flat_content():
    content = "print('a')\nprint('b')\n"
    assert max_nesting_depth(content) == 0


def test_max_nesting_depth_pops_back_on_dedent():
    content = "def f():\n" "    if True:\n" "        print('nested')\n" "print('top level again')\n"
    assert max_nesting_depth(content) == 2


def test_max_nesting_depth_ignores_blank_lines_between_nested_blocks():
    content = "def f():\n    if True:\n\n        print('nested')\n"
    assert max_nesting_depth(content) == 2


def test_count_functions_counts_python_defs():
    content = "def a():\n    pass\n\ndef b():\n    pass\n"
    assert count_functions(content) == 2


def test_count_functions_counts_javascript_function_keyword():
    content = "function add(a, b) {\n  return a + b;\n}\n"
    assert count_functions(content) == 1


def test_count_functions_counts_arrow_functions():
    content = "const add = (a, b) => a + b;\nconst sub = (a, b) => a - b;\n"
    assert count_functions(content) == 2


def test_count_functions_counts_java_methods():
    content = (
        "public class Calc {\n"
        "    public int add(int a, int b) {\n"
        "        return a + b;\n"
        "    }\n"
        "}\n"
    )
    assert count_functions(content) == 1


def test_count_functions_zero_for_no_functions():
    assert count_functions("x = 1\ny = 2\n") == 0


def test_assess_complexity_level_beginner_at_the_boundary():
    assert assess_complexity_level(total_lines=50, nesting_depth=2, function_count=3) == "beginner"


def test_assess_complexity_level_just_over_beginner_is_intermediate():
    assert (
        assess_complexity_level(total_lines=51, nesting_depth=2, function_count=3) == "intermediate"
    )


def test_assess_complexity_level_advanced_by_line_count():
    assert assess_complexity_level(total_lines=300, nesting_depth=0, function_count=0) == "advanced"


def test_assess_complexity_level_advanced_by_nesting_depth():
    assert assess_complexity_level(total_lines=10, nesting_depth=5, function_count=0) == "advanced"


def test_assess_complexity_level_advanced_by_function_count():
    assert assess_complexity_level(total_lines=10, nesting_depth=0, function_count=16) == "advanced"


def test_assess_complexity_level_mid_range_is_intermediate():
    assert (
        assess_complexity_level(total_lines=100, nesting_depth=3, function_count=5)
        == "intermediate"
    )


def test_analyze_file_complexity_returns_metrics_for_simple_file():
    content = "def hello():\n    print('hi')\n"
    metrics = analyze_file_complexity(content)
    assert metrics == ComplexityMetrics(
        total_lines=2, max_nesting_depth=1, function_count=1, level="beginner"
    )


def test_analyze_project_complexity_aggregates_across_files():
    file_a = "def a():\n    pass\n"
    file_b = "def b():\n    if True:\n        pass\n"
    metrics = analyze_project_complexity([file_a, file_b])
    assert metrics.total_lines == count_lines(file_a) + count_lines(file_b)
    assert metrics.max_nesting_depth == max(max_nesting_depth(file_a), max_nesting_depth(file_b))
    assert metrics.function_count == count_functions(file_a) + count_functions(file_b)
    assert metrics.level == assess_complexity_level(
        metrics.total_lines, metrics.max_nesting_depth, metrics.function_count
    )


def test_analyze_project_complexity_empty_list_is_zero_and_beginner():
    metrics = analyze_project_complexity([])
    assert metrics == ComplexityMetrics(
        total_lines=0, max_nesting_depth=0, function_count=0, level="beginner"
    )
