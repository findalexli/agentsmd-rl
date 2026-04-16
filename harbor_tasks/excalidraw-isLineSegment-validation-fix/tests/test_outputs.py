"""
Test suite for Excalidraw isLineSegment validation fix.

This tests that isLineSegment correctly validates both points in a segment,
not just the first point twice.
"""

import subprocess
import sys
import json
import os

REPO = "/workspace/excalidraw"


def write_test_file(filepath, content_lines):
    """Write test file with proper content."""
    with open(filepath, "w") as f:
        f.write("\n".join(content_lines))


def run_vitest_test(test_path, timeout=60):
    """Run a vitest test and return result."""
    return subprocess.run(
        ["yarn", "vitest", "run", test_path, "--reporter=json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def test_isLineSegment_valid_segment():
    """
    Test that valid line segments are correctly identified.

    This should pass on both base commit and fixed commit.
    """
    test_file = os.path.join(REPO, "packages/math/tests/f2p-valid.test.ts")

    # Write test file using list of lines to avoid curly brace escaping issues
    lines = [
        'import { isLineSegment } from "../src/segment";',
        'import { pointFrom } from "../src/point";',
        '',
        'describe("isLineSegment validation - valid segments", () => {',
        '  it("should return true for a valid segment with two valid points", () => {',
        '    const validSegment = [pointFrom(0, 0), pointFrom(1, 1)];',
        '    expect(isLineSegment(validSegment)).toBe(true);',
        '  });',
        '',
        '  it("should return true for another valid segment", () => {',
        '    const validSegment = [pointFrom(-5, 10), pointFrom(100, -200)];',
        '    expect(isLineSegment(validSegment)).toBe(true);',
        '  });',
        '});',
    ]
    write_test_file(test_file, lines)

    try:
        result = run_vitest_test("packages/math/tests/f2p-valid.test.ts")
        os.remove(test_file)
        assert result.returncode == 0, f"Valid segment tests failed:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_isLineSegment_rejects_invalid_second_element():
    """
    FAIL-TO-PASS: Test that segments with invalid second element are rejected.

    This is the core bug: the original code checks segment[0] twice instead
    of checking segment[0] and segment[1]. So invalid segments like
    [[0,0], "not-a-point"] would incorrectly pass validation.

    This test MUST fail on the base commit and pass on the fix.
    """
    test_file = os.path.join(REPO, "packages/math/tests/f2p-invalid.test.ts")

    lines = [
        'import { isLineSegment } from "../src/segment";',
        '',
        'describe("isLineSegment validation - invalid second element", () => {',
        '  it("should return false when second element is a string", () => {',
        '    const invalidSegment = [[0, 0], "not-a-point"];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element is a number", () => {',
        '    const invalidSegment = [[0, 0], 42];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element is null", () => {',
        '    const invalidSegment = [[0, 0], null];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element is undefined", () => {',
        '    const invalidSegment = [[0, 0], undefined];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element is an object", () => {',
        '    const invalidSegment = [[0, 0], { x: 1, y: 2 }];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element is an array with 3 elements", () => {',
        '    const invalidSegment = [[0, 0], [1, 2, 3]];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '',
        '  it("should return false when second element has non-numeric values", () => {',
        '    const invalidSegment = [[0, 0], ["a", "b"]];',
        '    expect(isLineSegment(invalidSegment)).toBe(false);',
        '  });',
        '});',
    ]
    write_test_file(test_file, lines)

    try:
        result = run_vitest_test("packages/math/tests/f2p-invalid.test.ts")
        os.remove(test_file)
        # This is the key test - it MUST pass for the fix
        assert result.returncode == 0, f"Invalid second element tests failed (bug not fixed):\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_isLineSegment_rejects_wrong_length():
    """
    Test that segments with wrong length are rejected.

    This should pass on both base commit and fixed commit (existing behavior).
    """
    test_file = os.path.join(REPO, "packages/math/tests/f2p-length.test.ts")

    lines = [
        'import { isLineSegment } from "../src/segment";',
        '',
        'describe("isLineSegment validation - wrong length", () => {',
        '  it("should return false for single element array", () => {',
        '    expect(isLineSegment([[0, 0]])).toBe(false);',
        '  });',
        '',
        '  it("should return false for empty array", () => {',
        '    expect(isLineSegment([])).toBe(false);',
        '  });',
        '',
        '  it("should return false for array with 3 elements", () => {',
        '    expect(isLineSegment([[0, 0], [1, 1], [2, 2]])).toBe(false);',
        '  });',
        '});',
    ]
    write_test_file(test_file, lines)

    try:
        result = run_vitest_test("packages/math/tests/f2p-length.test.ts")
        os.remove(test_file)
        assert result.returncode == 0, f"Wrong length tests failed:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_repo_vitest_math_package():
    """
    PASS-TO-PASS: Run the existing vitest tests for the math package.

    This verifies the repo's own test suite passes.
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "packages/math/tests/segment.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Repo's own segment tests failed:\n{result.stdout}\n{result.stderr}"


def test_isLineSegment_comprehensive():
    """
    Comprehensive test covering various edge cases.

    This validates the fix works across multiple scenarios.
    """
    test_file = os.path.join(REPO, "packages/math/tests/comprehensive.test.ts")

    lines = [
        'import { isLineSegment } from "../src/segment";',
        '',
        'describe("isLineSegment comprehensive tests", () => {',
        '  // Valid cases',
        '  it("accepts segment with positive coordinates", () => {',
        '    expect(isLineSegment([[0, 0], [1, 1]])).toBe(true);',
        '  });',
        '',
        '  it("accepts segment with negative coordinates", () => {',
        '    expect(isLineSegment([[-5, -10], [100, 200]])).toBe(true);',
        '  });',
        '',
        '  it("accepts segment with decimal coordinates", () => {',
        '    expect(isLineSegment([[0.5, 0.25], [1.5, 2.75]])).toBe(true);',
        '  });',
        '',
        '  it("accepts segment with zero coordinates", () => {',
        '    expect(isLineSegment([[0, 0], [0, 0]])).toBe(true);',
        '  });',
        '',
        '  // Invalid second element cases - these are the critical F2P tests',
        '  it("rejects segment where second element is string", () => {',
        '    expect(isLineSegment([[0, 0], "invalid"])).toBe(false);',
        '  });',
        '',
        '  it("rejects segment where second element has only one number", () => {',
        '    expect(isLineSegment([[0, 0], [1]])).toBe(false);',
        '  });',
        '',
        '  it("rejects segment where second element is boolean", () => {',
        '    expect(isLineSegment([[0, 0], true])).toBe(false);',
        '  });',
        '',
        '  // Non-array segment',
        '  it("rejects non-array input", () => {',
        '    expect(isLineSegment("not an array")).toBe(false);',
        '  });',
        '',
        '  it("rejects null input", () => {',
        '    expect(isLineSegment(null)).toBe(false);',
        '  });',
        '',
        '  it("rejects undefined input", () => {',
        '    expect(isLineSegment(undefined)).toBe(false);',
        '  });',
        '});',
    ]
    write_test_file(test_file, lines)

    try:
        result = run_vitest_test("packages/math/tests/comprehensive.test.ts")
        os.remove(test_file)
        assert result.returncode == 0, f"Comprehensive tests failed:\n{result.stdout}\n{result.stderr}"
    except Exception as e:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_repo_lint():
    """
    PASS-TO-PASS: Run the repo's ESLint checks.

    This verifies the codebase passes the project's linting rules.
    CI command: yarn test:code
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_typecheck():
    """
    PASS-TO-PASS: Run TypeScript type checking.

    This verifies the codebase passes TypeScript type checking.
    CI command: yarn test:typecheck
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-500:]}"


def test_repo_math_package_all_tests():
    """
    PASS-TO-PASS: Run all existing vitest tests for the math package.

    This runs the complete math package test suite including:
    - curve.test.ts
    - ellipse.test.ts
    - line.test.ts
    - point.test.ts
    - range.test.ts
    - segment.test.ts
    - vector.test.ts
    """
    result = subprocess.run(
        ["yarn", "vitest", "run", "packages/math/tests/", "--watch=false"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Math package tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
