"""
Tests for ClickHouse padString heap-buffer-overflow fix.

The bug was a heap-buffer-overflow caused by memcpySmallAllowReadWriteOverflow15
reading beyond allocated memory because the PaddingChars class stored the pad
string in a regular std::string without 15 extra bytes of read padding.
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/padString.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def _read_target():
    """Read the target source file."""
    with open(FULL_PATH, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests
# =============================================================================


def test_pad_string_member_not_string_type():
    """
    Fail-to-pass: The pad_string member in the PaddingChars class must NOT be
    declared as 'String' type. String (std::string) lacks the 15 extra bytes of
    read padding required by memcpySmallAllowReadWriteOverflow15.

    The broken code has 'String pad_string;' as the class member just above the
    '/// Offsets of code points in `pad_string`' comment block.
    """
    content = _read_target()

    if re.search(r'String\s+pad_string\s*;\s*\n\s*/// Offsets of code points in `pad_string`', content):
        raise AssertionError(
            "pad_string member in PaddingChars class still declared as String; "
            "must use a buffer type that provides adequate read padding"
        )

    assert "pad_string" in content, "pad_string member identifier is missing from the file"


def test_no_reinterpret_cast_on_pad_data():
    """
    Fail-to-pass: writeSlice calls must NOT use reinterpret_cast on
    pad_string.data(). The broken code uses reinterpret_cast because
    String::data() returns char*, but the correct buffer type's data()
    should return a pointer type that matches what writeSlice expects.

    Note: reinterpret_cast may still appear elsewhere (e.g. isAllASCII)
    since those use a different pad_string (function parameter, not the
    class member). Only the writeSlice calls matter for this test.
    """
    content = _read_target()

    if re.search(r'writeSlice.*reinterpret_cast.*pad_string\.data\(\)', content):
        raise AssertionError(
            "writeSlice calls still use reinterpret_cast on pad_string.data(); "
            "the data pointer type should already match writeSlice's parameter type"
        )

    assert "pad_string.data()" in content, \
        "writeSlice should reference pad_string.data()"


def test_no_manual_argument_count_check():
    """
    Fail-to-pass: The argument validation must NOT use the manual error code
    NUMBER_OF_ARGUMENTS_DOESNT_MATCH. ClickHouse has standard helpers for
    function argument validation that should be used instead of manual
    type-checking throws.
    """
    content = _read_target()
    if "NUMBER_OF_ARGUMENTS_DOESNT_MATCH" in content:
        raise AssertionError(
            "Manual argument count check with NUMBER_OF_ARGUMENTS_DOESNT_MATCH "
            "should be replaced with standard ClickHouse validation helpers"
        )


def test_error_message_lists_both_accepted_types():
    """
    Fail-to-pass: The error message for the first argument must accurately
    list both String and FixedString as accepted types.
    """
    content = _read_target()
    assert "must be a String or FixedString" in content, \
        "Error message should state 'must be a String or FixedString'"


def test_no_redundant_runtime_exception_for_const_column():
    """
    Fail-to-pass: The runtime exception for null column_pad_const must be
    removed. The broken code throws "must be a constant string", but this
    condition is already guaranteed by prior argument validation.
    """
    content = _read_target()
    if "must be a constant string" in content:
        raise AssertionError(
            "Redundant 'must be a constant string' runtime exception should be removed; "
            "this condition is already guaranteed by prior validation"
        )


# =============================================================================
# Pass-to-pass tests (origin: repo_tests)
# =============================================================================


def test_pad_string_sql_test_exists():
    """
    Pass-to-pass: Existing 01940_pad_string SQL test files should be present.
    """
    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/01940_pad_string.sql")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.sql test file should exist"

    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/01940_pad_string.reference")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.reference test file should exist"


def test_leftpad_fixedstring_sql_test_exists():
    """
    Pass-to-pass: Existing 02986_leftpad_fixedstring SQL test files should be present.
    """
    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/02986_leftpad_fixedstring.sql")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "02986_leftpad_fixedstring.sql test file should exist"


def test_pad_string_cpp_has_valid_structure():
    """
    Pass-to-pass: padString.cpp should have valid include/namespace structure.
    After any edits, the file must remain structurally sound.
    """
    content = _read_target()

    assert "#include <" in content, "Missing include statements"
    assert "namespace DB" in content, "Missing DB namespace"
    assert "class PaddingChars" in content, "Missing PaddingChars class"
    assert "class FunctionPadString" in content, "Missing FunctionPadString class"
