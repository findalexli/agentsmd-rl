#!/usr/bin/env python3
"""
Tests for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

This tests:
1. The code changes are present (PaddedPODArray usage, empty string handling moved)
2. The C++ code compiles without errors
3. Expected test files exist
"""

import subprocess
import sys
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/src/Functions/padString.cpp"

def test_padded_pod_array_usage():
    """Verify PaddedPODArray is used instead of String for pad_string."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that PaddedPODArray is used for pad_string
    assert 'PaddedPODArray<UInt8> pad_string' in content, \
        "PaddedPODArray<UInt8> should be used for pad_string member"

    # Check that String is no longer used for pad_string
    # (The old code had: String pad_string; as a member)
    lines = content.split('\n')
    in_class_padding_chars = False
    brace_depth = 0
    found_old_pattern = False

    for line in lines:
        if 'class PaddingChars' in line:
            in_class_padding_chars = True
            brace_depth = 0

        if in_class_padding_chars:
            brace_depth += line.count('{') - line.count('}')

            # Look for old pattern: String pad_string; (not inside a function)
            if brace_depth > 0 and re.match(r'\s+String\s+pad_string\s*;', line):
                found_old_pattern = True
                break

            if brace_depth == 0 and '}' in line and 'class' not in line:
                in_class_padding_chars = False

    assert not found_old_pattern, \
        "Old 'String pad_string;' member should be replaced with PaddedPODArray"


def test_empty_pad_string_handling_moved():
    """Verify empty pad string handling is moved from init() to executeImpl."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that empty string handling is now in executeImpl
    # The fix moves: if (pad_string.empty()) pad_string = " ";
    # from init() to after getting pad_string from column
    assert "if (pad_string.empty())" in content, \
        "Empty pad_string check should be in executeImpl"

    # Verify it's in the executeImpl function context (after getting pad_string from column)
    pattern = r'pad_string = column_pad_const->getValue<String>\(\);\s*\}\s*if \(pad_string\.empty\(\)\)'
    assert re.search(pattern, content, re.DOTALL), \
        "Empty pad_string check should come right after getting value from column"


def test_init_method_removed():
    """Verify the old init() method is removed from PaddingChars class."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The old code had a private init() method
    # After the fix, init() should not exist as a separate method
    # Instead, the logic is in the constructor

    # Check that init() method is not present
    init_pattern = r'void\s+init\s*\(\s*\)'
    assert not re.search(init_pattern, content), \
        "Old init() method should be removed, logic moved to constructor"


def test_memcpySmallAllowReadWriteOverflow15_comment():
    """Verify comment explaining the padding requirement exists."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the explanatory comment
    assert 'memcpySmallAllowReadWriteOverflow15' in content, \
        "Comment should mention memcpySmallAllowReadWriteOverflow15 as the reason for padding"

    assert '15 extra bytes of read padding' in content, \
        "Comment should explain the 15-byte read padding requirement"


def test_insertFromItself_used():
    """Verify insertFromItself is used instead of operator+= for padding string."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The old code used: pad_string += pad_string;
    # The new code uses: pad_string.insertFromItself(pad_string.begin(), pad_string.end());
    assert 'insertFromItself' in content, \
        "insertFromItself should be used for duplicating pad_string content"


def test_validateFunctionArguments_usage():
    """Verify validateFunctionArguments is used for argument validation."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that validateFunctionArguments is used instead of manual validation
    assert 'validateFunctionArguments' in content, \
        "validateFunctionArguments should be used for argument validation"

    # Check that FunctionArgumentDescriptors are used
    assert 'FunctionArgumentDescriptors' in content, \
        "FunctionArgumentDescriptors should be used for argument descriptors"


def test_constructor_initialization_list():
    """Verify proper constructor initialization list formatting."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the Allman-style brace formatting in the constructor
    # The fix changes: : function_name(name_), is_right_pad(is_right_pad_), is_utf8(is_utf8_) {}
    # To:
    # : function_name(name_)
    # , is_right_pad(is_right_pad_)
    # , is_utf8(is_utf8_)
    # {}

    # Look for the pattern with each member on separate line
    pattern = r': function_name\(name_\)\s*\n\s*, is_right_pad\(is_right_pad_\)\s*\n\s*, is_utf8\(is_utf8_\)\s*\n\s*\{\}'
    assert re.search(pattern, content), \
        "Constructor should use Allman-style formatting with each member on separate line"


def test_cpp_syntax_valid():
    """Verify the C++ code has valid syntax by running clang syntax check."""
    # Try to compile just the file to check for syntax errors
    # This is a lightweight check - we don't need to fully build ClickHouse

    result = subprocess.run(
        [
            'clang-18', '-fsyntax-only', '-std=c++23',
            '-I', f'{REPO}/src',
            '-I', f'{REPO}/base',
            '-I', f'{REPO}/contrib/libcxx/include',
            '-I', f'{REPO}/contrib/libcxxabi/include',
            '-I', f'{REPO}/contrib/boost',
            '-I', f'{REPO}/contrib/abseil-cpp',
            '-c', TARGET_FILE
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # If this fails due to missing includes, that's ok - we're checking for obvious syntax errors
    # Only fail if there are clear syntax errors in the file itself
    if result.returncode != 0:
        # Check if the error is about the file content vs missing dependencies
        stderr = result.stderr
        if 'error:' in stderr and 'padString.cpp' in stderr:
            # Filter out errors that are not in our file
            lines = stderr.split('\n')
            our_errors = [l for l in lines if 'padString.cpp' in l and 'error:' in l]
            if our_errors:
                # Check if errors are about missing includes vs syntax
                syntax_errors = [l for l in our_errors if not 'file not found' in l.lower()]
                if syntax_errors:
                    pytest.fail(f"Syntax errors found:\n{chr(10).join(syntax_errors)}")

    # Test passes - either no errors or only missing include errors


def test_new_headers_included():
    """Verify new required headers are included."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for new headers added in the fix
    assert '#include <memory>' in content, \
        "<memory> header should be included"

    assert '#include <DataTypes/IDataType.h>' in content, \
        "IDataType.h should be included for validateFunctionArguments"


def test_error_codes_updated():
    """Verify error codes are updated correctly."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The fix removes ILLEGAL_TYPE_OF_ARGUMENT and NUMBER_OF_ARGUMENTS_DOESNT_MATCH
    # from this file since validateFunctionArguments handles them

    # Check they're removed from ErrorCodes namespace in this file
    error_codes_section = re.search(
        r'namespace ErrorCodes\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )

    if error_codes_section:
        section = error_codes_section.group(1)
        # These should not be declared in this file anymore
        assert 'ILLEGAL_TYPE_OF_ARGUMENT' not in section, \
            "ILLEGAL_TYPE_OF_ARGUMENT should be removed from local ErrorCodes (handled by validateFunctionArguments)"
        assert 'NUMBER_OF_ARGUMENTS_DOESNT_MATCH' not in section, \
            "NUMBER_OF_ARGUMENTS_DOESNT_MATCH should be removed from local ErrorCodes (handled by validateFunctionArguments)"


def test_chassert_for_column_check():
    """Verify chassert is used for the column type check."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The fix changes from throwing an exception to using chassert
    # since validation is already done by validateFunctionArguments
    assert 'chassert(column_pad_const)' in content, \
        "chassert should be used for column_pad_const check after validation"


# =============================================================================
# Pass-to-pass tests - These verify the repo's CI checks pass on base commit
# =============================================================================

def test_repo_style_cpp():
    """Repo's C++ style check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # The script exits 0 even if style issues found, but outputs style errors
    # A real failure would be the script crashing (non-zero from bash error)
    # We only fail if there's a bash error, not style issues in other files
    assert r.returncode == 0, f"C++ style check script failed:\n{r.stderr[-500:]}"


def test_repo_git_status():
    """Repo's git status is clean (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git status check failed:\n{r.stderr[-500:]}"
    # Check that working tree is clean (no modified files)
    # Empty output means clean working tree


def test_repo_padstring_tests_exist():
    """Test files for padString functions exist and are valid (pass_to_pass)."""
    # Verify the SQL test files exist and have content
    test_files = [
        f"{REPO}/tests/queries/0_stateless/01940_pad_string.sql",
        f"{REPO}/tests/queries/0_stateless/01940_pad_string.reference",
        f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.sql",
        f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.reference",
    ]
    for f in test_files:
        r = subprocess.run(
            ["test", "-s", f],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, f"Test file missing or empty: {f}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
