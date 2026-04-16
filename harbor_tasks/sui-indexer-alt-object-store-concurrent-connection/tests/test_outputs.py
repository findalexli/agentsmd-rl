"""Tests for sui-indexer-alt-object-store ConcurrentConnection implementation.

This module tests that the ObjectStoreConnection properly implements
the ConcurrentConnection trait methods and init_watermark functionality.
"""

import subprocess
import sys

REPO = "/workspace/sui"
CRATE = "sui-indexer-alt-object-store"


def run_cargo_test(test_filter: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run cargo test for the specific crate."""
    cmd = ["cargo", "test", "-p", CRATE, "--lib"]
    if test_filter:
        cmd.extend(["--", test_filter])
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def run_cargo_check() -> subprocess.CompletedProcess:
    """Run cargo check for the specific crate."""
    return subprocess.run(
        ["cargo", "check", "-p", CRATE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )


def check_test_actually_ran(result: subprocess.CompletedProcess, test_name: str) -> bool:
    """Check if a specific test was actually found and ran.

    Cargo test exits with 0 even when no tests match the filter,
    so we need to verify the test actually ran.
    """
    combined_output = result.stdout + result.stderr
    # Test ran if we see it in the output
    # Cargo test outputs test names as "tests::test_name" with "... ok" or "... FAILED"
    test_full_name = f"tests::{test_name}"
    return (test_full_name in combined_output and ("... ok" in combined_output or "... FAILED" in combined_output))


# =============================================================================
# Fail-to-pass tests: These test the actual behavioral changes
# =============================================================================

def test_reader_watermark_returns_data():
    """
    ConcurrentConnection::reader_watermark() should return actual watermark data.

    Before fix: Returns Ok(None) (unimplemented stub)
    After fix: Returns Ok(Some(ReaderWatermark{...}))
    """
    r = run_cargo_test("test_reader_watermark_roundtrip", timeout=120)
    assert check_test_actually_ran(r, "test_reader_watermark_roundtrip"), \
        f"Test test_reader_watermark_roundtrip was not found - fix not applied"
    assert r.returncode == 0, f"reader_watermark test failed:\n{r.stderr[-1000:]}"


def test_pruner_watermark_returns_data():
    """
    ConcurrentConnection::pruner_watermark() should return actual watermark with wait time.

    Before fix: Returns Ok(None) (unimplemented stub)
    After fix: Returns Ok(Some(PrunerWatermark{...})) with computed wait_for_ms
    """
    r = run_cargo_test("test_pruner_watermark_wait_for_ms", timeout=120)
    assert check_test_actually_ran(r, "test_pruner_watermark_wait_for_ms"), \
        f"Test test_pruner_watermark_wait_for_ms was not found - fix not applied"
    assert r.returncode == 0, f"pruner_watermark test failed:\n{r.stderr[-1000:]}"


def test_set_reader_watermark_updates():
    """
    ConcurrentConnection::set_reader_watermark() should update watermark successfully.

    Before fix: Returns Err("Pruning not supported by this store")
    After fix: Updates watermark and returns Ok(true)

    This is tested via test_reader_watermark_roundtrip which exercises both read and set.
    """
    r = run_cargo_test("test_reader_watermark_roundtrip", timeout=120)
    assert check_test_actually_ran(r, "test_reader_watermark_roundtrip"), \
        f"Test test_reader_watermark_roundtrip was not found - fix not applied"
    assert r.returncode == 0, f"reader_watermark_roundtrip test failed:\n{r.stderr[-1000:]}"


def test_set_pruner_watermark_updates():
    """
    ConcurrentConnection::set_pruner_watermark() should update watermark successfully.

    Before fix: Returns Err("Pruning not supported by this store")
    After fix: Updates watermark and returns Ok(true)
    """
    r = run_cargo_test("test_set_pruner_watermark", timeout=120)
    assert check_test_actually_ran(r, "test_set_pruner_watermark"), \
        f"Test test_set_pruner_watermark was not found - fix not applied"
    assert r.returncode == 0, f"set_pruner_watermark test failed:\n{r.stderr[-1000:]}"


def test_init_watermark_with_checkpoint():
    """
    init_watermark() should properly use checkpoint_hi_inclusive parameter.

    Before fix: Ignores checkpoint parameter, delegates to reader_watermark
    After fix: Creates watermark with proper reader_lo = checkpoint + 1
    """
    r = run_cargo_test("test_init_watermark_fresh_with_checkpoint", timeout=120)
    assert check_test_actually_ran(r, "test_init_watermark_fresh_with_checkpoint"), \
        f"Test test_init_watermark_fresh_with_checkpoint was not found - fix not applied"
    assert r.returncode == 0, f"init_watermark with checkpoint test failed:\n{r.stderr[-1000:]}"


def test_legacy_watermark_migration():
    """
    init_watermark() should migrate legacy watermark format to new format.

    Before fix: Legacy format parsing fails or is not handled
    After fix: Detects legacy format (missing reader_lo/pruner fields) and migrates
    """
    r = run_cargo_test("test_init_watermark_migrates_legacy_format", timeout=120)
    assert check_test_actually_ran(r, "test_init_watermark_migrates_legacy_format"), \
        f"Test test_init_watermark_migrates_legacy_format was not found - fix not applied"
    assert r.returncode == 0, f"legacy watermark migration test failed:\n{r.stderr[-1000:]}"


def test_init_watermark_returns_existing():
    """
    init_watermark() should return existing watermark on AlreadyExists.

    Before fix: delegate_to_reader_watermark doesn't return proper InitWatermark
    After fix: Returns existing checkpoint_hi and reader_lo values
    """
    r = run_cargo_test("test_init_watermark_returns_existing_on_conflict", timeout=120)
    assert check_test_actually_ran(r, "test_init_watermark_returns_existing_on_conflict"), \
        f"Test test_init_watermark_returns_existing_on_conflict was not found - fix not applied"
    assert r.returncode == 0, f"init_watermark returns existing test failed:\n{r.stderr[-1000:]}"


# =============================================================================
# Pass-to-pass tests: Repo CI/CD commands
# =============================================================================

def test_cargo_check():
    """Repo's cargo check passes for the crate (pass_to_pass)."""
    r = run_cargo_check()
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_cargo_fmt():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_cargo_xlint():
    """Repo's license linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr[-500:]}"


def test_existing_unit_tests():
    """Existing unit tests in the crate pass (pass_to_pass).

    Runs existing tests excluding the new tests added by the fix.
    These are the baseline tests that should pass before the fix.
    """
    # Run tests but exclude the watermark tests that the fix adds
    # The only pre-existing test is test_watermark_operations
    r = subprocess.run(
        ["cargo", "test", "-p", CRATE, "--lib", "--", "test_watermark_operations"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Existing unit tests failed:\n{r.stderr[-1000:]}"


# =============================================================================
# Structural verification tests (gated behind behavioral pass)
# =============================================================================

def test_watermark_path_helper_exists():
    """Verify watermark_path helper function exists (structural check)."""
    import os
    lib_file = os.path.join(REPO, "crates", CRATE, "src", "lib.rs")
    with open(lib_file, 'r') as f:
        content = f.read()

    # This should only be checked if behavioral tests pass
    # The watermark_path function is a key helper added in the fix
    assert "fn watermark_path" in content, "watermark_path helper function not found"


def test_object_store_watermark_struct_exists():
    """Verify ObjectStoreWatermark struct with new fields exists."""
    import os
    lib_file = os.path.join(REPO, "crates", CRATE, "src", "lib.rs")
    with open(lib_file, 'r') as f:
        content = f.read()

    # Verify the new struct with reader_lo, pruner_hi, pruner_timestamp_ms fields
    assert "struct ObjectStoreWatermark" in content, "ObjectStoreWatermark struct not found"
    assert "reader_lo: u64" in content, "reader_lo field not found"
    assert "pruner_hi: u64" in content, "pruner_hi field not found"
    assert "pruner_timestamp_ms: u64" in content, "pruner_timestamp_ms field not found"


def test_get_watermark_helpers_exist():
    """Verify get_watermark_for_read and get_watermark_for_write helpers exist."""
    import os
    lib_file = os.path.join(REPO, "crates", CRATE, "src", "lib.rs")
    with open(lib_file, 'r') as f:
        content = f.read()

    assert "async fn get_watermark_for_read" in content, "get_watermark_for_read not found"
    assert "async fn get_watermark_for_write" in content, "get_watermark_for_write not found"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
