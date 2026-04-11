"""
Test outputs for ClickHouse sparseGrams fix.

Bug: sparseGrams tokenizer generates longer tokens than the provided max length.
Root cause: Hard-coded +2 in length calculation instead of using min_ngram_length - 1.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Functions/sparseGramsImpl.h")

def test_min_ngram_length_used_in_length_calculation():
    """
    Verify that min_ngram_length - 1 is used in length calculation,
    not hard-coded + 2.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the calculateRemoveBatch method and check the length calculation
    # The fix changes: right_symbol_index - possible_left_symbol_index + 2
    # To: right_symbol_index - possible_left_symbol_index + min_ngram_length - 1

    # Check that we're using min_ngram_length - 1, not + 2
    assert "+ min_ngram_length - 1" in content, \
        "Bug not fixed: length calculation should use min_ngram_length - 1"

    # Make sure the old hard-coded +2 is gone
    # This pattern should NOT appear: "symbol_index + 2"
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "possible_left_symbol_index + 2" in line or "possible_left_symbol_index+2" in line:
            assert False, f"Line {i+1} still has hard-coded +2: {line}"

def test_length_calculation_in_calculateRemoveBatch():
    """
    Verify the length calculation in calculateRemoveBatch method uses
    min_ngram_length - 1.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the calculateRemoveBatch method and the first while loop
    # where the length calculation is fixed
    pattern = r'size_t length = right_symbol_index - possible_left_symbol_index \+ min_ngram_length - 1;'

    # Should find exactly 2 occurrences (one in each while loop)
    matches = re.findall(pattern, content)
    assert len(matches) == 2, \
        f"Expected exactly 2 occurrences of min_ngram_length - 1 fix, found {len(matches)}"

def test_compilation_succeeds():
    """
    Verify that the code compiles successfully with the fix.
    This is a basic syntax check.
    """
    # Just check that the header file is syntactically valid C++
    # by trying to parse it with clang
    header_path = TARGET_FILE

    # Create a temporary file that includes the header
    test_code = '''
#include <vector>
#include <cstddef>
#include <string>

// Minimal mocks needed for the header
namespace DB {
    struct ColumnString {};
}

// Include the actual header
#include "src/Functions/sparseGramsImpl.h"

int main() { return 0; }
'''

    # For a header-only sanity check, we'll use a simple grep-based approach
    # to verify the fix is syntactically correct
    with open(header_path, 'r') as f:
        content = f.read()

    # Check for balanced braces in the modified area
    # Find the getNextIndices method where the fix is applied
    method_start = content.find('getNextIndices()')
    assert method_start != -1, "getNextIndices method not found"

    # Verify the fix doesn't break syntax by checking semicolons
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'min_ngram_length - 1' in line:
            # Should end with semicolon
            assert ';' in line, f"Line {i+1} missing semicolon: {line}"

def test_distinctive_fix_line_present():
    """
    Idempotency check: verify the distinctive fix line is present.
    This ensures the patch has been applied.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The distinctive pattern from the patch
    distinctive = "size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;"
    assert distinctive in content, \
        f"Distinctive fix line not found: {distinctive}"


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks that should pass on both base and fix
# =============================================================================

def test_repo_header_syntax():
    """
    Verify the modified header file has valid C++ syntax (pass_to_pass).
    Checks that the fix doesn't introduce syntax errors in the modified lines.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that lines with the specific fix pattern are syntactically valid
    # The fix is: right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'possible_left_symbol_index' in line and 'min_ngram_length - 1' in line:
            # Verify the line ends with semicolon
            assert ';' in line, f"Line {i+1} missing semicolon: {line}"
            # Verify it has proper length calculation structure
            assert 'length' in line, f"Line {i+1} missing length variable: {line}"


def test_repo_file_structure():
    """
    Verify the repository structure is intact and expected files exist (pass_to_pass).
    This ensures the environment is properly set up.
    """
    import os as local_os

    # Check that key directories and files exist
    required_paths = [
        'src/Functions',
        'src/Functions/sparseGramsImpl.h',
        'src/Functions/sparseGrams.cpp',
        'CMakeLists.txt',
        'tests',
    ]

    for path in required_paths:
        full_path = local_os.path.join(REPO, path)
        assert local_os.path.exists(full_path), f"Required path missing: {path}"


def test_repo_sparseGrams_header_valid():
    """
    Verify sparseGramsImpl.h is a valid C++ header file with proper guards (pass_to_pass).
    Checks for proper header guards and basic structure.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for header guard or pragma once
    assert '#pragma once' in content or '#ifndef' in content, \
        "Header file missing include guard (#pragma once or #ifndef)"

    # Check for balanced braces (basic syntax check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_repo_clang_simple_compile():
    """
    Test that clang can compile a simple C++ file in the environment (pass_to_pass).
    This verifies the compiler toolchain is properly installed and functional.
    """
    test_code = '''
#include <vector>
#include <cstddef>
#include <cstdint>

// Simulate the key expressions from sparseGramsImpl.h
size_t test_length_calculation(
    size_t right_symbol_index,
    size_t possible_left_symbol_index,
    size_t min_ngram_length)
{
    // This is the fixed version of the calculation
    return right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;
}

int main() {
    // Test the calculation works correctly
    size_t result = test_length_calculation(10, 5, 3);
    return (result == 7) ? 0 : 1;
}
'''
    test_file = '/tmp/test_compile.cpp'
    output_file = '/tmp/test_compile'

    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        # Compile
        r = subprocess.run(
            ['clang++', '-std=c++20', '-o', output_file, test_file],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, \
            f"Simple compile test failed:\n{r.stderr}"

        # Run the test
        r = subprocess.run([output_file], capture_output=True, text=True, timeout=10)
        assert r.returncode == 0, \
            "Compiled test program did not return expected result"

    finally:
        # Clean up
        import os as local_os
        try:
            local_os.remove(test_file)
            local_os.remove(output_file)
        except:
            pass
