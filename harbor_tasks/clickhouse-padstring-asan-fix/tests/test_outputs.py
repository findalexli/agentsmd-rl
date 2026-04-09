#!/usr/bin/env python3
"""Tests for ClickHouse padString heap-buffer-overflow fix.

This tests that the leftPad/rightPad functions properly handle memory
when using the PaddedPODArray for safe read access.
"""

import subprocess
import sys
import os

REPO_DIR = "/workspace/ClickHouse"
FUNCTION_FILE = f"{REPO_DIR}/src/Functions/padString.cpp"

def test_padding_chars_uses_padded_pod_array():
    """FAIL-TO-PASS: Verify PaddingChars uses PaddedPODArray instead of String.

    The bug was caused by using std::String for pad_string, which doesn't provide
the 15-byte read padding required by memcpySmallAllowReadWriteOverflow15.
    The fix uses PaddedPODArray<UInt8> which provides this safety padding.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Check that pad_string is now PaddedPODArray<UInt8>, not String
    assert "PaddedPODArray<UInt8> pad_string" in content, \
        "pad_string field should be PaddedPODArray<UInt8> for memory safety"

    # Make sure old String-based implementation is gone
    assert "String pad_string;" not in content, \
        "Old String-based pad_string field should be removed"

def test_no_string_concatenation_in_pad_init():
    """FAIL-TO-PASS: Verify the old pad_string += pad_string pattern is removed.

    The old code used pad_string += pad_string to expand the padding string,
    which could cause heap-buffer-overflow when the original string was then
    accessed with out-of-bounds reads by memcpySmallAllowReadWriteOverflow15.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Should use insertFromItself instead of += for PaddedPODArray
    assert "insertFromItself" in content, \
        "Should use PaddedPODArray::insertFromItself for string expansion"

def test_uses_memcpy_safe_data_method():
    """FAIL-TO-PASS: Verify pad_string.data() is used without reinterpret_cast.

    With PaddedPODArray, data() returns UInt8* directly, no cast needed.
    The old code had reinterpret_cast<const UInt8 *>(pad_string.data()).
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Should not have the old pattern with reinterpret_cast for pad_string
    old_pattern_count = content.count('reinterpret_cast<const UInt8 *>(pad_string.data())')
    assert old_pattern_count == 0, \
        f"Old reinterpret_cast pattern should be removed (found {old_pattern_count} instances)"

def test_padding_chars_constructor_handles_empty_pad():
    """Verify empty pad string handling moved to executeImpl.

    The fix moved the 'if (pad_string.empty()) pad_string = " ";' check
    from PaddingChars::init() to executeImpl() to handle it properly.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Should handle empty pad string in executeImpl
    assert 'if (pad_string.empty())' in content, \
        "Empty pad string check must exist somewhere in the code"

def test_explicit_num_chars_comparison():
    """FAIL-TO-PASS: Verify the style improvement: explicit == 0 comparison.

    Changed from if (!num_chars) to if (num_chars == 0) for clarity.
    """
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Check for the explicit comparison pattern in appendTo
    assert "if (num_chars == 0)" in content, \
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

def test_namespace_and_structure_intact():
    """Verify core function structure is preserved."""
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # Core components should still exist
    assert "FunctionPadString" in content, "FunctionPadString class should exist"
    assert "PaddingChars" in content, "PaddingChars class should exist"
    assert "executePad" in content, "executePad method should exist"
    assert "executeForSourceAndLength" in content, "executeForSourceAndLength method should exist"

def test_utf8_handling_preserved():
    """Verify UTF-8 handling code is still present."""
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # UTF-8 specific handling should exist
    assert "utf8_offsets" in content, "utf8_offsets field should exist for UTF-8 handling"
    assert "is_utf8" in content, "is_utf8 template parameter should exist"

def test_error_codes_cleanup():
    """FAIL-TO-PASS: Verify unused error codes were removed."""
    with open(FUNCTION_FILE, 'r') as f:
        content = f.read()

    # These should be removed as they're not needed with validateFunctionArguments
    assert "ILLEGAL_TYPE_OF_ARGUMENT" not in content, \
        "ILLEGAL_TYPE_OF_ARGUMENT should be removed (handled by validateFunctionArguments)"
    assert "NUMBER_OF_ARGUMENTS_DOESNT_MATCH" not in content, \
        "NUMBER_OF_ARGUMENTS_DOESNT_MATCH should be removed (handled by validateFunctionArguments)"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
