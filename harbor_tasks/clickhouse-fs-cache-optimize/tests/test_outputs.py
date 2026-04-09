"""
Tests for ClickHouse filesystem cache loading optimization.

This task involves optimizing how the filesystem cache loads metadata on server startup
by restructuring the loading logic into 3 phases with reduced lock contention.
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = "/workspace/clickhouse"
CACHE_DIR = f"{REPO}/src/Interpreters/Cache"


def test_code_compiles():
    """
    Verify the code changes don't introduce obvious syntax errors.

    Note: Full compilation is not practical in this test environment
    (requires cmake 3.25+, significant disk space, and build time).
    Instead, we verify the code structure is correct by checking:
    1. Key files exist and are non-empty
    2. Expected code patterns are present
    3. No obvious syntax issues (braces balance, etc.)
    """
    import os

    # Check that all target files exist and have content
    target_files = [
        f"{CACHE_DIR}/FileCache.cpp",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
    ]

    for filepath in target_files:
        assert os.path.exists(filepath), f"Target file {filepath} should exist"
        assert os.path.getsize(filepath) > 100, f"Target file {filepath} should have content"

    # Check FileCache.cpp has balanced braces (basic syntax check)
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # Basic brace balance check
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"FileCache.cpp should have balanced braces ({open_braces} open, {close_braces} close)"

    # Check for no obvious syntax errors (like double semicolons)
    assert ';;' not in content.replace(';;;;', '').replace(';;;;;;', ''), \
        "FileCache.cpp should not have double semicolons"


def test_is_initial_load_parameter_used():
    """
    Fail-to-pass: Verify that 'is_initial_load' parameter name is used instead of 'best_effort'.

    The patch renames the 'best_effort' parameter to 'is_initial_load' across all
    cache priority implementations to make its purpose clearer.
    """
    files_to_check = [
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
    ]

    for filepath in files_to_check:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check that is_initial_load is used
        assert "is_initial_load" in content, \
            f"File {filepath} should use 'is_initial_load' parameter"

        # The old parameter name should not exist in function signatures
        # (but might appear in comments, so we check function signatures specifically)
        func_sig_pattern = r'bool\s+best_effort\s*=\s*false'
        matches = re.findall(func_sig_pattern, content)
        assert len(matches) == 0, \
            f"File {filepath} should not use 'best_effort' as parameter name in function signatures"


def test_segment_to_load_struct_exists():
    """
    Fail-to-pass: Verify that SegmentToLoad struct is defined in FileCache.cpp.

    The patch introduces a SegmentToLoad struct to hold segment metadata during
    the 3-phase loading process.
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # Check for the SegmentToLoad struct definition
    assert "struct SegmentToLoad" in content, \
        "FileCache.cpp should define SegmentToLoad struct"

    # Check for the expected fields
    assert "UInt64 offset;" in content or "offset;" in content, \
        "SegmentToLoad should have offset field"
    assert "UInt64 size;" in content or "size;" in content, \
        "SegmentToLoad should have size field"
    assert "FileSegmentKind kind;" in content or "kind;" in content, \
        "SegmentToLoad should have kind field"
    assert "fs::path path;" in content or "path;" in content, \
        "SegmentToLoad should have path field"
    assert "IteratorPtr cache_it;" in content or "cache_it;" in content, \
        "SegmentToLoad should have cache_it field"


def test_three_phase_loading_pattern():
    """
    Fail-to-pass: Verify the 3-phase loading pattern is implemented.

    The patch restructures loadMetadataForKeys to use 3 phases:
    1. Scan and parse all segment files (no lock)
    2. Add all segments under a single write lock
    3. Construct FileSegment objects (no lock)
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # Check for Phase 1 comment
    phase1_patterns = [
        "Phase 1: scan and parse all segment files",
        "Phase 1: scan and parse"
    ]
    assert any(p in content for p in phase1_patterns), \
        "Should have Phase 1 comment for scanning segment files"

    # Check for Phase 2 comment
    phase2_patterns = [
        "Phase 2: add all segments for the key under a single write lock",
        "Phase 2: add all segments"
    ]
    assert any(p in content for p in phase2_patterns), \
        "Should have Phase 2 comment for adding segments under lock"

    # Check for Phase 3 comment
    phase3_patterns = [
        "Phase 3: construct FileSegment objects",
        "Phase 3: construct FileSegment"
    ]
    assert any(p in content for p in phase3_patterns), \
        "Should have Phase 3 comment for constructing FileSegment objects"

    # Verify the segments vector is used for batching
    assert "std::vector<SegmentToLoad> segments;" in content, \
        "Should use vector of SegmentToLoad for batching"


def test_main_priority_check_called():
    """
    Fail-to-pass: Verify that main_priority->check() is called in loadMetadataImpl.

    The patch adds a call to main_priority->check() after loading metadata to ensure
    cache consistency.
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # Find the loadMetadataImpl function and check for the check() call
    assert "main_priority->check(cache_state_guard.lock())" in content, \
        "main_priority->check() should be called in loadMetadataImpl"


def test_failed_to_fit_batch_logging():
    """
    Fail-to-pass: Verify batch logging of failed-to-fit files.

    The patch changes from logging each file that doesn't fit to batch logging
    all failed files per key at the end.
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # Check for failed_to_fit counter
    assert "size_t failed_to_fit = 0;" in content or "failed_to_fit = 0" in content, \
        "Should have failed_to_fit counter for batch logging"

    # Check for the increment
    assert "++failed_to_fit;" in content or "failed_to_fit++" in content, \
        "Should increment failed_to_fit counter"

    # Check for batch log message
    batch_log_patterns = [
        "file(s) for key {} do not fit in cache anymore",
        "file(s) for key",
        "failed_to_fit, key"
    ]
    assert any(p in content for p in batch_log_patterns), \
        "Should log failed files in batch rather than individually"


def test_lock_scope_optimization():
    """
    Pass-to-pass: Verify lock scope is optimized in loadMetadataForKeys.

    The patch reduces lock contention by acquiring the lock only once for
    adding all segments of a key, rather than per-segment.
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        content = f.read()

    # The lock should be acquired in a scoped block for Phase 2
    # Look for the pattern of acquiring writeLock and state_lock together
    lock_patterns = [
        "auto lock = cache_guard.writeLock();",
        "auto state_lock = cache_state_guard.lock();",
    ]

    for pattern in lock_patterns:
        assert pattern in content, \
            f"Should use '{pattern}' for lock acquisition in Phase 2"

    # The old pattern of acquiring locks inside the offset loop should be removed
    # (This is more of a structural check - we verify the new structure exists above)


def test_slru_is_initial_load_logic():
    """
    Fail-to-pass: Verify SLRU cache priority uses is_initial_load correctly.

    The SLRU implementation has special logic for is_initial_load that allows
    segments to fit in either queue during initial load.
    """
    with open(f"{CACHE_DIR}/SLRUFileCachePriority.cpp", 'r') as f:
        content = f.read()

    # Check that canFit uses is_initial_load parameter
    assert "bool is_initial_load) const" in content, \
        "SLRUFileCachePriority::canFit should use is_initial_load parameter"

    # Check for the is_initial_load check that allows fitting in either queue
    assert "if (is_initial_load)" in content, \
        "SLRUFileCachePriority::canFit should check is_initial_load"

    # Check that it allows fitting in either queue during initial load
    assert "probationary_queue.canFit" in content and "protected_queue.canFit" in content, \
        "SLRU canFit should check both queues when is_initial_load is true"


def test_no_per_segment_lock_in_phase3():
    """
    Pass-to-pass: Verify Phase 3 does not hold locks while constructing FileSegments.

    The patch specifically moves FileSegment construction outside of locked sections.
    """
    with open(f"{CACHE_DIR}/FileCache.cpp", 'r') as f:
        lines = f.readlines()

    # Find the Phase 3 section
    in_phase3 = False
    phase3_brace_depth = 0
    found_file_segment_construction = False

    for i, line in enumerate(lines):
        if "Phase 3: construct FileSegment" in line:
            in_phase3 = True
            phase3_brace_depth = 0

        if in_phase3:
            # Count braces to track scope
            phase3_brace_depth += line.count('{') - line.count('}')

            # Check for FileSegment construction
            if "std::make_shared<FileSegment>" in line:
                found_file_segment_construction = True
                # The construction should be outside any lock scope
                # We verify this by checking the line doesn't contain lock acquisition
                assert "writeLock" not in line and "lock()" not in line, \
                    "FileSegment construction should not hold locks"

            # End of Phase 3 section (rough heuristic)
            if phase3_brace_depth == 0 and '{' in line or i > len(lines) - 10:
                break

    assert found_file_segment_construction, \
        "Should construct FileSegment objects in Phase 3"


# =============================================================================
# Pass-to-pass tests - verify CI/CD checks pass on both base and fix
# =============================================================================

def test_repo_python_syntax():
    """Repo's Python files have valid syntax (pass_to_pass)."""
    import py_compile
    import os

    py_files = [
        f"{REPO}/ci/jobs/check_style.py",
        f"{REPO}/ci/jobs/build_clickhouse.py",
        f"{REPO}/ci/jobs/unit_tests_job.py",
    ]

    for filepath in py_files:
        if os.path.exists(filepath):
            py_compile.compile(filepath, doraise=True)


def test_repo_yaml_wellformedness():
    """Repo's YAML config files are well-formed (pass_to_pass)."""
    import yaml
    import os

    yaml_files = [
        f"{REPO}/tests/config/config.d/abort_on_logical_error.yaml",
        f"{REPO}/tests/config/config.d/handlers.yaml",
        f"{REPO}/tests/config/users.d/allow_introspection_functions.yaml",
    ]

    for filepath in yaml_files:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                yaml.safe_load(f)


def test_repo_xml_wellformedness():
    """Repo's XML config files are well-formed (pass_to_pass)."""
    import xml.etree.ElementTree as ET
    import os

    xml_files = [
        f"{REPO}/tests/config/client_config.xml",
        f"{REPO}/tests/config/config.d/clusters.xml",
        f"{REPO}/tests/config/config.d/backups.xml",
    ]

    for filepath in xml_files:
        if os.path.exists(filepath):
            ET.parse(filepath)


def test_cache_files_exist():
    """Cache-related source files exist and are non-empty (pass_to_pass)."""
    import os

    cache_files = [
        f"{CACHE_DIR}/FileCache.cpp",
        f"{CACHE_DIR}/FileCache.h",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.cpp",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.cpp",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
    ]

    for filepath in cache_files:
        assert os.path.exists(filepath), f"Cache file {filepath} should exist"
        assert os.path.getsize(filepath) > 0, f"Cache file {filepath} should not be empty"


def test_cache_headers_have_pragma_once():
    """Cache header files have #pragma once (pass_to_pass)."""
    header_files = [
        f"{CACHE_DIR}/FileCache.h",
        f"{CACHE_DIR}/IFileCachePriority.h",
        f"{CACHE_DIR}/LRUFileCachePriority.h",
        f"{CACHE_DIR}/SLRUFileCachePriority.h",
        f"{CACHE_DIR}/SplitFileCachePriority.h",
    ]

    for filepath in header_files:
        with open(filepath, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == '#pragma once', \
            f"Header {filepath} should have '#pragma once' as first line"


def test_repo_git_structure():
    """Repo has valid git structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
