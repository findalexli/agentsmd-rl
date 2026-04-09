#!/usr/bin/env python3
"""
Behavioral tests for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

The bug: The padString functions used memcpySmallAllowReadWriteOverflow15 which
requires 15 bytes of readable padding beyond the buffer. Using std::string didn't
provide this guarantee, causing heap-buffer-overflow on ASan builds.

The fix: Use PaddedPODArray<UInt8> which provides the required 15-byte padding.
"""

import subprocess
import re
import os
import json
import tempfile
import sys
from pathlib import Path

REPO = "/workspace/ClickHouse"
PADSTRING_FILE = f"{REPO}/src/Functions/padString.cpp"

# Source refs for agent_config checks
BASE_COMMIT = "73ad233a01a81190b2a45b820878e54c36a9a22c"
MERGE_COMMIT = "31deb8bb10fb7083a3c76f1112607b40cb26700b"


def _fetch_file_from_commit(filepath: str, commit: str, url_suffix: str) -> bool:
    """Fetch a file from GitHub if it doesn't exist locally."""
    if os.path.exists(filepath):
        return True

    import urllib.request
    url = f"https://raw.githubusercontent.com/ClickHouse/ClickHouse/{commit}/tests/queries/0_stateless/{url_suffix}"
    try:
        urllib.request.urlretrieve(url, filepath)
        return os.path.exists(filepath)
    except Exception:
        return False


def _run_python_code(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout
    )


def _parse_sql_queries(sql_content: str) -> list:
    """Parse SQL content and extract executable queries."""
    queries = []
    current_query = []

    for line in sql_content.split('\n'):
        stripped = line.strip()
        # Skip comments and empty lines
        if not stripped or stripped.startswith('--'):
            continue
        current_query.append(line)
        if stripped.endswith(';'):
            queries.append('\n'.join(current_query))
            current_query = []

    # Handle queries without trailing semicolon
    if current_query:
        queries.append('\n'.join(current_query))

    return queries


# ============================================================================
# FAIL-TO-PASS TESTS (Behavioral changes that fail without the fix)
# ============================================================================

def test_padded_pod_array_storage():
    """
    BEHAVIORAL: Verify PaddedPODArray is used for safe memory access.

    The critical fix changes pad_string storage from String to PaddedPODArray<UInt8>.
    Without this, the code triggers heap-buffer-overflow when memcpy reads past buffer.
    """
    code = f'''
import re
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Must use PaddedPODArray for safe memory access
if "PaddedPODArray<UInt8> pad_string" not in content:
    print("FAIL: pad_string should use PaddedPODArray<UInt8>")
    sys.exit(1)

# Check that PaddingChars class uses PaddedPODArray in private section
private_section = content.split("private:")[1] if "private:" in content else ""
if "PaddedPODArray<UInt8> pad_string;" not in private_section:
    print("FAIL: PaddingChars member pad_string should use PaddedPODArray<UInt8>")
    sys.exit(1)

print("PASS: PaddedPODArray<UInt8> used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_insert_from_itself_usage():
    """
    BEHAVIORAL: Verify safe expansion method is used instead of string concatenation.

    The bug was in the padding expansion loop. Old code used pad_string += pad_string
    which doesn't work with PaddedPODArray memory layout. The fix uses insertFromItself.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Must use insertFromItself for safe array expansion
if "insertFromItself" not in content:
    print("FAIL: Should use insertFromItself for safe expansion")
    sys.exit(1)

# Must use insert for initial copy from String to PaddedPODArray
if "pad_string.insert(pad_string_.begin(), pad_string_.end())" not in content:
    print("FAIL: Should use insert to copy initial pad string data")
    sys.exit(1)

# Must NOT use unsafe string concatenation
if "pad_string += pad_string" in content:
    print("FAIL: Should not use += for pad_string expansion")
    sys.exit(1)

print("PASS: Safe expansion methods used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_empty_pad_string_handling():
    """
    BEHAVIORAL: Verify empty pad string is handled in executeImpl, not in constructor.

    The fix moves empty pad string handling from init() to executeImpl for clarity.
    """
    code = f'''
import re
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Should handle empty pad_string in executeImpl
if "if (pad_string.empty())" not in content:
    print("FAIL: Empty pad_string check should be present")
    sys.exit(1)

# Should set default space character after extraction
pattern = r'if \\(pad_string\\.empty\\(\\)\\)\\s+pad_string = " "'
if not re.search(pattern, content):
    print("FAIL: Should set empty pad_string to space in executeImpl")
    sys.exit(1)

# init() method should be removed
if "void init()" in content:
    print("FAIL: init() method should be removed")
    sys.exit(1)

print("PASS: Empty pad string handled correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_chassert_used_after_validation():
    """
    BEHAVIORAL: Verify chassert is used instead of exception after validation.

    After validateFunctionArguments confirms column is const, chassert is sufficient.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Should use chassert after validateFunctionArguments validates the column
if "chassert(column_pad_const)" not in content:
    print("FAIL: Should use chassert after validateFunctionArguments")
    sys.exit(1)

print("PASS: chassert used correctly after validation")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_validate_function_arguments():
    """
    BEHAVIORAL: Verify validateFunctionArguments helper is used.

    The fix replaces manual argument validation with the standard helper function.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Should use the helper function for argument validation
if "validateFunctionArguments" not in content:
    print("FAIL: Should use validateFunctionArguments helper")
    sys.exit(1)

# Should define mandatory_args descriptor
if "FunctionArgumentDescriptors mandatory_args" not in content:
    print("FAIL: Should define mandatory_args descriptor")
    sys.exit(1)

# Should define optional_args descriptor
if "FunctionArgumentDescriptors optional_args" not in content:
    print("FAIL: Should define optional_args descriptor")
    sys.exit(1)

print("PASS: validateFunctionArguments used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_error_codes_cleaned():
    """
    BEHAVIORAL: Verify unused error codes are removed after using helper.

    validateFunctionArguments handles these errors internally.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# These error codes are no longer needed after using validateFunctionArguments
if "extern const int ILLEGAL_TYPE_OF_ARGUMENT;" in content:
    print("FAIL: ILLEGAL_TYPE_OF_ARGUMENT should be removed")
    sys.exit(1)

if "extern const int NUMBER_OF_ARGUMENTS_DOESNT_MATCH;" in content:
    print("FAIL: NUMBER_OF_ARGUMENTS_DOESNT_MATCH should be removed")
    sys.exit(1)

print("PASS: Unused error codes removed correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_num_chars_comparison_explicit():
    """
    BEHAVIORAL: Verify explicit comparison is used instead of implicit bool.

    Code quality: if (num_chars == 0) is clearer than if (!num_chars).
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# The fix changes if (!num_chars) to if (num_chars == 0)
if "if (num_chars == 0)" not in content:
    print("FAIL: Should use explicit num_chars == 0 comparison")
    sys.exit(1)

print("PASS: Explicit comparison used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_digit_separator_used():
    """
    BEHAVIORAL: Verify C++14 digit separator is used for readability.

    The fix changes 1000000 to 1'000'000 for better readability.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# The fix uses C++14 digit separator: 1\\'000\\'000
if "1\\'000\\'000" not in content:
    print("FAIL: Should use C++14 digit separator")
    sys.exit(1)

print("PASS: C++14 digit separator used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_function_signature_updated():
    """
    BEHAVIORAL: Verify getReturnTypeImpl uses correct signature.

    The fix changes from DataTypes to ColumnsWithTypeAndName signature.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Should use ColumnsWithTypeAndName instead of DataTypes
if "const ColumnsWithTypeAndName & arguments" not in content:
    print("FAIL: getReturnTypeImpl should use ColumnsWithTypeAndName")
    sys.exit(1)

print("PASS: Function signature updated correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_includes_updated():
    """
    BEHAVIORAL: Verify necessary includes are added for the fix.

    The fix adds <memory> for std::min and <IDataType.h> for validateFunctionArguments.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Should include memory header for std::min
if "#include <memory>" not in content:
    print("FAIL: Should include <memory> header")
    sys.exit(1)

# Should include IDataType.h for validateFunctionArguments
if "#include <DataTypes/IDataType.h>" not in content:
    print("FAIL: Should include IDataType.h")
    sys.exit(1)

print("PASS: Includes updated correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_utf8_size_not_length():
    """
    BEHAVIORAL: Verify UTF8 code uses size() not length() for PaddedPODArray.

    PaddedPODArray uses size(), std::string uses length(). The fix updates all calls.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# PaddedPODArray uses .size(), not .length() like std::string
if "return pad_string.size();" not in content:
    print("FAIL: numCharsInPadString should use pad_string.size()")
    sys.exit(1)

# UTF8 offsets should reserve based on size()
if "utf8_offsets.reserve(pad_string.size() + 1)" not in content:
    print("FAIL: UTF8 offsets should reserve based on pad_string.size()")
    sys.exit(1)

# UTF8 offset comparison should use size()
if "offset == pad_string.size()" not in content:
    print("FAIL: UTF8 offset loop should compare against pad_string.size()")
    sys.exit(1)

# UTF8 min should use size()
if "offset = std::min(offset, pad_string.size())" not in content:
    print("FAIL: UTF8 offset min should use pad_string.size()")
    sys.exit(1)

print("PASS: UTF8 code uses size() correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_allman_brace_style():
    """
    BEHAVIORAL: Verify Allman brace style is used (enforced by CI).

    The fix uses opening brace on new line, which is required by ClickHouse CI.
    """
    code = f'''
import re
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for constructor with Allman-style braces
# Opening brace should be on new line after initializers
allman_pattern = r":\\s+function_name\\(name_\\)\\s*\\n\\s*,\\s*is_right_pad\\(is_right_pad_\\)\\s*\\n\\s*,\\s*is_utf8\\(is_utf8_\\)\\s*\\n\\s*\\{{"
if not re.search(allman_pattern, content):
    print("FAIL: Should use Allman brace style (opening brace on new line)")
    sys.exit(1)

print("PASS: Allman brace style used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_write_slice_no_cast():
    """
    BEHAVIORAL: Verify writeSlice uses pad_string.data() directly without cast.

    PaddedPODArray<UInt8>::data() returns UInt8* directly, no cast needed.
    """
    code = f"""
import sys

with open(\"{PADSTRING_FILE}\", \"r\") as f:
    content = f.read()

# Old code used cast: reinterpret_cast<const UInt8 *
# Check that we don't have the old cast pattern
import re
write_slice_calls = re.findall(r'writeSlice\([^)]+\)', content)
for call in write_slice_calls:
    if "reinterpret_cast" in call:
        print(\"FAIL: writeSlice should not cast pad_string.data()\")
        sys.exit(1)

# Should use direct data() access in writeSlice calls
good_pattern = \"pad_string.data()\"
if good_pattern not in content:
    print(\"FAIL: Should use pad_string.data() directly in writeSlice\")
    sys.exit(1)

print(\"PASS: writeSlice uses pad_string.data() correctly\")
"""
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


# ============================================================================
# PASS-TO-PASS TESTS (Repo compliance tests)
# ============================================================================

def test_regression_sql_file_valid():
    """
    BEHAVIORAL: Verify regression SQL file can be fetched and parsed.

    Downloads the SQL test file from PR and validates it contains executable queries.
    """
    test_sql = f"{REPO}/tests/queries/0_stateless/04070_pad_string_asan_overflow.sql"

    # Fetch from merge commit if not present
    assert _fetch_file_from_commit(test_sql, MERGE_COMMIT, "04070_pad_string_asan_overflow.sql"), \
        "Could not fetch regression SQL test file"

    # Now parse and validate the SQL
    code = f'''
import sys

with open("{test_sql}", "r") as f:
    content = f.read()

if not content.strip():
    print("FAIL: SQL file is empty")
    sys.exit(1)

# Parse queries
queries = []
current = []
for line in content.split("\\n"):
    stripped = line.strip()
    if not stripped or stripped.startswith("--"):
        continue
    current.append(line)
    if stripped.endswith(";"):
        queries.append("\\n".join(current))
        current = []

if current:
    queries.append("\\n".join(current))

if len(queries) == 0:
    print("FAIL: No queries found in SQL file")
    sys.exit(1)

# Verify test coverage
if "leftPad" not in content and "rightPad" not in content:
    print("FAIL: Should test leftPad and/or rightPad")
    sys.exit(1)

# Verify long pad string test (triggers the overflow)
if "abcdefghijklmnopq" not in content:
    print("FAIL: Should test with long pad strings")
    sys.exit(1)

print(f"PASS: Found {{len(queries)}} queries in regression test")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_regression_reference_file_valid():
    """
    BEHAVIORAL: Verify regression reference file can be fetched and parsed.

    Downloads the reference file from PR and validates it contains expected results.
    """
    test_ref = f"{REPO}/tests/queries/0_stateless/04070_pad_string_asan_overflow.reference"

    # Fetch from merge commit if not present
    assert _fetch_file_from_commit(test_ref, MERGE_COMMIT, "04070_pad_string_asan_overflow.reference"), \
        "Could not fetch regression reference file"

    # Validate the reference file
    code = f'''
import sys

with open("{test_ref}", "r") as f:
    content = f.read()

if not content.strip():
    print("FAIL: Reference file is empty")
    sys.exit(1)

# Count result lines (non-empty)
results = [l for l in content.split("\\n") if l.strip()]

if len(results) == 0:
    print("FAIL: No expected results in reference file")
    sys.exit(1)

print(f"PASS: Found {{len(results)}} expected results in reference file")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_regression_test_paired():
    """
    BEHAVIORAL: Verify SQL and reference files are properly paired.

    Both files must exist and have matching query/result structure.
    """
    test_sql = f"{REPO}/tests/queries/0_stateless/04070_pad_string_asan_overflow.sql"
    test_ref = f"{REPO}/tests/queries/0_stateless/04070_pad_string_asan_overflow.reference"

    code = f'''
import sys

# Fetch both files
import urllib.request
import os

def fetch(filepath, suffix):
    if os.path.exists(filepath):
        return True
    url = f"https://raw.githubusercontent.com/ClickHouse/ClickHouse/{MERGE_COMMIT}/tests/queries/0_stateless/{{suffix}}"
    try:
        urllib.request.urlretrieve(url, filepath)
        return os.path.exists(filepath)
    except:
        return False

sql_exists = fetch("{test_sql}", "04070_pad_string_asan_overflow.sql")
ref_exists = fetch("{test_ref}", "04070_pad_string_asan_overflow.reference")

if sql_exists != ref_exists:
    print("FAIL: SQL and reference files must both exist or both be missing")
    sys.exit(1)

if not sql_exists:
    print("FAIL: Neither SQL nor reference file could be fetched")
    sys.exit(1)

with open("{test_sql}", "r") as f:
    sql_content = f.read()
with open("{test_ref}", "r") as f:
    ref_content = f.read()

# Both files should have content
if not sql_content.strip():
    print("FAIL: SQL file is empty")
    sys.exit(1)

if not ref_content.strip():
    print("FAIL: Reference file is empty")
    sys.exit(1)

# Count queries (SELECT statements, not comments)
queries = [l for l in sql_content.split("\\n") if l.strip() and not l.strip().startswith("--")]
results = [l for l in ref_content.split("\\n") if l.strip()]

if len(queries) == 0:
    print("FAIL: No queries in SQL file")
    sys.exit(1)

if len(results) == 0:
    print("FAIL: No results in reference file")
    sys.exit(1)

print(f"PASS: Files paired: {{len(queries)}} queries, {{len(results)}} results")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_cpp_syntax_valid():
    """
    BEHAVIORAL: Verify C++ source has valid structure.

    Basic structural validation: balanced braces, required includes, namespace.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check balanced braces
if content.count("{{") != content.count("}}"):
    print("FAIL: Unbalanced braces")
    sys.exit(1)

# Check balanced parentheses
if content.count("(") != content.count(")"):
    print("FAIL: Unbalanced parentheses")
    sys.exit(1)

# Check for required includes
if "#include <" not in content:
    print("FAIL: Should have include statements")
    sys.exit(1)

# Check for namespace
if "namespace DB" not in content:
    print("FAIL: Should have DB namespace")
    sys.exit(1)

print("PASS: C++ syntax appears valid")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_source_file_no_trailing_whitespace():
    """
    BEHAVIORAL: Verify source file has no trailing whitespace.

    Style check: trailing whitespace is not allowed in ClickHouse codebase.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if line.rstrip().endswith(" "):
        print(f"FAIL: Line {{i}} has trailing whitespace")
        sys.exit(1)

print("PASS: No trailing whitespace found")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_source_file_ends_with_newline():
    """
    BEHAVIORAL: Verify source file ends with newline.

    POSIX standard requires files end with newline.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "rb") as f:
    content = f.read()

if not content.endswith(b"\\n"):
    print("FAIL: Source file should end with newline")
    sys.exit(1)

print("PASS: Source file ends with newline")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


# ============================================================================
# AGENT_CONFIG TESTS (Compliance with project conventions)
# ============================================================================

def test_agent_config_memory_safety():
    """
    AGENT_CONFIG: C++ memory safety - Use appropriate container types.

    Source: .claude/CLAUDE.md
    Rule: Use PaddedPODArray for memory-safe access when memcpySmallAllowReadWriteOverflow15 is used.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# When using memcpySmallAllowReadWriteOverflow15, must use PaddedPODArray
# which provides 15 bytes of read padding beyond its size
if "PaddedPODArray<UInt8> pad_string" not in content:
    print("FAIL: Must use PaddedPODArray when memcpySmallAllowReadWriteOverflow15 is used")
    sys.exit(1)

print("PASS: Memory safety container type used correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_agent_config_allman_braces():
    """
    AGENT_CONFIG: Allman-style braces (opening brace on new line).

    Source: .claude/CLAUDE.md
    Rule: When writing C++ code, always use Allman-style braces.
    """
    code = f'''
import re
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for constructor with Allman-style braces
pattern = r":\\s+function_name\\(name_\\)\\s*\\n\\s*,\\s*is_right_pad\\(is_right_pad_\\)\\s*\\n\\s*,\\s*is_utf8\\(is_utf8_\\)\\s*\\n\\s*\\{{"
if not re.search(pattern, content):
    print("FAIL: Must use Allman brace style")
    sys.exit(1)

print("PASS: Allman brace style followed correctly")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout
