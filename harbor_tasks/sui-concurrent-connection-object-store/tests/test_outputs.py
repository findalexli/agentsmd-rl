"""
Test suite for ObjectStoreConnection ConcurrentConnection implementation.

These tests verify that:
1. The ConcurrentConnection trait methods are properly implemented (not just stubs)
2. The init_watermark method properly initializes watermarks
3. The code compiles and passes clippy checks
"""

import subprocess
import sys

REPO = "/workspace/sui"
CRATE = "sui-indexer-alt-object-store"


def run_cmd(cmd: list[str], cwd: str = REPO, timeout: int = 300) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return result.returncode, result.stdout, result.stderr


def test_cargo_check_compiles():
    """Verify that the crate compiles without errors."""
    rc, stdout, stderr = run_cmd(["cargo", "check", "-p", CRATE])
    output = stdout + stderr
    assert rc == 0, f"cargo check failed:\n{output[-2000:]}"


def test_existing_watermark_operations():
    """
    Run the existing test_watermark_operations test.
    This test exists in both base and fixed versions.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_watermark_operations", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr
    assert rc == 0, f"test_watermark_operations failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_reader_watermark_exists_and_passes():
    """
    Test that reader_watermark_roundtrip test exists and passes.

    Before fix: This test doesn't exist.
    After fix: Test exists and verifies reader_watermark returns actual data.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_reader_watermark_roundtrip", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    # If test doesn't exist, we get "running 0 tests"
    if "running 0 tests" in output:
        # The test doesn't exist yet - this means the fix hasn't been applied
        assert False, "test_reader_watermark_roundtrip doesn't exist - fix not applied"

    assert rc == 0, f"test_reader_watermark_roundtrip failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_pruner_watermark_exists_and_passes():
    """
    Test that pruner_watermark tests exist and pass.

    Before fix: pruner_watermark returns Ok(None).
    After fix: Returns actual data with proper wait_for_ms calculation.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_pruner_watermark_wait_for_ms", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        assert False, "test_pruner_watermark_wait_for_ms doesn't exist - fix not applied"

    assert rc == 0, f"test_pruner_watermark_wait_for_ms failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_pruner_saturates_when_ready():
    """
    Test that pruner_watermark properly saturates when ready.

    Before fix: pruner_watermark returns Ok(None).
    After fix: Returns PrunerWatermark with wait_for_ms = 0 when ready.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_pruner_watermark_saturates_when_ready", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        assert False, "test_pruner_watermark_saturates_when_ready doesn't exist - fix not applied"

    assert rc == 0, f"test_pruner_watermark_saturates_when_ready failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_set_reader_watermark_works():
    """
    Test that set_reader_watermark returns Ok(true) instead of bailing.

    Before fix: bails with "Pruning not supported by this store".
    After fix: Updates watermark and returns Ok(true).
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_set_reader_watermark", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        # Try a different test name pattern
        rc2, stdout2, stderr2 = run_cmd(
            ["cargo", "test", "-p", CRATE, "test_reader_watermark_roundtrip", "--", "--nocapture"],
            timeout=180
        )
        output2 = stdout2 + stderr2
        if "running 0 tests" in output2:
            assert False, "set_reader_watermark tests don't exist - fix not applied"
        # If reader test exists, that's good enough - it tests the full roundtrip
        assert rc2 == 0, f"test_reader_watermark_roundtrip failed:\n{output2[-2000:]}"
        return

    assert rc == 0, f"set_reader_watermark test failed:\n{output[-2000:]}"


def test_set_pruner_watermark_works():
    """
    Test that set_pruner_watermark returns Ok(true) instead of bailing.

    Before fix: bails with "Pruning not supported by this store".
    After fix: Updates watermark and returns Ok(true).
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_set_pruner_watermark", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        assert False, "test_set_pruner_watermark doesn't exist - fix not applied"

    assert rc == 0, f"test_set_pruner_watermark failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_init_watermark_fresh():
    """
    Test that init_watermark creates fresh watermarks correctly.

    Before fix: init_watermark delegates to reader_watermark which returns None.
    After fix: init_watermark creates proper watermark with reader_lo = checkpoint + 1.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_init_watermark_fresh_with_checkpoint", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        assert False, "test_init_watermark_fresh_with_checkpoint doesn't exist - fix not applied"

    assert rc == 0, f"test_init_watermark_fresh_with_checkpoint failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_init_watermark_migrates_legacy():
    """
    Test that init_watermark properly migrates legacy format.

    Before fix: Legacy migration not implemented.
    After fix: Legacy watermarks are migrated to new format.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "test_init_watermark_migrates_legacy_format", "--", "--nocapture"],
        timeout=180
    )
    output = stdout + stderr

    if "running 0 tests" in output:
        assert False, "test_init_watermark_migrates_legacy_format doesn't exist - fix not applied"

    assert rc == 0, f"test_init_watermark_migrates_legacy_format failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-1000:]}"


def test_all_lib_tests_pass():
    """
    Run all library tests to ensure nothing is broken.
    Pass-to-pass test that should always pass.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "test", "-p", CRATE, "--lib"],
        timeout=300
    )
    output = stdout + stderr
    assert rc == 0, f"cargo test --lib failed:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Tests did not all pass:\n{output[-1000:]}"


def test_cargo_clippy():
    """
    Run cargo clippy to check for lint warnings.
    Pass-to-pass test that should always pass.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "clippy", "-p", CRATE, "--", "-D", "warnings"],
        timeout=300
    )
    output = stdout + stderr
    assert rc == 0, f"cargo clippy failed:\n{output[-2000:]}"


def test_cargo_fmt():
    """
    Run cargo fmt --check to verify code formatting.
    Pass-to-pass test that should always pass.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "fmt", "--check", "-p", CRATE],
        timeout=60
    )
    output = stdout + stderr
    assert rc == 0, f"cargo fmt --check failed (formatting issues):\n{output[-1000:]}"


def test_cargo_doc():
    """
    Run cargo doc to verify documentation builds without errors.
    Pass-to-pass test that should always pass.
    """
    rc, stdout, stderr = run_cmd(
        ["cargo", "doc", "-p", CRATE, "--no-deps"],
        timeout=300
    )
    output = stdout + stderr
    assert rc == 0, f"cargo doc failed:\n{output[-2000:]}"
