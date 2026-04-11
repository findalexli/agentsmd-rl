"""
Test suite for chroma-hnsw-reload-repro task.

This task requires adding a regression test for an HNSW index reload
assertion failure in the hnswlib library.
"""

import subprocess
import os

REPO = "/workspace/chroma"
RUST_DIR = f"{REPO}/rust"
TEST_FILE = f"{RUST_DIR}/index/tests/hnsw_reload_repro.rs"


# ============================================================================
# FAIL-TO-PASS TESTS
# These fail on base commit and pass after the fix is applied
# ============================================================================


def test_file_exists():
    """Fail-to-pass: The test file must be created at the expected location."""
    assert os.path.exists(TEST_FILE), f"Test file not found at {TEST_FILE}"


def test_test_compiles():
    """Fail-to-pass: The test file must compile without errors.

    This test uses cargo check to verify the test code compiles successfully.
    Before the fix: file doesn't exist, so compilation fails.
    After the fix: file exists and compiles correctly.
    """
    result = subprocess.run(
        ["cargo", "check", "--test", "hnsw_reload_repro", "-p", "chroma-index"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_repro_test_runs():
    """Fail-to-pass: The reproduction test can be built and executed.

    This test verifies that the reproduction test binary can be built
    and actually runs. It only runs the test compilation (--no-run) to
    avoid triggering the actual assertion failure/crash in the test
    environment, but verifies the test target is valid.

    Before the fix: test file doesn't exist, so cargo test --no-run fails.
    After the fix: test binary compiles successfully.
    """
    # Build the test binary
    result = subprocess.run(
        ["cargo", "test", "--test", "hnsw_reload_repro", "-p", "chroma-index", "--no-run"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Test binary build failed:\n{result.stderr}"

    # Verify the test binary exists
    test_binary_pattern = f"{RUST_DIR}/target/debug/deps/hnsw_reload_repro"
    found_binary = False
    if os.path.exists(f"{RUST_DIR}/target/debug/deps"):
        for f in os.listdir(f"{RUST_DIR}/target/debug/deps"):
            if f.startswith("hnsw_reload_repro") and not f.endswith(".d"):
                found_binary = True
                break

    assert found_binary, "Test binary not found in target/debug/deps/"


def test_repro_test_structure():
    """Fail-to-pass: The reproduction test has the correct structure.

    This verifies that the test file contains the expected function signatures,
    imports, and patterns that match the PR diff requirements.

    Before the fix: file doesn't exist or doesn't have correct structure.
    After the fix: file exists with proper test implementation.
    """
    assert os.path.exists(TEST_FILE), f"Test file not found at {TEST_FILE}"

    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # Check for the main test function name from the PR
    assert "fn deleted_heads_can_abort_a_future_reload()" in content, \
        "Missing main test function: deleted_heads_can_abort_a_future_reload"

    # Check for required imports that show the test uses the correct APIs
    required_patterns = [
        "chroma_blockstore::provider::BlockfileProvider",
        "chroma_index::hnsw_provider::HnswIndexProvider",
        "chroma_index::spann::types::SpannIndexWriter",
        "chroma_types::CollectionUuid",
        "tokio::runtime::Builder",
        "new_multi_thread",
    ]

    for pattern in required_patterns:
        assert pattern in content, f"Missing required pattern: {pattern}"


# ============================================================================
# PASS-TO-PASS TESTS
# These verify that the fix doesn't break existing functionality
# ============================================================================


def test_rust_code_compiles():
    """Pass-to-pass: The chroma-index crate compiles without errors.

    This ensures the fix doesn't introduce compilation errors in the crate.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "chroma-index"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Crate compilation failed:\n{result.stderr}"


def test_rustfmt():
    """Pass-to-pass: The chroma-index crate passes rustfmt check."""
    result = subprocess.run(
        ["cargo", "fmt", "--check", "-p", "chroma-index"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Rustfmt check failed:\n{result.stderr}"


def test_clippy():
    """Pass-to-pass: The chroma-index crate passes clippy linting."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "chroma-index", "--", "-D", "warnings"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Clippy check failed:\n{result.stderr[-1000:]}"


def test_repo_tests_pass():
    """Pass-to-pass: The chroma-index crate's existing tests pass.

    This runs the crate's own test suite (excluding the new hnsw_reload_repro test
    and test_flush_from_memory_propagates_errors which fails in Docker due to
    permission handling differences) to ensure the fix doesn't break any existing
    functionality.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "chroma-index", "--lib", "--",
         "--skip", "test_flush_from_memory_propagates_errors"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"Existing tests failed:\n{result.stderr[-1000:]}"


def test_hnsw_provider_tests():
    """Pass-to-pass: HNSW provider tests pass (excluding Docker-specific test).

    These tests cover the HnswIndexProvider which is central to the reload
    functionality being fixed by this PR.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "chroma-index", "--lib", "hnsw_provider", "--",
         "--skip", "test_flush_from_memory_propagates_errors"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"HNSW provider tests failed:\n{result.stderr[-500:]}"


def test_spann_tests():
    """Pass-to-pass: SPANN index tests pass.

    These tests cover the SpannIndex which uses the HNSW provider and is
    directly related to the reload issue being fixed.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "chroma-index", "--lib", "spann"],
        cwd=RUST_DIR,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"SPANN tests failed:\n{result.stderr[-500:]}"
