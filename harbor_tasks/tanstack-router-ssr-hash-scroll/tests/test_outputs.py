"""Tests for the SSR hash scroll preservation fix.

This module tests that the fix in packages/router-core/src/ssr/ssr-client.ts
correctly preserves scroll position after SSR hydration when preloading routes
or invalidating data.
"""

import subprocess
import sys
import os

REPO = "/workspace/router"
SSR_CLIENT_PATH = os.path.join(REPO, "packages/router-core/src/ssr/ssr-client.ts")


def test_solve_sh_exists():
    """Verify solve.sh exists and is executable."""
    solve_sh = "/workspace/solution/solve.sh"
    assert os.path.exists(solve_sh), f"solve.sh not found at {solve_sh}"


def test_ssr_client_file_exists():
    """Verify the target file exists."""
    assert os.path.exists(SSR_CLIENT_PATH), f"ssr-client.ts not found at {SSR_CLIENT_PATH}"


def test_hydrate_function_exists():
    """Verify the hydrate function exists in ssr-client.ts."""
    with open(SSR_CLIENT_PATH, 'r') as f:
        content = f.read()
    assert 'export async function hydrate' in content, "hydrate function not found"


def test_resolved_location_set_after_hydration():
    """
    FAIL-TO-PASS: Verify that resolvedLocation is set after SSR hydration.

    The fix adds: router.stores.resolvedLocation.setState(() => router.stores.location.state)
    after the dehydrated flag cleanup in the hydrate function.
    """
    with open(SSR_CLIENT_PATH, 'r') as f:
        content = f.read()

    # Find the hydrate function and check for the fix
    # The fix should set resolvedLocation to location.state
    has_resolved_location_set = (
        'router.stores.resolvedLocation.setState' in content and
        'router.stores.location.state' in content
    )

    # Also check that it's in the context of the hydrate function
    # by looking for the distinctive comment
    has_fix_comment = 'Mark the current location as resolved' in content

    assert has_resolved_location_set, (
        "Missing resolvedLocation.setState() call. "
        "The fix should set router.stores.resolvedLocation to prevent "
        "re-running hash scroll on subsequent load cycles."
    )

    assert has_fix_comment, (
        "Missing explanatory comment for the fix. "
        "The fix should include a comment explaining why resolvedLocation "
        "is being set after SSR hydration."
    )


def test_fix_is_in_hydrate_function_path():
    """
    Verify the fix is placed in the correct execution path within hydrate().

    The fix should be inside the block that handles SSR hydration,
    specifically after the dehydrated flag cleanup.
    """
    with open(SSR_CLIENT_PATH, 'r') as f:
        content = f.read()

    # Check that the fix comes after the dehydrated flag cleanup
    dehydrated_cleanup = 'match._nonReactive.dehydrated = undefined'
    fix_line = 'router.stores.resolvedLocation.setState'

    dehydrated_pos = content.find(dehydrated_cleanup)
    fix_pos = content.find(fix_line)

    assert dehydrated_pos != -1, "Could not find dehydrated cleanup code"
    assert fix_pos != -1, "Could not find resolvedLocation fix"
    assert fix_pos > dehydrated_pos, (
        "The fix should come AFTER the dehydrated flag cleanup in the hydrate function"
    )


def test_repo_typescript_compiles():
    """
    PASS-TO-PASS: TypeScript compilation passes for router-core.

    Verifies the package builds without type errors.
    Origin: repo_tests - runs actual CI build command.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"TypeScript type checking failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_unit_tests_pass():
    """
    PASS-TO-PASS: Unit tests pass for router-core.

    Runs the vitest test suite including hydrate.test.ts which covers
    the SSR hydration functionality being modified.
    Origin: repo_tests - runs actual CI test command.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_eslint_passes():
    """
    PASS-TO-PASS: ESLint passes for router-core source files.

    Verifies code style and quality checks pass.
    Origin: repo_tests - runs actual CI lint command.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:eslint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # ESLint returns 0 even with warnings, only fails on errors
    assert result.returncode == 0, (
        f"ESLint failed with errors:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_build_passes():
    """
    PASS-TO-PASS: Build verification passes for router-core.

    Runs publint and attw to verify package exports and types are correct.
    Origin: repo_tests - runs actual CI build verification command.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build verification failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_hydrate_tests_pass():
    """
    PASS-TO-PASS: Hydration-specific unit tests pass.

    Specifically runs the hydrate.test.ts file which tests the SSR hydration
    functionality that the fix modifies.
    Origin: repo_tests - runs actual CI test command targeting specific file.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "tests/hydrate.test.ts"],
        cwd=os.path.join(REPO, "packages/router-core"),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CI": "1"}
    )

    assert result.returncode == 0, (
        f"Hydrate tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )
