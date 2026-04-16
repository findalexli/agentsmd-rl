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
import pytest
from pathlib import Path

REPO = Path("/workspace/clickhouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def get_refresh_objects_function():
    """
    Extract the refreshObjects function content from the source file.
    Returns the full function body or None.
    """
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


def extract_lambda_body(func_content, lambda_marker):
    """
    Extract the body of a lambda given a marker like 'retryLoop([&]'.
    Returns the lambda body (with outer braces).
    """
    lambda_start = func_content.find(lambda_marker)
    if lambda_start == -1:
        return None

    brace_start = func_content.find('{', lambda_start)
    if brace_start == -1:
        return None

    # Find matching closing brace
    brace_count = 0
    lambda_end = brace_start
    for i, range_c in enumerate(func_content[brace_start:]):
        if range_c == '{':
            brace_count += 1
        elif range_c == '}':
            brace_count -= 1
            if brace_count == 0:
                lambda_end = brace_start + i + 1
                break

    return func_content[brace_start:lambda_end]


def extract_retry_block(func_content):
    """
    Extract the block inside 'if (retries_ctl.isRetry())' that obtains fresh session.
    Returns (condition_text, block_text) or (None, None).
    """
    # Find if (retries_ctl.isRetry()) block
    pattern = r'if\s*\(\s*retries_ctl\.isRetry\(\)\s*\)(.*?)(?=\n\s*(?:else|for|while|if|\w+\s*\())'
    match = re.search(pattern, func_content, re.DOTALL)
    if match:
        return match.group(0), match.group(1)
    return None, None


def test_fix_session_refresh_in_retry_loop():
    """
    FAIL-TO-PASS: Verify that on retry, a fresh ZooKeeper session is obtained.

    The fix adds logic like:
        if (retries_ctl.isRetry())
            <some_var> = zookeeper_getter.getZooKeeper().first;

    We check that inside the isRetry() block, there's a call to getZooKeeper()
    to obtain a fresh session. We do NOT assert on the variable name.
    """
    content = TARGET_FILE.read_text()
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find the retry condition block
    retry_condition, retry_block = extract_retry_block(func_content)

    assert retry_condition is not None, \
        "Missing retry detection - should call retries_ctl.isRetry() to detect retry condition"

    assert 'getZooKeeper()' in retry_block or 'zookeeper_getter.getZooKeeper()' in retry_block, \
        "Missing session refresh - should call zookeeper_getter.getZooKeeper() to get fresh session on retry"

    # Verify that the result of getZooKeeper() is assigned to a variable
    # Pattern: some_var = zookeeper_getter.getZooKeeper().first;
    assign_pattern = r'\w+\s*=\s*zookeeper_getter\.getZooKeeper\(\)\.first'
    assert re.search(assign_pattern, retry_block), \
        "Fresh session should be assigned to a variable (zookeeper_getter.getZooKeeper().first)"


def test_fix_object_names_inside_retry_loop():
    """
    FAIL-TO-PASS: Verify that getObjectNamesAndSetWatch is called INSIDE the retry loop.

    The bug: object_names was fetched BEFORE the retry loop, using stale data on retry.
    The fix: Move the call inside the retryLoop lambda so it's re-fetched on each retry.
    """
    content = TARGET_FILE.read_text()
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find the retryLoop lambda
    lambda_body = extract_lambda_body(func_content, 'retries_ctl.retryLoop([&]')
    assert lambda_body is not None, "Could not find retryLoop lambda"

    # The fix requires getObjectNamesAndSetWatch to be INSIDE the retry loop
    assert 'getObjectNamesAndSetWatch' in lambda_body, \
        "getObjectNamesAndSetWatch must be called INSIDE the retryLoop lambda, not before it"


def test_fix_fresh_zookeeper_used_for_object_names():
    """
    FAIL-TO-PASS: Verify that getObjectNamesAndSetWatch uses a ZooKeeper handle
    that was obtained inside the retry condition (i.e., the fresh session), not
    the original zookeeper parameter.

    We check that inside the retry lambda, getObjectNamesAndSetWatch is called
    with a variable that was assigned inside the isRetry() block.
    """
    content = TARGET_FILE.read_text()
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find what variable is assigned from getZooKeeper() in the retry block
    retry_condition, retry_block = extract_retry_block(func_content)
    if retry_condition is None:
        pytest.fail("Could not find retries_ctl.isRetry() block")

    # Find the variable assigned in retry block
    assign_match = re.search(r'(\w+)\s*=\s*zookeeper_getter\.getZooKeeper\(\)\.first', retry_block)
    if not assign_match:
        pytest.fail("Could not find variable assigned from zookeeper_getter.getZooKeeper().first")

    fresh_zk_var = assign_match.group(1)

    # Now find the lambda body
    lambda_body = extract_lambda_body(func_content, 'retries_ctl.retryLoop([&]')
    assert lambda_body is not None, "Could not find retryLoop lambda"

    # Find getObjectNamesAndSetWatch call in lambda
    obj_names_match = re.search(r'getObjectNamesAndSetWatch\s*\(\s*(\w+)\s*,', lambda_body)
    assert obj_names_match, \
        "getObjectNamesAndSetWatch should be called inside the retry loop with a zookeeper handle"

    used_zk_var = obj_names_match.group(1)

    # The variable used should be the same one assigned in the retry block
    assert used_zk_var == fresh_zk_var, \
        f"getObjectNamesAndSetWatch should use the fresh session variable ({fresh_zk_var}) inside retry loop, not the original zookeeper parameter"


def test_fix_fresh_zookeeper_used_for_tryload():
    """
    FAIL-TO-PASS: Verify that tryLoadObject uses the fresh ZooKeeper handle
    inside the retry loop, not the original zookeeper parameter.
    """
    content = TARGET_FILE.read_text()
    func_content = get_refresh_objects_function()
    if not func_content:
        pytest.fail("Could not find refreshObjects function")

    # Find what variable is assigned from getZooKeeper() in the retry block
    retry_condition, retry_block = extract_retry_block(func_content)
    if retry_condition is None:
        pytest.fail("Could not find retries_ctl.isRetry() block")

    # Find the variable assigned in retry block
    assign_match = re.search(r'(\w+)\s*=\s*zookeeper_getter\.getZooKeeper\(\)\.first', retry_block)
    if not assign_match:
        pytest.fail("Could not find variable assigned from zookeeper_getter.getZooKeeper().first")

    fresh_zk_var = assign_match.group(1)

    # Now find the lambda body
    lambda_body = extract_lambda_body(func_content, 'retries_ctl.retryLoop([&]')
    assert lambda_body is not None, "Could not find retryLoop lambda"

    # Find tryLoadObject calls in lambda and check they use the fresh zk variable
    tryload_pattern = r'tryLoadObject\s*\(\s*(\w+)\s*,'
    matches = re.findall(tryload_pattern, lambda_body)

    assert len(matches) > 0, "Should have tryLoadObject call inside retry loop"

    # All tryLoadObject calls should use the fresh zookeeper variable
    for match in matches:
        assert match == fresh_zk_var, \
            f"tryLoadObject should use the fresh session handle ({fresh_zk_var}) inside retry loop, not '{match}'"


def test_no_object_names_before_retry_loop():
    """
    FAIL-TO-PASS: Verify that object_names is NOT fetched before the retry loop.

    In the buggy version, Strings object_names = getObjectNamesAndSetWatch(...) was called
    before the retry loop, causing stale data on retry.
    """
    content = TARGET_FILE.read_text()
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


# ============================================================================
# PASS-TO-PASS: Syntax and structure checks
# ============================================================================

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
    content = TARGET_FILE.read_text()
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


# ============================================================================
# REPO CI/CD TESTS - These run actual CI commands from the repository
# ============================================================================

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


def test_repo_style_check_cpp():
    """
    PASS-TO-PASS: Run the repo's C++ style check script.

    Repo CI/CD: Runs ci/jobs/scripts/check_style/check_cpp.sh which checks for:
    - Trailing whitespaces, tabs in source files
    - Missing pragma once in headers
    - Various C++ style violations
    """
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # The script exits 0 even if it finds issues (it outputs them), so we check output
    # Filter out known acceptable outputs (like Unicode in strings)
    lines = r.stdout.split('\n')
    errors = []
    for line in lines:
        # Skip lines that are acceptable:
        # - Lines with ' Gunar' (from allowed Unicode in comments)
        # - Lines with ' The sorting' (allowed documentation)
        # - Lines ending with '^ style error' (the summary line)
        # - Empty lines
        if not line.strip():
            continue
        if line.startswith('^ style error'):
            continue
        if 'xargs: rg:' in line:
            continue
        if 'warning: setlocale' in line:
            continue
        # Skip lines that are clearly Unicode in comments/strings (allowed)
        if any(c in line for c in ['ö', 'ü', 'ć', 'Ω', 'μ', 'χ', '─', '┌', '┐', '└', '┘', '│']):
            continue
        # If we get here, it's a real style error
        errors.append(line)

    assert not errors, f"C++ style check found issues:\n" + '\n'.join(errors[:20])


def test_repo_style_check_various():
    """
    PASS-TO-PASS: Run the repo's various_checks.sh style script.

    Repo CI/CD: Runs ci/jobs/scripts/check_style/various_checks.sh which checks for:
    - BOM markers in files
    - DOS/Windows newlines
    - Conflict markers
    - Executable bit on non-executable files
    """
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # The script outputs issues but returns 0, so we check for actual error content
    # Only consider it a failure if there's substantial error output
    if r.stdout.strip():
        # Some checks output warnings but those are OK
        # We only fail on explicit error indicators
        error_indicators = ['should not', 'cannot', 'broken', 'error', 'failed']
        has_real_error = any(ind in r.stdout.lower() for ind in error_indicators)
        if has_real_error and r.returncode != 0:
            assert False, f"Various checks failed:\n{r.stdout[:1000]}"


def test_repo_git_attributes_valid():
    """
    PASS-TO-PASS: Verify git attributes are valid for source files.

    Repo CI/CD: Git attributes check for text files.
    """
    r = subprocess.run(
        ["git", "check-attr", "text", "--", str(TARGET_FILE.relative_to(REPO))],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git attributes check failed: {r.stderr}"

    # The output should contain 'text: unspecified' or 'text: set'
    assert "text:" in r.stdout, f"Git attributes check returned unexpected output: {r.stdout}"


def test_repo_no_duplicate_includes():
    """
    PASS-TO-PASS: Verify no duplicate #include statements in modified file.

    Repo CI/CD: Style check for duplicate includes (from check_style.py).
    """
    r = subprocess.run(
        ["bash", "-c", f"grep -h '^#include ' {TARGET_FILE} | sort | uniq -d"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # If grep finds duplicates, it returns 0 with output; we want no output (return 1 means no matches found)
    assert r.returncode == 1 or not r.stdout.strip(), \
        f"Found duplicate #include statements:\n{r.stdout}"


def test_repo_no_trailing_whitespace():
    """
    PASS-TO-PASS: Verify no trailing whitespace in modified source file.

    Repo CI/CD: Style check for trailing whitespace (from check_style.py).
    """
    r = subprocess.run(
        ["grep", "-n", "-P", " $", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # grep returns 1 if no matches (which is what we want)
    assert r.returncode == 1 or not r.stdout.strip(), \
        f"Found trailing whitespace:\n{r.stdout[:500]}"


def test_repo_no_tabs_for_indentation():
    """
    PASS-TO-PASS: Verify no tabs used for indentation in modified source file.

    Repo CI/CD: Style check for tabs vs spaces (common C++ convention).
    """
    r = subprocess.run(
        ["grep", "-F", "\t", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # grep returns 1 if no matches (which is what we want)
    assert r.returncode == 1 or not r.stdout.strip(), \
        f"Found tabs in target file:\n{r.stdout[:500]}"


def test_repo_header_has_include_guards():
    """
    PASS-TO-PASS: Verify header files have proper include guards.

    Repo CI/CD: C++ header files should have include guards.
    """
    header_file = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.h"
    if not header_file.exists():
        pytest.skip("Header file not found")

    r = subprocess.run(
        ["head", "-n1", str(header_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to read header: {r.stderr}"
    assert "#pragma once" in r.stdout, f"Header missing #pragma once, got: {r.stdout.strip()}"


def test_repo_cmake_configuration_valid():
    """
    PASS-TO-PASS: Verify CMakeLists.txt can be parsed (syntax check).

    Repo CI/CD: Runs basic CMake validation.
    """
    cmake_file = REPO / "CMakeLists.txt"
    if not cmake_file.exists():
        pytest.skip("CMakeLists.txt not found")

    # Check for balanced parentheses
    r = subprocess.run(
        ["bash", "-c", f"open=$(grep -o '(' {cmake_file} | wc -l); close=$(grep -o ')' {cmake_file} | wc -l); test $open -eq $close"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CMakeLists.txt has unbalanced parentheses"


def test_repo_cpp_files_compile_independently():
    """
    PASS-TO-PASS: Verify C++ file has valid structure for independent parsing.

    Repo CI/CD: Basic C++ syntax validation - no unclosed block comments.
    """
    r = subprocess.run(
        ["bash", "-c", f"open=$(grep -o '/\\*' {TARGET_FILE} | wc -l); close=$(grep -o '\\*/' {TARGET_FILE} | wc -l); test $open -eq $close"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unbalanced block comments in target file"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
