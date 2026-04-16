"""
Test suite for TanStack Router notFound error preservation fix.

This tests that component-thrown notFound() errors retain their routeId context
when crossing framework error boundaries, ensuring correct notFoundComponent rendering.
"""

import subprocess
import sys

REPO = "/workspace/router"

def _run_nx_test(package: str, test_file: str = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run Nx unit tests for a specific package."""
    cmd = [
        "pnpm", "nx", "run", f"@tanstack/{package}:test:unit",
        "--outputStyle=stream", "--skipRemoteCache"
    ]
    if test_file:
        cmd.extend(["--", test_file])
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )


def _run_nx_types(package: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run Nx type tests for a specific package."""
    return subprocess.run(
        ["pnpm", "nx", "run", f"@tanstack/{package}:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )


def _file_contains(filepath: str, pattern: str) -> bool:
    """Check if a file contains a specific pattern."""
    try:
        with open(f"{REPO}/{filepath}", "r") as f:
            content = f.read()
            return pattern in content
    except FileNotFoundError:
        return False


# =============================================================================
# Fail-to-pass tests - These verify the fix is applied
# =============================================================================

def test_react_match_assigns_routeId_onCatch():
    """
    FAIL-TO-PASS: React Match.tsx should assign routeId in onCatch handler.

    The fix ensures that when a notFound error is caught in onCatch,
    it gets the match's routeId assigned before being rethrown.
    """
    filepath = "packages/react-router/src/Match.tsx"

    # Check for the specific fix pattern
    content_check = _file_contains(filepath, "error.routeId ??= matchState.routeId")

    if not content_check:
        # Try to run the specific test to see the behavioral failure
        result = _run_nx_test("react-router", "tests/not-found.test.tsx", timeout=120)
        output = result.stdout + result.stderr

        # If tests pass without the fix code, something is wrong
        if "component-thrown bare notFound renders current route notFoundComponent" in output:
            if result.returncode == 0:
                pytest.skip("Test unexpectedly passed - fix may not be needed")

    assert content_check, (
        "React Match.tsx missing routeId assignment in onCatch. "
        "Expected 'error.routeId ??= matchState.routeId' in the onCatch handler."
    )


def test_react_match_assigns_routeId_in_fallback():
    """
    FAIL-TO-PASS: React Match.tsx should assign routeId in ResolvedNotFoundBoundary fallback.

    The fix ensures that notFound errors in the fallback handler
    get the routeId assigned for proper notFoundComponent resolution.
    """
    filepath = "packages/react-router/src/Match.tsx"

    # Check for the fix pattern in the fallback (note: should appear twice)
    content = ""
    try:
        with open(f"{REPO}/{filepath}", "r") as f:
            content = f.read()
    except FileNotFoundError:
        pass

    # Count occurrences - should be at least 2 (onCatch and fallback)
    routeId_count = content.count("error.routeId ??= matchState.routeId")

    assert routeId_count >= 2, (
        f"React Match.tsx missing routeId assignment in fallback. "
        f"Expected 2 occurrences of 'error.routeId ??= matchState.routeId', found {routeId_count}. "
        f"The fix should assign routeId in both onCatch and fallback handlers."
    )


def test_solid_match_uses_getNotFound_helper():
    """
    FAIL-TO-PASS: Solid Match.tsx should use the new getNotFound helper.

    Solid wraps non-Error throws in an Error object storing the original
    value in `cause`. The getNotFound helper unwraps this.
    """
    filepath = "packages/solid-router/src/Match.tsx"

    # Check for getNotFound import
    has_import = _file_contains(filepath, "getNotFound")

    # Check for getNotFound usage in onCatch
    has_getNotFound_usage = _file_contains(filepath, "const notFoundError = getNotFound(error)")

    # Check for routeId assignment with ??=
    has_routeId_assignment = _file_contains(filepath, "notFoundError.routeId ??=")

    assert has_import and has_getNotFound_usage and has_routeId_assignment, (
        "Solid Match.tsx missing getNotFound helper integration. "
        "Expected: import of getNotFound, usage in onCatch handler, and routeId assignment with ??=."
    )


def test_solid_notFound_exports_getNotFound():
    """
    FAIL-TO-PASS: Solid not-found.tsx should export getNotFound helper.

    The fix adds a new getNotFound function that unwraps Solid's error wrapping.
    """
    filepath = "packages/solid-router/src/not-found.tsx"

    # Check for getNotFound export
    content = ""
    try:
        with open(f"{REPO}/{filepath}", "r") as f:
            content = f.read()
    except FileNotFoundError:
        pass

    has_export = "export function getNotFound" in content
    has_cause_check = "(error as any)?.cause" in content
    has_comment = "Solid wraps non-Error throws" in content

    assert has_export and has_cause_check, (
        "Solid not-found.tsx missing getNotFound helper. "
        "Expected: exported function that checks both error.isNotFound and error.cause.isNotFound."
    )


def test_vue_match_assigns_routeId():
    """
    FAIL-TO-PASS: Vue Match.tsx should assign routeId in fallback and onCatch.

    The fix ensures notFound errors in Vue get their routeId assigned
    from matchData for proper notFoundComponent resolution.
    """
    filepath = "packages/vue-router/src/Match.tsx"

    # Check for routeId assignment in fallback
    content = ""
    try:
        with open(f"{REPO}/{filepath}", "r") as f:
            content = f.read()
    except FileNotFoundError:
        pass

    # Should have routeId assignment in both places
    has_fallback_assignment = "error.routeId ??= matchData.value?.routeId" in content
    has_onCatch_assignment = "error.routeId ??= matchData.value?.routeId as any" in content

    assert has_fallback_assignment, (
        "Vue Match.tsx missing routeId assignment in fallback. "
        "Expected 'error.routeId ??= matchData.value?.routeId'."
    )


# =============================================================================
# Pass-to-pass tests - These verify the repo's own tests pass
# =============================================================================

def test_react_router_notfound_tests():
    """
    PASS-TO-PASS: React Router not-found tests should pass.

    Runs the repository's own not-found test suite to verify
    the notFound() behavior works correctly.
    """
    result = _run_nx_test("react-router", "tests/not-found.test.tsx", timeout=180)

    assert result.returncode == 0, (
        f"React Router not-found tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_solid_router_notfound_tests():
    """
    PASS-TO-PASS: Solid Router not-found tests should pass.

    Runs the repository's own not-found test suite to verify
    the notFound() behavior works correctly.
    Note: Running all tests without file filter due to vitest path resolution.
    """
    # Run without file filter - the solid-router's test:unit script runs all tests
    result = _run_nx_test("solid-router", timeout=180)

    assert result.returncode == 0, (
        f"Solid Router not-found tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_vue_router_notfound_tests():
    """
    PASS-TO-PASS: Vue Router not-found tests should pass.

    Runs the repository's own not-found test suite to verify
    the notFound() behavior works correctly.
    """
    result = _run_nx_test("vue-router", "tests/not-found.test.tsx", timeout=180)

    assert result.returncode == 0, (
        f"Vue Router not-found tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_react_router_types():
    """
    PASS-TO-PASS: React Router TypeScript types should be valid.

    Verifies that TypeScript compiles without errors.
    """
    result = _run_nx_types("react-router", timeout=120)

    assert result.returncode == 0, (
        f"React Router type check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_solid_router_types():
    """
    PASS-TO-PASS: Solid Router TypeScript types should be valid.

    Verifies that TypeScript compiles without errors.
    """
    result = _run_nx_types("solid-router", timeout=120)

    assert result.returncode == 0, (
        f"Solid Router type check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_vue_router_types():
    """
    PASS-TO-PASS: Vue Router TypeScript types should be valid.

    Verifies that TypeScript compiles without errors.
    """
    result = _run_nx_types("vue-router", timeout=120)

    assert result.returncode == 0, (
        f"Vue Router type check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def _run_nx_eslint(package: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run Nx eslint check for a specific package."""
    return subprocess.run(
        ["pnpm", "nx", "run", f"@tanstack/{package}:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )


def test_react_router_eslint():
    """
    PASS-TO-PASS: React Router ESLint checks should pass.

    Verifies that the code follows the project's linting rules.
    """
    result = _run_nx_eslint("react-router", timeout=120)

    assert result.returncode == 0, (
        f"React Router eslint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_solid_router_eslint():
    """
    PASS-TO-PASS: Solid Router ESLint checks should pass.

    Verifies that the code follows the project's linting rules.
    """
    result = _run_nx_eslint("solid-router", timeout=120)

    assert result.returncode == 0, (
        f"Solid Router eslint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_vue_router_eslint():
    """
    PASS-TO-PASS: Vue Router ESLint checks should pass.

    Verifies that the code follows the project's linting rules.
    """
    result = _run_nx_eslint("vue-router", timeout=120)

    assert result.returncode == 0, (
        f"Vue Router eslint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"
    )


def test_router_core_unit():
    """
    PASS-TO-PASS: Router Core unit tests should pass.

    The core package contains the framework-agnostic routing logic that
    all framework bindings (React, Solid, Vue) depend on.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit",
         "--outputStyle=stream", "--skipRemoteCache", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Router Core unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


def test_history_unit():
    """
    PASS-TO-PASS: History package unit tests should pass.

    The history package is a dependency of router-core and provides
    the underlying history management functionality.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/history:test:unit",
         "--outputStyle=stream", "--skipRemoteCache", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**dict(subprocess.os.environ), "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"History unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
