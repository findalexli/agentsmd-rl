"""Tests for Chroma bloom filter improvements and bug fixes.

This task involves fixing several bugs in the bloom filter implementation:
1. Introducing deep_clone() to properly isolate cached instances from writer mutations
2. Fixing error propagation for BloomFilterSerializationError
3. Fixing cache key consistency between commit() and get()
4. Optimizing read path to use cached bloom filter when available
"""

import subprocess
import sys
from pathlib import Path
import pytest

REPO = "/workspace/chroma"
RUST_ROOT = f"{REPO}"  # Cargo.toml is at repo root
RUST_SEGMENT = f"{REPO}/rust/segment"


def run_cargo(args: list[str], cwd: str = RUST_SEGMENT, timeout: int = 180) -> subprocess.CompletedProcess:
    """Run a cargo command and return the result."""
    return subprocess.run(
        ["cargo"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_cargo_check():
    """Verify the Rust code compiles without errors."""
    result = run_cargo(["check"], timeout=300)
    assert result.returncode == 0, f"Cargo check failed:\n{result.stderr}"


def test_deep_clone_method_exists():
    """Verify the deep_clone() method exists and is properly implemented.

    This is a fail-to-pass test: before the fix, deep_clone() doesn't exist.
    After the fix, it should exist and create independent copies.
    """
    # Check that deep_clone method is defined in the source
    result = subprocess.run(
        ["grep", "-n", "pub fn deep_clone", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "deep_clone() method not found in bloom_filter.rs"
    assert "deep_clone" in result.stdout, "deep_clone method signature not found"


def test_deep_clone_isolation():
    """Run the unit test that verifies deep_clone properly isolates instances.

    The test verifies:
    - Cloned bloom filter starts with same state
    - Mutating original doesn't affect clone
    - Mutating clone doesn't affect original
    - Shallow clone shares state (Arc), deep_clone doesn't
    """
    # First check if the test exists (fail-to-pass: test shouldn't exist on base commit)
    result = subprocess.run(
        ["grep", "fn test_deep_clone_isolation", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail("test_deep_clone_isolation test not found - deep_clone feature not implemented")

    result = run_cargo(["test", "test_deep_clone_isolation", "--", "--nocapture"])
    assert result.returncode == 0, f"test_deep_clone_isolation failed:\n{result.stdout}\n{result.stderr}"


def test_error_propagation_fix():
    """Verify BloomFilterSerializationError now wraps BloomFilterError.

    Before: BloomFilterSerializationError was a unit variant
    After: BloomFilterSerializationError(BloomFilterError) wraps the error
    """
    # Check the error type now has a wrapped BloomFilterError
    result = subprocess.run(
        ["grep", "BloomFilterSerializationError(BloomFilterError)",
         f"{RUST_SEGMENT}/src/blockfile_record.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "BloomFilterSerializationError doesn't wrap BloomFilterError. "
        "The error propagation fix may be missing."
    )


def test_cache_key_from_path_method():
    """Verify cache_key_from_path helper method exists for consistent cache keys.

    This method ensures commit() and get() use the same cache key format,
    fixing a bug where the read path used full path but insert key was just UUID.
    """
    result = subprocess.run(
        ["grep", "fn cache_key_from_path", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "cache_key_from_path() method not found"


def test_deep_clone_used_in_commit():
    """Verify commit() uses deep_clone() instead of clone() for cache insertion.

    Before: commit() used bf.clone() which shared the Arc - mutations affected cache
    After: commit() uses bf.deep_clone() for proper isolation
    """
    # Check commit method uses deep_clone
    result = subprocess.run(
        ["grep", "bf.deep_clone()", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "commit() doesn't use deep_clone(). "
        "The cached bloom filter may be incorrectly shared with writer."
    )
    # Should appear at least twice (commit and get methods)
    assert result.stdout.count("deep_clone()") >= 2, (
        "deep_clone() should be used in both commit() and get() methods"
    )


def test_fetch_bloom_filter_method():
    """Verify the ensure_bloom_filter was renamed to fetch_bloom_filter.

    This is part of the read path optimization to distinguish between:
    - fetch_bloom_filter(): loads from storage (when use_bloom_filter is true)
    - try_load_bloom_filter_from_cache(): only uses cache (optimization path)
    """
    result = subprocess.run(
        ["grep", "async fn fetch_bloom_filter", f"{RUST_SEGMENT}/src/blockfile_record.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "fetch_bloom_filter() method not found. "
        "The read path optimization may be missing."
    )


def test_try_load_from_cache_method():
    """Verify try_load_bloom_filter_from_cache() method exists.

    This method allows the read path to use cached bloom filters
    without triggering a storage fetch.
    """
    result = subprocess.run(
        ["grep", "async fn try_load_bloom_filter_from_cache",
         f"{RUST_SEGMENT}/src/blockfile_record.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "try_load_bloom_filter_from_cache() method not found. "
        "The read path cache optimization may be missing."
    )


def test_flush_error_propagation():
    """Verify bloom filter flush errors now fail the compaction.

    Before: flush errors were logged as warnings but compaction succeeded
    After: flush errors are propagated and fail the compaction
    """
    # Check that save() is followed by error handling - look for the pattern
    # where save() result is handled with map_err and ? operator
    # The pattern spans multiple lines: save().await.map_err(...)?
    result = subprocess.run(
        ["grep", "-A2", "save()", f"{RUST_SEGMENT}/src/blockfile_record.rs"],
        capture_output=True,
        text=True,
    )
    # Check if save() call exists and is followed by .await.map_err or .await
    assert result.returncode == 0, "save() call not found in blockfile_record.rs"
    # Check for error propagation pattern (should have await and map_err in context)
    assert ".await" in result.stdout, "save() call should be followed by .await"
    # Check that the error is propagated with ? operator (by checking for map_err)
    assert "map_err" in result.stdout, "save() errors not propagated with map_err"


def test_relaxed_ordering_usage():
    """Verify atomic operations use Relaxed ordering instead of SeqCst in deep_clone.

    This is a minor optimization changing Ordering::SeqCst to Ordering::Relaxed
    for the live_count and stale_count atomic loads specifically in the deep_clone method.
    """
    # Check that deep_clone method exists first
    result = subprocess.run(
        ["grep", "-A 20", "pub fn deep_clone", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail("deep_clone() method not found - cannot verify Ordering::Relaxed usage")

    # Check that deep_clone method body uses Relaxed ordering
    deep_clone_body = result.stdout
    relaxed_count = deep_clone_body.count("Ordering::Relaxed")
    assert relaxed_count >= 2, (
        f"Expected at least 2 uses of Ordering::Relaxed in deep_clone, found {relaxed_count}. "
        "The atomic ordering optimization in deep_clone may be incomplete."
    )


def test_false_positive_rate_comment():
    """Verify the false positive rate comment was corrected.

    The comment incorrectly said 0.001% but the actual rate is 0.1%.
    """
    result = subprocess.run(
        ["grep", "with a 0.1% false positive rate", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "False positive rate comment not corrected to 0.1%. "
        "The documentation fix may be missing."
    )


def test_bloom_filter_unit_tests():
    """Run all bloom_filter module unit tests to ensure no regressions."""
    result = run_cargo(["test", "bloom_filter::", "--", "--nocapture"])
    assert result.returncode == 0, f"Bloom filter unit tests failed:\n{result.stdout}\n{result.stderr}"


# =============================================================================
# Pass-to-Pass Tests - Repo CI Checks
# These tests verify the repo's CI passes on the base commit (before the fix).
# Note: Some tests require protoc which is not installed in the Docker image.
# They are structured to pass when the environment is properly configured.
# =============================================================================


def test_cargo_fmt_check():
    """Rust code formatting passes (pass_to_pass).

    This is the repo's lint check from .github/workflows/pr.yml:
    cargo fmt -- --check
    """
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=RUST_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"cargo fmt check failed:\n{result.stderr}"


def test_cargo_clippy_check():
    """Rust clippy linting passes (pass_to_pass).

    This is the repo's lint check from .github/workflows/pr.yml:
    cargo clippy --all-targets --all-features --keep-going -- -D warnings

    Note: We run on just the segment package to avoid disk space issues
    with compiling the entire workspace in Docker.
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "chroma-segment", "--all-features", "--", "-D", "warnings"],
        cwd=RUST_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_bloom_filter_module_tests():
    """Bloom filter module unit tests pass (pass_to_pass).

    Runs the existing unit tests in the bloom_filter module:
    - test_format_key
    - test_insert_and_contains
    - test_mark_deleted
    - test_serialization_roundtrip
    - test_needs_rebuild_stale_ratio
    - test_needs_rebuild_over_capacity
    """
    result = subprocess.run(
        ["cargo", "test", "--lib", "bloom_filter::", "--", "--nocapture"],
        cwd=RUST_SEGMENT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Bloom filter unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_modified_files_exist():
    """Modified source files exist and are readable (pass_to_pass)."""
    # Files modified by the PR
    modified_files = [
        f"{REPO}/rust/segment/src/bloom_filter.rs",
        f"{REPO}/rust/segment/src/blockfile_record.rs",
    ]
    for filepath in modified_files:
        assert Path(filepath).exists(), f"Modified file does not exist: {filepath}"
        # Verify file is readable and non-empty
        content = Path(filepath).read_text()
        assert len(content) > 0, f"Modified file is empty: {filepath}"


def test_bloom_filter_has_tests():
    """Bloom filter module contains unit tests (pass_to_pass)."""
    result = subprocess.run(
        ["grep", "-c", r"#\[test\]", f"{REPO}/rust/segment/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "No tests found in bloom_filter.rs"
    test_count = int(result.stdout.strip())
    assert test_count >= 7, f"Expected at least 7 tests, found {test_count}"


def test_no_trailing_whitespace_rust():
    """No trailing whitespace in modified Rust files (pass_to_pass).

    Mirrors the pre-commit check from .github/workflows/pr.yml:
    pre-commit run --all-files trailing-whitespace
    """
    modified_files = [
        f"{REPO}/rust/segment/src/bloom_filter.rs",
        f"{REPO}/rust/segment/src/blockfile_record.rs",
    ]
    for filepath in modified_files:
        content = Path(filepath).read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            assert not line.endswith(" "), f"Trailing whitespace in {filepath}:{i}"
            assert not line.endswith("\t"), f"Trailing tab in {filepath}:{i}"
