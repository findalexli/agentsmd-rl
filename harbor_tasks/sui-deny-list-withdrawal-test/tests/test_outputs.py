#!/usr/bin/env python3
"""Test outputs for Sui deny list withdrawal test task."""

import subprocess
import os

REPO = "/workspace/sui"
TARGET_MOVE_FILE = "crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.move"
TARGET_SNAP_FILE = "crates/sui-adapter-transactional-tests/tests/deny_list_v2/coin_deny_and_undeny_address_balance_receiver.snap"


def test_move_file_has_withdrawal_test():
    """The Move test file contains the withdrawal from denied address test case."""
    move_path = os.path.join(REPO, TARGET_MOVE_FILE)
    with open(move_path, 'r') as f:
        content = f.read()

    # Check for the distinctive test pattern: withdrawal from denied account B
    assert "withdraw funds from denied account B" in content, \
        "Missing withdrawal test comment"
    assert "sui::balance::redeem_funds" in content, \
        "Missing redeem_funds call in test"

    # Check for create-checkpoint directive (added in PR)
    assert "//# create-checkpoint" in content, \
        "Missing create-checkpoint directive"


def test_move_file_task_count():
    """The Move test file should have the correct number of tasks (13 after fix)."""
    move_path = os.path.join(REPO, TARGET_MOVE_FILE)
    with open(move_path, 'r') as f:
        content = f.read()

    # Count the number of task directives (//# lines)
    task_lines = [line for line in content.split('\n') if line.strip().startswith('//#')]

    # The patch adds 2 new tasks: create-checkpoint and the withdrawal test
    # Original had 11 tasks, new should have 13
    assert len(task_lines) >= 13, f"Expected at least 13 tasks, found {len(task_lines)}"


def test_move_file_task_ordering():
    """The Move test file has tasks in correct order with withdrawal test after checkpoint."""
    move_path = os.path.join(REPO, TARGET_MOVE_FILE)
    with open(move_path, 'r') as f:
        content = f.read()

    # Find the positions of key directives
    checkpoint_pos = content.find("//# create-checkpoint")
    withdrawal_pos = content.find("withdraw funds from denied account B")
    undeny_pos = content.find("deny_list_v2_remove")

    assert checkpoint_pos > 0, "create-checkpoint not found"
    assert withdrawal_pos > 0, "withdrawal test not found"
    assert undeny_pos > 0, "undeny (deny_list_v2_remove) not found"

    # Withdrawal test should come after checkpoint and before undeny
    assert checkpoint_pos < withdrawal_pos < undeny_pos, \
        "Tasks not in correct order: checkpoint < withdrawal < undeny"


def test_move_file_withdrawal_sender():
    """The withdrawal test uses sender B (the denied address)."""
    move_path = os.path.join(REPO, TARGET_MOVE_FILE)
    with open(move_path, 'r') as f:
        content = f.read()

    # Find the withdrawal test block
    lines = content.split('\n')
    found_sender_b = False
    for i, line in enumerate(lines):
        if "withdraw funds from denied account B" in line:
            # Check the programmable directive before it uses sender B
            for j in range(max(0, i-3), i):
                if "//# programmable" in lines[j] and "--sender B" in lines[j]:
                    found_sender_b = True
                    break
            break

    assert found_sender_b, "Withdrawal test should use --sender B"


def test_snapshot_file_updated():
    """The snapshot file reflects the new test cases."""
    snap_path = os.path.join(REPO, TARGET_SNAP_FILE)
    with open(snap_path, 'r') as f:
        content = f.read()

    # Should show 13 tasks processed (not 11)
    assert "processed 13 tasks" in content, \
        "Snapshot not updated to show 13 tasks"


def test_snapshot_has_withdrawal_error():
    """The snapshot shows the withdrawal denial error message."""
    snap_path = os.path.join(REPO, TARGET_SNAP_FILE)
    with open(snap_path, 'r') as f:
        content = f.read()

    # The new test should produce an error about address B being denied for withdrawal
    assert "Address @B is denied for coin" in content, \
        "Snapshot missing the withdrawal denial error for address B"


def test_snapshot_task_numbering():
    """The snapshot has correct task numbering for new tasks."""
    snap_path = os.path.join(REPO, TARGET_SNAP_FILE)
    with open(snap_path, 'r') as f:
        content = f.read()

    # Should show task 5 as create-checkpoint
    assert "task 5" in content and "create-checkpoint" in content, \
        "Snapshot missing task 5 create-checkpoint"

    # Should show task 8 as the withdrawal test
    assert "task 8" in content and "withdraw funds from denied account B" in content, \
        "Snapshot missing task 8 withdrawal test"


def test_snapshot_no_assertion_line():
    """The snapshot has the assertion_line removed (as per the PR)."""
    snap_path = os.path.join(REPO, TARGET_SNAP_FILE)
    with open(snap_path, 'r') as f:
        content = f.read()

    # The PR removes the assertion_line line
    assert "assertion_line:" not in content, \
        "Snapshot should not contain assertion_line (was removed in PR)"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks - ensure existing functionality works)
# =============================================================================

def test_move_workspace_compiles():
    """Move workspace compiles with cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--manifest-path", "external-crates/move/Cargo.toml", "-p", "move-transactional-test-runner"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Move workspace check failed:\n{r.stderr[-500:]}"


def test_move_workspace_clippy():
    """Move workspace passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--manifest-path", "external-crates/move/Cargo.toml", "-p", "move-core-types", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Move workspace clippy failed:\n{r.stderr[-500:]}"


def test_move_workspace_formatting():
    """Move workspace code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=60, cwd=os.path.join(REPO, "external-crates/move"),
    )
    assert r.returncode == 0, f"Move workspace formatting check failed:\n{r.stderr[-500:]}"


def test_move_core_types_compiles():
    """Move core types crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--manifest-path", "external-crates/move/Cargo.toml", "-p", "move-core-types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Move core types check failed:\n{r.stderr[-500:]}"


def test_sui_adapter_tx_tests_compiles():
    """Sui adapter transactional tests crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-adapter-transactional-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Sui adapter transactional tests check failed:\n{r.stderr[-500:]}"
