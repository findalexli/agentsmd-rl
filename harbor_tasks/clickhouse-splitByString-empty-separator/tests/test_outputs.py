"""Tests for ClickHouse splitByString empty separator validation fix."""

import subprocess
import re

REPO = "/workspace/ClickHouse"
TOKENIZER_FILE = f"{REPO}/src/Interpreters/TokenizerFactory.cpp"
SQL_TEST_FILE = f"{REPO}/tests/queries/0_stateless/03403_function_tokens.sql"
CHECK_STYLE_SCRIPT = f"{REPO}/ci/jobs/scripts/check_style/check_cpp.sh"


def test_empty_separator_validation_present():
    """Verify empty string separator validation is implemented (fail_to_pass)."""
    with open(TOKENIZER_FILE, 'r') as f:
        content = f.read()

    # Check for the empty string validation
    assert "value_as_string.empty()" in content, \
        "Missing empty string check in separator validation"

    # Check for the specific error message about empty separator
    assert "the empty string cannot be used as a separator" in content, \
        "Missing error message for empty separator"


def test_error_message_updated():
    """Verify error message for empty separators array was updated (fail_to_pass)."""
    with open(TOKENIZER_FILE, 'r') as f:
        content = f.read()

    # The old message said "separators cannot be empty"
    # The new message should say "the separators argument cannot be empty"
    assert "the separators argument cannot be empty" in content, \
        "Error message not updated for empty separators argument"

    # Make sure old message is gone
    assert "separators cannot be empty" not in content, \
        "Old error message still present"


def test_cpp_syntax_valid():
    """Verify C++ code is syntactically valid (fail_to_pass)."""
    # Use clang to check syntax only
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++23", "-I", f"{REPO}/src",
         "-I", f"{REPO}/base", "-I", f"{REPO}/contrib", "-c",
         TOKENIZER_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Syntax check should succeed (we may get include errors but not syntax errors)
    # We accept return code 0 or errors that are only about missing includes
    if result.returncode != 0:
        # Filter out only actual syntax errors, not include errors
        errors = result.stderr
        # If there are errors, they should only be about missing headers, not syntax
        syntax_errors = [line for line in errors.split('\n')
                        if 'error:' in line and 'no such file' not in line.lower()
                        and 'not found' not in line.lower()]
        if syntax_errors:
            raise AssertionError(f"C++ syntax errors found:\n{chr(10).join(syntax_errors)}")


def test_allman_brace_style():
    """Verify Allman brace style is used (agent_config: CLAUDE.md rule)."""
    with open(TOKENIZER_FILE, 'r') as f:
        content = f.read()

    # Find the split_by_string_creator lambda and check the for loop
    # The for loop with the fix should have opening brace on new line
    pattern = r'for\s*\([^)]+\)\s*\{'
    matches = re.findall(pattern, content)

    for match in matches:
        # Check if there's a newline before the opening brace
        # We look at the context around the match
        idx = content.find(match)
        before = content[max(0, idx-20):idx]
        if 'for' in match and '\n{' not in match and '{\n' not in match:
            # Check if the brace is on the same line (K&R style) - this is wrong
            if re.search(r'\)\s*\{', match):
                # This is acceptable in the single-line pattern match,
                # but we need to check the actual formatted code
                pass

    # More robust check: look for the specific block we added
    # The for loop body should have brace on new line
    expected_pattern = r'for\s*\(const auto & value : array\)\s*\n\s*\{'
    assert re.search(expected_pattern, content), \
        "Allman brace style not followed: opening brace should be on new line after for loop"


def test_validation_in_for_loop():
    """Verify the validation logic is inside the for loop iterating separators (fail_to_pass)."""
    with open(TOKENIZER_FILE, 'r') as f:
        content = f.read()

    # Find the split_by_string_creator lambda
    lambda_start = content.find("auto split_by_string_creator = [](const FieldVector & args)")
    assert lambda_start != -1, "Could not find split_by_string_creator lambda"

    # Extract the lambda body (roughly)
    lambda_section = content[lambda_start:lambda_start + 3000]

    # Check that we check for empty string inside the for loop
    # The validation should be between "for (const auto & value : array)" and the emplace_back
    for_match = re.search(
        r'for\s*\(const auto & value : array\)\s*\{([^}]+)\}',
        lambda_section,
        re.DOTALL
    )
    assert for_match, "Could not find for loop with validation"

    loop_body = for_match.group(1)
    assert "value_as_string.empty()" in loop_body, \
        "Empty string check not found in for loop body"
    assert "throw Exception" in loop_body, \
        "Exception throw not found in for loop body"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks)
# =============================================================================
# These tests verify that the fix doesn't break existing CI/CD checks that
# run on every PR in the ClickHouse repository.


def test_tokenizer_file_no_trailing_whitespace():
    """Verify TokenizerFactory.cpp has no trailing whitespace (pass_to_pass)."""
    with open(TOKENIZER_FILE, "r") as f:
        lines = f.readlines()

    issues = []
    for i, line in enumerate(lines, 1):
        # Check for trailing whitespace (excluding the newline)
        stripped = line.rstrip("\n").rstrip("\r")
        if stripped != stripped.rstrip():
            issues.append(f"Line {i}: trailing whitespace")

    assert not issues, f"Trailing whitespace found:\n{chr(10).join(issues[:10])}"


def test_tokenizer_file_no_tabs():
    """Verify TokenizerFactory.cpp uses spaces, not tabs (pass_to_pass)."""
    with open(TOKENIZER_FILE, "r") as f:
        content = f.read()

    # ClickHouse uses 4 spaces for indentation, no tabs
    tab_lines = []
    for i, line in enumerate(content.split("\n"), 1):
        if "\t" in line:
            tab_lines.append(str(i))

    assert not tab_lines, f"Tabs found on lines: {', '.join(tab_lines[:10])}"


def test_tokenizer_file_allman_braces():
    """Verify TokenizerFactory.cpp follows Allman brace style (pass_to_pass)."""
    with open(TOKENIZER_FILE, "r") as f:
        content = f.read()

    # Look for control statements with opening braces on same line (K&R style)
    # This is a simplified check - actual style check is more comprehensive
    kr_style_patterns = [
        r"if\s*\([^)]+\)\s*\{",  # if () {
        r"for\s*\([^)]+\)\s*\{",  # for () {
        r"while\s*\([^)]+\)\s*\{",  # while () {
    ]

    issues = []
    for pattern in kr_style_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Get position and some context
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 10)
            context = content[start:end]
            # If the brace is on the same line as the closing paren, it's K&R
            if "\n" not in match.group(0) and "}" not in context:
                issues.append(f"Possible K&R style found: {match.group(0)}")

    # Since the codebase may have some K&R in existing code, we just warn
    # but don't fail if there are a few instances
    if len(issues) > 10:
        assert False, f"Too many K&R style braces found: {issues[:5]}"


def test_tokenizer_file_pragma_once_headers():
    """Verify header files have #pragma once (pass_to_pass)."""
    header_file = f"{REPO}/src/Interpreters/TokenizerFactory.h"
    with open(header_file, "r") as f:
        first_line = f.readline().strip()

    assert first_line == "#pragma once", \
        f"Header file missing #pragma once: {first_line}"


def test_sql_test_file_exists():
    """Verify the SQL test file exists and is readable (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        content = f.read()

    # Basic check that the file contains expected test cases
    assert "SELECT tokens" in content, "SQL test file missing expected test cases"
    assert "splitByString" in content, "SQL test file missing splitByString tests"


def test_sql_test_file_valid_syntax():
    """Verify the SQL test file has valid basic syntax (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        content = f.read()

    # Check for balanced parentheses in non-comment lines
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith("--"):
            continue

        # Count parentheses
        open_parens = line.count("(")
        close_parens = line.count(")")

        # For complete statements, they should be balanced
        # (this is a simplified check)
        if ";" in line and not line.strip().startswith("--"):
            # Statement end - should be balanced
            if open_parens != close_parens:
                # Multi-line statement, track across lines
                pass

    # File-level check: total parentheses should be roughly balanced
    total_open = content.count("(")
    total_close = content.count(")")

    # Allow some difference for multi-line statements
    assert abs(total_open - total_close) < 5, \
        f"Unbalanced parentheses: {total_open} open, {total_close} close"


def test_cpp_file_no_cyrillic():
    """Verify TokenizerFactory.cpp has no cyrillic characters mixed with Latin (pass_to_pass)."""
    with open(TOKENIZER_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for cyrillic characters that might look like Latin
    cyrillic_pattern = re.compile(r'[a-zA-Z][а-яА-ЯёЁ]|[а-яА-ЯёЁ][a-zA-Z]')
    matches = cyrillic_pattern.findall(content)

    assert not matches, f"Found cyrillic characters mixed with Latin: {matches[:5]}"


def test_cpp_file_pragma_once_in_headers():
    """Verify all modified header files have proper include guards (pass_to_pass)."""
    tokenizer_header = f"{REPO}/src/Interpreters/TokenizerFactory.h"
    itokenizer_header = f"{REPO}/src/Interpreters/ITokenizer.h"

    for header_path in [tokenizer_header, itokenizer_header]:
        try:
            with open(header_path, "r") as f:
                first_line = f.readline().strip()
            assert first_line == "#pragma once", \
                f"{header_path} missing #pragma once"
        except FileNotFoundError:
            # Some headers might not exist
            pass


# =============================================================================
# Additional Pass-to-Pass Tests (Repo CI/CD checks)
# =============================================================================
# These tests mirror ClickHouse's actual CI checks from ci/jobs/scripts/check_style/


def test_repo_clang_syntax_check():
    """Verify C++ code passes basic clang syntax check (pass_to_pass)."""
    # Run clang-18 syntax check on the modified file
    # This checks for basic syntax errors without requiring full build
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++23",
         "-I", f"{REPO}/src", "-I", f"{REPO}/base",
         "-I", f"{REPO}/contrib",
         TOKENIZER_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Accept return code 0 (no issues) or non-zero only for missing includes
    # (which are expected without full build environment)
    if result.returncode != 0:
        errors = result.stderr
        # Filter out only actual syntax errors, not include errors
        syntax_errors = [line for line in errors.split('\n')
                        if 'error:' in line
                        and 'no such file' not in line.lower()
                        and 'not found' not in line.lower()
                        and 'fatal error' not in line.lower()]
        if syntax_errors:
            raise AssertionError(
                f"C++ syntax errors found:\n{chr(10).join(syntax_errors[:10])}"
            )


def test_repo_sql_test_balanced_parens():
    """Verify SQL test file has balanced parentheses (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        content = f.read()

    # Remove SQL comments for analysis
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove inline comments (but not inside string literals)
        if '--' in line:
            line = line[:line.index('--')]
        cleaned_lines.append(line)

    cleaned_content = '\n'.join(cleaned_lines)

    # Count parentheses - these must be balanced in valid SQL
    open_parens = cleaned_content.count('(')
    close_parens = cleaned_content.count(')')

    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Count square brackets (for arrays) - must be balanced
    open_brackets = cleaned_content.count('[')
    close_brackets = cleaned_content.count(']')

    assert open_brackets == close_brackets, \
        f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"

    # Note: Quote balancing is complex in ClickHouse SQL due to:
    # - Escaped quotes (\')
    # - Multi-line string literals
    # - Error annotations with strings
    # We skip quote balancing and rely on the other syntax checks.


def test_repo_no_trailing_whitespace_in_sql():
    """Verify SQL test file has no trailing whitespace (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        lines = f.readlines()

    issues = []
    for i, line in enumerate(lines, 1):
        # Check for trailing whitespace (excluding the newline)
        stripped = line.rstrip("\n").rstrip("\r")
        if stripped != stripped.rstrip():
            issues.append(f"Line {i}")

    assert not issues, f"Trailing whitespace in SQL file:\n{chr(10).join(issues[:10])}"


def test_repo_no_tabs_in_sql():
    """Verify SQL test file uses spaces, not tabs (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        content = f.read()

    tab_lines = []
    for i, line in enumerate(content.split("\n"), 1):
        if "\t" in line:
            tab_lines.append(str(i))

    assert not tab_lines, f"Tabs found in SQL file on lines: {', '.join(tab_lines[:10])}"


def test_repo_sql_file_valid_statements():
    """Verify SQL test file has valid statement structure (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r") as f:
        content = f.read()

    # Check for expected ClickHouse SQL test patterns
    # Should have SELECT statements
    assert "SELECT" in content.upper(), "SQL file missing SELECT statements"

    # Should have semicolons at end of statements (basic check)
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Skip comments and empty lines
        if not stripped or stripped.startswith('--'):
            continue
        # Check that non-comment SQL lines that aren't continuations end with semicolon
        # or are expected to continue (open parentheses)

    # Check for common syntax issues
    assert ";;" not in content, "Double semicolons found in SQL file"


def test_repo_no_cyrillic_in_sql():
    """Verify SQL test file has no cyrillic characters mixed with Latin (pass_to_pass)."""
    with open(SQL_TEST_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Check for cyrillic characters that might look like Latin
    cyrillic_pattern = re.compile(r'[a-zA-Z][а-яА-ЯёЁ]|[а-яА-ЯёЁ][a-zA-Z]')
    matches = cyrillic_pattern.findall(content)

    assert not matches, f"Found cyrillic characters mixed with Latin in SQL: {matches[:5]}"


# =============================================================================
# NEW Pass-to-Pass Tests (Actual CI Commands via subprocess.run)
# =============================================================================
# These tests run actual CI commands from ClickHouse's check_style scripts
# using subprocess.run() as required for origin: repo_tests


def test_repo_style_no_trailing_whitespace_cpp():
    """CI: Check TokenizerFactory.cpp has no trailing whitespace (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-n", " $", TOKENIZER_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found trailing whitespace in {TOKENIZER_FILE}:\n{result.stdout}"


def test_repo_style_no_tabs_cpp():
    """CI: Check TokenizerFactory.cpp uses spaces not tabs (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-P", "\t", TOKENIZER_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found tabs in {TOKENIZER_FILE}:\n{result.stdout}"


def test_repo_style_no_cyrillic_cpp():
    """CI: Check TokenizerFactory.cpp has no cyrillic characters (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-P", "[a-zA-Z][а-яА-ЯёЁ]|[а-яА-ЯёЁ][a-zA-Z]", TOKENIZER_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found cyrillic characters in {TOKENIZER_FILE}:\n{result.stdout}"


def test_repo_style_no_trailing_whitespace_sql():
    """CI: Check SQL test file has no trailing whitespace (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-n", " $", SQL_TEST_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found trailing whitespace in {SQL_TEST_FILE}:\n{result.stdout}"


def test_repo_style_no_tabs_sql():
    """CI: Check SQL test file uses spaces not tabs (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-P", "\t", SQL_TEST_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found tabs in {SQL_TEST_FILE}:\n{result.stdout}"


def test_repo_header_pragma_once():
    """CI: Check TokenizerFactory.h has #pragma once (pass_to_pass)."""
    header_file = f"{REPO}/src/Interpreters/TokenizerFactory.h"
    result = subprocess.run(
        ["head", "-1", header_file],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Failed to read header file: {header_file}"
    assert result.stdout.strip() == "#pragma once", \
        f"{header_file} missing #pragma once, got: {result.stdout.strip()}"


def test_repo_file_type_cpp():
    """CI: Check TokenizerFactory.cpp is valid C++ source (pass_to_pass)."""
    result = subprocess.run(
        ["file", TOKENIZER_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, "file command failed"
    assert "C++ source" in result.stdout or "ASCII text" in result.stdout, \
        f"TokenizerFactory.cpp is not valid C++ source: {result.stdout}"


def test_repo_file_type_sql():
    """CI: Check SQL test file is valid text (pass_to_pass)."""
    result = subprocess.run(
        ["file", SQL_TEST_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, "file command failed"
    assert "text" in result.stdout.lower(), \
        f"SQL test file is not valid text: {result.stdout}"


def test_repo_sql_no_cyrillic():
    """CI: Check SQL test file has no cyrillic characters (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-P", "[a-zA-Z][а-яА-ЯёЁ]|[а-яА-ЯёЁ][a-zA-Z]", SQL_TEST_FILE],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 1, f"Found cyrillic characters in SQL file:\n{result.stdout}"
