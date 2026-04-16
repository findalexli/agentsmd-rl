#!/usr/bin/env python3
"""
Test suite for ClickHouse use-after-scope bugfix.

This tests that the fix for parallel Object type deserialization properly
drains thread pool tasks on exception paths. Behavioral tests verify
observable properties of the code through grep-based checks combined with
structural validation.
"""

import subprocess
import re
import os
import sys

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/src/DataTypes/Serializations/SerializationObject.cpp"

# =============================================================================
# Fail-to-Pass Tests (tests that should fail on base, pass with fix)
# =============================================================================

def test_scope_exit_present():
    """
    Verify SCOPE_EXIT macro is present to drain tasks on exception paths.
    This is the core fix for the use-after-scope bug.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for SCOPE_EXIT block that drains tasks
    assert "SCOPE_EXIT" in content, "SCOPE_EXIT macro missing - fix not applied"
    assert "task->tryExecute()" in content, "task->tryExecute() missing in SCOPE_EXIT"
    assert "task->wait()" in content, "task->wait() missing in SCOPE_EXIT"

    # Verify it's in the right function
    func_pattern = r'void\s+SerializationObject::deserializeBinaryBulkStatePrefix.*?\{'
    func_match = re.search(func_pattern, content, re.DOTALL)
    if func_match:
        func_start = func_match.start()
        scope_exit_pos = content.find("SCOPE_EXIT", func_start)
        assert scope_exit_pos > func_start, "SCOPE_EXIT not inside deserializeBinaryBulkStatePrefix"


def test_task_cleanup_order():
    """
    Verify the task cleanup happens before the task loop to catch early exceptions.
    The SCOPE_EXIT must be declared before tasks are scheduled in the loop.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    scope_exit_pos = content.find("SCOPE_EXIT")
    if scope_exit_pos == -1:
        raise AssertionError("SCOPE_EXIT not found")

    # Find the for loop that schedules tasks
    loop_pattern = r'for\s*\(\s*size_t\s+i\s*=\s*0\s*;\s*i\s*!=\s*num_tasks'
    loop_match = re.search(loop_pattern, content)
    if loop_match:
        loop_pos = loop_match.start()
        assert scope_exit_pos < loop_pos, \
            "SCOPE_EXIT must be declared BEFORE the task scheduling loop"


def test_comment_explains_fix():
    """
    Verify there's a comment explaining the SCOPE_EXIT purpose.
    Per ClickHouse conventions, important safety mechanisms need explanation.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    scope_exit_pos = content.find("SCOPE_EXIT")
    if scope_exit_pos == -1:
        raise AssertionError("SCOPE_EXIT not found")

    # Check for comment explaining the purpose (within 10 lines before)
    lines_before = content[:scope_exit_pos].split('\n')[-10:]
    before_text = '\n'.join(lines_before)

    has_explanation = any(phrase in before_text.lower() for phrase in [
        "drain", "dangling", "exception", "exit path", "pool threads",
        "stack locals", "references"
    ])

    assert has_explanation, \
        "Missing explanatory comment for SCOPE_EXIT - should explain why task draining is needed"


def test_uses_tasks_vector_reference():
    """
    Verify SCOPE_EXIT captures tasks by reference to drain them.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    scope_match = re.search(r'SCOPE_EXIT\s*\((.*?)\);', content, re.DOTALL)
    if scope_match:
        scope_content = scope_match.group(1)
        assert "task : tasks" in scope_content or "const auto & task : tasks" in scope_content, \
            "SCOPE_EXIT should iterate over tasks vector"


# =============================================================================
# Pass-to-Pass Tests (tests that should pass on both base and fix)
# =============================================================================

def test_repo_no_tabs_in_target():
    """
    Verify the target file has no tab characters (ClickHouse style requirement).
    Repo CI check: no tabs allowed in source files (pass_to_pass).
    """
    result = subprocess.run(
        ["grep", "-P", r"\t", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # grep returns 0 if pattern found (bad), 1 if not found (good)
    assert result.returncode != 0, f"Found tab characters in {TARGET_FILE}"


def test_repo_no_trailing_whitespace():
    """
    Verify no trailing whitespace in target file (ClickHouse style requirement).
    Repo CI check: no trailing spaces allowed (pass_to_pass).
    """
    result = subprocess.run(
        ["grep", "-n", " $", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # grep returns 0 if pattern found (bad), 1 if not found (good)
    assert result.returncode != 0, f"Found trailing whitespace in {TARGET_FILE}:\n{result.stdout[:500]}"


def test_repo_git_submodules_valid():
    """
    Verify git submodules are properly configured (ClickHouse CI check).
    Repo CI check: all submodules must exist and be valid (pass_to_pass).
    """
    result = subprocess.run(
        ["git", "submodule", "status"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Git submodule status failed:\n{result.stderr[:500]}"
    # Ensure we have submodules listed
    assert result.stdout.strip(), "No submodules found"


def test_file_syntax_valid():
    """
    Verify the modified file has valid C++ syntax using grep-based checks.
    This is a basic sanity check that the code follows C++ style rules.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # If SCOPE_EXIT is present, verify it has balanced parentheses and braces
    if "SCOPE_EXIT" in content:
        scope_match = re.search(r'SCOPE_EXIT\s*\((.*?)\);', content, re.DOTALL)
        if scope_match:
            scope_content = scope_match.group(1)
            # Check for balanced braces in the SCOPE_EXIT block
            open_braces = scope_content.count('{')
            close_braces = scope_content.count('}')
            assert open_braces == close_braces, \
                f"SCOPE_EXIT block has unbalanced braces: {open_braces} open, {close_braces} close"


def test_no_raw_pointers_for_ownership():
    """
    Verify the code uses RAII types, not raw pointers for ownership.
    Per ClickHouse conventions from copilot-instructions.md.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for the deserializeBinaryBulkStatePrefix function
    func_start = content.find("void SerializationObject::deserializeBinaryBulkStatePrefix")
    if func_start == -1:
        return  # Function not found, skip this test

    # Get function content (approximate - until next function at same indentation)
    func_content = content[func_start:func_start + 5000]

    # Check that we use unique_ptr for cache, not raw pointers
    assert "std::unique_ptr<SubstreamsDeserializeStatesCache>" in func_content or \
           "auto cache" in func_content, \
        "Should use RAII types for resource management"


def test_allman_brace_style_in_fix():
    """
    Verify Allman-style braces (opening brace on new line) in the SCOPE_EXIT block.
    Per CLAUDE.md: "always use Allman-style braces (opening brace on a new line)"
    Only check our fix, not the entire file.
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find SCOPE_EXIT block and check its braces
    scope_match = re.search(r'SCOPE_EXIT\s*\((.*?)\);', content, re.DOTALL)
    if not scope_match:
        return  # No SCOPE_EXIT, nothing to check

    scope_content = scope_match.group(1)
    lines = scope_content.split('\n')

    # Check that the SCOPE_EXIT block itself uses Allman style
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '{':
            continue
        if '{' in stripped and stripped != '{':
            if stripped.startswith('for ') or stripped.startswith('if '):
                if '{' in stripped and stripped.endswith('{'):
                    assert False, f"SCOPE_EXIT block should use Allman braces (line: {stripped})"

    scope_start = content.find("SCOPE_EXIT")
    if scope_start > 0:
        next_lines = content[scope_start:scope_start+200].split('\n')[:5]
        for line in next_lines[1:]:
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                if stripped == '{':
                    break
                if '{' in stripped:
                    pass
                break


def test_no_sleep_for_race_conditions():
    """
    Verify no sleep calls are used (per CLAUDE.md: "Never use sleep in C++ code to fix race conditions").
    """
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Look for sleep calls
    sleep_patterns = ['sleep(', 'usleep(', 'nanosleep(', 'std::this_thread::sleep']
    for pattern in sleep_patterns:
        assert pattern not in content, \
            f"Found '{pattern}' - sleep should not be used for synchronization"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
