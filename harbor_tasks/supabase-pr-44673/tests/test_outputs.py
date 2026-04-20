"""
Tests for supabase/supabase PR #44673: fix(www): bust social-media cache for dynamic OG images

The bug: getAbsoluteBlogSocialImage() returns the same URL on every deploy.
Social-media crawlers cache the OG image and show stale content.

The fix: appends ?v={timestamp} to URLs containing /functions/v1/generate-og,
forcing crawlers to fetch fresh images on each deploy.
"""

import subprocess
import os
import re
import sys

REPO = "/workspace/supabase"
WWW_APP = os.path.join(REPO, "apps/www")
TEST_FILE = os.path.join(WWW_APP, "lib/blog-images.test.ts")


def test_cache_bust_dynamic_og():
    """
    f2p: Dynamic OG function URLs must get a cache-busting query param appended.

    On base commit: getAbsoluteBlogSocialImage returns the URL unchanged.
    After fix: URL has an extra query parameter appended (e.g., ?v=... or &t=...).

    The test accepts ANY parameter-name (v, t, cb, etc.) so long as a unique
    value is appended after the original query string. This allows alternative
    correct fixes to pass.
    """
    # First, verify the test exists in the test file
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    if "appends a cache-busting param to dynamic OG function URLs" not in content:
        raise AssertionError(
            "Test 'appends a cache-busting param to dynamic OG function URLs' not found in test file.\n"
            "The fix must add this test to verify cache-busting behavior."
        )

    # Run the specific test
    returncode, output = run_vitest_test("appends a cache-busting param to dynamic OG function URLs")

    # Print output for debugging
    if returncode != 0:
        print(f"STDOUT/STDERR:\n{output[-3000:]}")

    assert returncode == 0, (
        f"Test 'appends a cache-busting param to dynamic OG function URLs' failed.\n"
        f"getAbsoluteBlogSocialImage should append a unique query parameter to URLs containing /functions/v1/generate-og.\n"
        f"Output: {output[-1000:]}"
    )


def test_no_cache_bust_static_image():
    """
    p2p: Static image URLs must NOT be modified.

    This verifies the fix doesn't break existing behavior for non-OG images.
    On both base and fixed commits, static images should pass through unchanged.
    """
    # First, verify the test exists in the test file
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    if "does not append a cache-busting param to static image URLs" not in content:
        raise AssertionError(
            "Test 'does not append a cache-busting param to static image URLs' not found in test file.\n"
            "The fix must add this test to verify static images are not affected."
        )

    returncode, output = run_vitest_test("does not append a cache-busting param to static image URLs")

    if returncode != 0:
        print(f"STDOUT/STDERR:\n{output[-3000:]}")

    assert returncode == 0, (
        f"Test 'does not append a cache-busting param to static image URLs' failed.\n"
        f"Static images should pass through getAbsoluteBlogSocialImage unchanged.\n"
        f"Output: {output[-1000:]}"
    )


def test_existing_social_image_test():
    """
    p2p: The existing test 'builds absolute social image URLs' must still pass.

    This is a regression test to ensure the fix doesn't break existing functionality.
    """
    returncode, output = run_vitest_test("builds absolute social image URLs")

    assert returncode == 0, (
        f"Existing test 'builds absolute social image URLs' failed (regression).\n"
        f"Output: {output[-1000:]}"
    )


def test_repo_tests_pass():
    """
    p2p: The www app's test suite must pass after the fix is applied.

    This ensures no other tests in the blog-images test file are broken.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "--run", "lib/blog-images.test.ts"],
        cwd=WWW_APP,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout[-2000:]}")
        print(f"STDERR:\n{result.stderr[-2000:]}")

    assert result.returncode == 0, (
        f"Blog-images test suite failed.\n"
        f"stdout: {result.stdout[-1000:]}\n"
        f"stderr: {result.stderr[-1000:]}"
    )


def test_repo_all_tests_pass():
    """
    p2p: The www app's full test suite (all test files) must pass.

    This is the actual CI command from .github/workflows/www-tests.yml.
    """
    result = subprocess.run(
        ["pnpm", "run", "test"],
        cwd=WWW_APP,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout[-2000:]}")
        print(f"STDERR:\n{result.stderr[-2000:]}")

    assert result.returncode == 0, (
        f"Full www test suite failed.\n"
        f"stdout: {result.stdout[-1000:]}\n"
        f"stderr: {result.stderr[-1000:]}"
    )


def test_repo_lint():
    """
    p2p: The www app's linter must pass.

    This is the lint command from the CI workflow.
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=WWW_APP,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout[-2000:]}")
        print(f"STDERR:\n{result.stderr[-2000:]}")

    assert result.returncode == 0, (
        f"Lint failed.\n"
        f"stdout: {result.stdout[-1000:]}\n"
        f"stderr: {result.stderr[-1000:]}"
    )


def test_repo_typecheck():
    """
    p2p: The www app's typecheck must pass.

    This is the typecheck command from the CI workflow.
    """
    result = subprocess.run(
        ["pnpm", "run", "typecheck"],
        cwd=WWW_APP,
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout[-2000:]}")
        print(f"STDERR:\n{result.stderr[-2000:]}")

    assert result.returncode == 0, (
        f"Typecheck failed.\n"
        f"stdout: {result.stdout[-1000:]}\n"
        f"stderr: {result.stderr[-1000:]}"
    )


def run_vitest_test(pattern: str, timeout: int = 120) -> tuple[int, str]:
    """Run vitest with a test name pattern filter and return (exit_code, output)."""
    result = subprocess.run(
        ["pnpm", "vitest", "--run", "--testNamePattern", pattern, "lib/blog-images.test.ts"],
        cwd=WWW_APP,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout + result.stderr


if __name__ == "__main__":
    # Run all tests when executed directly
    tests = [
        test_cache_bust_dynamic_og,
        test_no_cache_bust_static_image,
        test_existing_social_image_test,
        test_repo_tests_pass,
        test_repo_all_tests_pass,
        test_repo_lint,
        test_repo_typecheck,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ", flush=True)
            test()
            print("PASSED")
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed: {', '.join(failed)}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)