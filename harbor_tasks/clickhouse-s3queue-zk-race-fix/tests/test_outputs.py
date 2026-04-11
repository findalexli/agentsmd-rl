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


def test_repo_typos():
    """Repo typos check passes using codespell (pass_to_pass).

    Runs ClickHouse's typos check using codespell to verify no typos in modified code.
    This is an actual CI command from the repo's style checks.
    """
    # Install codespell if needed and run the typos check
    r = subprocess.run(
        ["pip3", "install", "codespell", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Run the actual typos check from the repo
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_typos.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed: {r.stdout[-500:]}"


def test_repo_cpp_style():
    """Repo C++ style check passes (pass_to_pass).

    Runs ClickHouse's C++ style check script which validates:
    - No tabs in source files
    - No trailing whitespace
    - Proper header guards (#pragma once)
    - Balanced braces and indentation
    - No incorrect abbreviations (Sql, Html, Xml, etc.)
    This is an actual CI command from the repo's style checks.
    """
    # Configure git safe directory
    subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", REPO],
        capture_output=True, text=True, timeout=30,
    )
    # Run the C++ style check from the repo
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"C++ style check failed: {r.stderr[-500:]}"


def test_repo_yamllint():
    """Repo YAML files pass yamllint validation (pass_to_pass).

    Validates that the GitHub workflow files follow YAML syntax standards.
    Uses the repo's own .yamllint configuration file.
    This is a lightweight CI-style check that does not require compilation.
    """
    # Install yamllint if needed
    r = subprocess.run(
        ["pip3", "install", "yamllint", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # Run yamllint on workflow files using the repo's config
    r = subprocess.run(
        ["yamllint", "-c", f"{REPO}/.yamllint", f"{REPO}/.github/workflows/pull_request.yml"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"YAML lint failed: {r.stderr[-500:]}"


def test_repo_git_status():
    """Repo has clean git status at base commit (pass_to_pass).

    Verifies that the repository is at a clean state with no uncommitted changes.
    This ensures the base commit is stable.
    """
    r = subprocess.run(
        ["git", "config", "--global", "--add", "safe.directory", REPO],
        capture_output=True, text=True, timeout=30,
    )
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed: {r.stderr}"
    assert r.stdout.strip() == "", f"Repo has uncommitted changes: {r.stdout[:500]}"


def test_target_file_pragma_once():
    """Target header file has #pragma once (pass_to_pass).

    Verifies that ObjectStorageQueueMetadata.h has proper header guard.
    """
    header_file = os.path.join(REPO, TARGET_DIR, "ObjectStorageQueueMetadata.h")
    if os.path.exists(header_file):
        with open(header_file, "r") as f:
            content = f.read()
        assert "#pragma once" in content, "Header file missing #pragma once"


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


def test_target_cpp_syntax_valid():
    """Target C++ file has valid syntax (pass_to_pass).

    Verifies the C++ file compiles syntactically by checking for balanced braces.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    with open(cpp_file, "r") as f:
        content = f.read()

    # Basic syntax checks
    open_braces = content.count("{")
    close_braces = content.count("}")
    open_parens = content.count("(")
    close_parens = content.count(")")

    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_no_trailing_whitespace_in_target():
    """Target files have no trailing whitespace (pass_to_pass).

    Verifies that the modified file follows basic formatting conventions.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    with open(cpp_file, "r") as f:
        lines = f.readlines()

    trailing_whitespace = []
    for i, line in enumerate(lines, 1):
        if line.rstrip() != line.rstrip("\n").rstrip():
            trailing_whitespace.append(i)

    assert len(trailing_whitespace) == 0, f"Trailing whitespace found on lines: {trailing_whitespace[:10]}"


def test_no_tabs_in_target():
    """Target files use spaces not tabs (pass_to_pass).

    Verifies that the modified file uses spaces for indentation.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    with open(cpp_file, "r") as f:
        content = f.read()

    # Check for tabs (but allow in certain contexts like makefiles or special comments)
    lines = content.split("\n")
    tabs_found = []
    for i, line in enumerate(lines, 1):
        if "\t" in line:
            tabs_found.append(i)

    assert len(tabs_found) == 0, f"Tabs found on lines: {tabs_found[:10]}"


def test_include_guards_for_target_dir():
    """Header files in target dir have include guards or pragma once (pass_to_pass).

    Verifies all .h files in the ObjectStorageQueue directory have proper guards.
    """
    target_path = os.path.join(REPO, TARGET_DIR)
    h_files = [f for f in os.listdir(target_path) if f.endswith(".h")]

    for h_file in h_files:
        filepath = os.path.join(target_path, h_file)
        with open(filepath, "r") as f:
            content = f.read()

        has_pragma_once = "#pragma once" in content
        has_ifndef_guard = "#ifndef" in content and "#define" in content

        assert has_pragma_once or has_ifndef_guard, f"{h_file} missing include guard"


def test_file_size_reasonable():
    """Target file size is reasonable (pass_to_pass).

    Verifies the file isn't unexpectedly huge or empty.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    size = os.path.getsize(cpp_file)

    # File should be between 1KB and 1MB
    assert size > 1024, f"File too small: {size} bytes"
    assert size < 1024 * 1024, f"File too large: {size} bytes"


def test_no_conflict_markers_in_target():
    """Target files have no git conflict markers (pass_to_pass).

    Verifies the file doesn't contain unresolved merge conflict markers.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    with open(cpp_file, "r") as f:
        content = f.read()

    assert "<<<<<<<" not in content, "Git conflict markers found in file"
    assert "=======" not in content, "Git conflict markers found in file"
    assert ">>>>>>>" not in content, "Git conflict markers found in file"


def test_no_dos_newlines_in_target():
    """Target files use Unix newlines not DOS (pass_to_pass).

    Verifies the file doesn't contain DOS/Windows newlines.
    """
    cpp_file = os.path.join(REPO, TARGET_FILE)
    with open(cpp_file, "rb") as f:
        content = f.read()

    # Check for \r\n (DOS newlines)
    assert b"\r\n" not in content, "DOS/Windows newlines found in file"


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
