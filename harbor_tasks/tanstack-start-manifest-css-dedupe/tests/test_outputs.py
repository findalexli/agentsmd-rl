"""Tests for TanStack Start manifest CSS deduplication fix.

This module tests that CSS assets are properly deduplicated in the Start manifest
to prevent shared stylesheets from appearing multiple times within a route entry
or across an active parent-child route chain.
"""

import os
import subprocess
import json
import sys

REPO = "/workspace/router"


def get_test_env():
    """Get environment variables for subprocess commands.

    Preserves PATH from the parent environment while adding CI-specific vars.
    """
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "CI": "1",
        "NX_DAEMON": "false",
    }
PACKAGE_PATH = f"{REPO}/packages/start-plugin-core"


def run_nx_test(test_pattern: str = None, test_name: str = None) -> tuple[int, str, str]:
    """Run tests via Nx for the start-plugin-core package.

    Args:
        test_pattern: File pattern to match tests
        test_name: Specific test name pattern (-t)

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:unit",
        "--outputStyle=stream",
        "--skipRemoteCache",
    ]

    # Add test file pattern if specified
    if test_pattern:
        cmd.extend(["--", test_pattern])

    # Add test name filter if specified
    if test_name:
        cmd.extend(["-t", test_name])

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=get_test_env(),
    )

    return result.returncode, result.stdout, result.stderr


def test_dedupe_css_from_shared_imported_chunks():
    """Test that CSS from shared imported chunks is deduplicated.

    When a chunk imports multiple other chunks that share a common dependency,
    the shared CSS should only appear once in the collected assets, not multiple
    times for each import path.

    This is a fail-to-pass test that verifies the fix for duplicate CSS assets.
    """
    returncode, stdout, stderr = run_nx_test(
        test_pattern="tests/start-manifest-plugin/manifestBuilder.test.ts",
        test_name="dedupes css from shared imported chunks",
    )

    output = stdout + stderr

    assert returncode == 0, (
        f"Test 'dedupes css from shared imported chunks' failed.\n"
        f"Expected: pass\n"
        f"Return code: {returncode}\n"
        f"Output: {output}"
    )

    # Verify test was actually found and ran
    assert "dedupes css from shared imported chunks" in output or "PASS" in output or "✓" in output, (
        f"Test may not have run - pattern not found in output:\n{output}"
    )


def test_dedupe_route_css_overlapping_chunk_imports():
    """Test that route CSS is deduplicated through overlapping chunk imports.

    When a route chunk imports multiple branch chunks that share a common dependency,
    the shared CSS should only appear once in the route's assets array.

    This is a fail-to-pass test that verifies proper route-level CSS deduplication.
    """
    returncode, stdout, stderr = run_nx_test(
        test_pattern="tests/start-manifest-plugin/manifestBuilder.test.ts",
        test_name="dedupes route css gathered through overlapping chunk imports",
    )

    output = stdout + stderr

    assert returncode == 0, (
        f"Test 'dedupes route css gathered through overlapping chunk imports' failed.\n"
        f"Expected: pass\n"
        f"Return code: {returncode}\n"
        f"Output: {output}"
    )

    assert "dedupes route css gathered through overlapping chunk imports" in output or "PASS" in output or "✓" in output, (
        f"Test may not have run - pattern not found in output:\n{output}"
    )


def test_dedupe_route_css_ancestor_routes():
    """Test that route CSS already owned by ancestor routes is deduplicated.

    When a child route shares CSS assets with its ancestor routes, those assets
    should not be duplicated in the child route's manifest entry.

    This is a fail-to-pass test that verifies proper ancestor-based deduplication.
    """
    returncode, stdout, stderr = run_nx_test(
        test_pattern="tests/start-manifest-plugin/manifestBuilder.test.ts",
        test_name="dedupes route css already owned by ancestor routes",
    )

    output = stdout + stderr

    assert returncode == 0, (
        f"Test 'dedupes route css already owned by ancestor routes' failed.\n"
        f"Expected: pass\n"
        f"Return code: {returncode}\n"
        f"Output: {output}"
    )

    assert "dedupes route css already owned by ancestor routes" in output or "PASS" in output or "✓" in output, (
        f"Test may not have run - pattern not found in output:\n{output}"
    )


def test_dedupe_assets_and_preloads_active_ancestor_path():
    """Test that assets and preloads are deduplicated only along the active ancestor path.

    Assets and preloads should be deduplicated when shared between parent and child
    routes, but cousin routes (different branches) should maintain their own copies.

    This is a pass-to-pass test verifying the complete deduplication logic.
    """
    returncode, stdout, stderr = run_nx_test(
        test_pattern="tests/start-manifest-plugin/manifestBuilder.test.ts",
        test_name="dedupes assets and preloads only along the active ancestor path",
    )

    output = stdout + stderr

    assert returncode == 0, (
        f"Test 'dedupes assets and preloads only along the active ancestor path' failed.\n"
        f"Expected: pass\n"
        f"Return code: {returncode}\n"
        f"Output: {output}"
    )

    assert "dedupes assets and preloads only along the active ancestor path" in output or "PASS" in output or "✓" in output, (
        f"Test may not have run - pattern not found in output:\n{output}"
    )


def test_backtracking_preserves_reused_assets():
    """Test that backtracking preserves reused assets for cousin routes.

    When the deduplication algorithm backtracks after processing a branch,
it should
    properly allow assets to be reused by cousin routes in other branches.

    This is a pass-to-pass test verifying proper backtracking behavior.
    """
    returncode, stdout, stderr = run_nx_test(
        test_pattern="tests/start-manifest-plugin/manifestBuilder.test.ts",
        test_name="backtracking preserves reused assets and preloads for cousin routes",
    )

    output = stdout + stderr

    assert returncode == 0, (
        f"Test 'backtracking preserves reused assets and preloads for cousin routes' failed.\n"
        f"Expected: pass\n"
        f"Return code: {returncode}\n"
        f"Output: {output}"
    )

    assert "backtracking preserves reused assets" in output or "PASS" in output or "✓" in output, (
        f"Test may not have run - pattern not found in output:\n{output}"
    )


def test_manifest_builder_all_tests():
    """Run all manifest builder tests to ensure no regressions.

    This is a comprehensive test that runs all tests in the manifestBuilder.test.ts
    file to ensure the fix doesn't break any existing functionality.
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:unit",
        "--outputStyle=stream",
        "--skipRemoteCache",
        "--",
        "tests/start-manifest-plugin/manifestBuilder.test.ts",
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=get_test_env(),
    )

    output = result.stdout + result.stderr

    # Check for test results - look for failure indicators
    assert result.returncode == 0, (
        f"Manifest builder tests failed.\n"
        f"Return code: {result.returncode}\n"
        f"Output: {output}"
    )

    # Verify tests actually ran (check for PASS or test count)
    assert "FAIL" not in output, f"Tests reported failures:\n{output}"


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and fixed
# =============================================================================

def test_repo_unit_tests():
    """Repo's unit tests for start-plugin-core pass (pass_to_pass).

    This test runs the unit test suite for the @tanstack/start-plugin-core
    package to verify that the fix doesn't break existing functionality.
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:unit",
        "--outputStyle=stream",
        "--skipRemoteCache",
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=get_test_env(),
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, (
        f"Unit tests failed.\n"
        f"Return code: {result.returncode}\n"
        f"Output: {output[-1000:]}"
    )

    # Verify tests actually ran
    assert "passed" in output.lower() or "PASS" in output, (
        f"Tests may not have run:\n{output[-500:]}"
    )


def test_repo_eslint():
    """Repo's ESLint check for start-plugin-core passes (pass_to_pass).

    This test runs ESLint on the @tanstack/start-plugin-core package
    to verify code style consistency.
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:eslint",
        "--outputStyle=stream",
        "--skipRemoteCache",
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=get_test_env(),
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, (
        f"ESLint check failed.\n"
        f"Return code: {result.returncode}\n"
        f"Output: {output[-500:]}"
    )


def test_repo_types():
    """Repo's TypeScript type check for start-plugin-core passes (pass_to_pass).

    This test runs TypeScript type checking for the @tanstack/start-plugin-core
    package to verify type safety across multiple TypeScript versions.
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:types",
        "--outputStyle=stream",
        "--skipRemoteCache",
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=get_test_env(),
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, (
        f"Type check failed.\n"
        f"Return code: {result.returncode}\n"
        f"Output: {output[-500:]}"
    )


def test_repo_build():
    """Repo's build validation for start-plugin-core passes (pass_to_pass).

    This test runs build validation (publint + attw) for the @tanstack/start-plugin-core
    package to verify package exports and types are correctly configured.
    """
    cmd = [
        "pnpm", "nx", "run",
        "@tanstack/start-plugin-core:test:build",
        "--outputStyle=stream",
        "--skipRemoteCache",
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=get_test_env(),
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0, (
        f"Build validation failed.\n"
        f"Return code: {result.returncode}\n"
        f"Output: {output[-500:]}"
    )


if __name__ == "__main__":
    # Run all tests
    tests = [
        # Fail-to-pass tests (verify the fix works)
        test_dedupe_css_from_shared_imported_chunks,
        test_dedupe_route_css_overlapping_chunk_imports,
        test_dedupe_route_css_ancestor_routes,
        test_dedupe_assets_and_preloads_active_ancestor_path,
        test_backtracking_preserves_reused_assets,
        test_manifest_builder_all_tests,
        # Pass-to-pass tests (verify existing functionality still works)
        test_repo_unit_tests,
        test_repo_eslint,
        test_repo_types,
        test_repo_build,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Unexpected error: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")

    if failed > 0:
        sys.exit(1)
