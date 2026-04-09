#!/usr/bin/env python3
"""
Test suite for ClickHouse PR #102170: Fix crash caused by stale ZooKeeper session in UDF retry loop.

The bug: In refreshObjects(), the object_names list and zookeeper handle were captured BEFORE
the retry loop. If the session expired and a retry occurred, the code would use stale data.

The fix: Move getObjectNamesAndSetWatch() inside the retry loop and obtain a fresh session
on each retry via zookeeper_getter.
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/clickhouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def get_refresh_objects_function():
    """Extract the refreshObjects function content from the source file."""
    content = TARGET_FILE.read_text()

    # Find the refreshObjects function
    pattern = r'void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects\(const zkutil::ZooKeeperPtr & zookeeper, UserDefinedSQLObjectType object_type\).*?(?=\nvoid |\n}\s*\Z|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        # Try a more flexible search
        start_idx = content.find('void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects')
        if start_idx == -1:
            return None

        # Find the end of the function (next function definition or end of class)
        next_func = content.find('\nvoid ', start_idx + 1)
        next_class_end = content.find(r'\n}\s*\n', start_idx)

        if next_func != -1:
            end_idx = next_func
        elif next_class_end != -1:
            end_idx = next_class_end
        else:
            end_idx = len(content)

        return content[start_idx:end_idx]

    return match.group(0)


def test_fix_session_refresh_in_retry_loop():
    """
    FAIL-TO-PASS: Verify that on retry, a fresh ZooKeeper session is obtained.

    The fix adds: if (retries_ctl.isRetry()) current_zookeeper = zookeeper_getter.getZooKeeper().first;
    """
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Check for the key fix: obtaining fresh session on retry
    has_retry_check = 'retries_ctl.isRetry()' in func_content
    has_session_refresh = 'zookeeper_getter.getZooKeeper()' in func_content
    has_current_zookeeper = 'current_zookeeper' in func_content

    assert has_retry_check, "Missing retry check - should call isRetry() to detect retry condition"
    assert has_session_refresh, "Missing session refresh - should get fresh ZooKeeper on retry"
    assert has_current_zookeeper, "Missing current_zookeeper variable - should use fresh session handle"


def test_fix_object_names_inside_retry_loop():
    """
    FAIL-TO-PASS: Verify that getObjectNamesAndSetWatch is called INSIDE the retry loop.

    The bug: object_names was fetched BEFORE the retry loop, using stale data on retry.
    The fix: Move the call inside the retryLoop lambda so it's re-fetched on each retry.
    """
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find the retryLoop lambda
    retry_loop_match = re.search(
        r'retries_ctl\.retryLoop\(\[&\].*?\{.*?\}\);',
        func_content,
        re.DOTALL
    )

    if not retry_loop_match:
        # Try simpler pattern
        retry_start = func_content.find('retries_ctl.retryLoop([&]')
        if retry_start == -1:
            pytest.fail("Could not find retryLoop call")

        # Extract the lambda body (approximately)
        brace_start = func_content.find('{', retry_start)
        if brace_start == -1:
            pytest.fail("Could not find retryLoop lambda body")

        # Find matching closing brace
        brace_count = 0
        lambda_end = brace_start
        for i, char in enumerate(func_content[brace_start:]):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    lambda_end = brace_start + i
                    break

        lambda_content = func_content[brace_start:lambda_end+1]
    else:
        lambda_content = retry_loop_match.group(0)

    # The fix requires getObjectNamesAndSetWatch to be INSIDE the retry loop
    assert 'getObjectNamesAndSetWatch' in lambda_content, \
        "getObjectNamesAndSetWatch must be called INSIDE the retryLoop lambda, not before it"


def test_fix_uses_current_zookeeper_in_tryload():
    """
    FAIL-TO-PASS: Verify that tryLoadObject uses current_zookeeper, not the original zookeeper handle.

    The fix changes tryLoadObject(zookeeper, ...) to tryLoadObject(current_zookeeper, ...)
    """
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find the retryLoop lambda content
    retry_start = func_content.find('retries_ctl.retryLoop([&]')
    if retry_start == -1:
        pytest.fail("Could not find retryLoop call")

    # Extract lambda body
    brace_start = func_content.find('{', retry_start)
    if brace_start == -1:
        pytest.fail("Could not find retryLoop lambda body")

    # Count braces to find the end
    brace_count = 0
    lambda_end = brace_start
    for i, char in enumerate(func_content[brace_start:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                lambda_end = brace_start + i + 1
                break

    lambda_content = func_content[brace_start:lambda_end]

    # In the retry loop, tryLoadObject should use current_zookeeper, not the original zookeeper
    # Look for tryLoadObject calls in the lambda
    tryload_pattern = r'tryLoadObject\((\w+),'
    matches = re.findall(tryload_pattern, lambda_content)

    assert len(matches) > 0, "Should have tryLoadObject call inside retry loop"

    # All tryLoadObject calls should use current_zookeeper, not the parameter zookeeper
    for match in matches:
        assert match == 'current_zookeeper', \
            f"tryLoadObject should use 'current_zookeeper' inside retry loop, not '{match}'"


def test_code_compiles_syntax():
    """
    PASS-TO-PASS: Verify the C++ source file has valid syntax (no unmatched braces).
    """
    content = TARGET_FILE.read_text()

    # Basic brace balance check
    open_braces = content.count('{')
    close_braces = content.count('}')

    assert open_braces == close_braces, f"Unmatched braces: {open_braces} open, {close_braces} close"

    # Basic parenthesis balance check
    open_parens = content.count('(')
    close_parens = content.count(')')

    assert open_parens == close_parens, f"Unmatched parentheses: {open_parens} open, {close_parens} close"


def test_function_structure_intact():
    """
    PASS-TO-PASS: Verify the overall function structure is intact with key components.
    """
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Check for expected components
    required_components = [
        'LOG_DEBUG',
        'ZooKeeperRetriesControl',
        'retryLoop',
        'setAllObjects',
    ]

    for component in required_components:
        assert component in func_content, f"Missing required component: {component}"


def test_no_object_names_before_retry_loop():
    """
    FAIL-TO-PASS: Verify that object_names is NOT fetched before the retry loop.

    In the buggy version, Strings object_names = getObjectNamesAndSetWatch(...) was called
    before the retry loop, causing stale data on retry.
    """
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find the retry loop start
    retry_loop_pos = func_content.find('retries_ctl.retryLoop')
    if retry_loop_pos == -1:
        pytest.fail("Could not find retryLoop call")

    # Get content BEFORE the retry loop
    before_retry = func_content[:retry_loop_pos]

    # Should NOT have getObjectNamesAndSetWatch before the retry loop
    # (It should now be inside the retry loop)
    assert 'getObjectNamesAndSetWatch' not in before_retry, \
        "getObjectNamesAndSetWatch should NOT be called before the retry loop (it causes the bug)"


def test_repo_git_integrity():
    """
    PASS-TO-PASS: Verify the git repository is in a valid state.
    """
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # Should succeed and return (no output expected in clean state)
    assert r.returncode == 0, f"Git status failed: {r.stderr}"


def test_repo_file_integrity():
    """
    PASS-TO-PASS: Verify the target source file is valid UTF-8 and readable.
    """
    try:
        content = TARGET_FILE.read_text(encoding='utf-8')
        # Check for null bytes (indicates corruption)
        assert '\x00' not in content, "File contains null bytes (corruption)"
        # Check file is not empty
        assert len(content) > 0, "File is empty"
    except UnicodeDecodeError as e:
        pytest.fail(f"File is not valid UTF-8: {e}")
    except Exception as e:
        pytest.fail(f"Could not read target file: {e}")


def test_cmake_configuration_valid():
    """
    PASS-TO-PASS: Verify CMakeLists.txt can be parsed (syntax check).
    """
    cmake_file = REPO / "CMakeLists.txt"
    if not cmake_file.exists():
        pytest.skip("CMakeLists.txt not found")

    content = cmake_file.read_text()

    # Check for balanced parentheses in CMake commands
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"CMakeLists.txt has unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check for basic required sections
    required_sections = ['project', 'cmake_minimum_required']
    for section in required_sections:
        assert section.lower() in content.lower(), f"Missing required CMake section: {section}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
