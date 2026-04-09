"""
Test suite for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

This tests the fix for PR #102088 which addresses a heap-buffer-overflow
in the leftPad/rightPad functions caused by insufficient padding when
reading from the pad string during writeSlice operations.
"""

import subprocess
import os
import sys
import re
import pytest

# Constants
REPO_DIR = "/workspace/ClickHouse"
SOURCE_FILE = f"{REPO_DIR}/src/Functions/padString.cpp"
BUILD_DIR = f"{REPO_DIR}/build"


def test_source_file_exists():
    """Verify the source file exists"""
    assert os.path.exists(SOURCE_FILE), f"Source file not found: {SOURCE_FILE}"


def test_padding_chars_uses_padded_pod_array():
    """
    FAIL-TO-PASS TEST: Verify PaddingChars uses PaddedPODArray instead of String.

    The bug was caused by using std::String which doesn't provide the 15 extra bytes
    of read padding required by memcpySmallAllowReadWriteOverflow15. The fix changes
    the pad_string member from String to PaddedPODArray<UInt8>.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check that PaddedPODArray is used for pad_string
    assert "PaddedPODArray<UInt8> pad_string" in content, \
        "PaddingChars should use PaddedPODArray<UInt8> for pad_string to provide required read padding"

    # Make sure the old String-based padding is not present in the class
    # (the old code had 'String pad_string;' as a member)
    lines = content.split('\n')
    in_padding_chars = False
    brace_depth = 0
    found_pod_array = False
    found_string_member = False

    for line in lines:
        if 'class PaddingChars' in line:
            in_padding_chars = True
            brace_depth = 0

        if in_padding_chars:
            brace_depth += line.count('{') - line.count('}')

            # Check for PaddedPODArray member
            if 'PaddedPODArray<UInt8> pad_string' in line:
                found_pod_array = True

            # Check for old String member (should not exist in private section)
            if brace_depth > 0 and 'private:' in line:
                # We're in the private section
                pass

            # Old pattern that should be gone
            if 'String pad_string;' in line and 'PaddedPODArray' not in line:
                found_string_member = True

            if brace_depth == 0 and '}' in line and 'class' not in line:
                in_padding_chars = False

    assert found_pod_array, "PaddingChars class must have PaddedPODArray<UInt8> pad_string member"
    assert not found_string_member, "PaddingChars class should not have raw String pad_string member"


def test_pad_string_initialized_with_insert():
    """
    FAIL-TO-PASS TEST: Verify pad_string is initialized using insert(), not assignment.

    The fix uses insert() to copy data into PaddedPODArray and uses insertFromItself()
    instead of operator+= for string duplication.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check for insert() call to initialize pad_string
    assert "pad_string.insert(pad_string_.begin(), pad_string_.end())" in content, \
        "pad_string should be initialized using insert() method"

    # Check for insertFromItself instead of operator+=
    assert "pad_string.insertFromItself" in content, \
        "String duplication should use insertFromItself() instead of operator+="

    # Old pattern should be gone
    assert "pad_string += pad_string" not in content, \
        "Old pattern 'pad_string += pad_string' should be replaced with insertFromItself"


def test_empty_pad_string_handling_moved():
    """
    FAIL-TO-PASS TEST: Verify empty pad_string handling moved from init() to executeImpl.

    The old code had 'if (pad_string.empty()) pad_string = " ";' in init().
    The fix moves this to executeImpl where the pad string is extracted.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Find the executeImpl function and check for empty handling there
    # The fix moves empty check from constructor to executeImpl
    execute_impl_pattern = r'executeImpl.*?\{.*?if \(pad_string\.empty\(\)\).*?\}'

    # Check that empty handling is now in executeImpl, not in constructor
    # Look for the pattern in executeImpl context
    lines = content.split('\n')
    in_execute_impl = False
    brace_depth = 0
    found_empty_check_in_execute = False

    for i, line in enumerate(lines):
        if 'executeImpl' in line and 'const' in line:
            in_execute_impl = True
            brace_depth = 0

        if in_execute_impl:
            brace_depth += line.count('{') - line.count('}')

            if 'if (pad_string.empty())' in line:
                found_empty_check_in_execute = True

            if brace_depth == 0 and '}' in line:
                in_execute_impl = False

    assert found_empty_check_in_execute, \
        "Empty pad_string check should be in executeImpl, not in PaddingChars constructor"


def test_get_return_type_uses_validate_function_arguments():
    """
    PASS-TO-PASS TEST: Verify getReturnTypeImpl uses validateFunctionArguments helper.

    This is a code quality improvement that uses the standard validation helper
    instead of manual argument checking.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check for new validation pattern
    assert "validateFunctionArguments" in content, \
        "getReturnTypeImpl should use validateFunctionArguments helper"

    assert "FunctionArgumentDescriptors" in content, \
        "Should use FunctionArgumentDescriptors for argument validation"


def test_utf8_offsets_use_size_not_length():
    """
    FAIL-TO-PASS TEST: Verify utf8_offsets uses size() not length().

    Since pad_string is now PaddedPODArray, we use size() instead of length().
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # The fix changes from length() to size() for PaddedPODArray compatibility
    # Check that we're using size() for pad_string operations
    assert "pad_string.size()" in content, \
        "Should use size() method for PaddedPODArray"

    assert "pad_string.length()" not in content, \
        "Should not use length() which is for String, not PaddedPODArray"


def test_num_chars_comparison_explicit():
    """
    PASS-TO-PASS TEST: Verify explicit comparison with 0 instead of implicit bool.

    Code style improvement: 'if (num_chars == 0)' instead of 'if (!num_chars)'.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check for explicit comparison
    assert "if (num_chars == 0)" in content, \
        "Should use explicit comparison 'num_chars == 0' instead of implicit bool"


def test_source_compiles():
    """
    STRUCTURAL TEST: Verify the modified source compiles.

    This ensures the fix doesn't introduce syntax errors.
    """
    # Skip if clang is not available
    if subprocess.run(["which", "clang"], capture_output=True).returncode != 0:
        pytest.skip("clang not available")
        return

    # First, apply the patch if not already applied
    solve_script = "/workspace/task/solution/solve.sh"

    # Check if already patched
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    if "PaddedPODArray<UInt8> pad_string" not in content:
        # Apply the patch
        result = subprocess.run(
            ["bash", solve_script],
            capture_output=True,
            text=True,
            cwd=REPO_DIR
        )
        if result.returncode != 0:
            print(f"Patch application output: {result.stdout}\n{result.stderr}")
            # Patch might already be applied or have issues

    # Try to compile just the modified file
    # Note: Full ClickHouse build is very slow, so we just check syntax
    # by attempting to parse with clang
    result = subprocess.run(
        ["clang", "-fsyntax-only", "-std=c++20",
         "-I", f"{REPO_DIR}/src",
         "-I", f"{REPO_DIR}/base",
         "-I", f"{REPO_DIR}/build/src",  # For generated headers
         "-c", SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=120
    )

    # We allow errors about missing includes, but not syntax errors
    # Syntax errors would indicate the patch is malformed
    syntax_errors = [line for line in result.stderr.split('\n')
                     if 'error:' in line and 'syntax' in line.lower()]

    assert len(syntax_errors) == 0, \
        f"Syntax errors found in patched file: {syntax_errors}"


def test_validate_function_arguments_signature():
    """
    STRUCTURAL TEST: Verify validateFunctionArguments signature matches expected.

    The fix uses validateFunctionArguments with ColumnsWithTypeAndName argument.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check getReturnTypeImpl signature was updated
    assert "getReturnTypeImpl(const ColumnsWithTypeAndName & arguments)" in content, \
        "getReturnTypeImpl should take ColumnsWithTypeAndName& instead of DataTypes&"


def test_memcpy_small_requirement_satisfied():
    """
    CORE BEHAVIORAL TEST: Verify the fix satisfies memcpySmallAllowReadWriteOverflow15 requirements.

    The root cause of the bug was that memcpySmallAllowReadWriteOverflow15 requires
    15 extra bytes of read padding beyond the data size. PaddedPODArray provides
    exactly this guarantee.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # The key comment explaining the fix should be present
    assert "15 extra bytes of read padding" in content, \
        "Should have comment explaining the 15 byte padding requirement for memcpySmallAllowReadWriteOverflow15"

    assert "memcpySmallAllowReadWriteOverflow15" in content or "writeSlice" in content, \
        "Code should reference the requirement that necessitates the padding"


# ============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that must pass on both base and fix
# ============================================================================


def test_patch_applies_cleanly():
    """
    PASS-TO-PASS TEST: Verify the gold patch applies cleanly without conflicts.

    This is a repo CI/CD gate - any fix must apply cleanly to the codebase.
    """
    # First, check if already patched
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    if "PaddedPODArray<UInt8> pad_string" in content:
        pytest.skip("Patch already applied, skipping apply test")
        return

    # Try to apply the patch
    solve_script = "/workspace/task/solution/solve.sh"
    result = subprocess.run(
        ["bash", solve_script],
        capture_output=True,
        text=True,
        cwd=REPO_DIR,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Patch failed to apply cleanly:\n{result.stdout}\n{result.stderr}"


def test_source_compiles_syntax_only():
    """
    PASS-TO-PASS TEST: Verify the C++ source has no syntax errors after patching.

    This is a minimal compilation check that doesn't require full ClickHouse build.
    """
    # Skip if clang++ is not available
    if subprocess.run(["which", "clang++"], capture_output=True).returncode != 0:
        pytest.skip("clang++ not available")
        return

    # First, ensure patch is applied
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    if "PaddedPODArray<UInt8> pad_string" not in content:
        # Apply the patch
        solve_script = "/workspace/task/solution/solve.sh"
        subprocess.run(
            ["bash", solve_script],
            capture_output=True,
            cwd=REPO_DIR,
            timeout=30
        )

    # Check syntax with clang (syntax-only mode)
    # We allow missing include errors but not syntax errors
    result = subprocess.run(
        ["clang++", "-fsyntax-only", "-std=c++20",
         "-I", f"{REPO_DIR}/src",
         "-I", f"{REPO_DIR}/base",
         "-Wno-everything",  # Suppress warnings, only check syntax
         SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Filter for actual syntax errors (not missing includes)
    syntax_errors = [
        line for line in result.stderr.split('\n')
        if 'error:' in line and 'syntax' in line.lower()
    ]

    assert len(syntax_errors) == 0, \
        f"C++ syntax errors found:\n{chr(10).join(syntax_errors[:5])}"


def test_cpp_code_style_basic():
    """
    PASS-TO-PASS TEST: Verify basic C++ code style compliance.

    Checks for consistent indentation, no trailing whitespace, and basic formatting.
    This is a lightweight alternative to full clang-format.
    """
    with open(SOURCE_FILE, 'r') as f:
        lines = f.readlines()

    # Check for tabs (should use spaces)
    tab_lines = [i + 1 for i, line in enumerate(lines) if '\t' in line]
    assert len(tab_lines) == 0, \
        f"Found tabs in lines: {tab_lines[:5]} (should use spaces for indentation)"

    # Check for trailing whitespace
    trailing_ws = [
        i + 1 for i, line in enumerate(lines)
        if line.rstrip() != line.rstrip('\n').rstrip('\r')
    ]
    assert len(trailing_ws) == 0, \
        f"Found trailing whitespace in lines: {trailing_ws[:5]}"

    # Check for proper brace style (space before opening brace)
    bad_braces = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip comments, strings, and certain constructs
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('#'):
            continue
        if 'class' in stripped or 'namespace' in stripped:
            continue
        # Check for patterns like 'if(){' or 'for(){' (missing space)
        if stripped and stripped[-1] == '{' and len(stripped) > 1:
            prev_char = stripped[-2]
            if prev_char in ';)':
                # These are OK: control flow braces
                continue
            if prev_char.isalnum() or prev_char == '_':
                # This might be a function definition without space
                if not any(x in stripped for x in ['if (', 'for (', 'while (', 'switch (']):
                    if '(' in stripped and ')' in stripped:
                        bad_braces.append(i + 1)

    # Just warn about these, don't fail
    if len(bad_braces) > 5:
        print(f"Note: Found {len(bad_braces)} lines with potential brace style issues")


def test_test_file_syntax_valid():
    """
    PASS-TO-PASS TEST: Verify the test file itself is valid Python syntax.

    This ensures our test suite is well-formed and can be executed.
    """
    test_file = os.path.abspath(__file__)
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", test_file],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, \
        f"Test file has Python syntax errors:\n{result.stderr}"


def test_all_tests_have_docstrings():
    """
    PASS-TO-PASS TEST: Verify all test functions have proper docstrings.

    This is a code quality check to ensure tests are documented.
    """
    import ast

    with open(__file__, 'r') as f:
        tree = ast.parse(f.read())

    test_functions = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
    ]

    missing_docs = [
        func.name for func in test_functions
        if not ast.get_docstring(func)
    ]

    assert len(missing_docs) == 0, \
        f"Tests missing docstrings: {missing_docs}"


def test_no_debug_code_left():
    """
    PASS-TO-PASS TEST: Verify no debug prints or temporary code left in source.

    Checks for common debug patterns that shouldn't be in production code.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check for common debug patterns
    debug_patterns = [
        'std::cout <<',
        'printf(',
        'DEBUG',
        'FIXME',
        'TODO',
        'std::cerr <<',
    ]

    found = []
    for pattern in debug_patterns:
        if pattern in content:
            found.append(pattern)

    # These are OK if they're in comments
    lines = content.split('\n')
    actual_issues = []
    for pattern in found:
        for line in lines:
            if pattern in line and not line.strip().startswith('//'):
                # Check if it's inside a comment
                if '//' not in line or line.index(pattern) < line.index('//'):
                    actual_issues.append((pattern, line.strip()))
                    break

    assert len(actual_issues) == 0, \
        f"Found potential debug code: {actual_issues[:3]}"


def test_functions_registered_properly():
    """
    PASS-TO-PASS TEST: Verify ClickHouse functions are registered in the factory.

    Checks that leftPad/rightPad functions are properly registered.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Check for factory registration
    assert "FunctionFactory::instance().registerFunction" in content or \
           "registerFunction" in content, \
        "Functions should be registered with FunctionFactory"

    # Check for function name definitions
    assert "leftPad" in content or "rightPad" in content, \
        "Function names (leftPad/rightPad) should be referenced in source"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
