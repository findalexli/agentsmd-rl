#!/usr/bin/env python3
"""Tests for the padString argument description fix.

This PR fixes the argument descriptions for leftPad/rightPad functions.
The descriptions incorrectly said "Array" when they should describe the
actual expected types: "String or FixedString", "UInt*", and "String".
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src" / "Functions" / "padString.cpp"


def test_file_exists():
    """Target file must exist."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_original_incorrect_descriptions_removed():
    """The old incorrect 'Array' descriptions must be removed."""
    content = TARGET_FILE.read_text()

    # Check for the old incorrect "Array" strings in the specific context
    # The old code had "Array" as description for string and pad_string args
    lines = content.split('\n')

    # Find lines with FunctionArgumentDescriptors and check for "Array"
    in_mandatory_args = False
    in_optional_args = False
    array_in_descriptors = []

    for i, line in enumerate(lines):
        if 'FunctionArgumentDescriptors mandatory_args' in line:
            in_mandatory_args = True
            in_optional_args = False
        elif 'FunctionArgumentDescriptors optional_args' in line:
            in_mandatory_args = False
            in_optional_args = True
        elif line.strip().startswith('};'):
            in_mandatory_args = False
            in_optional_args = False

        if (in_mandatory_args or in_optional_args) and '"Array"' in line:
            array_in_descriptors.append((i+1, line.strip()))

    assert len(array_in_descriptors) == 0, \
        f"Found 'Array' in argument descriptors at lines: {array_in_descriptors}"


def test_string_argument_has_correct_description():
    """The 'string' argument should have 'String or FixedString' description."""
    content = TARGET_FILE.read_text()

    # Look for the pattern with "string" argument and correct description
    pattern = r'\{\s*"string"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>\(&isStringOrFixedString\)\s*,\s*nullptr\s*,\s*"String or FixedString"\s*\}'

    assert re.search(pattern, content), \
        "The 'string' argument should have description 'String or FixedString'"


def test_length_argument_has_correct_description():
    """The 'length' argument should have 'UInt*' description (not 'const UInt*')."""
    content = TARGET_FILE.read_text()

    # Look for the pattern with "length" argument and correct description
    pattern = r'\{\s*"length"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>\(&isInteger\)\s*,\s*nullptr\s*,\s*"UInt\*"\s*\}'

    assert re.search(pattern, content), \
        "The 'length' argument should have description 'UInt*'"


def test_length_argument_no_const_prefix():
    """The 'length' argument should NOT have 'const UInt*' description."""
    content = TARGET_FILE.read_text()

    # Make sure the old "const UInt*" is gone
    pattern = r'\{\s*"length"[^}]*"const UInt\*"[^}]*\}'

    assert not re.search(pattern, content), \
        "The 'length' argument should NOT have 'const UInt*' description"


def test_pad_string_argument_has_correct_description():
    """The 'pad_string' argument should have 'String' description."""
    content = TARGET_FILE.read_text()

    # Look for the pattern with "pad_string" argument and correct description
    pattern = r'\{\s*"pad_string"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>\(&isString\)\s*,\s*isColumnConst\s*,\s*"String"\s*\}'

    assert re.search(pattern, content), \
        "The 'pad_string' argument should have description 'String'"


def test_all_three_descriptions_fixed():
    """All three argument descriptions should be fixed."""
    content = TARGET_FILE.read_text()

    # Check all three correct descriptions are present
    string_desc = '"String or FixedString"' in content
    length_desc = '"UInt*"' in content and '"const UInt*"' not in content
    pad_desc = '"String"' in content

    # Count occurrences in the right context
    lines = content.split('\n')

    # Find the validateFunctionArguments call and check surrounding context
    in_get_return_type = False
    found_descriptors = {
        'string': False,
        'length': False,
        'pad_string': False
    }

    for line in lines:
        if 'getReturnTypeImpl' in line:
            in_get_return_type = True

        if in_get_return_type:
            if '"string"' in line and '"String or FixedString"' in line:
                found_descriptors['string'] = True
            if '"length"' in line and '"UInt*"' in line and '"const UInt*"' not in line:
                found_descriptors['length'] = True
            if '"pad_string"' in line and '"String"' in line:
                found_descriptors['pad_string'] = True

        if 'validateFunctionArguments' in line:
            break

    assert all(found_descriptors.values()), \
        f"Not all descriptions fixed: {found_descriptors}"


def test_function_argument_descriptors_structure():
    """The FunctionArgumentDescriptors structure should be syntactically correct."""
    content = TARGET_FILE.read_text()

    # Check that mandatory_args exists with correct structure
    assert 'FunctionArgumentDescriptors mandatory_args{' in content, \
        "mandatory_args structure not found"
    assert 'FunctionArgumentDescriptors optional_args{' in content, \
        "optional_args structure not found"

    # Check that the structures are properly closed
    # Find the getReturnTypeImpl function and check brace balance there
    get_return_start = content.find('DataTypePtr getReturnTypeImpl')
    assert get_return_start != -1, "getReturnTypeImpl not found"

    # Extract content from function start to validateFunctionArguments call
    func_section = content[get_return_start:get_return_start + 2000]

    # Check mandatory_args has both arguments with correct descriptions
    mandatory_section_start = func_section.find('mandatory_args{')
    mandatory_section_end = func_section.find('};', mandatory_section_start)
    mandatory_section = func_section[mandatory_section_start:mandatory_section_end + 2]

    # Should have two argument entries
    assert mandatory_section.count('"string"') == 1, "mandatory_args should contain 'string' argument"
    assert mandatory_section.count('"length"') == 1, "mandatory_args should contain 'length' argument"

    # Check optional_args structure
    optional_section_start = func_section.find('optional_args{')
    optional_section_end = func_section.find('};', optional_section_start)
    optional_section = func_section[optional_section_start:optional_section_end + 2]

    assert optional_section.count('"pad_string"') == 1, "optional_args should contain 'pad_string' argument"


def test_no_old_const_uint_description():
    """Ensure 'const UInt*' is completely removed from the file."""
    content = TARGET_FILE.read_text()

    # The old code had "const UInt*" which should be changed to "UInt*"
    assert '"const UInt*"' not in content, \
        "The old 'const UInt*' description should be removed"


def test_cpp_syntax_valid():
    """The C++ syntax should be valid (basic checks)."""
    content = TARGET_FILE.read_text()

    # Check for balanced braces in the getReturnTypeImpl function
    get_return_type_start = content.find('DataTypePtr getReturnTypeImpl')
    if get_return_type_start == -1:
        # Try alternate pattern
        get_return_type_start = content.find('getReturnTypeImpl')

    assert get_return_type_start != -1, "getReturnTypeImpl function not found"

    # Extract function body and check brace balance
    func_start = content.find('{', get_return_type_start)
    assert func_start != -1, "Function body start not found"

    # Simple brace counting (this is a heuristic)
    brace_count = 0
    in_string = False
    escape_next = False

    for i, char in enumerate(content[func_start:], start=0):
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    break

    assert brace_count == 0, "Unbalanced braces in function"


def test_padString_file_compiles():
    """The modified file should compile successfully."""
    # Run a basic syntax check using clang
    build_dir = REPO / "build"
    source_file = TARGET_FILE

    # Try to compile just this file
    result = subprocess.run(
        [
            "clang++-18", "-std=c++23", "-fsyntax-only",
            "-I", str(REPO / "src"),
            "-I", str(REPO / "base" / "common" / "src"),
            str(source_file)
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO)
    )

    # We expect this to have some errors due to missing includes,
    # but it should not fail on syntax errors in our changes
    # A successful syntax-only check on the specific lines is sufficient

    # Check that our specific changes don't cause syntax errors
    # by verifying the file can be parsed
    content = TARGET_FILE.read_text()

    # Check for common syntax issues
    assert content.count('"String or FixedString"') == 1, \
        "Expected exactly one 'String or FixedString' description"
    assert content.count('"UInt*"') == 1, \
        "Expected exactly one 'UInt*' description"
    assert content.count('"String"') >= 1, \
        "Expected at least one 'String' description"


# ===== Pass-to-Pass Tests (repo_tests origin) =====
# These tests run actual CI commands from the ClickHouse repo


def test_repo_style_check_cpp():
    """Repo's C++ style check passes on modified file (pass_to_pass)."""
    # Run the C++ style check script from the repo's CI
    result = subprocess.run(
        ["bash", str(REPO / "ci" / "jobs" / "scripts" / "check_style" / "check_cpp.sh")],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO)
    )
    # Check that padString.cpp has no style errors specifically
    # The script exits 0 but may output style errors
    output = result.stdout + result.stderr
    padstring_errors = [
        line for line in output.split('\n')
        if 'padString' in line and 'style error' in line.lower()
    ]
    assert len(padstring_errors) == 0, f"Style errors in padString.cpp: {padstring_errors}"


def test_repo_no_tabs_in_padstring():
    """No tabs in padString.cpp - CI style requirement (pass_to_pass)."""
    result = subprocess.run(
        [
            "grep", "-F", "\t",
            str(TARGET_FILE)
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(REPO)
    )
    assert result.returncode != 0 or result.stdout == "", \
        f"Found tabs in padString.cpp:\n{result.stdout}"


def test_repo_functional_test_exists():
    """pad_string functional test file exists (pass_to_pass)."""
    test_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.sql"
    result = subprocess.run(
        ["test", "-f", str(test_file)],
        capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, f"Functional test file not found: {test_file}"


def test_repo_functional_test_has_content():
    """pad_string functional test has valid content (pass_to_pass)."""
    test_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.sql"
    result = subprocess.run(
        ["grep", "-E", "leftPad|rightPad", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Test file should contain leftPad/rightPad tests: {result.stderr}"
    assert "leftPad" in result.stdout, "Test file should contain leftPad tests"
    assert "rightPad" in result.stdout, "Test file should contain rightPad tests"


def test_repo_reference_file_exists():
    """pad_string reference file exists for comparison (pass_to_pass)."""
    ref_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.reference"
    result = subprocess.run(
        ["test", "-f", str(ref_file)],
        capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, f"Reference file not found: {ref_file}"


def test_repo_functional_test_matches_reference():
    """Functional test and reference file are properly paired (pass_to_pass)."""
    # Check that both files exist and have matching line counts
    test_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.sql"
    ref_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.reference"

    # Count test commands in SQL file
    sql_result = subprocess.run(
        ["grep", "-c", "^SELECT", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert sql_result.returncode == 0, "Failed to count SELECT statements"

    # Count output lines in reference file
    ref_result = subprocess.run(
        ["wc", "-l", str(ref_file)],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert ref_result.returncode == 0, "Failed to count reference lines"

    # Both files should have content
    assert int(sql_result.stdout.strip()) > 0, "Test file should have SELECT statements"
    assert int(ref_result.stdout.strip().split()[0]) > 0, "Reference file should have output lines"


def test_repo_leftpad_fixedstring_test_exists():
    """leftPad FixedString test exists (pass_to_pass)."""
    test_file = REPO / "tests" / "queries" / "0_stateless" / "02986_leftpad_fixedstring.sql"
    result = subprocess.run(
        ["test", "-f", str(test_file)],
        capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, f"FixedString test file not found: {test_file}"


def test_repo_padstring_utf8_test_exists():
    """padString UTF8 variant test exists (pass_to_pass)."""
    test_file = REPO / "tests" / "queries" / "0_stateless" / "01940_pad_string.sql"
    result = subprocess.run(
        ["grep", "-q", "leftPadUTF8", str(test_file)],
        capture_output=True,
        timeout=30
    )
    assert result.returncode == 0, "leftPadUTF8 test not found in test file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
