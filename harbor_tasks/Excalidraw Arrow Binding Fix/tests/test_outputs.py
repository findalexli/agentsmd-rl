"""
Test suite for Excalidraw arrow binding fix.

This tests the fix for arrow drag start in bindable area jumping across bindable elements.
The bug was that when dragging an arrow that starts in a bindable element's area,
the arrow would incorrectly update its points, causing visual jumps.

The fix adds a check in updateBoundPoint to detect initial arrow creation and skip
point updates during that phase.
"""

import subprocess
import os
import re

REPO = "/workspace/excalidraw"
BINDING_FILE = "packages/element/src/binding.ts"


def test_typescript_compiles():
    """Verify TypeScript compiles without errors."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_fix_has_required_import():
    """
    Verify the fix includes necessary imports for point comparison.

    The fix requires comparing arrow points to detect initial creation state.
    This test ensures the required comparison utilities are imported.
    """
    with open(os.path.join(REPO, BINDING_FILE), "r") as f:
        content = f.read()

    # Extract the import section at the top of the file
    import_section = content[:content.find("export const")]

    # The fix needs some point comparison utility - either pointsEqual or equivalent
    has_pointsEqual = "pointsEqual" in import_section

    assert has_pointsEqual, \
        "Fix must import pointsEqual (or equivalent) from the math package for point comparison"


def test_updateboundpoint_has_initial_arrow_guard():
    """
    Verify updateBoundPoint has a guard condition for initial arrow creation.

    The bug occurs because updateBoundPoint updates arrow points even during initial
    creation. The fix must add a condition to detect initial arrow state (when the
    last point is at origin 0,0) and return null to skip point updates.

    This test verifies the logic structure of the fix without requiring exact code.
    """
    with open(os.path.join(REPO, BINDING_FILE), "r") as f:
        content = f.read()

    # Find the updateBoundPoint function
    func_match = re.search(
        r'export const updateBoundPoint\s*=\s*\([^)]*\)\s*:\s*[^=]+=>\s*\{',
        content
    )
    assert func_match, "Could not find updateBoundPoint function"

    # Get the function body by tracking braces
    start_idx = func_match.end()
    brace_count = 1
    end_idx = start_idx

    while brace_count > 0 and end_idx < len(content):
        if content[end_idx] == '{':
            brace_count += 1
        elif content[end_idx] == '}':
            brace_count -= 1
        end_idx += 1

    func_body = content[start_idx:end_idx-1]

    # The function must have:
    # 1. An early return that checks for null binding
    # 2. Additional condition(s) in that early return that check for initial arrow state

    # Find the early return block (starts with "if (binding == null" or similar)
    early_return_match = re.search(
        r'if\s*\(\s*binding\s*==\s*null',
        func_body
    )
    assert early_return_match, \
        "Function must have early return check for null binding"

    # Get the condition block (find matching closing paren)
    condition_start = early_return_match.start()
    paren_count = 1
    condition_end = condition_start + len(early_return_match.group(0))

    while paren_count > 0 and condition_end < len(func_body):
        if func_body[condition_end] == '(':
            paren_count += 1
        elif func_body[condition_end] == ')':
            paren_count -= 1
        condition_end += 1

    condition_block = func_body[condition_start:condition_end]

    # The condition must check for initial arrow state
    # This could be done in various ways, but should involve checking
    # the arrow's points array
    has_points_check = (
        "arrow.points" in condition_block and
        ("length" in condition_block or "[0" in condition_block or "- 1]" in condition_block)
    )

    # And should involve a comparison to detect initial state
    has_comparison = (
        "pointsEqual" in condition_block or
        "0" in condition_block or
        "pointFrom" in condition_block
    )

    assert has_points_check, \
        "Fix must check arrow.points in the early return condition to detect initial state"
    assert has_comparison, \
        "Fix must include a comparison to detect initial arrow state (0,0 point)"


def test_fix_does_not_break_existing_logic():
    """
    Verify the fix doesn't remove or break existing functionality.

    The existing logic handles various binding scenarios. The fix should add
    a new condition without breaking what's already there.
    """
    with open(os.path.join(REPO, BINDING_FILE), "r") as f:
        content = f.read()

    # Key existing patterns that must remain:
    required_patterns = [
        "export const updateBoundPoint",
        "binding == null",
        "elementId !== bindableElement.id",
        "arrow.points.length > 2",
        "return null",
    ]

    for pattern in required_patterns:
        assert pattern in content, f"Existing logic removed: {pattern}"


def test_move_tests_pass():
    """
    Run the move tests to verify arrow binding behavior.

    These tests verify that arrows move correctly with bindable elements.
    The fix should make these tests pass with the correct arrow positions.
    """
    result = subprocess.run(
        ["yarn", "test:app", "move.test.tsx", "-t", "rectangles with binding arrow", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Check for test pass indicators
    passed = (
        result.returncode == 0 or
        "PASS" in result.stdout or
        ("Tests:" in result.stdout and "failed" not in result.stdout.lower())
    )

    assert passed, f"Move tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_history_tests_pass():
    """
    Run history tests related to arrow binding.

    Arrow binding affects undo/redo history. The fix should preserve correct
    history behavior for bidirectional binding scenarios.
    """
    result = subprocess.run(
        ["yarn", "test:app", "history.test.tsx", "-t", "bidirectional binding", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Check for test pass indicators
    passed = (
        result.returncode == 0 or
        "PASS" in result.stdout or
        ("Tests:" in result.stdout and "failed" not in result.stdout.lower())
    )

    assert passed, f"History tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These verify the fix doesn't break existing CI/CD checks that run on PRs.
# =============================================================================


def test_repo_eslint_passes():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_prettier_passes():
    """Repo's Prettier check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_element_tests_pass():
    """Repo's element package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Element tests failed:\n{r.stderr[-500:]}"


def test_repo_math_tests_pass():
    """Repo's math package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/math"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Math tests failed:\n{r.stderr[-500:]}"


def test_repo_common_tests_pass():
    """Repo's common package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/common"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Common tests failed:\n{r.stderr[-500:]}"


def test_repo_utils_tests_pass():
    """Repo's utils package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/utils"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Utils tests failed:\n{r.stderr[-500:]}"


def test_repo_binding_tests_pass():
    """Repo's binding-specific tests pass (pass_to_pass).

    These tests directly cover the binding.ts file that the fix modifies,
    testing arrow binding behavior including the updateBoundPoint function.
    """
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/element/tests/binding.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Binding tests failed:\n{r.stderr[-500:]}"
