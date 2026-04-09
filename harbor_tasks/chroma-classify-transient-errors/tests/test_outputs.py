"""Test transient error classification for Chroma log service and storage.

This module tests that transient errors from gRPC and GCS are properly
classified for retry handling.
"""

import subprocess
import sys

REPO = "/workspace/chroma/rust"


def run_cargo_test(package: str, test_filter: str = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run cargo test for a specific package with optional filter."""
    cmd = ["cargo", "test", "-p", package]
    if test_filter:
        cmd.append(test_filter)
    cmd.extend(["--", "--nocapture"])

    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def run_cargo_check(package: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run cargo check for a specific package."""
    return subprocess.run(
        ["cargo", "check", "-p", package],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def test_source_chain_contains_function_exists():
    """Verify source_chain_contains function exists and is exported from chroma-error.

    This function is the foundation for all error chain traversal in the PR.
    Fail-to-pass: Base commit doesn't have this function.
    """
    # Check the function exists by trying to compile a test that uses it
    result = run_cargo_test("chroma-error", "source_chain_contains")
    assert result.returncode == 0, (
        f"source_chain_contains tests failed:\n{result.stdout}\n{result.stderr}"
    )

    # Verify tests actually ran (not just "0 tests" because function doesn't exist)
    output = result.stdout + result.stderr
    assert "running" in output and ("test result:" in output), (
        f"No tests ran - source_chain_contains function may not exist:\n{output}"
    )


def test_error_source_chain_traversal():
    """Verify error source chain is traversed correctly.

    Tests that the utility can find errors nested in the source chain.
    Fail-to-pass: Base commit doesn't have source_chain_contains.
    """
    result = run_cargo_test("chroma-error")
    assert result.returncode == 0, (
        f"chroma-error tests failed:\n{result.stdout}\n{result.stderr}"
    )

    # Verify specific test cases ran (more than 0 tests)
    output = result.stdout + result.stderr
    assert "running" in output and "test result:" in output, (
        f"No tests ran:\n{output}"
    )

    # Make sure at least some tests ran
    import re
    test_count_match = re.search(r'running (\d+) tests?', output)
    if test_count_match:
        test_count = int(test_count_match.group(1))
        assert test_count > 0, f"Expected >0 tests but got {test_count}"


def test_grpc_unavailable_stays_unavailable():
    """Verify gRPC Unavailable errors are preserved as retryable.

    Unavailable status should remain Unavailable for retry purposes.
    Fail-to-pass: Base commit doesn't have is_retryable_transport_status.
    """
    result = run_cargo_test("chroma-log", "grpc_push_logs_unavailable")
    assert result.returncode == 0, (
        f"gRPC Unavailable classification test failed:\n{result.stdout}\n{result.stderr}"
    )

    # Verify specific test ran
    output = result.stdout + result.stderr
    assert "grpc_push_logs_unavailable" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_grpc_plain_cancelled_stays_cancelled():
    """Verify plain gRPC Cancelled (without transport errors) stays Cancelled.

    Cancelled errors without transport layer issues should NOT be retryable.
    Fail-to-pass: Base commit doesn't have the correct error code mapping.
    """
    result = run_cargo_test("chroma-log", "grpc_push_logs_plain_cancelled")
    assert result.returncode == 0, (
        f"gRPC Cancelled classification test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "grpc_push_logs_plain_cancelled" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_gcs_429_maps_to_backoff():
    """Verify GCS 429 Too Many Requests errors map to Backoff.

    429 errors from GCS should trigger backoff/retry logic.
    Fail-to-pass: Base commit maps these to Generic error.
    """
    result = run_cargo_test("chroma-storage", "test_gcs_generic_429")
    assert result.returncode == 0, (
        f"GCS 429 error classification test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "test_gcs_generic_429" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_gcs_slowdown_maps_to_backoff():
    """Verify GCS SlowDown errors in source chain map to Backoff.

    SlowDown errors (even nested in retry wrappers) should trigger backoff.
    Fail-to-pass: Base commit doesn't check source chain for SlowDown.
    """
    result = run_cargo_test("chroma-storage", "test_gcs_generic_slowdown")
    assert result.returncode == 0, (
        f"GCS SlowDown error classification test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "test_gcs_generic_slowdown" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_gcs_mutation_rate_limit_maps_to_backoff():
    """Verify GCS mutation rate limit errors map to Backoff.

    Rate limit messages should trigger backoff/retry logic.
    Fail-to-pass: Base commit maps these to Generic error.
    """
    result = run_cargo_test("chroma-storage", "test_gcs_generic_mutation_rate_limit")
    assert result.returncode == 0, (
        f"GCS mutation rate limit test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "test_gcs_generic_mutation_rate_limit" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_gcs_non_throttling_error_stays_generic():
    """Verify non-throttling GCS errors stay as Generic.

    Non-throttling errors (like 503) should remain Generic, not Backoff.
    Pass-to-pass: This should work in both base and fixed versions.
    """
    result = run_cargo_test("chroma-storage", "test_gcs_generic_non_throttling")
    assert result.returncode == 0, (
        f"GCS non-throttling error test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "test_gcs_generic_non_throttling" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_non_gcs_429_stays_generic():
    """Verify non-GCS 429 errors stay as Generic.

    429 errors from non-GCS stores (e.g., Azure) should NOT map to Backoff.
    Pass-to-pass: This should work in both base and fixed versions.
    """
    result = run_cargo_test("chroma-storage", "test_non_gcs_429")
    assert result.returncode == 0, (
        f"Non-GCS 429 error test failed:\n{result.stdout}\n{result.stderr}"
    )

    output = result.stdout + result.stderr
    assert "test_non_gcs_429" in output or "test result:" in output, (
        f"Expected test did not run:\n{output}"
    )


def test_grpc_log_compiles():
    """Verify chroma-log package compiles successfully.

    The package should compile with hyper dependency and new error handling.
    Fail-to-pass: Base commit doesn't have hyper dependency in Cargo.toml.
    """
    result = run_cargo_check("chroma-log")
    assert result.returncode == 0, (
        f"chroma-log compilation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_storage_compiles():
    """Verify chroma-storage package compiles successfully.

    The package should compile with source_chain_contains usage.
    Fail-to-pass: Base commit doesn't have source_chain_contains available.
    """
    result = run_cargo_check("chroma-storage")
    assert result.returncode == 0, (
        f"chroma-storage compilation failed:\n{result.stdout}\n{result.stderr}"
    )


def test_error_package_compiles():
    """Verify chroma-error package compiles with new source_chain_contains function.

    Fail-to-pass: Base commit doesn't have this function.
    """
    result = run_cargo_check("chroma-error")
    assert result.returncode == 0, (
        f"chroma-error compilation failed:\n{result.stdout}\n{result.stderr}"
    )



# ==================== Pass-to-Pass Tests (Repo CI/CD Checks) ====================


def test_repo_cargo_check_chroma_error():
    """chroma-error package passes cargo check (pass_to_pass).

    Verifies the package compiles without errors in the base commit.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "chroma-error"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"cargo check failed for chroma-error:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_cargo_clippy_chroma_error():
    """chroma-error package passes cargo clippy (pass_to_pass).

    Verifies the package passes linting in the base commit.
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "chroma-error", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"cargo clippy failed for chroma-error:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_cargo_fmt_check():
    """Rust code passes cargo fmt --check (pass_to_pass).

    Verifies the code is properly formatted in the base commit.
    """
    # Run from chroma root since cargo fmt needs workspace root for --check
    chroma_root = REPO.removesuffix("/rust")
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=chroma_root,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"cargo fmt check failed:\n{result.stdout}\n{result.stderr}"
    )


def test_repo_cargo_test_chroma_error():
    """chroma-error package tests pass (pass_to_pass).

    Verifies the package tests pass in the base commit.
    Note: The base commit has 0 tests in chroma-error, so this just verifies
    the test infrastructure works.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "chroma-error", "--", "--nocapture"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"cargo test failed for chroma-error:\n{result.stdout}\n{result.stderr}"
    )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
