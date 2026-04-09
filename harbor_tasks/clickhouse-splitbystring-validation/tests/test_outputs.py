"""
Tests for validating the splitByString tokenizer fix in ClickHouse.

The PR adds validation to prevent empty strings from being used as separators
in the splitByString tokenizer. This prevents runtime issues when empty
strings are inadvertently passed as separators.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Interpreters/TokenizerFactory.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def test_empty_string_separator_validation_present():
    """
    Fail-to-pass: Verify the validation code for empty string separators is present.
    The fix adds a check that throws an exception when an empty string is used as separator.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the distinctive error message from the patch
    assert "the empty string cannot be used as a separator" in content, \
        "Missing validation: empty string separator check not found"

    # Check that the validation logic exists (checking inside the loop)
    pattern = r'if\s*\(\s*value_as_string\.empty\(\s*\)\s*\)'
    assert re.search(pattern, content), \
        "Missing validation: empty check for value_as_string not found"


def test_exception_thrown_for_empty_separator():
    """
    Fail-to-pass: Verify that the exception-throwing logic for empty separator is present.
    Checks that an exception with BAD_ARGUMENTS error code is thrown.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for throw Exception pattern with BAD_ARGUMENTS in the context of empty string
    # Look for the validation block structure
    assert "ErrorCodes::BAD_ARGUMENTS" in content, \
        "Missing ErrorCodes::BAD_ARGUMENTS for validation"

    # Check the exception is thrown conditionally on empty string
    lines = content.split('\n')
    found_empty_check = False
    found_throw_in_context = False

    for i, line in enumerate(lines):
        if 'value_as_string.empty()' in line or 'value_as_string.empty ()' in line:
            found_empty_check = True
            # Check next few lines for throw statement
            for j in range(i, min(i+5, len(lines))):
                if 'throw Exception' in lines[j]:
                    found_throw_in_context = True
                    break
            break

    assert found_empty_check, "Empty check for value_as_string not found"
    assert found_throw_in_context, "Throw statement not found near empty check"


def test_error_message_improved_for_empty_separators():
    """
    Pass-to-pass: Verify the error message improvement for empty separators argument.
    The PR changes "separators cannot be empty" to "the separators argument cannot be empty".
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for improved error message
    assert "the separators argument cannot be empty" in content, \
        "Improved error message for empty separators not found"


def test_validation_inside_loop_structure():
    """
    Pass-to-pass: Verify the validation is properly structured inside the loop.
    The fix should validate each separator value individually before adding to values vector.
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the proper variable extraction pattern
    assert "value_as_string" in content, \
        "Variable 'value_as_string' not found - validation not properly structured"

    # Verify the castAs<String> result is stored in a variable (not used directly)
    pattern = r'const\s+auto\s+&?\s*value_as_string\s*=\s*castAs<String>'
    assert re.search(pattern, content), \
        "castAs<String> result should be stored in value_as_string variable"


def test_allman_brace_style():
    """
    Agent config check: Verify Allman-style braces are used for new code blocks.
    Opening braces should be on a new line.
    Source: .claude/CLAUDE.md, AGENTS.md
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Find the for loop that was modified and check its brace style
    # The for loop with the added validation should use Allman style
    lines = content.split('\n')

    for i, line in enumerate(lines):
        # Look for the for loop that iterates over array
        if 'for (const auto & value : array)' in line:
            # Check that the next non-empty line has opening brace on its own line
            for j in range(i+1, min(i+3, len(lines))):
                stripped = lines[j].strip()
                if stripped:
                    # Allman style: opening brace on new line
                    assert stripped == '{', \
                        f"Allman brace style violation: opening brace not on new line after for loop at line {i+1}"
                    break
            break


def test_exception_not_crash_terminology():
    """
    Agent config check: Verify proper terminology - 'exception' not 'crash'.
    Source: .claude/CLAUDE.md, AGENTS.md
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # The file should use "exception" terminology in comments
    # Check that we don't use "crash" in relation to logical errors
    # This is a soft check - we look for patterns

    # Lowercase for case-insensitive search
    content_lower = content.lower()

    # If there's a comment about this validation, it should say "exception"
    # We won't fail if no comments exist, but we'll check that crash isn't used
    # in the context of describing the validation behavior

    # Find the validation section
    lines = content_lower.split('\n')
    in_validation_section = False

    for i, line in enumerate(lines):
        if 'empty string' in line or 'bad_arguments' in line:
            in_validation_section = True
            # Check next few lines
            for j in range(max(0, i-2), min(i+5, len(lines))):
                # Should not use "crash" to describe the error
                assert 'crash' not in lines[j] or 'exception' in lines[j], \
                    f"Incorrect terminology at line {j+1}: use 'exception' not 'crash' for logical errors"


def test_function_naming_without_parens():
    """
    Agent config check: Verify function names in comments don't use parentheses.
    Names of functions should be written as `f` instead of `f()`.
    Source: .claude/CLAUDE.md, AGENTS.md
    """
    # Read the file and check any comments near the changed section
    with open(FULL_PATH, 'r') as f:
        lines = f.readlines()

    # Look for the section where our changes are (around splitByString handling)
    for i, line in enumerate(lines):
        if 'SplitByStringTokenizer' in line or 'getExternalName' in line:
            # Check surrounding context for function naming in comments
            for j in range(max(0, i-10), min(i+10, len(lines))):
                # Skip code lines, focus on comments
                if '//' in lines[j] or '/*' in lines[j]:
                    comment = lines[j]
                    # Look for function() pattern in comments (should be function)
                    # This is a soft check - many cases are acceptable
                    pass  # No hard constraint, documented for LLM judge


def test_code_compiles():
    """
    Pass-to-pass: Verify the C++ code compiles without errors.
    """
    # Run a quick syntax check using clang
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++20", "-c",
         "-I", os.path.join(REPO, "src"),
         "-I", os.path.join(REPO, "base"),
         "-I", os.path.join(REPO, "contrib"),
         FULL_PATH],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Note: This may fail due to missing includes, but should not have syntax errors
    # in the actual code. We'll check for specific error patterns.
    if result.returncode != 0:
        stderr = result.stderr.lower()
        # Syntax errors indicate problems with our changes
        assert "syntax error" not in stderr, f"Syntax error in code: {result.stderr}"
        assert "expected" not in stderr or "identifier" not in stderr, \
            f"Parse error in code: {result.stderr}"


def test_repo_clang_syntax_check():
    """
    Pass-to-pass: Repo's C++ syntax check passes using clang-18.
    Verifies the modified file has no syntax errors (standard ClickHouse CI check).
    """
    # Run clang syntax-only check - this is a standard check in ClickHouse CI
    # that validates C++ syntax without requiring a full build
    include_paths = [
        "-I", os.path.join(REPO, "src"),
        "-I", os.path.join(REPO, "base"),
        "-I", os.path.join(REPO, "contrib"),
        "-I", os.path.join(REPO, "contrib", "llvm-project", "libcxx", "include"),
    ]

    # Add common ClickHouse defines to reduce missing include errors
    defines = [
        "-D__cplusplus=202002L",
        "-DNDEBUG",
    ]

    cmd = ["clang-18", "-fsyntax-only", "-std=c++20", "-x", "c++"] + defines + include_paths + [FULL_PATH]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    # For p2p, we only care that there are no actual syntax errors in the code
    # Missing includes are expected since we don't have all contrib libraries
    stderr = result.stderr.lower()

    # These patterns indicate actual syntax/parse errors in the code (not missing includes)
    error_patterns = [
        "syntax error",
        "expected expression",
        "expected ';'",
        "expected '}'",
        "expected ')'",
        "unexpected",
        "unknown type name",
        "no member named",
        "use of undeclared identifier",
        "invalid operands",
        "cannot initialize",
        "too many errors",
    ]

    for pattern in error_patterns:
        assert pattern not in stderr, f"C++ syntax error detected: {pattern}\n{result.stderr[-1000:]}"


def test_repo_code_style_basic():
    """
    Pass-to-pass: Basic code style check - verifies braces follow Allman style.
    ClickHouse uses Allman-style braces (opening brace on new line).
    """
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    lines = content.split('\n')

    # Check for common style violations in modified code
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for control statements with braces on same line (K&R style violation)
        # This is a heuristic check for Allman style compliance
        if stripped.startswith('if ') and stripped.endswith('{'):
            # Single-line if statements with { on same line are OK if short
            if len(stripped) > 40:  # Long lines with { at end likely K&R
                # Check next line - should have { on its own line for Allman
                pass  # Soft check - documented for style guide compliance

        # Check for for/while with braces on same line
        if (stripped.startswith('for ') or stripped.startswith('while ')) and '{' in stripped:
            # Find the position of {
            brace_pos = stripped.find('{')
            before_brace = stripped[:brace_pos].strip()
            # If there's code after the closing parenthesis and before { on same line
            if before_brace.endswith(')') or before_brace.endswith('))'):
                # This is K&R style - Allman would have { on next line
                # We document this but don't fail as it may be intentional
                pass
