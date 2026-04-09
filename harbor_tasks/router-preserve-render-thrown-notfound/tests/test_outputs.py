#!/usr/bin/env python3
"""
Test suite for TanStack Router #7077
Verifies that notFound() errors thrown from components preserve route context.
"""
import subprocess
import os
import sys

REPO = "/workspace/router"


def run_nx_test(package: str, test_file: str = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run nx unit tests for a specific package."""
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
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )


def run_nx_build(package: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run nx build for a specific package."""
    return subprocess.run(
        ["pnpm", "nx", "run", f"@tanstack/{package}:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )


# =============================================================================
# Fail-to-Pass Tests: These verify the core bug fix behavior
# =============================================================================

def test_react_router_component_thrown_notfound():
    """
    React Router: Component-thrown bare notFound renders current route notFoundComponent.
    This test validates that when a component throws notFound() without explicit routeId,
    the route context is preserved and the correct notFoundComponent is rendered.
    """
    # Run the specific test that verifies component-thrown notFound behavior
    r = run_nx_test("react-router", "tests/not-found.test.tsx", timeout=120)

    if r.returncode != 0:
        # Check if the specific test cases are failing (the bug)
        output = r.stdout + r.stderr
        if "component-thrown bare notFound" in output.lower() or \
           "not-found.test.tsx" in output:
            assert False, f"React Router component-thrown notFound tests failed (bug present):\n{output[-2000:]}"

    assert r.returncode == 0, f"React Router not-found tests failed:\n{r.stdout[-2000:]}{r.stderr[-1000:]}"


def run_vitest_direct(package: str, test_file: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run vitest directly for a specific package (bypass nx test:unit script issues)."""
    return subprocess.run(
        ["pnpm", "exec", "vitest", "run", test_file],
        cwd=os.path.join(REPO, f"packages/{package}"),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )


def test_solid_router_component_thrown_notfound():
    """
    Solid Router: Component-thrown bare notFound renders current route notFoundComponent.
    Solid wraps non-Error throws in an Error with `cause`, so this tests the getNotFound() fix.
    """
    # Use vitest directly because solid-router's test:unit script is `vitest && vitest --mode server`
    # which doesn't work well with file filtering via nx
    r = run_vitest_direct("solid-router", "tests/not-found.test.tsx", timeout=120)

    if r.returncode != 0:
        output = r.stdout + r.stderr
        if "component-thrown bare notFound" in output.lower() or \
           "not-found.test.tsx" in output:
            assert False, f"Solid Router component-thrown notFound tests failed (bug present):\n{output[-2000:]}"

    assert r.returncode == 0, f"Solid Router not-found tests failed:\n{r.stdout[-2000:]}{r.stderr[-1000:]}"


def test_vue_router_component_thrown_notfound():
    """
    Vue Router: Component-thrown bare notFound renders current route notFoundComponent.
    Tests that Vue Match.tsx properly preserves routeId when notFound is thrown from components.
    """
    r = run_nx_test("vue-router", "tests/not-found.test.tsx", timeout=120)

    if r.returncode != 0:
        output = r.stdout + r.stderr
        if "component-thrown bare notFound" in output.lower() or \
           "not-found.test.tsx" in output:
            assert False, f"Vue Router component-thrown notFound tests failed (bug present):\n{output[-2000:]}"

    assert r.returncode == 0, f"Vue Router not-found tests failed:\n{r.stdout[-2000:]}{r.stderr[-1000:]}"


# =============================================================================
# Structural verification tests: Verify the code changes are present
# These are gated - they only provide points if behavioral tests pass first
# =============================================================================

def test_react_matchtsx_contains_fix():
    """
    Verify React Match.tsx contains the routeId preservation fix.
    The fix adds 'error.routeId ??= matchState.routeId' in two places.
    """
    match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")
    with open(match_file, 'r') as f:
        content = f.read()

    # Check for the fix: routeId assignment with null coalescing
    has_onCatch_fix = "error.routeId ??=" in content
    has_fallback_fix = content.count("error.routeId ??=") >= 2

    assert has_onCatch_fix, "React Match.tsx missing onCatch routeId preservation fix"
    assert has_fallback_fix, "React Match.tsx missing fallback routeId preservation fix"


def test_solid_matchtsx_contains_fix():
    """
    Verify Solid Match.tsx contains the getNotFound import and routeId preservation.
    """
    match_file = os.path.join(REPO, "packages/solid-router/src/Match.tsx")
    with open(match_file, 'r') as f:
        content = f.read()

    # Check for getNotFound import
    has_getNotFound_import = "getNotFound" in content

    # Check for routeId preservation
    has_routeId_fix = "notFoundError.routeId ??=" in content

    assert has_getNotFound_import, "Solid Match.tsx missing getNotFound import"
    assert has_routeId_fix, "Solid Match.tsx missing routeId preservation fix"


def test_solid_notfoundtsx_contains_getNotFound():
    """
    Verify Solid not-found.tsx exports the getNotFound helper.
    This helper unwraps Solid's Error wrapping for non-Error throws.
    """
    notfound_file = os.path.join(REPO, "packages/solid-router/src/not-found.tsx")
    with open(notfound_file, 'r') as f:
        content = f.read()

    has_getNotFound_export = "export function getNotFound" in content
    has_cause_unwrapping = "(error as any)?.cause" in content

    assert has_getNotFound_export, "Solid not-found.tsx missing getNotFound export"
    assert has_cause_unwrapping, "Solid not-found.tsx missing Error.cause unwrapping logic"


def test_vue_matchtsx_contains_fix():
    """
    Verify Vue Match.tsx contains the routeId preservation fix.
    """
    match_file = os.path.join(REPO, "packages/vue-router/src/Match.tsx")
    with open(match_file, 'r') as f:
        content = f.read()

    # Check for the fix: routeId assignment with null coalescing
    has_routeId_fix = "error.routeId ??=" in content

    assert has_routeId_fix, "Vue Match.tsx missing routeId preservation fix"


# =============================================================================
# Pass-to-Pass Tests: Verify repo tests still pass (upstream quality checks)
# =============================================================================

def test_react_router_build():
    """React Router package builds successfully (pass_to_pass)."""
    r = run_nx_build("react-router", timeout=120)
    assert r.returncode == 0, f"React Router build failed:\n{r.stderr[-1000:]}"


def test_solid_router_build():
    """Solid Router package builds successfully (pass_to_pass)."""
    r = run_nx_build("solid-router", timeout=120)
    assert r.returncode == 0, f"Solid Router build failed:\n{r.stderr[-1000:]}"


def test_vue_router_build():
    """Vue Router package builds successfully (pass_to_pass)."""
    r = run_nx_build("vue-router", timeout=120)
    assert r.returncode == 0, f"Vue Router build failed:\n{r.stderr[-1000:]}"


def test_react_router_all_notfound_tests():
    """All React Router not-found tests pass (upstream regression suite)."""
    r = run_nx_test("react-router", "tests/not-found.test.tsx", timeout=120)
    assert r.returncode == 0, f"React Router all not-found tests failed:\n{r.stdout[-2000:]}"


def test_solid_router_all_notfound_tests():
    """All Solid Router not-found tests pass (upstream regression suite)."""
    # Use vitest directly because solid-router's test:unit script has issues with file filtering
    r = run_vitest_direct("solid-router", "tests/not-found.test.tsx", timeout=120)
    assert r.returncode == 0, f"Solid Router all not-found tests failed:\n{r.stdout[-2000:]}"


def test_vue_router_all_notfound_tests():
    """All Vue Router not-found tests pass (upstream regression suite)."""
    r = run_nx_test("vue-router", "tests/not-found.test.tsx", timeout=120)
    assert r.returncode == 0, f"Vue Router all not-found tests failed:\n{r.stdout[-2000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
