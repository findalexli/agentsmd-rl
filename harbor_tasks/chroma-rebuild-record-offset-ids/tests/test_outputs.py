"""
Test suite for Chroma segment rebuild fix (PR #6699).

This tests that vector segment rebuilds properly retain references to
the record segment reader so they can refer to pre-existing offset IDs.
"""

import subprocess
import os

REPO = "/workspace/chroma"
RUST_DIR = f"{REPO}/rust"


def run_cargo_test(test_pattern: str, timeout: int = 300) -> tuple[bool, str]:
    """Run a specific cargo test pattern and return (passed, output)."""
    result = subprocess.run(
        ["cargo", "test", test_pattern, "--", "--nocapture"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.returncode == 0, result.stdout + result.stderr


def run_cargo_check() -> tuple[bool, str]:
    """Run cargo check and return (passed, output)."""
    result = subprocess.run(
        ["cargo", "check", "--all-targets"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.returncode == 0, result.stdout + result.stderr


def test_is_full_rebuild_method():
    """
    Test that CompactionContext has the is_full_rebuild() method.

    This method distinguishes between a full rebuild (where RECORD scope is active)
    vs a partial rebuild (where only VECTOR scope is active).
    """
    # First verify the code compiles
    passed, output = run_cargo_check()
    assert passed, f"Code does not compile:\n{output}"

    # Test the compact orchestrator tests that exercise is_full_rebuild
    passed, output = run_cargo_test("test_rebuild_vector_only", timeout=600)
    assert passed, f"test_rebuild_vector_only failed:\n{output}"

    # Verify the method signature exists in the source
    compact_file = f"{RUST_DIR}/worker/src/execution/orchestration/compact.rs"
    with open(compact_file, 'r') as f:
        content = f.read()

    # Check for is_full_rebuild method
    assert "is_full_rebuild" in content, "is_full_rebuild method not found in compact.rs"
    assert "scope_is_active(&chroma_types::SegmentScope::RECORD)" in content, \
        "is_full_rebuild should check RECORD scope"


def test_source_record_operation_upsert():
    """
    Test that SourceRecordSegmentProvider yields Upserts instead of Adds.

    Before the fix, records sourced from the record segment were treated as Add
    operations. After the fix, they are correctly treated as Upsert operations
    since they may already exist.
    """
    source_file = f"{RUST_DIR}/worker/src/execution/operators/source_record_segment.rs"
    with open(source_file, 'r') as f:
        content = f.read()

    # Check that the operation is Upsert
    assert "operation: chroma_types::Operation::Upsert" in content, \
        "SourceRecordSegment should yield Upsert operations"

    # Verify Add is not used (should not find Operation::Add in the non-test code)
    # The test code also checks for Upsert now
    test_section = content.split("mod tests")[0] if "mod tests" in content else content
    assert "Operation::Add" not in test_section, \
        "SourceRecordSegment should not yield Add operations in production code"


def test_record_reader_retained_in_rebuild():
    """
    Test that record reader is retained during vector-only rebuilds.

    The fix changes the condition from `!self.context.is_rebuild` to
    `!self.context.is_full_rebuild()` so that during a vector-only rebuild,
    the record reader is still available to look up offset IDs.
    """
    log_fetch_file = f"{RUST_DIR}/worker/src/execution/orchestration/log_fetch_orchestrator.rs"
    with open(log_fetch_file, 'r') as f:
        content = f.read()

    # Check that is_full_rebuild is used, not just is_rebuild
    assert "is_full_rebuild()" in content, \
        "log_fetch_orchestrator should use is_full_rebuild() for record_reader filter"

    # Verify the comment explaining the fix is present
    assert "rebuilding but not applying to the record segment" in content, \
        "Expected explanatory comment about vector-only rebuilds"


def test_apply_segment_scopes_passed():
    """
    Test that apply_segment_scopes is passed through LogFetchOrchestrator.

    The fix requires passing the apply_segment_scopes from CompactionContext
    to LogFetchOrchestrator so it can determine what kind of rebuild this is.
    """
    log_fetch_file = f"{RUST_DIR}/worker/src/execution/orchestration/log_fetch_orchestrator.rs"
    with open(log_fetch_file, 'r') as f:
        content = f.read()

    # Check the new function parameter exists
    assert "apply_segment_scopes: std::collections::HashSet<chroma_types::SegmentScope>" in content, \
        "apply_segment_scopes parameter should be in LogFetchOrchestrator::new"

    # Check it's passed to CompactionContext::new
    assert "apply_segment_scopes," in content, \
        "apply_segment_scopes should be passed to CompactionContext"


def test_distributed_hnsw_get_all_offset_ids():
    """
    Test that DistributedHNSWSegmentReader has get_all_offset_ids method.

    This method is needed by the test to verify that offset IDs match between
    vector and record segments after a rebuild.
    """
    hnsw_file = f"{RUST_DIR}/segment/src/distributed_hnsw.rs"
    with open(hnsw_file, 'r') as f:
        content = f.read()

    # Check for the new method
    assert "get_all_offset_ids" in content, \
        "DistributedHNSWSegmentReader should have get_all_offset_ids method"

    # Verify it returns the expected type
    assert "Result<Vec<usize>, Box<dyn ChromaError>>" in content, \
        "get_all_offset_ids should return Vec<usize>"


def test_apply_logs_orchestrator_uses_full_rebuild():
    """
    Test that ApplyLogsOrchestrator uses is_full_rebuild() instead of is_rebuild.

    The fix changes the condition for setting collection_logical_size_bytes
    to use is_full_rebuild() for more accurate size calculation.
    """
    apply_logs_file = f"{RUST_DIR}/worker/src/execution/orchestration/apply_logs_orchestrator.rs"
    with open(apply_logs_file, 'r') as f:
        content = f.read()

    # Should use is_full_rebuild() not just is_rebuild for collection size calc
    assert "is_full_rebuild()" in content, \
        "ApplyLogsOrchestrator should use is_full_rebuild() for size calculation"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks)
# =============================================================================
# These tests verify that the repo's CI/CD checks pass on both the base
# commit and after the fix is applied, ensuring no regressions.


def test_repo_cargo_check():
    """Repo's cargo check passes on worker and chroma-segment packages (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "--lib", "--package", "worker", "--package", "chroma-segment"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr[-1000:]}"


def test_repo_cargo_clippy():
    """Repo's cargo clippy passes on worker and chroma-segment packages (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "clippy", "--lib", "--package", "worker", "--package", "chroma-segment"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Cargo clippy failed:\n{result.stderr[-1000:]}"


def test_repo_cargo_fmt():
    """Repo's Rust code formatting passes (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Cargo fmt check failed:\n{result.stdout[-500:]}"
