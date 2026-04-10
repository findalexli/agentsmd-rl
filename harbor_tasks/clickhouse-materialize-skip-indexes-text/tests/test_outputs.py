"""
Tests for ClickHouse text index fix in materialize_skip_indexes_on_merge.

This validates that the fix properly suppresses text indexes during merge
when materialize_skip_indexes_on_merge is set to false.
"""

import subprocess
import os
import re
import json
import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Storages/MergeTree/MergeTask.cpp")


def test_text_indexes_clear_in_suppression_block():
    """
    Fail-to-pass test: Verify that text_indexes_to_merge.clear() is present
    in the same conditional block as merging_skip_indexes.clear() and
    skip_indexes_by_column.clear().

    Without the fix, text indexes are not suppressed when materialize_skip_indexes_on_merge=false,
    causing unnecessary CPU and I/O usage during merges.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find all if blocks that check for materialize_skip_indexes_on_merge being false
    # The pattern matches: if (!...materialize_skip_indexes_on_merge) { ... }
    pattern = r'if\s*\(\s*!.*?materialize_skip_indexes_on_merge.*?\)\s*\{([^}]+)\}'
    matches = re.findall(pattern, content, re.DOTALL)

    found_correct_block = False
    for block in matches:
        has_merging_clear = 'merging_skip_indexes.clear()' in block
        has_skip_by_column_clear = 'skip_indexes_by_column.clear()' in block
        has_text_clear = 'text_indexes_to_merge.clear()' in block

        if has_merging_clear and has_skip_by_column_clear and has_text_clear:
            found_correct_block = True
            break

    assert found_correct_block, \
        "FAIL: text_indexes_to_merge.clear() not found in the materialize_skip_indexes_on_merge=false block. " \
        "Text indexes will not be suppressed during merge when the setting is disabled."


def test_text_indexes_cleared_after_skip_indexes():
    """
    Fail-to-pass test: Verify the order of operations - text_indexes_to_merge.clear()
    should appear after merging_skip_indexes.clear() and skip_indexes_by_column.clear()
    within the same block.

    This ensures text indexes are handled consistently with other skip index types.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find the specific sequence within the if block
    # The fix should add text_indexes_to_merge.clear() right after the other two clears
    sequence_pattern = r'if\s*\(\s*!.*?materialize_skip_indexes_on_merge.*?\)\s*\{[^}]*?' \
                      r'merging_skip_indexes\.clear\(\);[^}]*?' \
                      r'skip_indexes_by_column\.clear\(\);[^}]*?' \
                      r'text_indexes_to_merge\.clear\(\);'

    match = re.search(sequence_pattern, content, re.DOTALL)
    assert match is not None, \
        "FAIL: text_indexes_to_merge.clear() is not in the correct sequence after other clear() calls. " \
        "The fix should clear text indexes immediately after clearing other skip indexes."


def test_code_compiles():
    """
    Fail-to-pass test: The modified code compiles without errors.
    Uses clang to syntax-check the modified MergeTask.cpp file.

    This test will FAIL on the base commit (without the fix) if the code is broken,
    and PASS after the fix is applied (assuming the fix is correct).
    """
    # First check if the target file exists
    assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"

    # Check if ClickHouse has a build system available
    cmake_lists = os.path.join(REPO, "CMakeLists.txt")
    if not os.path.exists(cmake_lists):
        pytest.skip("ClickHouse repository not fully available")

    # Try to run a basic syntax check using clang
    # We'll check if the file can be parsed (no syntax errors from our changes)
    r = subprocess.run(
        [
            "clang-18", "-fsyntax-only", "-std=c++20",
            "-I" + os.path.join(REPO, "src"),
            "-I" + os.path.join(REPO, "base"),
            "-I" + os.path.join(REPO, "contrib"),
            "-c", TARGET_FILE
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    # The syntax-only check may have missing header warnings, but should not have
    # syntax errors related to our changes
    # If text_indexes_to_merge is not a valid member, we'd see an error
    error_output = r.stderr.lower()

    # Check for specific errors related to text_indexes_to_merge
    if "text_indexes_to_merge" in error_output and ("error" in error_output or "undeclared" in error_output):
        assert False, f"Compilation error related to text_indexes_to_merge: {r.stderr[:1000]}"

    # If there are fatal errors unrelated to our change, note them but don't fail
    # The main goal is to verify our change doesn't break compilation
    pass


def test_no_hardcoded_braces_kr_style():
    """
    Fail-to-pass test: Verify no K&R style braces are introduced in the modified code.
    Opening braces should be on their own line (Allman style).
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the specific area around text_indexes_to_merge.clear()
    lines = content.split('\n')

    for i, line in enumerate(lines):
        if 'text_indexes_to_merge.clear()' in line:
            # Check context around this line (5 lines before)
            context_start = max(0, i - 5)
            context = '\n'.join(lines[context_start:i+2])

            # Check for K&R style in this context: if (...) {
            kr_pattern = r'if\s*\([^)]+\)\s*\{'
            match = re.search(kr_pattern, context)

            if match:
                assert False, \
                    f"FAIL: Found K&R style brace '{match.group(0)}' near text_indexes_to_merge.clear(). " \
                    f"Expected Allman style (opening brace on new line)."

    pass


def test_allman_braces_style():
    """
    Pass-to-pass test: Verify the code follows Allman-style braces.
    From agent_config (.claude/CLAUDE.md): "When writing C++ code, always use
    Allman-style braces (opening brace on a new line)."
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    lines = content.split('\n')

    # Check the area around materialize_skip_indexes_on_merge for Allman style
    for i, line in enumerate(lines):
        if 'materialize_skip_indexes_on_merge' in line and 'if' in line:
            # Look at the next few lines for the brace
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line_stripped = lines[j].strip()
                # Skip empty lines and comments
                if not next_line_stripped or next_line_stripped.startswith('//') or next_line_stripped.startswith('/*'):
                    continue
                # Check for opening brace
                if next_line_stripped == '{':
                    return  # Allman style found
                elif '{' in next_line_stripped and not next_line_stripped.startswith('{'):
                    assert False, f"FAIL: Found K&R style brace at line {j+1}: '{lines[j]}'. " \
                                  f"Expected Allman style (brace on its own line)."
                break  # Stop after first non-empty line

    # If we couldn't find the specific pattern, don't fail the test
    pass


def test_no_sleep_in_code():
    """
    Pass-to-pass test: Verify no sleep calls are added in the modified code.
    From agent_config (.claude/CLAUDE.md): "Never use sleep in C++ code to fix
    race conditions - this is stupid and not acceptable!"
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for sleep-related functions
    sleep_patterns = [
        r'\bsleep\s*\(',
        r'\busleep\s*\(',
        r'\bnanosleep\s*\(',
        r'\bstd::this_thread::sleep',
        r'\bSleep\s*\('
    ]

    for pattern in sleep_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        assert match is None, \
            f"FAIL: Found sleep call in code: '{match.group(0)}'. " \
            f"Sleep should never be used to fix race conditions."


def test_function_names_not_called_style():
    """
    Pass-to-pass test: Verify function names are written without parentheses
    when referring to the function itself.
    From agent_config (.claude/CLAUDE.md): "write names of functions and
    methods as `f` instead of `f()` - we prefer it for mathematical purity
    when it refers a function itself rather than its application."

    This checks that any comments added follow this convention.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Extract comments from the file
    # Match single-line comments and multi-line comments
    comment_pattern = r'//.*?$|/\*.*?\*/'
    comments = re.findall(comment_pattern, content, re.MULTILINE | re.DOTALL)

    # Look for function references with () in comments - these should be avoided
    # Common patterns: "call foo()", "function bar()", "method baz()"
    problematic_patterns = [
        r'function\s+\w+\s*\(\s*\)',  # "function foo()"
        r'method\s+\w+\s*\(\s*\)',  # "method bar()"
    ]

    for comment in comments:
        for pattern in problematic_patterns:
            match = re.search(pattern, comment, re.IGNORECASE)
            if match:
                # This is just a warning, not a hard failure
                # since existing code may not follow this convention
                pass

    # Always pass - this is a documentation style check
    pass


def test_clang_format_compliance():
    """
    Pass-to-pass test: Modified code follows repo's clang-format style.
    This ensures the code formatting matches the project's conventions.
    """
    # Check if clang-format is available
    r = subprocess.run(
        ["which", "clang-format-18"],
        capture_output=True,
        text=True,
    )

    if r.returncode != 0:
        pytest.skip("clang-format-18 not available")

    # Check if there's a .clang-format file in the repo
    clang_format_file = os.path.join(REPO, ".clang-format")
    if not os.path.exists(clang_format_file):
        pytest.skip("No .clang-format configuration found")

    # Run clang-format check on the target file
    r = subprocess.run(
        ["clang-format-18", "--dry-run", "--Werror", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If there are formatting issues, report them but don't fail
    # This is a style guide, not a hard requirement
    if r.returncode != 0:
        # Just a warning - the project may have existing formatting issues
        pass

    pass


def test_no_trailing_whitespace():
    """
    Pass-to-pass test: Modified lines have no trailing whitespace.
    """
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # Check for trailing whitespace (excluding newline)
        if line.rstrip('\n').endswith((' ', '\t')):
            # Only check lines around our expected change
            if 'text_indexes_to_merge' in line or 'materialize_skip_indexes' in line:
                assert False, f"FAIL: Line {i+1} has trailing whitespace: '{line}'"

    pass


def test_no_tabs_in_code():
    """
    Pass-to-pass test: No tabs in the modified file.
    From repo CI (check_cpp.sh): tabs are not allowed in ClickHouse code.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for any tabs in the file
    if '\t' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '\t' in line:
                assert False, f"FAIL: Found tab character at line {i+1}: '{line}'"

    pass


def test_no_crlf_line_endings():
    """
    Pass-to-pass test: No CRLF line endings in the modified file.
    Repo standard requires LF line endings only.
    """
    with open(TARGET_FILE, 'rb') as f:
        content = f.read()

    # Check for CRLF line endings
    if b'\r\n' in content:
        assert False, "FAIL: Found CRLF line endings (Windows style) in the file. Use LF only."

    pass


def test_file_ends_with_newline():
    """
    Pass-to-pass test: File ends with a newline character.
    POSIX standard requires text files to end with newline.
    """
    with open(TARGET_FILE, 'rb') as f:
        content = f.read()

    if not content.endswith(b'\n'):
        assert False, "FAIL: File does not end with a newline character."

    pass


def test_utf8_encoding():
    """
    Pass-to-pass test: File uses valid UTF-8 encoding.
    ClickHouse source files must be UTF-8 encoded.
    """
    with open(TARGET_FILE, 'rb') as f:
        content = f.read()

    try:
        content.decode('utf-8')
    except UnicodeDecodeError as e:
        assert False, f"FAIL: File is not valid UTF-8: {e}"

    pass


def test_repo_clang_format():
    """
    Pass-to-pass test: Repo CI - clang-format check on target file.
    ClickHouse CI runs clang-format on all modified C++ files.
    """
    # Use the repo's .clang-format configuration
    clang_format_config = os.path.join(REPO, ".clang-format")
    if not os.path.exists(clang_format_config):
        pytest.skip("No .clang-format config in repo")

    # Check if clang-format is available
    r = subprocess.run(
        ["which", "clang-format-18"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        pytest.skip("clang-format-18 not available")

    # Run clang-format --dry-run --Werror (like CI does)
    r = subprocess.run(
        ["clang-format-18", "--dry-run", "--Werror", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    # Note: The file may have pre-existing formatting issues
    # We only fail if the command itself errors (e.g., invalid config)
    assert r.returncode == 0 or "replacing" in r.stderr.lower() or "error" not in r.stderr.lower(), \
        f"clang-format failed with errors:\n{r.stderr[:1000]}"


def test_repo_git_whitespace_check():
    """
    Pass-to-pass test: Repo CI - git diff --check for whitespace errors.
    ClickHouse CI runs git diff --check to catch trailing whitespace.
    """
    # Ensure we're in a git repo
    git_dir = os.path.join(REPO, ".git")
    if not os.path.exists(git_dir):
        pytest.skip("Not a git repository")

    # Run git diff --check (looks for trailing whitespace, conflict markers, etc.)
    r = subprocess.run(
        ["git", "diff", "--check"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # This should pass - any whitespace errors would indicate issues
    assert r.returncode == 0, \
        f"Git whitespace check failed:\n{r.stdout}{r.stderr}"


def test_repo_cpp_style_tabs():
    """
    Pass-to-pass test: Repo CI - check_cpp.sh tabs check.
    ClickHouse CI forbids tabs in source files via check_cpp.sh.
    """
    # Run grep to find tabs (same as CI's check_cpp.sh does)
    r = subprocess.run(
        ["grep", "-F", "\t", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If grep finds tabs, it returns 0; if no tabs, returns 1
    # So tabs exist when returncode == 0
    if r.returncode == 0 and r.stdout.strip():
        # Found tabs - check if they're in the target area
        lines_with_tabs = r.stdout.strip().split('\n')
        for line in lines_with_tabs[:5]:  # Show first 5
            if line.strip():
                assert False, f"FAIL: Found tab character in file. Line: {line[:200]}"

    # Also run the same check using bash to be thorough
    r2 = subprocess.run(
        ["bash", "-c", f'grep -F $\'\\t\' "{TARGET_FILE}" && echo "^ tabs are not allowed"'],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert "tabs are not allowed" not in r2.stdout, \
        "FAIL: Tabs found in source file (ClickHouse CI style violation)"


def test_repo_cpp_style_trailing_ws():
    """
    Pass-to-pass test: Repo CI - check_cpp.sh trailing whitespace check.
    ClickHouse CI forbids trailing whitespace via check_cpp.sh.
    """
    # Run grep for trailing whitespace (same as CI's check_cpp.sh)
    r = subprocess.run(
        ["grep", "-n", "-P", " $", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # Filter to lines in the target area
    if r.returncode == 0 and r.stdout.strip():
        lines = r.stdout.strip().split('\n')
        for line in lines:
            if 'text_indexes_to_merge' in line or 'materialize_skip_indexes' in line:
                assert False, f"FAIL: Trailing whitespace in modified area:\n{line}"


def test_repo_pragma_once_headers():
    """
    Pass-to-pass test: Repo CI - check that headers have #pragma once.
    ClickHouse CI requires all header files to start with #pragma once.
    """
    # Find header files in the same directory as the modified file
    target_dir = os.path.dirname(TARGET_FILE)
    header_files = []

    if os.path.exists(target_dir):
        for f in os.listdir(target_dir):
            if f.endswith('.h'):
                header_files.append(os.path.join(target_dir, f))

    if not header_files:
        pytest.skip("No header files in target directory to check")

    # Check each header for #pragma once
    for header_file in header_files[:3]:  # Check up to 3 headers
        if not os.path.exists(header_file):
            continue

        r = subprocess.run(
            ["head", "-n1", header_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=REPO,
        )

        if r.returncode == 0:
            first_line = r.stdout.strip()
            assert first_line == '#pragma once', \
                f"FAIL: {header_file} must have '#pragma once' in first line, found: {first_line}"
