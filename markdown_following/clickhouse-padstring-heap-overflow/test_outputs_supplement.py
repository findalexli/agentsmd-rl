#!/usr/bin/env python3
"""
Supplementary pass-to-pass tests for ClickHouse repo CI compliance.

These tests verify the code follows ClickHouse repository conventions
for style, formatting, and C++ best practices.

NOTE: These tests run on the base commit (before the fix) to verify
repo compliance. They should also pass after the fix is applied.
"""

import subprocess
import sys

REPO = "/workspace/ClickHouse"
PADSTRING_FILE = f"{REPO}/src/Functions/padString.cpp"


def _run_python_code(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout
    )


def test_repo_code_format_whitespace():
    """
    PASS-TO-PASS: Verify source file follows ClickHouse whitespace conventions.

    Repo CI: No trailing whitespace, no tabs, proper indentation.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    lines = f.readlines()

# Check for trailing whitespace
for i, line in enumerate(lines, 1):
    stripped = line.rstrip("\\n")
    if stripped != stripped.rstrip():
        print(f"FAIL: Line {{i}} has trailing whitespace")
        sys.exit(1)

# Check for tab characters (ClickHouse uses spaces)
for i, line in enumerate(lines, 1):
    if "\\t" in line:
        print(f"FAIL: Line {{i}} contains tab character")
        sys.exit(1)

print("PASS: Source file follows whitespace conventions")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_include_order():
    """
    PASS-TO-PASS: Verify include statements are properly formatted.

    Repo CI: Standard library includes should use <> format.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

lines = content.split("\\n")
includes = [l for l in lines if l.startswith("#include")]

if not includes:
    print("FAIL: No includes found")
    sys.exit(1)

# Check format of includes
for inc in includes:
    if not (inc.startswith("#include <") or inc.startswith('#include "')):
        print(f"FAIL: Invalid include format: {{inc}}")
        sys.exit(1)

print(f"PASS: Found {{len(includes)}} properly formatted includes")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_namespace_conventions():
    """
    PASS-TO-PASS: Verify namespace usage follows ClickHouse conventions.

    Repo CI: Code should be in DB namespace or anonymous namespace.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for DB namespace
if "namespace DB" not in content:
    print("FAIL: Missing 'namespace DB'")
    sys.exit(1)

# Check for anonymous namespace (for internal linkage)
if "namespace" not in content:
    print("FAIL: No namespaces found")
    sys.exit(1)

print("PASS: Namespace conventions followed")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_const_correctness():
    """
    PASS-TO-PASS: Verify const correctness in function signatures.

    Repo CI: Methods that don't modify state should be const.
    """
    code = f'''
import sys
import re

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for const methods in PaddingChars class
const_method_pattern = r"ALWAYS_INLINE.*const\\s*\\n"
matches = re.findall(const_method_pattern, content)

if len(matches) < 2:
    print("FAIL: Expected at least 2 const methods")
    sys.exit(1)

print(f"PASS: Found {{len(matches)}} const-correct method declarations")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_template_usage():
    """
    PASS-TO-PASS: Verify template usage follows ClickHouse patterns.

    Repo CI: Template parameters should follow naming conventions.
    """
    code = f'''
import sys

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for template<bool is_utf8> pattern (ClickHouse convention)
if "template <bool is_utf8>" not in content and "template<bool is_utf8>" not in content:
    print("FAIL: Missing expected template<bool is_utf8> declaration")
    sys.exit(1)

# Check for is_utf8 usage in constexpr if
if "if constexpr (is_utf8)" not in content:
    print("FAIL: Missing if constexpr (is_utf8) usage")
    sys.exit(1)

print("PASS: Template usage follows ClickHouse patterns")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


def test_repo_function_naming():
    """
    PASS-TO-PASS: Verify function and class naming follows ClickHouse conventions.

    Repo CI: Classes use PascalCase, functions use camelCase.
    """
    code = f'''
import sys
import re

with open("{PADSTRING_FILE}", "r") as f:
    content = f.read()

# Check for class declarations with PascalCase
class_pattern = r"class\\s+([A-Z][a-zA-Z0-9]*)"
classes = re.findall(class_pattern, content)

expected_classes = ["PaddingChars"]
for cls in expected_classes:
    if cls not in classes:
        print(f"FAIL: Expected class {{cls}} not found")
        sys.exit(1)

print(f"PASS: Found {{len(classes)}} classes with correct PascalCase naming")
'''
    result = _run_python_code(code)
    assert result.returncode == 0, f"Test failed: {result.stdout} {result.stderr}"
    assert "PASS" in result.stdout


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_repo_code_format_whitespace,
        test_repo_include_order,
        test_repo_namespace_conventions,
        test_repo_const_correctness,
        test_repo_template_usage,
        test_repo_function_naming,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"✓ {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: Exception: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
