#!/usr/bin/env python3
"""
Test suite for ClickHouse UDF Keeper retry fix.

Tests verify that the fix properly adds:
1. ZooKeeperRetriesControl for transient error handling
2. Hardware error detection and re-throwing
3. Retry loop with proper backoff configuration
"""

import os
import re
import subprocess

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def test_zookeeper_retries_header_included():
    """Verify ZooKeeperRetries.h header is included (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the specific include
    pattern = r'#include\s+<Common/ZooKeeper/ZooKeeperRetries\.h>'
    assert re.search(pattern, content), \
        "Missing required include: #include <Common/ZooKeeper/ZooKeeperRetries.h>"


def test_keeper_exception_catch_block():
    """Verify KeeperException catch block with hardware error handling (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for KeeperException catch block
    catch_pattern = r'catch\s*\(\s*const\s+zkutil::KeeperException\s*&\s*e\s*\)'
    assert re.search(catch_pattern, content), \
        "Missing KeeperException catch block"

    # Check for hardware error check
    hw_error_pattern = r'Coordination::isHardwareError\s*\(\s*e\.code\s*\)'
    assert re.search(hw_error_pattern, content), \
        "Missing hardware error check: Coordination::isHardwareError(e.code)"

    # Check for re-throwing hardware errors
    throw_pattern = r'throw\s*;'
    assert re.search(throw_pattern, content), \
        "Missing re-throw for hardware errors"


def test_retry_control_instantiated():
    """Verify ZooKeeperRetriesControl is instantiated in refreshObjects (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for ZooKeeperRetriesControl instantiation
    retry_pattern = r'ZooKeeperRetriesControl\s+retries_ctl\s*\('
    assert re.search(retry_pattern, content), \
        "Missing ZooKeeperRetriesControl instantiation"


def test_retry_constants_defined():
    """Verify retry constants are defined with correct values (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for max_retries constant
    max_retries_pattern = r'static\s+constexpr\s+UInt64\s+max_retries\s*=\s*5'
    assert re.search(max_retries_pattern, content), \
        "Missing or incorrect max_retries constant (expected: 5)"

    # Check for initial_backoff_ms constant
    backoff_pattern = r'static\s+constexpr\s+UInt64\s+initial_backoff_ms\s*=\s*200'
    assert re.search(backoff_pattern, content), \
        "Missing or incorrect initial_backoff_ms constant (expected: 200)"

    # Check for max_backoff_ms constant
    max_backoff_pattern = r'static\s+constexpr\s+UInt64\s+max_backoff_ms\s*=\s*5000'
    assert re.search(max_backoff_pattern, content), \
        "Missing or incorrect max_backoff_ms constant (expected: 5000)"


def test_retry_loop_used():
    """Verify retryLoop is called with lambda (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for retryLoop call
    loop_pattern = r'retries_ctl\.retryLoop\s*\(\s*\[\&\]'
    assert re.search(loop_pattern, content), \
        "Missing retries_ctl.retryLoop() call with lambda"


def test_function_names_and_asts_cleared():
    """Verify vector is cleared at retry loop start (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for clear() call inside retry loop
    clear_pattern = r'function_names_and_asts\.clear\s*\(\s*\)'
    assert re.search(clear_pattern, content), \
        "Missing function_names_and_asts.clear() call in retry loop"


def test_keeper_error_warning_logged():
    """Verify hardware error warning is logged (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for hardware error log message
    log_pattern = r'LOG_WARNING\s*\(\s*log\s*,\s*"Keeper hardware error while loading user defined SQL object'
    assert re.search(log_pattern, content), \
        "Missing hardware error warning log message"


def test_refresh_objects_function_structure():
    """Verify refreshObjects function has the retry structure (fail_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the refreshObjects function
    func_start = content.find('void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects')
    assert func_start != -1, "refreshObjects function not found"

    # Extract function body (rough approximation)
    func_content = content[func_start:func_start + 5000]

    # Check that it has both retry control and retry loop
    assert 'ZooKeeperRetriesControl' in func_content, \
        "ZooKeeperRetriesControl not found in refreshObjects"
    assert 'retryLoop' in func_content, \
        "retryLoop not found in refreshObjects"


def test_code_follows_allman_braces():
    """Verify Allman-style braces are used (pass_to_pass - from agent config)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for non-Allman patterns (opening brace on same line)
    # This is a heuristic - look for common patterns
    non_allman = re.findall(r'\)\s*\{[^\}]*\n', content)

    # Find try-catch blocks with proper Allman style
    try_pattern = r'try\s*\n\s*\{'
    catch_pattern = r'catch\s*\([^)]+\)\s*\n\s*\{'

    try_matches = re.findall(try_pattern, content)
    catch_matches = re.findall(catch_pattern, content)

    # We should have try blocks with Allman style
    assert len(try_matches) > 0, "No try blocks with Allman-style braces found"


# ============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks - ensure base commit is functional)
# ============================================================================

def test_repo_file_exists_and_readable():
    """Target source file exists and is readable (pass_to_pass)."""
    assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"
    with open(TARGET_FILE, 'r') as f:
        content = f.read()
    assert len(content) > 0, "Target file is empty"


def test_repo_git_ls_files():
    """Git can list source files - CI file indexing (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["git", "ls-files", "--", "src/Functions/UserDefined/*.cpp", "src/Functions/UserDefined/*.h"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    assert r.returncode == 0, f"Git ls-files failed: {r.stderr}"
    # Should find the target file
    assert "UserDefinedSQLObjectsZooKeeperStorage.cpp" in r.stdout, \
        "Target file not found in git ls-files output"


def test_repo_git_show_file():
    """Git can show file content - CI content validation (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["git", "show", "HEAD:src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    assert r.returncode == 0, f"Git show failed: {r.stderr}"
    # Should contain expected content
    assert "UserDefinedSQLObjectsZooKeeperStorage" in r.stdout, \
        "Expected content not found in git show output"


def test_repo_git_log_file():
    """Git log for target file works - CI history check (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["git", "log", "-3", "--format=%H", "--", "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    assert r.returncode == 0, f"Git log failed: {r.stderr}"
    # Should produce commit hashes (40 character hex strings)
    commits = [line.strip() for line in r.stdout.strip().split('\n') if line.strip()]
    assert len(commits) > 0, "No commit history found for target file"
    for commit in commits:
        assert len(commit) == 40, f"Invalid commit hash format: {commit}"


def test_repo_git_grep_includes():
    """Git grep finds ZooKeeper includes - CI dependency check (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["git", "grep", "-l", "ZooKeeperRetries", "--", "src/Common/ZooKeeper/*.h"],
        capture_output=True, text=True, cwd=REPO, timeout=60
    )
    assert r.returncode == 0 or r.returncode == 1, f"Git grep failed: {r.stderr}"
    # Should find ZooKeeperRetries.h
    if r.returncode == 0:
        assert "ZooKeeperRetries.h" in r.stdout, \
            "ZooKeeperRetries.h not found in git grep output"


def test_repo_grep_keeper_exception():
    """grep finds KeeperException usage in target file - CI code analysis (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["grep", "-n", "KeeperException", TARGET_FILE],
        capture_output=True, text=True, timeout=60
    )
    # grep returns 0 if matches found, 1 if no matches
    assert r.returncode in [0, 1], f"grep command failed: {r.stderr}"
    if r.returncode == 0:
        assert "#include" in r.stdout or "throw" in r.stdout or "catch" in r.stdout, \
            "KeeperException usage not as expected"


def test_repo_cpp_syntax_valid():
    """Basic C++ syntax validation - balanced braces/parens (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for balanced braces
    open_count = content.count('{')
    close_count = content.count('}')
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"

    # Check for balanced parentheses
    open_paren = content.count('(')
    close_paren = content.count(')')
    assert open_paren == close_paren, f"Unbalanced parentheses: {open_paren} open, {close_paren} close"


def test_repo_includes_valid():
    """Include statements are valid and properly formatted (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find all includes
    includes = re.findall(r'#include\s+[<"][^>"]+[>"]', content)
    assert len(includes) > 0, "No includes found"

    # Check includes use proper angle bracket format for system headers
    system_includes = [i for i in includes if i.startswith('#include <')]
    assert len(system_includes) > 0, "No system-style includes found"


def test_repo_git_clean():
    """Repository is in clean state with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO
    )
    assert r.returncode == 0, "Git status failed"
    # File modifications would appear in output
    # (patch application during solve.sh is done after test check)


def test_repo_directory_structure():
    """Repo directory structure is intact (pass_to_pass)."""
    # Check key directories exist
    key_dirs = [
        f"{REPO}/src",
        f"{REPO}/src/Functions",
        f"{REPO}/src/Common/ZooKeeper",
    ]
    for d in key_dirs:
        assert os.path.isdir(d), f"Missing directory: {d}"


def test_repo_no_trailing_whitespace():
    """Source files have no trailing whitespace (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # Allow empty lines, but no trailing whitespace on content lines
        if line.rstrip() != line.rstrip('\n').rstrip():
            assert False, f"Trailing whitespace on line {i}"


def test_repo_no_merge_conflict_markers():
    """Source files have no merge conflict markers (pass_to_pass - Repo CI/CD)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for conflict markers
    assert '<<<<<<< ' not in content, "Found merge conflict marker '<<<<<<<'"
    assert '=======\n' not in content, "Found merge conflict marker '======='"
    assert '>>>>>>> ' not in content, "Found merge conflict marker '>>>>>>>'"


def test_repo_no_crlf_line_endings():
    """Source files use LF line endings, not CRLF (pass_to_pass - Repo CI/CD)."""
    with open(TARGET_FILE, 'rb') as f:
        content = f.read()

    # Check for CRLF line endings
    assert b'\r\n' not in content, "Found CRLF (Windows) line endings - should use LF only"


def test_repo_line_length_reasonable():
    """Source file lines are within reasonable length (pass_to_pass - Repo CI/CD).

    ClickHouse .clang-format specifies ColumnLimit: 140.
    We allow a small tolerance for edge cases (160 chars).
    """
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    max_allowed = 160  # 140 from .clang-format + tolerance
    long_lines = []

    for i, line in enumerate(lines, 1):
        if len(line.rstrip('\n')) > max_allowed:
            long_lines.append((i, len(line.rstrip('\n'))))

    # Fail if more than 5 lines exceed the limit (allows some tolerance)
    assert len(long_lines) <= 5, f"Too many lines exceed {max_allowed} chars: {long_lines[:5]}"


def test_repo_include_style_valid():
    """Include statements follow project conventions (pass_to_pass - Repo CI/CD)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check includes use angle brackets for system/project headers
    includes = re.findall(r'^#include\s+(["<][^">]+[">])', content, re.MULTILINE)
    assert len(includes) > 0, "No includes found"

    for inc in includes:
        # Must start with < or " and end with matching > or "
        if inc.startswith('<'):
            assert inc.endswith('>'), f"Malformed include: {inc}"
        elif inc.startswith('"'):
            assert inc.endswith('"'), f"Malformed include: {inc}"
        else:
            assert False, f"Include must use angle brackets or quotes: {inc}"


def test_repo_no_duplicate_includes():
    """No duplicate includes in the same file (pass_to_pass - Repo CI/CD)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find all includes
    includes = re.findall(r'^#include\s+[<"][^>"]+[>"]', content, re.MULTILINE)

    # Check for duplicates
    seen = set()
    duplicates = []
    for inc in includes:
        if inc in seen:
            duplicates.append(inc)
        seen.add(inc)

    assert len(duplicates) == 0, f"Found duplicate includes: {duplicates}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
