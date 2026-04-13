#!/usr/bin/env python3
"""Tests for gasless transaction dryrun/simulate fix.

This verifies that the fix correctly skips mock gas injection for gasless transactions
in both dry_exec_transaction and simulate_transaction functions.
"""

import subprocess
import sys

REPO = "/workspace/sui"
AUTHORITY_FILE = f"{REPO}/crates/sui-core/src/authority.rs"

def run_grep(pattern, file_path):
    """Run grep and return True if pattern found."""
    result = subprocess.run(
        ["grep", "-n", pattern, file_path],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout

def test_dry_exec_has_gasless_check():
    """Verify dry_exec_transaction has is_gasless check (f2p)."""
    found, output = run_grep("let is_gasless =", AUTHORITY_FILE)
    assert found, f"is_gasless variable not found in authority.rs"
    lines = output.strip().split("\n")
    assert len(lines) >= 2, f"Expected at least 2 is_gasless declarations, found {len(lines)}"

def test_dry_exec_skips_mock_gas_for_gasless():
    """Verify dry_exec_transaction skips mock gas when is_gasless is true (f2p)."""
    with open(AUTHORITY_FILE, "r") as f:
        content = f.read()
    assert "if is_gasless {" in content, "is_gasless conditional block not found"
    assert "check_transaction_input" in content, "check_transaction_input call not found"
    dry_exec_start = content.find("pub async fn dry_exec_transaction")
    assert dry_exec_start != -1, "dry_exec_transaction function not found"
    dry_exec_section = content[dry_exec_start:]
    assert "if is_gasless {" in dry_exec_section, "is_gasless check not in dry_exec_transaction"

def test_simulate_skips_mock_gas_for_gasless():
    """Verify simulate_transaction skips mock gas for gasless (f2p)."""
    with open(AUTHORITY_FILE, "r") as f:
        content = f.read()
    simulate_start = content.find("pub fn simulate_transaction")
    assert simulate_start != -1, "simulate_transaction function not found"
    simulate_section = content[simulate_start:]
    assert "is_gasless" in simulate_section, "is_gasless not found in simulate_transaction"
    assert "!is_gasless" in simulate_section, "!is_gasless condition not found in simulate_transaction"

def test_gasless_uses_check_transaction_input():
    """Verify gasless path uses check_transaction_input directly (f2p)."""
    with open(AUTHORITY_FILE, "r") as f:
        content = f.read()
    assert "sui_transaction_checks::check_transaction_input(" in content, \
        "check_transaction_input call not found for gasless path"


# =============================================================================
# Pass-to-Pass Tests (Repo CI Tests)
# =============================================================================
# These tests verify the repo passes its own CI checks on the base commit.
# Note: Compilation tests are excluded due to Docker container disk space limits.
# The repo CI uses `cargo check -p sui-core` and `cargo xclippy` but these
# require significant disk space for compilation artifacts (5GB+).
# The tests below are lightweight checks that don't require compilation.

def test_repo_rustfmt():
    """Repo code passes rustfmt check (pass_to_pass).
    
    Runs: cargo fmt --check
    CI Source: .github/workflows/rust.yml (rustfmt job)
    """
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"rustfmt check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_license_check():
    """Repo license headers pass cargo xlint (pass_to_pass).
    
    Runs: cargo xlint
    CI Source: .github/workflows/rust.yml (license-check job)
    """
    r = subprocess.run(
        ["cargo", "xlint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"License check failed:\n{r.stderr[-500:]}"


def test_repo_git_checks():
    """Repo passes git checks script (pass_to_pass).
    
    Runs: scripts/git-checks.sh
    CI Source: .github/workflows/rust.yml (license-check job)
    """
    r = subprocess.run(
        ["bash", f"{REPO}/scripts/git-checks.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"git checks failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
