"""Tests for ScrollArea overscroll-behavior fix.

Tests verify that the varsResolver in ScrollArea correctly handles
the overscroll-behavior CSS property when scrollbars is set to 'x' or 'y'.
"""

import subprocess
import sys
import os

REPO = "/workspace/mantine"
SCROLLAREA_PATH = f"{REPO}/packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx"
SCROLLAREA_CSS_PATH = f"{REPO}/packages/@mantine/core/src/components/ScrollArea/ScrollArea.module.css"
SCROLLAREA_TEST_PATH = f"{REPO}/packages/@mantine/core/src/components/ScrollArea/ScrollArea.test.tsx"

def read_scrollarea_file():
    """Read the ScrollArea source file."""
    with open(SCROLLAREA_PATH, 'r') as f:
        return f.read()


def test_varsResolver_x_scrollbar_sets_y_to_auto():
    """When scrollbars='x', overscroll-behavior should be 'value auto'.

    This ensures horizontal ScrollArea doesn't capture vertical scroll events.
    """
    content = read_scrollarea_file()

    # Check that the fix is present: when scrollbars is 'x',
    # we should see `${overscrollBehavior} auto` pattern
    assert "scrollbars === 'x'" in content, "Missing scrollbars === 'x' check"
    assert "`${overscrollBehavior} auto`" in content, "Missing '${overscrollBehavior} auto' pattern"


def test_varsResolver_y_scrollbar_sets_x_to_auto():
    """When scrollbars='y', overscroll-behavior should be 'auto value'.

    This ensures vertical ScrollArea doesn't capture horizontal scroll events.
    """
    content = read_scrollarea_file()

    # Check that the fix is present: when scrollbars is 'y',
    # we should see `auto ${overscrollBehavior}` pattern
    assert "scrollbars === 'y'" in content, "Missing scrollbars === 'y' check"
    assert "`auto ${overscrollBehavior}`" in content, "Missing 'auto ${overscrollBehavior}' pattern"


def test_varsResolver_has_scrollbars_param():
    """The varsResolver should destructure scrollbars from props."""
    content = read_scrollarea_file()

    # Check that varsResolver destructures scrollbars
    assert "scrollbarSize, overscrollBehavior, scrollbars" in content, \
        "varsResolver should destructure scrollbars parameter"


def test_overrideOverscrollBehavior_variable():
    """The fix should use an overrideOverscrollBehavior variable."""
    content = read_scrollarea_file()

    assert "overrideOverscrollBehavior" in content, \
        "Should use overrideOverscrollBehavior variable"


def test_varsResolver_is_function_not_arrow_in_body():
    """The varsResolver body should be a function body with curly braces."""
    content = read_scrollarea_file()

    # After the fix, varsResolver uses a function body with curly braces
    # Pattern: "(_, { scrollbarSize, overscrollBehavior, scrollbars }) => {"
    assert "scrollbarSize, overscrollBehavior, scrollbars }) => {" in content, \
        "varsResolver should use function body with curly braces"


def test_scrollbar_check_conditional_logic():
    """The fix should have conditional logic to check scrollbars value."""
    content = read_scrollarea_file()

    # Check that both conditions exist in the file
    x_condition = "if (scrollbars === 'x')" in content
    y_condition = "if (scrollbars === 'y')" in content or "else if (scrollbars === 'y')" in content

    assert x_condition, "Missing conditional check for scrollbars === 'x'"
    assert y_condition, "Missing conditional check for scrollbars === 'y'"


def test_overscrollBehavior_and_scrollbars_check():
    """The fix should check that both overscrollBehavior and scrollbars are defined."""
    content = read_scrollarea_file()

    # Look for the combined check
    assert "if (overscrollBehavior && scrollbars)" in content, \
        "Should check that both overscrollBehavior and scrollbars are defined"


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI tests that should pass on base commit
# =============================================================================


def test_repo_scrollarea_jest():
    """ScrollArea unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "jest", SCROLLAREA_TEST_PATH],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ScrollArea jest tests failed:\n{r.stderr[-1000:]}"


def test_repo_scrollarea_prettier():
    """ScrollArea source file is formatted correctly (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "prettier", "--check", SCROLLAREA_PATH],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_scrollarea_eslint():
    """ScrollArea source file passes eslint (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "eslint", SCROLLAREA_PATH],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


def test_repo_scrollarea_stylelint():
    """ScrollArea CSS passes stylelint (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "stylelint", SCROLLAREA_CSS_PATH],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint check failed:\n{r.stderr[-500:]}"
