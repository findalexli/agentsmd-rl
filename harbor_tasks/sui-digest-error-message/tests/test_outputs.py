"""
Test outputs for sui-digest-error-message benchmark task.

This tests the improved error messages for Digest parsing from &str.
The PR refactors multiple digest types to use a shared digest_from_base58()
function that provides better error messages.
"""

import subprocess
import sys

REPO = "/workspace/sui"
DIGESTS_FILE = f"{REPO}/crates/sui-types/src/digests.rs"


def run_cargo_test(package: str, test_filter: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a specific cargo test in the given package."""
    cmd = ["cargo", "test", "-p", package, "--lib"]
    if test_filter:
        # Use filter without --exact to allow module prefix matching
        cmd.extend(["--", test_filter])

    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def test_digest_from_base58_exists():
    """
    F2P: The digest_from_base58 helper function must exist.
    This function centralizes the logic for parsing digests from base58 strings.
    """
    result = subprocess.run(
        ["grep", "-q", "fn digest_from_base58", DIGESTS_FILE],
        capture_output=True
    )
    assert result.returncode == 0, "digest_from_base58 function not found in digests.rs"


def test_digest_from_base58_eq_32():
    """
    F2P: digest_from_base58 must accept valid 32-byte base58 strings.
    A string of 32 '1's in base58 decodes to 32 zero bytes.
    """
    result = run_cargo_test("sui-types", "test_digest_from_base58_eq_32", timeout=300)
    output = result.stdout + result.stderr

    # Must have return code 0 and at least 1 test passed
    # On base commit, the test doesn't exist so we get "0 passed"
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}"
    assert "1 passed" in output, f"Expected exactly 1 test passed (test must exist and pass), got:\n{output}"


def test_digest_from_base58_lt_32():
    """
    F2P: digest_from_base58 must reject strings decoding to < 32 bytes.
    Error message should include the actual decoded length and the input string.
    """
    result = run_cargo_test("sui-types", "test_digest_from_base58_lt_32", timeout=300)
    output = result.stdout + result.stderr

    # Must have return code 0 and at least 1 test passed
    # On base commit, the test doesn't exist so we get "0 passed"
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}"
    assert "1 passed" in output, f"Expected exactly 1 test passed (test must exist and pass), got:\n{output}"


def test_digest_from_base58_gt_32():
    """
    F2P: digest_from_base58 must reject strings decoding to > 32 bytes.
    Error message should include the truncated input and actual decoded length.
    """
    result = run_cargo_test("sui-types", "test_digest_from_base58_gt_32", timeout=300)
    output = result.stdout + result.stderr

    # Must have return code 0 and at least 1 test passed
    # On base commit, the test doesn't exist so we get "0 passed"
    assert result.returncode == 0, f"Test failed:\n{result.stderr[-1000:]}"
    assert "1 passed" in output, f"Expected exactly 1 test passed (test must exist and pass), got:\n{output}"


def test_cargo_check():
    """
    P2P: The code must pass cargo check (compilation test).
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo check failed:\n{result.stderr[-1000:]}"


def test_unit_tests_pass():
    """
    P2P: All unit tests in the sui-types crate must pass.
    """
    result = run_cargo_test("sui-types", timeout=300)
    assert result.returncode == 0, \
        f"Unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"
