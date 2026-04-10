"""
Tests for ClickHouse PR #102171: Fix crash caused by stale ZooKeeper session in UDF retry loop.

This PR fixes a bug where the ZooKeeper session was not renewed during retries in the
refreshObjects function, potentially causing crashes with stale session handles.
"""

import subprocess
import re
import os
import sys

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"
FILE_PATH = os.path.join(REPO, TARGET_FILE)


def get_file_content():
    """Read the target file content."""
    with open(FILE_PATH, 'r') as f:
        return f.read()


def test_session_renewal_logic_exists():
    """F2P: Check that session renewal logic exists in retry loop.

    The fix adds: if (retries_ctl.isRetry()) current_zookeeper = zookeeper_getter.getZooKeeper().first
    """
    content = get_file_content()

    # Check for the session renewal logic inside the retry loop
    assert "if (retries_ctl.isRetry())" in content, \
        "Missing session renewal check: if (retries_ctl.isRetry())"

    assert "current_zookeeper = zookeeper_getter.getZooKeeper().first" in content, \
        "Missing session renewal assignment: current_zookeeper = zookeeper_getter.getZooKeeper().first"

    # Check for the comment explaining the renewal
    assert "Renew the session on retry" in content, \
        "Missing comment explaining session renewal"


def test_object_names_moved_into_retry_loop():
    """F2P: Verify object_names declaration moved inside retryLoop.

    Before: Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type); was BEFORE retryLoop
    After: It should be INSIDE the retryLoop lambda so it's re-fetched on each retry
    """
    content = get_file_content()

    # Find the refreshObjects function
    func_match = re.search(
        r'void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects.*?\{',
        content,
        re.DOTALL
    )
    assert func_match, "Could not find refreshObjects function"

    # Get the function body (rough approximation - look until next function or end of file at similar indentation)
    func_start = func_match.end()

    # Find the retryLoop call
    retry_loop_match = re.search(r'retries_ctl\.retryLoop\(\[&\]', content[func_start:])
    assert retry_loop_match, "Could not find retryLoop call"

    retry_loop_start = func_start + retry_loop_match.start()

    # Find the opening brace of the retryLoop lambda
    lambda_start = content.find('{', retry_loop_start)
    assert lambda_start != -1, "Could not find retryLoop lambda opening brace"

    # Find the closing brace of the retryLoop lambda (next '}' at similar indentation after the for loop)
    # Look for the pattern inside the lambda: Strings object_names = getObjectNamesAndSetWatch
    lambda_content = content[lambda_start:lambda_start + 2000]

    assert "Strings object_names = getObjectNamesAndSetWatch(current_zookeeper" in lambda_content, \
        "object_names should be declared inside retryLoop with current_zookeeper parameter"

    # Verify object_names is NOT declared before retryLoop (the old bug)
    content_before_retry = content[func_start:retry_loop_start]

    # Should NOT have object_names declaration before retryLoop
    before_decl_match = re.search(r'Strings\s+object_names\s*=\s*getObjectNamesAndSetWatch', content_before_retry)
    assert before_decl_match is None, \
        "BUG: object_names should NOT be declared before retryLoop (it was moved inside)"


def test_current_zookeeper_variable_exists():
    """F2P: Check that current_zookeeper variable was added."""
    content = get_file_content()

    # Check for the new variable declaration
    assert "zkutil::ZooKeeperPtr current_zookeeper = zookeeper;" in content, \
        "Missing current_zookeeper variable declaration"


def test_tryLoadObject_uses_current_zookeeper():
    """F2P: Verify tryLoadObject uses current_zookeeper, not the stale parameter."""
    content = get_file_content()

    # The fix changes: tryLoadObject(zookeeper, ...) -> tryLoadObject(current_zookeeper, ...)
    # inside the retryLoop lambda

    # Find the retryLoop section
    retry_match = re.search(r'retries_ctl\.retryLoop\(\[&\]\s*\{', content)
    assert retry_match, "Could not find retryLoop lambda"

    retry_start = retry_match.start()

    # Get content from retryLoop start to find the tryLoadObject call
    retry_section = content[retry_start:retry_start + 1500]

    # Check that tryLoadObject uses current_zookeeper inside the retry loop
    assert "tryLoadObject(current_zookeeper, UserDefinedSQLObjectType::Function" in retry_section, \
        "tryLoadObject should use current_zookeeper inside retryLoop"

    # Make sure it's not using the stale 'zookeeper' parameter in the loop
    # (there might still be 'zookeeper' in comments or the function signature, but not in the call)
    lines = retry_section.split('\n')
    for i, line in enumerate(lines):
        if 'tryLoadObject' in line and 'current_zookeeper' not in line:
            # If tryLoadObject is called without current_zookeeper inside retryLoop, it's a bug
            if 'zookeeper' in line and 'zookeeper_getter' not in line:
                # Check if it's the parameter 'zookeeper' not something else
                if re.search(r'tryLoadObject\(\s*zookeeper\s*,', line):
                    assert False, f"Line {i}: tryLoadObject still uses stale 'zookeeper' parameter: {line}"


def test_cpp_syntax_valid():
    """F2P: Verify the C++ code has valid syntax by attempting to compile just this file.

    This catches any syntax errors introduced by the patch.
    """
    # Use clang to check syntax only (-fsyntax-only)
    # We need to set up include paths properly
    include_paths = [
        "-I.",
        "-Isrc",
        "-Ibase",
        "-Icontrib",
    ]

    # Run clang syntax check
    cmd = [
        "clang-16",
        "-fsyntax-only",
        "-std=c++20",
        "-x", "c++",
    ] + include_paths + [
        FILE_PATH
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # The syntax check may have errors due to missing dependencies, but shouldn't have
    # parse errors from our changes
    stderr = result.stderr.lower()

    # Check for syntax-related errors (not missing header errors)
    syntax_errors = [
        "expected",
        "undeclared identifier",
        "syntax error",
        "invalid",
        "redefinition",
    ]

    for error in syntax_errors:
        if error in stderr and "file not found" not in stderr:
            # Only fail if we see syntax errors unrelated to missing headers
            lines_with_error = [l for l in result.stderr.split('\n') if error in l.lower()]
            if lines_with_error:
                # Check that these errors are in our target file
                target_errors = [l for l in lines_with_error if TARGET_FILE in l]
                if target_errors:
                    assert False, f"Syntax error in {TARGET_FILE}: {target_errors[0]}"

    # If we get here, syntax check passed (or only has missing header issues which are OK)


def test_comment_explains_session_refresh():
    """F2P: Verify updated comment explains session refresh behavior."""
    content = get_file_content()

    # The old comment mentioned "5-second sleep in processWatchQueue" which is removed
    # The new comment should mention session renewal

    # Check for the updated comment
    assert "re-fetch the object list" in content, \
        "Missing comment about re-fetching object list on new session"

    assert "watches are set on the live session" in content, \
        "Missing comment about watches being set on live session"

    # The old comment about 5-second sleep should be gone
    old_comment = "5-second sleep in processWatchQueue"
    assert old_comment not in content, \
        f"Old comment '{old_comment}' should be removed"


def test_no_sleep_for_race_conditions():
    """P2P: Check that no sleep calls were added (per agent config rules).

    The CLAUDE.md explicitly forbids using sleep to fix race conditions.
    """
    content = get_file_content()

    # Look for sleep calls in the modified function
    func_match = re.search(
        r'void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects.*?^\}',
        content,
        re.DOTALL | re.MULTILINE
    )

    if func_match:
        func_content = func_match.group(0)

        # Check for sleep functions
        sleep_patterns = [
            r'\bsleep\s*\(',
            r'\busleep\s*\(',
            r'\bnanosleep\s*\(',
            r'\bstd::this_thread::sleep_for',
            r'\bstd::this_thread::sleep_until',
        ]

        for pattern in sleep_patterns:
            assert not re.search(pattern, func_content), \
                f"Found forbidden sleep pattern '{pattern}' in refreshObjects (agent config forbids sleep for race conditions)"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/Code Quality Checks
# These tests verify the code passes standard ClickHouse CI checks on both
# the base commit and after the gold fix (regression prevention).
# =============================================================================


def test_repo_no_trailing_whitespace():
    """P2P: Target file has no trailing whitespace (ClickHouse style check).

    Uses grep command like the CI style check (ci/jobs/scripts/check_style/check_cpp.sh)
    to verify no trailing spaces. grep returns 1 when no matches found (which is what we want).
    """
    result = subprocess.run(
        ["grep", "-n", " $", FILE_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    # grep returns 1 if no matches found (good - no trailing whitespace)
    # grep returns 0 if matches found (bad - trailing whitespace exists)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')[:5]
        assert False, f"Trailing whitespace found:\n" + '\n'.join(lines)
    elif result.returncode != 1:
        assert False, f"grep failed with return code {result.returncode}: {result.stderr}"


def test_repo_no_tabs():
    """P2P: Target file uses spaces not tabs (ClickHouse style check).

    Uses grep -F to check for literal tab characters like the CI style check
    (ci/jobs/scripts/check_style/check_cpp.sh line 46). grep returns 1 when no matches found.
    """
    result = subprocess.run(
        ["grep", "-n", "-F", "\t", FILE_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    # grep returns 1 if no matches found (good - no tabs)
    # grep returns 0 if matches found (bad - tabs exist)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')[:5]
        assert False, f"Tab characters found (use 4 spaces instead):\n" + '\n'.join(lines)
    elif result.returncode != 1:
        assert False, f"grep failed with return code {result.returncode}: {result.stderr}"


def test_repo_no_bom():
    """P2P: Target file has no UTF-8/UTF-16 BOM marker (ClickHouse style check).

    Uses grep to check for BOM markers like the CI check in various_checks.sh
    (lines 95-98) which checks for UTF-8 and UTF-16 BOM markers.
    """
    # Check for UTF-8 BOM (EF BB BF)
    result_utf8 = subprocess.run(
        ["bash", "-c", f"grep -l $'\\xEF\\xBB\\xBF' {FILE_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    if result_utf8.returncode == 0:
        assert False, "UTF-8 BOM marker found at start of file"

    # Check for UTF-16LE BOM (FF FE)
    result_utf16le = subprocess.run(
        ["bash", "-c", f"grep -l $'\\xFF\\xFE' {FILE_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    if result_utf16le.returncode == 0:
        assert False, "UTF-16LE BOM marker found"

    # Check for UTF-16BE BOM (FE FF)
    result_utf16be = subprocess.run(
        ["bash", "-c", f"grep -l $'\\xFE\\xFF' {FILE_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    if result_utf16be.returncode == 0:
        assert False, "UTF-16BE BOM marker found"


def test_repo_clang_syntax_check():
    """P2P: Target file has valid C++ syntax (clang syntax-only check).

    Uses clang-16 to verify the file parses correctly as C++20.
    Ignores missing header errors (expected in isolated environment).
    This mirrors the approach in test_cpp_syntax_valid() but as a p2p check.
    """
    include_paths = ["-I.", "-Isrc", "-Ibase", "-Icontrib"]
    cmd = [
        "clang-16",
        "-fsyntax-only",
        "-std=c++20",
        "-x", "c++",
    ] + include_paths + [FILE_PATH]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Check for syntax errors in the target file (ignore missing headers)
    stderr = result.stderr
    if result.returncode != 0:
        # Filter out "file not found" errors - those are expected in isolated env
        error_lines = stderr.split('\n')
        syntax_errors = []
        for line in error_lines:
            line_lower = line.lower()
            # Skip lines about missing files - expected in isolated environment
            if "file not found" in line_lower or "no such file" in line_lower:
                continue
            # Skip system include errors
            if "/usr/include" in line or "fatal error:" in line_lower:
                continue
            # Look for actual syntax errors in our target file
            if TARGET_FILE in line and any(e in line_lower for e in [
                "expected", "syntax error", "undeclared", "invalid", "redefinition"
            ]):
                syntax_errors.append(line)

        if syntax_errors:
            assert False, f"C++ syntax errors found:\n" + '\n'.join(syntax_errors[:5])


def test_repo_check_settings_style():
    """P2P: Settings style check passes (ClickHouse CI check).

    Runs the check-settings-style script from the ClickHouse CI which validates
    that settings declarations follow the proper format and are not duplicated.
    Source: ci/jobs/scripts/check_style/check-settings-style
    """
    script_path = os.path.join(REPO, "ci/jobs/scripts/check_style/check-settings-style")
    result = subprocess.run(
        ["bash", script_path],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    # Script returns 0 if no issues, non-zero if issues found
    if result.returncode != 0 and result.stdout:
        # Only fail if there are actual output lines (style violations)
        violations = result.stdout.strip().split('\n')[:5]
        assert False, f"Settings style violations found:\n" + '\n'.join(violations)


def test_repo_code_style_basic():
    """P2P: Target file passes basic C++ style checks (ClickHouse style).

    Uses grep commands to check for common style violations:
    - No tabs (4 spaces for indentation)
    - No trailing whitespace
    - No curly braces on same line as control statements (Allman style)
    These checks mirror those in ci/jobs/scripts/check_style/check_cpp.sh.
    """
    # Check for tabs using grep -F (like CI does: grep -F $'\t')
    tab_result = subprocess.run(
        ["grep", "-n", "-F", "\t", FILE_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    # grep returns 1 if no matches (good), 0 if matches found (bad)
    if tab_result.returncode == 0:
        lines = tab_result.stdout.strip().split('\n')[:3]
        assert False, f"Tab characters found (use 4 spaces):\n" + '\n'.join(lines)

    # Check for trailing whitespace using grep (like CI does: grep -n -P ' $')
    trailing_result = subprocess.run(
        ["grep", "-n", " $", FILE_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    # grep returns 1 if no matches (good), 0 if matches found (bad)
    if trailing_result.returncode == 0:
        lines = trailing_result.stdout.strip().split('\n')[:3]
        assert False, f"Trailing whitespace found:\n" + '\n'.join(lines)

    # Check for bad brace style using the same regex pattern as CI check_cpp.sh
    # Pattern: control statement followed by { on same line
    style_result = subprocess.run(
        [
            "grep", "-n", "-P",
            r'((\b(class|struct|namespace|enum|if|for|while|else|throw|switch)\b.*|\)(\s*const)?(\s*noexcept)?(\s*override)?\s*))\{$|\s$|^ {1,3}[^\* ]\S|\t|^\s*\b(if|else if|if constexpr|else if constexpr|for|while|catch|switch)\b\(|\( [^\s\\]|\S \)',
            FILE_PATH
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    # Filter out false positives (single-line comments, multiline comment continuations)
    if style_result.returncode == 0:
        lines = style_result.stdout.strip().split('\n')
        filtered = []
        for line in lines:
            # Skip single-line comments and continuation of multiline comments
            if re.search(r'//|\s+\*|\$\(\(', line):
                continue
            filtered.append(line)
        if filtered:
            errors = filtered[:3]
            assert False, f"Style violations found:\n" + '\n'.join(errors)
