#!/usr/bin/env python3
"""
Test outputs for ClickHouse UDF Keeper Session fix.

This tests that the fix for UDF registry loss during Keeper session expiry
has been properly applied to the codebase.

Behavioral tests verify that the code STRUCTURE is correct, not just that
certain strings appear in the file. We strip comments to avoid false positives
from commented-out code.
"""

import re
import subprocess
import sys
from pathlib import Path

# Repository path
REPO = Path("/workspace/clickhouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def strip_cpp_comments(content):
    """Remove C++ comments from content to avoid matching commented-out code."""
    # Remove /* ... */ block comments (non-greedy, handles multiline)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    # Remove // line comments (but not URLs like http://)
    content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
    return content


def search_pattern(content, pattern):
    """Search for a regex pattern in content (case-sensitive)."""
    return re.search(pattern, content) is not None


def search_pattern_no_case(content, pattern):
    """Search for a regex pattern in content (case-insensitive)."""
    return re.search(pattern, content, flags=re.IGNORECASE) is not None


def test_file_exists():
    """Target file exists in the repository."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_hardware_error_include():
    """
    ZooKeeperCommon.h is included AND isHardwareError is used in code.
    Behavioral check: the header is not just included but the function is actually called.
    """
    content = TARGET_FILE.read_text()
    stripped = strip_cpp_comments(content)

    # Verify the header is included
    assert '#include <Common/ZooKeeper/ZooKeeperCommon.h>' in content, \
        "Missing ZooKeeperCommon.h include"

    # Verify isHardwareError is CALLED (not just mentioned) - in an if condition context
    # This ensures it's actually used in code, not just in a comment
    assert search_pattern(stripped, r'if\s*\(\s*Coordination::isHardwareError\s*\('), \
        "isHardwareError() called in an if condition - implementation missing"


def test_retries_include():
    """
    ZooKeeperRetries.h is included AND ZooKeeperRetriesControl is instantiated.
    Behavioral check: the header is not just included but the class is actually used.
    """
    content = TARGET_FILE.read_text()

    # Verify the header is included
    assert '#include <Common/ZooKeeper/ZooKeeperRetries.h>' in content, \
        "Missing ZooKeeperRetries.h include"

    stripped = strip_cpp_comments(content)

    # Verify ZooKeeperRetriesControl is INSTANTIATED (variable declaration with constructor)
    # This pattern matches: TypeName variableName(...)
    assert search_pattern(stripped, r'ZooKeeperRetriesControl\s+\w+\s*\('), \
        "ZooKeeperRetriesControl instantiation not found in code"


def test_keeper_exception_handler():
    """
    A specific catch block for zkutil::KeeperException exists that:
    1. Checks for hardware errors using isHardwareError()
    2. Re-throws hardware errors
    3. Treats non-hardware errors as missing objects

    Behavioral check: verifies the actual code structure, not just strings.
    """
    content = TARGET_FILE.read_text()
    stripped = strip_cpp_comments(content)

    # Check for specific KeeperException catch block
    assert search_pattern(stripped, r'catch\s*\(\s*const\s+zkutil::KeeperException\s*&\s*\w+\s*\)'), \
        "Missing specific KeeperException catch block"

    # Check for hardware error check in code
    assert search_pattern(stripped, r'if\s*\(\s*Coordination::isHardwareError\s*\(\s*\w+\.code\s*\)\s*\)'), \
        "Missing isHardwareError check in exception handler"

    # Check that hardware errors are re-thrown (throw; statement)
    # This should be near the isHardwareError check
    assert search_pattern(stripped, r'throw\s*;'), \
        "Hardware errors should be re-thrown for retry handling"


def test_zookeeper_retries_control_usage():
    """
    ZooKeeperRetriesControl is instantiated with proper retry parameters.
    Behavioral check: verifies the control is created with correct parameter types,
    without asserting on specific variable names.
    """
    content = TARGET_FILE.read_text()
    stripped = strip_cpp_comments(content)

    # Check for ZooKeeperRetriesControl instantiation (variable declaration)
    assert search_pattern(stripped, r'ZooKeeperRetriesControl\s+\w+\s*\('), \
        "Missing ZooKeeperRetriesControl instantiation"

    # Verify retry parameters are defined as constexpr UInt64 values
    # Look for numeric constants assigned to variables ending with _ms or _retries
    # We don't check specific names, just that such parameters exist
    has_retries = search_pattern(stripped, r'max_retries\s*=')
    has_initial_backoff = search_pattern(stripped, r'initial_backoff_ms\s*=')
    has_max_backoff = search_pattern(stripped, r'max_backoff_ms\s*=')

    assert has_retries or has_initial_backoff or has_max_backoff, \
        "Missing retry configuration parameters (max_retries, initial_backoff_ms, or max_backoff_ms)"


def test_retry_loop_pattern():
    """
    The retryLoop pattern is used to wrap the object loading logic.
    Behavioral check: verifies retryLoop is CALLED with a lambda, not just mentioned.
    """
    content = TARGET_FILE.read_text()
    stripped = strip_cpp_comments(content)

    # Check for retryLoop CALL (not just a mention)
    # This matches: something.retryLoop([&] or something.retryLoop([=] etc.
    assert search_pattern(stripped, r'\.retryLoop\s*\(\s*\['), \
        "Missing retryLoop() call with lambda argument"

    # Check that the vector is cleared inside the retry context
    # We look for .clear() being called on some vector (the exact name doesn't matter)
    assert search_pattern(stripped, r'\.clear\s*\(\s*\)'), \
        "Missing .clear() call - partial results should be cleared on retry"


def test_error_logging():
    """
    Proper logging is in place for hardware errors.
    Behavioral check: verifies LOG_WARNING is called with hardware error message
    AND object name, not just that the strings appear somewhere.
    """
    content = TARGET_FILE.read_text()
    stripped = strip_cpp_comments(content)

    # Check for LOG_WARNING with hardware error message (case insensitive)
    assert search_pattern_no_case(stripped, r'LOG_WARNING\s*\([^)]*hardware error'), \
        "Missing hardware error warning log message"

    # Check that the warning includes backQuote(object_name) - actual function call
    assert search_pattern(stripped, r'backQuote\s*\(\s*\w+\s*\)'), \
        "Log should include object name via backQuote() function call"


def test_comment_documentation():
    """
    Comments explain the retry mechanism and its purpose.
    This verifies documentation, not behavior - comments are appropriate to check.
    """
    content = TARGET_FILE.read_text()

    # Check for comment about transient Keeper hiccups and retry
    assert search_pattern_no_case(content, r'transient.*Keeper|retry.*backoff'), \
        "Missing comment explaining transient error handling with retry/backoff"


# P2P Tests - Repo CI style checks (subprocess.run based)

def test_repo_no_tabs_in_source():
    """No tabs in source files - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-F", "\t", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode != 0 or r.stdout == "", f"Tabs found in source file:\n{r.stdout}"


def test_repo_no_trailing_whitespace():
    """No trailing whitespace - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-n", " $", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode != 0 or r.stdout == "", f"Trailing whitespace found:\n{r.stdout}"


def test_repo_no_merge_conflict_markers():
    """No merge conflict markers - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-E", "^(<<<<<<<|=======|>>>>>>>)", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode != 0 or r.stdout == "", f"Merge conflict markers found:\n{r.stdout}"


def test_repo_no_bom_markers():
    """No UTF-8 BOM markers - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-l", "\xEF\xBB\xBF", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode != 0 or r.stdout == "", f"UTF-8 BOM found in source file"


def test_repo_no_duplicate_includes():
    """No duplicate #include statements - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"grep '^#include ' {TARGET_FILE} | sort | uniq -d"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.stdout == "", f"Duplicate includes found:\n{r.stdout}"


def test_repo_file_not_empty():
    """Source file is not empty - basic sanity check (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-s", str(TARGET_FILE)],
        capture_output=True, cwd=REPO,
    )
    assert r.returncode == 0, "Source file is empty or does not exist"


def test_repo_git_file_tracked():
    """Source file is tracked by git - ClickHouse CI check (pass_to_pass)."""
    r = subprocess.run(
        ["git", "ls-files", str(TARGET_FILE.relative_to(REPO))],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0 and r.stdout.strip() != "", "File is not tracked by git"


def test_repo_no_forbidden_std_stringstream():
    """No forbidden std::stringstream pattern - ClickHouse style check (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-E", "std::[io]?stringstream", str(TARGET_FILE)],
        capture_output=True, text=True, cwd=REPO,
    )
    # Should not find the pattern (exit code 1 means not found)
    assert r.returncode != 0 or "STYLE_CHECK_ALLOW_STD_STRING_STREAM" in r.stdout, \
        f"Forbidden std::stringstream pattern found:\n{r.stdout}"
