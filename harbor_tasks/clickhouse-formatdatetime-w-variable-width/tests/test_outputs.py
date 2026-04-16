"""
Tests for formatDateTime %W variable-width formatter fix.

These tests verify behavior by:
1. Extracting the containsOnlyFixedWidthMySQLFormatters function from actual ClickHouse source
2. Compiling it into a test harness
3. Calling the compiled function with various inputs and asserting on return values

This approach tests the ACTUAL code in /workspace/ClickHouse/src/Functions/formatDateTime.cpp,
not embedded copies with hardcoded buggy/fixed implementations.
"""

import subprocess
import sys
import tempfile
import os
import re
import pathlib


REPO = "/workspace/ClickHouse"


def extract_function_from_source():
    """Extract the containsOnlyFixedWidthMySQLFormatters function and its helpers from actual source."""
    cpp_file = pathlib.Path(REPO) / 'src' / 'Functions' / 'formatDateTime.cpp'

    if not cpp_file.exists():
        raise RuntimeError(f"Source file not found: {cpp_file}")

    content = cpp_file.read_text()

    # Find the helper function and the main function together
    pattern = r'(static void throwLastCharacterIsPercentException\(\).*?static bool containsOnlyFixedWidthMySQLFormatters\(.*?\n(?:[^}]*\n)*?\s{4}\})'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        raise RuntimeError("Could not find functions in source")

    return match.group(1)


def create_test_harness(function_code):
    """Create a complete C++ test harness that includes the extracted function."""
    # Replace the throw statement with our own exception
    # The source uses escaped double quotes: "\'%\' must not..."
    old_throw = '''        throw Exception(ErrorCodes::BAD_ARGUMENTS, "\'%\' must not be the last character in the format string, use \'%%\' instead");'''
    new_throw = '''        throw std::runtime_error("invalid format");'''
    modified_code = function_code.replace(old_throw, new_throw)
    
    if old_throw not in function_code:
        print(f"WARNING: Could not find throw statement to replace. Function code snippet:\n{function_code[:500]}")

    harness = '''
#include <array>
#include <string_view>
#include <algorithm>
#include <iostream>
#include <cstring>
#include <stdexcept>

// Stubs for ClickHouse types
#define ErrorCodes int
const int BAD_ARGUMENTS = 1;

// The extracted function from ClickHouse source (with throw replaced)
''' + modified_code + '''

// Test runner
int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <test_case>" << std::endl;
        return 1;
    }

    const char* test = argv[1];

    // Test 1: %W should be variable-width (return false) when mysql_M_is_month_name=true
    if (strcmp(test, "test_w_with_m_is_month_name_true") == 0) {
        try {
            bool result = containsOnlyFixedWidthMySQLFormatters("%W", true, false, false);
            if (result == false) {
                return 0; // PASS: %W is variable-width
            }
            std::cerr << "FAIL: %W should be variable-width when mysql_M_is_month_name=true, got fixed-width" << std::endl;
        } catch (const std::runtime_error& e) {
            std::cerr << "Exception: " << e.what() << std::endl;
        }
        return 1;
    }

    // Test 2: %W should be variable-width when mysql_M_is_month_name=false
    if (strcmp(test, "test_w_with_m_is_month_name_false") == 0) {
        try {
            bool result = containsOnlyFixedWidthMySQLFormatters("%W", false, false, false);
            if (result == false) {
                return 0; // PASS: %W is variable-width
            }
            std::cerr << "FAIL: %W should be variable-width when mysql_M_is_month_name=false, got fixed-width" << std::endl;
        } catch (const std::runtime_error& e) {
            std::cerr << "Exception: " << e.what() << std::endl;
        }
        return 1;
    }

    // Test 3: %W should be variable-width with various flag combinations
    if (strcmp(test, "test_w_with_various_flags") == 0) {
        struct FlagCombo {
            bool m_is_month;
            bool no_leading_zeros;
            bool space_padding;
        };
        FlagCombo combos[] = {
            {true, false, false},
            {true, false, true},
            {true, true, false},
            {true, true, true},
            {false, true, false},
            {false, true, true},
            {false, false, true},
            {false, false, false},
        };

        for (const auto& combo : combos) {
            try {
                bool result = containsOnlyFixedWidthMySQLFormatters("%W", combo.m_is_month, combo.no_leading_zeros, combo.space_padding);
                if (result != false) {
                    std::cerr << "FAIL: %W should be variable-width with flags (" << combo.m_is_month << ", " << combo.no_leading_zeros << ", " << combo.space_padding << "), got fixed-width" << std::endl;
                    return 1;
                }
            } catch (const std::runtime_error& e) {
                std::cerr << "Exception with flags (" << combo.m_is_month << ", " << combo.no_leading_zeros << ", " << combo.space_padding << "): " << e.what() << std::endl;
                return 1;
            }
        }
        return 0; // PASS: %W is variable-width with all combinations
    }

    // Test 4: %M should be variable-width only when mysql_M_is_month_name=true
    if (strcmp(test, "test_m_with_m_is_month_name") == 0) {
        try {
            bool result_true = containsOnlyFixedWidthMySQLFormatters("%M", true, false, false);
            bool result_false = containsOnlyFixedWidthMySQLFormatters("%M", false, false, false);

            if (result_true == false && result_false == true) {
                return 0; // PASS: %M variable when M_is_month=true, fixed otherwise
            }
            if (result_true != false) {
                std::cerr << "FAIL: %M should be variable-width when mysql_M_is_month_name=true" << std::endl;
            }
            if (result_false != true) {
                std::cerr << "FAIL: %M should be fixed-width when mysql_M_is_month_name=false" << std::endl;
            }
        } catch (const std::runtime_error& e) {
            std::cerr << "Exception: " << e.what() << std::endl;
        }
        return 1;
    }

    // Test 5: Fixed-width formatters should still work
    if (strcmp(test, "test_fixed_width_formatters") == 0) {
        try {
            bool result = containsOnlyFixedWidthMySQLFormatters("%Y-%m-%d", false, false, false);
            if (result == true) {
                return 0; // PASS
            }
            std::cerr << "FAIL: %Y-%m-%d should be fixed-width" << std::endl;
        } catch (const std::runtime_error& e) {
            std::cerr << "Exception: " << e.what() << std::endl;
        }
        return 1;
    }

    std::cerr << "Unknown test: " << test << std::endl;
    return 1;
}
'''
    return harness


def compile_test_harness(harness_code):
    """Compile the C++ test harness."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write(harness_code)
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
    """Extract function from source, create harness, and compile once before all tests."""
    global TEST_EXE
    function_code = extract_function_from_source()
    harness_code = create_test_harness(function_code)
    TEST_EXE = compile_test_harness(harness_code)


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

def test_w_variable_width_with_m_is_month_name_true():
    """
    Test that %W is detected as variable-width when mysql_M_is_month_name=true.

    This is the core bug: when mysql_M_is_month_name=true and
    mysql_e_with_space_padding=false, %W was incorrectly treated as fixed-width.
    """
    passed, stderr = run_test("test_w_with_m_is_month_name_true")
    assert passed, f"Bug not detected: %W should be variable-width when mysql_M_is_month_name=true. stderr: {stderr}"


def test_w_variable_width_with_m_is_month_name_false():
    """
    Test that %W is detected as variable-width when mysql_M_is_month_name=false.
    """
    passed, stderr = run_test("test_w_with_m_is_month_name_false")
    assert passed, f"%W should be variable-width when mysql_M_is_month_name=false. stderr: {stderr}"


def test_w_variable_width_with_various_flags():
    """
    Test that %W is consistently variable-width across all flag combinations.

    The bug manifests when mysql_M_is_month_name=true AND mysql_e_with_space_padding=false.
    After fix, %W should be detected as variable-width regardless of any flags.
    """
    passed, stderr = run_test("test_w_with_various_flags")
    assert passed, f"%W not consistently variable-width across all flag combinations: {stderr}"


# =============================================================================
# Pass-to-pass tests (these should pass before and after the fix)
# =============================================================================

def test_m_behavior_unchanged():
    """
    Test that %M behavior is unchanged: variable-width only when mysql_M_is_month_name=true.

    The fix should not change %M behavior - it should still be variable-width
    only when mysql_M_is_month_name=true.
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

def test_repo_file_structure():
    """Repo's essential files exist and are accessible (pass_to_pass)."""
    repo_path = pathlib.Path(REPO)

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
    repo_path = pathlib.Path(REPO)
    cpp_file = repo_path / "src" / "Functions" / "formatDateTime.cpp"

    try:
        content = cpp_file.read_text(encoding='utf-8')
        assert len(content) > 0, "File should not be empty"
        assert "containsOnlyFixedWidthMySQLFormatters" in content, \
            "Target function not found in file"
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"


def test_repo_python_syntax():
    """Repo's Python CI scripts have valid syntax (pass_to_pass)."""
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
                compile(content, py_file, 'exec')
            except SyntaxError as e:
                assert False, f"Python syntax error in {py_file}: {e}"


def test_repo_git_state():
    """Repo has a clean git state at expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"

    r2 = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r2.returncode == 0, f"Git rev-parse failed: {r2.stderr}"
    current_commit = r2.stdout.strip()
    assert current_commit.startswith("61a4296"), \
        f"Not at expected base commit, got: {current_commit}"


def test_repo_cmake_syntax():
    """Repo's CMakeLists.txt has valid syntax (pass_to_pass)."""
    repo_path = pathlib.Path(REPO)
    cmake_file = repo_path / "CMakeLists.txt"

    content = cmake_file.read_text(encoding='utf-8')

    assert "cmake_minimum_required" in content, "Missing cmake_minimum_required"
    assert "project(" in content, "Missing project declaration"
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_repo_style_shell_scripts():
    """Repo's shell scripts have valid syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh",
        f"{REPO}/ci/jobs/scripts/check_style/various_checks.sh",
        f"{REPO}/ci/jobs/scripts/check_style/check_typos.sh",
        f"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh",
    ]

    for script in scripts:
        if os.path.exists(script):
            r = subprocess.run(
                ["bash", "-n", script],
                capture_output=True, text=True, timeout=60,
            )
            assert r.returncode == 0, f"Shell syntax error in {script}: {r.stderr}"


def test_repo_style_python_scripts():
    """Repo's Python CI scripts have valid syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/ci/jobs/check_style.py",
        f"{REPO}/ci/jobs/fast_test.py",
    ]

    for script in scripts:
        if os.path.exists(script):
            r = subprocess.run(
                ["python3", "-m", "py_compile", script],
                capture_output=True, text=True, timeout=60,
            )
            assert r.returncode == 0, f"Python syntax error in {script}: {r.stderr}"


def test_repo_git_history():
    """Repo's git history is accessible (pass_to_pass)."""
    r = subprocess.run(
        ["git", "diff", "--stat", "HEAD~1"],
        capture_output=True, text=True, cwd=REPO, timeout=60,
    )
    assert r.returncode == 0, f"Git history check failed: {r.stderr}"
    assert len(r.stdout) > 0, "Git diff produced no output"


# =============================================================================
# Behavioral tests that verify the actual source was modified
# These extract and compile the actual source, so they test real behavior
# =============================================================================

def test_source_file_was_modified():
    """
    Verify the source file contains a fix by checking that %W is now
    handled correctly when extracted and compiled.

    This is a behavioral test - it compiles the actual source and verifies
    the function returns correct results.
    """
    # This is implicitly tested by the behavioral tests above since they
    # extract and compile the actual source. But we make it explicit here.
    function_code = extract_function_from_source()
    harness_code = create_test_harness(function_code)
    exe = compile_test_harness(harness_code)

    # Run a test that would fail with buggy code
    result = subprocess.run(
        [exe, "test_w_with_m_is_month_name_true"],
        capture_output=True, text=True, timeout=10
    )
    os.unlink(exe)

    assert result.returncode == 0, \
        f"Source code bug not fixed: %W still not variable-width when mysql_M_is_month_name=true"


# =============================================================================
# NEW: Repo CI/CD tests using actual CI commands (subprocess.run)
# These tests run real CI tools from the repository
# =============================================================================

def test_repo_shellcheck_ci_scripts():
    """Repo CI shell scripts pass shellcheck (pass_to_pass)."""
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True, text=True, timeout=120,
    )
    script = f"{REPO}/ci/jobs/scripts/check_style/check_submodules.sh"
    if os.path.exists(script):
        r = subprocess.run(
            ["shellcheck", "-x", script],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"shellcheck failed for {script}:\n{r.stdout}\n{r.stderr}"


def test_repo_python_ci_scripts_py_compile():
    """Repo Python CI scripts pass py_compile syntax check (pass_to_pass)."""
    scripts = [
        f"{REPO}/ci/jobs/check_style.py",
        f"{REPO}/ci/jobs/fast_test.py",
        f"{REPO}/ci/jobs/functional_tests.py",
    ]
    for script in scripts:
        if os.path.exists(script):
            r = subprocess.run(
                ["python3", "-m", "py_compile", script],
                capture_output=True, text=True, timeout=60,
            )
            assert r.returncode == 0, f"Python syntax error in {script}:\n{r.stderr}"


def test_repo_clang_format_check_cpp():
    """Repo formatDateTime.cpp can be processed by clang-format (pass_to_pass)."""
    subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=120,
    )
    subprocess.run(
        ["apt-get", "install", "-y", "-qq", "clang-format"],
        capture_output=True, text=True, timeout=120,
    )
    target_file = f"{REPO}/src/Functions/formatDateTime.cpp"
    assert os.path.exists(target_file), f"Target file not found: {target_file}"

    r = subprocess.run(
        ["clang-format", "--dry-run", target_file],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode in [0, 1], f"clang-format failed to parse file: {r.stderr}"
    assert "error:" not in r.stderr.lower() or "clang-format-violations" in r.stderr.lower(), \
        f"clang-format found parsing errors: {r.stderr}"
ENDOFPYTHON
echo "Done"
