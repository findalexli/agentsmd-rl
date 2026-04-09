"""
Test outputs for Chroma SourceRecordSegmentV2Operator task.

These tests verify that:
1. The new SourceRecordSegmentV2Operator exists and is properly structured
2. The materialize_logs_for_rebuild function exists and handles Add operations
3. The operator properly partitions records based on max_partition_size
4. Error handling for non-Add operations works correctly
5. The SourceRecordSegmentOperator uses Operation::Add (not Upsert)

Pass-to-pass (P2P) tests verify that the repo's CI/CD checks pass on both
the base commit and after the gold fix. These include:
- cargo fmt (formatting check)
- cargo clippy (linting check)
- cargo check (compilation check)
"""

import subprocess
import sys
import os
import pytest

REPO = "/workspace/chroma"
RUST_DIR = f"{REPO}/rust"
RUST_WORKER = f"{REPO}/rust/worker"
RUST_SEGMENT = f"{REPO}/rust/segment"


def test_source_record_segment_v2_operator_exists():
    """F2P: Verify the SourceRecordSegmentV2Operator struct exists."""
    # Verify the file exists
    v2_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment_v2.rs"
    assert os.path.exists(v2_file), f"SourceRecordSegmentV2 file not found at {v2_file}"

    # Verify the struct definition exists
    with open(v2_file, 'r') as f:
        content = f.read()
        assert "pub struct SourceRecordSegmentV2Operator" in content, \
            "SourceRecordSegmentV2Operator struct not found"
        assert "pub fn new(max_partition_size: usize)" in content, \
            "Constructor with max_partition_size parameter not found"


def test_materialize_logs_for_rebuild_exists():
    """F2P: Verify materialize_logs_for_rebuild function exists."""
    types_file = f"{RUST_SEGMENT}/src/types.rs"

    with open(types_file, 'r') as f:
        content = f.read()

    # Check for the function definition
    assert "pub async fn materialize_logs_for_rebuild" in content, \
        "materialize_logs_for_rebuild function not found"

    # Check for the UnsupportedOperationForRebuild error
    assert "UnsupportedOperationForRebuild" in content, \
        "UnsupportedOperationForRebuild error variant not found"


def test_source_record_segment_v2_tests_exist():
    """F2P: Verify the unit tests for SourceRecordSegmentV2Operator exist and pass."""
    # First check the tests exist
    v2_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment_v2.rs"

    with open(v2_file, 'r') as f:
        content = f.read()

    # Verify test functions exist
    assert "async fn test_source_v2_basic" in content, \
        "test_source_v2_basic test not found"
    assert "async fn test_source_v2_empty" in content, \
        "test_source_v2_empty test not found"
    assert "async fn test_source_v2_preserves_offset_ids" in content, \
        "test_source_v2_preserves_offset_ids test not found"

    # Check if we're in a limited environment before running cargo
    result = subprocess.run(
        ["which", "protoc"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("Skipping: protoc not installed in environment")

    # Run the tests
    result = subprocess.run(
        ["cargo", "test", "--package", "chroma-worker", "source_record_segment_v2", "--", "--nocapture"],
        cwd=f"{REPO}/rust",
        capture_output=True,
        text=True,
        timeout=300
    )

    # Skip on resource constraints
    if result.returncode != 0:
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")

    assert result.returncode == 0, \
        f"SourceRecordSegmentV2 tests failed:\n{result.stdout}\n{result.stderr}"


def test_operator_uses_add_not_upsert():
    """F2P: Verify SourceRecordSegmentOperator uses Operation::Add, not Upsert."""
    sr_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment.rs"

    with open(sr_file, 'r') as f:
        content = f.read()

    # Find the operation assignment in the run method
    # Should be Operation::Add, not Operation::Upsert
    lines = content.split('\n')

    # Look for the operation line in the run implementation
    found_operation_line = False
    for i, line in enumerate(lines):
        if 'operation:' in line and 'OperationRecord' in lines[i-5:i]:
            # Check this is in the main implementation, not tests
            if 'mod tests' not in content[:content.find(line)] or content.find(line) < content.find('mod tests'):
                found_operation_line = True
                assert 'Operation::Add' in line, \
                    f"SourceRecordSegmentOperator should use Operation::Add, found: {line}"
                break

    # Also check the test assertions were updated
    assert 'assert_eq!(record.record.operation, Operation::Add)' in content, \
        "Test assertion should check for Operation::Add"


def test_v2_operator_partition_logic():
    """F2P: Verify V2 operator correctly partitions records."""
    v2_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment_v2.rs"

    with open(v2_file, 'r') as f:
        content = f.read()

    # Check for partition logic
    assert "max_partition_size" in content, \
        "max_partition_size parameter not used"
    assert "current_partition_logs.len() >= self.max_partition_size" in content, \
        "Partition size check not found"
    assert "partitions.push" in content, \
        "Partition pushing logic not found"

    # Verify the operator materializes logs using the new function
    assert "materialize_logs_for_rebuild" in content, \
        "Should use materialize_logs_for_rebuild function"


def test_v2_operator_handles_empty_reader():
    """F2P: Verify V2 operator handles empty/None reader correctly."""
    v2_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment_v2.rs"

    with open(v2_file, 'r') as f:
        content = f.read()

    # Check for None handling
    assert "record_segment_reader.as_ref()" in content, \
        "Should check if reader exists"
    assert "partitions: vec![]" in content or "partitions: vec![]" in content.replace(" ", ""), \
        "Should return empty partitions when reader is None"


def test_error_handling_for_non_add_operations():
    """F2P: Verify materialize_logs_for_rebuild rejects non-Add operations."""
    types_file = f"{RUST_SEGMENT}/src/types.rs"

    with open(types_file, 'r') as f:
        content = f.read()

    # Find the materialize_logs_for_rebuild function
    func_start = content.find("pub async fn materialize_logs_for_rebuild")
    assert func_start != -1, "materialize_logs_for_rebuild not found"

    # Get function body (next function or end of impl block)
    func_end = content.find("\npub ", func_start + 1)
    if func_end == -1:
        func_end = len(content)

    func_body = content[func_start:func_end]

    # Check for operation validation
    assert "log_record.record.operation != Operation::Add" in func_body, \
        "Should check that operation is Add"
    assert "UnsupportedOperationForRebuild" in func_body, \
        "Should return error for non-Add operations"


def test_log_fetch_orchestrator_integration():
    """F2P: Verify orchestrator uses V2 operator for partial rebuilds."""
    orch_file = f"{RUST_WORKER}/src/execution/orchestration/log_fetch_orchestrator.rs"

    with open(orch_file, 'r') as f:
        content = f.read()

    # Check imports
    assert "source_record_segment_v2" in content, \
        "source_record_segment_v2 module not imported"
    assert "SourceRecordSegmentV2Operator" in content, \
        "SourceRecordSegmentV2Operator not imported"
    assert "SourceRecordSegmentV2Input" in content, \
        "SourceRecordSegmentV2Input not imported"
    assert "SourceRecordSegmentV2Output" in content, \
        "SourceRecordSegmentV2Output not imported"
    assert "SourceRecordSegmentV2Error" in content, \
        "SourceRecordSegmentV2Error not imported"

    # Check for the handler implementation
    assert "Handler<TaskResult<SourceRecordSegmentV2Output" in content, \
        "Handler for SourceRecordSegmentV2Output not implemented"


def test_compact_integration():
    """F2P: Verify compact orchestration has rebuild test."""
    compact_file = f"{RUST_WORKER}/src/execution/orchestration/compact.rs"

    with open(compact_file, 'r') as f:
        content = f.read()

    # Check for the metadata rebuild FTS test
    assert "async fn test_metadata_rebuild_fts" in content, \
        "test_metadata_rebuild_fts test not found"


def test_source_record_segment_operator_constructors():
    """P2P: Verify SourceRecordSegmentOperator has new() and Default impl."""
    sr_file = f"{RUST_WORKER}/src/execution/operators/source_record_segment.rs"

    with open(sr_file, 'r') as f:
        content = f.read()

    # Check for new() constructor
    assert "pub fn new() -> Self" in content, \
        "SourceRecordSegmentOperator::new() not found"

    # Check for Default impl
    assert "impl Default for SourceRecordSegmentOperator" in content, \
        "Default impl for SourceRecordSegmentOperator not found"


def test_compilation_succeeds():
    """F2P: Verify the entire worker package compiles."""
    # Check if we're in a limited environment
    result = subprocess.run(
        ["which", "protoc"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("Skipping: protoc not installed in environment")

    result = subprocess.run(
        ["cargo", "check", "--package", "worker"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Skip on resource constraints
    if result.returncode != 0:
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")

    assert result.returncode == 0, \
        f"Worker package failed to compile:\n{result.stderr}"


def test_unit_tests_pass():
    """F2P: Verify all related unit tests pass."""
    # Check if we're in a limited environment
    result = subprocess.run(
        ["which", "protoc"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip("Skipping: protoc not installed in environment")

    # Run tests for source_record_segment (both v1 and v2)
    result = subprocess.run(
        ["cargo", "test", "--package", "worker", "source_record_segment", "--", "--nocapture"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Skip on resource constraints
    if result.returncode != 0:
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")

    assert result.returncode == 0, \
        f"Source record segment tests failed:\n{result.stdout}\n{result.stderr}"


# =============================================================================
# Pass-to-Pass (P2P) Tests - Repo CI/CD Checks
# These tests verify the repo's CI/CD pipeline passes on both base and fixed code
# =============================================================================

def test_repo_cargo_fmt():
    """P2P: Verify Rust code passes cargo fmt check (repo CI/CD)."""
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"cargo fmt check failed:\n{result.stderr}"


def test_repo_cargo_check_worker():
    """P2P: Verify worker package compiles with cargo check (repo CI/CD)."""
    # Note: This may require protoc to be installed in the environment
    # If it fails due to missing protoc, this test may be skipped
    result = subprocess.run(
        ["cargo", "check", "--package", "worker"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Only fail if it's not a protoc-related error or resource constraint
    if result.returncode != 0:
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        assert False, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_repo_cargo_clippy_worker():
    """P2P: Verify worker package passes cargo clippy (repo CI/CD)."""
    # Note: This may require protoc to be installed in the environment
    result = subprocess.run(
        ["cargo", "clippy", "--package", "worker", "--", "-D", "warnings"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Only fail if it's not a protoc-related error or resource constraint
    if result.returncode != 0:
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        assert False, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_repo_worker_tests():
    """P2P: Verify worker package tests pass (repo CI/CD)."""
    # Run a subset of worker tests that don't require external services
    result = subprocess.run(
        ["cargo", "test", "--package", "worker", "--lib", "--", "--nocapture"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Only fail if it's not a protoc-related error or resource constraint
    if result.returncode != 0:
        if "protoc" in result.stderr.lower() or "protobuf" in result.stderr.lower():
            pytest.skip("Skipping: protoc not installed in environment")
        if "No space left" in result.stderr:
            pytest.skip("Skipping: insufficient disk space")
        assert False, f"Worker tests failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
