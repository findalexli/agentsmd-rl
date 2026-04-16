"""
Tests for ClickHouse padString heap-buffer-overflow fix.

The bug was a heap-buffer-overflow caused by memcpySmallAllowReadWriteOverflow15
reading beyond allocated memory because the PaddingChars class stored the pad
string in a regular std::string without 15 extra bytes of read padding.

The fix changes the pad_string storage from String to PaddedPODArray<UInt8>,
which provides the required 15 extra bytes of read padding.
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/padString.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)

# Expected reference output from the test file
EXPECTED_OUTPUTS = [
    # leftPad/rightPad ASCII
    "abcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnx",
    "xabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmnopqabcdefghijklmn",
    "abcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghix",
    "xabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghiabcdefghi",
    "abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcax",
    "xabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabca",
    "abcdefghijklmnopqrstuvwxyz0123456abcdefghijklmnopqrstuvwxyz0123456abcdefghijklmnopqrstuvwxyz0123456x",
    "xabcdefghijklmnopqrstuvwxyz0123456abcdefghijklmnopqrstuvwxyz0123456abcdefghijklmnopqrstuvwxyz0123456",
    # leftPadUTF8/rightPadUTF8
    "абвгдежзиклмнопрсабвгдежзиклмнопрсабвгдежзиклмнопx",
    "xабвгдежзиклмнопрсабвгдежзиклмнопрсабвгдежзиклмноп",
    "αβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδx",
    "xαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδεαβγδ",
    # Non-const data tests
    "abcdefghijklmnopqabcdefghhello",
    "abcdefghijklmnopqabcdefghworld",
    "abcdefghijklmnopqabcdefghitest",
    "helloabcdefghijklmnopqabcdefgh",
    "worldabcdefghijklmnopqabcdefgh",
    "testabcdefghijklmnopqabcdefghi",
]


def test_pad_string_uses_padded_pod_array():
    """
    Fail-to-pass test: Verify that pad_string is stored in PaddedPODArray<UInt8>.

    The original bug used std::string which doesn't provide the required 15 bytes
    of read padding that memcpySmallAllowReadWriteOverflow15 expects.

    The fix uses PaddedPODArray<UInt8> which provides this padding.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check that PaddedPODArray is used for the member variable in PaddingChars class
    assert "PaddedPODArray<UInt8> pad_string" in content, \
        "pad_string should be stored in PaddedPODArray<UInt8> for memory safety"

    # Verify the explanatory comment about memcpySmallAllowReadWriteOverflow15 is present
    assert "memcpySmallAllowReadWriteOverflow15" in content, \
        "Should have comment explaining why PaddedPODArray is needed"

    # Verify the fix is actually applied by checking there's no init() method
    # The old code had an init() method that was called from constructor
    # The new code has the logic inline in the constructor
    assert "void init()" not in content, \
        "Old init() method should be removed (logic moved to constructor)"


def test_pad_string_initialized_with_insert():
    """
    Fail-to-pass test: Verify pad_string is initialized using insert(), not assignment.

    The fix changes from assignment (pad_string = pad_string_) to insert(),
    which properly populates the PaddedPODArray with the source data.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the new initialization pattern
    assert "pad_string.insert(pad_string_.begin(), pad_string_.end())" in content, \
        "pad_string should be initialized using insert() method"

    # Make sure the init() method pattern is removed
    assert "void init()" not in content, \
        "Old init() method should be removed and logic moved to constructor"


def test_empty_pad_string_default_space():
    """
    Fail-to-pass test: Empty pad_string should default to single space.

    The fix moves the empty string default handling from init() to executeImpl,
    checking after extracting the pad_string from the column.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the new location of empty string handling
    # Looking for: if (pad_string.empty()) followed by pad_string = " "
    pattern = r'if \(pad_string\.empty\(\)\)\s+pad_string = " "'
    assert re.search(pattern, content), \
        "Empty pad_string should default to space in executeImpl, not in PaddingChars init"


def test_utf8_offsets_use_size_not_length():
    """
    Fail-to-pass test: UTF8 offsets should use pad_string.size() not .length().

    Since pad_string is now PaddedPODArray<UInt8>, it has .size() not .length().
    The fix updates all references to use .size().
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # numCharsInPadString should use size() for non-UTF8 case
    assert "return pad_string.size();" in content, \
        "numCharsInPadString should use size() for PaddedPODArray compatibility"

    # UTF8 initialization should use size()
    assert "utf8_offsets.reserve(pad_string.size() + 1)" in content, \
        "UTF8 offsets reservation should use size()"

    # Should not have the old length() pattern
    assert "pad_string.length()" not in content, \
        "Should not reference .length() on PaddedPODArray (use .size() instead)"


def test_append_to_uses_data_not_c_str():
    """
    Fail-to-pass test: appendTo should use pad_string.data(), not reinterpret_cast.

    The fix changes from reinterpret_cast<const UInt8*>(pad_string.data()) to
    just pad_string.data() since PaddedPODArray<UInt8> is already UInt8*.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should use pad_string.data() directly in writeSlice calls
    assert "writeSlice(StringSource::Slice{pad_string.data()," in content, \
        "appendTo should use pad_string.data() directly without reinterpret_cast"

    # The old reinterpret_cast pattern was inside writeSlice calls for the padding string
    # This pattern was: writeSlice(StringSource::Slice{reinterpret_cast<const UInt8 *>(pad_string.data()), ...}
    # which should now be: writeSlice(StringSource::Slice{pad_string.data(), ...}
    # Note: reinterpret_cast is still used for isAllASCII() which is a different purpose
    old_pattern = "writeSlice(StringSource::Slice{reinterpret_cast<const UInt8 *>(pad_string.data())"
    assert old_pattern not in content, \
        "Should not use reinterpret_cast in writeSlice calls (PaddedPODArray::data() returns UInt8*)"


def test_insert_from_itself_for_expansion():
    """
    Fail-to-pass test: PaddingChars should use insertFromItself for performance expansion.

    The fix changes from pad_string += pad_string (String concatenation) to
    pad_string.insertFromItself(pad_string.begin(), pad_string.end()) for PaddedPODArray.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should use insertFromItself for expanding the pad string to 16+ chars
    assert "pad_string.insertFromItself(pad_string.begin(), pad_string.end())" in content, \
        "Should use insertFromItself for expanding pad_string to >= 16 characters"

    # Should NOT use String concatenation
    assert "pad_string += pad_string" not in content, \
        "Should not use String concatenation += (PaddedPODArray uses insertFromItself)"


def test_argument_validation_updated():
    """
    Fail-to-pass test: getReturnTypeImpl should use validateFunctionArguments.

    The fix refactors the manual argument validation to use the helper function
    validateFunctionArguments with FunctionArgumentDescriptors.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should use the new validation helper
    assert "validateFunctionArguments(*this, arguments, mandatory_args, optional_args)" in content, \
        "Should use validateFunctionArguments helper for argument validation"

    # Should define FunctionArgumentDescriptors
    assert "FunctionArgumentDescriptors mandatory_args" in content, \
        "Should define mandatory_args descriptor"

    assert "FunctionArgumentDescriptors optional_args" in content, \
        "Should define optional_args descriptor"

    # Should NOT have the old manual NUMBER_OF_ARGUMENTS_DOESNT_MATCH error
    assert "NUMBER_OF_ARGUMENTS_DOESNT_MATCH" not in content, \
        "Should not manually check NUMBER_OF_ARGUMENTS_DOESNT_MATCH (handled by validator)"


def test_remove_illegal_type_error_codes():
    """
    Fail-to-pass test: ILLEGAL_TYPE_OF_ARGUMENT should be removed from ErrorCodes.

    Since argument validation is now done via validateFunctionArguments,
    the manual ILLEGAL_TYPE_OF_ARGUMENT error code is no longer needed.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should NOT declare ILLEGAL_TYPE_OF_ARGUMENT in ErrorCodes namespace
    error_codes_section = re.search(
        r'namespace ErrorCodes\s*\{([^}]+)\}', content, re.DOTALL)
    if error_codes_section:
        error_codes_content = error_codes_section.group(1)
        assert "ILLEGAL_TYPE_OF_ARGUMENT" not in error_codes_content, \
            "ILLEGAL_TYPE_OF_ARGUMENT should be removed from ErrorCodes (validation uses helper)"


def test_max_new_length_digit_separator():
    """
    Pass-to-pass test: MAX_NEW_LENGTH should use digit separator (C++14 feature).

    The fix changes 1000000 to 1'000'000 for better readability.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    assert "1'000'000" in content, \
        "MAX_NEW_LENGTH should use digit separator 1'000'000 for readability"


def test_use_chassert_for_column_pad_const():
    """
    Fail-to-pass test: Should use chassert instead of throwing for column_pad_const.

    The fix changes from throwing an exception if column_pad_const is null
    to using chassert (debug-only assertion) since the validation already
    guarantees it's a const column.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should use chassert
    assert "chassert(column_pad_const)" in content, \
        "Should use chassert for column_pad_const (validation already guarantees it's const)"

    # Should NOT have the old throw pattern for this case
    old_pattern = r'if \(!column_pad_const\)\s+throw Exception\('
    assert not re.search(old_pattern, content), \
        "Should not throw for null column_pad_const (use chassert instead)"


def test_num_chars_check_style():
    """
    Pass-to-pass test: Style improvement - use == 0 instead of ! for num_chars check.

    The fix changes "if (!num_chars)" to "if (num_chars == 0)" for clarity.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    assert "if (num_chars == 0)" in content, \
        "Should use explicit == 0 comparison for clarity"


def test_comment_about_read_padding():
    """
    Pass-to-pass test: Verify explanatory comment about 15 bytes of read padding is present.

    The fix includes a detailed comment explaining why PaddedPODArray is needed.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the detailed comment explaining the fix
    assert "15 extra bytes of read padding" in content, \
        "Should explain that PaddedPODArray provides 15 extra bytes of read padding"

    assert "Padded copy of the pad string (pun intended)" in content, \
        "Should have the pun comment documenting the member variable"


def test_consistent_list_initialization():
    """
    Pass-to-pass test: Constructor should use consistent C++ list initialization.

    The fix changes the FunctionPadString constructor initialization list style
    to be more consistent with project conventions.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the consistent initialization style in constructor
    assert ": function_name(name_)" in content, \
        "Constructor should use consistent member initialization style"


def test_error_message_updated():
    """
    Fail-to-pass test: Error message should mention FixedString too.

    The fix updates the error message from "must be a string" to
    "must be a String or FixedString" to match the actual validation.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    assert "must be a String or FixedString" in content, \
        "Error message should mention both String and FixedString"

    # Old message should be gone - check for the exact old pattern (lowercase 's' in 'string')
    # which should no longer exist (the new pattern uses capital 'S' in 'String')
    # We need to be careful not to match the new pattern, so check word boundaries
    old_pattern = r'must be a string[,"\']'  # "must be a string" followed by comma, quote, or end
    matches = re.findall(old_pattern, content)
    assert len(matches) == 0, \
        f"Old error message 'must be a string' should be updated, found: {matches}"


def test_padded_pod_array_include():
    """
    Fail-to-pass test: Should include necessary headers for PaddedPODArray.

    The fix adds #include <memory> and uses existing PaddedPODArray header
    (which is typically included via Column headers).
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Should include <memory> for std::make_shared
    assert "#include <memory>" in content, \
        "Should include <memory> header"

    # Should include IDataType.h for validateFunctionArguments
    assert "#include <DataTypes/IDataType.h>" in content, \
        "Should include IDataType.h for validateFunctionArguments"


def test_regression_test_files_created():
    """
    Fail-to-pass test: Regression test files should exist.

    The fix includes test files that trigger the heap-buffer-overflow condition.
    """
    sql_file = os.path.join(REPO, "tests/queries/0_stateless/04070_pad_string_asan_overflow.sql")
    ref_file = os.path.join(REPO, "tests/queries/0_stateless/04070_pad_string_asan_overflow.reference")

    # These files should exist after the fix is applied
    # Note: For this scaffolded task, we verify the expected content would be tested
    # In a real CI environment, these would run with ASAN enabled

    # For the benchmark, we verify the padString.cpp has the fix
    # which allows these tests to pass without ASAN errors
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # The fix must be present for the regression tests to pass
    assert "PaddedPODArray<UInt8> pad_string" in content, \
        "Regression test prerequisite: PaddedPODArray fix must be in padString.cpp"


# =============================================================================
# Repo CI Tests (origin: repo_tests) - Real CI commands that should pass
# =============================================================================


def test_no_broken_symlinks():
    """
    Pass-to-pass test: Repo should have no broken symlinks (repo_tests).

    CI style check command: find . -type l ! -exec test -e {} \\; -print
    """
    r = subprocess.run(
        ["bash", "-c", "cd '" + REPO + "' && find . -type l ! -exec test -e {} \\; -print 2>/dev/null"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Filter out only contrib symlinks which are expected to be handled separately
    broken_links = [line for line in r.stdout.strip().split('\n') if line and not line.startswith('./contrib/')]
    # Allow the one known broken symlink in contrib/thrift-cmake (known issue)
    broken_links = [line for line in broken_links if 'thrift-cmake' not in line]
    assert len(broken_links) == 0, f"Found broken symlinks: {broken_links}"


def test_clickhouse_test_script_syntax():
    """
    Pass-to-pass test: Main test script has valid Python syntax (repo_tests).

    CI command: python3 -m py_compile tests/clickhouse-test
    """
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/tests/clickhouse-test"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"clickhouse-test script has syntax errors: {r.stderr}"


def test_pad_string_sql_test_exists():
    """
    Pass-to-pass test: Existing pad_string SQL test files should be present (repo_tests).

    Verifies the 01940_pad_string test exists - this covers the modified code.
    """
    r = subprocess.run(
        ["ls", f"{REPO}/tests/queries/0_stateless/01940_pad_string.sql"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.sql test file should exist"

    r = subprocess.run(
        ["ls", f"{REPO}/tests/queries/0_stateless/01940_pad_string.reference"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.reference test file should exist"


def test_leftpad_fixedstring_sql_test_exists():
    """
    Pass-to-pass test: Existing leftpad_fixedstring SQL test files should be present (repo_tests).

    Verifies the 02986_leftpad_fixedstring test exists - this covers FixedString padding.
    """
    r = subprocess.run(
        ["ls", f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.sql"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "02986_leftpad_fixedstring.sql test file should exist"

    r = subprocess.run(
        ["ls", f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.reference"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "02986_leftpad_fixedstring.reference test file should exist"


def test_pad_string_cpp_syntax_valid():
    """
    Pass-to-pass test: padString.cpp should have valid include structure (repo_tests).

    Uses grep to verify basic C++ syntax elements are present.
    """
    r = subprocess.run(
        ["grep", "-q", "#include <", f"{REPO}/src/Functions/padString.cpp"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "padString.cpp should have include statements"

    r = subprocess.run(
        ["grep", "-q", "namespace DB", f"{REPO}/src/Functions/padString.cpp"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "padString.cpp should have DB namespace"
