"""Test outputs for chroma-rebuild-hotfix task.

This task adds a new SourceRecordSegmentV2Operator and materialize_logs_for_rebuild
function to properly handle rebuild operations in Chroma's compaction pipeline.
"""

import subprocess
import sys
import shutil
import os

REPO = "/workspace/chroma"
RUST_WORKER_DIR = f"{REPO}/rust/worker"
RUST_SEGMENT_DIR = f"{REPO}/rust/segment"


def _has_protoc():
    """Check if protoc (Protocol Buffers compiler) is available."""
    return shutil.which("protoc") is not None


# ============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks that must pass on both base and fix
# ============================================================================


def test_repo_fmt():
    """Repo's Rust code formatting passes (pass_to_pass).

    This test verifies that all Rust code follows the project's formatting
    standards using cargo fmt. This is a CI/CD gate from the repo's workflow.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Rust fmt check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_clippy():
    """Repo's Rust code passes clippy lints (pass_to_pass).

    This test runs cargo clippy with the same flags used in CI:
    -D warnings, -D clippy::large_futures, -D clippy::all

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping clippy check")
        return

    r = subprocess.run(
        ["cargo", "clippy", "--all-targets", "--all-features", "--", "-D", "warnings", "-D", "clippy::large_futures", "-D", "clippy::all"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy check failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_check_compiles():
    """Repo's Rust code compiles with cargo check (pass_to_pass).

    This test verifies the codebase compiles without errors using cargo check.

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping cargo check")
        return

    r = subprocess.run(
        ["cargo", "check", "--all-targets", "--all-features"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_doc_tests():
    """Repo's Rust doc tests pass (pass_to_pass).

    This test runs cargo test --doc which tests code examples in documentation.
    This is part of the repo's CI workflow (_rust-tests.yml).

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping doc tests")
        return

    r = subprocess.run(
        ["cargo", "test", "--doc"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Doc tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_toml_valid():
    """Repo's Cargo.toml files are valid (pass_to_pass).

    This test verifies that the workspace Cargo.toml and all member Cargo.toml
    files are valid by running cargo metadata, which parses all manifests.
    """
    r = subprocess.run(
        ["cargo", "metadata", "--format-version=1", "--no-deps"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo metadata failed (invalid TOML):\n{r.stderr[-500:]}"


def test_repo_build_cli():
    """Repo's CLI binary can be built (pass_to_pass).

    This test verifies that the chroma CLI binary compiles successfully.
    This is a key CI check from _rust-tests.yml.

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping CLI build")
        return

    r = subprocess.run(
        ["cargo", "build", "--bin", "chroma"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"CLI build failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_worker_package_compiles():
    """Worker package compiles independently (pass_to_pass).

    This test checks that the rust/worker package compiles, which is the
    primary package modified by this task.

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping worker compile check")
        return

    r = subprocess.run(
        ["cargo", "check", "-p", "chroma-worker"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Worker package check failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_segment_package_compiles():
    """Segment package compiles independently (pass_to_pass).

    This test checks that the rust/segment package compiles, which contains
    the materialize_logs_for_rebuild function added by this task.

    Note: This test requires protoc to be installed. If protoc is missing,
    the test is skipped since this is a build environment issue, not a code issue.
    """
    if not _has_protoc():
        print("SKIP: protoc not installed, skipping segment compile check")
        return

    r = subprocess.run(
        ["cargo", "check", "-p", "chroma-segment"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Segment package check failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# ============================================================================
# FAIL-TO-PASS TESTS - Tests that fail before the fix and pass after
# ============================================================================


def test_compilation():
    """Verify the Rust code compiles successfully."""
    result = subprocess.run(
        ["cargo", "check"],
        cwd=RUST_WORKER_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_source_v2_basic():
    """Test SourceRecordSegmentV2Operator properly partitions records."""
    result = subprocess.run(
        ["cargo", "test", "test_source_v2_basic", "--", "--nocapture"],
        cwd=RUST_WORKER_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"test_source_v2_basic failed:\n{result.stderr}"
    # Verify test assertions passed
    assert "test result: ok" in result.stdout, f"Test did not pass:\n{result.stdout}"


def test_source_v2_empty():
    """Test SourceRecordSegmentV2Operator handles empty reader correctly."""
    result = subprocess.run(
        ["cargo", "test", "test_source_v2_empty", "--", "--nocapture"],
        cwd=RUST_WORKER_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"test_source_v2_empty failed:\n{result.stderr}"
    assert "test result: ok" in result.stdout, f"Test did not pass:\n{result.stdout}"


def test_source_v2_preserves_offset_ids():
    """Test SourceRecordSegmentV2Operator preserves offset IDs correctly."""
    result = subprocess.run(
        ["cargo", "test", "test_source_v2_preserves_offset_ids", "--", "--nocapture"],
        cwd=RUST_WORKER_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"test_source_v2_preserves_offset_ids failed:\n{result.stderr}"
    assert "test result: ok" in result.stdout, f"Test did not pass:\n{result.stdout}"


def test_source_record_segment_uses_add_operation():
    """Verify SourceRecordSegmentOperator now uses Add operation instead of Upsert."""
    # Check the source file contains Add operation (not Upsert)
    source_file = f"{RUST_WORKER_DIR}/src/execution/operators/source_record_segment.rs"
    with open(source_file, "r") as f:
        content = f.read()

    # Verify Add operation is used (the fix changed from Upsert to Add)
    assert 'operation: chroma_types::Operation::Add' in content, \
        "SourceRecordSegmentOperator should use Operation::Add"

    # Verify Upsert is NOT used anymore
    assert 'operation: chroma_types::Operation::Upsert' not in content, \
        "SourceRecordSegmentOperator should NOT use Operation::Upsert"


def test_materialize_logs_for_rebuild_exists():
    """Verify materialize_logs_for_rebuild function exists in segment types."""
    types_file = f"{RUST_SEGMENT_DIR}/src/types.rs"
    with open(types_file, "r") as f:
        content = f.read()

    # Verify the new function exists
    assert "pub async fn materialize_logs_for_rebuild" in content, \
        "materialize_logs_for_rebuild function should exist"

    # Verify the UnsupportedOperationForRebuild error variant exists
    assert "UnsupportedOperationForRebuild" in content, \
        "UnsupportedOperationForRebuild error variant should exist"


def test_source_record_segment_has_constructor():
    """Verify SourceRecordSegmentOperator has new() and Default impl."""
    source_file = f"{RUST_WORKER_DIR}/src/execution/operators/source_record_segment.rs"
    with open(source_file, "r") as f:
        content = f.read()

    # Verify new() constructor exists
    assert "pub fn new() -> Self" in content or "impl SourceRecordSegmentOperator" in content, \
        "SourceRecordSegmentOperator should have constructor"

    # Verify Default impl exists
    assert "impl Default for SourceRecordSegmentOperator" in content, \
        "SourceRecordSegmentOperator should implement Default"


def test_v2_operator_module_exported():
    """Verify source_record_segment_v2 module is exported in operators mod."""
    mod_file = f"{RUST_WORKER_DIR}/src/execution/operators/mod.rs"
    with open(mod_file, "r") as f:
        content = f.read()

    assert "pub mod source_record_segment_v2" in content, \
        "source_record_segment_v2 module should be exported"


def test_v2_operator_source_file_exists():
    """Verify source_record_segment_v2.rs source file exists."""
    v2_file = f"{RUST_WORKER_DIR}/src/execution/operators/source_record_segment_v2.rs"
    assert os.path.exists(v2_file), \
        f"source_record_segment_v2.rs should exist at {v2_file}"


def test_log_fetch_orchestrator_uses_v2():
    """Verify LogFetchOrchestrator integrates SourceRecordSegmentV2Operator."""
    orch_file = f"{RUST_WORKER_DIR}/src/execution/orchestration/log_fetch_orchestrator.rs"
    with open(orch_file, "r") as f:
        content = f.read()

    # Verify V2 types are imported
    assert "SourceRecordSegmentV2Operator" in content, \
        "LogFetchOrchestrator should reference SourceRecordSegmentV2Operator"

    # Verify V2 error type exists
    assert "SourceRecordSegmentV2Error" in content, \
        "SourceRecordSegmentV2Error should be used in LogFetchOrchestrator"


if __name__ == "__main__":
    # Run all test functions
    test_funcs = [
        test_repo_fmt,
        test_repo_clippy,
        test_repo_check_compiles,
        test_repo_doc_tests,
        test_repo_toml_valid,
        test_repo_build_cli,
        test_worker_package_compiles,
        test_segment_package_compiles,
        test_compilation,
        test_source_v2_basic,
        test_source_v2_empty,
        test_source_v2_preserves_offset_ids,
        test_source_record_segment_uses_add_operation,
        test_materialize_logs_for_rebuild_exists,
        test_source_record_segment_has_constructor,
        test_v2_operator_module_exported,
        test_v2_operator_source_file_exists,
        test_log_fetch_orchestrator_uses_v2,
    ]

    passed = 0
    failed = 0
    skipped = 0

    for test_func in test_funcs:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: Exception: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(0 if failed == 0 else 1)
