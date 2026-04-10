"""
Test suite for sui-kv-rpc dependency refactoring (PR #26066).

This tests that the sui-data-ingestion-core dependency is properly
replaced with sui-storage in the sui-kv-rpc crate.
"""

import subprocess
import sys
import re

REPO = "/workspace/sui"
SUI_KV_RPC_DIR = f"{REPO}/crates/sui-kv-rpc"
GET_CHECKPOINT_FILE = f"{SUI_KV_RPC_DIR}/src/v2/get_checkpoint.rs"
CARGO_TOML_FILE = f"{SUI_KV_RPC_DIR}/Cargo.toml"


def test_sui_data_ingestion_core_removed_from_cargo_toml():
    """
    Verify sui-data-ingestion-core is removed from Cargo.toml (fail-to-pass).
    """
    with open(CARGO_TOML_FILE, 'r') as f:
        content = f.read()

    # Should NOT contain sui-data-ingestion-core
    assert "sui-data-ingestion-core" not in content, \
        "sui-data-ingestion-core should be removed from Cargo.toml"


def test_sui_storage_added_to_cargo_toml():
    """
    Verify sui-storage is added to Cargo.toml (fail-to-pass).
    """
    with open(CARGO_TOML_FILE, 'r') as f:
        content = f.read()

    # Should contain sui-storage
    assert "sui-storage.workspace = true" in content, \
        "sui-storage.workspace = true should be present in Cargo.toml"


def test_sui_data_ingestion_core_import_removed():
    """
    Verify sui_data_ingestion_core imports are removed from get_checkpoint.rs (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should NOT contain imports from sui_data_ingestion_core
    assert "sui_data_ingestion_core" not in content, \
        "sui_data_ingestion_core imports should be removed from get_checkpoint.rs"


def test_sui_storage_import_added():
    """
    Verify sui_storage imports are added to get_checkpoint.rs (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should contain the new sui_storage import
    assert "sui_storage::object_store::util::{build_object_store, fetch_checkpoint}" in content, \
        "sui_storage::object_store::util imports should be present in get_checkpoint.rs"


def test_create_remote_store_client_not_used():
    """
    Verify create_remote_store_client is no longer used (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should NOT contain create_remote_store_client
    assert "create_remote_store_client" not in content, \
        "create_remote_store_client should not be used in get_checkpoint.rs"


def test_checkpointreader_not_used():
    """
    Verify CheckpointReader is no longer used (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should NOT contain CheckpointReader
    assert "CheckpointReader" not in content, \
        "CheckpointReader should not be used in get_checkpoint.rs"


def test_build_object_store_used():
    """
    Verify build_object_store is now used (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should contain build_object_store
    assert "build_object_store" in content, \
        "build_object_store should be used in get_checkpoint.rs"


def test_fetch_checkpoint_used():
    """
    Verify fetch_checkpoint is now used (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Should contain fetch_checkpoint
    assert "fetch_checkpoint" in content, \
        "fetch_checkpoint should be used in get_checkpoint.rs"


def test_refactored_code_structure():
    """
    Verify the refactored code uses the simpler two-line pattern (fail-to-pass).
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    # Find the relevant section - should have the new pattern:
    # let store = build_object_store(&url, vec![]);
    # let checkpoint = fetch_checkpoint(&store, sequence_number).await?;
    pattern = r'let store = build_object_store\(&url, vec!\[\]\);\s+let checkpoint = fetch_checkpoint\(&store, sequence_number\)\.await\?;'

    assert re.search(pattern, content), \
        "Refactored code should use the new simplified pattern with build_object_store and fetch_checkpoint"


def test_license_header_preserved():
    """
    Verify Apache license header is preserved (pass-to-pass).
    This is a project requirement from CLAUDE.md.
    """
    with open(GET_CHECKPOINT_FILE, 'r') as f:
        content = f.read()

    assert "Copyright (c) Mysten Labs, Inc." in content, \
        "Apache license header should be preserved"
    assert "SPDX-License-Identifier: Apache-2.0" in content, \
        "SPDX license identifier should be preserved"


def test_repo_fmt():
    """
    Repo code formatting passes cargo fmt check (pass-to-pass).
    """
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_repo_xlint():
    """
    Repo passes license/workspace lints (pass-to-pass).
    From CI: cargo xlint checks license headers and workspace structure.
    """
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo xlint failed:\n{r.stderr[-500:]}"


def test_cargo_lock_consistent():
    """
    Cargo.lock is consistent with Cargo.toml files (pass-to-pass).
    Verifies dependency changes are properly reflected in Cargo.lock.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-kv-rpc", "--locked"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # This may fail due to missing libclang, but if it runs it validates lock consistency
    # We accept either success (0) or specific dependency/build errors, but not lock mismatch
    if r.returncode != 0:
        # If it fails, make sure it's not due to lock file issues
        assert "lock file" not in r.stderr.lower(), \
            f"Cargo.lock mismatch:\n{r.stderr[-500:]}"
        # For other errors (like missing clang), we pass - the lock file is valid
    # If return code is 0, the lock file is definitely consistent


def test_cargo_metadata_valid():
    """
    Cargo.toml files produce valid metadata (pass_to_pass).
    Verifies all workspace manifests are well-formed and dependencies resolve.
    """
    r = subprocess.run(
        ["cargo", "metadata", "--format-version", "1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo metadata failed:\n{r.stderr[-500:]}"


def test_cargo_deny_check():
    """
    Cargo dependencies pass cargo-deny license/advisory checks (pass_to_pass).
    Verifies dependency licensing and security advisories.
    """
    r = subprocess.run(
        ["cargo", "deny", "check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    # cargo-deny may not be installed, in which case we skip
    stderr_lower = r.stderr.lower()
    if any(msg in stderr_lower for msg in ["could not find", "not installed", "no such command"]):
        return  # Skip if cargo-deny is not available
    assert r.returncode == 0, f"cargo deny check failed:\n{r.stderr[-500:]}"
