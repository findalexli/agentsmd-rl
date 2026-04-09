#!/usr/bin/env python3
"""Tests for the Sui jsonrpc_index fix.

This verifies that accumulator event addresses are now included in the
transactions_to_addr index so that queryTransactionBlocks with ToAddress
returns transactions involving address balance transfers.
"""

import subprocess
import sys

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-core/src/jsonrpc_index.rs"


def test_accumulator_events_included_in_index():
    """FAIL-TO-PASS: Verify accumulator_events are chained into affected_addresses.

    The fix chains accumulator_events.iter().map(...) into the affected_addresses
    iterator that populates transactions_to_addr. Before the fix, only
    mutated_objects were indexed, missing address balance transfers via
    accumulator events.
    """
    filepath = f"{REPO}/{TARGET_FILE}"
    with open(filepath, 'r') as f:
        content = f.read()

    # Check that the fix is present: accumulator_events should be chained
    # with the mutated_objects to form affected_addresses
    assert "affected_addresses" in content, "Missing 'affected_addresses' variable - fix not applied"
    assert "accumulator_events" in content, "Missing 'accumulator_events' reference - fix not applied"

    # Verify the chain pattern - both mutated_objects filter_map and accumulator_events
    # should be combined to create affected_addresses
    assert ".chain(" in content, "Missing .chain() call to combine iterators - fix not applied"

    # Verify that affected_addresses is used for transactions_to_addr insertion
    assert "batch.insert_batch(&self.tables.transactions_to_addr, affected_addresses)" in content, \
        "affected_addresses not used for transactions_to_addr insertion - fix not applied"


def test_cargo_check_sui_core():
    """PASS-TO-PASS: Verify sui-core compiles without errors."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_cargo_check_sui_json_rpc_tests():
    """PASS-TO-PASS: Verify sui-json-rpc-tests compiles without errors."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-json-rpc-tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_jsonrpc_index_syntax():
    """PASS-TO-PASS: Verify jsonrpc_index.rs has valid Rust syntax."""
    filepath = f"{REPO}/{TARGET_FILE}"

    # Check that the file is valid Rust by looking for expected structures
    with open(filepath, 'r') as f:
        content = f.read()

    # Basic syntax checks
    assert content.count('{') > 0, "Missing opening braces"
    assert content.count('}') > 0, "Missing closing braces"
    assert "impl IndexStore" in content, "Missing IndexStore impl block"


def test_index_tx_method_present():
    """PASS-TO-PASS: Verify the IndexStore::index_tx method exists."""
    filepath = f"{REPO}/{TARGET_FILE}"
    with open(filepath, 'r') as f:
        content = f.read()

    assert "pub fn index_tx(" in content, \
        "Missing index_tx method"
    assert "transactions_to_addr" in content, \
        "Missing transactions_to_addr table reference"
    assert "accumulator_events" in content, \
        "Missing accumulator_events parameter"


def test_transactions_to_addr_indexing_logic():
    """FAIL-TO-PASS: Verify transactions_to_addr includes both mutated_objects and accumulator_events.

    Before the fix, only mutated_objects were used to populate transactions_to_addr.
    After the fix, both mutated_objects (via filter_map) and accumulator_events
    (via .chain().map()) should be included.
    """
    filepath = f"{REPO}/{TARGET_FILE}"
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the section dealing with transactions_to_addr
    # After fix, we should see affected_addresses being defined with .chain()
    # combining both mutated_objects and accumulator_events

    # Check that the new pattern exists: affected_addresses combined iterator
    if "let affected_addresses" in content:
        # The fix has been applied
        # Verify both sources are in the chain
        chain_section = content[content.find("let affected"):content.find("batch.insert_batch(&self.tables.transactions_to_addr")]
        assert ".chain(" in chain_section, "Missing .chain() in affected_addresses definition"
        assert "accumulator_events" in chain_section, "Missing accumulator_events in chain"
        assert "mutated_objects" in chain_section, "Missing mutated_objects in chain"
    else:
        # The old pattern - only mutated_objects, no affected_addresses variable
        # This should fail when the fix is not applied
        to_addr_section = content.split("transactions_to_addr")[1] if "transactions_to_addr" in content else ""
        # Check if it's using the old pattern (direct insert_batch without affected_addresses variable)
        assert "affected_addresses" in content, \
            "The fix has not been applied: affected_addresses variable not found"


def test_cargo_fmt():
    """PASS-TO-PASS: Verify code formatting passes (cargo fmt --check)."""
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"cargo fmt --check failed:\n{result.stderr[-1000:] or result.stdout[-1000:]}"


def test_cargo_clippy_sui_core():
    """PASS-TO-PASS: Verify clippy lints pass for sui-core crate."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "sui-core", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_cargo_xlint():
    """PASS-TO-PASS: Verify license header check passes (cargo xlint)."""
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"cargo xlint failed:\n{result.stderr[-1000:] or result.stdout[-1000:]}"


def test_git_checks():
    """PASS-TO-PASS: Verify git checks script passes."""
    result = subprocess.run(
        ["bash", "scripts/git-checks.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"git-checks.sh failed:\n{result.stderr[-1000:] or result.stdout[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
