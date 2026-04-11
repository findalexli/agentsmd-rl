"""
Tests for the receive_object gas charging changes.

This validates:
1. Protocol config has new cost fields (f2p)
2. Native implementation charges gas per-byte (f2p)
3. Code compiles (p2p via cargo check)
"""

import subprocess
import sys
import os

REPO = "/workspace/sui"
TIMEOUT = 300  # 5 minutes for cargo commands


def test_protocol_config_has_new_fields():
    """
    Fail-to-pass: Protocol config must have the new cost fields.

    The PR adds:
    - transfer_receive_object_cost_per_byte
    - transfer_receive_object_type_cost_per_byte
    """
    lib_rs = os.path.join(REPO, "crates/sui-protocol-config/src/lib.rs")

    with open(lib_rs, 'r') as f:
        content = f.read()

    # Check for the new field declarations
    assert "transfer_receive_object_cost_per_byte: Option<u64>" in content, \
        "Missing transfer_receive_object_cost_per_byte field in ProtocolConfig"

    assert "transfer_receive_object_type_cost_per_byte: Option<u64>" in content, \
        "Missing transfer_receive_object_type_cost_per_byte field in ProtocolConfig"


def test_protocol_config_sets_values_for_version_119():
    """
    Fail-to-pass: Protocol version 119 must set the new cost values.

    The PR sets:
    - transfer_receive_object_cost_per_byte = Some(1)
    - transfer_receive_object_type_cost_per_byte = Some(2)
    """
    lib_rs = os.path.join(REPO, "crates/sui-protocol-config/src/lib.rs")

    with open(lib_rs, 'r') as f:
        content = f.read()

    # Find version 119 block and check it sets the new fields
    assert "cfg.transfer_receive_object_cost_per_byte = Some(1)" in content, \
        "Protocol version 119 should set transfer_receive_object_cost_per_byte to Some(1)"

    assert "cfg.transfer_receive_object_type_cost_per_byte = Some(2)" in content, \
        "Protocol version 119 should set transfer_receive_object_type_cost_per_byte to Some(2)"


def test_native_cost_params_has_new_fields():
    """
    Fail-to-pass: TransferReceiveObjectInternalCostParams must have new cost fields.
    """
    transfer_rs = os.path.join(REPO, "sui-execution/latest/sui-move-natives/src/transfer.rs")

    with open(transfer_rs, 'r') as f:
        content = f.read()

    # Check the struct has the new fields
    assert "transfer_receive_object_internal_cost_per_byte: InternalGas" in content, \
        "Missing transfer_receive_object_internal_cost_per_byte in TransferReceiveObjectInternalCostParams"

    assert "transfer_receive_object_internal_type_cost_per_byte: InternalGas" in content, \
        "Missing transfer_receive_object_internal_type_cost_per_byte in TransferReceiveObjectInternalCostParams"


def test_native_receive_charges_type_cost():
    """
    Fail-to-pass: receive_object_internal must charge gas based on type size.

    The PR adds this charging before processing:
    native_charge_gas_early_exit!(
        context,
        transfer_receive_object_internal_cost_params
            .transfer_receive_object_internal_type_cost_per_byte
            * u64::from(child_ty.size()?).into()
    );
    """
    transfer_rs = os.path.join(REPO, "sui-execution/latest/sui-move-natives/src/transfer.rs")

    with open(transfer_rs, 'r') as f:
        content = f.read()

    # Check that the type-based charging is present
    assert "transfer_receive_object_internal_type_cost_per_byte" in content and \
           "child_ty.size()" in content, \
        "receive_object_internal must charge gas based on child_ty.size()"


def test_native_receive_charges_per_byte_cost():
    """
    Fail-to-pass: receive_object_internal must charge gas based on object size.

    The PR adds this charging before returning the child.
    """
    transfer_rs = os.path.join(REPO, "sui-execution/latest/sui-move-natives/src/transfer.rs")

    with open(transfer_rs, 'r') as f:
        content = f.read()

    # Check that the size-based charging is present
    assert "abstract_memory_size" in content, \
        "receive_object_internal must call abstract_memory_size for per-byte charging"

    assert "transfer_receive_object_internal_cost_per_byte" in content and \
           "child_size" in content, \
        "receive_object_internal must charge gas based on child_size"


def test_natives_cost_table_passes_new_params():
    """
    Fail-to-pass: NativesCostTable must pass the new protocol config values.
    """
    lib_rs = os.path.join(REPO, "sui-execution/latest/sui-move-natives/src/lib.rs")

    with open(lib_rs, 'r') as f:
        content = f.read()

    # Check that the new fields are populated from protocol config
    assert "transfer_receive_object_internal_cost_per_byte: protocol_config" in content and \
           "transfer_receive_object_cost_per_byte_as_option" in content, \
        "NativesCostTable must pass transfer_receive_object_cost_per_byte from protocol config"

    assert "transfer_receive_object_internal_type_cost_per_byte: protocol_config" in content and \
           "transfer_receive_object_type_cost_per_byte_as_option" in content, \
        "NativesCostTable must pass transfer_receive_object_type_cost_per_byte from protocol config"


def test_transfer_rs_imports_sizeconfig():
    """
    Fail-to-pass: transfer.rs must import SizeConfig and ValueView for size calculation.
    """
    transfer_rs = os.path.join(REPO, "sui-execution/latest/sui-move-natives/src/transfer.rs")

    with open(transfer_rs, 'r') as f:
        content = f.read()

    # Check the new import is present
    assert "use move_vm_runtime::shared::views::{SizeConfig, ValueView};" in content, \
        "transfer.rs must import SizeConfig and ValueView for abstract_memory_size"


def test_cargo_check_passes():
    """
    Pass-to-pass: The code must compile with cargo check on the protocol-config package.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-protocol-config"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-2000:]}"


def test_natives_check_passes():
    """
    Pass-to-pass: The sui-move-natives-latest package must compile.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-move-natives-latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"sui-move-natives-latest check failed:\n{result.stderr[-2000:]}"


def test_protocol_config_clippy_passes():
    """
    Pass-to-pass: cargo clippy on sui-protocol-config passes (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "sui-protocol-config", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo clippy on sui-protocol-config failed:\n{result.stderr[-2000:]}"


def test_move_natives_clippy_passes():
    """
    Pass-to-pass: cargo clippy on sui-move-natives-latest passes (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "sui-move-natives-latest", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo clippy on sui-move-natives-latest failed:\n{result.stderr[-2000:]}"


def test_protocol_config_unit_tests_pass():
    """
    Pass-to-pass: Unit tests for sui-protocol-config pass (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-protocol-config"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo test on sui-protocol-config failed:\n{result.stderr[-2000:]}"


def test_move_natives_unit_tests_pass():
    """
    Pass-to-pass: Unit tests for sui-move-natives-latest pass (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-move-natives-latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo test on sui-move-natives-latest failed:\n{result.stderr[-2000:]}"


def test_cargo_xlint_passes():
    """
    Pass-to-pass: cargo xlint passes (repo CI license/checks).
    """
    result = subprocess.run(
        ["cargo", "xlint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo xlint failed:\n{result.stderr[-2000:]}"


def test_execution_layer_cut_works():
    """
    Pass-to-pass: Execution layer cut works (repo CI check).
    """
    result = subprocess.run(
        ["./scripts/execution_layer.py", "cut", "for_ci_test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300  # 5 minutes
    )

    assert result.returncode == 0, f"execution_layer.py cut failed:\n{result.stderr[-2000:]}"


def test_cargo_fmt_check():
    """
    Pass-to-pass: Rust code formatting passes (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"cargo fmt --check failed:\n{result.stderr[-1000:]}"


def test_cargo_doc_builds():
    """
    Pass-to-pass: cargo doc builds for sui-protocol-config (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "doc", "-p", "sui-protocol-config", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"cargo doc failed:\n{result.stderr[-2000:]}"


def test_doctests_pass():
    """
    Pass-to-pass: doctests for sui-protocol-config pass (repo CI check).
    """
    result = subprocess.run(
        ["cargo", "test", "--doc", "-p", "sui-protocol-config"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TIMEOUT
    )

    assert result.returncode == 0, f"doctests failed:\n{result.stderr[-2000:]}"


def test_git_checks_pass():
    """
    Pass-to-pass: git checks script passes (repo CI check).
    """
    result = subprocess.run(
        ["./scripts/git-checks.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"git-checks.sh failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
