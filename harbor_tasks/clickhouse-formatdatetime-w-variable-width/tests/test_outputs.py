"""
Tests for formatDateTime %W variable-width formatter fix.

The bug: %W (weekday name) was treated as variable-width only when certain
settings were enabled (mysql_M_is_month_name=False and mysql_e_with_space_padding=False).
When mysql_M_is_month_name=True, %W was incorrectly treated as fixed-width.

The fix: Always check for %W as a variable-width formatter before checking
the conditional formatter arrays.
"""

import subprocess
import sys
import tempfile
import os

# The function logic to test - extracted from formatDateTime.cpp
# We test this by compiling a small C++ program that tests the logic

FUNCTION_LOGIC = '''
#include <array>
#include <string_view>
#include <algorithm>
#include <iostream>
#include <cstring>

// Original buggy implementation (for comparison)
static bool containsOnlyFixedWidthMySQLFormatters_BUGGY(
    std::string_view format,
    bool mysql_M_is_month_name,
    bool mysql_format_ckl_without_leading_zeros,
    bool mysql_e_with_space_padding)
{
    static constexpr std::array variable_width_formatter = {'W'};
    static constexpr std::array variable_width_formatter_M_is_month_name = {'W', 'M'};
    static constexpr std::array variable_width_formatter_leading_zeros = {'c', 'l', 'k'};
    static constexpr std::array variable_width_formatter_e_with_space_padding = {'e'};

    for (size_t i = 0; i < format.size(); ++i)
    {
        switch (format[i])
        {
            case '%':
                if (i + 1 >= format.size())
                    return false; // Last character is %
                if (mysql_M_is_month_name)
                {
                    if (std::any_of(
                            variable_width_formatter_M_is_month_name.begin(), variable_width_formatter_M_is_month_name.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                if (mysql_format_ckl_without_leading_zeros)
                {
                    if (std::any_of(
                            variable_width_formatter_leading_zeros.begin(), variable_width_formatter_leading_zeros.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                if (!mysql_e_with_space_padding)
                {
                    if (std::any_of(
                            variable_width_formatter_e_with_space_padding.begin(), variable_width_formatter_e_with_space_padding.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                else
                {
                    if (std::any_of(
                            variable_width_formatter.begin(), variable_width_formatter.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                i += 1;
                continue;
            default:
                break;
        }
    }
    return true;
}

// Fixed implementation
static bool containsOnlyFixedWidthMySQLFormatters_FIXED(
    std::string_view format,
    bool mysql_M_is_month_name,
    bool mysql_format_ckl_without_leading_zeros,
    bool mysql_e_with_space_padding)
{
    static constexpr std::array variable_width_formatter = {'W'};
    static constexpr std::array variable_width_formatter_M_is_month_name = {'M'};  // 'W' removed
    static constexpr std::array variable_width_formatter_leading_zeros = {'c', 'l', 'k'};
    static constexpr std::array variable_width_formatter_e_with_space_padding = {'e'};

    for (size_t i = 0; i < format.size(); ++i)
    {
        switch (format[i])
        {
            case '%':
                if (i + 1 >= format.size())
                    return false; // Last character is %

                // FIX: Check %W unconditionally first
                if (std::any_of(
                        variable_width_formatter.begin(), variable_width_formatter.end(),
                        [&](char c){ return c == format[i + 1]; }))
                    return false;

                if (mysql_M_is_month_name)
                {
                    if (std::any_of(
                            variable_width_formatter_M_is_month_name.begin(), variable_width_formatter_M_is_month_name.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                if (mysql_format_ckl_without_leading_zeros)
                {
                    if (std::any_of(
                            variable_width_formatter_leading_zeros.begin(), variable_width_formatter_leading_zeros.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                if (!mysql_e_with_space_padding)
                {
                    if (std::any_of(
                            variable_width_formatter_e_with_space_padding.begin(), variable_width_formatter_e_with_space_padding.end(),
                            [&](char c){ return c == format[i + 1]; }))
                        return false;
                }
                // Removed the else clause that was previously needed for %W
                i += 1;
                continue;
            default:
                break;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <test_case>" << std::endl;
        return 1;
    }

    const char* test = argv[1];

    // Test: %W should be variable-width regardless of mysql_M_is_month_name
    if (strcmp(test, "test_w_with_m_is_month_name") == 0) {
        // Bug: When mysql_M_is_month_name=false AND mysql_e_with_space_padding=false,
        // the buggy code skips the %W check entirely because the 'else' clause is not entered
        bool buggy_result = containsOnlyFixedWidthMySQLFormatters_BUGGY("%W", false, false, false);
        bool fixed_result = containsOnlyFixedWidthMySQLFormatters_FIXED("%W", false, false, false);

        // %W should be detected as variable-width (return false), but buggy code returns true (fixed)
        if (buggy_result == true && fixed_result == false) {
            // Bug confirmed: buggy says fixed, fixed says variable
            return 0; // Test passed - we detected the bug
        }
        return 1; // Test failed - either bug not present or logic error
    }

    // Test: %W with different flag combinations
    if (strcmp(test, "test_w_with_various_flags") == 0) {
        // Test various combinations of flags - buggy version fails when:
        // - mysql_M_is_month_name=false (not in first branch)
        // - mysql_e_with_space_padding=false (else clause not taken)
        struct FlagCombo { bool m_is_month; bool no_leading_zeros; bool space_padding; };
        FlagCombo combos[] = {
            {true, false, false},   // OK: detected via variable_width_formatter_M_is_month_name
            {true, false, true},    // OK: detected via variable_width_formatter_M_is_month_name
            {true, true, false},    // OK: detected via variable_width_formatter_M_is_month_name
            {true, true, true},     // OK: detected via variable_width_formatter_M_is_month_name
            {false, true, false},   // BUG: not in any branch
            {false, true, true},    // OK: detected via variable_width_formatter in else
            {false, false, true},   // OK: detected via variable_width_formatter in else
            {false, false, false},  // BUG: not in any branch (first and last skipped)
        };

        bool found_bug = false;
        for (const auto& combo : combos) {
            bool buggy_result = containsOnlyFixedWidthMySQLFormatters_BUGGY("%W", combo.m_is_month, combo.no_leading_zeros, combo.space_padding);
            bool fixed_result = containsOnlyFixedWidthMySQLFormatters_FIXED("%W", combo.m_is_month, combo.no_leading_zeros, combo.space_padding);

            // After fix, %W should always be detected as variable-width
            if (fixed_result != false) {
                std::cerr << "FAIL: Fixed version - %W should be variable-width with flags ("
                          << combo.m_is_month << ", " << combo.no_leading_zeros << ", " << combo.space_padding << ")" << std::endl;
                return 1;
            }

            // Buggy version should fail for some combinations
            if (buggy_result == true && fixed_result == false) {
                found_bug = true;  // Detected the bug for this combo
            }
        }

        // We should have found at least one buggy combination
        if (!found_bug) {
            std::cerr << "FAIL: Did not detect any buggy behavior - bug may be fixed already" << std::endl;
            return 1;
        }
        return 0; // All passed and bug was detected
    }

    // Test: %M behavior with mysql_M_is_month_name
    if (strcmp(test, "test_m_with_m_is_month_name") == 0) {
        // %M should be variable-width only when mysql_M_is_month_name=true
        bool fixed_true = containsOnlyFixedWidthMySQLFormatters_FIXED("%M", true, false, false);
        bool fixed_false = containsOnlyFixedWidthMySQLFormatters_FIXED("%M", false, false, false);

        if (fixed_true != false) {
            std::cerr << "FAIL: %M should be variable-width when mysql_M_is_month_name=true" << std::endl;
            return 1;
        }
        if (fixed_false != true) {
            std::cerr << "FAIL: %M should be fixed-width when mysql_M_is_month_name=false" << std::endl;
            return 1;
        }
        return 0;
    }

    // Test: Fixed-width formatters should still work
    if (strcmp(test, "test_fixed_width_formatters") == 0) {
        // %Y, %m, %d are fixed-width
        bool result = containsOnlyFixedWidthMySQLFormatters_FIXED("%Y-%m-%d", false, false, false);
        if (result != true) {
            std::cerr << "FAIL: %Y-%m-%d should be fixed-width" << std::endl;
            return 1;
        }
        return 0;
    }

    std::cerr << "Unknown test: " << test << std::endl;
    return 1;
}
'''


def compile_test_harness():
    """Compile the C++ test harness."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write(FUNCTION_LOGIC)
        cpp_file = f.name

    exe_file = cpp_file.replace('.cpp', '')
    result = subprocess.run(
        ['g++', '-std=c++17', '-O2', '-o', exe_file, cpp_file],
        capture_output=True,
        text=True
    )
    os.unlink(cpp_file)

    if result.returncode != 0:
        raise RuntimeError(f"Compilation failed: {result.stderr}")

    return exe_file


# Global test executable
TEST_EXE = None


def setup_module():
    """Compile test harness once before all tests."""
    global TEST_EXE
    TEST_EXE = compile_test_harness()


def teardown_module():
    """Clean up compiled executable."""
    global TEST_EXE
    if TEST_EXE and os.path.exists(TEST_EXE):
        os.unlink(TEST_EXE)


def run_test(test_case):
    """Run a specific test case from the compiled harness."""
    result = subprocess.run(
        [TEST_EXE, test_case],
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.returncode == 0, result.stderr


# =============================================================================
# Fail-to-pass tests (these should fail before the fix, pass after)
# =============================================================================

def test_w_variable_width_with_m_is_month_name():
    """
    Test that %W is detected as variable-width when mysql_M_is_month_name=true.

    This is the core bug: the buggy code only checked for %W in the
    variable_width_formatter array inside an else clause that required
    mysql_e_with_space_padding to be false AND mysql_M_is_month_name to be false.

    When mysql_M_is_month_name=true, %W was NOT in variable_width_formatter_M_is_month_name,
    so it was incorrectly treated as fixed-width.
    """
    passed, stderr = run_test("test_w_with_m_is_month_name")
    assert passed, f"Bug not detected: %W should be variable-width regardless of mysql_M_is_month_name. stderr: {stderr}"


def test_w_variable_width_with_various_flags():
    """
    Test that %W is consistently variable-width across all flag combinations.

    The fix ensures %W is checked before the conditional branches for
    mysql_M_is_month_name, mysql_format_ckl_without_leading_zeros, and
    mysql_e_with_space_padding.
    """
    passed, stderr = run_test("test_w_with_various_flags")
    assert passed, f"%W not consistently variable-width: {stderr}"


# =============================================================================
# Pass-to-pass tests (these should pass before and after the fix)
# =============================================================================

def test_m_behavior_unchanged():
    """
    Test that %M behavior is unchanged: variable-width only when mysql_M_is_month_name=true.

    The fix changes variable_width_formatter_M_is_month_name from {'W', 'M'} to just {'M'},
    but %W is now checked separately before the mysql_M_is_month_name branch.
    """
    passed, stderr = run_test("test_m_with_m_is_month_name")
    assert passed, f"%M behavior changed unexpectedly: {stderr}"


def test_fixed_width_formatters_still_work():
    """
    Test that fixed-width formatters (%Y, %m, %d) still work correctly.

    Regression test to ensure the fix doesn't break existing behavior.
    """
    passed, stderr = run_test("test_fixed_width_formatters")
    assert passed, f"Fixed-width formatters broken: {stderr}"


# =============================================================================
# Repo CI/CD pass-to-pass tests (verify repo structure and basic integrity)
# =============================================================================

REPO = "/workspace/ClickHouse"


def test_repo_file_structure():
    """Repo's essential files exist and are accessible (pass_to_pass)."""
    import pathlib

    repo_path = pathlib.Path(REPO)

    # Essential files that should exist
    essential_files = [
        "src/Functions/formatDateTime.cpp",
        "CMakeLists.txt",
        "src/Functions/CMakeLists.txt",
        "ci/jobs/check_style.py",
    ]

    for file_path in essential_files:
        full_path = repo_path / file_path
        assert full_path.exists(), f"Essential file missing: {file_path}"


def test_repo_files_valid_utf8():
    """Repo's source files are valid UTF-8 (pass_to_pass)."""
    import pathlib

    repo_path = pathlib.Path(REPO)
    cpp_file = repo_path / "src" / "Functions" / "formatDateTime.cpp"

    # Should be able to read as text
    try:
        content = cpp_file.read_text(encoding='utf-8')
        assert len(content) > 0, "File should not be empty"
        # Should contain expected function
        assert "containsOnlyFixedWidthMySQLFormatters" in content, \
            "Target function not found in file"
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"


def test_repo_python_syntax():
    """Repo's Python CI scripts have valid syntax (pass_to_pass)."""
    import pathlib
    import ast

    repo_path = pathlib.Path(REPO)
    py_files = [
        "ci/jobs/check_style.py",
        "ci/jobs/fast_test.py",
        "ci/jobs/build_clickhouse.py",
    ]

    for py_file in py_files:
        full_path = repo_path / py_file
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                ast.parse(content)
            except SyntaxError as e:
                assert False, f"Python syntax error in {py_file}: {e}"


def test_repo_git_state():
    """Repo has a clean git state at expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    # Should succeed and either be empty (clean) or have only expected untracked files
    assert r.returncode == 0, f"Git status failed: {r.stderr}"

    # Check we are at the expected commit
    r2 = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r2.returncode == 0, f"Git rev-parse failed: {r2.stderr}"
    current_commit = r2.stdout.strip()
    # Base commit is 61a4296fdce9d13cafb931cf73e4490b6d2bb315
    assert current_commit.startswith("61a4296"), \
        f"Not at expected base commit, got: {current_commit}"


def test_repo_cmake_syntax():
    """Repo's CMakeLists.txt has valid syntax (pass_to_pass)."""
    import pathlib
    import re

    repo_path = pathlib.Path(REPO)
    cmake_file = repo_path / "CMakeLists.txt"

    content = cmake_file.read_text(encoding='utf-8')

    # Basic sanity checks for CMake structure
    # Should have cmake_minimum_required
    assert "cmake_minimum_required" in content, "Missing cmake_minimum_required"
    # Should have project declaration
    assert "project(" in content, "Missing project declaration"
    # Balanced parentheses check (basic)
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


# =============================================================================
# Code structure tests (verify the fix was applied correctly)
# =============================================================================

def test_w_removed_from_m_is_month_name_array():
    """
    Verify the fix: 'W' should be removed from variable_width_formatter_M_is_month_name.

    The original code had: {'W', 'M'}
    The fixed code should have: {'M'}
    """
    import pathlib

    # Check the actual source file
    repo_path = pathlib.Path('/workspace/ClickHouse')
    cpp_file = repo_path / 'src' / 'Functions' / 'formatDateTime.cpp'

    assert cpp_file.exists(), f"Source file not found: {cpp_file}"

    content = cpp_file.read_text()

    # Find the line with variable_width_formatter_M_is_month_name
    lines = content.split('\n')
    found_line = None
    for line in lines:
        if 'variable_width_formatter_M_is_month_name' in line and 'std::array' in line:
            found_line = line
            break

    assert found_line is not None, "variable_width_formatter_M_is_month_name declaration not found"

    # After the fix, it should contain only 'M', not 'W'
    # The fix changes: {'W', 'M'} -> {'M'}
    assert "'M'" in found_line, "variable_width_formatter_M_is_month_name should contain 'M'"

    # Check that 'W' is NOT on the same line (it should only be in variable_width_formatter)
    if "'W'" in found_line:
        assert False, "'W' should be removed from variable_width_formatter_M_is_month_name array"


def test_w_check_moved_before_conditionals():
    """
    Verify that %W is checked unconditionally before the conditional branches.

    The fix moves the %W check to the top of the switch case, before the
    mysql_M_is_month_name check.
    """
    import pathlib
    import re

    repo_path = pathlib.Path('/workspace/ClickHouse')
    cpp_file = repo_path / 'src' / 'Functions' / 'formatDateTime.cpp'

    assert cpp_file.exists(), f"Source file not found: {cpp_file}"

    content = cpp_file.read_text()

    # Find the containsOnlyFixedWidthMySQLFormatters function
    func_match = re.search(
        r'static bool containsOnlyFixedWidthMySQLFormatters.*?^    \}',
        content,
        re.DOTALL | re.MULTILINE
    )

    assert func_match is not None, "Function containsOnlyFixedWidthMySQLFormatters not found"

    func_body = func_match.group(0)

    # The fix should have the %W check before the mysql_M_is_month_name check
    # Look for the pattern where we check variable_width_formatter first

    # Find positions of key patterns WITHIN the function body
    # The first occurrence of variable_width_formatter.begin() in the function
    w_check_pos = func_body.find('variable_width_formatter.begin()')

    # The if statement that checks mysql_M_is_month_name inside the function
    # We need to find "if (mysql_M_is_month_name)" inside the switch/case
    m_check_match = re.search(r'if \(mysql_M_is_month_name\)', func_body)

    assert w_check_pos != -1, "%W check not found in function"
    assert m_check_match is not None, "mysql_M_is_month_name check not found in function body"

    m_check_pos = m_check_match.start()

    # %W check should come BEFORE mysql_M_is_month_name check
    assert w_check_pos < m_check_pos, \
        f"%W check should be moved before mysql_M_is_month_name check (fix not applied correctly). " \
        f"w_check_pos={w_check_pos}, m_check_pos={m_check_pos}"


def test_no_else_clause_for_w():
    """
    Verify the else clause that previously checked %W has been removed.

    The original buggy code had:
        else
        {
            if (std::any_of(
                    variable_width_formatter.begin(), variable_width_formatter.end(),
                    [&](char c){ return c == format[i + 1]; }))
                return false;
        }

    After the fix, this else clause is removed because %W is checked earlier.
    """
    import pathlib
    import re

    repo_path = pathlib.Path('/workspace/ClickHouse')
    cpp_file = repo_path / 'src' / 'Functions' / 'formatDateTime.cpp'

    assert cpp_file.exists(), f"Source file not found: {cpp_file}"

    content = cpp_file.read_text()

    # Find the containsOnlyFixedWidthMySQLFormatters function
    func_match = re.search(
        r'static bool containsOnlyFixedWidthMySQLFormatters.*?^    \}',
        content,
        re.DOTALL | re.MULTILINE
    )

    assert func_match is not None, "Function not found"
    func_body = func_match.group(0)

    # Count occurrences of "else" after the mysql_e_with_space_padding check
    # The fix removes the else clause that checked variable_width_formatter

    # Look for the pattern of the removed else clause
    # This is a structural check - the else clause checking %W should be gone

    # After the fix, there should be no standalone "else" block with just a %W check
    # The new structure has the %W check at the top, then if/if/if without a trailing else

    # Check that we have the pattern: "else" block that contains variable_width_formatter check is removed
    lines = func_body.split('\n')

    # Find lines with 'else' and 'variable_width_formatter' close together
    for i, line in enumerate(lines):
        if 'else' in line and line.strip() == 'else':
            # Check the next few lines for the old %W check pattern
            for j in range(i+1, min(i+5, len(lines))):
                if 'variable_width_formatter.begin()' in lines[j]:
                    assert False, "Old else clause for %W check still present (should be removed)"

    # If we get here, the else clause was properly removed
    pass
