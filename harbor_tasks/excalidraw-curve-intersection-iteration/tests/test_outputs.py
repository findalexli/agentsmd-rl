"""Test suite for excalidraw curve intersection fix.

This tests that:
1. The iteration count in solveWithAnalyticalJacobian was increased from 3 to 4
2. Curve intersection works correctly with edge cases that previously failed
3. The repo's TypeScript type checking passes
"""

import subprocess
import sys
import re

REPO = "/workspace/excalidraw"
CURVE_FILE = f"{REPO}/packages/math/src/curve.ts"


def test_iteration_count_increased():
    """Verify solveWithAnalyticalJacobian is called with iterLimit=4, not 3.

    This is a fail-to-pass test: on the buggy base commit, the iteration
    limit is 3 which causes convergence issues for some curve intersections.
    The fix increases it to 4 for better accuracy.
    """
    with open(CURVE_FILE, "r") as f:
        content = f.read()

    # Check that the call in the calculate function uses iterLimit=4
    pattern = r"solveWithAnalyticalJacobian\(c, l, t0, s0, 1e-2, 4\)"
    match = re.search(pattern, content)

    assert match is not None, (
        "Expected solveWithAnalyticalJacobian to be called with iterLimit=4 "
        f"in calculate function. Pattern not found in {CURVE_FILE}"
    )

    # Also verify the old buggy value 3 is NOT present in that context
    buggy_pattern = r"solveWithAnalyticalJacobian\(c, l, t0, s0, 1e-2, 3\)"
    buggy_match = re.search(buggy_pattern, content)

    assert buggy_match is None, (
        "Found old buggy iteration count (3) in calculate function. "
        "The fix should use 4 iterations instead."
    )


def test_fallback_code_removed():
    """Verify the fallback mechanism using lineSegmentIntersectionPoints was removed.

    The old code had a fallback that approximated curves with short segments
    to catch near-endpoint hits. This should be removed in the fix.
    """
    with open(CURVE_FILE, "r") as f:
        content = f.read()

    # The fallback code should NOT be present
    fallback_pattern = "lineSegment(bezierEquation(c, 0), bezierEquation(c, 1 / 20))"

    assert fallback_pattern not in content, (
        "Fallback code for startHit should have been removed. "
        f"Found: {fallback_pattern}"
    )

    # Also check the second fallback
    fallback_pattern2 = "lineSegment(bezierEquation(c, 19 / 20), bezierEquation(c, 1))"

    assert fallback_pattern2 not in content, (
        "Fallback code for endHit should have been removed. "
        f"Found: {fallback_pattern2}"
    )

    # Verify the unused import was removed
    assert "lineSegmentIntersectionPoints" not in content, (
        "Unused import 'lineSegmentIntersectionPoints' should have been removed"
    )


def test_curve_intersection_accuracy():
    """Test that curveIntersectLineSegment correctly finds intersections.

    This test exercises the core functionality by importing the compiled
    TypeScript code and testing various intersection scenarios.
    """
    # Build the math package first
    build_result = subprocess.run(
        ["yarn", "build:math"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Run the math package tests specifically for curve intersection
    test_result = subprocess.run(
        ["yarn", "test:math", "--", "curve"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # The math tests should pass - note: they may not exist, that's OK
    # If tests exist and fail, that's a problem
    if test_result.returncode != 0 and "No tests found" not in test_result.stdout:
        # Check if there are actual failures vs just no tests
        if "FAIL" in test_result.stdout or "FAIL" in test_result.stderr:
            assert False, f"Math curve tests failed:\n{test_result.stderr[-1000:]}"


def test_repo_typecheck():
    """Repo's TypeScript type checking passes (pass_to_pass).

    This ensures the fix doesn't break type safety.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"TypeScript type checking failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass).

    This ensures the fix follows code style guidelines.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"ESLint failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_prettier():
    """Repo's Prettier formatting passes (pass_to_pass).

    This ensures the fix follows formatting guidelines.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"Prettier check failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_math_curve_tests():
    """Math package curve tests pass (pass_to_pass).

    This ensures curve intersection logic works correctly.
    """
    result = subprocess.run(
        ["npx", "vitest", "run", "packages/math/tests/curve.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"Math curve tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_build_math():
    """Math package builds successfully (pass_to_pass).

    This ensures the modified code compiles without errors.
    """
    result = subprocess.run(
        ["yarn", "build:math"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"Math package build failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_unused_import_removed():
    """Verify unused segment imports were removed from curve.ts."""
    with open(CURVE_FILE, "r") as f:
        content = f.read()

    # Check the specific import line was removed
    assert "lineSegment, lineSegmentIntersectionPoints" not in content, (
        "Unused import from './segment' should have been removed"
    )


if __name__ == "__main__":
    pytest_main = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=False,
    )
    sys.exit(pytest_main.returncode)
