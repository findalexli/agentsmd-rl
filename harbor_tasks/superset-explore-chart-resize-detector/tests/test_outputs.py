"""
Test for superset PR #39160: Fix unnecessary scroll bars on charts in Explore view.

This test validates that the useResizeDetectorByObserver hook correctly uses
targetRef to observe the same element it measures, fixing the resize detection bug.
"""

import subprocess
import re
import sys
import json
from pathlib import Path

REPO_ROOT = Path("/workspace/superset")
FRONTEND_DIR = REPO_ROOT / "superset-frontend"
HOOK_FILE = FRONTEND_DIR / "src/explore/components/ExploreChartPanel/useResizeDetectorByObserver.ts"
INDEX_FILE = FRONTEND_DIR / "src/explore/components/ExploreChartPanel/index.tsx"


def test_hook_uses_target_ref():
    """
    Fail-to-pass: The hook must use targetRef option instead of a separate observerRef.
    The fix ensures we observe the same element we measure.
    """
    content = HOOK_FILE.read_text()

    # The fix should use targetRef: ref to observe the same element being measured
    assert "targetRef: ref," in content, (
        "Hook must use 'targetRef: ref' option to observe the measured element. "
        "This is the core fix - observing the same element that's being measured."
    )

    # Should NOT have observerRef destructuring from useResizeDetector
    # (the buggy pattern had: const { ref: observerRef } = useResizeDetector(...))
    match = re.search(r"const\s*\{\s*ref:\s*observerRef\s*\}\s*=\s*useResizeDetector", content)
    assert match is None, (
        "Hook must NOT destructure 'ref: observerRef' from useResizeDetector. "
        "This was the buggy pattern that observed a different element."
    )


def test_hook_returns_correct_interface():
    """
    Pass-to-pass: The hook should return { ref, width, height } without observerRef.
    """
    content = HOOK_FILE.read_text()

    # Should return ref (for attaching to measured element)
    assert "return {" in content and "ref," in content, (
        "Hook must return 'ref' for attaching to the measured element"
    )

    # Should return width and height
    assert "width," in content, "Hook must return 'width'"
    assert "height," in content, "Hook must return 'height'"

    # Should NOT return observerRef anymore
    assert "observerRef," not in content.split("return {")[1].split("}")[0], (
        "Hook must NOT return 'observerRef' in the return statement"
    )


def test_index_does_not_use_resize_observer_ref():
    """
    Fail-to-pass: ExploreChartPanel should not use resizeObserverRef.
    The fix removes the need for a separate observer ref.
    """
    content = INDEX_FILE.read_text()

    # Should NOT destructure resizeObserverRef from the hook
    assert "resizeObserverRef" not in content, (
        "ExploreChartPanel must NOT use 'resizeObserverRef' from useResizeDetectorByObserver. "
        "The fix removes this separate observer reference."
    )

    # Should still use chartPanelRef from the hook
    assert "chartPanelRef" in content, (
        "ExploreChartPanel should still use 'chartPanelRef' to attach to the chart container"
    )


def test_hook_has_proper_resize_handler():
    """
    Pass-to-pass: The hook should have a proper onResize callback.
    """
    content = HOOK_FILE.read_text()

    # Should define onResize callback
    assert "onResize" in content, "Hook must define an onResize callback"

    # Should call setChartPanelSize with width and height
    assert "setChartPanelSize({ width, height })" in content, (
        "Hook must call setChartPanelSize with width and height in onResize"
    )


def test_hook_uses_debounce_mode():
    """
    Pass-to-pass: The hook should use debounce mode to avoid excessive re-renders.
    """
    content = HOOK_FILE.read_text()

    assert "refreshMode: 'debounce'" in content, (
        "Hook must use 'debounce' refreshMode for performance"
    )

    assert "refreshRate: 300" in content, (
        "Hook must use 300ms refreshRate for debouncing"
    )


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors after the fix.
    Note: We skip this test because the repo requires plugins to be built first.
    The status.json notes indicate: "npm run type (tsc --noEmit) requires plugins
    to be built first - skipped".
    """
    # Skip this test - tsc requires complex build setup
    # The hook file itself is syntactically valid, but full type checking requires
    # the entire project build pipeline which is not available in test environment
    import pytest
    pytest.skip("TypeScript compilation requires plugins to be built first - see status.json notes")


def test_no_regressions_in_return_values():
    """
    The hook should maintain the same return shape (minus observerRef).
    """
    content = HOOK_FILE.read_text()

    # Find the return statement
    return_match = re.search(r"return\s*\{([^}]+)\}", content, re.DOTALL)
    assert return_match is not None, "Hook must have a return statement"

    return_body = return_match.group(1)

    # Should have ref, width, height
    assert "ref," in return_body or "ref" in return_body, "Must return ref"
    assert "width," in return_body or "width" in return_body, "Must return width"
    assert "height," in return_body or "height" in return_body, "Must return height"

    # Should not have observerRef
    assert "observerRef" not in return_body, "Must NOT return observerRef"


def test_hook_imports_correctly():
    """
    The hook should import useResizeDetector from react-resize-detector.
    """
    content = HOOK_FILE.read_text()

    # Should import useResizeDetector
    assert "useResizeDetector" in content, "Hook must import or use useResizeDetector"

    # Should import from react-resize-detector (directly or via re-export)
    # Note: the file may import from a re-export, so we just check it's used
    import_match = re.search(r"import\s+.*\{[^}]*useResizeDetector", content)
    # Or it could use a require/different pattern
    # Just verify the hook is being called somewhere
    hook_call = re.search(r"useResizeDetector\s*\(", content)
    assert hook_call is not None, "Hook must call useResizeDetector"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks
# These verify the repo's own tests pass on both base commit and after fix
# =============================================================================


def test_repo_lint():
    """
    Repo lint check passes (pass_to_pass).
    Runs oxlint to verify code quality standards.
    """
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_tests_explore_chart_panel():
    """
    Repo tests for ExploreChartPanel pass (pass_to_pass).
    Runs Jest tests for the modified module.
    """
    r = subprocess.run(
        ["npx", "jest", "--testPathPatterns=ExploreChartPanel", "--maxWorkers=1", "--silent"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND_DIR,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
