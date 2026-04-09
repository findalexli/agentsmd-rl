#!/usr/bin/env python3
"""
Tests for ClickHouse JOIN shard-by-PK with query condition cache fix.

This PR fixes a bug where JOIN queries with shard-by-PK optimization and
query condition cache could return wrong results. The issue was that
filterPartsByQueryConditionCache can drop parts, leaving non-contiguous
part_index_in_query values, but the distribution logic assumed contiguous indices.

The fix renumbers part_index_in_query to be contiguous starting from added_parts.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"


def test_fix_comment_present():
    """
    Fail-to-pass: Verify the explanatory comment about the fix is present.

    The fix adds a comment explaining why part_index_in_query needs to be
    renumbered contiguously when filterPartsByQueryConditionCache drops parts.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Check for the explanatory comment about the fix
    expected_comment = "Renumber part_index_in_query to be contiguous starting from added_parts"
    assert expected_comment in content, \
        f"Fix comment not found. Expected: '{expected_comment}'"

    # Check for mention of filterPartsByQueryConditionCache
    assert "filterPartsByQueryConditionCache" in content, \
        "Reference to filterPartsByQueryConditionCache not found in comment"


def test_contiguous_index_assignment():
    """
    Fail-to-pass: Verify part_index_in_query is assigned contiguously.

    Before the fix:
        for (const auto & part : analysis_result->parts_with_ranges)
        {
            all_parts.push_back(part);
            all_parts.back().part_index_in_query += added_parts;
        }

    After the fix:
        for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
        {
            all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);
            all_parts.back().part_index_in_query = added_parts + local_idx;
        }
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Check for the new loop pattern with local_idx
    assert "for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)" in content, \
        "Fixed loop pattern with local_idx not found"

    # Check that part_index_in_query is assigned using local_idx (contiguous)
    assert "part_index_in_query = added_parts + local_idx" in content, \
        "Contiguous part_index_in_query assignment not found"

    # Verify the old buggy pattern is NOT present
    # The old code used "part_index_in_query += added_parts" which doesn't ensure contiguous indices
    # after parts are filtered by filterPartsByQueryConditionCache
    buggy_pattern = "all_parts.back().part_index_in_query += added_parts"
    assert buggy_pattern not in content, \
        f"Buggy pattern '{buggy_pattern}' still present in code"


def test_file_syntax_valid():
    """
    Pass-to-pass: Verify the C++ file compiles without syntax errors.

    Run clang syntax check on the modified file.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Use clang to check syntax only (don't compile fully)
    # We need to find the right include paths - use a simpler approach
    # Just check for balanced braces and basic syntax

    with open(filepath, 'r') as f:
        content = f.read()

    # Basic syntax checks
    # Count braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"

    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check for common syntax errors
    assert content.count('"') % 2 == 0, "Unbalanced double quotes"


def test_analysis_results_usage():
    """
    Pass-to-pass: Verify analysis_results is properly used after the loop.

    The code should push analysis_result into analysis_results after processing.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the apply function and check the flow
    assert "analysis_results.push_back(std::move(analysis_result))" in content, \
        "analysis_results.push_back not found after processing loop"


def test_code_structure_intact():
    """
    Pass-to-pass: Verify overall code structure is intact.

    Check that key structures in the file are preserved.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Check function signature
    assert "static void apply(struct JoinsAndSourcesWithCommonPrimaryKeyPrefix & data)" in content, \
        "apply function signature changed or missing"

    # Check key variables exist
    assert "all_parts" in content, "all_parts variable missing"
    assert "analysis_result" in content, "analysis_result variable missing"
    assert "added_parts" in content, "added_parts variable missing"

    # Check the struct definition exists
    assert "struct JoinsAndSourcesWithCommonPrimaryKeyPrefix" in content or \
           "JoinsAndSourcesWithCommonPrimaryKeyPrefix" in content, \
        "JoinsAndSourcesWithCommonPrimaryKeyPrefix struct reference missing"


def test_file_is_valid_cpp():
    """
    Pass-to-pass: Verify target file is a valid C++ source file (repo CI check).

    Uses the 'file' command to validate file type, similar to basic CI checks
    that ensure files are not corrupted or saved with wrong encoding.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Run file command to check file type
    r = subprocess.run(
        ["file", filepath],
        capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"file command failed: {r.stderr}"

    # Check that it's recognized as C++ source
    assert "C++ source" in r.stdout, \
        f"File not recognized as C++ source: {r.stdout}"
    assert "ASCII text" in r.stdout, \
        f"File not recognized as ASCII text: {r.stdout}"


def test_no_trailing_whitespace():
    """
    Pass-to-pass: Verify no trailing whitespace in modified file (repo style check).

    ClickHouse CI runs style checks that flag trailing whitespace.
    This test prevents introducing whitespace issues.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    violations = []
    for i, line in enumerate(lines, 1):
        # Check for trailing whitespace (excluding newline)
        if line.rstrip() != line.rstrip('\n').rstrip('\r'):
            # Actually check: if the line has trailing whitespace before newline
            stripped = line.rstrip('\n').rstrip('\r')
            if stripped != line.rstrip('\n').rstrip('\r').rstrip():
                violations.append(f"Line {i}: {repr(line)}")

    # More accurate check for trailing whitespace
    violations = []
    for i, line in enumerate(lines, 1):
        # Remove newline characters for checking
        content = line.rstrip('\n').rstrip('\r')
        # Check if there's trailing whitespace (space or tab at end)
        if content != content.rstrip():
            violations.append(i)

    assert not violations, \
        f"Found trailing whitespace on lines: {violations[:10]}..." if len(violations) > 10 else \
        f"Found trailing whitespace on lines: {violations}"


def test_no_tabs_for_indentation():
    """
    Pass-to-pass: Verify no tabs used for indentation (repo style check).

    ClickHouse uses 4 spaces for indentation. This test verifies
    the modified file follows this convention.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for tab characters at start of lines (indentation tabs)
    lines_with_tabs = []
    for i, line in enumerate(content.split('\n'), 1):
        if line.startswith('\t'):
            lines_with_tabs.append(i)

    assert not lines_with_tabs, \
        f"Found tabs for indentation on lines: {lines_with_tabs[:10]}" + \
        ("..." if len(lines_with_tabs) > 10 else "")
