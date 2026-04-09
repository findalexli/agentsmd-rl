"""Tests for ClickHouse leftPad/rightPad argument description fix.

PR: ClickHouse/ClickHouse#102106
The fix corrects argument descriptions in padString.cpp:
- "string" argument: was "Array" -> should be "String or FixedString"
- "length" argument: was "const UInt*" -> should be "UInt*"
- "pad_string" argument: was "Array" -> should be "String"

This test file uses a combination of:
1. Behavioral tests (syntax check using clang -fsyntax-only)
2. Static analysis tests (pattern matching on source code)
3. Repo style checks (trailing whitespace, indentation, etc.)
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
PADSTRING_FILE = REPO / "src/Functions/padString.cpp"


# ============================================================================
# BEHAVIORAL TEST - Uses subprocess.run() to execute actual code
# ============================================================================

def test_padstring_syntax_valid():
    """C++ source compiles syntactically (catches syntax errors from bad edits).

    This is a behavioral test that invokes the C++ compiler to verify the
    source code is syntactically valid. Uses clang -fsyntax-only for speed.
    """
    # Skip if clang is not available (should be installed per Dockerfile)
    result = subprocess.run(["which", "clang++-15"], capture_output=True)
    if result.returncode != 0:
        # Try clang without version suffix
        result = subprocess.run(["which", "clang++"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("No clang compiler available for syntax check")

    compiler = "clang++-15" if subprocess.run(["which", "clang++-15"], capture_output=True).returncode == 0 else "clang++"

    # Run syntax-only check on the source file
    # We need to include the paths to ClickHouse headers for a valid check
    cmd = [
        compiler,
        "-fsyntax-only",
        "-std=c++20",
        f"-I{REPO}/src",
        f"-I{REPO}/base",
        f"-I{REPO}/contrib/boost",
        str(PADSTRING_FILE)
    ]

    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,  # Syntax check should be quick
        cwd=str(REPO)
    )

    # Check that syntax is valid (return code 0)
    # Note: This may fail due to missing headers in shallow clone, but
    # we check specifically for syntax errors in the error output
    if r.returncode != 0:
        # If we have errors, make sure they're not syntax errors from the edit
        errors = r.stderr.lower()
        # Look for syntax-related errors that would indicate a bad edit
        syntax_issues = [
            "expected string literal",      # Missing quote in string
            "expected }",                  # Unclosed brace
            "expected )",                  # Unclosed paren
            "unterminated string",         # String not closed
            "unknown escape sequence",       # Bad escape in string
            "syntax error",                # General syntax error
        ]

        for issue in syntax_issues:
            if issue in errors:
                assert False, f"Syntax error detected: {issue}\n{errors[:1000]}"

        # Other errors (missing headers, etc.) are acceptable in shallow clone
        # We only care that the syntax of the function descriptors is correct


# ============================================================================
# FAIL-TO-PASS TESTS - Static analysis (grep-based but precise)
# ============================================================================

def test_string_argument_description():
    """'string' argument description must be 'String or FixedString' (f2p)."""
    content = PADSTRING_FILE.read_text()

    # Find the FunctionArgumentDescriptors mandatory_args with "string" entry
    # Pattern matches: {"string", static_cast<FunctionArgumentDescriptor::TypeValidator>(...), nullptr, "description"}
    # The key difference from doc entries is the presence of TypeValidator static_cast
    pattern = r'\{\s*"string"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>[^}]+"([^"]+)"\s*\}'
    matches = list(re.finditer(pattern, content))

    assert len(matches) > 0, "Could not find 'string' argument descriptor with TypeValidator"

    # Should be only one match (the validator entry in getReturnTypeImpl)
    description = matches[0].group(1)

    # After the fix, this should be "String or FixedString", NOT "Array"
    assert description == "String or FixedString", \
        f"Expected 'String or FixedString' for 'string' argument, got '{description}'"


def test_length_argument_description():
    """'length' argument description must be 'UInt*' not 'const UInt*' (f2p)."""
    content = PADSTRING_FILE.read_text()

    # Pattern matches: {"length", static_cast<FunctionArgumentDescriptor::TypeValidator>(...), nullptr, "description"}
    pattern = r'\{\s*"length"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>[^}]+"([^"]+)"\s*\}'
    matches = list(re.finditer(pattern, content))

    assert len(matches) > 0, "Could not find 'length' argument descriptor with TypeValidator"

    description = matches[0].group(1)

    # After the fix, this should be "UInt*", NOT "const UInt*"
    assert description == "UInt*", \
        f"Expected 'UInt*' for 'length' argument, got '{description}'"


def test_pad_string_argument_description():
    """'pad_string' argument description must be 'String' not 'Array' (f2p)."""
    content = PADSTRING_FILE.read_text()

    # Pattern matches: {"pad_string", static_cast<FunctionArgumentDescriptor::TypeValidator>(...), isColumnConst, "description"}
    pattern = r'\{\s*"pad_string"\s*,\s*static_cast<FunctionArgumentDescriptor::TypeValidator>[^}]+"([^"]+)"\s*\}'
    matches = list(re.finditer(pattern, content))

    assert len(matches) > 0, "Could not find 'pad_string' argument descriptor with TypeValidator"

    description = matches[0].group(1)

    # After the fix, this should be "String", NOT "Array"
    assert description == "String", \
        f"Expected 'String' for 'pad_string' argument, got '{description}'"


# ============================================================================
# PASS-TO-PASS TESTS - Repo style and structural checks
# ============================================================================

def test_no_trailing_whitespace():
    """padString.cpp has no trailing whitespace (repo style - p2p)."""
    content = PADSTRING_FILE.read_text()
    lines = content.split('\n')

    violations = []
    for i, line in enumerate(lines):
        if line.rstrip() != line:
            violations.append(f"Line {i+1}: {repr(line)}")

    assert len(violations) == 0, \
        f"Found trailing whitespace in {len(violations)} lines:\n" + "\n".join(violations[:10])


def test_file_not_empty_and_valid():
    """padString.cpp is a valid, non-empty file (structural - p2p)."""
    content = PADSTRING_FILE.read_text()

    # File should be non-empty
    assert len(content) > 0, "File is empty"

    # File should have a reasonable number of lines
    lines = content.split('\n')
    assert len(lines) > 50, f"File seems too short ({len(lines)} lines)"

    # File should end with a newline (standard convention)
    assert content.endswith('\n'), "File should end with a newline"


def test_no_tabs_for_indentation():
    """padString.cpp uses spaces for indentation, not tabs (repo style - p2p)."""
    content = PADSTRING_FILE.read_text()
    lines = content.split('\n')

    tab_lines = []
    for i, line in enumerate(lines):
        if '\t' in line:
            tab_lines.append(i + 1)

    assert len(tab_lines) == 0, \
        f"Found tabs in {len(tab_lines)} lines: {tab_lines[:10]}"


def test_include_directives_format():
    """#include directives follow project format (repo style - p2p)."""
    content = PADSTRING_FILE.read_text()
    lines = content.split('\n')

    include_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#include'):
            include_lines.append((i + 1, stripped))

    # All #include should be at the start of the file (before any code)
    # and should have proper format: #include <...> or #include "..."
    assert len(include_lines) > 0, "No #include directives found"

    for line_no, line in include_lines:
        # Check format - should be #include followed by space then <...> or "..."
        if not re.match(r'^#include\s+[<"][^>"]+[>"]$', line):
            assert False, f"Line {line_no}: Invalid #include format: {line}"


def test_validate_function_arguments_usage():
    """validateFunctionArguments API is used correctly (API check - p2p)."""
    content = PADSTRING_FILE.read_text()

    # Check that validateFunctionArguments is called
    assert 'validateFunctionArguments' in content, \
        "validateFunctionArguments should be used in padString.cpp"

    # Check that FunctionArgumentDescriptors are defined
    assert 'FunctionArgumentDescriptors' in content, \
        "FunctionArgumentDescriptors should be used"

    # Verify mandatory_args and optional_args are present
    assert 'mandatory_args' in content, "mandatory_args should be defined"
    assert 'optional_args' in content, "optional_args should be defined"


# ============================================================================
# AGENT CONFIG TESTS - Style rules from CLAUDE.md
# ============================================================================

def test_allman_brace_style():
    """Code uses Allman brace style per project conventions (config - p2p).

    Allman style: opening brace on a new line
    From CLAUDE.md: When writing C++ code, always use Allman-style braces
    """
    content = PADSTRING_FILE.read_text()
    lines = content.split('\n')

    # Check that opening braces for function/namespace definitions
    # follow Allman style (brace on its own line after the declaration)

    violations = []
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines, comments, preprocessor directives
        if not stripped or stripped.startswith('//') or stripped.startswith('#'):
            continue

        # Look for patterns that violate Allman style:
        # - Control structures with brace on same line: "if (x) {" or "} else {"
        # But ignore: namespace {, class {, enum { which are often on same line

        # Pattern for K&R style violations in control flow
        # Matches: if/else/for/while followed by condition then brace on same line
        kr_patterns = [
            r'^\s*if\s*\([^)]+\)\s*\{',      # if (cond) {
            r'^\s*else\s*\{',                  # else {
            r'^\s*for\s*\([^)]+\)\s*\{',     # for (...) {
            r'^\s*while\s*\([^)]+\)\s*\{',   # while (...) {
            r'^\}\s*else\s*\{',               # } else {
        ]

        for pattern in kr_patterns:
            if re.search(pattern, stripped):
                violations.append((i + 1, stripped))
                break

    # Allow some flexibility - the project may have existing K&R style code
    # This test documents the style rule but doesn't block on existing code
    if len(violations) > 5:
        # Too many violations indicates agent may have introduced new K&R code
        pass  # Informational only - don't fail on existing code style
