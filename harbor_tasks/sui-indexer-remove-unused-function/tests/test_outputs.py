"""Test outputs for sui-indexer-remove-unused-function task.

This task verifies that the unused SequentialStore::sequential_connect method
and the unused anyhow::Context import have been removed from the codebase.
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/sui")
TARGET_FILE = REPO / "crates" / "sui-indexer-alt-framework-store-traits" / "src" / "lib.rs"


def test_sequential_connect_removed():
    """FAIL-TO-PASS: The unused sequential_connect method must be removed."""
    content = TARGET_FILE.read_text()

    # The method should no longer exist in the file
    if "async fn sequential_connect" in content:
        raise AssertionError(
            "The unused 'sequential_connect' method still exists in SequentialStore trait. "
            "This vestigial function should be removed as it is no longer used anywhere in the codebase."
        )

    # Verify the distinctive error context message is gone
    if "Failed to establish sequential connection to store" in content:
        raise AssertionError(
            "The error message from sequential_connect still exists in the file."
        )


def test_context_import_removed():
    """FAIL-TO-PASS: The unused anyhow::Context import must be removed."""
    content = TARGET_FILE.read_text()

    # Check that Context import is not present (it was only used by sequential_connect)
    # We need to be careful not to match comments or other uses
    lines = content.split('\n')
    for line in lines:
        # Skip comments
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
            continue
        # Check for the import
        if 'use anyhow::Context;' in line:
            raise AssertionError(
                "The unused 'anyhow::Context' import still exists. "
                "This import was only used by the removed sequential_connect method and should be removed."
            )


def test_compiles():
    """PASS-TO-PASS: The crate must compile successfully after the changes."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework-store-traits"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        raise AssertionError(
            f"Code does not compile:\n{result.stderr[-1000:]}"
        )


def test_no_clippy_warnings():
    """PASS-TO-PASS: No clippy warnings should be present (especially dead_code/unused)."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "sui-indexer-alt-framework-store-traits", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        # Check specifically for dead_code or unused warnings related to our target
        stderr = result.stderr
        if "dead_code" in stderr or "unused" in stderr:
            raise AssertionError(
                f"Clippy found dead code or unused items:\n{stderr[-1000:]}"
            )
        # Other warnings are also failures due to -D warnings
        raise AssertionError(
            f"Clippy warnings found:\n{stderr[-1000:]}"
        )


def test_transaction_method_still_present():
    """SANITY CHECK: The transaction method should still exist after removing sequential_connect."""
    content = TARGET_FILE.read_text()

    # The transaction method that comes right after sequential_connect should still be there
    if "async fn transaction<'a, R, F>" not in content:
        raise AssertionError(
            "The 'transaction' method was accidentally removed. "
            "Only the sequential_connect method should be removed."
        )

    # The SequentialStore trait should still exist
    if "pub trait SequentialStore" not in content:
        raise AssertionError(
            "The SequentialStore trait was accidentally removed or renamed."
        )


def test_cargo_fmt():
    """PASS-TO-PASS: Code must be properly formatted (cargo fmt --check)."""
    result = subprocess.run(
        ["cargo", "fmt", "-p", "sui-indexer-alt-framework-store-traits", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Code is not properly formatted. Run `cargo fmt -p sui-indexer-alt-framework-store-traits` to fix:\n{result.stderr[-500:]}"
        )


def test_crate_unit_tests():
    """PASS-TO-PASS: Crate unit tests must pass."""
    result = subprocess.run(
        ["cargo", "test", "--lib", "-p", "sui-indexer-alt-framework-store-traits"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Unit tests failed:\n{result.stderr[-1000:]}"
        )
