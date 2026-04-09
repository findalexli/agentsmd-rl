#!/usr/bin/env python3
"""
Tests for UDF registry loss fix during Keeper session expiry.

The fix addresses two issues:
1. tryLoadObject() catches all KeeperException errors the same way, meaning hardware
   errors (connection loss, session expiry) are treated like "node not found" errors
2. refreshObjects() doesn't retry when Keeper hiccups occur

The fix:
1. Adds special handling in tryLoadObject() to re-throw hardware errors so they can be retried
2. Adds ZooKeeperRetriesControl with backoff to refreshObjects() to handle transient failures
"""

import subprocess
import os
import re
import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def read_target_file():
    """Read the target source file."""
    with open(FULL_PATH, 'r') as f:
        return f.read()


def test_hardware_error_handling():
    """
    FAIL TO PASS: tryLoadObject must re-throw Keeper hardware errors.

    The fix adds a catch block specifically for zkutil::KeeperException that:
    - Checks if the error is a hardware error using Coordination::isHardwareError()
    - Re-throws hardware errors so the caller can handle them (retry)
    - Treats non-hardware errors as missing objects (returns nullptr)
    """
    content = read_target_file()

    # Check for the new KeeperException catch block with hardware error handling
    pattern = r'catch\s*\(\s*const\s+zkutil::KeeperException\s*&\s*e\s*\)'
    match = re.search(pattern, content)
    assert match is not None, (
        "Missing catch block for zkutil::KeeperException. "
        "The fix should catch KeeperException separately to handle hardware errors."
    )

    # Check for isHardwareError call
    assert 'isHardwareError(e.code)' in content, (
        "Missing isHardwareError(e.code) check. "
        "Hardware errors must be detected to trigger retry logic."
    )

    # Check that hardware errors are re-thrown
    hardware_section = content[match.start():match.start() + 800]
    assert 'throw;' in hardware_section, (
        "Hardware errors must be re-thrown to allow retry. "
        "The catch block should re-throw after logging the hardware error."
    )


def test_retry_constants():
    """
    FAIL TO PASS: Retry constants must be defined correctly.

    The fix uses these constants for the retry logic:
    - max_retries = 5
    - initial_backoff_ms = 200
    - max_backoff_ms = 5000
    """
    content = read_target_file()

    # Check for retry constants
    assert 'static constexpr UInt64 max_retries = 5;' in content, (
        "Missing or incorrect max_retries constant. Should be 'static constexpr UInt64 max_retries = 5;'"
    )

    assert 'static constexpr UInt64 initial_backoff_ms = 200;' in content, (
        "Missing or incorrect initial_backoff_ms constant. Should be 'static constexpr UInt64 initial_backoff_ms = 200;'"
    )

    assert 'static constexpr UInt64 max_backoff_ms = 5000;' in content, (
        "Missing or incorrect max_backoff_ms constant. Should be 'static constexpr UInt64 max_backoff_ms = 5000;'"
    )


def test_zookeeper_retries_control():
    """
    FAIL TO PASS: refreshObjects must use ZooKeeperRetriesControl.

    The fix wraps the object loading loop in a ZooKeeperRetriesControl retryLoop
    to handle transient Keeper hiccups with automatic backoff.
    """
    content = read_target_file()

    # Check for ZooKeeperRetriesControl usage
    assert 'ZooKeeperRetriesControl retries_ctl' in content, (
        "Missing ZooKeeperRetriesControl instance. "
        "refreshObjects should use ZooKeeperRetriesControl for retry logic."
    )

    # Check for retryLoop call
    assert 'retries_ctl.retryLoop' in content, (
        "Missing retries_ctl.retryLoop() call. "
        "The object loading should be wrapped in a retry loop."
    )

    # Check for function_names_and_asts.clear() inside retry loop
    assert 'function_names_and_asts.clear()' in content, (
        "Missing function_names_and_asts.clear() in retry loop. "
        "The vector must be cleared at the start of each retry attempt."
    )


def test_includes_added():
    """
    FAIL TO PASS: Required headers must be included.

    The fix requires these additional includes:
    - ZooKeeperCommon.h for isHardwareError()
    - ZooKeeperRetries.h for ZooKeeperRetriesControl
    """
    content = read_target_file()

    # Check for new includes
    assert '#include <Common/ZooKeeper/ZooKeeperCommon.h>' in content, (
        "Missing ZooKeeperCommon.h include. Required for isHardwareError()."
    )

    assert '#include <Common/ZooKeeper/ZooKeeperRetries.h>' in content, (
        "Missing ZooKeeperRetries.h include. Required for ZooKeeperRetriesControl."
    )


def test_hardware_error_log_message():
    """
    FAIL TO PASS: Specific log message for hardware errors must exist.

    The fix adds a distinctive warning log for Keeper hardware errors.
    """
    content = read_target_file()

    # Check for the specific log message
    assert 'Keeper hardware error while loading user defined SQL object' in content, (
        "Missing distinctive hardware error log message. "
        "The fix should log a specific warning when hardware errors occur."
    )


def test_catch_ordering():
    """
    FAIL TO PASS: KeeperException catch must come before the generic catch.

    Since KeeperException is a subclass of std::exception (caught by catch (...)),
    the specific catch block must appear before the generic catch (...).
    """
    content = read_target_file()

    # Find the tryLoadObject function and look at the catch blocks within it
    # The new catch blocks are added around line 360-375 in the tryLoadObject function
    tryloadobject_start = content.find('tryLoadObject')
    assert tryloadobject_start != -1, "Could not find tryLoadObject function"

    # Get a section of the file starting from tryLoadObject (about 500 chars should cover the function)
    tryloadobject_section = content[tryloadobject_start:tryloadobject_start + 5000]

    # Find both catch blocks within this section (relative positions)
    keeper_catch_rel = tryloadobject_section.find('catch (const zkutil::KeeperException & e)')
    generic_catch_rel = tryloadobject_section.find('catch (...)', tryloadobject_section.find('ASTPtr UserDefinedSQLObjectsZooKeeperStorage::tryLoadObject'))

    assert keeper_catch_rel != -1, "Missing KeeperException catch block in tryLoadObject"

    # Find the generic catch AFTER the KeeperException catch in this function
    # Look for the second catch (...) after KeeperException catch
    generic_after_keeper = tryloadobject_section.find('catch (...)', keeper_catch_rel)
    assert generic_after_keeper != -1, "Missing generic catch (...) block after KeeperException catch"

    # Keeper catch must come before the generic catch in the same scope
    # This verifies the ordering is correct for the new catch blocks added by the fix


def test_code_compiles_syntax():
    """
    PASS TO PASS: Basic syntax validation.

    Verify the file has valid C++ syntax by checking for balanced braces
    and proper structure. This is a lightweight check.
    """
    content = read_target_file()

    # Check for basic C++ structure
    assert 'namespace DB' in content, "Missing DB namespace"

    # Count braces as a basic syntax check
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open, {close_braces} close"
    )

    # Check for class or function definitions
    assert 'UserDefinedSQLObjectsZooKeeperStorage' in content, (
        "Missing UserDefinedSQLObjectsZooKeeperStorage class reference"
    )


def test_repo_style_checks():
    """
    PASS TO PASS: Repository style checks pass.

    Runs the repository's style check scripts that validate code hygiene:
    - check_submodules.sh: submodule integrity
    These are fast, non-compilation checks that ensure code quality.
    """
    # Skip if git repo not available (e.g., minimal Docker clone)
    git_dir = os.path.join(REPO, ".git")
    if not os.path.exists(git_dir):
        pytest.skip("Git repository not available (minimal clone)")

    style_scripts = [
        "./ci/jobs/scripts/check_style/check_submodules.sh",
    ]

    for script in style_scripts:
        # Skip if script doesn't exist
        if not os.path.exists(os.path.join(REPO, script)):
            pytest.skip(f"Style check script {script} not found")

        r = subprocess.run(
            ["bash", script],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Style check script {script} failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
        )


def test_repo_cpp_style():
    """
    PASS TO PASS: C++ style checks pass (no new issues in target file).

    Runs the repository's C++ style check script. This validates:
    - No trailing whitespace
    - Proper include style
    - No forbidden APIs
    - Proper brace style
    - And many other C++ style rules

    Only checks that the target file doesn't introduce NEW style issues.
    """
    # Skip if git repo not available (e.g., minimal Docker clone)
    git_dir = os.path.join(REPO, ".git")
    if not os.path.exists(git_dir):
        pytest.skip("Git repository not available (minimal clone)")

    # Skip if script doesn't exist
    script_path = "./ci/jobs/scripts/check_style/check_cpp.sh"
    if not os.path.exists(os.path.join(REPO, script_path)):
        pytest.skip(f"Style check script {script_path} not found")

    # First install ripgrep which is required by the check script
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Ignore apt-get errors, ripgrep may already be installed

    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "ripgrep"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Ignore apt-get errors, ripgrep may already be installed

    r = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )

    # The script may find pre-existing issues, but we only fail if the
    # target file has issues. Check that the target file path doesn't
    # appear in the error output.
    if r.returncode != 0:
        target_file_rel = TARGET_FILE
        # check if target file appears in the output
        if target_file_rel in r.stdout or target_file_rel.replace(
            "/", ""
        ) in r.stdout.replace("/", ""):
            assert False, (
                f"C++ style check found issues in target file:\n{r.stdout[-1000:]}"
            )
        # If target file not in output, pre-existing issues are acceptable
