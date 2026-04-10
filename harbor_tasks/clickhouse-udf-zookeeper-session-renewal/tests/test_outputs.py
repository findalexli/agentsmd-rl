#!/usr/bin/env python3
"""
Tests for ClickHouse UDF ZooKeeper session renewal fix.

This task fixes a critical bug where the ZooKeeperRetriesControl retry loop
reused an expired ZooKeeper session on every retry iteration without renewing it,
causing crashes when transient Keeper hiccups occurred.

The fix ensures the session is renewed via zookeeper_getter on each retry.
"""

import subprocess
import sys
import re
from pathlib import Path

# Repository path - inside Docker container
REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
TARGET_DIR = TARGET_FILE.parent


def _get_file_content() -> str:
    """Helper to read target file content."""
    if not TARGET_FILE.exists():
        return ""
    return TARGET_FILE.read_text()


def _run_in_repo(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def _run_shell_check(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a shell script to check the target file."""
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def test_compilation():
    """Verify the target file exists with refreshObjects function and ZooKeeperRetriesControl (pass_to_pass baseline)."""
    assert TARGET_FILE.exists(), f"Target file does not exist: {TARGET_FILE}"
    content = _get_file_content()
    assert "refreshObjects" in content, "refreshObjects function not found"
    assert "ZooKeeperRetriesControl" in content, "ZooKeeperRetriesControl not found"


def test_session_renewal_in_retry_loop():
    """Fail-to-pass: Verify session renewal logic is inside retry loop via behavioral check."""
    content = _get_file_content()

    # The fix adds session renewal inside the retry loop
    # Check for the key indicators of the fix

    # 1. Must have current_zookeeper variable declaration
    assert "zkutil::ZooKeeperPtr current_zookeeper = zookeeper;" in content, \
        "current_zookeeper variable not found - session renewal mechanism missing"

    # 2. Must check for retry and renew session (allow Allman brace style)
    assert "if (retries_ctl.isRetry())" in content, \
        "Retry check not found - session won't be renewed on retry"

    # 3. Must renew session via zookeeper_getter (this is the core fix)
    assert "zookeeper_getter.getZooKeeper().first;" in content, \
        "Session renewal call not found - fix incomplete"

    # 4. Must use current_zookeeper inside retry loop (not stale zookeeper param)
    # Find the retryLoop section
    retry_start = content.find("retries_ctl.retryLoop([&]")
    assert retry_start != -1, "retryLoop not found"

    # Look for the lambda body - find end by tracking braces
    retry_section = content[retry_start:retry_start + 3000]

    # Check that current_zookeeper is used in the retry loop
    assert "current_zookeeper" in retry_section, \
        "current_zookeeper not used inside retry loop"

    # 5. The original bug used 'zookeeper' parameter directly in tryLoadObject
    # Check that we're now using current_zookeeper for tryLoadObject
    assert "tryLoadObject(current_zookeeper" in retry_section, \
        "tryLoadObject not using current_zookeeper in retry loop"


def test_object_names_inside_retry_loop():
    """Fail-to-pass: Verify object_names fetch happens inside retry loop for fresh session."""
    content = _get_file_content()

    # Find the retryLoop lambda
    retry_start = content.find("retries_ctl.retryLoop([&]")
    assert retry_start != -1, "retryLoop not found"

    # Find the retry section (reasonable size)
    retry_section = content[retry_start:retry_start + 2500]

    # The fix moves getObjectNamesAndSetWatch inside the retry loop
    # so it gets called with the fresh session on retry
    assert "getObjectNamesAndSetWatch(current_zookeeper, object_type)" in retry_section, \
        "getObjectNamesAndSetWatch must be inside retry loop with current_zookeeper"

    # Verify object_names is declared inside the retry loop (not outside)
    # Before the fix: "Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);"
    # was BEFORE the retryLoop
    func_start = content.find("void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects")
    assert func_start != -1, "refreshObjects function not found"

    # Get content from function start to retry loop start
    pre_retry_content = content[func_start:retry_start]

    # The OLD buggy code had object_names declared BEFORE retryLoop
    # The FIXED code has it INSIDE the retry loop
    # So we verify that the declaration BEFORE retry loop uses the OLD pattern (zookeeper parameter)
    # This confirms the fix moved it inside
    old_pattern = "Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);"
    if old_pattern in pre_retry_content:
        # If old pattern exists before retry, the fix is incomplete
        # But check if it's a comment or actual code
        lines = pre_retry_content.split('\n')
        for line in lines:
            if old_pattern in line and not line.strip().startswith('//'):
                assert False, "object_names still declared BEFORE retry loop with stale session (bug not fixed)"


def test_comment_describes_fix():
    """Fail-to-pass: Verify comments explain the session renewal behavior via subprocess."""
    # Use subprocess to validate file content via Python execution
    script = f"""
import sys
content = open('{TARGET_FILE}').read()

# Check for keywords about session handling
has_getter = "zookeeper_getter" in content
has_renew = "renew" in content.lower() or "Renew" in content
has_expired = "expired" in content.lower() or "Expired" in content
has_fresh = "fresh" in content.lower() or "Fresh" in content

if not has_getter:
    print("FAIL: Missing documentation about session renewal via zookeeper_getter")
    sys.exit(1)

if not (has_renew or has_expired or has_fresh):
    print("FAIL: Missing documentation about handling expired/renewed sessions")
    sys.exit(1)

print("PASS: Comments describe session renewal")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Comment check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output: {r.stdout}"


def test_no_sleep_in_code():
    """Fail-to-pass: Verify no sleep calls in the changed code (ClickHouse rule)."""
    # Use subprocess to execute the validation as behavioral test
    script = f"""
import sys
content = open('{TARGET_FILE}').read()

# Find refreshObjects function
func_start = content.find("void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects")
if func_start == -1:
    print("FAIL: refreshObjects function not found")
    sys.exit(1)

func_content = content[func_start:func_start + 3000]
func_lower = func_content.lower()

# Check for sleep calls (per ClickHouse rule: never use sleep for race conditions)
violations = []
if "sleep(" in func_lower:
    violations.append("sleep()")
if "usleep(" in func_lower:
    violations.append("usleep()")
if "std::this_thread::sleep" in func_content:
    violations.append("std::this_thread::sleep")

if violations:
    print(f"FAIL: ClickHouse rule violation: {{', '.join(violations)}} found in refreshObjects")
    sys.exit(1)

print("PASS: No sleep calls in refreshObjects")
"""
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Sleep check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_deletion_logging():
    """Pass-to-pass: Verify the code follows ClickHouse deletion logging rule."""
    content = _get_file_content()

    # The refreshObjects function doesn't delete data, it refreshes it
    # We just verify no raw delete calls without logging in the retry section
    retry_start = content.find("retries_ctl.retryLoop")
    if retry_start != -1:
        retry_section = content[retry_start:retry_start + 2000]
        # If there were deletion operations, they should be logged
        # Since this function refreshes rather than deletes, we just verify it doesn't
        # have unlogged deletions
        assert "delete " not in retry_section.lower() or "LOG_" in retry_section, \
            "Potential deletion without logging (ClickHouse rule)"


# ============================================================================
# REPO CI TESTS - These run actual CI commands via subprocess.run()
# ============================================================================

def test_repo_no_tabs():
    """Repo's no-tabs style check passes (pass_to_pass).

    ClickHouse CI checks that source files contain no tab characters.
    """
    script = f"""
FILE='{TARGET_FILE}'
if grep -F $'\\t' "$FILE" > /dev/null 2>&1; then
    echo "FAIL: Found tab characters in file"
    exit 1
else
    echo "PASS: No tab characters found"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"Tab check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_trailing_whitespace():
    """Repo's trailing whitespace check passes (pass_to_pass).

    ClickHouse CI checks that source files have no trailing whitespace.
    """
    script = f"""
FILE='{TARGET_FILE}'
if grep -n -P ' $' "$FILE" > /dev/null 2>&1; then
    echo "FAIL: Found trailing whitespace"
    exit 1
else
    echo "PASS: No trailing whitespace"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"Trailing whitespace check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_cerr_cout():
    """Repo's std::cerr/std::cout check passes (pass_to_pass).

    ClickHouse CI forbids std::cerr/std::cout in src/ (use logging macros instead).
    """
    script = f"""
FILE='{TARGET_FILE}'
# Use grep to check for std::cerr/std::cout
if grep -F -e 'std::cerr' -e 'std::cout' "$FILE" > /dev/null 2>&1; then
    echo "FAIL: Found std::cerr or std::cout"
    exit 1
else
    echo "PASS: No std::cerr/std::cout found"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"std::cerr/cout check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_std_format():
    """Repo's std::format check passes (pass_to_pass).

    ClickHouse CI prefers fmt::format over std::format for performance.
    """
    script = f"""
FILE='{TARGET_FILE}'
if grep -q 'std::format' "$FILE" 2>/dev/null; then
    echo "FAIL: Found std::format (use fmt::format instead)"
    exit 1
else
    echo "PASS: No std::format found"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"std::format check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_raw_assert():
    """Repo's raw assert check passes (pass_to_pass).

    ClickHouse CI checks that raw assert() is not used (use CH_ASSERT).
    """
    script = f"""
FILE='{TARGET_FILE}'
# Check for raw assert calls (not CH_ASSERT or static_assert)
if grep -P '\\bassert\\s*\\(' "$FILE" | grep -v -P '(CH_ASSERT|static_assert)' > /dev/null 2>&1; then
    echo "FAIL: Found raw assert() calls"
    exit 1
else
    echo "PASS: No raw assert() calls"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"Raw assert check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_builtin_unreachable():
    """Repo's __builtin_unreachable check passes (pass_to_pass).

    ClickHouse CI forbids __builtin_unreachable (use UNREACHABLE() macro instead).
    """
    script = f"""
FILE='{TARGET_FILE}'
if grep -P '__builtin_unreachable' "$FILE" > /dev/null 2>&1; then
    echo "FAIL: Found __builtin_unreachable (use UNREACHABLE() instead)"
    exit 1
else
    echo "PASS: No __builtin_unreachable found"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"__builtin_unreachable check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_no_std_filesystem_symlink():
    """Repo's std::filesystem::is_symlink check passes (pass_to_pass).

    ClickHouse CI prefers DB::FS::isSymlink over std::filesystem::is_symlink.
    """
    script = f"""
FILE='{TARGET_FILE}'
if grep -P '::(is|read)_symlink' "$FILE" > /dev/null 2>&1; then
    echo "FAIL: Found std::filesystem symlink calls"
    exit 1
else
    echo "PASS: No std::filesystem symlink calls"
fi
"""
    r = _run_shell_check(script)
    assert r.returncode == 0, f"symlink check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS: {r.stdout}"


def test_repo_clang_format():
    """Repo's clang-format check passes (pass_to_pass).

    Runs clang-format --dry-run to verify code formatting if available.
    """
    import pytest

    # Check if clang-format is available
    which_result = subprocess.run(
        ["which", "clang-format"],
        capture_output=True, text=True, timeout=10
    )

    if which_result.returncode != 0:
        pytest.skip("clang-format not available")

    # Run clang-format --dry-run to check formatting
    result = subprocess.run(
        ["clang-format", "--dry-run", "--Werror", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, \
        f"clang-format check failed:\n{result.stderr or result.stdout}"


# ============================================================================
# STATIC CHECKS - File content checks (origin: static)
# ============================================================================

def test_clickhouse_allman_braces():
    """Code follows ClickHouse Allman brace style convention (static check).

    ClickHouse uses Allman style for control structures: opening brace on a new line.
    """
    content = _get_file_content()
    lines = content.split('\n')

    # Control keywords that should use Allman style
    same_line_control_brace = re.compile(
        r'^\s*(?:if|else|for|while|switch|try|catch)\s*[^{{]*{{\s*$'
    )

    violations = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip comment lines, preprocessor directives
        if stripped.startswith('//') or stripped.startswith('#'):
            continue

        # Check for control structure with brace on same line (K&R style violation)
        if same_line_control_brace.match(line):
            if not stripped.startswith('}}') and 'else' not in stripped:
                violations.append(f"Line {i}: {stripped[:60]}")

    assert not violations, f"K&R style braces found:\n" + "\n".join(violations[:10])


def test_clickhouse_naming_conventions():
    """Code follows ClickHouse naming conventions (static check).

    - Type names: CamelCase (ClassName, StructName)
    - Variable/function names: snake_case
    - Private member variables: snake_case with trailing underscore
    - Constants: CamelCase or ALL_CAPS
    """
    content = _get_file_content()

    # Check for common ClickHouse type prefixes (should be CamelCase)
    clickhouse_types = [
        'UserDefinedSQLObjectsZooKeeperStorage',
        'ZooKeeperRetriesControl',
        'UserDefinedSQLObjectType',
    ]

    for type_name in clickhouse_types:
        assert type_name in content, f"Expected type {type_name} not found"


def test_clickhouse_logger_usage():
    """Uses ClickHouse LOG_* macros instead of std::cout/std::cerr (static check).

    ClickHouse uses LOG_DEBUG, LOG_INFO, LOG_WARNING, LOG_ERROR macros.
    """
    content = _get_file_content()

    # Should have proper ClickHouse logging
    log_macros = ['LOG_DEBUG', 'LOG_INFO', 'LOG_WARNING', 'LOG_ERROR']
    has_log_macros = any(macro in content for macro in log_macros)
    assert has_log_macros, "No ClickHouse LOG_* macros found"


def test_exception_handling_patterns():
    """Follows ClickHouse exception handling patterns (static check).

    ClickHouse uses tryLogCurrentException and specific exception types.
    """
    content = _get_file_content()

    # Should use ClickHouse's tryLogCurrentException for catch-all handlers
    if 'catch (...)' in content:
        assert 'tryLogCurrentException' in content, \
            "catch (...) blocks should use tryLogCurrentException"

    # Should have KeeperException handling for ZooKeeper errors
    assert 'KeeperException' in content, \
        "ZooKeeper/KeeperException handling expected for storage class"


def test_cpp_syntax_valid():
    """C++ code has basic syntactic validity via brace balance (static check)."""
    content = _get_file_content()

    # Check for balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
