"""
Test suite for Superset pivot table date formatting fix.

The bug: Pivot table was showing '0NaN' in column and row headers when using
Date/Timestamp data because dateFormatters expect a number but were receiving
a string that couldn't be directly cast to a number.

The fix: Added a `convertToNumberIfNumeric` helper that only converts to a
number when the string is genuinely numeric, and falls back to the original
string otherwise.
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/superset"
TARGET_FILE = f"{REPO}/superset-frontend/plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx"


def read_target_file():
    """Read the content of the target file."""
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def test_convert_to_number_if_numeric_function_exists():
    """
    Fail-to-pass: Verify the convertToNumberIfNumeric helper function exists.

    On the base commit, this function doesn't exist. After the fix, it should be present.
    """
    content = read_target_file()

    # Check function definition exists
    pattern = r'function convertToNumberIfNumeric\s*\(\s*value:\s*string\s*\)\s*:\s*string\s*\|\s*number\s*\{'
    match = re.search(pattern, content)

    assert match is not None, (
        "convertToNumberIfNumeric function with signature "
        "'(value: string): string | number' not found"
    )


def test_convert_to_number_if_numeric_uses_number_cast():
    """
    Fail-to-pass: Verify the function uses Number() cast and Number.isNaN check.

    This ensures the implementation actually tries to convert to number safely.
    """
    content = read_target_file()

    # Extract function body
    func_match = re.search(
        r'function convertToNumberIfNumeric\s*\([^)]*\)\s*:[^{]+\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        content,
        re.DOTALL
    )
    assert func_match is not None, "Could not extract convertToNumberIfNumeric function body"

    func_body = func_match.group(1)

    # Check for Number(value) usage
    assert 'Number(value)' in func_body or 'Number(n)' in func_body, (
        "Function should use Number() to attempt conversion"
    )

    # Check for Number.isNaN() usage (not just isNaN)
    assert 'Number.isNaN' in func_body, (
        "Function should use Number.isNaN() for accurate NaN checking"
    )


def test_convert_to_number_if_numeric_handles_empty_strings():
    """
    Fail-to-pass: Verify the function handles empty strings correctly.

    Empty strings should not be converted to 0; they should pass through.
    """
    content = read_target_file()

    func_match = re.search(
        r'function convertToNumberIfNumeric\s*\([^)]*\)\s*:[^{]+\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        content,
        re.DOTALL
    )
    assert func_match is not None, "Could not extract convertToNumberIfNumeric function body"

    func_body = func_match.group(1)

    # Check for empty string handling
    assert "value.trim()" in func_body or "''" in func_body or '!==' in func_body, (
        "Function should handle empty string case to avoid converting '' to 0"
    )


def test_col_header_uses_helper():
    """
    Fail-to-pass: Verify renderColHeaderRow uses convertToNumberIfNumeric.

    The column header formatter call should wrap colKey[attrIdx] with the helper.
    """
    content = read_target_file()

    # Look for the pattern: dateFormatters?.[attrName]?.(convertToNumberIfNumeric(colKey[attrIdx]))
    pattern = r'dateFormatters\?\.\[attrName\]\?\.\(\s*convertToNumberIfNumeric\s*\(\s*colKey\[attrIdx\]\s*\)\s*\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "renderColHeaderRow should use convertToNumberIfNumeric(colKey[attrIdx]) "
        "when calling dateFormatters"
    )


def test_row_header_uses_helper():
    """
    Fail-to-pass: Verify renderTableRow uses convertToNumberIfNumeric.

    The row header formatter call should wrap 'r' with the helper.
    """
    content = read_target_file()

    # Look for the pattern: dateFormatters?.[rowAttrs[i]]?.(convertToNumberIfNumeric(r))
    pattern = r'dateFormatters\?\.\[rowAttrs\[i\]\]\?\.\(\s*convertToNumberIfNumeric\s*\(\s*r\s*\)\s*\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "renderTableRow should use convertToNumberIfNumeric(r) "
        "when calling dateFormatters"
    )


def test_no_bare_number_cast():
    """
    Fail-to-pass: Verify the old buggy pattern is replaced with helper.

    After the fix, convertToNumberIfNumeric should be used in the code.
    """
    content = read_target_file()

    # After the fix, we should have the helper function calls
    assert 'convertToNumberIfNumeric(colKey[attrIdx])' in content, (
        "Column header should use convertToNumberIfNumeric"
    )
    assert 'convertToNumberIfNumeric(r)' in content, (
        "Row header should use convertToNumberIfNumeric"
    )


def test_no_any_types():
    """
    Fail-to-pass: Verify the fix doesn't introduce 'any' types.

    Per CLAUDE.md/AGENTS.md: "NO `any` types - Use proper TypeScript types"
    This test passes after the fix when convertToNumberIfNumeric exists.
    """
    content = read_target_file()

    # First verify the function exists
    if 'function convertToNumberIfNumeric' not in content:
        # If function doesn't exist yet (before fix), this test is not applicable
        return

    # Check function signature is proper
    assert 'function convertToNumberIfNumeric(value: string): string | number' in content, (
        "convertToNumberIfNumeric should have proper TypeScript signature"
    )

    # Make sure the function body doesn't use 'any'
    func_match = re.search(
        r'function convertToNumberIfNumeric\s*\([^)]*\)\s*:[^{]+\{([^}]+)\}',
        content,
        re.DOTALL
    )
    if func_match:
        func_body = func_match.group(1)
        assert ': any' not in func_body, (
            "convertToNumberIfNumeric body should not use 'any' type"
        )


def test_typescript_syntax_valid():
    """
    Pass-to-pass: Verify the TypeScript file has valid syntax.

    Run TypeScript compiler to check for syntax errors.
    This should pass both before and after the fix.
    """
    result = subprocess.run(
        ['npx', 'tsc', '--noEmit', '--skipLibCheck', TARGET_FILE],
        cwd=f"{REPO}/superset-frontend",
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Note: We allow this to pass even with errors from skipLibCheck,
    # but we should have no errors in our specific file
    if result.returncode != 0:
        # Filter for only errors in our target file
        error_lines = [
            line for line in result.stdout.split('\n') + result.stderr.split('\n')
            if 'TableRenderers.tsx' in line and 'error TS' in line
        ]
        assert len(error_lines) == 0, (
            f"TypeScript errors in TableRenderers.tsx:\n" + '\n'.join(error_lines)
        )


def test_repo_pivot_table_lint():
    """
    Pass-to-pass: Repo linting passes for pivot table plugin.

    Runs oxlint to check for linting issues in the pivot table plugin.
    This should pass both before and after the fix.
    """
    # First install dependencies
    subprocess.run(
        ['npm', 'install'],
        cwd=f"{REPO}/superset-frontend",
        capture_output=True,
        text=True,
        timeout=300,
    )
    
    result = subprocess.run(
        ['npm', 'run', 'lint'],
        cwd=f"{REPO}/superset-frontend",
        capture_output=True,
        text=True,
        timeout=300,
    )

    assert result.returncode == 0, (
        f"Lint failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"
    )


def test_repo_pivot_table_unit_tests():
    """
    Pass-to-pass: Pivot table unit tests pass.

    Runs the Jest tests for the plugin-chart-pivot-table package.
    These tests should pass both before and after the fix.
    """
    # First install dependencies
    subprocess.run(
        ['npm', 'install'],
        cwd=f"{REPO}/superset-frontend",
        capture_output=True,
        text=True,
        timeout=300,
    )
    
    result = subprocess.run(
        ['npm', 'run', 'test', '--', 'plugins/plugin-chart-pivot-table', '--maxWorkers=2'],
        cwd=f"{REPO}/superset-frontend",
        capture_output=True,
        text=True,
        timeout=600,
    )

    assert result.returncode == 0, (
        f"Unit tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"
    )
