"""Tests for Sui safe_unwrap/safe_assert hardening PR.

This PR replaces potentially panicking operations in Move native functions
with safe macros that return proper VM errors.
"""

import subprocess
import re
import os

REPO = "/workspace/sui"
MOVE_BINARY_FORMAT = f"{REPO}/external-crates/move/crates/move-binary-format"
SUI_MOVE_NATIVES = f"{REPO}/sui-execution/latest/sui-move-natives"


def test_move_binary_format_compiles():
    """move-binary-format crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "move-binary-format"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-1000:]}"


def test_sui_move_natives_compiles():
    """sui-move-natives-latest crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-move-natives-latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-1000:]}"


def test_safe_assert_eq_macro_exists():
    """safe_assert_eq macro is defined in move-binary-format/src/lib.rs"""
    lib_rs = f"{MOVE_BINARY_FORMAT}/src/lib.rs"
    with open(lib_rs) as f:
        content = f.read()

    # Check for safe_assert_eq macro definition
    assert "macro_rules! safe_assert_eq" in content, \
        "safe_assert_eq macro not found in lib.rs"

    # Check it has proper structure with left/right comparison
    assert "left != right" in content, \
        "safe_assert_eq macro doesn't compare left vs right"


def test_safe_unwrap_err_uses_qualified_paths():
    """safe_unwrap_err macro uses fully qualified paths."""
    lib_rs = f"{MOVE_BINARY_FORMAT}/src/lib.rs"
    with open(lib_rs) as f:
        content = f.read()

    # Check for fully qualified paths in the macro
    assert "move_binary_format::errors::PartialVMError" in content, \
        "safe_unwrap_err doesn't use fully qualified path for PartialVMError"
    assert "move_core_types::vm_status::StatusCode" in content, \
        "safe_unwrap_err doesn't use fully qualified path for StatusCode"


def test_native_accumulator_uses_safe_macros():
    """accumulator.rs uses safe_unwrap and safe_unwrap_err macros."""
    file_path = f"{SUI_MOVE_NATIVES}/src/accumulator.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe macros
    assert "use move_binary_format::{safe_unwrap, safe_unwrap_err}" in content, \
        "accumulator.rs doesn't import safe_unwrap macros"

    # Should use safe_unwrap_err for value_as operations
    assert "safe_unwrap_err!(safe_unwrap!(args.pop_back()).value_as::<u64>())" in content, \
        "accumulator.rs doesn't use safe_unwrap_err for value_as"


def test_native_address_uses_safe_macros():
    """address.rs uses safe_unwrap and safe_unwrap_err macros."""
    file_path = f"{SUI_MOVE_NATIVES}/src/address.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe macros
    assert "use move_binary_format::{safe_unwrap, safe_unwrap_err}" in content, \
        "address.rs doesn't import safe_unwrap macros"

    # Should NOT have unwrap() on try_into for address bytes
    addr_bytes_pattern = r"addr_bytes_le\.try_into\(\)\.unwrap\(\)"
    assert not re.search(addr_bytes_pattern, content), \
        "address.rs still uses .unwrap() on addr_bytes_le.try_into()"


def test_native_config_uses_safe_assert_eq():
    """config.rs uses safe_assert_eq macro instead of assert_eq."""
    file_path = f"{SUI_MOVE_NATIVES}/src/config.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_assert_eq
    assert "use move_binary_format::{safe_assert_eq, safe_unwrap}" in content, \
        "config.rs doesn't import safe_assert_eq"

    # Should use safe_assert_eq instead of assert_eq
    assert "safe_assert_eq!(ty_args.len(), 4)" in content, \
        "config.rs doesn't use safe_assert_eq for ty_args check"
    assert "safe_assert_eq!(args.len(), 3)" in content, \
        "config.rs doesn't use safe_assert_eq for args check"


def test_native_dynamic_field_uses_safe_macros():
    """dynamic_field.rs uses safe_assert, safe_assert_eq, safe_unwrap, safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/dynamic_field.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import all safe macros
    expected_import = ("use move_binary_format::{")
    assert expected_import in content, \
        "dynamic_field.rs doesn't import move_binary_format macros"
    assert "safe_assert" in content and "safe_assert_eq" in content, \
        "dynamic_field.rs doesn't import safe_assert macros"
    assert "safe_unwrap" in content and "safe_unwrap_err" in content, \
        "dynamic_field.rs doesn't import safe_unwrap macros"

    # Check for usage in the file
    assert "safe_assert_eq!(ty_args.len(), 1)" in content, \
        "dynamic_field.rs doesn't use safe_assert_eq for ty_args"


def test_native_event_uses_safe_macros():
    """event.rs uses safe_assert, safe_assert_eq, safe_unwrap, safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/event.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import all safe macros
    assert "use move_binary_format::{safe_assert, safe_assert_eq, safe_unwrap, safe_unwrap_err}" in content, \
        "event.rs doesn't import safe macros correctly"

    # Should use safe_unwrap for pop operations
    assert "safe_unwrap!(ty_args.pop())" in content, \
        "event.rs doesn't use safe_unwrap for ty_args.pop()"
    assert "safe_unwrap!(args.pop_back())" in content, \
        "event.rs doesn't use safe_unwrap for args.pop_back()"


def test_native_transfer_uses_safe_macros():
    """transfer.rs uses safe_assert, safe_unwrap, safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/transfer.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe macros
    assert "use move_binary_format::{safe_assert, safe_unwrap, safe_unwrap_err}" in content, \
        "transfer.rs doesn't import safe macros correctly"

    # Should NOT have bare .unwrap() on args.pop_back() for object transfer
    # The pattern should use safe_unwrap
    transfer_pattern = r"let obj = args\.pop_back\(\)\.unwrap\(\)"
    assert not re.search(transfer_pattern, content), \
        "transfer.rs still uses bare .unwrap() on args.pop_back() for obj"


def test_native_tx_context_uses_safe_macros():
    """tx_context.rs uses safe_unwrap_err for TransactionDigest parsing."""
    file_path = f"{SUI_MOVE_NATIVES}/src/tx_context.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap_err
    assert "use move_binary_format::safe_unwrap_err" in content, \
        "tx_context.rs doesn't import safe_unwrap_err"

    # Should use safe_unwrap_err for TransactionDigest parsing
    assert "safe_unwrap_err!(TransactionDigest::try_from(tx_hash.as_slice()))" in content, \
        "tx_context.rs doesn't use safe_unwrap_err for TransactionDigest parsing"

    # Should NOT have the old comment and unwrap pattern
    old_comment = "unwrap safe because all digests in Move are serialized"
    assert old_comment not in content, \
        "tx_context.rs still has old 'unwrap safe' comment"


def test_native_types_uses_safe_macros():
    """types.rs uses safe_unwrap macro."""
    file_path = f"{SUI_MOVE_NATIVES}/src/types.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap
    assert "use move_binary_format::safe_unwrap" in content, \
        "types.rs doesn't import safe_unwrap"

    # Should use safe_unwrap for ty_args.pop()
    assert "let ty = safe_unwrap!(ty_args.pop())" in content, \
        "types.rs doesn't use safe_unwrap for ty_args.pop()"


def test_native_test_scenario_uses_safe_macros():
    """test_scenario.rs uses safe_assert, safe_unwrap, safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/test_scenario.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe macros
    assert "use move_binary_format::{safe_assert, safe_unwrap, safe_unwrap_err}" in content, \
        "test_scenario.rs doesn't import safe macros correctly"

    # Function return types should be changed to PartialVMResult
    assert "fn get_specified_ty(mut ty_args: Vec<Type>) -> PartialVMResult<Type>" in content, \
        "get_specified_ty doesn't return PartialVMResult"


def test_native_funds_accumulator_uses_safe_macros():
    """funds_accumulator.rs uses safe_unwrap and safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/funds_accumulator.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe macros
    assert "use move_binary_format::{safe_unwrap, safe_unwrap_err}" in content, \
        "funds_accumulator.rs doesn't import safe macros correctly"

    # Should use safe_unwrap_err for U256 parsing
    assert "safe_unwrap_err!(safe_unwrap!(args.pop_back()).value_as::<U256>())" in content, \
        "funds_accumulator.rs doesn't use safe_unwrap_err for U256 parsing"


def test_native_crypto_group_ops_uses_safe_macros():
    """crypto/group_ops.rs uses safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/crypto/group_ops.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap_err
    assert "use move_binary_format::safe_unwrap_err" in content, \
        "group_ops.rs doesn't import safe_unwrap_err"

    # Should use safe_unwrap_err instead of .expect()
    assert "safe_unwrap_err!(G::multi_scalar_mul" in content, \
        "group_ops.rs doesn't use safe_unwrap_err for multi_scalar_mul"


def test_native_crypto_hmac_uses_safe_macros():
    """crypto/hmac.rs uses safe_unwrap_err."""
    file_path = f"{SUI_MOVE_NATIVES}/src/crypto/hmac.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap_err
    assert "use move_binary_format::safe_unwrap_err" in content, \
        "hmac.rs doesn't import safe_unwrap_err"

    # Should use safe_unwrap_err instead of .expect()
    assert "safe_unwrap_err!(hmac::HmacKey::from_bytes" in content, \
        "hmac.rs doesn't use safe_unwrap_err for HmacKey::from_bytes"


def test_native_test_utils_uses_safe_macros():
    """test_utils.rs uses safe_unwrap macro."""
    file_path = f"{SUI_MOVE_NATIVES}/src/test_utils.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap
    assert "use move_binary_format::safe_unwrap" in content, \
        "test_utils.rs doesn't import safe_unwrap"

    # Should use safe_unwrap for ty_args.pop()
    assert "let ty = safe_unwrap!(ty_args.pop())" in content, \
        "test_utils.rs doesn't use safe_unwrap for ty_args.pop()"


def test_native_lib_uses_safe_macros():
    """lib.rs (natives) uses safe_unwrap and adds safety comments."""
    file_path = f"{SUI_MOVE_NATIVES}/src/lib.rs"
    with open(file_path) as f:
        content = f.read()

    # Should import safe_unwrap
    assert "use move_binary_format::safe_unwrap" in content, \
        "lib.rs doesn't import safe_unwrap"

    # Should have safety comment for Identifier::new
    assert "// Safe: string literals are always valid identifiers" in content, \
        "lib.rs doesn't have safety comment for Identifier::new"

    # Should use safe_unwrap for get_nth_struct_field
    assert "Ok(safe_unwrap!(itr.nth(n)))" in content, \
        "lib.rs doesn't use safe_unwrap for itr.nth(n)"


# =============================================================================
# Pass-to-Pass Tests - Verify repo CI/CD passes on base and after fix
# =============================================================================

def test_repo_sui_move_natives_check():
    """sui-move-natives-latest compiles successfully (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-move-natives-latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-1000:]}"


def test_repo_sui_move_natives_clippy():
    """sui-move-natives-latest passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-move-natives-latest", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


def test_repo_sui_move_natives_test():
    """sui-move-natives-latest unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "sui-move-natives-latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-1000:]}"
