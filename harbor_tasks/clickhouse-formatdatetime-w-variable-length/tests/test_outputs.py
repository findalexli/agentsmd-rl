#!/usr/bin/env python3
"""Tests for formatDateTime %W variable-length formatter fix.

Bug: The %W formatter (weekday name) was not consistently treated as variable-length.
When mysql_M_is_month_name=true, %W would incorrectly be considered fixed-width.

Fix: Always check for %W unconditionally before other format-specific checks.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Functions/formatDateTime.cpp")


def get_function_body(content):
    """Extract the containsOnlyFixedWidthMySQLFormatters function body."""
    # Find the function - it starts with the signature and ends with the closing brace
    pattern = r'(static bool containsOnlyFixedWidthMySQLFormatters\(std::string_view format[^)]*\))\s*\{'
    match = re.search(pattern, content)
    if not match:
        return None

    start_idx = match.end() - 1  # Position of the opening brace

    # Find matching closing brace
    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(content[start_idx:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = start_idx + i
                break

    return content[start_idx:end_idx+1]


def test_variable_width_formatter_array_updated():
    """F2P: Verify variable_width_formatter_M_is_month_name no longer includes 'W'."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The fix changes the array to only contain 'M'
    pattern = r"static constexpr std::array variable_width_formatter_M_is_month_name = \{'M'\};"
    assert re.search(pattern, content), \
        "variable_width_formatter_M_is_month_name should only contain 'M', not 'W'"


def test_unconditional_w_check_added():
    """F2P: Verify %W is now checked unconditionally before other format checks."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    func_body = get_function_body(content)
    assert func_body, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    # After the fix, the pattern should be:
    # 1. if (i + 1 >= format.size()) check
    # 2. variable_width_formatter check (for 'W') - UNCONDITIONAL
    # 3. if (mysql_M_is_month_name) check

    # Find the positions of the key checks in the switch case
    percent_size_check = "if (i + 1 >= format.size())"
    w_check = "if (std::any_of(\n                            variable_width_formatter.begin(),"
    m_check = "if (mysql_M_is_month_name)"

    percent_pos = func_body.find(percent_size_check)
    w_pos = func_body.find(w_check)
    m_pos = func_body.find(m_check)

    # All should exist
    assert percent_pos != -1, "Should find percent size check"
    assert w_pos != -1, "Should find variable_width_formatter check"
    assert m_pos != -1, "Should find mysql_M_is_month_name check"

    # The fix: variable_width_formatter check should come BEFORE mysql_M_is_month_name check
    # and AFTER the percent size check
    assert percent_pos < w_pos, \
        f"Percent size check should come before variable_width_formatter check"
    assert w_pos < m_pos, \
        f"variable_width_formatter check should come BEFORE mysql_M_is_month_name check"


def test_no_redundant_w_in_m_array():
    """F2P: Verify 'W' is not redundantly in the M_is_month_name array."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the variable_width_formatter_M_is_month_name array definition
    match = re.search(
        r"static constexpr std::array variable_width_formatter_M_is_month_name = \{([^}]+)\};",
        content
    )
    assert match, "Should find variable_width_formatter_M_is_month_name array definition"

    array_content = match.group(1)
    # After fix, only 'M' should be in this array (not 'W')
    assert "'W'" not in array_content, \
        f"'W' should NOT be in variable_width_formatter_M_is_month_name array (found: {array_content})"
    assert "'M'" in array_content, \
        "'M' should be in variable_width_formatter_M_is_month_name array"


def test_w_in_variable_width_formatter():
    """P2P: Verify 'W' remains in the main variable_width_formatter array."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the variable_width_formatter array
    match = re.search(
        r"static constexpr std::array variable_width_formatter = \{([^}]+)\};",
        content
    )
    assert match, "Should find variable_width_formatter array definition"

    array_content = match.group(1)
    assert "'W'" in array_content, \
        f"'W' should be in variable_width_formatter array (found: {array_content})"


def test_function_signature_unchanged():
    """P2P: Verify the function signature remains unchanged."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    expected_sig = (
        "static bool containsOnlyFixedWidthMySQLFormatters"
        "(std::string_view format, bool mysql_M_is_month_name, "
        "bool mysql_format_ckl_without_leading_zeros, bool mysql_e_with_space_padding)"
    )
    assert expected_sig in content, "Function signature should not change"


def test_no_sleep_in_code():
    """P2P (agent config): Verify no sleep calls were added to fix race conditions."""
    func_body = get_function_body(open(TARGET_FILE, 'r').read())
    if func_body:
        # Check for sleep-related calls
        sleep_patterns = [r'\bsleep\s*\(', r'\busleep\s*\(', r'Sleep\s*\(', r'nanosleep\s*\(']
        for pattern in sleep_patterns:
            assert not re.search(pattern, func_body, re.IGNORECASE), \
                f"Should not use sleep() calls (found pattern: {pattern})"


def test_code_uses_allman_braces():
    """P2P (agent config): Verify the modified code uses Allman-style braces."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    func_body = get_function_body(content)
    if not func_body:
        return  # Skip if we can't find the function

    # Check for K&R style in control structures (if/else/for/while)
    # In Allman style: opening brace should be on its own line after the statement
    lines = func_body.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check for patterns like "if (condition) {" which is K&R, not Allman
        if re.match(r'^(if|else|for|while|switch)\s*\([^)]*\)\s*\{\s*$', stripped):
            assert False, f"Found K&R style brace on line {i}: {line}"


def test_repo_style_cpp():
    """P2P: Target file C++ style check passes (pass_to_pass)."""
    # Run style check and filter to only our target file
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # Filter errors to only those related to our target file
    # Style errors are indicated by lines starting with "^" or containing the file path
    lines = r.stdout.split('\n') if r.stdout else []
    target_file_errors = []
    current_file = None
    for line in lines:
        # Track which file the error is for
        if 'src/Functions/formatDateTime.cpp' in line:
            current_file = 'target'
        elif line.startswith('^'):
            if current_file == 'target' or 'formatDateTime' in line:
                target_file_errors.append(line)
        elif line.startswith('/') and 'src/' in line:
            # New file section - reset tracking
            current_file = 'other'
    assert len(target_file_errors) == 0, f"Target file style check failed:\n{chr(10).join(target_file_errors[:10])}"


def test_repo_various_checks():
    """P2P: Repo various checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # The script outputs warnings but we check for errors
    lines = r.stdout.split('\n') if r.stdout else []
    error_lines = [l for l in lines if 'should' in l.lower() or 'must' in l.lower() or 'error' in l.lower()]
    # Filter to real errors (lines with actionable issues)
    real_errors = [l for l in error_lines if l.strip() and not l.startswith('#')]
    assert len(real_errors) == 0, f"Various checks failed:\n{chr(10).join(real_errors[:10])}"


def test_repo_functional_test_files_exist():
    """P2P: formatDateTime functional test files exist (pass_to_pass)."""
    test_files = [
        "tests/queries/0_stateless/00718_format_datetime.sql",
        "tests/queries/0_stateless/00718_format_datetime.reference",
        "tests/queries/0_stateless/00719_format_datetime_f_varsize_bug.sql",
        "tests/queries/0_stateless/00719_format_datetime_f_varsize_bug.reference",
    ]
    for test_file in test_files:
        full_path = os.path.join(REPO, test_file)
        assert os.path.exists(full_path), f"Test file should exist: {test_file}"
