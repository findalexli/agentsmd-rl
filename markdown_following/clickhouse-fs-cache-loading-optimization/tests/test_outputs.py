#!/usr/bin/env python3
"""
Tests for ClickHouse fs cache loading optimization (PR #101500).
"""

import subprocess
import re
import os
import pytest

REPO = "/workspace/ClickHouse"
CACHE_DIR = f"{REPO}/src/Interpreters/Cache"


def _read_file(relpath):
    """Read file content from the cache directory."""
    filepath = os.path.join(CACHE_DIR, relpath)
    with open(filepath, "r") as f:
        return f.read()


def _find_function_body(content, func_signature):
    """Extract the body of a function/method by finding its start and the next top-level function."""
    start = content.find(func_signature)
    if start == -1:
        return ""
    # Find the next function definition after this one
    rest = content[start + len(func_signature):]
    next_func = re.search(r'\n(?:void |bool |size_t |auto |IFileCachePriority::)', rest)
    end = start + len(func_signature) + (next_func.start() if next_func else len(rest))
    return content[start:end]


def test_syntax_check():
    """All modified files exist, have content, and balanced braces (pass_to_pass)."""
    files_to_check = [
        "FileCache.cpp",
        "IFileCachePriority.h",
        "LRUFileCachePriority.h",
        "SLRUFileCachePriority.h",
        "SLRUFileCachePriority.cpp",
        "SplitFileCachePriority.h",
        "SplitFileCachePriority.cpp",
    ]
    for filename in files_to_check:
        filepath = os.path.join(CACHE_DIR, filename)
        assert os.path.exists(filepath), f"File does not exist: {filepath}"
        with open(filepath, "r") as f:
            content = f.read()
            assert len(content) > 0, f"File is empty: {filepath}"
            if content.count("{") != content.count("}"):
                pytest.fail(f"Unbalanced braces in {filepath}: {content.count('{')} vs {content.count('}')}")


def test_best_effort_renamed_in_interface():
    """Parameter renamed from 'best_effort' to 'is_initial_load' in IFileCachePriority.h (fail_to_pass)."""
    content = _read_file("IFileCachePriority.h")
    assert "is_initial_load" in content, "Missing 'is_initial_load' parameter in IFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' parameter still present in IFileCachePriority.h"


def test_best_effort_renamed_in_lru_header():
    """Parameter renamed from 'best_effort' to 'is_initial_load' in LRUFileCachePriority.h (fail_to_pass)."""
    content = _read_file("LRUFileCachePriority.h")
    assert "is_initial_load" in content, "Missing 'is_initial_load' in LRUFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in LRUFileCachePriority.h"


def test_best_effort_renamed_in_slru_header():
    """Parameter renamed from 'best_effort'/'is_startup' to 'is_initial_load' in SLRUFileCachePriority.h (fail_to_pass)."""
    content = _read_file("SLRUFileCachePriority.h")
    assert "is_initial_load" in content, "Missing 'is_initial_load' in SLRUFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in SLRUFileCachePriority.h"
    assert "is_startup" not in content, "Old 'is_startup' still present in SLRUFileCachePriority.h"


def test_best_effort_renamed_in_slru_cpp():
    """Parameter renamed in SLRUFileCachePriority.cpp (fail_to_pass)."""
    content = _read_file("SLRUFileCachePriority.cpp")
    assert "is_initial_load" in content, "Missing 'is_initial_load' in SLRUFileCachePriority.cpp"
    assert "best_effort" not in content, "Old 'best_effort' still present in SLRUFileCachePriority.cpp"
    assert "is_startup" not in content, "Old 'is_startup' still present in SLRUFileCachePriority.cpp"


def test_best_effort_renamed_in_split_header():
    """Parameter renamed from 'best_effort' to 'is_initial_load' in SplitFileCachePriority.h (fail_to_pass)."""
    content = _read_file("SplitFileCachePriority.h")
    assert "is_initial_load" in content, "Missing 'is_initial_load' in SplitFileCachePriority.h"
    assert "best_effort" not in content, "Old 'best_effort' still present in SplitFileCachePriority.h"


def test_best_effort_renamed_in_split_cpp():
    """Parameter renamed in SplitFileCachePriority.cpp (fail_to_pass)."""
    content = _read_file("SplitFileCachePriority.cpp")
    assert "is_initial_load" in content, "Missing 'is_initial_load' in SplitFileCachePriority.cpp"
    assert "best_effort" not in content, "Old 'best_effort' still present in SplitFileCachePriority.cpp"


def test_segment_to_load_struct_exists():
    """SegmentToLoad struct created in FileCache.cpp for three-phase loading (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    func_body = _find_function_body(content, "void FileCache::loadMetadataForKeys")
    assert "struct SegmentToLoad" in func_body, "Missing SegmentToLoad struct in loadMetadataForKeys"
    assert "UInt64 offset" in func_body, "Missing offset field in SegmentToLoad"
    assert "UInt64 size" in func_body, "Missing size field in SegmentToLoad"
    assert "FileSegmentKind kind" in func_body, "Missing kind field in SegmentToLoad"
    assert "IFileCachePriority::IteratorPtr cache_it" in func_body, "Missing cache_it field in SegmentToLoad"


def test_three_phase_loading_structure():
    """loadMetadataForKeys uses three-phase loading (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    func_body = _find_function_body(content, "void FileCache::loadMetadataForKeys")
    assert "Phase 1: scan and parse all segment files" in func_body, "Missing Phase 1 comment"
    assert "Phase 2: add all segments for the key under a single write lock" in func_body, "Missing Phase 2 comment"
    assert "Phase 3: construct FileSegment objects and emplace" in func_body, "Missing Phase 3 comment"


def test_main_priority_check_added():
    """main_priority->check() called in loadMetadataImpl after loading metadata (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    func_body = _find_function_body(content, "void FileCache::loadMetadataImpl()")
    assert "main_priority->check(cache_state_guard.lock())" in func_body, \
        "Missing main_priority->check() call in loadMetadataImpl"
    # Verify it appears after the exception rethrow and before assertCacheCorrectness
    check_idx = func_body.find("main_priority->check(cache_state_guard.lock())")
    assert_idx = func_body.find("assertCacheCorrectness()")
    assert check_idx < assert_idx, \
        "main_priority->check() must appear before assertCacheCorrectness() in loadMetadataImpl"


def test_vector_segments_used():
    """segments vector used to collect files before processing (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    func_body = _find_function_body(content, "void FileCache::loadMetadataForKeys")
    assert "std::vector<SegmentToLoad> segments" in func_body, "Missing segments vector declaration"
    # Use word boundary to distinguish segments.push_back from e.g. file_segments.push_back
    assert re.search(r'\bsegments\.push_back\b', func_body), "Missing segments.push_back call"


def test_failed_to_fit_tracking():
    """failed_to_fit counter used for batched failure logging (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    func_body = _find_function_body(content, "void FileCache::loadMetadataForKeys")
    assert "failed_to_fit" in func_body, "Missing failed_to_fit variable"
    assert re.search(r'\+\+failed_to_fit|failed_to_fit\+\+', func_body), "Missing failed_to_fit increment"


def test_no_unused_variables():
    """offset and size declared inside loop scope, not at function scope (fail_to_pass)."""
    content = _read_file("FileCache.cpp")
    # Find the function and look at the first ~20 lines after the signature
    func_start = content.find("void FileCache::loadMetadataForKeys")
    assert func_start != -1, "loadMetadataForKeys function not found"
    # Get the signature through the opening brace
    after_sig = content[func_start:]
    brace_idx = after_sig.find("{")
    assert brace_idx != -1, "Function opening brace not found"
    # Look at first 600 chars of function body (before the key iteration loop)
    early_body = after_sig[brace_idx:brace_idx + 600]
    # Old code had UInt64 offset = 0; and UInt64 size = 0; before the for loop
    has_offset_decl = "UInt64 offset = 0;" in early_body
    has_size_decl = "UInt64 size = 0;" in early_body
    if has_offset_decl and has_size_decl:
        pytest.fail("offset and size should be declared inside the loop, not at function scope")


def test_clang_format_style_compliance():
    """Code is syntactically valid C++ (clang-format can parse all files without error) (pass_to_pass)."""
    files = [
        os.path.join(CACHE_DIR, f) for f in [
            "FileCache.cpp",
            "IFileCachePriority.h",
            "LRUFileCachePriority.h",
            "SLRUFileCachePriority.h",
            "SLRUFileCachePriority.cpp",
            "SplitFileCachePriority.h",
            "SplitFileCachePriority.cpp",
        ]
    ]
    style = "{BasedOnStyle: Google, BreakBeforeBraces: Allman, IndentWidth: 4, ColumnLimit: 140}"
    for filepath in files:
        r = subprocess.run(
            ["clang-format-14", f"--style={style}", filepath],
            capture_output=True, text=True, timeout=60,
        )
        # clang-format exits non-zero only on fatal parse errors, not style violations
        assert r.returncode == 0, f"clang-format failed to parse {os.path.basename(filepath)}: {r.stderr.strip()[:500]}"


def test_pragma_once_in_headers():
    """All header files have #pragma once as first line (pass_to_pass)."""
    header_files = [
        "IFileCachePriority.h",
        "LRUFileCachePriority.h",
        "SLRUFileCachePriority.h",
        "SplitFileCachePriority.h",
    ]
    for filename in header_files:
        filepath = os.path.join(CACHE_DIR, filename)
        r = subprocess.run(
            ["head", "-n1", filepath],
            capture_output=True, text=True, timeout=60
        )
        assert r.returncode == 0, f"Failed to read {filepath}"
        first_line = r.stdout.strip()
        assert first_line == "#pragma once", f"{filename} missing #pragma once, got: {first_line}"


def test_no_tabs_in_modified_files():
    """Modified files don't contain tab characters (pass_to_pass)."""
    files_to_check = [
        "FileCache.cpp",
        "IFileCachePriority.h",
        "LRUFileCachePriority.h",
        "SLRUFileCachePriority.h",
        "SLRUFileCachePriority.cpp",
        "SplitFileCachePriority.h",
        "SplitFileCachePriority.cpp",
    ]
    for filename in files_to_check:
        filepath = os.path.join(CACHE_DIR, filename)
        with open(filepath, "r") as f:
            content = f.read()
        tab_count = content.count("\t")
        if tab_count > 0:
            pytest.fail(f"{filepath} contains {tab_count} tab characters")


def test_no_trailing_whitespace():
    """Modified files don't have trailing whitespace (pass_to_pass)."""
    files_to_check = [
        "FileCache.cpp",
        "IFileCachePriority.h",
        "LRUFileCachePriority.h",
        "SLRUFileCachePriority.h",
        "SLRUFileCachePriority.cpp",
        "SplitFileCachePriority.h",
        "SplitFileCachePriority.cpp",
    ]
    for filename in files_to_check:
        filepath = os.path.join(CACHE_DIR, filename)
        r = subprocess.run(
            ["grep", "-n", "[[:space:]]$", filepath],
            capture_output=True, text=True, timeout=60
        )
        if r.returncode == 0 and r.stdout.strip():
            lines = r.stdout.strip().split("\n")[:5]
            pytest.fail(f"{filepath} has trailing whitespace:\n" + "\n".join(lines))


def test_includes_properly_ordered():
    """Source files follow ClickHouse include ordering convention (pass_to_pass)."""
    filepath = os.path.join(CACHE_DIR, "FileCache.cpp")
    r = subprocess.run(
        ["head", "-n5", filepath],
        capture_output=True, text=True, timeout=60
    )
    assert r.returncode == 0, "Failed to read FileCache.cpp"
    lines = r.stdout.strip().split("\n")
    # ClickHouse convention: first line after copyright is the corresponding header
    first_include = next((line.strip() for line in lines if line.strip().startswith("#include")), "")
    assert "FileCache.h" in first_include, \
        f"First include should be the corresponding header, got: {first_include}"


def test_balanced_braces_in_modified_files():
    """All modified C++ files have balanced braces (pass_to_pass)."""
    files = [
        "FileCache.cpp",
        "IFileCachePriority.h",
        "LRUFileCachePriority.h",
        "SLRUFileCachePriority.h",
        "SLRUFileCachePriority.cpp",
        "SplitFileCachePriority.h",
        "SplitFileCachePriority.cpp",
    ]
    for filename in files:
        filepath = os.path.join(CACHE_DIR, filename)
        with open(filepath, "r") as f:
            content = f.read()
        open_braces = content.count("{")
        close_braces = content.count("}")
        if open_braces != close_braces:
            pytest.fail(f"{filename}: unbalanced braces ({open_braces} vs {close_braces})")


if __name__ == "__main__":
    import sys
    pytest.main([__file__, "-v"] + sys.argv[1:])
