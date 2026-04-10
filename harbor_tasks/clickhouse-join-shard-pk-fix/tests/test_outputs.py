#!/usr/bin/env python3
"""
Tests for the ClickHouse JOIN with shard-by-PK and query condition cache fix.

The bug was in optimizeJoinByShards::apply() which assumed contiguous part_index_in_query values,
but filterPartsByQueryConditionCache can drop parts leaving gaps in the indices.

This caused the layer distribution logic to assign parts to wrong sources, producing 0 rows
instead of correct results.
"""

import subprocess
import os
import re
import ast
import sys
from pathlib import Path

REPO_PATH = Path("/workspace/ClickHouse")
TARGET_FILE = REPO_PATH / "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"

# Docker-internal repo path (what the REPO environment variable should be inside container)
REPO = "/workspace/ClickHouse"
TARGET_DIR = Path(REPO) / "src/Processors/QueryPlan/Optimizations"


class BugPatternChecker(ast.NodeVisitor):
    """AST visitor to detect the buggy loop pattern."""

    def __init__(self):
        self.has_buggy_range_for = False
        self.has_fixed_index_for = False
        self.found_increment = False

    def visit_For(self, node):
        # Check for range-based for loop (buggy pattern)
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Attribute):
                if node.iter.func.attr == "push_back":
                    self.has_buggy_range_for = True
        self.generic_visit(node)

    def visit_For(self, node):
        # Python 3.9+ compatibility - handle both old and new AST node types
        if hasattr(ast, 'NameConstant') and isinstance(node.target, ast.NameConstant):
            return

        # Check for the specific buggy pattern:
        # for (const auto & part : analysis_result->parts_with_ranges)
        if isinstance(node.iter, (ast.Attribute, ast.Subscript, ast.Call)):
            # Check if this looks like iteration over parts_with_ranges
            iter_str = ast.unparse(node.iter) if hasattr(ast, 'unparse') else ""
            if 'parts_with_ranges' in iter_str:
                # Check if body has push_back and += pattern
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.AugAssign):
                        if isinstance(stmt.op, ast.Add):
                            self.found_increment = True

        self.generic_visit(node)


def read_source_file():
    """Read the target source file."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def test_source_file_exists():
    """Verify the target source file exists."""
    assert TARGET_FILE.exists(), f"Target file does not exist: {TARGET_FILE}"


def test_file_has_apply_function():
    """Verify the file contains the apply() function that was fixed."""
    source = read_source_file()
    assert "static void apply(" in source, "apply() function not found"


def test_renumber_comment_present():
    """Verify the explanatory comment about renumbering is present (post-fix check)."""
    source = read_source_file()
    assert "Renumber part_index_in_query to be contiguous" in source, \
        "Fix comment not found - patch may not be applied"


def test_query_condition_cache_comment():
    """Verify the comment mentions filterPartsByQueryConditionCache (post-fix check)."""
    source = read_source_file()
    assert "filterPartsByQueryConditionCache" in source, \
        "filterPartsByQueryConditionCache comment not found"


def test_uses_index_based_loop():
    """Verify the fix uses index-based loop instead of range-based for (post-fix check)."""
    source = read_source_file()

    # Find the loop - should use local_idx index variable
    # Pattern: for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
    loop_pattern = r'for\s*\(\s*size_t\s+local_idx\s*=\s*0\s*;\s*local_idx\s*<\s*analysis_result->parts_with_ranges\.size\(\)\s*;\s*\+\+local_idx\s*\)'

    assert re.search(loop_pattern, source), \
        "Fixed index-based loop pattern not found"


def test_assigns_contiguous_index():
    """Verify part_index_in_query is assigned contiguous values (post-fix check)."""
    source = read_source_file()

    # The fix should have: all_parts.back().part_index_in_query = added_parts + local_idx;
    assignment_pattern = r'\.part_index_in_query\s*=\s*added_parts\s*\+\s*local_idx'

    assert re.search(assignment_pattern, source), \
        "Contiguous index assignment not found - should be 'added_parts + local_idx'"


def test_not_using_range_based_increment():
    """Verify the buggy range-based for with += pattern is NOT present (fail-to-pass check)."""
    source = read_source_file()

    # The buggy pattern was:
    # for (const auto & part : analysis_result->parts_with_ranges)
    # {
    #     all_parts.push_back(part);
    #     all_parts.back().part_index_in_query += added_parts;
    #

    # Check we don't have the buggy increment pattern
    buggy_pattern = r'\.part_index_in_query\s*\+?=\s*\+?\s*added_parts'

    # This should NOT match the += pattern (we use = added_parts + local_idx instead)
    # But careful: the fix also uses "added_parts" on the right side

    # More specific: look for += added_parts (the buggy pattern)
    increment_pattern = r'\.part_index_in_query\s*\+=\s*added_parts'

    match = re.search(increment_pattern, source)
    assert match is None, \
        f"Buggy increment pattern found at position {match.start() if match else 0}: '+= added_parts' should be '= added_parts + local_idx'"


def test_loop_uses_parts_with_ranges_indexing():
    """Verify the loop body indexes parts_with_ranges[local_idx] (post-fix check)."""
    source = read_source_file()

    # Should push back with explicit index: analysis_result->parts_with_ranges[local_idx]
    index_pattern = r'analysis_result->parts_with_ranges\[local_idx\]'

    assert re.search(index_pattern, source), \
        "Loop should index parts_with_ranges[local_idx]"


def test_distinctive_line_pattern():
    """Test for the distinctive line that identifies this specific fix."""
    source = read_source_file()

    # This is the most distinctive line from the patch
    distinctive = "Renumber part_index_in_query to be contiguous starting from added_parts"

    assert distinctive in source, \
        f"Distinctive fix line not found: '{distinctive}'"


def test_syntax_compiles():
    """Verify the C++ code compiles (syntax check)."""
    if not TARGET_FILE.exists():
        pytest.skip("Source file not found")

    # Run clang syntax check (fast, no object generation)
    result = subprocess.run(
        ["clang++", "-fsyntax-only", "-std=c++20", "-I", str(REPO_PATH / "src"), str(TARGET_FILE)],
        capture_output=True,
        text=True,
        cwd=str(REPO_PATH),
        timeout=60
    )

    # Note: This may have false positives due to missing includes
    # We mainly check for gross syntax errors
    if result.returncode != 0:
        # Filter out "file not found" errors which are include path issues
        errors = [line for line in result.stderr.split('\n')
                  if 'error:' in line and 'file not found' not in line and 'no such file' not in line.lower()]
        if errors:
            # Only fail on actual syntax errors, not missing headers
            non_header_errors = [e for e in errors if not any(x in e for x in ['#include', 'not found', 'could not find'])]
            if non_header_errors:
                assert False, f"Syntax errors found:\n{chr(10).join(non_header_errors[:5])}"


def test_builds_with_ninja():
    """Integration test: verify the code builds with ninja."""
    build_dir = REPO_PATH / "build"

    if not (build_dir / "build.ninja").exists():
        pytest.skip("Ninja build not configured")

    # Try to build just the target file's object (fastest check)
    result = subprocess.run(
        ["ninja", "-j4", "src/Processors/QueryPlan/Optimizations/CMakeFiles/clickhouse_query_plan_optimizations.dir/optimizeJoinByShards.cpp.o"],
        capture_output=True,
        text=True,
        cwd=str(build_dir),
        timeout=300
    )

    assert result.returncode == 0, f"Build failed:\n{result.stderr[-2000:]}"


# === Pass-to-Pass Tests: Repo CI/CD checks ===
# These tests verify that the repo's own CI checks pass on both base and fixed code.

REPO = "/workspace/ClickHouse"
TARGET_DIR = Path(REPO) / "src/Processors/QueryPlan/Optimizations"


def test_repo_clang_format():
    """ClickHouse source passes clang-format check (pass_to_pass)."""
    # NOTE: Disabled because the base commit code doesn't match the current
    # clang-format version. This is a known issue with older commits.
    pytest.skip("clang-format check disabled - base commit has pre-existing format issues")


def test_repo_clang_tidy():
    """ClickHouse source passes basic clang-tidy checks (pass_to_pass)."""
    target_file = TARGET_DIR / "optimizeJoinByShards.cpp"
    if not target_file.exists():
        pytest.skip("Target file not found")

    # Run clang-tidy with essential checks only (fast)
    r = subprocess.run(
        ["clang-tidy", str(target_file), "--", "-std=c++20", "-I", str(Path(REPO) / "src")],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Only fail on errors, not warnings
    errors = [line for line in r.stderr.split('\n') if 'error:' in line]
    if errors:
        assert False, f"clang-tidy errors found:\n{chr(10).join(errors[:5])}"


def test_repo_ninja_build_optimizations():
    """ClickHouse QueryPlan optimizations module builds with ninja (pass_to_pass)."""
    build_dir = Path(REPO) / "build"
    if not (build_dir / "build.ninja").exists():
        pytest.skip("Ninja build not configured")

    # Build just the target module to keep it fast
    r = subprocess.run(
        ["ninja", "-j4", "src/Processors/QueryPlan/Optimizations/CMakeFiles/clickhouse_query_plan_optimizations.dir/optimizeJoinByShards.cpp.o"],
        capture_output=True, text=True, timeout=120, cwd=str(build_dir),
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


def test_repo_code_style_braces():
    """ClickHouse code follows Allman brace style (pass_to_pass)."""
    target_file = TARGET_DIR / "optimizeJoinByShards.cpp"
    if not target_file.exists():
        pytest.skip("Target file not found")

    source = target_file.read_text()

    # Check for K&R style (brace on same line) which is discouraged in ClickHouse
    # Look for function definitions or control structures with brace on same line
    kr_patterns = [
        r'\)\s*\{',  # closing paren followed by opening brace on same line
    ]

    # This is a heuristic check - we look for the most common patterns
    # and verify they follow Allman style (brace on new line)
    lines = source.split('\n')
    violations = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        # Look for K&R patterns: control statements with { on same line
        if re.match(r'^\s*(if|for|while|switch)\s*\(.*\)\s*\{\s*$', stripped):
            violations.append(f"Line {i+1}: {stripped[:60]}")

    # Be lenient - just check we don't have obvious violations in the fixed code
    # The fix itself should follow Allman style
    assert len(violations) == 0, f"K&R style braces found (ClickHouse uses Allman style):\n{chr(10).join(violations[:5])}"


def test_repo_cpp_style_check():
    """ClickHouse source passes C++ style check script (pass_to_pass).

    This runs the actual CI style check script from ci/jobs/scripts/check_style/check_cpp.sh
    on the modified file. This is the same check that runs in ClickHouse CI.
    """
    target_file = TARGET_DIR / "optimizeJoinByShards.cpp"
    if not target_file.exists():
        pytest.skip("Target file not found")

    # Run the actual CI style check script
    r = subprocess.run(
        ["bash", "-c", f"./ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    # Filter for errors related to our target file only
    output = r.stdout + r.stderr
    target_file_name = "optimizeJoinByShards.cpp"

    errors = []
    for line in output.split('\n'):
        if target_file_name in line and ('error' in line.lower() or 'style' in line.lower() or line.endswith('^')):
            errors.append(line)
        elif line.startswith('^') and errors:
            # Include the marker line after errors
            errors.append(line)

    # The script returns 0 even with findings, so check for actual error messages
    if errors:
        assert False, f"C++ style check found issues:\n{chr(10).join(errors[:10])}"


def test_repo_no_trailing_whitespace():
    """ClickHouse source has no trailing whitespace (pass_to_pass)."""
    target_file = TARGET_DIR / "optimizeJoinByShards.cpp"
    if not target_file.exists():
        pytest.skip("Target file not found")

    r = subprocess.run(
        ["grep", "-n", "-P", " $", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    if r.returncode == 0 and r.stdout.strip():
        lines = r.stdout.strip().split('\n')[:5]
        assert False, f"Trailing whitespace found:\n{chr(10).join(lines)}"


def test_repo_no_tabs():
    """ClickHouse source uses spaces, not tabs (pass_to_pass)."""
    target_file = TARGET_DIR / "optimizeJoinByShards.cpp"
    if not target_file.exists():
        pytest.skip("Target file not found")

    r = subprocess.run(
        ["grep", "-F", "\t", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )

    assert r.returncode != 0 or not r.stdout.strip(), \
        f"Tab characters found in source - ClickHouse uses spaces for indentation"


def test_repo_pragma_once_headers():
    """ClickHouse header files have #pragma once (pass_to_pass)."""
    # Find all header files in the same directory as the modified file
    header_files = list(TARGET_DIR.glob("*.h"))
    if not header_files:
        pytest.skip("No header files to check")

    missing_pragma = []
    for h in header_files:
        r = subprocess.run(
            ["head", "-n1", str(h)],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        if r.returncode == 0 and r.stdout.strip() != "#pragma once":
            missing_pragma.append(h.name)

    assert len(missing_pragma) == 0, \
        f"Header files missing #pragma once: {missing_pragma}"


# Import pytest for skip functionality
try:
    import pytest
except ImportError:
    # Make a stub pytest module for when pytest isn't installed
    class StubPytest:
        @staticmethod
        def skip(reason):
            print(f"SKIP: {reason}")
            return
    pytest = StubPytest()


if __name__ == "__main__":
    # Run all tests
    import traceback

    tests = [
        test_source_file_exists,
        test_file_has_apply_function,
        test_renumber_comment_present,
        test_query_condition_cache_comment,
        test_uses_index_based_loop,
        test_assigns_contiguous_index,
        test_not_using_range_based_increment,
        test_loop_uses_parts_with_ranges_indexing,
        test_distinctive_line_pattern,
        test_syntax_compiles,
        test_builds_with_ninja,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
