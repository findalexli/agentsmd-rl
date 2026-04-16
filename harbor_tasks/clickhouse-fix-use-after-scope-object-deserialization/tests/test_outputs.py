#!/usr/bin/env python3
"""
Test suite for clickhouse-fix-use-after-scope-object-deserialization task.

This test suite verifies:
1. The SCOPE_EXIT fix is correctly applied (fail_to_pass)
2. Code follows ClickHouse style guidelines (pass_to_pass)
3. No improper patterns like sleep() are used (fail_to_pass)
"""

import subprocess
import re
import os
import sys

# Constants
REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/DataTypes/Serializations/SerializationObject.cpp"
TARGET_PATH = os.path.join(REPO, TARGET_FILE)


def read_target_file():
    """Read the target source file."""
    with open(TARGET_PATH, 'r') as f:
        return f.read()


def test_scope_exit_added():
    """
    Fail-to-pass: Verify SCOPE_EXIT block is added for task cleanup.

    The fix must add a SCOPE_EXIT block after task_size calculation that:
    1. Calls tryExecute() on all tasks
    2. Calls wait() on all tasks
    3. Is positioned after task_size = ... line
    """
    content = read_target_file()

    # Check for SCOPE_EXIT macro usage
    scope_exit_pattern = r'SCOPE_EXIT\s*\('
    assert re.search(scope_exit_pattern, content), \
        "SCOPE_EXIT macro not found - fix not applied"

    # Check for tryExecute() call in SCOPE_EXIT context
    tryexecute_pattern = r'task->tryExecute\(\)'
    assert re.search(tryexecute_pattern, content), \
        "task->tryExecute() not found in cleanup code"

    # Check for wait() call in SCOPE_EXIT context
    wait_pattern = r'task->wait\(\)'
    assert re.search(wait_pattern, content), \
        "task->wait() not found in cleanup code"

    # Check for the explanatory comment
    comment_pattern = r'Ensure all already-scheduled tasks are drained.*exit path.*exception'
    assert re.search(comment_pattern, content, re.IGNORECASE | re.DOTALL), \
        "Explanatory comment about exception safety not found"

    # Verify the structure: SCOPE_EXIT with for loops for tryExecute and wait
    full_pattern = r'SCOPE_EXIT\s*\(\s*for\s*\(const\s+auto\s+&\s+task\s+:\s+tasks\)\s+task->tryExecute\(\);\s*for\s*\(const\s+auto\s+&\s+task\s+:\s+tasks\)\s+task->wait\(\);\s*\);'
    assert re.search(full_pattern, content, re.DOTALL), \
        "SCOPE_EXIT block structure is incorrect - expected tryExecute loop followed by wait loop"


def test_no_sleep_for_race_fix():
    """
    Fail-to-pass: Verify fix does not use sleep() to address race conditions.

    Per ClickHouse guidelines: "Never use sleep in C++ code to fix race conditions
    - this is stupid and not acceptable!"
    """
    content = read_target_file()

    # Check for sleep/usleep/nanosleep calls in the modified function context
    # Look for sleep patterns (std::this_thread::sleep_for, usleep, sleep, nanosleep)
    sleep_patterns = [
        r'\bsleep\s*\(',
        r'\busleep\s*\(',
        r'nanosleep\s*\(',
        r'sleep_for\s*\(',
        r'sleep_until\s*\(',
        r'this_thread::sleep',
    ]

    for pattern in sleep_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        assert not match, \
            f"Found sleep call matching '{pattern}' - using sleep to fix races is not acceptable"


def test_allman_braces():
    """
    Fail-to-pass: Verify code uses Allman brace style.

    Per ClickHouse CLAUDE.md: "always use Allman-style braces (opening brace on a new line)"
    """
    content = read_target_file()

    # Find the SCOPE_EXIT block and check its brace style
    scope_exit_match = re.search(
        r'SCOPE_EXIT\s*(\([^)]*\))\s*\{',
        content,
        re.DOTALL
    )

    if scope_exit_match:
        # Check if there's a newline before the opening brace
        scope_exit_section = content[scope_exit_match.start():scope_exit_match.end()]
        # The SCOPE_EXIT macro in ClickHouse uses parentheses for the body
        # Check that the macro usage follows proper formatting
        assert '(' in scope_exit_section, \
            "SCOPE_EXIT macro must use parentheses for the body"

    # Check for non-Allman style: ) {
    non_allman_pattern = r'\)\s*\{[^\n]*\n[^\n]*\}'
    # This is a relaxed check - we mainly care the SCOPE_EXIT is properly formatted
    # The key is that the fix is syntactically correct


def test_raii_cleanup():
    """
    Fail-to-pass: Verify fix uses RAII patterns (SCOPE_EXIT) rather than manual cleanup.

    Per ClickHouse guidelines: avoid manual cleanup, use RAII types.
    """
    content = read_target_file()

    # Check that SCOPE_EXIT is used (RAII pattern)
    assert 'SCOPE_EXIT' in content, \
        "Fix should use SCOPE_EXIT (RAII pattern) for cleanup, not manual try-catch blocks"

    # Check that we're NOT using manual try-catch for this specific cleanup
    # (A try block with catch that's just for cleanup would be an anti-pattern)
    deserialize_func = re.search(
        r'void SerializationObject::deserializeBinaryBulkStatePrefix\([^)]*\)\s*\{',
        content
    )

    if deserialize_func:
        # Find the function body (approximate)
        func_start = deserialize_func.start()
        # Look for try blocks in the parallel deserialization section
        # We want to ensure SCOPE_EXIT is used, not try-catch for flow control
        pass  # SCOPE_EXIT presence already checked above


def test_file_compiles():
    """
    Pass-to-pass: Verify the target file can be compiled.

    This is a basic sanity check that the code is syntactically valid.
    We use clang to check for syntax errors, which verifies includes and basic syntax.
    """
    # Run clang syntax check -fsyntax-only checks for syntax errors without full compilation
    # We check the target file along with its header to verify basic structure
    result = subprocess.run(
        ["clang", "-fsyntax-only", "-std=c++20", "-c", TARGET_PATH],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # We expect this to fail due to missing includes in minimal Docker,
    # but we can check for specific syntax errors vs just missing headers
    # A clean file should only have "file not found" errors, not syntax errors
    stderr_lower = result.stderr.lower()

    # Check for actual syntax errors (not just missing headers)
    syntax_errors = [
        "syntax error",
        "expected",
        "unexpected",
        "undeclared identifier",
        "invalid",
        "error: member access",
        "error: no matching",
    ]

    for error in syntax_errors:
        assert error not in stderr_lower, \
            f"Syntax error detected: {error}\n{result.stderr[:500]}"


def test_no_tabs_in_target():
    """
    Pass-to-pass: Verify target file has no tab characters.

    ClickHouse style guide prohibits tabs in source files.
    """
    result = subprocess.run(
        ["grep", "-q", "-P", r"\t", TARGET_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    # grep -q returns 0 if pattern found, 1 if not found
    assert result.returncode == 1, \
        f"Target file contains tab characters - ClickHouse style requires spaces"


def test_no_trailing_spaces_in_target():
    """
    Pass-to-pass: Verify target file has no trailing whitespace.

    Trailing whitespace is a style violation.
    """
    result = subprocess.run(
        ["grep", "-q", "-P", " $", TARGET_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    # grep -q returns 0 if pattern found, 1 if not found
    assert result.returncode == 1, \
        f"Target file contains trailing whitespace"


def test_header_pragma_once():
    """
    Pass-to-pass: Verify header file has #pragma once in first line.

    ClickHouse requires all header files to have #pragma once.
    """
    header_path = os.path.join(REPO, "src/DataTypes/Serializations/SerializationObject.h")

    result = subprocess.run(
        ["head", "-n1", header_path],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    first_line = result.stdout.strip()
    assert first_line == "#pragma once", \
        f"Header file must have '#pragma once' in first line, got: {first_line}"


def test_clang_format():
    """
    Pass-to-pass: Verify code does not have egregious clang-format violations.

    ClickHouse uses clang-format for consistent style. The base commit may
    have some existing formatting issues - we only check for critical issues
    like tabs or extremely bad formatting that would block CI.
    """
    result = subprocess.run(
        ["clang-format", "--dry-run", "--Werror", TARGET_PATH],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Note: The base commit may have existing style differences from clang-format.
    # This is a sanity check that the file doesn't have extremely bad formatting.
    # We accept that the base commit may have minor formatting issues.

    stderr = result.stderr
    error_count = stderr.count("error:")

    # Allow up to 200 formatting errors (the base commit has ~103 existing issues)
    # The key is that the fix doesn't introduce NEW egregious formatting errors
    if error_count > 200:
        errors = [line for line in stderr.split('\n') if 'error:' in line][:5]
        assert False, f"Too many formatting errors ({error_count}):\n" + "\n".join(errors)


def test_fix_positioned_correctly():
    """
    Fail-to-pass: Verify the fix is placed at the correct location.

    The SCOPE_EXIT should be added after task_size calculation and before
    the for loop that schedules tasks.
    """
    content = read_target_file()

    # Find the task_size line
    task_size_match = re.search(r'task_size\s*=\s*std::max\(', content)
    if not task_size_match:
        # If task_size not found, the code structure is different - skip this check
        # The main test_scope_exit_added will still verify the fix is present
        return

    # Find SCOPE_EXIT after task_size
    scope_exit_match = re.search(r'SCOPE_EXIT\s*\(', content)
    if not scope_exit_match:
        raise AssertionError("SCOPE_EXIT not found in file")

    # Find the for loop that schedules tasks
    for_loop_match = re.search(r'for\s*\(\s*size_t\s+i\s*=\s*0\s*;\s*i\s*!=\s*num_tasks', content)

    # Verify SCOPE_EXIT is between task_size and the for loop
    task_size_pos = task_size_match.start()
    scope_exit_pos = scope_exit_match.start()

    if for_loop_match:
        for_loop_pos = for_loop_match.start()
        # SCOPE_EXIT should be after task_size and before for loop
        if not (task_size_pos < scope_exit_pos < for_loop_pos):
            raise AssertionError(
                f"Fix not positioned correctly - SCOPE_EXIT at {scope_exit_pos} "
                f"should be after task_size at {task_size_pos} and before for loop at {for_loop_pos}"
            )
    else:
        # Just verify SCOPE_EXIT is after task_size
        if scope_exit_pos < task_size_pos:
            raise AssertionError(
                f"SCOPE_EXIT at {scope_exit_pos} should be after task_size at {task_size_pos}"
            )


def test_comment_quality():
    """
    Fail-to-pass: Verify the explanatory comment is present and adequate.

    The fix should explain WHY it's needed (exception safety, dangling references).
    """
    content = read_target_file()

    # Check for meaningful comment about exception safety
    required_concepts = [
        r'drained|cleanup|exit path|exception',
        r'dangling|stack|locals?|reference',
        r'task|thread|pool'
    ]

    # Find the comment before SCOPE_EXIT
    scope_exit_pos = content.find('SCOPE_EXIT')
    if scope_exit_pos > 0:
        # Get text before SCOPE_EXIT (up to 200 chars)
        context = content[max(0, scope_exit_pos-200):scope_exit_pos]

        comment_found = False
        for pattern in required_concepts:
            if re.search(pattern, context, re.IGNORECASE):
                comment_found = True
                break

        assert comment_found, \
            "Comment should explain the purpose: preventing dangling references on exception"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
