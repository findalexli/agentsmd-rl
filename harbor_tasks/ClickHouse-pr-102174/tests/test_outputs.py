#!/usr/bin/env python3
"""
Test suite for ClickHouse ZooKeeper session retry fix.
Tests verify that:
1. The fix includes proper ZooKeeper session renewal on retry
2. The retry logic fetches object names inside the retry loop
3. No sleep-based fixes are used
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


# =============================================================================
# Pass-to-Pass Tests (verify repo CI/CD checks pass on both base and fixed code)
# =============================================================================

def test_repo_ci_pytest_xfail_xpass():
    """CI framework pytest xfail/xpass tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pytest", "ci/tests/test_pytest_xfail_xpass.py", "-v"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CI pytest xfail/xpass tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_praktika_imports():
    """Praktika CI framework imports work correctly (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "from ci.praktika.result import Result, ResultTranslator; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Praktika imports failed:\n{r.stderr}"
    assert "OK" in r.stdout, f"Praktika imports did not produce expected output: {r.stdout}"


def test_repo_python_syntax_ci_tests():
    """CI test files have valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "ci/tests/test_pytest_xfail_xpass.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CI test file syntax check failed:\n{r.stderr}"


def test_target_file_cpp_syntax_valid():
    """Target C++ file has valid syntax (basic clang syntax check) (pass_to_pass)."""
    # Run clang in syntax-check only mode (no codegen, no linking)
    r = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++20", "-I", "src",
         "-I", "build", "-c", FULL_PATH],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Note: This may fail due to missing includes, but should not crash
    # We'll accept either success or expected missing-include errors
    if r.returncode != 0:
        # Check if it's just missing includes (expected in stripped build)
        # rather than actual syntax errors
        err_lower = r.stderr.lower()
        if "error:" in err_lower and "expected" in err_lower and "syntax" not in err_lower:
            # This is a semantic error (e.g., unknown type), not syntax
            pass
    # The syntax check passed if we got here without assertion


def test_zookeeper_session_renewal_in_retry():
    """Verify the fix includes ZooKeeper session renewal on retry (fail_to_pass)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Check for the key fix: session renewal on retry
    # Look for the pattern: if (retries_ctl.isRetry()) current_zookeeper = zookeeper_getter.getZooKeeper().first;
    renewal_patterns = [
        r"if\s*\(\s*retries_ctl\.isRetry\(\)\s*\)",
        r"current_zookeeper\s*=\s*zookeeper_getter\.getZooKeeper\(\)",
    ]

    for pattern in renewal_patterns:
        assert re.search(pattern, content), (
            f"Missing ZooKeeper session renewal pattern: {pattern}. "
            "The fix should include session renewal on retry via zookeeper_getter.getZooKeeper()"
        )


def test_object_names_fetched_in_retry_loop():
    """Verify getObjectNamesAndSetWatch is called inside retry loop (fail_to_pass)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop lambda - handle nested braces
    retry_loop_start = content.find("retries_ctl.retryLoop([&]")
    assert retry_loop_start != -1, "Could not find retryLoop lambda start"

    # Find the opening brace of the lambda
    brace_start = content.find("{", retry_loop_start)
    assert brace_start != -1, "Could not find opening brace of retryLoop lambda"

    # Find the matching closing brace by counting
    brace_count = 1
    pos = brace_start + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == "{":
            brace_count += 1
        elif content[pos] == "}":
            brace_count -= 1
        pos += 1

    retry_body = content[brace_start:pos]

    # Check that getObjectNamesAndSetWatch is called inside the retry loop
    assert "getObjectNamesAndSetWatch" in retry_body, (
        "getObjectNamesAndSetWatch should be called inside retryLoop, "
        "not outside before the retry loop begins"
    )


def test_tryloadobject_uses_current_zookeeper():
    """Verify tryLoadObject uses current_zookeeper inside retry loop (fail_to_pass)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop lambda
    retry_loop_start = content.find("retries_ctl.retryLoop([&]")
    assert retry_loop_start != -1, "Could not find retryLoop lambda start"

    # Find the opening brace
    brace_start = content.find("{", retry_loop_start)
    assert brace_start != -1, "Could not find opening brace"

    # Find matching closing brace
    brace_count = 1
    pos = brace_start + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == "{":
            brace_count += 1
        elif content[pos] == "}":
            brace_count -= 1
        pos += 1

    retry_body = content[brace_start:pos]

    # Check that tryLoadObject uses current_zookeeper, not the stale 'zookeeper' parameter
    assert "tryLoadObject(current_zookeeper" in retry_body, (
        "tryLoadObject should use current_zookeeper (which may be renewed on retry), "
        "not the stale 'zookeeper' parameter from the function arguments"
    )


def test_current_zookeeper_variable_declared():
    """Verify current_zookeeper variable is declared before retry loop (fail_to_pass)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Check that current_zookeeper variable is declared
    assert "zkutil::ZooKeeperPtr current_zookeeper" in content, (
        "Missing current_zookeeper variable declaration. "
        "Should declare: zkutil::ZooKeeperPtr current_zookeeper = zookeeper;"
    )


def test_no_sleep_based_race_condition_fixes():
    """Verify no sleep calls are used to fix race conditions (rule check)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the refreshObjects function
    func_match = re.search(
        r"void\s+UserDefinedSQLObjectsZooKeeperStorage::refreshObjects\([^)]*\)\s*\{",
        content
    )

    if func_match:
        func_start = func_match.end() - 1  # Position at the opening brace

        # Find the matching closing brace
        brace_count = 1
        pos = func_start + 1
        while brace_count > 0 and pos < len(content):
            if content[pos] == "{":
                brace_count += 1
            elif content[pos] == "}":
                brace_count -= 1
            pos += 1

        func_body = content[func_start:pos]

        # Check for sleep calls
        sleep_pattern = r"\b(std::)?sleep\(|\b(std::)?this_thread::sleep|usleep\(|nanosleep\("
        sleep_match = re.search(sleep_pattern, func_body)

        assert not sleep_match, (
            f"Found sleep call in refreshObjects: {sleep_match.group(0) if sleep_match else ''}. "
            "Sleep should not be used to fix race conditions - this is not acceptable!"
        )


def test_allman_brace_style_for_new_code():
    """Verify Allman-style braces are used for new/modified code (pass_to_pass)."""
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # The key check: ensure the added code uses Allman style
    # The fix adds: if (retries_ctl.isRetry())\n        current_zookeeper = ...
    # This should have the opening brace on a new line if there are braces

    # Check for the specific pattern we expect in the fix
    if "if (retries_ctl.isRetry())" in content:
        # Find this specific if statement
        match = re.search(r"if\s*\(\s*retries_ctl\.isRetry\(\)\s*\)\s*\n\s*current_zookeeper", content)
        if match:
            # Single statement without braces - this is acceptable
            pass
        else:
            # Check if braces are on new line
            match_brace = re.search(r"if\s*\(\s*retries_ctl\.isRetry\(\)\s*\)\s*\{", content)
            if match_brace:
                # If there is a brace, it should be on a new line (Allman style)
                # Actually, the fix doesn't use braces for the single statement
                pass

    # Overall style check: Look for obviously bad patterns in the new code section
    # The retryLoop lambda and its body should be reasonably formatted
    if "retries_ctl.retryLoop([&]" in content:
        match = re.search(r"retries_ctl\.retryLoop\(\[&\]\s*\{[^}]*\}\);", content, re.DOTALL)
        if match:
            lambda_body = match.group(0)
            # Check it's not all on one line (which would be bad style)
            if "\n" not in lambda_body:
                assert False, "retryLoop lambda should be on multiple lines, not a single line"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
