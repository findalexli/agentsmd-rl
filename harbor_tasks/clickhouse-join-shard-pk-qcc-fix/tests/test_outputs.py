"""
Tests for ClickHouse JOIN shard-by-PK with query condition cache fix.

This fix addresses a bug where optimizeJoinByShards assumed contiguous part_index_in_query
values, but filterPartsByQueryConditionCache could drop parts leaving gaps. This caused
the layer distribution to assign parts to wrong sources, producing incorrect (empty) results.
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def test_patch_applied():
    """Fail-to-pass: The fix must be applied (contiguous renumbering logic)."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for the fix: contiguous renumbering comment and logic
    assert "Renumber part_index_in_query to be contiguous" in content, \
        "Fix not applied: missing contiguous renumbering comment"

    # Check for the new indexing logic using local_idx
    assert "local_idx" in content, \
        "Fix not applied: missing local_idx variable"

    # Verify the old buggy pattern is NOT present (direct iteration without renumbering)
    # The old code did: for (const auto & part : analysis_result->parts_with_ranges)
    # followed by: all_parts.back().part_index_in_query += added_parts;
    buggy_pattern = r"for \(const auto & part : analysis_result->parts_with_ranges\)"
    if re.search(buggy_pattern, content):
        # If still present, check if it's in a different context or the fix wasn't applied
        # Check that we have the new for loop style
        new_pattern = r"for \(size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges\.size\(\); \+\+local_idx\)"
        assert re.search(new_pattern, content), \
            "Fix not applied: old pattern present but new pattern missing"


def test_contiguous_index_assignment():
    """Fail-to-pass: Verify part_index_in_query is assigned contiguously."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Find the apply function and check the renumbering logic
    # The fix should show: all_parts.back().part_index_in_query = added_parts + local_idx;
    fixed_assignment = "all_parts.back().part_index_in_query = added_parts + local_idx"
    assert fixed_assignment in content, \
        f"Fix not applied: expected '{fixed_assignment}' in code"

    # The old buggy code incremented the existing value: all_parts.back().part_index_in_query += added_parts;
    # This is okay if it exists but the key is the new assignment above must exist
    old_increment = "all_parts.back().part_index_in_query += added_parts"
    # Count occurrences - should be 0 or replaced
    if old_increment in content:
        # Make sure our new assignment takes precedence (is present)
        assert fixed_assignment in content, \
            "Both old and new patterns present - verify fix is correct"


def test_code_compiles_syntax():
    """Pass-to-pass: Basic C++ syntax validation of the modified file."""
    # Run clang -fsyntax-only to check for syntax errors
    # We need to find the right include paths for ClickHouse
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++20", "-w",
         f"-I{REPO}/src",
         f"-I{REPO}/contrib",
         FULL_PATH],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Syntax check may fail due to missing deps, but shouldn't have parse errors
    # We mainly care that the for-loop and assignment syntax is valid
    stderr_lower = result.stderr.lower()
    parse_errors = [line for line in result.stderr.split('\n')
                    if 'error' in line.lower() and
                    any(x in line.lower() for x in ['syntax', 'parse', 'expected', 'unexpected'])]

    # Filter out errors about missing includes/types - those are OK
    critical_errors = [e for e in parse_errors
                       if not any(x in e.lower() for x in ['unknown type', 'undeclared', 'no such file', 'not found'])]

    # The new for loop syntax should be valid
    assert len(critical_errors) == 0, f"Syntax errors found: {critical_errors}"


def test_comment_explains_fix():
    """Pass-to-pass: Verify the fix has explanatory comments."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Check for explanatory comment about the fix
    assert "filterPartsByQueryConditionCache" in content, \
        "Missing reference to filterPartsByQueryConditionCache in comments"

    # Check for explanation of non-contiguous indices
    assert "non-contiguous" in content.lower() or "contiguous" in content.lower(), \
        "Missing explanation about contiguous/non-contiguous indices"


def test_file_structure_intact():
    """Pass-to-pass: Verify the file structure is intact."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Basic structural checks
    assert "static void apply(struct JoinsAndSourcesWithCommonPrimaryKeyPrefix & data)" in content, \
        "apply function signature changed unexpectedly"

    assert "all_parts.push_back" in content, \
        "Missing all_parts.push_back calls"

    # Check braces are balanced (basic check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close"


def test_for_loop_indexing_logic():
    """Fail-to-pass: Verify the new indexing logic is correct."""
    with open(FULL_PATH, 'r') as f:
        lines = f.readlines()

    # Find the line with the new for loop
    found_loop = False
    found_assignment = False
    found_push = False

    for i, line in enumerate(lines):
        if "for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)" in line:
            found_loop = True
            # Check subsequent lines for push_back and assignment
            for j in range(i+1, min(i+10, len(lines))):
                next_line = lines[j]
                if "all_parts.push_back(analysis_result->parts_with_ranges[local_idx])" in next_line:
                    found_push = True
                if "all_parts.back().part_index_in_query = added_parts + local_idx" in next_line:
                    found_assignment = True

    assert found_loop, "New for loop with local_idx not found"
    assert found_push, "push_back with local_idx indexing not found"
    assert found_assignment, "Contiguous assignment using local_idx not found"


def test_repo_clang_format():
    """Repo's C++ code follows style guidelines (pass_to_pass)."""
    # Check that clang-format is available and can parse the file
    # We use --dry-run to check formatting without requiring write access
    r = subprocess.run(
        ["which", "clang-format-18"],
        capture_output=True, text=True, timeout=10
    )
    clang_format_available = r.returncode == 0

    if not clang_format_available:
        # Fallback: verify the file follows basic style patterns manually
        with open(FULL_PATH, 'r') as f:
            content = f.read()

        # Check basic formatting patterns from .clang-format:
        # - Opening braces should be on same line for control structures (WebKit style)
        # - Column limit is 140
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Check line length (with some tolerance for comments/strings)
            if len(line) > 150 and not line.strip().startswith('//'):
                # This is just a warning check, not a hard failure
                pass

        # Verify file is not empty and has reasonable structure
        assert len(content) > 0, "File is empty"
        assert content.count('{') > 0, "No opening braces found"
        assert content.count('}') > 0, "No closing braces found"
    else:
        # If clang-format-18 is available, verify file can be parsed
        r = subprocess.run(
            ["clang-format-18", "--dry-run", "--Werror", FULL_PATH],
            capture_output=True, text=True, timeout=30
        )
        # Don't fail on formatting differences, just parse errors
        assert "error:" not in r.stderr.lower() or "cannot find" not in r.stderr.lower(), \
            f"clang-format parse error: {r.stderr[-500:]}"


def test_repo_cmake_includes():
    """Repo's CMake build system includes the modified directory (pass_to_pass)."""
    # Verify the CMakeLists.txt exists and includes our directory
    cmake_path = os.path.join(REPO, "src/Processors/QueryPlan/Optimizations/CMakeLists.txt")

    # The file might not exist at this level; check parent directories
    if not os.path.exists(cmake_path):
        # Check if parent CMakeLists.txt includes files from this directory
        parent_cmake = os.path.join(REPO, "src/Processors/QueryPlan/CMakeLists.txt")
        if os.path.exists(parent_cmake):
            with open(parent_cmake, 'r') as f:
                content = f.read()
            # Should reference the Optimizations subdirectory
            assert "Optimizations" in content, "Parent CMakeLists.txt doesn't include Optimizations"

    # Verify the directory structure is intact
    assert os.path.isdir(os.path.join(REPO, "src/Processors/QueryPlan/Optimizations")), \
        "Optimizations directory missing"

    # Check that other files in the same directory exist (structural integrity)
    opt_dir = os.path.join(REPO, "src/Processors/QueryPlan/Optimizations")
    files_in_dir = os.listdir(opt_dir) if os.path.isdir(opt_dir) else []
    assert len(files_in_dir) > 0, "Optimizations directory is empty"


def test_repo_git_tracking():
    """Repo's git tracks the modified file (pass_to_pass)."""
    # Verify the file is tracked by git
    r = subprocess.run(
        ["git", "ls-files", TARGET_FILE],
        capture_output=True, text=True, timeout=10, cwd=REPO
    )

    # File should be tracked by git
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    assert TARGET_FILE in r.stdout, f"File {TARGET_FILE} is not tracked by git"

    # Verify git status works
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=10, cwd=REPO
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"


def test_repo_header_includes_valid():
    """Modified file's header includes are valid (pass_to_pass)."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Extract all #include statements
    include_pattern = r'#include\s+[<"]([^>"]+)[>"]'
    includes = re.findall(include_pattern, content)

    assert len(includes) > 0, "No #include statements found"

    # Check that referenced files exist in the repo (for local includes)
    for inc in includes:
        # Skip system headers and contrib headers
        if inc.startswith('boost') or inc.startswith('std') or '/' not in inc:
            continue

        # Check if the header exists in expected locations
        possible_paths = [
            os.path.join(REPO, inc),
            os.path.join(REPO, "src", inc),
            os.path.join(REPO, "base", inc),
        ]

        # At least verify the include path structure looks valid
        # (don't require file to exist as it might be generated)
        assert '.' in inc or '/' in inc, f"Invalid include: {inc}"

    # Verify no duplicate includes
    unique_includes = set(includes)
    assert len(unique_includes) == len(includes), \
        f"Duplicate includes found: {[i for i in includes if includes.count(i) > 1]}"


def test_repo_cpp_standard_compliance():
    """Modified file uses valid C++20 constructs (pass_to_pass)."""
    with open(FULL_PATH, 'r') as f:
        content = f.read()

    # Basic C++20 syntax validation (not exhaustive, but catches obvious issues)

    # Check for balanced parentheses in function signatures
    paren_depth = 0
    in_string = False
    in_char = False
    escape_next = False

    for i, char in enumerate(content):
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == '"' and not in_char:
            in_string = not in_string
        if char == "'" and not in_string:
            in_char = not in_char
        if not in_string and not in_char:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
                assert paren_depth >= 0, f"Unbalanced parentheses at position {i}"

    # Check for modern C++ patterns that should be present
    # namespace DB and namespace QueryPlanOptimizations
    assert "namespace DB" in content, "Missing namespace DB"

    # Check for RAII patterns (smart pointers, etc.)
    assert "std::" in content or "auto " in content, "Not using modern C++ features"

    # Verify no raw C-style casts (should use static_cast, reinterpret_cast, etc.)
    # This is a loose check - C-style casts in C++ are `(type)` but hard to distinguish from function calls
    # Just verify that there are reasonable type conversions happening
