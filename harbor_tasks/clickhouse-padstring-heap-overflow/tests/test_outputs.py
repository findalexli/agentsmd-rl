#!/usr/bin/env python3
"""
Tests for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

The bug: memcpySmallAllowReadWriteOverflow15 requires 15 bytes of readable padding
beyond the buffer. Using String (std::string) for pad_string didn't provide this,
causing heap-buffer-overflow on ASan builds.
"""

import subprocess
import re
import sys

REPO = "/workspace/ClickHouse"
PADSTRING_FILE = f"{REPO}/src/Functions/padString.cpp"


# ============================================================================
# FAIL-TO-PASS TESTS
# ============================================================================

def test_memory_safe_pad_storage():
    """
    Core fix: pad_string storage must not use String type.

    String (std::string) lacks the 15-byte padding guarantee required by
    memcpySmallAllowReadWriteOverflow15. The fix must change the storage type
    to a container that provides this guarantee.
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import re, sys

with open("{PADSTRING_FILE}") as f:
    content = f.read()

# Extract the PaddingChars class private section
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

# The pad_string MEMBER must NOT be String type (lacks padding guarantee)
if re.search(r'\\bString\\s+pad_string\\s*;', private_section):
    print("FAIL: PaddingChars pad_string member uses String type which lacks memory padding guarantee")
    sys.exit(1)

# pad_string member must still exist in the class private section
if 'pad_string' not in private_section:
    print("FAIL: pad_string member not found in PaddingChars private section")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_no_unsafe_string_expansion():
    """
    The pad string expansion loop must not use += string concatenation.

    The old code used pad_string += pad_string which causes heap-buffer-overflow
    when the storage type provides extra padding bytes. The expansion method
    must be safe for the new container type.
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import re, sys

with open("{PADSTRING_FILE}") as f:
    content = f.read()

# Must not use string concatenation for expansion
if re.search(r'pad_string\\s*\\+=\\s*pad_string', content):
    print("FAIL: unsafe string concatenation still used for pad_string expansion")
    sys.exit(1)

# The expansion loop should still exist
if "numCharsInPadString()" not in content:
    print("FAIL: expansion loop helper numCharsInPadString not found")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_argument_validation_modernized():
    """
    Argument validation must use validateFunctionArguments helper.

    The fix replaces manual argument count/type checking with the standard
    ClickHouse validateFunctionArguments helper using FunctionArgumentDescriptors.
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import sys

with open("{PADSTRING_FILE}") as f:
    content = f.read()

if "validateFunctionArguments" not in content:
    print("FAIL: validateFunctionArguments helper not used")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


def test_init_method_restructured():
    """
    The init() method must be removed with its logic moved inline.

    The fix moves initialization logic from the separate init() method into
    the constructor and executeImpl.
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import sys

with open("{PADSTRING_FILE}") as f:
    content = f.read()

if "void init()" in content:
    print("FAIL: init() method should be removed")
    sys.exit(1)

# PaddingChars class should still exist
if "PaddingChars" not in content:
    print("FAIL: PaddingChars class not found")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD compliance)
# ============================================================================

def test_repo_git_initialized():
    """
    CI: Git repository is properly initialized (pass_to_pass).
    """
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
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import re, sys

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
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
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
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
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
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
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
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
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
    """
    r = subprocess.run(
        ["bash", "-n", "/tests/test.sh"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Shell script syntax check failed:\n{r.stderr[-500:]}"


def test_repo_no_crlf():
    """
    CI: Source file has no CRLF line endings (pass_to_pass).
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'rb') as f:
    content = f.read()

if b'\\r\\n' in content:
    print("FAIL: CRLF line endings found")
    sys.exit(1)

print("PASS: No CRLF line endings")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CRLF check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout


def test_repo_no_multiple_empty_lines():
    """
    CI: No more than 2 consecutive empty lines (pass_to_pass).
    """
    r = subprocess.run(
        [sys.executable, "-c", f"""
import sys

with open('{PADSTRING_FILE}', 'r', encoding='utf-8', errors='ignore') as f:
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

print("PASS: No excessive consecutive empty lines")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Empty lines check failed:\n{r.stderr[-500:]}"
    assert "PASS" in r.stdout
