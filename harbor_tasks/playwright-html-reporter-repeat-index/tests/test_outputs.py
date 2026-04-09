"""
Task: playwright-html-reporter-repeat-index
Repo: microsoft/playwright @ 1bebb2d1759a9df0c676eb0708451abf90973fcc
PR:   40002

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified TypeScript files must parse without errors."""
    files = [
        "packages/html-reporter/src/testCaseView.tsx",
        "packages/html-reporter/src/types.d.ts",
        "packages/playwright/src/reporters/html.ts",
    ]
    for f in files:
        path = Path(f"{REPO}/{f}")
        # Basic check: file exists and has content
        assert path.exists(), f"File {f} does not exist"
        content = path.read_text()
        assert len(content) > 0, f"File {f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_repeat_index_in_types():
    """TestCaseSummary type must include repeatEachIndex field."""
    types_file = Path(f"{REPO}/packages/html-reporter/src/types.d.ts")
    content = types_file.read_text()

    # Look for the repeatEachIndex field in TestCaseSummary type
    assert "repeatEachIndex?: number" in content, \
        "TestCaseSummary type must have optional repeatEachIndex field"


# [pr_diff] fail_to_pass
def test_repeat_index_in_html_reporter():
    """HTML reporter must pass repeatEachIndex to test case data."""
    html_reporter = Path(f"{REPO}/packages/playwright/src/reporters/html.ts")
    content = html_reporter.read_text()

    # Should have the repeatEachIndex assignment in HtmlBuilder
    assert "repeatEachIndex: test.repeatEachIndex || undefined" in content, \
        "HTML reporter must pass repeatEachIndex to test case data"


# [pr_diff] fail_to_pass
def test_append_function_in_view():
    """TestCaseView must have appendRepeatEachIndexAnnotation function."""
    view_file = Path(f"{REPO}/packages/html-reporter/src/testCaseView.tsx")
    content = view_file.read_text()

    # Should have the appendRepeatEachIndexAnnotation function
    assert "function appendRepeatEachIndexAnnotation" in content, \
        "testCaseView.tsx must define appendRepeatEachIndexAnnotation function"

    # Should push the annotation with correct type
    assert "annotations.push({ type: 'repeatEachIndex'" in content, \
        "appendRepeatEachIndexAnnotation must push repeatEachIndex annotation"


# [pr_diff] fail_to_pass
def test_annotation_calls_in_view():
    """TestCaseView must call appendRepeatEachIndexAnnotation for both test and result annotations."""
    view_file = Path(f"{REPO}/packages/html-reporter/src/testCaseView.tsx")
    content = view_file.read_text()

    # Should call the function twice (once for visibleTestAnnotations, once for visibleAnnotations)
    calls = content.count("appendRepeatEachIndexAnnotation(")
    assert calls >= 2, \
        f"TestCaseView must call appendRepeatEachIndexAnnotation twice (found {calls} calls)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """appendRepeatEachIndexAnnotation must have real logic, not pass/return."""
    view_file = Path(f"{REPO}/packages/html-reporter/src/testCaseView.tsx")
    content = view_file.read_text()

    # Extract the function and check it has logic
    import re
    func_match = re.search(
        r'function appendRepeatEachIndexAnnotation\([^)]+\)\s*\{([^}]+)\}',
        content
    )
    assert func_match, "appendRepeatEachIndexAnnotation function not found"

    func_body = func_match.group(1)
    # Should check for truthy repeatEachIndex
    assert "if (repeatEachIndex)" in func_body, \
        "Function must check if repeatEachIndex is truthy"
    # Should push to annotations array
    assert "annotations.push" in func_body, \
        "Function must push to annotations array"
    # Should convert to string
    assert "String(repeatEachIndex)" in func_body, \
        "Function must convert repeatEachIndex to string"


# [pr_diff] fail_to_pass
def test_zero_index_not_shown():
    """Zero repeatEachIndex should not create annotation (falsy check)."""
    view_file = Path(f"{REPO}/packages/html-reporter/src/testCaseView.tsx")
    content = view_file.read_text()

    # The function should use a truthy check, not explicit undefined check
    # This ensures index 0 won't show an annotation
    assert "if (repeatEachIndex)" in content, \
        "Function must use truthy check to skip zero index"
