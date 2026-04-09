"""Tests for curve intersection iteration fix.

This test suite verifies that the curve-line intersection calculation
has sufficient iterations to converge on near-tangent intersections.
"""

import subprocess
import os

REPO = "/workspace/excalidraw"
MATH_PKG = f"{REPO}/packages/math"


def test_iteration_count_increased():
    """Verify that the iteration limit was increased from 3 to 4."""
    curve_file = f"{MATH_PKG}/src/curve.ts"
    with open(curve_file, "r") as f:
        content = f.read()

    # Check for the fixed iteration count
    assert "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)" in content, \
        "Iteration limit should be increased to 4"

    # Ensure old iteration count is gone
    assert "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 3)" not in content, \
        "Old iteration limit of 3 should be removed"


def test_fallback_code_removed():
    """Verify that the fallback endpoint approximation code was removed."""
    curve_file = f"{MATH_PKG}/src/curve.ts"
    with open(curve_file, "r") as f:
        content = f.read()

    # The fallback code should be removed
    assert "// Fallback: approximate the curve with short segments" not in content, \
        "Fallback comment should be removed"
    assert "lineSegmentIntersectionPoints" not in content, \
        "lineSegmentIntersectionPoints call should be removed (only in fallback)"


def test_import_line_segment_removed():
    """Verify the import for lineSegment was removed since it is no longer used."""
    curve_file = f"{MATH_PKG}/src/curve.ts"
    with open(curve_file, "r") as f:
        content = f.read()

    # The specific import line should be removed
    assert 'import { lineSegment, lineSegmentIntersectionPoints } from "./segment";' not in content, \
        "Unused import should be removed"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks)
# =============================================================================

def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_math_tests():
    """Repo's math package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--run", "packages/math"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Math package tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
