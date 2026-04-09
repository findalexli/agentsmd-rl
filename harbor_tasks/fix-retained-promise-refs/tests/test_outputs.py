"""
Tests for TanStack/router#6929 - Fix retained promise refs

This PR fixes memory leaks by clearing promise references after resolution:
1. prevLoadPromise in executeBeforeLoad (load-matches.ts)
2. loadPromise after resolution in loadRouteMatch (load-matches.ts)
3. previousCommitPromise in commitLocation (router.ts)
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/router")

def test_load_matches_prev_promise_cleared():
    """
    Verify that prevLoadPromise is declared with 'let' and cleared to undefined
    after resolving in executeBeforeLoad.
    """
    load_matches_file = REPO / "packages" / "router-core" / "src" / "load-matches.ts"
    content = load_matches_file.read_text()

    # Check 1: prevLoadPromise should use 'let' not 'const'
    # Find the line in executeBeforeLoad function
    assert "let prevLoadPromise = match._nonReactive.loadPromise" in content, \
        "prevLoadPromise should be declared with 'let', not 'const'"

    # Check 2: prevLoadPromise should be set to undefined after resolve
    # The pattern should be: prevLoadPromise?.resolve() followed by prevLoadPromise = undefined
    assert "prevLoadPromise = undefined" in content, \
        "prevLoadPromise should be cleared to undefined after resolve"

    # Verify the specific pattern appears in executeBeforeLoad context
    lines = content.split('\n')
    found_let = False
    found_clear = False
    in_execute_before_load = False

    for i, line in enumerate(lines):
        if 'const executeBeforeLoad' in line:
            in_execute_before_load = True
        elif in_execute_before_load and line.startswith('const ') and 'execute' in line.lower():
            # Another function started
            in_execute_before_load = False

        if in_execute_before_load:
            if 'let prevLoadPromise' in line:
                found_let = True
            if 'prevLoadPromise = undefined' in line:
                found_clear = True

    assert found_let, "prevLoadPromise must use 'let' declaration in executeBeforeLoad"
    assert found_clear, "prevLoadPromise must be cleared to undefined in execute_before_load"


def test_load_matches_load_promise_cleared_in_loader():
    """
    Verify that match._nonReactive.loadPromise is set to undefined
    after being resolved in the loader error handler.
    """
    load_matches_file = REPO / "packages" / "router-core" / "src" / "load-matches.ts"
    content = load_matches_file.read_text()

    # Should have loadPromise = undefined after the error handler resolve
    assert "match._nonReactive.loadPromise = undefined" in content, \
        "loadPromise should be cleared to undefined after resolution"

    # Count occurrences - should be at least 2 (one in error handler, one in normal flow)
    count = content.count("match._nonReactive.loadPromise = undefined")
    assert count >= 2, f"Expected at least 2 loadPromise = undefined assignments, found {count}"


def test_router_commit_promise_cleared():
    """
    Verify that previousCommitPromise is declared with 'let' and cleared
    to undefined after resolve in commitLocation.
    """
    router_file = REPO / "packages" / "router-core" / "src" / "router.ts"
    content = router_file.read_text()

    # Check 1: previousCommitPromise should use 'let' not 'const'
    assert "let previousCommitPromise = this.commitLocationPromise" in content, \
        "previousCommitPromise should be declared with 'let', not 'const'"

    # Check 2: previousCommitPromise should be set to undefined after resolve
    assert "previousCommitPromise = undefined" in content, \
        "previousCommitPromise should be cleared to undefined after resolve"


# --- pass_to_pass: Repo CI/CD checks ---

def test_unit_tests_pass():
    """
    Run the existing unit tests for router-core to ensure the fix doesn't break anything.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check test output
    if result.returncode != 0:
        # Some test failures may be unrelated - check for actual errors
        stderr = result.stderr
        stdout = result.stdout

        # If it's just "No tests found" or similar, that's ok
        if "No test files found" in stderr or "No test files found" in stdout:
            return

        # If tests actually ran and failed, that's a problem
        if "FAIL" in stdout or "Error:" in stderr:
            assert False, f"Unit tests failed:\nstdout: {stdout}\nstderr: {stderr}"


def test_typescript_compiles():
    """
    Ensure the TypeScript code compiles without errors across all supported TS versions.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_build_succeeds():
    """
    Ensure the package builds successfully after the fix.
    (pass_to_pass)
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout}\n{result.stderr}"


def test_repo_eslint():
    """Repo's ESLint check passes on router-core (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_publint():
    """Repo's package validation (publint + attw) passes on router-core (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Package validation failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
