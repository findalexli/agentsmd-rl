"""
Tests for TanStack/router#6998: Fix HeadContent remounts on history.replaceState

This PR fixes a Flash of Unstyled Content (FOUC) regression in Solid Router by
using Solid.createMemo with replaceEqualDeep to maintain referential stability
of head content tags across history state updates.
"""

import subprocess
import os
import re

REPO = "/workspace/router"


def run_cmd(cmd: list[str], timeout: int = 600, cwd: str = REPO) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )


# =============================================================================
# FAIL-TO-PASS TESTS
# =============================================================================

def test_use_tags_imports_replace_equal_deep():
    """
    The useTags function must import replaceEqualDeep from @tanstack/router-core.
    (fail_to_pass)
    """
    file_path = os.path.join(REPO, "packages/solid-router/src/headContentUtils.tsx")

    with open(file_path, "r") as f:
        content = f.read()

    # The fix requires importing replaceEqualDeep from @tanstack/router-core
    assert "replaceEqualDeep" in content, (
        "headContentUtils.tsx must import replaceEqualDeep from @tanstack/router-core"
    )

    # Verify it's imported from the correct package
    assert re.search(r"import\s*\{[^}]*replaceEqualDeep[^}]*\}\s*from\s*['\"]@tanstack/router-core['\"]", content), (
        "replaceEqualDeep must be imported from @tanstack/router-core"
    )


def test_use_tags_returns_create_memo():
    """
    The useTags function must return Solid.createMemo for referential stability.
    (fail_to_pass)
    """
    file_path = os.path.join(REPO, "packages/solid-router/src/headContentUtils.tsx")

    with open(file_path, "r") as f:
        content = f.read()

    # The return statement must use Solid.createMemo with prev parameter
    assert re.search(r"return\s+Solid\.createMemo\s*\(\s*\(\s*prev", content), (
        "useTags must return Solid.createMemo with a prev parameter for memoization"
    )


def test_use_tags_calls_replace_equal_deep():
    """
    The useTags function must call replaceEqualDeep(prev, next) for referential stability.
    (fail_to_pass)
    """
    file_path = os.path.join(REPO, "packages/solid-router/src/headContentUtils.tsx")

    with open(file_path, "r") as f:
        content = f.read()

    # Must call replaceEqualDeep(prev, next) for referential stability
    assert re.search(r"replaceEqualDeep\s*\(\s*prev\s*,\s*next\s*\)", content), (
        "useTags must call replaceEqualDeep(prev, next) to maintain referential stability"
    )


# =============================================================================
# PASS-TO-PASS TESTS
# =============================================================================

def test_solid_router_unit_tests():
    """
    All existing Solid Router unit tests must pass.
    (pass_to_pass)
    """
    result = run_cmd([
        "pnpm", "nx", "run", "@tanstack/solid-router:test:unit",
        "--outputStyle=stream", "--skipRemoteCache"
    ], timeout=600)

    assert result.returncode == 0, (
        f"Solid Router unit tests failed:\n"
        f"stdout: {result.stdout[-2000:] if result.stdout else 'none'}\n"
        f"stderr: {result.stderr[-2000:] if result.stderr else 'none'}"
    )


def test_solid_router_type_check():
    """
    Solid Router must pass TypeScript type checking.
    (pass_to_pass)
    """
    result = run_cmd([
        "pnpm", "nx", "run", "@tanstack/solid-router:test:types",
        "--outputStyle=stream", "--skipRemoteCache"
    ], timeout=300)

    assert result.returncode == 0, (
        f"Solid Router type check failed:\n"
        f"stdout: {result.stdout[-2000:] if result.stdout else 'none'}\n"
        f"stderr: {result.stderr[-2000:] if result.stderr else 'none'}"
    )


def test_solid_router_builds():
    """
    Solid Router must build successfully after the fix.
    (pass_to_pass)
    """
    result = run_cmd([
        "pnpm", "nx", "run", "@tanstack/solid-router:build",
        "--outputStyle=stream", "--skipRemoteCache"
    ], timeout=300)

    assert result.returncode == 0, (
        f"Solid Router build failed:\n"
        f"stdout: {result.stdout[-2000:] if result.stdout else 'none'}\n"
        f"stderr: {result.stderr[-2000:] if result.stderr else 'none'}"
    )


def test_solid_router_eslint():
    """
    Solid Router must pass ESLint checks (warnings allowed, no errors).
    (pass_to_pass)
    """
    result = run_cmd([
        "pnpm", "nx", "run", "@tanstack/solid-router:test:eslint",
        "--outputStyle=stream", "--skipRemoteCache"
    ], timeout=300)

    assert result.returncode == 0, (
        f"Solid Router ESLint failed:\n"
        f"stdout: {result.stdout[-2000:] if result.stdout else 'none'}\n"
        f"stderr: {result.stderr[-2000:] if result.stderr else 'none'}"
    )


def test_solid_router_publint():
    """
    Solid Router package exports must be valid (publint + attw checks).
    (pass_to_pass)
    """
    result = run_cmd([
        "pnpm", "nx", "run", "@tanstack/solid-router:test:build",
        "--outputStyle=stream", "--skipRemoteCache"
    ], timeout=300)

    assert result.returncode == 0, (
        f"Solid Router publint check failed:\n"
        f"stdout: {result.stdout[-2000:] if result.stdout else 'none'}\n"
        f"stderr: {result.stderr[-2000:] if result.stderr else 'none'}"
    )
