"""
Test suite for Sui cleanup PR #26086: remove unused fields and no-op flag.
Tests the core behavioral changes in transaction parsing logic.
"""

import subprocess
import sys
from pathlib import Path

# Path to the cloned Sui repository
REPO = Path("/workspace/sui")


def run_cargo_check():
    """Run cargo check to verify the code compiles."""
    result = subprocess.run(
        ["cargo", "check", "-p", "consensus-core", "-p", "sui-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode == 0, result.stdout + result.stderr


# =============================================================================
# PASS_TO_PASS TESTS - Repo CI/CD checks that must pass on both base and fix
# =============================================================================


def test_p2p_cargo_check_consensus_config():
    """
    Pass-to-pass: cargo check on consensus-config crate.
    This crate is part of the consensus module modified in the PR.
    """
    # Install libclang-dev which is required for rocksdb compilation
    install_result = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    install_result = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "libclang-dev"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["cargo", "check", "-p", "consensus-config"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"cargo check consensus-config failed:\n{result.stderr[-1000:]}"


def test_p2p_cargo_check_consensus_core():
    """
    Pass-to-pass: cargo check on consensus-core crate.
    This is the main consensus crate being modified in the PR.
    """
    # Install libclang-dev which is required for rocksdb compilation
    install_result = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    install_result = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "libclang-dev"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["cargo", "check", "-p", "consensus-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"cargo check consensus-core failed:\n{result.stderr[-1000:]}"


def test_p2p_cargo_check_sui_core():
    """
    Pass-to-pass: cargo check on sui-core crate.
    This crate depends on the consensus changes and must compile.
    """
    # Install libclang-dev which is required for rocksdb compilation
    install_result = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    install_result = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "libclang-dev"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    result = subprocess.run(
        ["cargo", "check", "-p", "sui-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert result.returncode == 0, f"cargo check sui-core failed:\n{result.stderr[-1000:]}"


def test_parse_block_transactions_logic():
    """
    Test that parse_block_transactions correctly rejects user transactions
    but always accepts system transactions.

    This is the core behavioral change: previously the function had a parameter
    always_accept_system_transactions, now system transactions are always accepted.
    """
    # Read the consensus_output_api.rs file
    api_file = REPO / "crates/sui-core/src/consensus_types/consensus_output_api.rs"
    assert api_file.exists(), f"File not found: {api_file}"

    content = api_file.read_text()

    # Check for the correct rejection logic
    assert (
        "transaction.is_user_transaction() && rejected_transaction_indices.contains"
        in content
    ), "parse_block_transactions should reject user transactions only when in rejected set"

    # Check that always_accept_system_transactions parameter was removed
    assert (
        "always_accept_system_transactions" not in content
    ), "always_accept_system_transactions should be removed from consensus_output_api.rs"

    # Check the comment explains the behavior
    assert (
        "System transactions are always accepted" in content
    ), "Comment should explain that system transactions are always accepted"


def test_committed_subdag_no_always_accept_field():
    """
    Test that CommittedSubDag no longer has the always_accept_system_transactions field.
    """
    commit_file = REPO / "consensus/core/src/commit.rs"
    assert commit_file.exists(), f"File not found: {commit_file}"

    content = commit_file.read_text()

    # Check the field was removed from the struct
    assert (
        "always_accept_system_transactions: bool" not in content
    ), "CommittedSubDag should not have always_accept_system_transactions field"

    # Check the new() function doesn't take the parameter
    # Look for the function signature after change (no always_accept parameter)
    struct_new_section = content.split("impl CommittedSubDag {", 1)[1].split("}", 1)[0]
    assert (
        "always_accept_system_transactions" not in struct_new_section
    ), "CommittedSubDag::new() should not accept always_accept_system_transactions parameter"


def test_consensus_protocol_config_no_field():
    """
    Test that ConsensusProtocolConfig no longer has always_accept_system_transactions field.
    """
    config_file = REPO / "consensus/config/src/consensus_protocol_config.rs"
    assert config_file.exists(), f"File not found: {config_file}"

    content = config_file.read_text()

    # Check the field was removed
    assert (
        "always_accept_system_transactions" not in content
    ), "ConsensusProtocolConfig should not have always_accept_system_transactions field"


def test_load_committed_subdag_no_context_param():
    """
    Test that load_committed_subdag_from_store no longer takes context parameter.
    """
    commit_file = REPO / "consensus/core/src/commit.rs"
    assert commit_file.exists(), f"File not found: {commit_file}"

    content = commit_file.read_text()

    # Find the function signature
    func_match = "pub(crate) fn load_committed_subdag_from_store("
    func_start = content.find(func_match)
    assert func_match in content, "load_committed_subdag_from_store function not found"

    # Get the function signature (first few lines after the name)
    func_section = content[func_start:func_start + 500]

    # Should NOT have context: &Arc<Context> parameter
    assert (
        "context: &Arc<Context>" not in func_section
    ), "load_committed_subdag_from_store should not take context parameter"


def test_unused_imports_removed():
    """
    Test that unused imports were cleaned up in authority.rs and commit.rs.
    """
    # Check authority.rs - Event import should be removed (keeping EventID)
    authority_file = REPO / "crates/sui-core/src/authority.rs"
    assert authority_file.exists(), f"File not found: {authority_file}"

    authority_content = authority_file.read_text()

    # Look for the imports section around line 138
    assert (
        "use sui_types::event::EventID;" in authority_content
    ), "EventID should still be imported"

    # Check that `Event` alone is not imported (removed from the import)
    # The import should be just EventID, not {Event, EventID}
    event_import_line = None
    for line in authority_content.split("\n"):
        if "sui_types::event" in line:
            event_import_line = line
            break

    assert event_import_line is not None, "event import line should exist"
    assert (
        "Event," not in event_import_line and "Event}" not in event_import_line
    ), "Event import should be removed, keeping only EventID"

    # Check commit.rs - Context import should be removed from use crate statement
    commit_file = REPO / "consensus/core/src/commit.rs"
    content = commit_file.read_text()

    # The use crate statement should not include Context
    use_crate_section = content.split("use crate::{", 1)[1].split("};", 1)[0]
    assert (
        "context::Context" not in use_crate_section
    ), "Context import should be removed from use crate in commit.rs"


def test_compilation():
    """
    Verify the code compiles successfully after changes.
    """
    success, output = run_cargo_check()
    assert success, f"Code should compile successfully:\n{output}"


def test_unused_events_column_family_removed():
    """
    Test that the unused deprecated 'events' column family was removed
    from AuthorityPerpetualTables.
    """
    tables_file = REPO / "crates/sui-core/src/authority/authority_store_tables.rs"
    assert tables_file.exists(), f"File not found: {tables_file}"

    content = tables_file.read_text()

    # Check that the deprecated events field was removed
    assert (
        "events: DBMap<(TransactionEventsDigest, usize), Event>" not in content
    ), "Deprecated events column family should be removed"

    # Verify events_2 still exists (the replacement)
    assert (
        "events_2: DBMap<TransactionDigest, TransactionEvents>" in content
    ), "events_2 column family should still exist"
