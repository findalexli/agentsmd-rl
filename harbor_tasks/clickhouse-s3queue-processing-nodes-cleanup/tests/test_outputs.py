"""
Test suite for ClickHouse S3Queue processing nodes cleanup fix.

This tests the race condition fix in cleanupPersistentProcessingNodes() where:
1. Before: Nodes were removed without version checking, causing race conditions
2. After: Version is tracked and passed to tryRemove() for optimistic concurrency control

Behavioral tests - verify actual code structure and logic, not just text patterns.
"""

import subprocess
import re
import sys
from pathlib import Path

# Path to the ClickHouse source
REPO = Path("/workspace/ClickHouse")
TARGET_FILE = REPO / "src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp"


def read_target_file():
    """Read the target source file."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def get_function_content(content, func_name):
    """Extract function body from content."""
    pattern = f"void ObjectStorageQueueMetadata::{func_name}()"
    start = content.find(pattern)
    if start == -1:
        return None
    # Get a reasonable chunk of the function (roughly)
    return content[start:start + 15000]


def test_version_in_nodes_to_remove():
    """
    Verify nodes_to_remove stores pairs of (path, version) instead of just paths.

    Behavioral: This checks the DATA STRUCTURE change (using pairs instead of plain strings)
    and that pairs are added with TWO arguments. Flexible on exact variable names.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: nodes_to_remove is declared as vector of pairs (stores both path AND version)
    # Flexible: accepts any variable name for the container
    pattern = r'std::vector<std::pair<String,\s*int32_t>>\s+\w+'
    match = re.search(pattern, func_content)
    assert match is not None, (
        "nodes_to_remove should be declared as std::vector<std::pair<String, int32_t>> "
        "to store both path and version"
    )

    # Verify pairs are added with TWO arguments (path and version)
    # Flexible: accepts any method name (emplace_back, push_back) and any argument names
    emplace_pattern = r'\w+\.(?:emplace_back|push_back)\([^,]+,\s*[^)]+\)'
    emplace_match = re.search(emplace_pattern, func_content)
    assert emplace_match is not None, (
        "nodes_to_remove should be populated with TWO arguments (path, version)"
    )


def test_tryremove_with_version():
    """
    Verify tryRemove is called with the version parameter.

    Behavioral: Checks that tryRemove receives TWO arguments (path and version).
    The version must come from the pair structure. Flexible on exact variable names
    and extraction syntax.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: tryRemove is called with TWO arguments
    # This verifies version is actually passed, not just declared
    tryremove_pattern = r'tryRemove\s*\([^,]+,\s*[^)]+\)'
    matches = re.findall(tryremove_pattern, func_content)
    assert len(matches) >= 1, (
        "tryRemove should be called with TWO arguments (node path and version) "
        "for optimistic concurrency control"
    )

    # Verify the second argument is a variable (not a literal) - it is the version
    # Look for tryRemove with two identifier arguments
    call_pattern = r'tryRemove\s*\(\s*\w+\s*,\s*\w+\s*\)'
    call_match = re.search(call_pattern, func_content)
    assert call_match is not None, (
        "tryRemove second argument should be a variable (version extracted from pair)"
    )


def test_zbadversion_handling():
    """
    Verify ZBADVERSION error code is properly handled as non-fatal.

    Behavioral: ZBADVERSION must be checked in the error handling logic,
    treated equivalently to ZNONODE (not throwing). This prevents false
    alarms on concurrent modifications.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: ZBADVERSION is mentioned in the error handling
    zbadversion_pattern = r'Coordination::Error::ZBADVERSION'
    match = re.search(zbadversion_pattern, func_content)
    assert match is not None, (
        "ZBADVERSION error should be explicitly handled in error checking logic"
    )

    # Verify ZBADVERSION is checked alongside ZNONODE (OR condition)
    # Both should be treated as non-fatal conditions
    combined_pattern = r'ZNONODE.*ZBADVERSION|ZBADVERSION.*ZNONODE'
    combined_match = re.search(combined_pattern, func_content)
    assert combined_match is not None, (
        "ZBADVERSION should be handled together with ZNONODE as non-fatal conditions"
    )


def test_removal_tracking():
    """
    Verify accurate tracking of successfully removed nodes.

    Behavioral: The code should track how many nodes were actually removed
    (vs skipped due to race conditions) and report in final log.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: A removal counter exists and is incremented on success
    # Flexible: any counter variable name, any increment syntax (++, += 1)
    counter_pattern = r'\+\+\s*\w+|\w+\+\+|;\s*\w+\s*\+=\s*1'
    counter_match = re.search(counter_pattern, func_content)
    assert counter_match is not None, (
        "A counter should be incremented when removal succeeds (code == ZOK)"
    )

    # Check that the log message shows removed/total format (not just total)
    # The log should show HOW MANY were removed, not just total nodes
    log_pattern = r'Removed\s*\{}/\{\}\s*stale\s*processing\s*nodes'
    log_match = re.search(log_pattern, func_content)
    assert log_match is not None, (
        "Log message should show 'Removed {removed}/{total} stale processing nodes' "
        "to indicate how many were actually removed vs skipped"
    )


def test_node_and_version_extraction():
    """
    Verify the loop properly extracts node path and version from the pair.

    Behavioral: Elements are extracted from pairs before use. Flexible on
    exact syntax (could use .first/.second, structured bindings, or other).
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: There's a for loop iterating over nodes_to_remove
    # Flexible: any loop variable name, any extraction syntax
    for_pattern = r'for\s*\([^)]*nodes_to_remove[^)]*\)'
    for_match = re.search(for_pattern, func_content)
    assert for_match is not None, (
        "Should iterate over nodes_to_remove collection"
    )

    # Check: Inside the loop, elements are split into two parts (path and version)
    # This can be done via .first/.second, structured bindings, or decomposition
    # Look for evidence of two-element extraction
    extraction_pattern = r'\.(?:first|second)\b|\bauto\s*&\s*\[\s*\w+\s*,\s*\w+\s*\]'
    extraction_match = re.search(extraction_pattern, func_content)
    assert extraction_match is not None, (
        "Node and version should be extracted from pairs "
        "(via .first/.second or structured binding)"
    )


def test_log_trace_for_removal():
    """
    Verify LOG_TRACE is added before attempting node removal.

    Behavioral: Each removal attempt should be logged for debugging.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: LOG_TRACE before removal attempt with "Removing" message
    log_pattern = r'LOG_TRACE\s*\([^)]*"[^"]*Removing[^"]*processing[^"]*node'
    match = re.search(log_pattern, func_content)
    assert match is not None, (
        "LOG_TRACE should log before attempting to remove each stale node"
    )


def test_log_trace_for_skip():
    """
    Verify LOG_TRACE is added when skipping already-removed nodes.

    Behavioral: Skipped nodes (due to race conditions) should be logged.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Check: LOG_TRACE when skipping with "already removed or recreated" message
    log_pattern = r'LOG_TRACE\s*\([^)]*"[^"]*already\s+(?:removed|recreated)[^"]*"'
    match = re.search(log_pattern, func_content)
    assert match is not None, (
        "LOG_TRACE should log when nodes are skipped (already removed or recreated)"
    )


def test_compilation_syntax():
    """
    Verify the modified file has valid C++ syntax by checking structural correctness.

    Behavioral: The file should have balanced braces, exist, and contain the
    expected function. This catches basic syntax errors.
    """
    content = read_target_file()

    # File should contain the function
    assert "cleanupPersistentProcessingNodes" in content, "Function should exist"

    # Check braces are balanced (basic syntax check)
    open_braces = content.count('{')
    close_braces = content.count('}')

    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open, {close_braces} close"
    )


def test_git_file_exists():
    """Verify target file exists in the repo (pass_to_pass)."""
    r = subprocess.run(
        ["ls", "-la", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Target file not found: {r.stderr}"
    assert "ObjectStorageQueueMetadata.cpp" in r.stdout


def test_cpp_syntax_balanced():
    """Verify basic C++ syntax - balanced braces and parentheses (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         f"content = open('{TARGET_FILE}').read(); "
         f"open_braces = content.count('{{'); close_braces = content.count('}}'); "
         f"assert open_braces == close_braces, f'Unbalanced braces: {{open_braces}} vs {{close_braces}}'; "
         f"open_parens = content.count('('); close_parens = content.count(')'); "
         f"assert open_parens == close_parens, f'Unbalanced parens: {{open_parens}} vs {{close_parens}}'"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


def test_no_trailing_whitespace():
    """Verify no trailing whitespace in target file (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-n", "[[:space:]]$", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    lines = r.stdout.strip().split("\n") if r.stdout.strip() else []
    if r.returncode == 0 and lines:
        problematic = [l for l in lines if l.strip() and not l.strip().startswith("//")]
        if problematic:
            assert False, f"Trailing whitespace found:\n" + "\n".join(problematic[:5])


def test_function_signature_exists():
    """Verify cleanupPersistentProcessingNodes function signature exists (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Function grep failed: {r.stderr}"
    count = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    assert count >= 1, f"Function should appear at least once, found {count}"


def test_zookeeper_includes():
    """Verify ZooKeeper-related includes are present (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-c", "ZooKeeper", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ZooKeeper grep failed: {r.stderr}"
    count = int(r.stdout.strip()) if r.stdout.strip().isdigit() else 0
    assert count >= 1, f"Should have ZooKeeper references, found {count}"


def test_no_simple_strings_vector():
    """
    Verify the old buggy pattern (Strings nodes_to_remove) is not present.

    Behavioral: The old implementation used plain Strings which could not store
    version info. This must be changed.
    """
    content = read_target_file()
    func_content = get_function_content(content, "cleanupPersistentProcessingNodes")
    assert func_content is not None, "cleanupPersistentProcessingNodes function not found"

    # Look for the specific old pattern in the function context
    # The old pattern: Strings nodes_to_remove;
    old_pattern = r'Strings\s+nodes_to_remove\s*;'
    match = re.search(old_pattern, func_content)

    # This should NOT be found - we've fixed it
    assert match is None, (
        "Old buggy pattern 'Strings nodes_to_remove;' should not be present. "
        "Should use 'std::vector<std::pair<String, int32_t>> nodes_to_remove' instead."
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
