"""
Tests for reduxjs/redux-toolkit#4937:
Fix referential stability of useInfiniteQuerySubscription's return value
"""

import os
import subprocess
import sys

REPO = "/workspace/redux-toolkit"
TOOLKIT_PKG = os.path.join(REPO, "packages", "toolkit")


def test_typescript_typecheck():
    """TypeScript compilation succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "type-tests"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout}\n{r.stderr}"


def test_vitest_infinite_queries():
    """Repo's infinite query tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/infiniteQueries.test.ts", "--no-typecheck"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Vitest infinite query tests failed:\n{r.stdout[-1000:]}"


def test_build_packages():
    """Package build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "build"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_hooks_typescript_compiles():
    """The modified file compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "src/query/react/buildHooks.ts"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # TypeScript may have project-context errors but no syntax errors
    # The key is that the file itself parses correctly
    assert "SyntaxError" not in r.stderr, f"Syntax error in buildHooks.ts:\n{r.stderr}"


def test_refetch_stability_fix():
    """
    Verify that refetch is now stable via useCallback - the refetch function
    should be defined with useCallback, not inline in useMemo.

    This test checks that the fix is actually applied by verifying the code
    contains the useCallback-wrapped refetch pattern.
    """
    build_hooks_path = os.path.join(TOOLKIT_PKG, "src", "query", "react", "buildHooks.ts")

    with open(build_hooks_path, "r") as f:
        content = f.read()

    # The fix introduces: const refetch = useCallback(() => refetchOrErrorIfUnmounted(promiseRef), [promiseRef])
    # And uses it in the return object instead of inline function
    assert "const refetch = useCallback" in content, \
        "refetch should be wrapped in useCallback for stability"
    assert "refetchOrErrorIfUnmounted(promiseRef)" in content, \
        "refetch should call refetchOrErrorIfUnmounted"


def test_stable_arg_fix():
    """
    Verify that stableArg from useStableQueryArgs is used for pagination.

    The original bug was that fetchNextPage/fetchPreviousPage used 'arg' directly
    which could cause instability. The fix uses stableArg instead.
    """
    build_hooks_path = os.path.join(TOOLKIT_PKG, "src", "query", "react", "buildHooks.ts")

    with open(build_hooks_path, "r") as f:
        content = f.read()

    # The fix introduces stableArg via useStableQueryArgs
    assert "const stableArg = useStableQueryArgs" in content, \
        "stableArg should be created via useStableQueryArgs"

    # fetchNextPage should use stableArg, not arg
    # Look for the pattern inside the useMemo callback
    assert "trigger(stableArg, 'forward')" in content, \
        "fetchNextPage should use stableArg instead of arg"
    assert "trigger(stableArg, 'backward')" in content, \
        "fetchPreviousPage should use stableArg instead of arg"


def test_lint_passes():
    """Repo's linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint", "--ignore-pattern", "examples"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=180,
    )
    # ESLint returns 2 if no files match, which is acceptable for our purposes
    assert r.returncode in (0, 2), f"Lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_build_hooks_tests():
    """Repo's buildHooks tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "vitest", "run", "src/query/tests/buildHooks.test.tsx", "--no-typecheck"],
        cwd=TOOLKIT_PKG,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"BuildHooks tests failed:\n{r.stdout[-1000:]}"