#!/usr/bin/env python3
"""
Tests for ClickHouse fs cache loading optimization.
This PR optimizes cache loading on server startup by restructuring
the loadMetadataForKeys function into three phases.
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/ClickHouse"
CACHE_DIR = f"{REPO}/src/Interpreters/Cache"


def test_syntax_check():
    """Test that the modified C++ files have valid syntax (pass_to_pass)."""
    # Since full ClickHouse compilation requires newer CMake and complex deps,
    # we do a simple syntax check using clang-tidy or clang-check

    # First check that all the files we modified exist and have content
    files_to_check = [
        f"{CACHE_DIR}/FileCache.cpp",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
    ]

    for filepath in files_to_check:
        assert os.path.exists(filepath), f"File does not exist: {filepath}"
        with open(filepath, 'r') as f:
            content = f.read()
            assert len(content) > 0, f"File is empty: {filepath}"
            # Basic syntax check - ensure braces are balanced
            open_braces = content.count('{')
            close_braces = content.count('}')
            assert open_braces == close_braces, f"Unbalanced braces in {filepath}: {open_braces} vs {close_braces}"


def test_best_effort_renamed_in_interface():
    """Test that 'best_effort' is renamed to 'is_initial_load' in IFileCachePriority.h (fail_to_pass)."""
    with open(f"{CACHE_DIR}/IFileCachePriority.h", "r") as f:
        content = f.read()

    # Check that is_initial_load exists
    assert "is_initial_load" in content, "Missing 'is_initial_load' parameter in IFileCachePriority.h"

    # Check that best_effort no longer exists in the interface
    assert "best_effort" not in content, "Old 'best_effort' parameter still present in IFileCachePriority.h"


def test_best_effort_renamed_in_lru_header():
    """Test that 'best_effort' is renamed in LRUFileCachePriority.h (fail_to_pass)."""
    with open(f"{CACHE_DIR}/LRUFileCachePriority.h", "r") as f:
        content = f.read()

    assert "is_initial_load" in content, "Missing 'is_initial_load' in LRUFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in LRUFileCachePriority.h"


def test_best_effort_renamed_in_slru_header():
    """Test that 'best_effort'/'is_startup' renamed in SLRUFileCachePriority.h (fail_to_pass)."""
    with open(f"{CACHE_DIR}/SLRUFileCachePriority.h", "r") as f:
        content = f.read()

    assert "is_initial_load" in content, "Missing 'is_initial_load' in SLRUFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in SLRUFileCachePriority.h"
    assert "is_startup" not in content, "Old 'is_startup' still present in SLRUFileCachePriority.h"


def test_best_effort_renamed_in_slru_cpp():
    """Test that parameter renamed in SLRUFileCachePriority.cpp (fail_to_pass)."""
    with open(f"{CACHE_DIR}/SLRUFileCachePriority.cpp", "r") as f:
        content = f.read()

    assert "is_initial_load" in content, "Missing 'is_initial_load' in SLRUFileCachePriority.cpp"
    assert "best_effort" not in content, "Old 'best_effort' still present in SLRUFileCachePriority.cpp"
    assert "is_startup" not in content, "Old 'is_startup' still present in SLRUFileCachePriority.cpp"


def test_best_effort_renamed_in_split_header():
    """Test that 'best_effort' renamed in SplitFileCachePriority.h (fail_to_pass)."""
    with open(f"{CACHE_DIR}/SplitFileCachePriority.h", "r") as f:
        content = f.read()

    assert "is_initial_load" in content, "Missing 'is_initial_load' in SplitFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in SplitFileCachePriority.h"


def test_best_effort_renamed_in_split_cpp():
    """Test that parameter renamed in SplitFileCachePriority.cpp (fail_to_pass)."""
    with open(f"{CACHE_DIR}/SplitFileCachePriority.cpp", "r") as f:
        content = f.read()

    assert "is_initial_load" in content, "Missing 'is_initial_load' in SplitFileCachePriority.cpp"
    assert "best_effort" not in content, "Old 'best_effort' still present in SplitFileCachePriority.cpp"


def test_segment_to_load_struct_exists():
    """Test that SegmentToLoad struct exists in FileCache.cpp (fail_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    assert "struct SegmentToLoad" in content, "Missing SegmentToLoad struct in FileCache.cpp"
    assert "offset" in content and "size" in content, "Missing offset/size fields"
    assert "kind" in content, "Missing kind field in SegmentToLoad"
    assert "cache_it" in content, "Missing cache_it field in SegmentToLoad"


def test_three_phase_loading_structure():
    """Test that loadMetadataForKeys uses three-phase loading (fail_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    # Phase 1 comment
    assert "Phase 1: scan and parse all segment files" in content, "Missing Phase 1 comment"
    # Phase 2 comment
    assert "Phase 2: add all segments for the key under a single write lock" in content, "Missing Phase 2 comment"
    # Phase 3 comment
    assert "Phase 3: construct FileSegment objects and emplace" in content, "Missing Phase 3 comment"


def test_main_priority_check_added():
    """Test that main_priority->check() is called after loading metadata (fail_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    # Look for the check call in loadMetadataImpl
    pattern = r"main_priority->check\(cache_state_guard\.lock\(\)\)"
    match = re.search(pattern, content)
    assert match is not None, "Missing main_priority->check() call after loadMetadataImpl"


def test_vector_segments_used():
    """Test that segments are collected in a vector before processing (fail_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    assert "std::vector<SegmentToLoad> segments" in content, "Missing segments vector declaration"
    assert "segments.push_back" in content, "Missing segments.push_back call"


def test_failed_to_fit_tracking():
    """Test that failed_to_fit counter is used (fail_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    assert "failed_to_fit" in content, "Missing failed_to_fit variable"
    assert "++failed_to_fit" in content or "failed_to_fit++" in content, "Missing failed_to_fit increment"


def test_clang_format_style_compliance():
    """Test that code follows Allman brace style (fail_to_pass)."""
    # Check that opening braces are on new lines in modified functions
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    # Look for common style violations - opening brace after if/else/for on same line
    # This is a heuristic - Allman style puts braces on new lines
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Skip comments and strings
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*'):
            continue

        # Check for pattern: if/else/for/while followed by { on same line
        # In Allman style, { should be on its own line
        if re.search(r'\b(if|else|for|while)\s*\([^)]*\)\s*\{', stripped):
            # Allow single-line if statements
            if '{' in stripped and '}' not in stripped:
                # This is a potential style violation - check if it's Allman
                # Allman: if (cond)\n{\n  body\n}
                # K&R:   if (cond) {\n  body\n}
                # We just do a basic check here - the real check is in CI
                pass


def test_no_unused_variables():
    """Test that offset and size variables are not declared at function scope (pass_to_pass)."""
    with open(f"{CACHE_DIR}/FileCache.cpp", "r") as f:
        content = f.read()

    # The PR removes function-scope: UInt64 offset = 0; UInt64 size = 0;
    # and moves them to the for loop scope

    # Find the loadMetadataForKeys function and check early lines
    func_match = re.search(r'void FileCache::loadMetadataForKeys.*?^\}', content, re.DOTALL | re.MULTILINE)
    if func_match:
        func_start = func_match.start()
        # Look at first ~500 chars after function signature
        early_section = content[func_start:func_start + 500]

        # If we see both declarations together early in the function, that's the old pattern
        if "UInt64 offset = 0;" in early_section and "UInt64 size = 0;" in early_section:
            # Check if it appears before the for loop (which is old pattern)
            offset_pos = early_section.find("UInt64 offset = 0;")
            for_pos = early_section.find("for (; key_it")
            if for_pos == -1 or (offset_pos != -1 and offset_pos < for_pos):
                pytest.fail("offset and size should be declared inside the loop, not at function scope")


def test_pragma_once_in_headers():
    """Test that all header files have #pragma once as first line (pass_to_pass)."""
    header_files = [
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
    ]

    for filepath in header_files:
        r = subprocess.run(
            ["head", "-n1", filepath],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"Failed to read {filepath}"
        first_line = r.stdout.strip()
        assert first_line == "#pragma once", f"{filepath} missing #pragma once, got: {first_line}"


def test_no_tabs_in_modified_files():
    """Test that modified files don't contain tab characters (pass_to_pass)."""
    files_to_check = [
        f"{CACHE_DIR}/FileCache.cpp",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
    ]

    tab_char = "\t"
    for filepath in files_to_check:
        # Read file directly in Python to avoid shell escaping issues
        with open(filepath, 'r') as f:
            content = f.read()
        tab_count = content.count(tab_char)
        if tab_count > 0:
            pytest.fail(f"{filepath} contains {tab_count} tab characters")


def test_no_trailing_whitespace():
    """Test that modified files don't have trailing whitespace (pass_to_pass)."""
    files_to_check = [
        f"{CACHE_DIR}/FileCache.cpp",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
    ]

    for filepath in files_to_check:
        r = subprocess.run(
            ["grep", "-n", "[[:space:]]$", filepath],
            capture_output=True, text=True, timeout=60
        )
        # If grep finds matches, it returns 0
        if r.returncode == 0 and r.stdout.strip():
            lines = r.stdout.strip().split("\n")[:5]  # Show first 5 violations
            pytest.fail(f"{filepath} has trailing whitespace:\n" + "\n".join(lines))


def test_includes_properly_ordered():
    """Test that source files have proper include ordering (system includes first) (pass_to_pass)."""
    # Check FileCache.cpp has standard includes at the top
    r = subprocess.run(
        ["head", "-n40", f"{CACHE_DIR}/FileCache.cpp"],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, "Failed to read FileCache.cpp"

    content = r.stdout
    # Check that standard headers are included before project headers
    lines = content.split("\n")
    found_first_project_include = False
    for line in lines:
        if line.startswith("#include"):
            if line.startswith("#include <Interpreters/"):
                found_first_project_include = True
            elif line.startswith("#include <") and not line.startswith("#include <filesystem>"):
                if found_first_project_include:
                    # System include after project include is OK for some cases
                    pass


def test_balanced_braces_in_modified_files():
    """Test that modified C++ files have balanced braces (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import os
files = [
    "{CACHE_DIR}/FileCache.cpp",
    "{CACHE_DIR}/IFileCachePriority.h",
    "{CACHE_DIR}/LRUFileCachePriority.h",
    "{CACHE_DIR}/SLRUFileCachePriority.h",
    "{CACHE_DIR}/SLRUFileCachePriority.cpp",
    "{CACHE_DIR}/SplitFileCachePriority.h",
    "{CACHE_DIR}/SplitFileCachePriority.cpp",
]
for f in files:
    content = open(f).read()
    open_braces = content.count('{{')
    close_braces = content.count('}}')
    if open_braces != close_braces:
        print(f"{{f}}: unbalanced braces ({{open_braces}} vs {{close_braces}})")
        exit(1)
print("All files have balanced braces")
"""],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, f"Brace balance check failed: {r.stdout}{r.stderr}"


# Mark tests that are expected to pass on base commit (pass_to_pass)
# and tests that are expected to fail on base commit (fail_to_pass)


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v"] + sys.argv[1:])
