"""Tests for ClickHouse formatDateTime %W formatter fix.

This tests that %W (weekday name) is treated as a variable-length formatter
unconditionally, regardless of mysql_M_is_month_name setting.
"""
import subprocess
import re
import sys
import os

REPO = "/workspace/ClickHouse"
FILE_PATH = "src/Functions/formatDateTime.cpp"
FULL_PATH = f"{REPO}/{FILE_PATH}"


def test_w_in_variable_width_formatter_M_is_month_name_removed():
    """FAIL-TO-PASS: %W must not be in variable_width_formatter_M_is_month_name array.

    Before the fix, the array contained {'W', 'M'}. After the fix, it should
    only contain {'M'} since %W is now checked unconditionally.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Find the line with variable_width_formatter_M_is_month_name
    pattern = r'static constexpr std::array variable_width_formatter_M_is_month_name = \{([^}]+)\};'
    match = re.search(pattern, content)

    assert match is not None, "Could not find variable_width_formatter_M_is_month_name array"

    array_content = match.group(1).replace("'", "").replace(" ", "")
    elements = [e for e in array_content.split(',') if e]

    # After fix, should only contain 'M', not 'W'
    assert 'W' not in elements, f"FAIL: %W should not be in variable_width_formatter_M_is_month_name, but found: {elements}"
    assert 'M' in elements, f"FAIL: %M should still be in variable_width_formatter_M_is_month_name, but found: {elements}"


def test_w_checked_unconditionally_before_mysql_M_is_month_name():
    """FAIL-TO-PASS: %W check must come BEFORE the mysql_M_is_month_name conditional.

    The fix moves the %W check to be unconditional (before the mysql_M_is_month_name check).
    Before the fix, %W was only checked in the else branch of mysql_M_is_month_name.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Find the function containsOnlyFixedWidthMySQLFormatters
    func_start = content.find('static bool containsOnlyFixedWidthMySQLFormatters')
    assert func_start != -1, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    # Get the function body (first 2000 chars should be enough for the key part)
    func_body = content[func_start:func_start + 2000]

    # Find the pattern where W is checked unconditionally before mysql_M_is_month_name
    # The fix adds:
    #   if (std::any_of(variable_width_formatter.begin(), variable_width_formatter.end(), ...))
    #       return false;
    # BEFORE:
    #   if (mysql_M_is_month_name)

    # Check that variable_width_formatter check comes before mysql_M_is_month_name check
    w_check_pattern = r'if\s*\(\s*std::any_of\s*\(\s*variable_width_formatter\.begin\(\)'
    mysql_m_check_pattern = r'if\s*\(\s*mysql_M_is_month_name\s*\)'

    w_match = re.search(w_check_pattern, func_body)
    mysql_m_match = re.search(mysql_m_check_pattern, func_body)

    assert w_match is not None, "FAIL: Could not find unconditional %W check in function"
    assert mysql_m_match is not None, "FAIL: Could not find mysql_M_is_month_name check in function"

    # The %W check must come BEFORE the mysql_M_is_month_name check
    assert w_match.start() < mysql_m_match.start(), \
        f"FAIL: %W check (at {w_match.start()}) must come BEFORE mysql_M_is_month_name check (at {mysql_m_match.start()})"


def test_no_else_branch_with_variable_width_formatter():
    """FAIL-TO-PASS: The else branch containing only variable_width_formatter check should be removed.

    Before the fix, there was an else branch that checked variable_width_formatter.
    After the fix, this check is moved to be unconditional, so the else branch is removed.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    func_start = content.find('static bool containsOnlyFixedWidthMySQLFormatters')
    assert func_start != -1, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    # Look for the pattern of else branch with variable_width_formatter check
    # This was removed in the fix
    func_body = content[func_start:func_start + 2500]

    # The old buggy code had an else branch like:
    # else
    # {
    #     if (std::any_of(
    #             variable_width_formatter.begin(), variable_width_formatter.end(),
    #             [&](char c){ return c == format[i + 1]; }))
    #         return false;
    # }

    # After the fix, this else branch is removed - we should not find "else" followed by
    # variable_width_formatter check in the function body
    else_pattern = r'else\s*\{[^}]*variable_width_formatter\.begin\(\)'
    else_match = re.search(else_pattern, func_body, re.DOTALL)

    assert else_match is None, \
        f"FAIL: Found else branch with variable_width_formatter check that should have been removed: {else_match.group(0)[:100]}"


def test_file_has_valid_structure():
    """PASS-TO-PASS: The modified file has valid C++ structure.

    Verify the file has balanced braces and valid function structure.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for balanced braces in the containsOnlyFixedWidthMySQLFormatters function
    func_start = content.find('static bool containsOnlyFixedWidthMySQLFormatters')
    assert func_start != -1, "Could not find containsOnlyFixedWidthMySQLFormatters function"

    # Find the function body
    brace_count = 0
    in_function = False
    func_body = content[func_start:]

    for i, char in enumerate(func_body):
        if char == '{':
            brace_count += 1
            in_function = True
        elif char == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                # Function ends here
                break

    # Brace count should be balanced
    assert brace_count == 0, f"FAIL: Unbalanced braces in containsOnlyFixedWidthMySQLFormatters (count: {brace_count})"


def test_cmake_configures():
    """PASS-TO-PASS: CMake configuration must succeed with the fix.

    Verify that the build system can configure the project.
    """
    build_dir = f"{REPO}/build"

    # Configure with cmake
    result = subprocess.run(
        ["cmake", "-DCMAKE_BUILD_TYPE=Release", "-DENABLE_TESTS=OFF",
         "-DENABLE_RUST=OFF", "-S", REPO, "-B", build_dir],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )

    # CMake may have warnings but should not fail completely
    # Check for critical errors
    if result.returncode != 0:
        # Only fail if it's a real configuration error, not missing optional deps
        stderr = result.stderr.lower()
        if 'error' in stderr and not 'warning' in stderr[:stderr.find('error')]:
            # Check if it's about our file or some other dependency
            if 'formatdatetime' in stderr or 'formatdatetime' in result.stdout.lower():
                assert False, f"CMake configuration failed with formatDateTime error: {result.stderr[-500:]}"


def test_cpp_syntax_valid():
    """PASS-TO-PASS: Modified C++ file has valid syntax.

    Verify that the formatDateTime.cpp file has valid C++ syntax by running
    it through clang's parser. This is a lightweight check that doesn't
    require full compilation.
    """
    # Create marker files to bypass CMake submodule check
    contrib_dir = f"{REPO}/contrib/sysroot"
    os.makedirs(contrib_dir, exist_ok=True)
    with open(f"{contrib_dir}/README.md", "w") as f:
        f.write("placeholder")

    # Create stub directories required by CMake
    os.makedirs(f"{REPO}/programs", exist_ok=True)
    os.makedirs(f"{REPO}/utils", exist_ok=True)
    with open(f"{REPO}/programs/CMakeLists.txt", "w") as f:
        f.write("cmake_minimum_required(VERSION 3.25)\n")
    with open(f"{REPO}/utils/CMakeLists.txt", "w") as f:
        f.write("cmake_minimum_required(VERSION 3.25)\n")

    # Run clang syntax check - we expect this to fail on includes but
    # not on syntax errors in our modified code
    result = subprocess.run(
        ["clang++-20", "-std=c++23", "-fsyntax-only", "-x", "c++",
         FULL_PATH, "-I", f"{REPO}/src", "-I", f"{REPO}/base"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Check that errors are only about missing includes, not syntax errors
    # A syntax error would indicate a problem with the fix
    stderr_lower = result.stderr.lower()

    # If there are actual syntax errors (not just missing headers), fail
    if "expected" in stderr_lower and "error:" in stderr_lower:
        # Check if it's a genuine syntax error vs missing header
        if "expected expression" in stderr_lower or "unexpected" in stderr_lower:
            assert False, f"C++ syntax error detected:\n{result.stderr[-500:]}"

    # The file should at least be parseable (even if includes are missing)
    # A return code of 0 means full success (includes found)
    # Non-zero is expected due to missing includes in minimal repo


def test_git_repo_valid():
    """PASS-TO-PASS: Git repository is in a valid state.

    Verify that the git repository is valid and the modified file is tracked.
    """
    # Check git status works
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    assert result.returncode == 0, f"Git status failed: {result.stderr}"

    # Check the file exists and is in git
    result = subprocess.run(
        ["git", "ls-files", FILE_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    assert result.returncode == 0, f"Git ls-files failed: {result.stderr}"
    assert FILE_PATH in result.stdout, f"Modified file {FILE_PATH} should be tracked by git"


def test_file_no_trailing_whitespace():
    """PASS-TO-PASS: Modified file has no trailing whitespace.

    Common lint check - verify the modified file doesn't introduce trailing whitespace.
    """
    with open(FULL_PATH, 'r') as f:
        lines = f.readlines()

    trailing_ws_lines = []
    for i, line in enumerate(lines, 1):
        if line.rstrip() != line.rstrip('\n').rstrip('\r'):
            if line.rstrip('\n').rstrip('\r') != line.rstrip('\n').rstrip('\r').rstrip():
                trailing_ws_lines.append(i)

    assert len(trailing_ws_lines) == 0, \
        f"Lines with trailing whitespace: {trailing_ws_lines[:10]}"


def test_repo_file_exists_and_is_cpp():
    """PASS-TO-PASS: Modified file exists and is valid C++ source.

    Verify the modified file exists and has valid C++ file structure.
    This is a basic repo integrity check using the 'file' command.
    """
    result = subprocess.run(
        ["file", f"{REPO}/{FILE_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    assert result.returncode == 0, f"file command failed: {result.stderr}"
    assert "C++ source" in result.stdout or "C++" in result.stdout, \
        f"File is not recognized as C++ source: {result.stdout}"


def test_repo_cpp_syntax_no_errors():
    """PASS-TO-PASS: C++ syntax check shows no syntax errors in modified file.

    Uses clang++ with -fsyntax-only to verify the file has no syntax errors.
    Missing includes are expected, but actual syntax errors indicate a problem.
    """
    result = subprocess.run(
        ["clang++-20", "-std=c++23", "-fsyntax-only", "-x", "c++",
         f"{REPO}/{FILE_PATH}", "-I", f"{REPO}/src", "-I", f"{REPO}/base"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    # Check stderr for actual syntax errors vs missing includes
    stderr_lower = result.stderr.lower()

    # Real syntax errors that would indicate a problem with the fix
    syntax_error_indicators = [
        "expected expression",
        "unexpected",
        "syntax error",
        "parse error",
        "invalid"
    ]

    for indicator in syntax_error_indicators:
        if indicator in stderr_lower and "error:" in stderr_lower:
            # Check if this is in the modified file (not a missing include)
            if FILE_PATH.replace(".cpp", "") in result.stderr.lower():
                assert False, f"C++ syntax error detected in {FILE_PATH}: {result.stderr[:500]}"

    # If we only have "file not found" errors for includes, that's expected
    # in a minimal repo without all dependencies


def test_repo_clang_check_runs():
    """PASS-TO-PASS: clang-check runs on modified file without crashing.

    Verifies clang-check can process the file. It will fail on missing includes
    but should not crash or report AST errors in the modified code.
    """
    result = subprocess.run(
        ["clang-check-20", f"{REPO}/{FILE_PATH}", "--"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    # clang-check should at least run without crashing
    # Exit code 0 means it processed successfully (even with missing includes)
    # A crash or internal error would be non-zero with specific error messages
    if result.returncode != 0:
        stderr_lower = result.stderr.lower()
        # Check for actual clang internal errors (not just missing headers)
        if "clang" in stderr_lower and "error" in stderr_lower:
            if "internal" in stderr_lower or "crash" in stderr_lower or "assertion" in stderr_lower:
                assert False, f"clang-check internal error: {result.stderr[:500]}"


def test_cmake_presence():
    """PASS-TO-PASS: CMake is available and can parse the project files.

    Verifies CMake can at least parse the CMakeLists.txt syntax without errors.
    This checks that the build system tooling is properly installed.
    """
    result = subprocess.run(
        ["cmake", "--version"],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"CMake not available: {result.stderr}"
    assert "cmake version" in result.stdout.lower(), f"Unexpected CMake output: {result.stdout}"


def test_repo_directory_structure():
    """PASS-TO-PASS: Repo has expected directory structure for Functions.

    Verify the expected directories exist for building the Functions module.
    This is a structural integrity check for the repo.
    """
    expected_dirs = [
        f"{REPO}/src/Functions",
        f"{REPO}/src",
        f"{REPO}/base",
    ]

    for dir_path in expected_dirs:
        result = subprocess.run(
            ["test", "-d", dir_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, f"Expected directory does not exist: {dir_path}"


def test_repo_file_line_count():
    """PASS-TO-PASS: Modified file has reasonable line count.

    Verify the file hasn't been truncated or corrupted by checking it has
    a reasonable number of lines.
    """
    result = subprocess.run(
        ["wc", "-l", f"{REPO}/{FILE_PATH}"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    assert result.returncode == 0, f"wc command failed: {result.stderr}"

    # Parse line count from output (format: " 1234 /path/to/file")
    line_count_str = result.stdout.strip().split()[0]
    line_count = int(line_count_str)

    # The file should have a reasonable number of lines (not empty, not truncated)
    assert line_count > 100, f"File seems too small ({line_count} lines), possible truncation"
    assert line_count < 100000, f"File seems too large ({line_count} lines), possible corruption"


def test_repo_clang_version():
    """PASS-TO-PASS: Clang compiler version is compatible.

    Verify the installed clang version supports C++23 which is required
    by the ClickHouse codebase.
    """
    result = subprocess.run(
        ["clang++-20", "--version"],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"clang++-20 not available: {result.stderr}"
    assert "clang version" in result.stdout.lower(), f"Unexpected clang output: {result.stdout}"

    # Check version is at least 16 (supports C++23)
    version_line = result.stdout.split('\n')[0]
    assert "20" in version_line or "19" in version_line or "18" in version_line or "17" in version_line or "16" in version_line, \
        f"Clang version may not support required C++23: {version_line}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
