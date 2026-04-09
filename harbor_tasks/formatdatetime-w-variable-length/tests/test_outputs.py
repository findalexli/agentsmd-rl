"""Tests for formatDateTime %W variable-length formatter fix.

This test verifies that the fix correctly treats %W (weekday name) as a
variable-length formatter unconditionally, not just in certain code paths.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Functions/formatDateTime.cpp"


def test_target_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_variable_width_formatter_m_is_month_name_array():
    """variable_width_formatter_M_is_month_name should only contain 'M', not 'W'.

    The fix removes 'W' from this array since %W is now handled unconditionally.
    """
    content = TARGET_FILE.read_text()

    # Find the array definition
    pattern = r'static constexpr std::array variable_width_formatter_M_is_month_name = \{([^}]+)\};'
    match = re.search(pattern, content)
    assert match is not None, "Could not find variable_width_formatter_M_is_month_name array"

    array_content = match.group(1)

    # Should contain 'M'
    assert "'M'" in array_content, "Array should contain 'M'"

    # Should NOT contain 'W' (this was the bug)
    assert "'W'" not in array_content, "Bug not fixed: array still contains 'W' - it should only contain 'M'"


def test_w_check_moved_outside_conditional():
    """The %W check must be outside the mysql_M_is_month_name conditional.

    The fix moves the variable_width_formatter check (for 'W') to be executed
    BEFORE the if (mysql_M_is_month_name) conditional, so it applies unconditionally.
    """
    content = TARGET_FILE.read_text()

    # Find the containsOnlyFixedWidthMySQLFormatters function
    func_pattern = r'static bool containsOnlyFixedWidthMySQLFormatters.*?^    \}'
    func_match = re.search(func_pattern, content, re.DOTALL | re.MULTILINE)
    assert func_match is not None, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    func_content = func_match.group(0)

    # Find the if (mysql_M_is_month_name) block
    if_pattern = r'if \(mysql_M_is_month_name\)'
    if_match = re.search(if_pattern, func_content)
    assert if_match is not None, "Could not find 'if (mysql_M_is_month_name)' conditional"

    if_start_pos = if_match.start()

    # Find all occurrences of "variable_width_formatter" followed by begin/end check
    w_check_pattern = r'if \(std::any_of\s*\(\s*variable_width_formatter\.begin\(\),\s*variable_width_formatter\.end\(\)'
    w_checks = list(re.finditer(w_check_pattern, func_content, re.DOTALL))

    # Should have exactly one check for variable_width_formatter (for 'W')
    # This check should be BEFORE the if (mysql_M_is_month_name)
    found_w_before_conditional = False
    for w_check in w_checks:
        if w_check.start() < if_start_pos:
            found_w_before_conditional = True
            break

    assert found_w_before_conditional, (
        "Bug not fixed: The %W (variable_width_formatter) check is not outside "
        "the mysql_M_is_month_name conditional. It should be checked unconditionally "
        "before the conditional."
    )


def test_no_w_check_in_else_branch():
    """The else branch should NOT contain the variable_width_formatter check.

    Before the fix, there was an else branch that checked variable_width_formatter.
    After the fix, this else branch is removed/merged since the check is now done
    unconditionally before the conditional.
    """
    content = TARGET_FILE.read_text()

    # Find the function
    func_pattern = r'static bool containsOnlyFixedWidthMySQLFormatters.*?^    \}'
    func_match = re.search(func_pattern, content, re.DOTALL | re.MULTILINE)
    assert func_match is not None, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    func_content = func_match.group(0)

    # Look for patterns that suggest an else branch checking variable_width_formatter
    # The old code had: else { if (std::any_of(variable_width_formatter...)) }
    # After the fix, this else block should be gone

    # Check that we don't see "else" followed by variable_width_formatter check
    else_pattern = r'else\s*\{[^}]*variable_width_formatter\.begin\(\)'
    else_match = re.search(else_pattern, func_content, re.DOTALL)

    assert else_match is None, (
        "Bug not fixed: Found an 'else' branch containing variable_width_formatter check. "
        "The else branch should be removed since the check is now unconditional."
    )


def test_compilation_succeeds():
    """The modified file should compile successfully.

    This is a basic sanity check that the code is syntactically correct.
    We try to compile just the affected file to save time.
    """
    # First, check if the build directory exists
    build_dir = REPO / "build"

    # If no build directory, we'll skip this test
    if not build_dir.exists():
        pytest.skip("Build directory not found, skipping compilation test")

    # Try to compile just the formatDateTime.cpp file
    result = subprocess.run(
        ["ninja", "src/Functions/CMakeFiles/clickhouse_functions.dir/formatDateTime.cpp.o"],
        cwd=build_dir,
        capture_output=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Compilation failed:\n{result.stderr.decode()}"
    )


def test_repo_no_tabs():
    """Target file has no tab characters (pass_to_pass).

    ClickHouse CI check_cpp.sh forbids tabs in C++ source files.
    """
    content = TARGET_FILE.read_text()
    assert "\t" not in content, "Tab characters found in target file (repo CI forbids tabs)"


def test_repo_no_trailing_whitespace():
    """Target file has no trailing whitespace (pass_to_pass).

    ClickHouse CI check_cpp.sh checks for trailing whitespace in C++ files.
    """
    content = TARGET_FILE.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        assert line == line.rstrip(" "), f"Trailing whitespace on line {i}"


def test_repo_no_crlf():
    """Target file uses Unix line endings (pass_to_pass).

    ClickHouse CI various_checks.sh forbids DOS/Windows newlines.
    """
    content = TARGET_FILE.read_bytes()
    assert b"\r\n" not in content, "CRLF line endings found (repo CI requires Unix LF)"


def test_repo_no_bom():
    """Target file has no UTF-8 BOM (pass_to_pass).

    ClickHouse CI various_checks.sh checks for BOM in source files.
    """
    content = TARGET_FILE.read_bytes()
    assert not content.startswith(b"\xef\xbb\xbf"), "UTF-8 BOM found in target file"


def test_repo_no_duplicate_includes():
    """Target file has no duplicate #include directives (pass_to_pass).

    ClickHouse CI check_style.py runs check_duplicate_includes on C++ files.
    """
    content = TARGET_FILE.read_text()
    includes = [line.strip() for line in content.splitlines() if line.strip().startswith("#include ")]
    seen = set()
    for inc in includes:
        assert inc not in seen, f"Duplicate include: {inc}"
        seen.add(inc)


def test_repo_allman_braces_in_function():
    """The modified function uses Allman-style braces (pass_to_pass).

    ClickHouse CI check_cpp.sh enforces opening braces on new lines
    for control structures (if/else/for/while/switch).
    """
    content = TARGET_FILE.read_text()
    func_pattern = r"static bool containsOnlyFixedWidthMySQLFormatters.*?^    \}"
    func_match = re.search(func_pattern, content, re.DOTALL | re.MULTILINE)
    assert func_match is not None, "Could not find containsOnlyFixedWidthMySQLFormatters function"
    func_content = func_match.group(0)

    for line in func_content.splitlines():
        stripped = line.strip()
        # Skip lines with lambdas (e.g., [&](char c){ return ... })
        if "[&]" in stripped or "[=]" in stripped:
            continue
        # Check for control statement with opening brace on same line
        if re.match(r"^\s*(if|else if|else|for|while|switch)\b", stripped):
            assert "{" not in stripped or stripped.endswith("{}"), (
                f"Allman brace violation: control statement has '{{' on same line:\n  {stripped}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
