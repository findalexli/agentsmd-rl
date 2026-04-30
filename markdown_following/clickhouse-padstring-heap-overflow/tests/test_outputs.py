#!/usr/bin/env python3
"""
Tests for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

The bug: memcpySmallAllowReadWriteOverflow15 requires 15 bytes of readable padding
beyond the buffer. Using String (std::string) for pad_string didn't provide this,
causing heap-buffer-overflow on ASan builds.
"""

import subprocess
import sys

REPO = "/workspace/ClickHouse"
PADSTRING_FILE = f"{REPO}/src/Functions/padString.cpp"

def _run_check(script, timeout=30):
    """Run an inline Python check script against the target source file."""
    r = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )
    return r


# ============================================================================
# FAIL-TO-PASS TESTS
# ============================================================================

def test_padded_pod_array_storage():
    """pad_string member uses PaddedPODArray<UInt8> for 15-byte read padding."""
    r = _run_check(f"""
import re, sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

class_start = content.find('class PaddingChars')
if class_start < 0:
    print("FAIL: PaddingChars class not found")
    sys.exit(1)

private_start = content.find('private:', class_start)
if private_start < 0:
    print("FAIL: no private section in PaddingChars")
    sys.exit(1)

class_end = content.find('}};', private_start)
private_section = content[private_start:class_end] if class_end > 0 else content[private_start:]

if 'PaddedPODArray<UInt8>' not in private_section:
    print("FAIL: pad_string storage must use PaddedPODArray<UInt8> for memory padding")
    sys.exit(1)

if re.search(r'\\bString\\s+pad_string\\s*;', private_section):
    print("FAIL: pad_string still uses String which lacks padding guarantee")
    sys.exit(1)

if 'pad_string' not in private_section:
    print("FAIL: pad_string member not found")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_insert_from_itself_usage():
    """Padding expansion uses insertFromItself, not += ."""
    r = _run_check(f"""
import re, sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'insertFromItself' not in content:
    print("FAIL: insertFromItself not found - expansion method missing")
    sys.exit(1)

if re.search(r'pad_string\\s*\\+=\\s*pad_string', content):
    print("FAIL: unsafe += self-concatenation still used for pad_string")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_empty_pad_string_handling():
    """Empty pad_string defaults to space in executeImpl, not in removed init()."""
    r = _run_check(f"""
import sys, re
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'void init()' in content:
    print("FAIL: init() method should not exist")
    sys.exit(1)

if 'PaddingChars' not in content:
    print("FAIL: PaddingChars class not found")
    sys.exit(1)

impl_start = content.find('ColumnPtr executeImpl')
if impl_start < 0:
    print("FAIL: executeImpl not found")
    sys.exit(1)

impl_region = content[impl_start:impl_start + 4000]
if 'pad_string.empty()' not in impl_region:
    print("FAIL: empty pad_string check missing from executeImpl")
    sys.exit(1)

if 'pad_string = " "' not in impl_region:
    print("FAIL: pad_string space default missing from executeImpl")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_chassert_used_after_validation():
    """Uses chassert for invariant checks after argument validation."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'chassert' not in content:
    print("FAIL: chassert not used")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_validate_function_arguments():
    """Uses validateFunctionArguments with FunctionArgumentDescriptors."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'validateFunctionArguments' not in content:
    print("FAIL: validateFunctionArguments not used")
    sys.exit(1)

if 'FunctionArgumentDescriptors' not in content:
    print("FAIL: FunctionArgumentDescriptors not found")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_error_codes_cleaned():
    """Removes unused ILLEGAL_TYPE_OF_ARGUMENT and NUMBER_OF_ARGUMENTS_DOESNT_MATCH."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'ILLEGAL_TYPE_OF_ARGUMENT' in content:
    print("FAIL: ILLEGAL_TYPE_OF_ARGUMENT should be removed")
    sys.exit(1)

if 'NUMBER_OF_ARGUMENTS_DOESNT_MATCH' in content:
    print("FAIL: NUMBER_OF_ARGUMENTS_DOESNT_MATCH should be removed")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_num_chars_comparison_explicit():
    """Uses explicit if (num_chars == 0) instead of if (!num_chars)."""
    r = _run_check(f"""
import re, sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'num_chars == 0' not in content:
    print("FAIL: explicit num_chars == 0 comparison not found")
    sys.exit(1)

if re.search(r'\\bif\\s*\\(\\s*!\\s*num_chars\\s*\\)', content):
    print("FAIL: implicit !num_chars still used")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_digit_separator_used():
    """Uses C++14 digit separator 1'000'000 for large numeric literal."""
    r = _run_check(f"""
import sys, re
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if "1'000'000" not in content:
    print("FAIL: C++14 digit separator not used for 1000000")
    sys.exit(1)

if re.search(r'\\b1000000\\b', content) and "1'000'000" not in content:
    print("FAIL: bare 1000000 still present without digit separator")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_function_signature_updated():
    """getReturnTypeImpl uses ColumnsWithTypeAndName, not DataTypes."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    lines = f.readlines()

# Find the getReturnTypeImpl declaration line
for i, line in enumerate(lines):
    if 'getReturnTypeImpl' in line and 'override' in line:
        if 'ColumnsWithTypeAndName' not in line:
            print(f"FAIL: getReturnTypeImpl on line {{i+1}} must use ColumnsWithTypeAndName")
            sys.exit(1)
        break
else:
    print("FAIL: getReturnTypeImpl declaration not found")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_includes_updated():
    """Adds required #include <memory> and #include <DataTypes/IDataType.h>."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if '#include <memory>' not in content:
    print("FAIL: missing #include <memory>")
    sys.exit(1)

if '#include <DataTypes/IDataType.h>' not in content:
    print("FAIL: missing #include <DataTypes/IDataType.h>")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_utf8_size_not_length():
    """UTF-8 path uses size() instead of length() for PaddedPODArray compatibility."""
    r = _run_check(f"""
import re, sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

if 'pad_string.size()' not in content:
    print("FAIL: pad_string.size() not found - must use size() not length()")
    sys.exit(1)

if 'pad_string.length()' in content:
    print("FAIL: pad_string.length() still used - must use size() instead")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_allman_brace_style():
    """FunctionPadString constructor uses Allman brace style."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    content = f.read()

ctor_start = content.find('FunctionPadString(const char * name_')
if ctor_start < 0:
    print("FAIL: FunctionPadString constructor not found")
    sys.exit(1)

ctor_end = content.find('{{', ctor_start)
ctor_block = content[ctor_start:ctor_end]
ctor_lines = ctor_block.split('\\n')

# In Allman style, no line before the opening brace should end with {{
for line in ctor_lines:
    stripped = line.strip()
    if stripped.endswith('{{') and len(stripped) > 1:
        print("FAIL: constructor uses K&R brace style (brace on same line)")
        sys.exit(1)

# Verify the opening brace exists somewhere after the signature
brace_pos = content.find('{{', ctor_end)
if brace_pos < 0:
    brace_pos = ctor_end

# The opening brace line should have {{ at start or be {{}} (empty body)
brace_line_start = content.rfind('\\n', 0, brace_pos) + 1
brace_line = content[brace_line_start:brace_line_start + 40].split('\\n')[0].strip()
if not (brace_line.startswith('{{') or brace_line == '{{}}'):
    print(f"FAIL: constructor brace not in Allman style, got: {{brace_line!r}}")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


def test_write_slice_no_cast():
    """writeSlice calls pass pad_string.data() without reinterpret_cast."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if 'writeSlice' in line and 'reinterpret_cast' in line:
        print(f"FAIL: writeSlice on line {{i}} still uses reinterpret_cast")
        sys.exit(1)

if 'writeSlice' not in ''.join(lines):
    print("FAIL: writeSlice calls not found")
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"STDOUT: {r.stdout}\nSTDERR: {r.stderr}"
    assert "PASS" in r.stdout


# ============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD compliance - regression guards)
# ============================================================================

def test_repo_git_initialized():
    """CI: Git repository is properly initialized."""
    subprocess.run(["git", "init"], capture_output=True, text=True, timeout=30, cwd=REPO)
    r = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0, f"Git status failed:\n{r.stderr[-500:]}"


def test_repo_no_duplicate_includes():
    """CI: No duplicate #include statements."""
    r = _run_check(f"""
import re, sys
with open("{PADSTRING_FILE}", 'r', encoding='utf-8', errors='ignore') as f:
    includes = []
    for line in f:
        if re.match(r'^#include ', line):
            includes.append(line.strip())

include_counts = {{line: includes.count(line) for line in includes}}
duplicates = {{line: count for line, count in include_counts.items() if count > 1}}
if duplicates:
    print(f"FAIL: Duplicate includes: {{duplicates}}")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_trailing_whitespace():
    """CI: Source file has no trailing whitespace."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if line.rstrip('\\n').rstrip('\\r').endswith(' ') or line.rstrip('\\n').rstrip('\\r').endswith('\\t'):
        print(f"FAIL: Line {{i}} has trailing whitespace")
        sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_tabs():
    """CI: Source file uses spaces, not tabs."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
if '\\t' in content:
    print("FAIL: Tabs found in source file")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_balanced_braces():
    """CI: C++ source has balanced braces and parentheses."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
if content.count('{{') != content.count('}}'):
    print("FAIL: Unbalanced braces")
    sys.exit(1)
if content.count('(') != content.count(')'):
    print("FAIL: Unbalanced parentheses")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_file_ends_with_newline():
    """CI: Source file ends with newline (POSIX)."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'rb') as f:
    content = f.read()
if not content.endswith(b'\\n'):
    print("FAIL: Source file should end with newline")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_shell_scripts_parse():
    """CI: Shell scripts pass bash -n syntax check."""
    r = subprocess.run(
        ["bash", "-n", "/tests/test.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Shell syntax check failed:\n{r.stderr[-500:]}"


def test_repo_no_crlf():
    """CI: Source file has no CRLF line endings."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'rb') as f:
    content = f.read()
if b'\\r\\n' in content:
    print("FAIL: CRLF line endings found")
    sys.exit(1)
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_multiple_empty_lines():
    """CI: No more than 2 consecutive empty lines."""
    r = _run_check(f"""
import sys
with open("{PADSTRING_FILE}", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
consecutive_empty = 0
for i, line in enumerate(lines, 1):
    if line.strip() == '':
        consecutive_empty += 1
        if consecutive_empty > 2:
            print(f"FAIL: More than 2 consecutive empty lines at line {{i}}")
            sys.exit(1)
    else:
        consecutive_empty = 0
print("PASS")
""")
    assert r.returncode == 0, f"STDERR: {r.stderr[-500:]}"
    assert "PASS" in r.stdout
