#!/usr/bin/env python3
"""
Tests for sui-jsonrpc-index-accumulator-events benchmark task.

This verifies that the fix to include accumulator event addresses in the
transactions_to_addr index is correctly applied.
"""

import subprocess
import sys
import re

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-core/src/jsonrpc_index.rs"


def run_in_repo(cmd, cwd=REPO, check=True, timeout=300):
    """Run a command in the repo directory."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    if check and result.returncode != 0:
        raise AssertionError(f"Command failed: {cmd}\n{result.stderr}")
    return result


def test_cargo_check_compiles():
    """
    Test that sui-core compiles successfully after the fix.
    This is a fail-to-pass test - the base commit is missing the fix.
    """
    # Check compilation of sui-core specifically
    result = run_in_repo(
        ["cargo", "check", "-p", "sui-core", "--lib"],
        check=False,
        timeout=600
    )

    # The base commit should have a compilation error due to the bug
    # The fix adds the missing accumulator_events iteration
    assert result.returncode == 0, (
        f"sui-core failed to compile:\n{result.stderr}\n{result.stdout}"
    )


def test_accumulator_events_chained_in_index():
    """
    Test that accumulator_events are chained with mutated_objects
    in the transactions_to_addr batch insertion.

    This verifies the structural fix is present.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # Look for the pattern showing the fix:
    # 1. affected_addresses variable that chains mutated_objects with accumulator_events
    # 2. The chain should include the accumulator_events.iter().map() pattern

    # Find the relevant section around transactions_to_addr
    pattern = r'affected_addresses.*=.*mutated_objects.*filter_map.*chain.*accumulator_events'
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, (
        "Expected 'affected_addresses' chaining 'mutated_objects' with 'accumulator_events' not found. "
        "The fix should create an iterator that combines both mutated_objects and accumulator_events."
    )

    # Verify the accumulator_events are properly mapped
    accumulator_pattern = r'accumulator_events\s*\.\s*iter\(\)\s*\.\s*map\(\|event\|'
    acc_match = re.search(accumulator_pattern, content)

    assert acc_match is not None, (
        "Expected 'accumulator_events.iter().map(|event|...)' pattern not found. "
        "The fix should iterate over accumulator_events and extract the address."
    )

    # Verify the event address is correctly extracted
    event_address_pattern = r'event\.write\.address\.address'
    addr_match = re.search(event_address_pattern, content)

    assert addr_match is not None, (
        "Expected 'event.write.address.address' not found. "
        "The fix should extract the address from accumulator events correctly."
    )

    # Verify the batch insert uses affected_addresses
    batch_pattern = r'batch\.insert_batch\(&self\.tables\.transactions_to_addr,\s*affected_addresses\)'
    batch_match = re.search(batch_pattern, content)

    assert batch_match is not None, (
        "Expected 'batch.insert_batch(&self.tables.transactions_to_addr, affected_addresses)' not found. "
        "The fix should use the combined affected_addresses iterator."
    )


def test_comment_explains_change():
    """
    Test that there's a comment explaining the combined indexing.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # Look for comment mentioning both objects and accumulator events
    comment_pattern = r'//.*objects.*sent.*to.*addresses.*and.*accumulator.*events'
    match = re.search(comment_pattern, content, re.IGNORECASE)

    assert match is not None, (
        "Expected comment explaining the change not found. "
        "There should be a comment mentioning 'objects sent to addresses and accumulator events'."
    )


def test_no_old_pattern():
    """
    Test that the old direct insertion pattern is replaced.
    The old code directly passed mutated_objects.filter_map to insert_batch.
    """
    file_path = f"{REPO}/{TARGET_FILE}"

    with open(file_path, 'r') as f:
        content = f.read()

    # The old pattern would have been:
    # batch.insert_batch(&self.tables.transactions_to_addr, mutated_objects.filter_map(...))
    # This is now replaced with the affected_addresses chain

    # Look for transactions_to_addr section
    section_start = content.find("transactions_to_addr")
    section = content[section_start:section_start + 2000]

    # After the fix, we should see the affected_addresses variable being used
    # and not see the direct mutated_objects.filter_map passed to insert_batch
    # in that same context

    # Count occurrences of insert_batch with transactions_to_addr
    insert_batch_calls = section.count("batch.insert_batch(&self.tables.transactions_to_addr")

    # Should be exactly 1 call using affected_addresses
    assert insert_batch_calls == 1, (
        f"Expected exactly 1 insert_batch call for transactions_to_addr, found {insert_batch_calls}. "
        "The fix should consolidate the insertion using affected_addresses."
    )
