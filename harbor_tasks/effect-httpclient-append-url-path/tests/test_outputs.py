#!/usr/bin/env python3
"""
Tests for HttpClientRequest.appendUrl URL path joining fix.

The bug: appendUrl uses simple string concatenation which can produce invalid URLs
when base URL doesn't end with '/' and path doesn't starts with '/'.

Before fix: "https://api.example.com/v1" + "users" = "https://api.example.com/v1users"
After fix:  "https://api.example.com/v1" + "users" = "https://api.example.com/v1/users"
"""
import subprocess
import os
import sys
import tempfile

REPO = os.environ.get("REPO", "/workspace/effect")

def run_cmd(cmd, timeout=600, cwd=None):
    if cwd is None:
        cwd = REPO
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return result


def run_tsx(code):
    """Run TypeScript code using pnpm exec tsx via a temp file."""
    # Write the code to a temp file to avoid shell escaping issues
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        r = run_cmd(f"pnpm exec tsx {temp_file} 2>&1", timeout=60)
        return r.stdout + r.stderr
    finally:
        os.unlink(temp_file)


def test_append_url_no_slash_both():
    """
    FAIL_TO_PASS: The core bug - no trailing slash on base, no leading slash on path.

    On base commit (buggy): "https://api.example.com/v1" + "users" = "https://api.example.com/v1users"
    After fix:             "https://api.example.com/v1" + "users" = "https://api.example.com/v1/users"

    This test MUST fail on base commit and pass after fix.
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1").pipe(
  HttpClientRequest.appendUrl("users")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1/users");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1/users"
            assert result_url == expected_url, f"Bug detected: got '{result_url}', expected '{expected_url}'"
            return  # Test passed

    assert False, f"Could not run appendUrl test. Output: {output[-500:]}"


def test_append_url_trailing_slash_base():
    """
    FAIL_TO_PASS: Base URL has trailing slash, path has no leading slash.

    Should correctly join: "https://api.example.com/v1/" + "users" = "https://api.example.com/v1/users"
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1/").pipe(
  HttpClientRequest.appendUrl("users")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1/users");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1/users"
            assert result_url == expected_url, f"Got '{result_url}', expected '{expected_url}'"
            return

    assert False, f"Could not run test. Output: {output[-500:]}"


def test_append_url_leading_slash_path():
    """
    FAIL_TO_PASS: Base URL has no trailing slash, path has leading slash.

    Should correctly join: "https://api.example.com/v1" + "/users" = "https://api.example.com/v1/users"
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1").pipe(
  HttpClientRequest.appendUrl("/users")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1/users");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1/users"
            assert result_url == expected_url, f"Got '{result_url}', expected '{expected_url}'"
            return

    assert False, f"Could not run test. Output: {output[-500:]}"


def test_append_url_both_slashes():
    """
    FAIL_TO_PASS: Both base has trailing slash and path has leading slash.

    Should correctly join: "https://api.example.com/v1/" + "/users" = "https://api.example.com/v1/users"
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1/").pipe(
  HttpClientRequest.appendUrl("/users")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1/users");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1/users"
            assert result_url == expected_url, f"Got '{result_url}', expected '{expected_url}'"
            return

    assert False, f"Could not run test. Output: {output[-500:]}"


def test_append_url_nested_path():
    """
    FAIL_TO_PASS: Nested path with multiple segments.

    Should correctly join: "https://api.example.com/v1" + "users/123/posts" = "https://api.example.com/v1/users/123/posts"
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1").pipe(
  HttpClientRequest.appendUrl("users/123/posts")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1/users/123/posts");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1/users/123/posts"
            assert result_url == expected_url, f"Got '{result_url}', expected '{expected_url}'"
            return

    assert False, f"Could not run test. Output: {output[-500:]}"


def test_append_url_empty_path():
    """
    PASS_TO_PASS: Empty path should not modify the URL.

    Should return the same URL: "https://api.example.com/v1" + "" = "https://api.example.com/v1"
    """
    test_code = '''import { HttpClientRequest } from "@effect/platform";

const request = HttpClientRequest.get("https://api.example.com/v1").pipe(
  HttpClientRequest.appendUrl("")
);

console.log("RESULT_URL:" + request.url);
console.log("EXPECTED_URL:https://api.example.com/v1");
'''
    output = run_tsx(test_code)

    for line in output.split('\n'):
        if line.startswith("RESULT_URL:"):
            result_url = line.split("RESULT_URL:")[1].strip()
            expected_url = "https://api.example.com/v1"
            assert result_url == expected_url, f"Got '{result_url}', expected '{expected_url}'"
            return

    assert False, f"Could not run test. Output: {output[-500:]}"


def test_platform_vitest_pass():
    """
    PASS_TO_PASS: Platform package vitest tests pass.

    This is a repo-level p2p test ensuring the platform package tests
    all pass on the base commit and continue to pass after the fix.
    """
    import subprocess
    r = subprocess.run(
        ["pnpm", "vitest", "run"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/packages/platform"
    )
    # Check for test summary indicating all passed
    output = r.stdout + r.stderr
    assert "Test Files" in output and "passed" in output, \
        f"Platform tests did not pass:\n{output[-500:]}"
    assert r.returncode == 0, f"Platform vitest failed with exit code {r.returncode}:\n{output[-500:]}"


def test_platform_eslint_pass():
    """
    PASS_TO_PASS: Platform package eslint passes with no warnings.

    This is a repo-level p2p test ensuring the platform package source
    code passes linting on the base commit and continues to pass after the fix.
    """
    import subprocess
    r = subprocess.run(
        ["npx", "eslint", "packages/platform/src", "--max-warnings=0"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"Platform eslint failed with exit code {r.returncode}:\n{output[-500:]}"


def test_circular_check():
    """
    PASS_TO_PASS: Repo circular dependency check passes.

    This is a repo-level p2p test ensuring the monorepo has no circular
    dependencies on the base commit and continues to pass after the fix.
    """
    import subprocess
    r = subprocess.run(
        ["pnpm", "circular"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"circular check failed with exit code {r.returncode}:\n{output[-500:]}"


if __name__ == "__main__":
    tests = [
        test_append_url_no_slash_both,
        test_append_url_trailing_slash_base,
        test_append_url_leading_slash_path,
        test_append_url_both_slashes,
        test_append_url_nested_path,
        test_append_url_empty_path,
        test_platform_vitest_pass,
        test_platform_eslint_pass,
        test_circular_check,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...")
            test()
            print(f"  PASSED: {test.__name__}")
        except AssertionError as e:
            print(f"  FAILED: {test.__name__}: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed:")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
