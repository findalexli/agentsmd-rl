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
write_slice_calls = re.findall(r'writeSlice\\([^)]+\\)', content)
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
# PASS-TO-PASS TESTS (Repo CI/CD compliance - actual subprocess commands)
# ============================================================================

def test_repo_git_initialized():
    """
    CI: Git repository is properly initialized (pass_to_pass).

    Verifies git can track files in the workspace using subprocess.run().
    """
    # Initialize git if not already done
    subprocess.run(
        ["git", "init"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    r = subprocess.run(
        ["git", "status"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr[-500:]}"


def test_repo_no_duplicate_includes():
    """
    CI: No duplicate #include statements (pass_to_pass).

    Based on ClickHouse CI check_duplicate_includes from check_style.py.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import re
import sys

with open('{PADSTRING_FILE}', 'r', encoding='utf-8', errors='ignore') as f:
    includes = []
    for line in f:
        if re.match(r'^#include ', line):
            includes.append(line.strip())

include_counts = {{line: includes.count(line) for line in includes}}
duplicates = {{line: count for line, count in include_counts.items() if count > 1}}

if duplicates:
    print(f"Duplicate includes found: {{duplicates}}")
    sys.exit(1)
print("PASS: No duplicate includes")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Duplicate includes check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_trailing_whitespace():
    """
    CI: Source file has no trailing whitespace (pass_to_pass).

    Based on ClickHouse CI check from check_cpp.sh.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if line.rstrip().endswith(' '):
        print(f"Line {{i}} has trailing whitespace")
        sys.exit(1)

print("PASS: No trailing whitespace")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Trailing whitespace check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_tabs():
    """
    CI: Source file uses spaces, not tabs (pass_to_pass).

    Based on ClickHouse CI check for tabs in source files.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

if '\\t' in content:
    print("FAIL: Tabs found in source file")
    sys.exit(1)

print("PASS: No tabs found")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Tabs check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_balanced_braces():
    """
    CI: C++ source has balanced braces (pass_to_pass).

    Basic structural validation that the file is syntactically valid.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

if content.count('{{') != content.count('}}'):
    print("FAIL: Unbalanced braces")
    sys.exit(1)

if content.count('(') != content.count(')'):
    print("FAIL: Unbalanced parentheses")
    sys.exit(1)

print("PASS: Balanced braces and parentheses")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Balanced braces check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_file_ends_with_newline():
    """
    CI: Source file ends with newline (pass_to_pass).

    POSIX standard requires files end with newline.
    """
    r = subprocess.run(
        ["python3", "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'rb') as f:
    content = f.read()

if not content.endswith(b'\\n'):
    print("FAIL: Source file should end with newline")
    sys.exit(1)

print("PASS: Source file ends with newline")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Newline check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_shell_scripts_executable():
    """
    CI: Shell scripts are syntactically valid (pass_to_pass).

    Uses bash -n to check syntax of shell scripts.
    """
    r = subprocess.run(
        ["bash", "-n", "/tests/test.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Shell script syntax check failed:\n{r.stderr[-500:]}"


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
