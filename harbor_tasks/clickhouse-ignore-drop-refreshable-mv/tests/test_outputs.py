#!/usr/bin/env python3
"""Test suite for ClickHouse refreshable materialized views fix."""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Interpreters/InterpreterDropQuery.cpp")


def test_refreshable_view_check_exists():
    """Verify that the refreshable materialized view check exists (f2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the comment about refreshable views
    assert "Don't ignore DROP for refreshable materialized views" in content, \
        "Missing comment about refreshable materialized views"

    # Check for the dynamic_cast to StorageMaterializedView
    assert "dynamic_cast<StorageMaterializedView *>" in content, \
        "Missing dynamic_cast to StorageMaterializedView"

    # Check for isRefreshable() call
    assert "isRefreshable()" in content, \
        "Missing isRefreshable() call"

    # Check for is_refreshable_view variable
    assert "is_refreshable_view" in content, \
        "Missing is_refreshable_view variable"

    # Check that is_refreshable_view is used in the condition
    # Looking for the pattern where it's checked before ignore_drop_queries_probability
    pattern = r'!is_refreshable_view\s*&&\s*settings\[Setting::ignore_drop_queries_probability\]'
    assert re.search(pattern, content), \
        "is_refreshable_view is not properly used in the DROP query condition"


def test_truncate_behavior_documented():
    """Verify that TRUNCATE behavior is documented in the comment (f2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the comment explaining why TRUNCATE is problematic
    assert "TRUNCATE doesn't stop" in content, \
        "Missing explanation about TRUNCATE not stopping refresh task"

    assert "orphaned view would keep refreshing indefinitely" in content, \
        "Missing explanation about orphaned view behavior"


def test_cpp_syntax_valid():
    """Verify that the C++ file has valid syntax (p2p)."""
    # Use clang-tidy to check syntax
    result = subprocess.run(
        ["clang-tidy", "-checks=-*", TARGET_FILE, "--"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # clang-tidy might return non-zero for issues, but we just want to verify
    # the file is parseable. If it can't parse, stderr will have errors.
    error_patterns = [
        r"fatal error: .* file not found",
        r"error: expected",
        r"error: syntax error",
        r"error: unmatched",
    ]

    combined_output = result.stdout + result.stderr
    for pattern in error_patterns:
        matches = re.findall(pattern, combined_output, re.IGNORECASE)
        assert not matches, f"Syntax error found: {matches}"


def test_logic_structure():
    """Verify the logic structure is correct (p2p)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # The fix adds a check that converts DROP to TRUNCATE only when NOT a refreshable view
    # This means the condition should be: !is_refreshable_view && other_conditions

    # Find the section around the ignore_drop_queries_probability check
    lines = content.split('\n')

    # Check that dynamic_cast happens before the condition
    materialized_view_line = -1
    condition_line = -1

    for i, line in enumerate(lines):
        if "auto * materialized_view = dynamic_cast" in line:
            materialized_view_line = i
        if "!is_refreshable_view" in line and "ignore_drop_queries_probability" in line:
            condition_line = i

    if materialized_view_line != -1 and condition_line != -1:
        assert materialized_view_line < condition_line, \
            "dynamic_cast should happen before the is_refreshable_view check"


def test_repo_cpp_structure_valid():
    """Repo's C++ files have valid structure (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for balanced braces
    open_count = content.count("{")
    close_count = content.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} vs {close_count}"

    # Check for balanced parentheses
    open_p = content.count("(")
    close_p = content.count(")")
    assert open_p == close_p, f"Unbalanced parens: {open_p} vs {close_p}"

    # Check no null bytes
    assert chr(0) not in content, "File contains null bytes"

    # Check valid UTF-8
    try:
        content.encode("utf-8")
    except UnicodeEncodeError as e:
        assert False, f"Invalid UTF-8: {e}"


def test_repo_clang_tidy_basic():
    """Repo's clang-tidy basic checks pass (pass_to_pass)."""
    # Run clang-tidy with minimal checks that don't require full build system
    r = subprocess.run(
        ["clang-tidy", "-checks=-*,-clang-diagnostic-unknown-argument",
         "-extra-arg=-Wno-unknown-pragmas",
         "-extra-arg=-Wno-unused-command-line-argument",
         TARGET_FILE, "--"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )

    # Check for fatal errors that would indicate syntax issues
    fatal_error_pattern = r"fatal error:.*file not found"
    combined = r.stdout + r.stderr

    # We expect "file not found" for includes since we're not in a proper build context
    # But we should NOT see syntax errors like "expected" or "syntax error"
    syntax_errors = re.findall(r"error: expected|error: syntax error|error: unmatched", combined)
    assert not syntax_errors, f"Syntax errors found: {syntax_errors[:3]}"


def test_repo_code_style_basic():
    """Repo's basic code style checks pass (pass_to_pass)."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    # Check that file doesn't have tabs (basic style check)
    for i, line in enumerate(lines, 1):
        if '\t' in line:
            # Allow tabs in certain contexts (like makefiles, embedded scripts)
            pass  # Just check, don't assert - this is a p2p test

    # Check that file doesn't have trailing whitespace
    trailing_ws_count = 0
    for i, line in enumerate(lines, 1):
        if line.rstrip() != line:
            trailing_ws_count += 1

    # Too much trailing whitespace is a problem
    assert trailing_ws_count < 50, f"Too many lines with trailing whitespace: {trailing_ws_count}"

    # Check file starts with expected pattern
    first_line = lines[0] if lines else ""
    valid_starts = ['#include', '///', '/*', '#pragma', 'module']
    assert any(first_line.startswith(p) for p in valid_starts), \
        f"File doesn't start with expected pattern: {first_line[:50]}"


def test_repo_file_readable():
    """Repo's target file is readable and valid (pass_to_pass)."""
    # File exists
    assert os.path.exists(TARGET_FILE), f"Target file doesn't exist: {TARGET_FILE}"

    # File is readable
    assert os.access(TARGET_FILE, os.R_OK), f"Target file not readable: {TARGET_FILE}"

    # File has content
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    assert len(content) > 0, "Target file is empty"
    assert len(content) > 1000, "Target file seems too small"

    # Check for expected includes
    assert '#include' in content, "File missing any includes"

    # Check for namespace usage
    assert 'namespace DB' in content or 'namespace' in content, "File missing namespace"
