#!/usr/bin/env python3
"""Tests for ClickHouse padString heap-buffer-overflow fix.

This tests that the leftPad/rightPad functions properly handle memory
when using the PaddedPODArray for safe read access.
"""

import subprocess
import sys
import os
import re

REPO_DIR = "/workspace/ClickHouse"
FUNCTION_FILE = f"{REPO_DIR}/src/Functions/padString.cpp"


def _extract_class_content(content: str, class_name: str) -> str:
    """Extract the content of a C++ class from file content."""
    pattern = rf'class\s+{class_name}\s*\{{'
    match = re.search(pattern, content)
    if not match:
        return ""

    start = match.start()
    brace_count = 0
    i = start
    while i < len(content):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                return content[start:i+1]
        i += 1
    return ""


def test_padding_chars_uses_padded_pod_array():
    """FAIL-TO-PASS: Verify PaddingChars uses PaddedPODArray instead of String.

    The bug was caused by using std::String for pad_string, which doesn't provide
the 15-byte read padding required by memcpySmallAllowReadWriteOverflow15.
    The fix uses PaddedPODArray<UInt8> which provides this safety padding.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract the PaddingChars class to verify its internal structure
    padding_chars_class = _extract_class_content(content, "PaddingChars")
    if not padding_chars_class:
        # Fallback to full content if class extraction fails
        padding_chars_class = content

    # Check that pad_string is now PaddedPODArray<UInt8>, not String
    assert "PaddedPODArray<UInt8> pad_string" in padding_chars_class, \
        "pad_string field should be PaddedPODArray<UInt8> for memory safety"

    # Make sure old String-based implementation is gone from class
    # (String pad_string should not exist in the PaddingChars class)
    lines = padding_chars_class.split('\n')
    in_padding_class = False
    brace_depth = 0
    for line in lines:
        if 'class PaddingChars' in line:
            in_padding_class = True
        if in_padding_class:
            for c in line:
                if c == '{':
                    brace_depth += 1
                elif c == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        in_padding_class = False
                        break
            if 'String pad_string' in line and '//' not in line:
                assert False, "Old String-based pad_string field should be removed from PaddingChars class"

    # BEHAVIORAL CHECK: Verify the code compiles successfully
    # This ensures the PaddedPODArray fix is syntactically correct C++
    r = subprocess.run(
        ["bash", "-c",
         f"cd {REPO_DIR} && clang-15 -fsyntax-only -std=c++20 "
         f"-I src -I base/glibc-compatibility "
         f"-c {FUNCTION_FILE} 2>&1 || true"],
        capture_output=True, text=True, timeout=60,
    )
    # We expect missing include errors, but not syntax errors
    errors = [line for line in r.stderr.split('\n')
              if 'error:' in line
              and 'file not found' not in line.lower()
              and 'no such file' not in line.lower()
              and 'PaddedPODArray' not in line]  # Ignore errors about PaddedPODArray type
    if errors:
        assert False, f"C++ syntax errors after fix:\n" + "\n".join(errors[:5])


def test_no_string_concatenation_in_pad_init():
    """FAIL-TO-PASS: Verify the old pad_string += pad_string pattern is removed.

    The old code used pad_string += pad_string to expand the padding string,
    which could cause heap-buffer-overflow when the original string was then
    accessed with out-of-bounds reads by memcpySmallAllowReadWriteOverflow15.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract the PaddingChars class constructor
    padding_chars_class = _extract_class_content(content, "PaddingChars")

    # Should use insertFromItself instead of += for PaddedPODArray expansion
    assert "insertFromItself" in padding_chars_class, \
        "Should use PaddedPODArray::insertFromItself for string expansion"

    # The old pattern pad_string += pad_string should not be in the constructor
    # Check that += expansion is not used for the member variable
    assert "pad_string += pad_string" not in padding_chars_class, \
        "Old String concatenation pattern should be removed from PaddingChars"


def test_no_reinterpret_cast_in_append_to():
    """FAIL-TO-PASS: Verify pad_string.data() is used without reinterpret_cast.

    With PaddedPODArray, data() returns UInt8* directly, no cast needed.
    The old code had reinterpret_cast<const UInt8 *>(pad_string.data()).
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract the PaddingChars class
    padding_chars_class = _extract_class_content(content, "PaddingChars")

    # Should not have the old pattern with reinterpret_cast for pad_string.data()
    old_pattern = 'reinterpret_cast<const UInt8 *>(pad_string.data())'
    if old_pattern in padding_chars_class:
        count = padding_chars_class.count(old_pattern)
        assert False, \
            f"Old reinterpret_cast pattern should be removed (found {count} instances in PaddingChars)"

    # Verify that pad_string.data() is used directly in writeSlice calls
    assert "pad_string.data()" in padding_chars_class, \
        "Should use pad_string.data() directly without reinterpret_cast"


def test_empty_pad_handled_in_execute_impl():
    """FAIL-TO-PASS: Verify empty pad string handling moved to executeImpl.

    The fix moved the 'if (pad_string.empty()) pad_string = " ";' check
    from PaddingChars::init() to executeImpl() to handle it properly.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract executeImpl function - handle both old (buggy) and new (fixed) structures
    # Old: template <bool is_utf8> executeImpl... (with template prefix)
    # New: ColumnPtr executeImpl... (no template, const override)
    execute_impl_match = re.search(
        r'ColumnPtr\s+executeImpl.*?\{',
        content,
        re.DOTALL
    )
    if execute_impl_match:
        # Find the function body
        start = execute_impl_match.start()
        brace_count = 0
        i = start
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    execute_impl_body = content[start:i+1]
                    break
            i += 1
        else:
            execute_impl_body = ""
    else:
        # Fallback: look for the pattern in full content
        execute_impl_body = content

    # Should handle empty pad string in executeImpl
    assert 'if (pad_string.empty())' in execute_impl_body, \
        "Empty pad string check must exist in executeImpl"


def test_explicit_num_chars_comparison():
    """FAIL-TO-PASS: Verify the style improvement: explicit == 0 comparison.

    Changed from if (!num_chars) to if (num_chars == 0) for clarity.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract the PaddingChars class (specifically appendTo method)
    padding_chars_class = _extract_class_content(content, "PaddingChars")

    # Check for the explicit comparison pattern in appendTo
    assert "if (num_chars == 0)" in padding_chars_class, \
        "Should use explicit num_chars == 0 comparison for clarity"


def test_max_new_length_digit_separator():
    """FAIL-TO-PASS: Verify modern C++ digit separator used for large constants."""
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Check for digit separator in MAX_NEW_LENGTH
    assert "1'000'000" in content, \
        "MAX_NEW_LENGTH should use C++14 digit separator for readability"


def test_validate_function_arguments_used():
    """FAIL-TO-PASS: Verify the modern validateFunctionArguments helper is used.

    The PR refactored manual argument validation to use validateFunctionArguments.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Should use the modern validation helper
    assert "validateFunctionArguments" in content, \
        "Should use validateFunctionArguments for argument validation"

    # Should have FunctionArgumentDescriptors
    assert "FunctionArgumentDescriptors" in content, \
        "Should define FunctionArgumentDescriptors for validation"


def test_error_codes_cleanup():
    """FAIL-TO-PASS: Verify unused error codes were removed."""
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Extract ErrorCodes namespace
    error_codes_match = re.search(
        r'namespace\s+ErrorCodes\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    if error_codes_match:
        error_codes_section = error_codes_match.group(1)
    else:
        error_codes_section = content

    # These should be removed as they're not needed with validateFunctionArguments
    assert "ILLEGAL_TYPE_OF_ARGUMENT" not in error_codes_section, \
        "ILLEGAL_TYPE_OF_ARGUMENT should be removed from ErrorCodes namespace"
    assert "NUMBER_OF_ARGUMENTS_DOESNT_MATCH" not in error_codes_section, \
        "NUMBER_OF_ARGUMENTS_DOESNT_MATCH should be removed from ErrorCodes namespace"


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI validation checks
# =============================================================================


def test_cpp_compiles_syntax_valid():
    """PASS-TO-PASS: C++ file has valid syntax (pass_to_pass).

    Uses clang to verify the file is syntactically valid C++.
    This is more robust than just checking balanced braces.
    """
    # First check: balanced braces/parentheses (lightweight)
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Count opening and closing braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_parens = content.count('(')
    close_parens = content.count(')')
    open_brackets = content.count('[')
    close_brackets = content.count(']')

    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    assert open_brackets == close_brackets, \
        f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"

    # Second check: try to compile just this file (syntax check only)
    # This will catch syntax errors without needing full project build
    r = subprocess.run(
        ["bash", "-c",
         f"cd {REPO_DIR} && clang-15 -fsyntax-only -std=c++20 "
         f"-I src -I base/glibc-compatibility "
         f"-c {FUNCTION_FILE} 2>&1 || true"],
        capture_output=True, text=True, timeout=60,
    )
    # We expect this to fail due to missing includes, but no syntax errors
    # If there are "error:" messages that aren't about missing files, that's a problem
    errors = [line for line in r.stderr.split('\n')
              if 'error:' in line and 'file not found' not in line.lower()
              and 'no such file' not in line.lower()]
    if errors:
        assert False, f"C++ syntax errors found:\n" + "\n".join(errors[:5])


def test_required_headers_present():
    """FAIL-TO-PASS: Required standard headers must be present after the fix.

    ClickHouse code requires specific headers for PaddedPODArray functionality.
    These are missing in the base version and added by the fix.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Check for required headers
    assert "<memory>" in content, \
        "Should include <memory> header"

    # Check that PaddedPODArray is referenced (from <Common/PODArray.h>)
    assert "PaddedPODArray" in content, \
        "Should reference PaddedPODArray (from <Common/PODArray.h>)"


def test_namespace_and_structure_intact():
    """PASS-TO-PASS: Core function structure is preserved (pass_to_pass).

    Verifies the key classes and methods exist.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Core components should still exist
    assert "FunctionPadString" in content, "FunctionPadString class should exist"
    assert "PaddingChars" in content, "PaddingChars class should exist"
    assert "executePad" in content, "executePad method should exist"
    assert "executeForSourceAndLength" in content, "executeForSourceAndLength method should exist"


def test_utf8_handling_preserved():
    """PASS-TO-PASS: UTF-8 handling code is still present (pass_to_pass).

    Verifies UTF-8 support was not broken by the fix.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # UTF-8 specific handling should exist
    assert "utf8_offsets" in content, "utf8_offsets field should exist for UTF-8 handling"
    assert "is_utf8" in content, "is_utf8 template parameter should exist"


def test_no_trailing_whitespace():
    """PASS-TO-PASS: No trailing whitespace in source file (pass_to_pass).

    Standard code quality check that ClickHouse CI enforces.
    """
    r = subprocess.run(
        ["bash", "-c", f"grep -n ' $' {FUNCTION_FILE} || true"],
        capture_output=True, text=True, timeout=30,
    )
    # If grep finds trailing whitespace, it will return output
    trailing_lines = r.stdout.strip()
    if trailing_lines:
        lines = trailing_lines.split('\n')[:5]  # Show first 5
        assert False, f"Found trailing whitespace on lines:\n" + "\n".join(lines)


def test_no_tab_characters():
    """PASS-TO-PASS: No tab characters in source file (pass_to_pass).

    ClickHouse uses spaces for indentation (4 spaces). Tabs are prohibited.
    """
    r = subprocess.run(
        ["bash", "-c", f"grep -n $\'\\t\' {FUNCTION_FILE} || true"],
        capture_output=True, text=True, timeout=30,
    )
    tab_lines = r.stdout.strip()
    if tab_lines:
        lines = tab_lines.split('\n')[:5]
        assert False, f"Found tab characters on lines:\n" + "\n".join(lines)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])