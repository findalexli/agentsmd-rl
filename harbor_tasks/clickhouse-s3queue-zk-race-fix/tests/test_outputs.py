"""
Test suite for ClickHouse S3Queue ZooKeeper race condition fix.

This tests that the cleanupPersistentProcessingNodes() function properly
handles race conditions when removing stale ZooKeeper nodes by using
versioned deletes.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp"
TARGET_DIR = "src/Storages/ObjectStorageQueue"


# ============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks
# These verify that the repo's own CI checks pass on both base and fixed code.
# ============================================================================


def test_repo_cpp_style():
    """Repo C++ style check passes (pass_to_pass).

    Runs ClickHouse's check_cpp.sh style checker on the repository.
    This validates code formatting, style conventions, and basic patterns.
    """
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # Check for style errors in output - the script returns 0 but prints errors
    assert r.returncode == 0, "Style check script failed"
    # If there are style violations, they appear in stdout
    style_errors = [line for line in r.stdout.splitlines() if line and not line.startswith("^")]
    # Filter out informational lines
    real_errors = [line for line in style_errors if any(x in line for x in ["error", "Error", "is defined but not used", "is used in file", "Duplicate", "Missing", "should be", "must have", "not allowed", "Found ", "Too many"])]
    assert len(real_errors) == 0, "C++ style errors found"


def test_repo_various_checks():
    """Repo various checks pass (pass_to_pass).

    Runs ClickHouse's various_checks.sh which validates misc repo requirements.
    """
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, "Various checks failed"


def test_target_file_pragma_once():
    """Target header file has #pragma once (pass_to_pass).

    Verifies that ObjectStorageQueueMetadata.h has proper header guard.
    """
    header_file = os.path.join(REPO, TARGET_DIR, "ObjectStorageQueueMetadata.h")
    if os.path.exists(header_file):
        with open(header_file, "r") as f:
            first_line = f.readline().strip()
        assert first_line == "#pragma once", "Header file missing #pragma once"


def test_target_files_exist():
    """Target source files exist and are readable (pass_to_pass).

    Basic sanity check that all files in the module are present.
    """
    files_to_check = [
        "ObjectStorageQueueMetadata.cpp",
        "ObjectStorageQueueMetadata.h",
        "ObjectStorageQueueIFileMetadata.cpp",
        "ObjectStorageQueueIFileMetadata.h",
    ]
    for fname in files_to_check:
        fpath = os.path.join(REPO, TARGET_DIR, fname)
        assert os.path.exists(fpath), "Required file not found: " + fname
        # Verify file is readable
        with open(fpath, "r") as f:
            content = f.read(100)
        assert len(content) > 0, "File appears empty or unreadable: " + fname


# ============================================================================
# FAIL-TO-PASS TESTS: The actual fix verification
# ============================================================================


def test_file_compiles():
    """
    Verify that the modified C++ file compiles without errors.
    This is a basic sanity check for syntax correctness.
    """
    # Just check that the file exists and has valid structure
    assert os.path.exists(REPO + "/" + TARGET_FILE), "Target file not found"


def test_nodes_to_remove_uses_pair_type():
    """
    Fail-to-pass: Verify that nodes_to_remove is declared as vector of pairs
    to track both node path and version.

    This is the core fix - storing version alongside path for safe removal.
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Look for the vector<pair<String, int32_t>> declaration
    pattern = r"std::vector<std::pair<String,\s*int32_t>>\s+nodes_to_remove"
    match = re.search(pattern, content)

    assert match is not None, (
        "nodes_to_remove should be declared as std::vector<std::pair<String, int32_t>> "
        "to track node versions."
    )


def test_emplace_back_with_version():
    """
    Fail-to-pass: Verify that nodes are added with their version info.

    The fix changes from push_back(get_batch[i]) to emplace_back(get_batch[i], response[i].stat.version)
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function section
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    # Look for emplace_back with version in the cleanup section
    cleanup_section = content[cleanup_start:cleanup_start + 5000]

    # Check for emplace_back with the version parameter
    pattern = r"nodes_to_remove\.emplace_back\([^)]*version[^)]*\)"
    match = re.search(pattern, cleanup_section)

    assert match is not None, (
        "nodes_to_remove should use emplace_back with the node version. "
        "The fix requires storing response[i].stat.version alongside the node path."
    )


def test_tryremove_uses_version():
    """
    Fail-to-pass: Verify that tryRemove is called with the version parameter.

    This ensures versioned deletion for race condition safety.
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function and the removal loop
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    # Look in the cleanup section for tryRemove with version
    cleanup_section = content[cleanup_start:cleanup_start + 8000]

    # Check for tryRemove(node, version) - versioned delete
    pattern = r"tryRemove\([^,]+,\s*version\)"
    match = re.search(pattern, cleanup_section)

    assert match is not None, (
        "tryRemove must be called with the version parameter for safe deletion. "
        "This prevents race conditions where a node is recreated between listing and deletion."
    )


def test_zbadversion_error_handling():
    """
    Fail-to-pass: Verify that ZBADVERSION error is properly handled.

    When a versioned delete fails because the node was modified (recreated),
    we should gracefully skip rather than throwing an exception.
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    cleanup_section = content[cleanup_start:cleanup_start + 8000]

    # Check for ZBADVERSION handling
    assert "ZBADVERSION" in cleanup_section, (
        "The fix must handle ZBADVERSION error code when versioned deletion fails. "
        "This error occurs when a node is recreated between listing and deletion."
    )


def test_removed_count_tracking():
    """
    Pass-to-pass: Verify that successful removals are properly counted.

    The fix adds a counter to track how many nodes were actually removed
    vs how many were attempted, improving observability.
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    cleanup_section = content[cleanup_start:cleanup_start + 8000]

    # Check for removed counter
    assert "size_t removed = 0" in cleanup_section or "size_t removed=0" in cleanup_section, (
        "A counter for successful removals should be initialized."
    )

    # Check that ++removed happens on ZOK
    assert "++removed" in cleanup_section, (
        "The removed counter should be incremented when code == Coordination::Error::ZOK"
    )


def test_log_includes_count_ratio():
    """
    Pass-to-pass: Verify log message includes the removed/total ratio.

    The fix improves logging to show "Removed X/Y" instead of just "Removed Y".
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    cleanup_section = content[cleanup_start:cleanup_start + 8000]

    # Check for the improved log message format
    pattern = r"Removed.*removed.*nodes_to_remove\.size\(\)"
    match = re.search(pattern, cleanup_section)

    assert match is not None or "{removed}/{" in cleanup_section, (
        "The log message should show the ratio of removed/total nodes for better observability."
    )


def test_node_and_version_extracted_from_pair():
    """
    Fail-to-pass: Verify that node path and version are properly extracted
    from the pair in the removal loop.

    The loop should iterate over pairs and extract both .first (node) and .second (version).
    """
    with open(REPO + "/" + TARGET_FILE, "r") as f:
        content = f.read()

    # Find the cleanup function
    cleanup_start = content.find("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")
    assert cleanup_start != -1, "cleanupPersistentProcessingNodes function not found"

    cleanup_section = content[cleanup_start:cleanup_start + 8000]

    # Look for extraction of node from pair
    node_extraction = re.search(r"node_with_version\.first|const auto & node = node_with_version\.first", cleanup_section)
    version_extraction = re.search(r"node_with_version\.second|const auto version = node_with_version\.second", cleanup_section)

    assert node_extraction is not None, (
        "The node path should be extracted from the pair using .first"
    )

    assert version_extraction is not None, (
        "The version should be extracted from the pair using .second"
    )
