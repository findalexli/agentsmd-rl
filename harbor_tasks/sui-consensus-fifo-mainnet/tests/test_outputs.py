"""Tests for verifying the Sui consensus FIFO compaction Mainnet enablement fix."""

import subprocess
import sys
import re

REPO = "/workspace/sui"
TARGET_FILE = f"{REPO}/consensus/core/src/authority_node.rs"


# =============================================================================
# Pass-to-Pass Tests (repo_tests origin - these run actual CI commands)
# =============================================================================


def test_repo_cargo_check_consensus_core():
    """Cargo check compiles consensus-core package (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "consensus-core"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_clippy_consensus_core():
    """Cargo clippy lints consensus-core package (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "consensus-core", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_fmt_check():
    """Cargo fmt check passes for all code (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr}"


# =============================================================================
# Fail-to-Pass Tests (the original fix verification tests)
# =============================================================================


def test_mainnet_guard_removed():
    """FIFO compaction for Mainnet is no longer gated - the chain type check is removed."""
    with open(TARGET_FILE) as f:
        content = f.read()

    # The guard that excludes Mainnet should be removed
    assert "&& context.protocol_config.chain() != ChainType::Mainnet" not in content, \
        "Mainnet exclusion guard still present - should be removed to enable FIFO for all networks"

    # The simplified line should just pass use_fifo_compaction directly
    assert "context.parameters.use_fifo_compaction," in content, \
        "Expected simplified use_fifo_compaction parameter without Mainnet guard"


def test_chain_type_import_removed():
    """ChainType import should be removed since it's no longer used."""
    with open(TARGET_FILE) as f:
        content = f.read()

    # Check the specific import pattern that included ChainType
    # The old code had: use consensus_config::{ChainType, ConsensusProtocolConfig};
    # This separate import should be removed (ChainType no longer needed)
    assert "use consensus_config::{ChainType, ConsensusProtocolConfig};" not in content, \
        "Old ChainType import still present - should be consolidated"

    # ConsensusProtocolConfig should still be imported
    assert "use consensus_config::ConsensusProtocolConfig;" in content, \
        "ConsensusProtocolConfig import missing"


def test_cargo_check_compiles():
    """Code compiles successfully after changes."""
    result = subprocess.run(
        ["cargo", "check", "-p", "consensus-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )

    if result.returncode != 0:
        # Print relevant error info
        error_output = result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr
        assert False, f"Compilation failed:\n{error_output}"


def test_fifo_compaction_used_correctly():
    """Verify the RocksDBStore is initialized with just use_fifo_compaction parameter."""
    with open(TARGET_FILE) as f:
        content = f.read()

    # Find the RocksDBStore::new call and verify parameter passing
    pattern = r"RocksDBStore::new\(\s*store_path,\s*context\.parameters\.use_fifo_compaction,\s*\)"
    match = re.search(pattern, content, re.DOTALL)
    assert match is not None, \
        "RocksDBStore::new should be called with just use_fifo_compaction parameter, no Mainnet guard"
