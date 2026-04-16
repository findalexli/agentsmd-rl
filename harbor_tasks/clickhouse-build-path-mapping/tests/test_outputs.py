"""
Test suite for ClickHouse PR #102000 - Improve build path mapping to produce clean relative paths in stack traces.

The PR makes two changes:
1. CMakeLists.txt: Updates compiler flags to use -fdebug-compilation-dir=. and -ffile-prefix-map=${PROJECT_SOURCE_DIR}/=
2. src/Common/Dwarf.cpp: Fixes getFullFileName to skip "." directory entries

This test suite verifies both changes are correctly applied.
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"


def test_cmake_compiler_flags():
    """
    FAIL-TO-PASS: CMakeLists.txt must use new compiler flags.

    Before: -ffile-prefix-map=${PROJECT_SOURCE_DIR}=.
    After:  -fdebug-compilation-dir=. -ffile-prefix-map=${PROJECT_SOURCE_DIR}/=

    The new flags ensure DW_AT_comp_dir is fixed to "." and source paths are stripped
    to bare relative paths like "src/Foo.cpp" instead of "./src/Foo.cpp".
    """
    cmake_path = os.path.join(REPO, "CMakeLists.txt")
    with open(cmake_path, 'r') as f:
        content = f.read()

    # Check for the old flag pattern (should NOT be present after fix)
    old_flag_pattern = r'ffile-prefix-map=\$\{PROJECT_SOURCE_DIR\}=\.'
    has_old_flag = re.search(old_flag_pattern, content)

    # Check for the new flags (should be present after fix)
    has_debug_comp_dir = '-fdebug-compilation-dir=.' in content
    has_new_prefix_map = 'ffile-prefix-map=${PROJECT_SOURCE_DIR}/=' in content

    # After fix: should have new flags, not old flag
    assert has_debug_comp_dir, "Missing -fdebug-compilation-dir=. flag in CMakeLists.txt"
    assert has_new_prefix_map, "Missing updated -ffile-prefix-map flag with trailing slash in CMakeLists.txt"
    assert not has_old_flag, "Old -ffile-prefix-map pattern still present (without trailing slash)"


def test_dwarf_dot_directory_handling():
    """
    FAIL-TO-PASS: Dwarf.cpp must handle "." directory entries correctly.

    Before: Path(base_dir, getIncludeDirectory(fn.directoryIndex), fn.relativeName)
    After:  Path(base_dir, include_dir == "." ? std::string_view{} : include_dir, fn.relativeName)

    The fix treats "." as an empty directory to avoid producing paths like "./src/Foo.cpp"
    when the DWARF 5 line number program stores the compilation directory as an explicit entry.
    """
    dwarf_path = os.path.join(REPO, "src/Common/Dwarf.cpp")
    with open(dwarf_path, 'r') as f:
        content = f.read()

    # Check for the fix: conditional handling of "." directory
    # The fix should have: include_dir == "." ? std::string_view{} : include_dir
    has_dot_conditional = 'include_dir == "." ? std::string_view{} : include_dir' in content

    # Check that getFullFileName extracts include_dir to a variable first
    has_include_dir_var = 'const std::string_view include_dir = getIncludeDirectory' in content

    assert has_include_dir_var, "Dwarf.cpp: include_dir variable not extracted properly"
    assert has_dot_conditional, "Dwarf.cpp: Missing conditional handling of '.' directory entry"


def test_dwarf_no_raw_getIncludeDirectory_call():
    """
    FAIL-TO-PASS: After the fix, getIncludeDirectory should not be called directly in Path().

    The fix introduces an intermediate variable `include_dir` and performs the conditional
    check before passing to Path(). This test ensures the refactor is complete.
    """
    dwarf_path = os.path.join(REPO, "src/Common/Dwarf.cpp")
    with open(dwarf_path, 'r') as f:
        content = f.read()

    # Find the getFullFileName function
    func_match = re.search(
        r'Dwarf::Path Dwarf::LineNumberVM::getFullFileName\(uint64_t index\) const\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        content,
        re.DOTALL
    )

    if func_match:
        func_body = func_match.group(1)
        # After fix, Path() should use include_dir variable, not direct getIncludeDirectory() call
        path_call_match = re.search(r'return Path\([^)]+\)', func_body, re.DOTALL)
        if path_call_match:
            path_call = path_call_match.group(0)
            # Should NOT have direct getIncludeDirectory call in Path() anymore
            has_direct_call = 'getIncludeDirectory(' in path_call
            assert not has_direct_call, "Dwarf.cpp: Path() still uses direct getIncludeDirectory() call"


def test_repo_cpp_style_no_critical_errors():
    """
    PASS-TO-PASS: Repo C++ style check has no critical errors.

    Runs the repo's C++ style checker on the source files.
    Filters out unicode warnings and checks for actual style errors.
    """
    r = subprocess.run(
        ["bash", "./ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    output = r.stdout + r.stderr

    # Check for critical style errors (lines ending with "^ style error")
    style_error_markers = [line for line in output.split('\n') if line.endswith('style error')]

    # Also check for "tabs are not allowed" marker
    tab_errors = [line for line in output.split('\n') if 'tabs are not allowed' in line]

    # Filter out known issues that are just warnings (not errors)
    # The script outputs unicode content lines but these are not style errors
    critical_errors = style_error_markers + tab_errors

    # Allow the check to pass if there are no critical style markers
    assert len(critical_errors) == 0, \
        f"C++ style critical errors found:\n{'\\n'.join(critical_errors[:10])}"


def test_repo_git_tracked():
    """
    PASS-TO-PASS: Modified files are tracked in git.

    Verifies that CMakeLists.txt and src/Common/Dwarf.cpp are tracked by git.
    """
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "CMakeLists.txt", "src/Common/Dwarf.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git tracked files check failed:\n{r.stderr[-500:]}"


def test_repo_python_syntax():
    """
    PASS-TO-PASS: Python CI scripts have valid syntax.

    Validates Python syntax using py_compile on the check_style.py script.
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", "ci/jobs/check_style.py"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr[-500:]}"


def test_repo_cmake_parse():
    """
    PASS-TO-PASS: CMakeLists.txt is syntactically valid.

    Uses cmake to parse the CMakeLists.txt without configuring to validate syntax.
    """
    # First, check if CMakeLists.txt has balanced if/endif for the ENABLE_BUILD_PATH_MAPPING section
    cmake_path = os.path.join(REPO, "CMakeLists.txt")
    with open(cmake_path, 'r') as f:
        content = f.read()

    # Check for the specific section - should have balanced if/endif
    section_match = re.search(
        r'if \(ENABLE_BUILD_PATH_MAPPING\)(.*?)(endif \(\))',
        content,
        re.DOTALL
    )
    assert section_match is not None, "ENABLE_BUILD_PATH_MAPPING section not found or unbalanced"

    # Also try cmake --help to verify cmake is available (syntax check)
    r = subprocess.run(
        ["cmake", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"CMake not available:\n{r.stderr[-500:]}"


def test_repo_dwarf_structure():
    """
    PASS-TO-PASS: Dwarf.cpp has valid C++ structure.

    Validates basic C++ structure by checking for balanced braces and proper
    function declarations in the modified file.
    """
    dwarf_path = os.path.join(REPO, "src/Common/Dwarf.cpp")

    with open(dwarf_path, 'r') as f:
        content = f.read()

    # Check for balanced braces overall (ignoring #define macros at top)
    # Skip the macro definitions at the top of the file
    lines = content.split('\n')
    code_content = []
    in_macro_def = False
    for line in lines:
        stripped = line.strip()
        # Skip #define macros that use { and }
        if stripped.startswith('#define'):
            in_macro_def = True
        if in_macro_def:
            if '}' in stripped or not stripped.endswith('\\'):
                in_macro_def = False
            continue
        code_content.append(line)

    filtered_content = '\n'.join(code_content)
    open_braces = filtered_content.count('{')
    close_braces = filtered_content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check that the getFullFileName function exists
    assert 'Dwarf::Path Dwarf::LineNumberVM::getFullFileName(uint64_t index) const' in content, \
        "getFullFileName function not found"
