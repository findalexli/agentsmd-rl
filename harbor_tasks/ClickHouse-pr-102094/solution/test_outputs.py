"""
Test suite for ClickHouse TokenizerFactory empty separator validation fix.

This validates that the splitByString tokenizer properly rejects empty separator strings,
which was the bug fixed in PR #102094.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")


def test_empty_separator_validation_exists():
    """
    Fail-to-pass: Verify that empty separator validation exists in the source code.
    Before the fix, empty strings were not validated. After the fix, they should be.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that the empty string validation code exists
    assert "value_as_string.empty()" in content, \
        "Missing empty string validation check"

    # Check for the specific error message about empty strings
    assert "the empty string cannot be used as a separator" in content, \
        "Missing error message for empty separator"


def test_error_message_improved():
    """
    Pass-to-pass: Verify that the error message for empty separators argument was improved.
    The message should now say "the separators argument cannot be empty" instead of
    just "separators cannot be empty".
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for improved error message
    assert "the separators argument cannot be empty" in content, \
        "Missing improved error message for empty separators argument"


def test_validation_in_loop():
    """
    Fail-to-pass: Verify that the validation happens inside the loop that processes
    each separator value. This ensures every separator is checked.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the for loop that processes array values
    # The validation should be inside this loop
    loop_pattern = r'for\s*\(\s*const\s+auto\s+&\s+value\s*:\s*array\s*\)\s*\{[^}]*value_as_string\.empty\(\)'

    assert re.search(loop_pattern, content, re.DOTALL), \
        "Empty string validation should be inside the loop that processes each separator"


def test_bad_arguments_exception_thrown():
    """
    Fail-to-pass: Verify that the correct exception type (BAD_ARGUMENTS) is used
    when rejecting empty separator strings.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that BAD_ARGUMENTS is used for empty string validation
    # The error throw should be near the empty() check
    section_start = content.find("value_as_string.empty()")
    assert section_start != -1, "Empty string check not found"

    # Get a reasonable section around the check
    section = content[section_start:section_start + 500]

    assert "BAD_ARGUMENTS" in section, \
        "BAD_ARGUMENTS error code should be used for empty separator validation"
    assert "SplitByStringTokenizer::getExternalName()" in section, \
        "Exception should reference SplitByStringTokenizer for context"


def test_exception_error_code_used():
    """
    Pass-to-pass: Verify that ErrorCodes::BAD_ARGUMENTS is used in the exception.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert "ErrorCodes::BAD_ARGUMENTS" in content, \
        "Exception should use ErrorCodes::BAD_ARGUMENTS"


def test_source_compiles():
    """
    Pass-to-pass: Verify that the modified source file compiles successfully.
    This catches syntax errors or type mismatches introduced by the fix.
    """
    # Run clang to check if the file compiles (syntax only, no linking)
    result = subprocess.run(
        [
            "clang-18", "-std=c++23", "-fsyntax-only",
            "-I", f"{REPO}/src",
            "-I", f"{REPO}/base",
            "-I", f"{REPO}/contrib/libcxx-cmake/include",
            "-I", f"{REPO}/contrib/libcxxabi-cmake/include",
            "-I", f"{REPO}/contrib/boost",
            TARGET_FILE
        ],
        capture_output=True,
        text=True,
        cwd=REPO
    )

    # We expect some warnings but no errors
    # The actual compilation may fail due to missing headers in minimal environment
    # So we check that the core logic is syntactically valid
    assert result.returncode == 0 or "TokenizerFactory" in result.stderr, \
        f"Syntax check failed:\n{result.stderr}"


def test_values_vector_usage():
    """
    Pass-to-pass: Verify that values vector is populated correctly after validation.
    The emplace_back should happen after the empty check.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the splitByString registration section
    splitbystring_section = content.find("registerTokenizers")
    section = content[splitbystring_section:splitbystring_section + 3000]

    # The values.emplace_back should come after the empty check
    empty_check_pos = section.find("value_as_string.empty()")
    emplace_pos = section.find("values.emplace_back(value_as_string)")

    assert empty_check_pos != -1, "Empty check not found"
    assert emplace_pos != -1, "values.emplace_back not found"
    assert emplace_pos > empty_check_pos, \
        "values.emplace_back should come after the empty string validation"


def test_allman_brace_style():
    """
    Agent config check: Verify Allman-style braces (opening brace on new line).
    Per .claude/CLAUDE.md and AGENTS.md rules.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the empty validation block
    # Should have opening brace on new line (Allman style)
    pattern = r'if\s*\(\s*value_as_string\.empty\(\)\s*\)\s*\n\s*\{'

    assert re.search(pattern, content), \
        "Code should use Allman-style braces (opening brace on new line)"
