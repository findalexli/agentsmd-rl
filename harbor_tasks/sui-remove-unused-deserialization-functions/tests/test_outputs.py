#!/usr/bin/env python3
"""Tests for PR #26160: Remove unused deserialization functions."""

import subprocess
import sys

REPO = "/workspace/sui"


def test_annotated_value_movevalue_simple_deserialize_removed():
    """MoveValue::simple_deserialize should be removed from annotated_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/annotated_value.rs") as f:
        content = f.read()

    # Check that simple_deserialize is NOT in the MoveValue impl block
    # The method should be completely removed
    impl_movevalue_start = content.find("impl MoveValue {")
    impl_movevalue_end = content.find("impl MoveStruct {")
    movevalue_section = content[impl_movevalue_start:impl_movevalue_end]

    assert "simple_deserialize" not in movevalue_section, \
        "MoveValue::simple_deserialize should be removed from annotated_value.rs"


def test_annotated_value_movestruct_simple_deserialize_removed():
    """MoveStruct::simple_deserialize should be removed from annotated_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/annotated_value.rs") as f:
        content = f.read()

    # Check that simple_deserialize is NOT in the MoveStruct impl block
    impl_movestruct_start = content.find("impl MoveStruct {")
    impl_movestruct_end = content.find("impl MoveVariant {")
    movestruct_section = content[impl_movestruct_start:impl_movestruct_end]

    assert "simple_deserialize" not in movestruct_section, \
        "MoveStruct::simple_deserialize should be removed from annotated_value.rs"


def test_annotated_value_movevariant_simple_deserialize_removed():
    """MoveVariant::simple_deserialize should be removed from annotated_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/annotated_value.rs") as f:
        content = f.read()

    # Check that simple_deserialize is NOT in the MoveVariant impl block
    impl_movevariant_start = content.find("impl MoveVariant {")
    impl_movevariant_end = content.find("impl MoveStructLayout {")
    movevariant_section = content[impl_movevariant_start:impl_movevariant_end]

    assert "simple_deserialize" not in movevariant_section, \
        "MoveVariant::simple_deserialize should be removed from annotated_value.rs"


def test_runtime_value_movestruct_simple_deserialize_removed():
    """MoveStruct::simple_deserialize should be removed from runtime_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/runtime_value.rs") as f:
        content = f.read()

    # Check that simple_deserialize is NOT in the MoveStruct impl block
    impl_movestruct_start = content.find("impl MoveStruct {")
    impl_movestruct_end = content.find("impl MoveVariant {")
    movestruct_section = content[impl_movestruct_start:impl_movestruct_end]

    assert "simple_deserialize" not in movestruct_section, \
        "MoveStruct::simple_deserialize should be removed from runtime_value.rs"


def test_runtime_value_movevariant_simple_deserialize_removed():
    """MoveVariant::simple_deserialize should be removed from runtime_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/runtime_value.rs") as f:
        content = f.read()

    # Check that simple_deserialize is NOT in the MoveVariant impl block
    impl_movevariant_start = content.find("impl MoveVariant {")
    impl_movevariant_end = content.find("impl MoveStructLayout {")
    movevariant_section = content[impl_movevariant_start:impl_movevariant_end]

    assert "simple_deserialize" not in movevariant_section, \
        "MoveVariant::simple_deserialize should be removed from runtime_value.rs"


def test_event_uses_bounded_visitor():
    """event.rs should use BoundedVisitor::deserialize_value instead of MoveValue::simple_deserialize"""
    with open(f"{REPO}/crates/sui-analytics-indexer/src/handlers/tables/event.rs") as f:
        content = f.read()

    assert "BoundedVisitor::deserialize_value" in content, \
        "event.rs should use BoundedVisitor::deserialize_value"
    assert "MoveValue::simple_deserialize" not in content, \
        "event.rs should not use MoveValue::simple_deserialize"


def test_value_test_has_helper_function():
    """value_test.rs should have the deser_annotated_value helper function"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/unit_tests/value_test.rs") as f:
        content = f.read()

    assert "fn deser_annotated_value" in content, \
        "value_test.rs should have deser_annotated_value helper function"


def test_annotated_value_anyhow_import_removed():
    """The unused anyhow import should be removed from annotated_value.rs"""
    with open(f"{REPO}/external-crates/move/crates/move-core-types/src/annotated_value.rs") as f:
        content = f.read()

    assert "use anyhow::Result as AResult;" not in content, \
        "Unused anyhow import should be removed from annotated_value.rs"


def test_event_imports_bounded_visitor():
    """event.rs should import BoundedVisitor from sui_types"""
    with open(f"{REPO}/crates/sui-analytics-indexer/src/handlers/tables/event.rs") as f:
        content = f.read()

    assert "sui_types::object::bounded_visitor::BoundedVisitor" in content, \
        "event.rs should import BoundedVisitor from sui_types::object::bounded_visitor"


def test_move_core_types_compiles():
    """move-core-types crate should compile successfully (pass-to-pass)"""
    # Run from external-crates/move directory where move-core-types is a workspace member
    r = subprocess.run(
        ["cargo", "check", "-p", "move-core-types"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"move-core-types failed to compile:\n{r.stderr[-1000:]}"


def test_move_core_types_tests_pass():
    """move-core-types tests should pass (pass-to-pass)"""
    # Run from external-crates/move directory where move-core-types is a workspace member
    # Use --lib to run only library tests (not doc tests)
    r = subprocess.run(
        ["cargo", "test", "-p", "move-core-types", "--lib", "--", "--test-threads=1"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"move-core-types tests failed:\n{r.stderr[-1000:]}"


def test_move_fmt():
    """External move crates code formatting passes (pass-to-pass)"""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"move fmt check failed:\n{r.stderr[-500:]}"


def test_move_clippy():
    """External move crates clippy passes (pass-to-pass)"""
    r = subprocess.run(
        ["cargo", "move-clippy", "-D", "warnings"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"move clippy failed:\n{r.stderr[-500:]}"


def test_move_core_types_value_tests():
    """move-core-types value_test unit tests pass (pass-to-pass)"""
    # Run specifically the value_test module to ensure it works before and after changes
    r = subprocess.run(
        ["cargo", "test", "-p", "move-core-types", "--lib", "value_test", "--", "--test-threads=1"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"move-core-types value_test tests failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
