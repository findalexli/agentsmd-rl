"""
Test outputs for the wal3 AlreadyInitialized bug fix.

This task tests that the manifest manager correctly returns AlreadyInitialized
instead of LogContentionRetry when a Spanner insert hits AlreadyExists.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/chroma")
MANIFEST_MANAGER = REPO / "rust/wal3/src/interfaces/repl/manifest_manager.rs"
REPL_02_TEST = REPO / "rust/wal3/tests/repl_02_initialized_init_again.rs"
REPL_06_TEST = REPO / "rust/wal3/tests/repl_06_parallel_open_or_initialize.rs"


def test_manifest_manager_returns_already_initialized():
    """
    F2P: The manifest manager must return AlreadyInitialized, not LogContentionRetry,
    when a Spanner insert hits AlreadyExists.
    """
    content = MANIFEST_MANAGER.read_text()

    # Find the AlreadyExists error handling block
    # The fix changes: return Err(Error::LogContentionRetry);
    # to: return Err(Error::AlreadyInitialized);

    # Check that the file contains the correct error return
    # Look for the pattern where AlreadyExists code returns AlreadyInitialized
    lines = content.split('\n')
    found_already_exists_block = False
    correct_error_in_block = False

    for i, line in enumerate(lines):
        if 'status.code() == Code::AlreadyExists' in line:
            found_already_exists_block = True
            # Check the next few lines for the return statement
            for j in range(i, min(i + 5, len(lines))):
                if 'return Err(Error::AlreadyInitialized)' in lines[j]:
                    correct_error_in_block = True
                    break
                if 'return Err(Error::LogContentionRetry)' in lines[j]:
                    # Bug still present
                    assert False, (
                        f"Found LogContentionRetry in AlreadyExists block at line {j + 1}. "
                        f"Should be AlreadyInitialized."
                    )

    assert found_already_exists_block, "Could not find AlreadyExists error handling block"
    assert correct_error_in_block, (
        "The AlreadyExists block does not return Error::AlreadyInitialized"
    )


def test_repl_02_checks_already_initialized():
    """
    F2P: The repl_02 test should verify the exact error variant (AlreadyInitialized)
    instead of just checking is_err().
    """
    content = REPL_02_TEST.read_text()

    # The test should use matches!(result, Err(Error::AlreadyInitialized))
    assert 'matches!(result, Err(Error::AlreadyInitialized))' in content, (
        "Test should verify exact AlreadyInitialized error variant"
    )

    # Should not have the old generic error check
    assert 'result.is_err()' not in content, (
        "Test should not use generic is_err() check"
    )


def test_repl_06_parallel_init_test_exists():
    """
    F2P: The repl_06 test for concurrent open_or_initialize should exist.
    """
    assert REPL_06_TEST.exists(), (
        "repl_06_parallel_open_or_initialize.rs test file should exist"
    )

    content = REPL_06_TEST.read_text()

    # Verify the test has the key components
    assert 'test_k8s_mcmr_integration_repl_06_parallel_open_or_initialize' in content, (
        "Test function should be present"
    )
    assert 'open_or_initialize' in content, (
        "Test should call open_or_initialize"
    )
    assert 'num_writers = 32' in content or 'num_writers=32' in content, (
        "Test should have 32 concurrent writers"
    )


def test_wal3_cargo_check():
    """
    P2P: wal3 crate should pass cargo check.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "wal3"],
        cwd=REPO / "rust",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"cargo check failed:\n{result.stderr[-2000:]}"
    )


def test_wal3_cargo_clippy():
    """
    P2P: wal3 crate should pass cargo clippy.
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "wal3", "--", "-D", "warnings"],
        cwd=REPO / "rust",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"cargo clippy failed:\n{result.stderr[-2000:]}"
    )


def test_wal3_code_compiles():
    """
    P2P: wal3 crate should compile without errors.
    """
    result = subprocess.run(
        ["cargo", "build", "-p", "wal3"],
        cwd=REPO / "rust",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"cargo build failed:\n{result.stderr[-2000:]}"
    )


def test_wal3_cargo_check_all_features():
    """
    P2P: wal3 crate should pass cargo check with all features enabled.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "wal3", "--all-features"],
        cwd=REPO / "rust",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, (
        f"cargo check --all-features failed:\n{result.stderr[-2000:]}"
    )


def test_repo_cargo_fmt():
    """
    P2P: All Rust code should pass cargo fmt check.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"cargo fmt check failed:\n{result.stderr[-500:]}"
    )


def test_wal3_cargo_metadata():
    """
    P2P: wal3 crate metadata should be valid and parseable.
    """
    result = subprocess.run(
        ["cargo", "metadata", "--manifest-path", str(REPO / "rust/wal3/Cargo.toml"), "--format-version", "1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"cargo metadata failed:\n{result.stderr[-500:]}"
    )
