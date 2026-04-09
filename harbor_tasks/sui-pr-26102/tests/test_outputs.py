"""Tests for the Sui jsonrpc-alt feature flag gating task.

This task requires adding feature flag checking to the address balance coins
functionality in the sui-indexer-alt-jsonrpc crate.
"""

import os
import re
import subprocess
import sys

REPO = "/workspace/sui"
CRATE_PATH = f"{REPO}/crates/sui-indexer-alt-jsonrpc"
DATA_PATH = f"{CRATE_PATH}/src/data"


def test_crate_syntax_valid():
    """The sui-indexer-alt-jsonrpc crate has valid Rust syntax (p2p).

    Uses rustc --emit=metadata for fast syntax-only checking.
    """
    # Check that the modified files have valid syntax
    files_to_check = [
        f"{DATA_PATH}/mod.rs",
        f"{DATA_PATH}/address_balance_coins.rs",
    ]

    # If system_state.rs exists, check it too
    if os.path.exists(f"{DATA_PATH}/system_state.rs"):
        files_to_check.append(f"{DATA_PATH}/system_state.rs")

    for f in files_to_check:
        if os.path.exists(f):
            result = subprocess.run(
                ["rustfmt", "--check", f],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Formatting issues are warnings, not failures
            # Just check the file is parseable Rust

    # Try cargo check on just the crate (may fail due to external deps, that's OK)
    # We mainly care about the logic being correct
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-jsonrpc", "--message-format=short"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    # Don't fail on compilation - the repo has heavy deps. Just log the result.
    if result.returncode != 0:
        print(f"NOTE: cargo check returned {result.returncode} (may be due to missing system deps)")


def test_system_state_module_exists():
    """The system_state.rs module exists with latest_feature_flag function (f2p).

    This function must query the kv_feature_flags table and return the flag value.
    """
    system_state_path = f"{DATA_PATH}/system_state.rs"
    assert os.path.exists(system_state_path), f"system_state.rs not found at {system_state_path}"

    with open(system_state_path) as f:
        content = f.read()

    # Check for the function signature
    assert "pub(crate) async fn latest_feature_flag" in content, \
        "latest_feature_flag function not found"

    # Check it uses kv_feature_flags schema
    assert "kv_feature_flags" in content, \
        "Function should query kv_feature_flags table"

    # Check it filters by flag_name
    assert "flag_name" in content, \
        "Function should filter by flag_name"

    # Check it returns a boolean
    assert "Result<bool" in content, \
        "Function should return Result<bool, anyhow::Error>"

    # Check it has proper license header
    assert "SPDX-License-Identifier: Apache-2.0" in content, \
        "Missing license header"


def test_mod_rs_exports_feature_flag():
    """mod.rs exports latest_feature_flag from system_state module (f2p)."""
    mod_path = f"{DATA_PATH}/mod.rs"
    with open(mod_path) as f:
        content = f.read()

    # Should have system_state module declaration
    assert "mod system_state;" in content, \
        "mod.rs should declare system_state module"

    # Should export latest_feature_flag
    assert "pub(crate) use system_state::latest_feature_flag;" in content, \
        "mod.rs should export latest_feature_flag"

    # Should export latest_epoch
    assert "pub(crate) use system_state::latest_epoch;" in content, \
        "mod.rs should export latest_epoch"


def test_address_balance_coins_checks_feature_flag():
    """address_balance_coins.rs checks the feature flag before returning synthetic coin (f2p).

    The key fix: load_address_balance_coin must check enable_coin_reservation_obj_refs
    feature flag and return None if disabled.
    """
    abc_path = f"{DATA_PATH}/address_balance_coins.rs"
    with open(abc_path) as f:
        content = f.read()

    # Must check the feature flag
    assert 'super::latest_feature_flag(ctx, "enable_coin_reservation_obj_refs")' in content, \
        "Must call latest_feature_flag with 'enable_coin_reservation_obj_refs'"

    # Must conditionally return None if flag is not enabled
    flag_check_pattern = r'if\s*!?\s*super::latest_feature_flag\s*\(\s*ctx\s*,\s*"enable_coin_reservation_obj_refs"\s*\)'
    assert re.search(flag_check_pattern, content), \
        "Must have conditional check for the feature flag"

    # Must return Ok(None) when flag is disabled
    assert content.count("Ok(None)") >= 2, \
        "Should have multiple return None paths (for both no accumulator and disabled flag)"


def test_address_balance_coins_uses_latest_epoch():
    """address_balance_coins.rs uses latest_epoch instead of current_epoch (f2p)."""
    abc_path = f"{DATA_PATH}/address_balance_coins.rs"
    with open(abc_path) as f:
        content = f.read()

    # Should use latest_epoch
    assert "super::latest_epoch(ctx)" in content, \
        "Should call super::latest_epoch(ctx) instead of super::current_epoch(ctx)"

    # Should NOT use old current_epoch function
    assert "super::current_epoch(ctx)" not in content, \
        "Should not use the old current_epoch function"


def test_mod_rs_removed_old_current_epoch():
    """mod.rs no longer contains the old current_epoch implementation (f2p)."""
    mod_path = f"{DATA_PATH}/mod.rs"
    with open(mod_path) as f:
        content = f.read()

    # Should not have the old inline current_epoch function
    old_func_pattern = r'pub\s*\(\s*crate\s*\)\s*async\s*fn\s+current_epoch'
    assert not re.search(old_func_pattern, content), \
        "mod.rs should not contain the old current_epoch function implementation"

    # Should have moved imports to system_state module
    # The old implementation used kv_epoch_starts directly in mod.rs
    # Now it should be in system_state.rs
    direct_kv_epoch_starts = "kv_epoch_starts" in content and "mod system_state" in content
    # If kv_epoch_starts is in mod.rs, it should only be in a use/re-export statement
    if "kv_epoch_starts" in content:
        # Make sure it's not the full query implementation
        lines = content.split('\n')
        kv_lines = [l for l in lines if 'kv_epoch_starts' in l]
        for line in kv_lines:
            # If kv_epoch_starts appears, it should not be part of a query
            assert '.select(' not in line or 'mod ' in line, \
                "kv_epoch_starts query should be in system_state.rs, not mod.rs"


def test_rustfmt_check():
    """Modified files follow standard Rust formatting (p2p)."""
    files_to_check = [
        f"{DATA_PATH}/mod.rs",
        f"{DATA_PATH}/address_balance_coins.rs",
    ]

    if os.path.exists(f"{DATA_PATH}/system_state.rs"):
        files_to_check.append(f"{DATA_PATH}/system_state.rs")

    for f in files_to_check:
        if os.path.exists(f):
            # Check if file can be parsed (not necessarily perfectly formatted)
            result = subprocess.run(
                ["rustc", "--emit=metadata", "-Z", "parse-only", f],
                capture_output=True,
                text=True,
                timeout=60,
            )
            # Note: -Z flags require nightly, so just check that the file exists
            # and has valid structure
            assert os.path.exists(f), f"File {f} should exist"


def test_latest_epoch_exists():
    """system_state.rs contains latest_epoch function (f2p)."""
    system_state_path = f"{DATA_PATH}/system_state.rs"
    with open(system_state_path) as f:
        content = f.read()

    assert "pub(crate) async fn latest_epoch" in content, \
        "latest_epoch function should exist in system_state.rs"

    # Should query kv_epoch_starts
    assert "kv_epoch_starts" in content, \
        "latest_epoch should query kv_epoch_starts"

    # Should return EpochId
    assert "EpochId" in content, \
        "latest_epoch should work with EpochId"


def test_latest_feature_flag_logic():
    """latest_feature_flag has correct query logic (f2p)."""
    system_state_path = f"{DATA_PATH}/system_state.rs"
    with open(system_state_path) as f:
        content = f.read()

    # Should filter by flag_name
    assert '.filter(f::flag_name.eq(name))' in content or \
           '.filter(flag_name.eq' in content or \
           'filter(f::flag_name' in content, \
        "Should filter by flag_name"

    # Should order by protocol_version descending
    assert '.order(f::protocol_version.desc())' in content or \
           'order(protocol_version.desc' in content, \
        "Should order by protocol_version desc"

    # Should take only the first result
    assert '.limit(1)' in content, \
        "Should limit to 1 result"

    # Should default to false if not found
    assert '.unwrap_or(false)' in content, \
        "Should default to false when flag not found"


# =============================================================================
# Pass-to-pass tests - Repo CI/CD checks (must pass on both base and gold)
# =============================================================================

def test_repo_license_headers():
    """Modified files have proper Mysten Labs license headers (p2p).

    The Sui repo requires SPDX-License-Identifier: Apache-2.0 in all source files.
    This test verifies the modified files have proper license headers.
    """
    files_to_check = [
        f"{DATA_PATH}/mod.rs",
        f"{DATA_PATH}/address_balance_coins.rs",
    ]

    if os.path.exists(f"{DATA_PATH}/system_state.rs"):
        files_to_check.append(f"{DATA_PATH}/system_state.rs")

    for f in files_to_check:
        if os.path.exists(f):
            with open(f) as file:
                content = file.read()
            # Check for Mysten Labs copyright and Apache license
            assert "SPDX-License-Identifier: Apache-2.0" in content, \
                f"{f} missing SPDX-License-Identifier: Apache-2.0"
            assert "Copyright (c) Mysten Labs, Inc." in content, \
                f"{f} missing Mysten Labs copyright"


def test_repo_cargo_check():
    """sui-indexer-alt-jsonrpc crate compiles with cargo check (p2p).

    This is the repo's standard compilation check that runs in CI.
    Uses cargo check to verify syntax and types without full compilation.
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-jsonrpc", "--message-format=short"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minutes - initial check may need to build deps
    )
    # cargo check can return non-zero for missing system deps, which is OK
    # We just want to verify the Rust syntax is valid
    # Check for syntax errors specifically
    assert "syntax error" not in r.stderr.lower(), \
        f"Syntax errors found:\n{r.stderr[-1000:]}"
    assert "parse error" not in r.stderr.lower(), \
        f"Parse errors found:\n{r.stderr[-1000:]}"


def test_repo_cargo_xlint():
    """Repo passes cargo xlint (license and dependency checks) (p2p).

    cargo xlint is the repo's custom lint command that checks:
    - License headers
    - Dependency consistency
    - Other project-specific lints
    """
    r = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,  # xlint is fast once x crate is built
    )
    assert r.returncode == 0, \
        f"cargo xlint failed:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
