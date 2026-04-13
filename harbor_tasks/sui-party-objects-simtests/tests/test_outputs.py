#!/usr/bin/env python3
"""Tests for verifying the PR changes to party objects simtests."""

import subprocess
import sys
import os

REPO = "/workspace/sui"


def test_new_deny_list_test_exists():
    """Verify that the new coin_deny_list_v2_party_owner_test function exists."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    assert "async fn coin_deny_list_v2_party_owner_test()" in content, \
        "New test coin_deny_list_v2_party_owner_test should exist in per_epoch_config_stress_tests.rs"


def test_deny_list_test_has_deny_address_assertion():
    """Verify the new test has the proper assertion for DENY_ADDRESS."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # Check for key elements of the new test
    assert "AddressDeniedForCoin" in content, \
        "Test should check for AddressDeniedForCoin error"
    assert "DENY_ADDRESS" in content, \
        "Test should reference DENY_ADDRESS"
    assert "trigger_reconfiguration" in content, \
        "Test should call trigger_reconfiguration to advance epoch"


def test_imports_added_to_stress_tests():
    """Verify that necessary imports were added to per_epoch_config_stress_tests.rs."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # Check for new imports added by the patch
    assert "use move_core_types::language_storage::{StructTag, TypeTag};" in content, \
        "Should import StructTag along with TypeTag"
    assert "use sui_types::execution_status::ExecutionErrorKind;" in content, \
        "Should import ExecutionErrorKind"
    assert "use sui_types::{SUI_DENY_LIST_OBJECT_ID, SUI_FRAMEWORK_ADDRESS, SUI_FRAMEWORK_PACKAGE_ID};" in content, \
        "Should import SUI_FRAMEWORK_ADDRESS along with other constants"


def test_mainnet_protocol_config_guards_removed_from_party_tests():
    """Verify that has_mainnet_protocol_config_override guards are removed from party_objects_tests.rs."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/party_objects_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # The guards should be removed - check that the pattern doesn't exist
    guard_pattern = "if sui_simulator::has_mainnet_protocol_config_override()"
    assert guard_pattern not in content, \
        f"Mainnet protocol config override guards should be removed from party_objects_tests.rs"


def test_party_tests_no_longer_skip_mainnet():
    """Verify specific party tests no longer have the mainnet skip guard."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/party_objects_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # Check that specific tests no longer have early return for mainnet
    test_functions = [
        "party_object_deletion",
        "party_object_deletion_multiple_times",
        "party_object_deletion_multiple_times_cert_racing",
        "party_object_transfer",
        "party_object_transfer_multiple_times",
        "party_object_transfer_multi_certs",
        "party_object_read",
        "party_object_grpc",
        "party_coin_grpc",
        "party_object_jsonrpc",
    ]

    for test_name in test_functions:
        # Find the function and check it doesn't have the guard
        import re
        pattern = rf"async fn {test_name}\(\) \{{[^}}]*has_mainnet_protocol_config_override"
        match = re.search(pattern, content, re.DOTALL)
        assert match is None, \
            f"Test {test_name} should not have has_mainnet_protocol_config_override guard"


def test_cargo_check_passes():
    """Verify that the code compiles with cargo check (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-e2e-tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=1800  # 30 minutes for initial compile
    )

    assert result.returncode == 0, \
        f"cargo check failed:\n{result.stderr[-2000:]}"


def test_rustfmt_check():
    """Verify that the code is properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Code is not properly formatted:\n{result.stdout}\n{result.stderr}"


def test_cargo_xlint():
    """Verify license headers and other project lints pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes
    )

    assert result.returncode == 0, \
        f"cargo xlint failed:\n{result.stderr[-1000:]}"


def test_cargo_clippy_e2e_tests():
    """Verify clippy passes on sui-e2e-tests crate (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "sui-e2e-tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes
    )

    assert result.returncode == 0, \
        f"cargo clippy failed for sui-e2e-tests:\n{result.stderr[-1000:]}"


def test_new_test_has_proper_test_structure():
    """Verify the new test has the expected structure and steps."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # Find the new test function and verify its structure
    import re

    # Look for the test function
    test_pattern = r"async fn coin_deny_list_v2_party_owner_test\(\) \{[^}]*\}"
    # This is a simplified check - we look for key parts

    # Step 1: Add to deny list
    assert "deny_list_v2_add" in content, \
        "Test should call deny_list_v2_add"

    # Step 2: trigger_reconfiguration for epoch advancement
    assert "trigger_reconfiguration" in content, \
        "Test should trigger reconfiguration"

    # Step 3: Build PTB with public_party_transfer
    assert "public_party_transfer" in content, \
        "Test should use public_party_transfer"

    # Step 4: Verify failure with AddressDeniedForCoin
    assert "execute_transaction_may_fail" in content, \
        "Test should use execute_transaction_may_fail"
    assert "effects.status().is_err()" in content, \
        "Test should check transaction failed"


def test_party_tests_have_sim_test_attribute():
    """Verify that party tests have the #[sim_test] attribute (pass_to_pass)."""
    target_file = os.path.join(REPO, "crates/sui-e2e-tests/tests/party_objects_tests.rs")

    with open(target_file, 'r') as f:
        content = f.read()

    # Check key tests have #[sim_test] attribute
    test_functions = [
        "party_object_deletion",
        "party_object_deletion_multiple_times",
        "party_object_transfer",
        "party_object_read",
    ]

    for test_name in test_functions:
        # Look for #[sim_test] before the function
        pattern = rf"#\[sim_test\]\s*\n\s*async fn {test_name}\(\)"
        import re
        match = re.search(pattern, content)
        assert match is not None, \
            f"Test {test_name} should have #[sim_test] attribute"


def test_repo_xlint():
    """Repo's license headers and lints pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo xlint failed:\n{result.stderr[-1000:]}"


def test_repo_rustfmt():
    """Repo's code formatting passes rustfmt check (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"cargo fmt check failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
