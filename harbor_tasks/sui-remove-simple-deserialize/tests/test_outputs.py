"""
Tests for verifying the simple_deserialize removal PR.

This tests that:
1. The deprecated simple_deserialize methods are removed from annotated_value.rs
2. The deprecated simple_deserialize methods are removed from runtime_value.rs
3. The usage in event.rs is already using BoundedVisitor::deserialize_value
4. The move-core-types crate compiles after the changes

Note: The event.rs file already uses BoundedVisitor::deserialize_value at the base commit
(the previous PR already migrated it). This PR only removes the now-unused methods.
"""

import subprocess
import re

REPO = "/workspace/sui"
ANNOTATED_VALUE_PATH = f"{REPO}/external-crates/move/crates/move-core-types/src/annotated_value.rs"
RUNTIME_VALUE_PATH = f"{REPO}/external-crates/move/crates/move-core-types/src/runtime_value.rs"
EVENT_PATH = f"{REPO}/crates/sui-analytics-indexer/src/handlers/tables/event.rs"


def test_move_value_simple_deserialize_removed():
    """MoveValue::simple_deserialize method should be removed from annotated_value.rs (fail_to_pass)."""
    with open(ANNOTATED_VALUE_PATH, 'r') as f:
        content = f.read()

    # Check that simple_deserialize method in MoveValue impl is removed
    # Find the MoveValue impl block and check it doesn't have simple_deserialize
    move_value_impl = re.search(
        r'impl MoveValue\s*\{([^}]|\{[^}]*\})*\}',
        content, re.DOTALL
    )
    if move_value_impl and "pub fn simple_deserialize" in move_value_impl.group(0):
        assert False, "MoveValue::simple_deserialize still exists in annotated_value.rs"


def test_move_struct_simple_deserialize_removed():
    """MoveStruct::simple_deserialize method should be removed from annotated_value.rs (fail_to_pass)."""
    with open(ANNOTATED_VALUE_PATH, 'r') as f:
        content = f.read()

    # Check MoveStruct impl block
    move_struct_impl = re.search(
        r'impl MoveStruct\s*\{([^}]|\{[^}]*\})*\}',
        content, re.DOTALL
    )
    if move_struct_impl and "pub fn simple_deserialize" in move_struct_impl.group(0):
        assert False, "MoveStruct::simple_deserialize still exists in annotated_value.rs"


def test_move_variant_simple_deserialize_removed():
    """MoveVariant::simple_deserialize method should be removed from annotated_value.rs (fail_to_pass)."""
    with open(ANNOTATED_VALUE_PATH, 'r') as f:
        content = f.read()

    # Check MoveVariant impl block
    move_variant_impl = re.search(
        r'impl MoveVariant\s*\{([^}]|\{[^}]*\})*\}',
        content, re.DOTALL
    )
    if move_variant_impl and "pub fn simple_deserialize" in move_variant_impl.group(0):
        assert False, "MoveVariant::simple_deserialize still exists in annotated_value.rs"


def test_runtime_struct_simple_deserialize_removed():
    """MoveStruct::simple_deserialize method should be removed from runtime_value.rs (fail_to_pass)."""
    with open(RUNTIME_VALUE_PATH, 'r') as f:
        content = f.read()

    # Check MoveStruct impl block in runtime_value.rs
    move_struct_impl = re.search(
        r'impl MoveStruct\s*\{([^}]|\{[^}]*\})*\}',
        content, re.DOTALL
    )
    if move_struct_impl and "pub fn simple_deserialize" in move_struct_impl.group(0):
        assert False, "MoveStruct::simple_deserialize still exists in runtime_value.rs"


def test_runtime_variant_simple_deserialize_removed():
    """MoveVariant::simple_deserialize method should be removed from runtime_value.rs (fail_to_pass)."""
    with open(RUNTIME_VALUE_PATH, 'r') as f:
        content = f.read()

    # Check MoveVariant impl block in runtime_value.rs
    move_variant_impl = re.search(
        r'impl MoveVariant\s*\{([^}]|\{[^}]*\})*\}',
        content, re.DOTALL
    )
    if move_variant_impl and "pub fn simple_deserialize" in move_variant_impl.group(0):
        assert False, "MoveVariant::simple_deserialize still exists in runtime_value.rs"


def test_event_rs_uses_bounded_visitor():
    """event.rs should use BoundedVisitor::deserialize_value (pass_to_pass - already fixed at base)."""
    with open(EVENT_PATH, 'r') as f:
        content = f.read()

    # Check that BoundedVisitor is imported
    assert "use sui_types::object::bounded_visitor::BoundedVisitor;" in content, \
        "BoundedVisitor import not found in event.rs"

    # Check that BoundedVisitor::deserialize_value is used
    assert "BoundedVisitor::deserialize_value" in content, \
        "BoundedVisitor::deserialize_value not found in event.rs"

    # Check that MoveValue::simple_deserialize is NOT used
    assert "MoveValue::simple_deserialize" not in content, \
        "MoveValue::simple_deserialize still used in event.rs"


def test_anyhow_result_not_imported():
    """anyhow::Result as AResult import should be removed from annotated_value.rs (fail_to_pass)."""
    with open(ANNOTATED_VALUE_PATH, 'r') as f:
        content = f.read()

    # The anyhow::Result as AResult import should be removed since simple_deserialize was the only user
    assert "use anyhow::Result as AResult;" not in content, \
        "anyhow::Result as AResult import still present in annotated_value.rs"


def test_cargo_check_move_core_types():
    """cargo check should pass on move-core-types crate after changes (pass_to_pass)."""
    # Check move-core-types crate from within its own directory
    move_core_types_dir = f"{REPO}/external-crates/move/crates/move-core-types"
    result = subprocess.run(
        ["cargo", "check"],
        cwd=move_core_types_dir,
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes
    )
    assert result.returncode == 0, f"cargo check failed for move-core-types:\n{result.stderr[-1000:]}"


def test_value_tests_compile():
    """cargo check should pass on move-core-types with tests (pass_to_pass)."""
    move_core_types_dir = f"{REPO}/external-crates/move/crates/move-core-types"
    result = subprocess.run(
        ["cargo", "check", "--tests"],
        cwd=move_core_types_dir,
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes
    )
    assert result.returncode == 0, f"cargo check --tests failed for move-core-types:\n{result.stderr[-1000:]}"


def test_move_core_types_clippy():
    """cargo clippy should pass on move-core-types (pass_to_pass - repo CI check)."""
    move_dir = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "clippy", "-p", "move-core-types", "--all-targets"],
        cwd=move_dir,
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes
    )
    assert result.returncode == 0, f"cargo clippy failed for move-core-types:\n{result.stderr[-1000:]}"


def test_move_core_types_tests():
    """cargo test --lib should pass on move-core-types (pass_to_pass - repo CI check)."""
    move_dir = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "test", "-p", "move-core-types", "--lib"],
        cwd=move_dir,
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes
    )
    assert result.returncode == 0, f"cargo test --lib failed for move-core-types:\n{result.stderr[-1000:]}"


def test_move_core_types_build():
    """cargo build --all-targets should pass on move-core-types (pass_to_pass - repo CI check)."""
    move_dir = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "build", "-p", "move-core-types", "--all-targets"],
        cwd=move_dir,
        capture_output=True,
        text=True,
        timeout=600  # 10 minutes
    )
    assert result.returncode == 0, f"cargo build --all-targets failed for move-core-types:\n{result.stderr[-1000:]}"
