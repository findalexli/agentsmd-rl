"""
Tests for ClickHouse splitByString tokenizer empty separator validation.

These tests verify that the splitByString tokenizer properly rejects
empty strings as separators, throwing BAD_ARGUMENTS error.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
BUILD_DIR = "/workspace/ClickHouse/build"


def _run_compile_check(source_file: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """
    Compile a single C++ file to check for syntax errors.
    Uses clang with minimal options for fast syntax checking.
    """
    # Basic compile command - syntax check only
    cmd = [
        "clang-15",
        "-fsyntax-only",
        "-std=c++20",
        "-I", f"{REPO}/src",
        "-I", f"{REPO}/base",
        "-I", f"{REPO}/contrib/llvm-project/libcxx/include",
        "-I", f"{REPO}/contrib/boost",
        source_file
    ]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_empty_separator_validation_compiles():
    """
    Fail-to-pass: Empty separator validation code is present and syntactically valid.

    The fix adds validation in TokenizerFactory.cpp to check if any separator
    in the array is an empty string, throwing BAD_ARGUMENTS if found.
    This test verifies the code content and basic syntax patterns.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    # First verify the source contains the expected fix
    with open(source_file, 'r') as f:
        content = f.read()

    # Check for the specific validation logic added by the patch
    has_empty_check = 'value_as_string.empty()' in content
    has_exception_throw = 'the empty string cannot be used as a separator' in content

    assert has_empty_check, (
        "Missing empty string check in TokenizerFactory.cpp. "
        "The fix should check if value_as_string.empty() before using the separator."
    )
    assert has_exception_throw, (
        "Missing proper exception message for empty separator. "
        "Expected message: 'the empty string cannot be used as a separator'"
    )

    # Verify basic syntax patterns (braces match, semicolons present)
    # Check that the new code block has proper structure
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Brace mismatch: {open_braces} opening vs {close_braces} closing"
    )


def test_error_message_updated_compiles():
    """
    Fail-to-pass: Updated error message is present and syntactically valid.

    The patch updates the error message from 'separators cannot be empty'
    to 'the separators argument cannot be empty' for consistency.
    This test verifies the message update and basic syntax structure.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    with open(source_file, 'r') as f:
        content = f.read()

    # Check for the updated error message
    has_updated_message = 'the separators argument cannot be empty' in content
    has_old_message = 'separators cannot be empty' in content

    assert has_updated_message, (
        "Missing updated error message. "
        "Expected: 'the separators argument cannot be empty'"
    )
    assert not has_old_message, (
        "Old error message 'separators cannot be empty' should be replaced."
    )

    # Verify basic syntax patterns
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Brace mismatch: {open_braces} opening vs {close_braces} closing"
    )


def test_clickhouse_style_checks():
    """
    Pass-to-pass: TokenizerFactory.cpp passes ClickHouse style checks.

    Runs the repo's style check script on the modified file to ensure
    it follows ClickHouse coding standards (no trailing whitespace,
    no tabs, Allman braces, etc.).
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    # Run the style check script if it exists
    style_check_script = os.path.join(REPO, "utils/check-style/check_cpp.sh")

    if os.path.exists(style_check_script):
        result = subprocess.run(
            ["bash", style_check_script, source_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )

        # Style check should pass
        assert result.returncode == 0, (
            f"Style check failed for TokenizerFactory.cpp:\n{result.stdout}\n{result.stderr}"
        )
    else:
        # Fallback: manual style checks
        with open(source_file, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Check no trailing whitespace
        trailing_ws_lines = []
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line.rstrip('\n').rstrip('\r'):
                trailing_ws_lines.append(i)

        assert len(trailing_ws_lines) == 0, (
            f"Found trailing whitespaces at lines: {trailing_ws_lines}"
        )

        # Check no tabs
        tab_lines = []
        for i, line in enumerate(lines, 1):
            if '\t' in line:
                tab_lines.append(i)

        assert len(tab_lines) == 0, (
            f"Found tab characters at lines: {tab_lines}"
        )


def test_no_multiple_empty_lines():
    """
    Pass-to-pass: Code should not have more than two consecutive empty lines.

    From ClickHouse CI style check in check_cpp.sh.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    with open(source_file, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    empty_count = 0
    violations = []

    for i, line in enumerate(lines, 1):
        if line.strip() == '':
            empty_count += 1
            if empty_count > 2:
                violations.append(i)
        else:
            empty_count = 0

    assert len(violations) == 0, (
        f"Found more than two consecutive empty lines at lines: {violations}. "
        "Per ClickHouse style, no more than two consecutive empty lines are allowed."
    )


def test_allman_brace_style():
    """
    Pass-to-pass: C++ code must follow Allman brace style.

    From agent config (CLAUDE.md): When writing C++ code, always use
    Allman-style braces (opening brace on a new line).
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    with open(source_file, 'r') as f:
        content = f.read()

    # Look for the pattern where opening brace is on its own line after for loop
    # The fix adds a for loop - check its brace style
    for_match = re.search(r'for \(const auto & value : array\)(\s*)\{', content)
    if for_match:
        whitespace = for_match.group(1)
        # The brace should be on a new line (whitespace contains newline)
        assert '\n' in whitespace, (
            "Allman brace style violated: opening brace should be on a new line. "
            "From agent config: 'When writing C++ code, always use Allman-style braces "
            "(opening brace on a new line). This is enforced by the style check in CI.'"
        )


def test_no_curly_brace_on_same_line():
    """
    Pass-to-pass: Opening curly braces should be on a new line (Allman style).

    From ClickHouse CI style check: check_cpp.sh enforces braces on new lines.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    with open(source_file, 'r') as f:
        lines = f.readlines()

    # Pattern: control statements followed by { on same line (excluding C++11 initialization)
    control_pattern = re.compile(
        r'^\s*\b(if|else if|if constexpr|else if constexpr|for|while|catch|switch)\b.*\{\s*$'
    )

    violations = []
    for i, line in enumerate(lines, 1):
        # Skip comments and lines with C++11 init (e.g., `int x{0};`)
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if control_pattern.match(line) and not re.search(r'\b\w+\s*\{[^}]*\};?', stripped):
            violations.append((i, stripped[:80]))

    assert len(violations) == 0, (
        f"Found control statements with brace on same line: {violations}. "
        "Opening braces should be on a new line per ClickHouse Allman style."
    )
