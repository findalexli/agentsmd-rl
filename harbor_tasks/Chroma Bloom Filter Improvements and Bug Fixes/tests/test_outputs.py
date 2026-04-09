"""Tests for Chroma bloom filter improvements and bug fixes.

This task involves fixing several bugs in the bloom filter implementation:
1. Introducing deep_clone() to properly isolate cached instances from writer mutations
2. Fixing error propagation for BloomFilterSerializationError
3. Fixing cache key consistency between commit() and get()
4. Optimizing read path to use cached bloom filter when available
"""

import subprocess
import sys

REPO = "/workspace/chroma"
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
        ["grep", "-n", "fn cache_key_from_path", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
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
    # Check that save() errors are propagated with ? operator
    result = subprocess.run(
        ["grep", "save().*map_err", f"{RUST_SEGMENT}/src/blockfile_record.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "Bloom filter save() errors not properly propagated. "
        "Flush errors should fail the compaction."
    )


def test_relaxed_ordering_usage():
    """Verify atomic operations use Relaxed ordering instead of SeqCst.

    This is a minor optimization changing Ordering::SeqCst to Ordering::Relaxed
    for the live_count and stale_count atomic loads.
    """
    result = subprocess.run(
        ["grep", "Ordering::Relaxed", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
        capture_output=True,
        text=True,
    )
    # Should have multiple uses of Relaxed ordering (in deep_clone and serialization)
    count = result.stdout.count("Ordering::Relaxed")
    assert count >= 4, (
        f"Expected at least 4 uses of Ordering::Relaxed, found {count}. "
        "The atomic ordering optimization may be incomplete."
    )


def test_false_positive_rate_comment():
    """Verify the false positive rate comment was corrected.

    The comment incorrectly said 0.001% but the actual rate is 0.1%.
    """
    result = subprocess.run(
        ["grep", "0.1% false positive rate", f"{RUST_SEGMENT}/src/bloom_filter.rs"],
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
