"""Tests for sui-indexer-alt-object-store ConcurrentConnection implementation."""

import subprocess
import sys
import os

REPO = "/workspace/sui"
CRATE = "sui-indexer-alt-object-store"


def run_cargo_test(test_filter: str = None, timeout: int = 300) -> tuple[bool, str]:
    """Run cargo test on the crate and return success status and output."""
    cmd = ["cargo", "test", "-p", CRATE, "--lib"]
    if test_filter:
        cmd.extend(["--", test_filter])

    env = os.environ.copy()
    env["RUST_BACKTRACE"] = "1"

    try:
        result = subprocess.run(
            cmd,
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Test timed out after {timeout}s"
    except Exception as e:
        return False, f"Error running test: {e}"


def run_cargo_check(timeout: int = 180) -> tuple[bool, str]:
    """Run cargo check on the crate."""
    cmd = ["cargo", "check", "-p", CRATE]

    try:
        result = subprocess.run(
            cmd,
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Check timed out after {timeout}s"
    except Exception as e:
        return False, f"Error running check: {e}"


def test_compilation():
    """Test that the code compiles successfully."""
    success, output = run_cargo_check()
    assert success, f"Compilation failed:\n{output}"


def test_comitter_watermark_operations():
    """Test committer watermark operations - basic watermark lifecycle."""
    success, output = run_cargo_test("test_watermark_operations", timeout=120)
    assert success, f"Committer watermark test failed:\n{output}"


def test_init_watermark_fresh_with_checkpoint():
    """Test init_watermark creates new watermark with checkpoint value."""
    success, output = run_cargo_test("test_init_watermark_fresh_with_checkpoint", timeout=60)
    assert success, f"Init watermark with checkpoint test failed:\n{output}"


def test_init_watermark_fresh_without_checkpoint():
    """Test init_watermark creates new watermark without checkpoint value."""
    success, output = run_cargo_test("test_init_watermark_fresh_without_checkpoint", timeout=60)
    assert success, f"Init watermark without checkpoint test failed:\n{output}"


def test_init_watermark_reads_new_format():
    """Test init_watermark correctly reads new format watermark."""
    success, output = run_cargo_test("test_init_watermark_reads_new_format", timeout=60)
    assert success, f"Init watermark reads new format test failed:\n{output}"


def test_init_watermark_reads_legacy_format():
    """Test init_watermark correctly reads legacy format watermark."""
    success, output = run_cargo_test("test_init_watermark_reads_legacy_format", timeout=60)
    assert success, f"Init watermark reads legacy format test failed:\n{output}"


def test_init_watermark_migrates_legacy_format():
    """Test init_watermark migrates legacy format to new format."""
    success, output = run_cargo_test("test_init_watermark_migrates_legacy_format", timeout=60)
    assert success, f"Init watermark migrates legacy format test failed:\n{output}"


def test_init_watermark_does_not_rewrite_new_format():
    """Test init_watermark doesn't rewrite already-migrated watermarks."""
    success, output = run_cargo_test("test_init_watermark_does_not_rewrite_new_format", timeout=60)
    assert success, f"Init watermark does not rewrite new format test failed:\n{output}"


def test_init_watermark_returns_existing_on_conflict():
    """Test init_watermark returns existing values when watermark already exists."""
    success, output = run_cargo_test("test_init_watermark_returns_existing_on_conflict", timeout=60)
    assert success, f"Init watermark returns existing on conflict test failed:\n{output}"


def test_reader_watermark_roundtrip():
    """Test reader_watermark returns values and set_reader_watermark updates them."""
    success, output = run_cargo_test("test_reader_watermark_roundtrip", timeout=60)
    assert success, f"Reader watermark roundtrip test failed:\n{output}"


def test_pruner_watermark_wait_calculation():
    """Test pruner_watermark calculates wait_for_ms correctly."""
    success, output = run_cargo_test("test_pruner_watermark_wait_for_ms", timeout=60)
    assert success, f"Pruner watermark wait calculation test failed:\n{output}"


def test_set_pruner_watermark():
    """Test set_pruner_watermark updates pruner_hi correctly."""
    success, output = run_cargo_test("test_set_pruner_watermark", timeout=60)
    assert success, f"Set pruner watermark test failed:\n{output}"


def test_pruner_watermark_saturates_when_ready():
    """Test pruner_watermark uses saturating_sub to avoid underflow."""
    success, output = run_cargo_test("test_pruner_watermark_saturates_when_ready", timeout=60)
    assert success, f"Pruner watermark saturates when ready test failed:\n{output}"


def test_pruner_watermark_overflow_handling():
    """Test pruner_watermark handles overflow errors correctly."""
    success, output = run_cargo_test("test_pruner_watermark_overflow", timeout=60)
    assert success, f"Pruner watermark overflow handling test failed:\n{output}"


def test_all_unit_tests():
    """Run all unit tests in the crate to ensure nothing is broken."""
    success, output = run_cargo_test(timeout=300)
    assert success, f"All unit tests failed:\n{output}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
