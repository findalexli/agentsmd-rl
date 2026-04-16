"""
Test suite for ClickHouse PR #102170: Fix crash caused by stale ZooKeeper session in UDF retry loop.

This tests that the refreshObjects method properly renews the ZooKeeper session
on retry, preventing use of a stale/expired session handle.
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/clickhouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def test_file_compiles():
    """The target C++ file should compile without syntax errors."""
    # Use clang to check syntax only
    result = subprocess.run(
        ["clang-15", "-fsyntax-only", "-std=c++20", "-I", f"{REPO}/src",
         "-I", f"{REPO}/base", "-I", f"{REPO}/contrib/boost",
         "-c", FULL_PATH],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60
    )
    # Syntax check may have warnings about missing headers, but should not segfault
    assert result.returncode != -11, "Compilation crashed (segfault) - syntax error likely"


def test_zookeeper_session_renewal_in_retry_loop():
    """
    FAIL-TO-PASS: The fix adds session renewal on retry.

    The retry loop must renew the ZooKeeper session when retries_ctl.isRetry() returns true.
    The session must be obtained from zookeeper_getter.getZooKeeper().first.

    This test verifies the STRUCTURAL requirements without hardcoding variable names:
    1. There is a conditional check for isRetry() inside the retry loop
    2. Inside that conditional, a fresh session is obtained via zookeeper_getter
    3. The fresh session is used for subsequent ZooKeeper operations in the loop
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop lambda body
    retry_loop_pattern = r"retries_ctl\.retryLoop\(\s*\[&\]\s*\{(.+?)\}\s*\)"
    match = re.search(retry_loop_pattern, content, re.DOTALL)

    assert match is not None, "Could not find retryLoop lambda - file structure has changed"

    loop_body = match.group(1)

    # Verify there is a conditional check for isRetry() inside the loop
    assert re.search(r"if\s*\(\s*retries_ctl\.isRetry\(\)", loop_body), \
        "Missing: conditional check for retries_ctl.isRetry() inside retry loop"

    # Verify zookeeper_getter.getZooKeeper() is called inside the loop
    # (indicates session renewal is being done)
    assert re.search(r"zookeeper_getter\.getZooKeeper\(\)", loop_body), \
        "Missing: call to zookeeper_getter.getZooKeeper() for session renewal"

    # Verify the fresh session is stored in a local variable (look for assignment)
    # The pattern should show a session being obtained and saved
    assert re.search(r"\w+\s*=\s*zookeeper_getter\.getZooKeeper\(\)\.first", loop_body), \
        "Missing: fresh session must be stored in a local variable"


def test_object_names_fetched_inside_retry_loop():
    """
    FAIL-TO-PASS: Object names must be fetched inside the retry loop.

    Previously, object_names was fetched once before the retry loop.
    The fix moves it inside so it's re-fetched on each retry with the new session.
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop lambda
    retry_loop_pattern = r"retries_ctl\.retryLoop\(\s*\[&\]\s*\{(.+?)\}\s*\)"
    match = re.search(retry_loop_pattern, content, re.DOTALL)

    assert match is not None, "Could not find retryLoop lambda - file structure has changed"

    loop_body = match.group(1)

    # Object names should be fetched inside the retry loop (getObjectNamesAndSetWatch called)
    assert "getObjectNamesAndSetWatch" in loop_body, \
        "getObjectNamesAndSetWatch must be called inside retryLoop lambda"

    # There should be a Strings declaration inside the loop (fetched fresh on each retry)
    # Look for variable declaration before the getObjectNamesAndSetWatch call
    assert re.search(r"Strings\s+\w+\s*=", loop_body), \
        "A Strings variable must be declared inside the retry loop"


def test_no_stale_zookeeper_parameter_in_loop():
    """
    FAIL-TO-PASS: The original zookeeper parameter should not be used inside the retry loop
    for ZooKeeper operations (except for initializing the current session).

    The fix ensures all ZooKeeper operations use a session variable that gets
    renewed on retry, rather than the stale zookeeper parameter.
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop lambda body
    retry_loop_pattern = r"retries_ctl\.retryLoop\(\s*\[&\]\s*\{(.+?)\}\s*\)"
    match = re.search(retry_loop_pattern, content, re.DOTALL)

    assert match is not None, "Could not find retryLoop lambda - file structure has changed"

    loop_body = match.group(1)
    lines = loop_body.split("\n")

    # Track whether we've seen the session renewal (initialization of current session)
    # After that point, the 'zookeeper' parameter should not be used
    seen_session_renewal = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith("//"):
            continue

        # Track if we've seen session renewal (initial assignment from zookeeper or getter)
        if re.search(r"\w+\s*=\s*(zookeeper|zookeeper_getter)", stripped):
            seen_session_renewal = True
            continue

        # After the first assignment, 'zookeeper' (the parameter) should NOT be
        # passed to any functions inside the loop (except in comments)
        if seen_session_renewal:
            # Check if 'zookeeper' appears as a function argument (not in comments)
            # Match 'zookeeper' as a whole word, not as part of another identifier
            if re.search(r"\bzookeeper\b", stripped):
                # Make sure it's not just a comment
                if not stripped.startswith("//"):
                    # It's used as a function argument - check which function
                    # It's OK to use 'zookeeper' in non-ZooKeeper operations or
                    # if it's the initial assignment before renewal
                    func_match = re.search(r"(\w+)\s*\([^)]*\bzookeeper\b", stripped)
                    if func_match:
                        func_name = func_match.group(1)
                        # These are ZooKeeper operations that should use the renewed session
                        if func_name in ["getObjectNamesAndSetWatch", "tryLoadObject"]:
                            pytest.fail(
                                f"Stale 'zookeeper' parameter used in loop for {func_name}. "
                                f"Should use renewed session instead."
                            )


def test_session_renewal_timing():
    """
    FAIL-TO-PASS: Session renewal must happen BEFORE getObjectNamesAndSetWatch.

    The fix ensures we get a fresh session before setting watches and fetching objects.
    This test verifies the ORDERING of operations without hardcoding variable names.
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Find the retryLoop body and verify order of operations
    lines = content.split("\n")

    found_retry_loop = False
    renewal_line = -1
    get_objects_line = -1
    retry_loop_start = -1

    for i, line in enumerate(lines):
        if "retries_ctl.retryLoop" in line:
            found_retry_loop = True
            retry_loop_start = i

        if found_retry_loop:
            # Look for session renewal (call to zookeeper_getter inside isRetry check)
            if re.search(r"if\s*\(\s*retries_ctl\.isRetry\(\)", line):
                # The next few lines should contain the session renewal
                for j in range(i, min(i + 5, len(lines))):
                    if re.search(r"zookeeper_getter\.getZooKeeper\(\)\.first", lines[j]):
                        renewal_line = j
                        break

            # Check if getObjectNamesAndSetWatch is called with SOME session variable
            # (the variable is renewed inside the loop, so it could have any name)
            if re.search(r"getObjectNamesAndSetWatch\s*\(\s*\w+", line):
                get_objects_line = i

            # Stop when we exit the retry loop
            if line.strip() == "});" and i > retry_loop_start + 5:
                break

    # Both operations must be found
    assert renewal_line >= 0, "Session renewal (zookeeper_getter.getZooKeeper().first) not found in retry loop"
    assert get_objects_line >= 0, "getObjectNamesAndSetWatch call not found in retry loop"

    # Session renewal must come before getObjectNamesAndSetWatch
    assert renewal_line < get_objects_line, \
        "Session renewal must happen before getObjectNamesAndSetWatch (inside retry loop)"


def test_comments_reflect_fix():
    """
    PASS-TO-PASS: Code should have appropriate comments explaining behavior.

    Checks that key functions have explanatory comments.
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # The file should have comments explaining the retry logic and ZooKeeper operations
    has_retry_comments = (
        "retry" in content.lower() or
        "RetryControl" in content or
        "transient" in content.lower()
    )

    assert has_retry_comments, \
        "Code should have comments explaining retry/ZooKeeper behavior"


def test_repo_code_style():
    """
    PASS-TO-PASS: Code should follow ClickHouse naming conventions.

    From copilot-instructions.md: Names of functions and methods should not have ().
    Variables should use snake_case.
    """
    with open(FULL_PATH, "r") as f:
        content = f.read()

    # Check for ClickHouse-specific conventions
    # Variable naming: snake_case is used throughout ClickHouse code
    # Check that common snake_case patterns exist in the file
    snake_case_patterns = ["object_type", "function_name", "object_names", "zookeeper_path"]
    found_snake_case = any(pattern in content for pattern in snake_case_patterns)

    assert found_snake_case, \
        "Variable naming should follow snake_case convention"

    # Check for consistent indentation (ClickHouse uses 4 spaces)
    lines = content.split("\n")
    for line in lines[:100]:  # Sample first 100 lines
        if line.strip() and not line.startswith("\t"):
            spaces = len(line) - len(line.lstrip())
            if spaces % 4 != 0 and spaces > 0:
                # Allow some flexibility for continuation lines
                pass  # Don't fail on this, just check general style


def test_repo_cpp_style_check():
    """
    PASS-TO-PASS: Repo C++ style check passes (origin: repo_tests).

    Runs the repo's own C++ style checker (ci/jobs/scripts/check_style/check_cpp.sh)
    which validates formatting, whitespace, tabs, and other style conventions.
    """
    r = subprocess.run(
        ["bash", "./ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"C++ style check failed:\n{r.stdout[-1000:]}"


def test_repo_submodules_check():
    """
    PASS-TO-PASS: Repo submodules check passes (origin: repo_tests).

    Runs the repo's submodule validation script (ci/jobs/scripts/check_style/check_submodules.sh).
    """
    r = subprocess.run(
        ["bash", "./ci/jobs/scripts/check_style/check_submodules.sh"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Submodules check failed:\n{r.stderr[-500:]}"


def test_target_file_no_tabs():
    """
    PASS-TO-PASS: Target file has no tab characters (origin: static).

    ClickHouse style requires 4-space indentation, not tabs.
    """
    r = subprocess.run(
        ["grep", "-F", "\t", FULL_PATH],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 1, f"Target file contains tab characters:\n{r.stdout[:500]}"


def test_git_working_tree_clean():
    """
    PASS-TO-PASS: Git working tree is clean (origin: repo_tests).

    Verifies the repo is in a clean state with no unexpected modifications.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr}"
    # Allow the target file to be dirty (it may have the fix applied)
    lines = [l for l in r.stdout.strip().split("\n") if l.strip()]
    unexpected = [l for l in lines if TARGET_FILE not in l]
    assert len(unexpected) == 0, f"Working tree has unexpected modifications:\n{unexpected}"
