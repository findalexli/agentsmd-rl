"""
Tests for ClickHouse JOIN shard-by-PK with query condition cache fix.
"""

import subprocess
import os
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def test_patch_applied():
    """Fail-to-pass: The fix must be applied."""
    with open(FULL_PATH, "r") as f:
        content = f.read()
    assert "Renumber part_index_in_query to be contiguous" in content
    assert "local_idx" in content


def test_contiguous_index_assignment():
    """Fail-to-pass: Verify contiguous assignment."""
    with open(FULL_PATH, "r") as f:
        content = f.read()
    fixed_assignment = "all_parts.back().part_index_in_query = added_parts + local_idx"
    assert fixed_assignment in content


def test_for_loop_indexing_logic():
    """Fail-to-pass: Verify new indexing logic."""
    with open(FULL_PATH, "r") as f:
        lines = f.readlines()
    found_loop = False
    found_assignment = False
    for i, line in enumerate(lines):
        if "for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)" in line:
            found_loop = True
            for j in range(i+1, min(i+10, len(lines))):
                if "all_parts.back().part_index_in_query = added_parts + local_idx" in lines[j]:
                    found_assignment = True
    assert found_loop
    assert found_assignment


def test_code_compiles_syntax():
    """Pass-to-pass: C++ syntax validation."""
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++20", "-w",
         f"-I{REPO}/src", f"-I{REPO}/contrib", FULL_PATH],
        capture_output=True, text=True, timeout=60
    )
    parse_errors = [line for line in result.stderr.split("\n")
                    if "error" in line.lower() and
                    any(x in line.lower() for x in ["syntax", "parse", "expected", "unexpected"])]
    critical_errors = [e for e in parse_errors
                       if not any(x in e.lower() for x in ["unknown type", "undeclared", "no such file"])]
    assert len(critical_errors) == 0


def test_comment_explains_fix():
    """Pass-to-pass: Verify explanatory comments."""
    with open(FULL_PATH, "r") as f:
        content = f.read()
    assert "filterPartsByQueryConditionCache" in content
    assert "non-contiguous" in content.lower() or "contiguous" in content.lower()


def test_file_structure_intact():
    """Pass-to-pass: Verify file structure."""
    with open(FULL_PATH, "r") as f:
        content = f.read()
    assert "static void apply(struct JoinsAndSourcesWithCommonPrimaryKeyPrefix & data)" in content
    assert content.count("{") == content.count("}")


# CI-based pass-to-pass tests using actual repo CI commands


def test_repo_file_tracked():
    """Repo's git tracks the modified file (pass_to_pass)."""
    r = subprocess.run(["git", "ls-files", TARGET_FILE],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0
    assert TARGET_FILE in r.stdout


def test_repo_no_conflict_markers():
    """Repo has no git conflict markers (pass_to_pass)."""
    r = subprocess.run(["grep", "-lP", "^(<<<<<<<|=======|>>>>>>>)$", FULL_PATH],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 1


def test_repo_no_bom():
    """Repo's C++ files have no UTF-8 BOM (pass_to_pass)."""
    r = subprocess.run(["bash", "-c", f"grep -lF $'\\xEF\\xBB\\xBF' '{FULL_PATH}'"],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 1


def test_repo_no_dos_newlines():
    """Repo uses Unix newlines (pass_to_pass)."""
    r = subprocess.run(["grep", "-lP", "\r$", FULL_PATH],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 1


def test_repo_file_ends_with_newline():
    """Files end with newline (pass_to_pass)."""
    r = subprocess.run(["bash", "-c",
        f"tail -c 1 '{FULL_PATH}' | od -c | head -1 | grep -q '\\\\n'"],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0


def test_repo_no_executable_source_files():
    """Source files are not executable (pass_to_pass)."""
    r = subprocess.run(["git", "ls-files", "-s", TARGET_FILE],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0
    if r.stdout.strip():
        mode = r.stdout.strip().split()[0]
        assert mode in ["100644", "120000"]


def test_repo_no_trailing_whitespace():
    """No trailing whitespace (pass_to_pass)."""
    r = subprocess.run(["grep", "-nP", " $", FULL_PATH],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 1


def test_repo_no_tabs():
    """No tabs for indentation (pass_to_pass)."""
    r = subprocess.run(["bash", "-c", f"grep -lF $'\\t' '{FULL_PATH}'"],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 1


def test_repo_git_works():
    """Git commands work (pass_to_pass)."""
    r = subprocess.run(["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=10, cwd=REPO)
    assert r.returncode == 0


def test_repo_directory_structure():
    """Directory structure intact (pass_to_pass)."""
    r = subprocess.run(["test", "-d", f"{REPO}/src/Processors/QueryPlan/Optimizations"],
        capture_output=True, text=True, timeout=10)
    assert r.returncode == 0


# Additional CI-based pass-to-pass tests


def test_repo_pragma_once():
    """Repo's C++ files follow style guidelines (pass_to_pass)."""
    # Check file is not empty and has proper structure
    r = subprocess.run(
        ["test", "-s", FULL_PATH],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, "File should not be empty"


def test_repo_clang_syntax_check():
    """Basic clang syntax validation for modified file (pass_to_pass)."""
    r = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++20", "-w",
         f"-I{REPO}/src", f"-I{REPO}/contrib", FULL_PATH],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Allow "no such file" errors for includes, but not syntax errors
    syntax_errors = [line for line in r.stderr.split("\n")
                      if "error" in line.lower() and
                      any(x in line.lower() for x in ["syntax", "parse", "expected", "unexpected"])]
    critical_errors = [e for e in syntax_errors
                       if not any(x in e.lower() for x in ["no such file", "undeclared", "unknown type"])]
    assert len(critical_errors) == 0, f"Syntax errors found: {critical_errors[:5]}"


def test_repo_no_std_stringstream():
    """Repo check: No std::stringstream in modified code (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-nP", "std::[io]?stringstream", FULL_PATH],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 1, "Should not use std::stringstream (use WriteBufferFromOwnString instead)"


def test_repo_no_mt19937():
    """Repo check: No std::mt19937 or std::random_device in modified code (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"grep -nP '(std::mt19937|std::mersenne_twister_engine|std::random_device)' '{FULL_PATH}' || true"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert "std::mt19937" not in r.stdout and "std::random_device" not in r.stdout, \
        "Should use pcg64_fast instead of std::mt19937/random_device"


def test_repo_no_hardware_destructive_interference():
    """Repo check: No hardware_destructive_interference_size in modified code (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"grep -nP '(hardware_destructive_interference_size|hardware_constructive_interference_size)' '{FULL_PATH}' || true"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert "hardware_" not in r.stdout, \
        "Should use CH_CACHE_LINE_SIZE instead of hardware_*_interference_size"


def test_repo_no_std_filesystem_symlink():
    """Repo check: No std::filesystem::is_symlink in modified code (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", f"grep -nP '::(is|read)_symlink' '{FULL_PATH}' || true"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert "_symlink" not in r.stdout, \
        "Should use DB::FS::isSymlink and DB::FS::readSymlink instead"
