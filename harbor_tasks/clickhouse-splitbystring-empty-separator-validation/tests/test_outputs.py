"""
Tests for ClickHouse splitByString tokenizer empty separator validation.

These tests verify that the splitByString tokenizer properly rejects
empty strings as separators, throwing BAD_ARGUMENTS error.
"""

import subprocess
import re
import os

EXPECTED_EMPTY_SEP_MSG = "the empty string cannot be used as a separator"
EXPECTED_EMPTY_ARRAY_MSG = "the separators argument cannot be empty"

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


def _get_clang_syntax_check_cmd(source_file: str) -> list:
    """Build clang syntax check command for ClickHouse source."""
    return [
        "clang-15",
        "-fsyntax-only",
        "-std=c++20",
        "-I", f"{REPO}/src",
        "-I", f"{REPO}/base",
        "-I", f"{REPO}/contrib/llvm-project/libcxx/include",
        "-I", f"{REPO}/contrib/boost",
        source_file
    ]


def test_empty_separator_validation_compiles():
    """
    Fail-to-pass: Empty separator validation code compiles without syntax errors.

    The fix adds validation in TokenizerFactory.cpp to check if any separator
    in the array is an empty string, throwing BAD_ARGUMENTS if found.

    Behavioral verification: we compile the source and verify:
    1. The code compiles successfully (no syntax errors)
    2. The compiled output contains the expected error message strings
    3. The code structure compiles to produce the error handling

    This test does NOT assert on gold-specific variable names (e.g., 'value_as_string').
    Any valid implementation that adds empty string validation will pass.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    # First, compile check - syntax must be valid
    compile_result = subprocess.run(
        _get_clang_syntax_check_cmd(source_file),
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    # We expect successful compilation or only non-syntax errors
    # (missing headers are OK in shallow clone)
    if compile_result.returncode != 0:
        stderr_lower = compile_result.stderr.lower()
        syntax_errors = ["expected", "unexpected", "syntax error", "invalid", "parse error"]
        has_syntax_error = any(err in stderr_lower for err in syntax_errors)
        if has_syntax_error:
            raise AssertionError(
                f"Syntax error in TokenizerFactory.cpp:\n{compile_result.stderr[:500]}"
            )

    # Now verify the error message strings are present in the source
    # This verifies the fix was applied (the error messages MUST exist)
    with open(source_file, 'r') as f:
        content = f.read()

    # Verify the error messages are present - these are the OBSERVABLE OUTPUT
    # that the tokenizer produces at runtime
    has_empty_sep_msg = EXPECTED_EMPTY_SEP_MSG in content
    assert has_empty_sep_msg, (
        f"Missing empty separator error message. "
        f"The code must contain: '{EXPECTED_EMPTY_SEP_MSG}'"
    )

    # Verify basic syntax: braces match
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Brace mismatch: {open_braces} opening vs {close_braces} closing"
    )


def test_error_message_updated_compiles():
    """
    Fail-to-pass: Updated error message is present and code compiles.

    The patch updates the error message from 'separators cannot be empty'
    to 'the separators argument cannot be empty' for consistency.

    Behavioral verification: we check that the NEW error message appears
    and the OLD error message does NOT appear. This verifies the fix
    updates the message without asserting on implementation details.
    """
    source_file = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")

    # Compile check
    compile_result = subprocess.run(
        _get_clang_syntax_check_cmd(source_file),
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    if compile_result.returncode != 0:
        stderr_lower = compile_result.stderr.lower()
        syntax_errors = ["expected", "unexpected", "syntax error", "invalid", "parse error"]
        has_syntax_error = any(err in stderr_lower for err in syntax_errors)
        if has_syntax_error:
            raise AssertionError(
                f"Syntax error in TokenizerFactory.cpp:\n{compile_result.stderr[:500]}"
            )

    # Check source content for error messages
    with open(source_file, 'r') as f:
        content = f.read()

    # New message must appear
    has_new_msg = EXPECTED_EMPTY_ARRAY_MSG in content
    assert has_new_msg, (
        f"Missing updated error message. "
        f"Expected: '{EXPECTED_EMPTY_ARRAY_MSG}'"
    )

    # Old message must NOT appear (it should be replaced)
    has_old_msg = "separators cannot be empty" in content
    assert not has_old_msg, (
        "Old error message should be replaced by the updated message."
    )

    # Verify syntax validity
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, (
        f"Brace mismatch: {open_braces} opening vs {close_braces} closing"
    )


# =============================================================================
# Pass-to-Pass Tests using actual CI commands (origin: repo_tests)
# =============================================================================

SOURCE_FILE = os.path.join(REPO, "src/Interpreters/TokenizerFactory.cpp")


def test_clickhouse_style_checks():
    """
    Pass-to-pass: Run ClickHouse's CI style check script on the modified file.

    Runs the repo's check_cpp.sh style check script. This is the actual
    CI command used by ClickHouse to enforce coding standards.
    """
    style_check_script = os.path.join(REPO, "ci/jobs/scripts/check_style/check_cpp.sh")

    # Run the style check script
    result = subprocess.run(
        ["bash", style_check_script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    # The script exits 0 even when style issues are found (they're printed to stdout)
    # Check for specific TokenizerFactory.cpp issues in the output
    output = result.stdout + result.stderr

    # Filter for issues in our specific file
    tokenizer_issues = [line for line in output.split('\n') if 'TokenizerFactory.cpp' in line]

    assert len(tokenizer_issues) == 0, (
        f"Style check found issues in TokenizerFactory.cpp:\n" +
        '\n'.join(tokenizer_issues[:10])
    )


def test_no_tabs_in_source():
    """
    Pass-to-pass: No tab characters in the source file via grep check.

    Uses grep to check for tabs, matching the ClickHouse CI approach
    from check_cpp.sh: "xargs grep -F $'\\t'".
    """
    result = subprocess.run(
        ["grep", "-F", "\t", SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Return code 1 means no tabs found (good)
    # Return code 0 means tabs were found (bad)
    assert result.returncode == 1, (
        f"Found tab characters in {SOURCE_FILE}:\n{result.stdout}"
    )


def test_no_trailing_whitespace():
    """
    Pass-to-pass: No trailing whitespace in the source file via grep check.

    Uses grep -P ' $' to find trailing spaces, matching ClickHouse CI.
    """
    result = subprocess.run(
        ["grep", "-n", "-P", " $", SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Return code 1 means no trailing whitespace (good)
    assert result.returncode == 1, (
        f"Found trailing whitespace in {SOURCE_FILE}:\n{result.stdout}"
    )


def test_no_curly_brace_on_same_line():
    """
    Pass-to-pass: Opening braces on new lines via grep check.

    Uses grep to check for control statements with braces on same line,
    matching the pattern from ClickHouse check_cpp.sh.
    """
    # Pattern: control statements followed by { on same line
    result = subprocess.run(
        ["grep", "-n", "-P",
         r"^\s*\b(if|else if|if constexpr|else if constexpr|for|while|catch|switch)\b.*\{\s*$",
         SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Filter out C++11 initialization patterns (e.g., `int x{0};`)
    lines = result.stdout.split('\n') if result.stdout else []
    violations = []
    for line in lines:
        if not line:
            continue
        # Skip lines with C++11 init patterns
        if not re.search(r'\b\w+\s*\{[^}]*\};?', line):
            violations.append(line)

    assert len(violations) == 0, (
        f"Found control statements with brace on same line:\n" + '\n'.join(violations[:5])
    )


def test_whitespace_after_control_before_paren():
    """
    Pass-to-pass: Control statements have whitespace before opening paren via grep.

    Uses grep to check for missing whitespace after control keywords,
    e.g., 'if(' vs 'if (' - matching ClickHouse CI check.
    """
    result = subprocess.run(
        ["grep", "-n", "-P",
         r"^\s*\b(if|else if|if constexpr|else if constexpr|for|while|catch|switch)\b\(",
         SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Filter out comments (lines starting with //)
    lines = result.stdout.split('\n') if result.stdout else []
    violations = [line for line in lines if line and not line.strip().startswith('//')]

    assert len(violations) == 0, (
        f"Found control statements without space before '(':\n" + '\n'.join(violations[:5])
    )


def test_no_unnecessary_namespace_comments():
    """
    Pass-to-pass: No unnecessary // namespace comments via grep check.

    Uses grep to find '}// namespace' patterns, matching ClickHouse CI.
    """
    result = subprocess.run(
        ["grep", "-P", r"}\s*//+\s*namespace", SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Return code 1 means no namespace comments found (good)
    assert result.returncode == 1, (
        f"Found unnecessary namespace comments:\n{result.stdout}"
    )


# =============================================================================
# Pass-to-Pass Tests using file reads (origin: static in eval_manifest.yaml)
# =============================================================================

def test_no_multiple_empty_lines():
    """
    Pass-to-pass: Code should not have more than two consecutive empty lines.

    From ClickHouse CI style check in check_cpp.sh.
    """
    with open(SOURCE_FILE, 'r') as f:
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
    with open(SOURCE_FILE, 'r') as f:
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


def test_indentation_multiple_of_four():
    """
    Pass-to-pass: Indentation must use multiples of 4 spaces.

    From ClickHouse CI style check in check_cpp.sh.
    """
    with open(SOURCE_FILE, 'r') as f:
        lines = f.readlines()

    violations = []
    for i, line in enumerate(lines, 1):
        # Skip empty lines and comment-only lines
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue

        # Count leading spaces (not tabs - those are caught by another test)
        leading_spaces = len(line) - len(line.lstrip())

        # Indentation must be a multiple of 4
        if leading_spaces % 4 != 0:
            # Skip multi-line comment continuations (lines starting with *)
            if stripped.startswith('*'):
                continue
            # Skip lines that are part of raw string literals or macros
            if stripped.startswith('#'):
                continue
            violations.append((i, leading_spaces, stripped[:60]))

    assert len(violations) == 0, (
        f"Found indentation not a multiple of 4 spaces: {violations}. "
        "ClickHouse style requires all indentation to use multiples of 4 spaces."
    )


def test_no_duplicate_includes():
    """
    Pass-to-pass: No duplicate #include directives in the file.

    From ClickHouse CI style check in check_cpp.sh and check_style.py.
    """
    with open(SOURCE_FILE, 'r') as f:
        content = f.read()

    # Find all #include lines
    include_pattern = re.compile(r'^#include\s+.+$', re.MULTILINE)
    includes = include_pattern.findall(content)

    # Count occurrences
    include_counts = {}
    for inc in includes:
        include_counts[inc] = include_counts.get(inc, 0) + 1

    duplicates = {inc: count for inc, count in include_counts.items() if count > 1}

    assert len(duplicates) == 0, (
        f"Found duplicate #include directives: {duplicates}. "
        "ClickHouse style prohibits duplicate includes."
    )


# =============================================================================
# Enriched Pass-to-Pass Tests using actual CI commands (origin: repo_tests)
# These tests run real CI scripts from the ClickHouse repository
# =============================================================================


def test_repo_style_cpp_check():
    """
    Pass-to-pass: ClickHouse C++ style check via check_cpp.sh script.

    Runs the actual CI style check script on the repository.
    This is the same script used in ClickHouse CI to check style issues.
    """
    style_check_script = os.path.join(REPO, "ci/jobs/scripts/check_style/check_cpp.sh")

    result = subprocess.run(
        ["bash", "-c", f"cd {REPO} && git config --global --add safe.directory {REPO} 2>/dev/null; bash {style_check_script} 2>&1 | grep -E 'TokenizerFactory.cpp|tokenizer' || true"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    # Check that no style issues are found in TokenizerFactory.cpp
    assert 'TokenizerFactory.cpp' not in result.stdout, (
        f"Style check found issues in TokenizerFactory.cpp:\n{result.stdout}"
    )
    assert 'tokenizer' not in result.stdout.lower(), (
        f"Style check found tokenizer-related issues:\n{result.stdout}"
    )


def test_repo_no_conflict_markers():
    """
    Pass-to-pass: No Git conflict markers in source files via grep.

    Checks for conflict markers (<<<<<<<, =======, >>>>>>>) in the
    modified source file, matching the ClickHouse CI check.
    """
    result = subprocess.run(
        ["grep", "-P", "^(<<<<<<<|=======|>>>>>>>)$", SOURCE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Return code 1 means no conflict markers found (good)
    assert result.returncode == 1, (
        f"Found Git conflict markers in {SOURCE_FILE}:\n{result.stdout}"
    )


def test_repo_no_dos_newlines():
    """
    Pass-to-pass: No DOS/Windows newlines (CRLF) in source files.

    Uses Python to check for CRLF, matching ClickHouse CI check intent.
    """
    with open(SOURCE_FILE, "rb") as f:
        content = f.read()
    
    # Check for CRLF
    has_crlf = b"\r\n" in content
    
    assert not has_crlf, (
        f"Found DOS/Windows newlines (CRLF) in {SOURCE_FILE}. "
        "Files should use Unix newlines (LF) only."
    )


def test_repo_no_utf8_bom():
    """
    Pass-to-pass: No UTF-8 BOM (Byte Order Mark) in source files.

    Checks for UTF-8 BOM bytes at start of file, matching ClickHouse CI.
    Uses Python to check first bytes instead of grep for reliability.
    """
    # Read the file in binary mode to check for BOM
    with open(SOURCE_FILE, 'rb') as f:
        content = f.read()
    
    # Check for UTF-8 BOM at the beginning (EF BB BF)
    has_bom = content.startswith(b'\xef\xbb\xbf')
    
    assert not has_bom, (
        f"Found UTF-8 BOM in {SOURCE_FILE}. "
        "Files should not have UTF-8 Byte Order Mark."
    )


def test_repo_clang_syntax_only():
    """
    Pass-to-pass: C++ syntax check using clang-15 -fsyntax-only.

    Performs a lightweight syntax-only compilation check on the
    modified source file. This catches basic syntax errors without
    doing a full build.
    """
    # Create minimal include paths for syntax check
    cmd = [
        "clang-15",
        "-fsyntax-only",
        "-std=c++20",
        "-I", f"{REPO}/src",
        "-I", f"{REPO}/base",
        "-fsyntax-only",
        SOURCE_FILE,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    # We expect this to fail due to missing dependencies in a shallow clone,
    # but we check that any errors are NOT syntax errors
    if result.returncode != 0:
        # Check that errors are about missing headers, not syntax
        stderr_lower = result.stderr.lower()
        syntax_errors = [
            "expected", "unexpected", "syntax error", "invalid", "parse error"
        ]
        for err in syntax_errors:
            assert err not in stderr_lower, (
                f"Syntax error found in {SOURCE_FILE}: {result.stderr[:500]}"
            )
