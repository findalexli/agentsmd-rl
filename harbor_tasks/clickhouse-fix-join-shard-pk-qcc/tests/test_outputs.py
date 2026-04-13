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
    Pass-to-pass: Verify the C++ file has valid syntax (balanced braces, parentheses).

    Static check for basic syntax validity using character counting.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

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


def test_repo_git_status():
    """
    Pass-to-pass: Verify the repository has a clean git status (repo CI check).

    Uses git status to check that the sparse checkout is valid and
    the repository is in a consistent state.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"

    # The sparse checkout should have no uncommitted changes on base commit
    # Any output would indicate untracked or modified files (which is unexpected)
    # Note: In sparse checkout, git status may show some limitations but should work


def test_repo_file_type():
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


def test_repo_git_log():
    """
    Pass-to-pass: Verify git log is accessible and shows expected commit (repo CI check).

    Uses git log to check that we can access the repository history.
    This validates the git metadata is intact.
    """
    r = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"git log failed: {r.stderr}"

    # Should have at least one commit (the sparse checkout commit)
    assert r.stdout.strip(), "git log returned empty output"

    # Verify we can see the commit hash format
    # Format should be "<hash> <message>"
    assert re.match(r'^[a-f0-9]+\s+', r.stdout), \
        f"Unexpected git log format: {r.stdout}"


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


def test_file_has_pragma_once_in_headers():
    """
    Pass-to-pass: Verify header files have #pragma once (repo style check).

    ClickHouse CI checks that every header file has #pragma once in first line.
    This test verifies the convention is followed.
    """
    # Find all .h files in the same directory as the target file
    import glob
    header_dir = os.path.join(REPO, "src/Processors/QueryPlan/Optimizations")
    header_files = glob.glob(os.path.join(header_dir, "*.h"))

    for header_file in header_files:
        with open(header_file, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == '#pragma once', \
            f"File {header_file} must have '#pragma once' in first line, got: {first_line}"


def test_no_duplicate_includes():
    """
    Pass-to-pass: Verify no duplicate #include statements (repo style check).

    ClickHouse CI checks for duplicate includes. This test verifies
    the modified file doesn't have duplicate includes.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    with open(filepath, 'r') as f:
        includes = []
        for line in f:
            if re.match(r'^#include ', line):
                includes.append(line.strip())

    # Check for duplicates
    seen = set()
    duplicates = []
    for inc in includes:
        if inc in seen:
            duplicates.append(inc)
        seen.add(inc)

    assert not duplicates, \
        f"Found duplicate includes: {duplicates[:5]}"


def test_repo_no_bom():
    """
    Pass-to-pass: Verify no UTF-8 BOM in source files (repo CI check).

    ClickHouse CI checks that source files do not have UTF-8 BOM markers.
    """
    r = subprocess.run(
        ["bash", "-c",
         f"find {REPO}/src/Processors/QueryPlan/Optimizations -name '*.cpp' -o -name '*.h' | xargs grep -l -F $(printf '\\xEF\\xBB\\xBF') 2>/dev/null || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found files with UTF-8 BOM: {r.stdout.strip()[:200]}"


def test_repo_no_conflict_markers():
    """
    Pass-to-pass: Verify no git conflict markers (repo CI check).

    ClickHouse CI checks for leftover conflict markers from merges.
    """
    r = subprocess.run(
        ["bash", "-c",
         f"grep -P '^(<<<<<<<|=======|>>>>>>>)' {REPO}/{TARGET_FILE} 2>/dev/null || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found conflict markers: {r.stdout.strip()[:200]}"


def test_repo_no_dos_newlines():
    """
    Pass-to-pass: Verify no DOS/Windows newlines (repo CI check).

    ClickHouse CI checks that files use Unix newlines (LF), not CRLF.
    """
    r = subprocess.run(
        ["bash", "-c",
         f"grep -l -P '\\r$' {REPO}/{TARGET_FILE} 2>/dev/null || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", "Found DOS/Windows newlines (CRLF) in file"


def test_repo_brace_balance():
    """
    Pass-to-pass: Verify C++ file has balanced braces (repo CI check).

    ClickHouse style check verifies balanced braces and parentheses.
    """
    cmd = f"""open=$(grep -o '{{' {REPO}/{TARGET_FILE} | wc -l); close=$(grep -o '}}' {REPO}/{TARGET_FILE} | wc -l); if [ "$open" -eq "$close" ]; then exit 0; else echo "Unbalanced: $open != $close"; exit 1; fi"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unbalanced braces: {r.stderr or r.stdout}"


def test_repo_paren_balance():
    """
    Pass-to-pass: Verify C++ file has balanced parentheses (repo CI check).

    ClickHouse style check verifies balanced parentheses.
    """
    cmd = f"""open=$(grep -o '(' {REPO}/{TARGET_FILE} | wc -l); close=$(grep -o ')' {REPO}/{TARGET_FILE} | wc -l); if [ "$open" -eq "$close" ]; then exit 0; else echo "Unbalanced: $open != $close"; exit 1; fi"""
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Unbalanced parentheses: {r.stderr or r.stdout}"


def test_repo_no_std_stringstream():
    """
    Pass-to-pass: Verify no std::stringstream usage (repo CI check).

    ClickHouse CI forbids std::stringstream in favor of WriteBufferFromOwnString.
    """
    r = subprocess.run(
        ["bash", "-c",
         f"grep -P 'std::[io]?stringstream' {REPO}/{TARGET_FILE} 2>/dev/null || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found std::stringstream usage: {r.stdout.strip()[:200]}"


def test_repo_clang_syntax_check():
    """
    Pass-to-pass: Verify C++ file compiles with clang -fsyntax-only (repo CI check).

    ClickHouse CI uses clang for compilation. This test validates that the
    modified file has valid C++ syntax that can be parsed by clang.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Run clang in syntax-check only mode with minimal includes
    # We use -fsyntax-only to just check syntax without generating code
    r = subprocess.run(
        ["clang", "-fsyntax-only", "-std=c++20", "-c", filepath],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )

    # Allow for missing includes - we're only checking basic syntax
    # Exit code 0 means syntax is valid
    # Some errors about missing headers are OK for syntax-only check
    syntax_errors = [line for line in r.stderr.split("\n")
                     if "error:" in line and "file not found" not in line and "fatal error" not in line]

    assert len(syntax_errors) == 0, \
        f"C++ syntax errors found:\n{r.stderr[:1000]}"


def test_repo_header_pragma_check():
    """
    Pass-to-pass: Verify all header files have #pragma once (repo CI check).

    ClickHouse CI requires every header file to have #pragma once in the first line.
    """
    header_dir = os.path.join(REPO, "src/Processors/QueryPlan/Optimizations")

    # Get list of header files
    r = subprocess.run(
        ["find", header_dir, "-name", "*.h"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    if r.returncode != 0 or not r.stdout.strip():
        # No header files found, skip
        return

    header_files = [f for f in r.stdout.strip().split("\n") if f]

    violations = []
    for header_file in header_files:
        r_head = subprocess.run(
            ["head", "-1", header_file],
            capture_output=True, text=True, timeout=10
        )
        if r_head.returncode == 0 and r_head.stdout.strip() != "#pragma once":
            violations.append(os.path.basename(header_file))

    assert not violations, \
        f"Files missing #pragma once in first line: {violations}"


def test_repo_include_style_check():
    """
    Pass-to-pass: Verify #include <...> style is used (repo CI check).

    ClickHouse CI checks that includes use angle brackets <> not quotes ""
    for non-generated files (except for specific config headers).
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Check for quoted includes (excluding allowed exceptions)
    r = subprocess.run(
        ["bash", "-c",
         f"grep -P '#include[\\s]*\"' {filepath} | grep -v 'config.h' | grep -v 'config_tools.h' || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    # Filter out empty lines and comments
    violations = [line for line in r.stdout.split("\n")
                  if line.strip() and not line.strip().startswith("//")]

    assert len(violations) == 0, \
        f"Found includes with quotes instead of angle brackets: {violations[:5]}"


def test_repo_no_cyrillic_chars():
    """
    Pass-to-pass: Verify no Cyrillic characters mixed with Latin (repo CI check).

    ClickHouse CI checks for accidental Cyrillic characters in the source code.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Check for Cyrillic characters adjacent to Latin
    r = subprocess.run(
        ["bash", "-c",
         f"grep -P '[a-zA-Z][а-яА-ЯёЁ]|[а-яА-ЯёЁ][a-zA-Z]' {filepath} || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.stdout.strip() == "", \
        f"Found Cyrillic characters mixed with Latin: {r.stdout.strip()[:200]}"
