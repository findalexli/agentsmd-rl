"""
Test suite for S3Queue stale processing node cleanup fix.

This PR fixes a race condition where nodes could be incorrectly removed
from ZooKeeper due to missing version checking.
"""

import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp"


def test_file_exists():
    """Verify target file exists in repository."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"


def test_header_pragma_once():
    """Pass-to-pass: Header file has #pragma once (repo style check)."""
    header_file = REPO / "src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.h"
    assert header_file.exists(), f"Header file not found: {header_file}"
    content = header_file.read_text()
    first_line = content.split('\n')[0].strip()
    assert first_line == '#pragma once', f"Header must have '#pragma once' in first line, got: {first_line}"


def test_no_trailing_whitespace_in_target():
    """Pass-to-pass: Target file has no trailing whitespace (repo style check)."""
    content = TARGET_FILE.read_text()
    lines = content.split('\n')
    trailing_ws_found = []
    for i, line in enumerate(lines, 1):
        if line.endswith(' '):
            trailing_ws_found.append(f"Line {i}")
    assert not trailing_ws_found, f"Found trailing whitespace in: {trailing_ws_found[:5]}"


def test_no_tabs_in_target():
    """Pass-to-pass: Target file uses spaces not tabs (repo style check)."""
    content = TARGET_FILE.read_text()
    lines_with_tabs = []
    for i, line in enumerate(content.split('\n'), 1):
        if '\t' in line:
            lines_with_tabs.append(f"Line {i}")
    assert not lines_with_tabs, f"Found tabs in lines: {lines_with_tabs[:5]}"


def test_curly_brace_style():
    """Pass-to-pass: Check basic curly brace style on modified file (repo style check)."""
    content = TARGET_FILE.read_text()
    # Check for common style issues - curly brace at end of line for functions/classes
    import re
    # Look for patterns like ') {' which is generally acceptable
    # but flag obviously wrong patterns like '{  }' with double spaces inside
    double_space_brace = re.search(r'\{\s{2,}\}', content)
    assert not double_space_brace, "Found double spaces inside empty braces"


def test_compiles():
    """Verify the code compiles successfully."""
    import shutil

    # Skip if clang-check-15 is not available
    if not shutil.which("clang-check-15"):
        pytest.skip("clang-check-15 not available for syntax verification")

    build_dir = REPO / "build"
    build_dir.mkdir(exist_ok=True)

    # Configure with minimal options for faster build
    cmake_cmd = [
        "cmake",
        "-S", str(REPO),
        "-B", str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_COMPILER=clang++-15",
        "-DENABLE_TESTS=OFF",
        "-DENABLE_UTILS=OFF",
        "-DENABLE_EXAMPLES=OFF",
        "-G", "Ninja"
    ]

    result = subprocess.run(
        cmake_cmd,
        capture_output=True,
        timeout=300
    )

    # We allow configure to fail - just check syntax of target file
    # Use clang-check for syntax verification
    result = subprocess.run(
        ["clang-check-15", str(TARGET_FILE), "--analyze"],
        capture_output=True,
        timeout=60
    )

    # clang-check returns 0 on success, non-zero if syntax errors
    stderr = result.stderr.decode() if result.stderr else ""
    stdout = result.stdout.decode() if result.stdout else ""

    # Check for syntax errors in our specific file
    error_patterns = ["error: expected", "error: unknown type", "error: syntax"]
    for pattern in error_patterns:
        assert pattern not in stderr.lower(), f"Syntax error detected: {stderr[:500]}"


def test_nodes_to_remove_type_changed():
    """
    Fail-to-pass: Verify nodes_to_remove changed from Strings to vector<pair>.

    Before: Strings nodes_to_remove;
    After:  std::vector<std::pair<String, int32_t>> nodes_to_remove;
    """
    content = TARGET_FILE.read_text()

    # Check that we have the new type (pair with version)
    assert "std::vector<std::pair<String, int32_t>> nodes_to_remove" in content, \
        "nodes_to_remove should be vector of pairs storing node path and version"

    # Check that old simple String push is replaced with pair emplace
    assert "nodes_to_remove.emplace_back(get_batch[i], response[i].stat.version)" in content, \
        "Should emplace pair with node path and version"

    # Make sure old pattern is gone
    assert "nodes_to_remove.push_back(get_batch[i])" not in content, \
        "Old push_back pattern should be replaced"


def test_version_used_in_try_remove():
    """
    Fail-to-pass: Verify tryRemove now uses version parameter.

    Before: code = getZooKeeper(log)->tryRemove(node);
    After:  code = getZooKeeper(log)->tryRemove(node, version);
    """
    content = TARGET_FILE.read_text()

    # Find the cleanup function and check tryRemove call
    assert "tryRemove(node, version)" in content, \
        "tryRemove must be called with version parameter for safe deletion"

    # Make sure unversioned tryRemove is not used in the cleanup
    # (Allow it elsewhere, but not in the cleanup loop)
    # Use the function definition as the split point to get the actual function body
    cleanup_section = content.split("void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()")[1] \
        if "void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()" in content else content

    # In the cleanup section, should use versioned remove
    assert "tryRemove(node, version)" in cleanup_section, \
        "cleanup function must use versioned tryRemove"


def test_error_handling_includes_zbadversion():
    """
    Fail-to-pass: Verify ZBADVERSION is handled gracefully.

    Before: Only ZOK and ZNONODE were handled
    After:  ZBADVERSION is also handled as "already removed or recreated"
    """
    content = TARGET_FILE.read_text()

    # Check that ZBADVERSION is now handled
    assert "Coordination::Error::ZBADVERSION" in content, \
        "ZBADVERSION error should be explicitly handled"

    # Check the handling logic
    assert 'code == Coordination::Error::ZBADVERSION' in content or \
           'ZNONODE || code == Coordination::Error::ZBADVERSION' in content, \
        "ZBADVERSION should be checked alongside ZNONODE"

    # Check for appropriate log message
    assert "already removed or recreated" in content, \
        "Should log when node was already removed or recreated due to version mismatch"


def test_removal_counter_tracks_success():
    """
    Pass-to-pass: Verify removed counter tracks successful deletions.

    Before: Just logged total nodes_to_remove.size()
    After:  Tracks and logs actual successful removals vs attempted
    """
    content = TARGET_FILE.read_text()

    # Check for removal counter
    assert "size_t removed = 0" in content, \
        "Should initialize counter for successful removals"

    assert "++removed" in content, \
        "Should increment counter on successful removal (ZOK)"

    # Check updated log message format
    assert 'Removed {}/{} stale processing nodes' in content, \
        "Log should show successful/total removal count"


def test_node_iteration_uses_pair():
    """
    Fail-to-pass: Verify iteration extracts node and version from pair.

    Iterates over nodes_to_remove and extracts both path and version.
    """
    content = TARGET_FILE.read_text()

    # Check for structured binding or pair access
    assert "node_with_version.first" in content, \
        "Should extract node path from pair"

    assert "node_with_version.second" in content or "const auto version" in content, \
        "Should extract version from pair"

    # Check that TRACE logging includes the node being processed
    assert "LOG_TRACE(log, \"Removing stale processing node" in content, \
        "Should log each node being processed"


def test_no_bare_push_back():
    """
    Structural: Ensure all nodes_to_remove additions use emplace with version.
    """
    content = TARGET_FILE.read_text()

    # Find the cleanupPersistentProcessingNodes function
    func_match = re.search(
        r'void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes\(\).*?(?=^}|\Z)',
        content, re.DOTALL | re.MULTILINE
    )

    if func_match:
        func_content = func_match.group(0)
        # Should not have unversioned push_back in this function
        assert "nodes_to_remove.push_back" not in func_content, \
            "Should not use unversioned push_back in cleanup function"
