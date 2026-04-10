#!/usr/bin/env python3
"""Tests for verifying removal of unused SequentialStore::sequential_connect function."""

import subprocess
import re

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-indexer-alt-framework-store-traits/src/lib.rs"

def test_compilation_after_removal():
    """Verify the crate compiles after removing the unused function (fail-to-pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework-store-traits"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr[-1000:]}"

def test_sequential_connect_function_removed():
    """Verify SequentialStore::sequential_connect function has been removed (fail-to-pass)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check that the distinctive error context string is removed
    assert "Failed to establish sequential connection to store" not in content, \
        "The sequential_connect function was not removed - distinctive error message still exists"

    # Check that the function signature is removed
    assert "async fn sequential_connect" not in content, \
        "The sequential_connect function signature still exists"

def test_unused_import_removed():
    """Verify unused anyhow::Context import has been removed (fail-to-pass)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # The import line 'use anyhow::Context;' should be removed
    # But we need to be careful - there might be other uses of Context in the file
    # Check if Context is used anywhere else in the file
    context_usages = re.findall(r'\.context\(|\.with_context\(', content, re.IGNORECASE)

    # If no .context() or .with_context() calls exist, the import should be removed
    if not context_usages:
        lines = content.split('\n')
        for line in lines:
            if line.strip() == "use anyhow::Context;":
                assert False, "Unused anyhow::Context import was not removed"

def test_transaction_method_still_present():
    """Verify the transaction method still exists (structural sanity check)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    assert "async fn transaction" in content, \
        "The transaction method should still exist but was not found"

def test_sequential_store_trait_intact():
    """Verify the SequentialStore trait definition is still intact (pass-to-pass)."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check that the trait is still defined
    assert "pub trait SequentialStore" in content, \
        "SequentialStore trait definition not found"

    # Check that SequentialConnection associated type still exists
    assert "type SequentialConnection" in content, \
        "SequentialConnection associated type missing"

    # Check that Store trait bound still exists (it's a higher-ranked trait bound with for<'c>)
    assert "Store<Connection<'c> = Self::SequentialConnection<'c>>" in content, \
        "Store trait bound missing"

def test_cargo_check_entire_indexer():
    """Run cargo check on the broader indexer crates to ensure no breakage (pass-to-pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework", "-p", "sui-indexer-alt"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    # This is informational - may fail due to other issues, but shouldn't fail due to our change
    # We mainly care that it doesn't fail because of the removed function
    if result.returncode != 0:
        # Check if the error is specifically about sequential_connect
        if "sequential_connect" in result.stderr:
            assert False, f"sequential_connect removal broke dependent crates:\n{result.stderr[-500:]}"


def test_cargo_clippy():
    """Repo's clippy passes on the modified crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-indexer-alt-framework-store-traits", "--all-targets", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


def test_cargo_doc():
    """Repo's doc generation passes on the modified crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "-p", "sui-indexer-alt-framework-store-traits", "--no-deps"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Doc generation failed:\n{r.stderr[-1000:]}"


def test_cargo_fmt():
    """Repo's formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test():
    """Repo's unit tests for the modified crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "sui-indexer-alt-framework-store-traits", "--", "--test-threads=1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


def test_repo_cargo_xlint():
    """Repo's custom xlint (license check) passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"xlint check failed:\n{r.stderr[-500:]}"
