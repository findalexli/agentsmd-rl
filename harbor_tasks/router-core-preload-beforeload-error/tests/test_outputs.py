"""
Tests for router-core preload beforeLoad error handling fix.

The bug: When a parent route's beforeLoad throws during preload,
child route handlers (beforeLoad and head) were incorrectly being executed.

The fix: Check firstBadMatchIndex in the load loop to properly stop
execution when a parent handler fails.
"""

import subprocess
import sys
import os

REPO = "/workspace/router"


def test_preload_parent_beforeload_error_skips_child_handlers():
    """
    Test that when parent beforeLoad throws during preload,
    child beforeLoad and head handlers are NOT called.

    This is a fail-to-pass test - it fails on base commit and passes
    after the fix is applied.
    """
    # First check if the regression test exists in the test file
    test_file_path = os.path.join(REPO, "packages/router-core/tests/load.test.ts")
    with open(test_file_path, "r") as f:
        test_content = f.read()

    # The regression test must exist
    test_name = "skip child beforeLoad when parent beforeLoad throws during preload"
    assert test_name in test_content, (
        f"Regression test '{test_name}' not found in load.test.ts. "
        f"The test was added in the PR and must exist for proper validation."
    )

    # Run the specific regression test that was added in the PR
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--",
            "tests/load.test.ts", "-t", test_name
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # Check the test passed
    assert result.returncode == 0, (
        f"Test failed with return code {result.returncode}:\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_unit_tests_pass():
    """
    Pass-to-pass test: router-core unit tests should pass after the fix.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Unit tests failed with return code {result.returncode}:\n"
        f"stderr: {result.stderr[-2000:]}\n"
        f"stdout: {result.stdout[-2000:]}"
    )


def test_typescript_types_pass():
    """
    Pass-to-pass test: TypeScript type checking should pass.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Type check failed with return code {result.returncode}:\n"
        f"stderr: {result.stderr[-2000:]}\n"
        f"stdout: {result.stdout[-2000:]}"
    )


def test_eslint_linter_passes():
    """
    Pass-to-pass test: ESLint checks should pass for router-core.
    CI command: pnpm nx run @tanstack/router-core:test:eslint
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"ESLint check failed with return code {result.returncode}:\n"
        f"stderr: {result.stderr[-2000:]}\n"
        f"stdout: {result.stdout[-2000:]}"
    )


def test_build_package_validation_passes():
    """
    Pass-to-pass test: Package build validation (publint + attw) should pass.
    CI command: pnpm nx run @tanstack/router-core:test:build
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build validation failed with return code {result.returncode}:\n"
        f"stderr: {result.stderr[-2000:]}\n"
        f"stdout: {result.stdout[-2000:]}"
    )


def test_prettier_formatting_passes():
    """
    Pass-to-pass test: Code formatting should follow prettier standards.
    CI command: npx prettier --check on load-matches.ts (the modified file)
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "packages/router-core/src/load-matches.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Prettier format check failed with return code {result.returncode}:\n"
        f"stderr: {result.stderr[-1000:]}\n"
        f"stdout: {result.stdout[-1000:]}"
    )


def test_code_logic_fix():
    """
    Verify the actual code fix is present.
    This checks that the logic change in load-matches.ts is correct.

    The fix changes two things:
    1. Loop break condition: check both serialError AND firstBadMatchIndex
    2. headMaxIndex calculation: use firstBadMatchIndex when defined
    """
    load_matches_path = os.path.join(
        REPO, "packages/router-core/src/load-matches.ts"
    )

    with open(load_matches_path, "r") as f:
        content = f.read()

    # Check for the key fix: checking firstBadMatchIndex in the loop
    # The fix adds: if (inner.serialError || inner.firstBadMatchIndex != null)
    has_loop_fix = (
        "inner.serialError || inner.firstBadMatchIndex != null" in content
    )

    # Check for headMaxIndex fix - should use firstBadMatchIndex directly
    has_headmax_fix = (
        "inner.firstBadMatchIndex !== undefined" in content and
        "? inner.firstBadMatchIndex" in content
    )

    assert has_loop_fix, (
        "Missing loop break fix: should check firstBadMatchIndex in addition to serialError"
    )

    assert has_headmax_fix, (
        "Missing headMaxIndex fix: should use firstBadMatchIndex when defined"
    )
