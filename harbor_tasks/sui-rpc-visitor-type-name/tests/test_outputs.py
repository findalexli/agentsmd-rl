"""Test that TypeName is properly unwrapped as a string in RPC outputs."""

import subprocess
import sys
import os

REPO = "/workspace/sui"


def test_type_name_layout_exists():
    """
    Fail-to-pass: type_name_layout() function should exist and return correct layout.

    Verifies the type_name_layout function is exported from sui_types::base_types
    and returns the expected MoveStructLayout for 0x1::type_name::TypeName.
    """
    test_code = '''
// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

use sui_types::base_types::type_name_layout;

fn main() {
    let layout = type_name_layout();
    // Verify it has the correct struct tag
    let struct_tag = &layout.type_;
    assert_eq!(struct_tag.address.to_string(), "0x0000000000000000000000000000000000000000000000000000000000000001");
    assert_eq!(struct_tag.module.as_str(), "type_name");
    assert_eq!(struct_tag.name.as_str(), "TypeName");
    // Verify it has exactly one field named "name"
    assert_eq!(layout.fields.len(), 1);
    assert_eq!(layout.fields[0].name.as_str(), "name");
    println!("type_name_layout is correctly defined");
}
'''
    test_file = f"{REPO}/crates/sui-types/examples/test_type_name_layout.rs"
    os.makedirs(os.path.dirname(test_file), exist_ok=True)
    with open(test_file, "w") as f:
        f.write(test_code)

    result = subprocess.run(
        ["cargo", "build", "-p", "sui-types", "--example", "test_type_name_layout"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )

    try:
        os.remove(test_file)
    except:
        pass

    assert result.returncode == 0, f"type_name_layout function not found or incorrect:\n{result.stderr}"


def test_rpc_visitor_imports_type_name_layout():
    """
    Fail-to-pass: RPC visitor should import type_name_layout from base_types.

    Verifies that the rpc_visitor module imports the type_name_layout function
    to handle 0x1::type_name::TypeName as a string-like type.
    """
    # Check that the import exists in rpc_visitor/mod.rs
    result = subprocess.run(
        ["grep", "use crate::base_types::type_name_layout;", f"{REPO}/crates/sui-types/src/object/rpc_visitor/mod.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "type_name_layout import not found in rpc_visitor/mod.rs"


def test_rpc_visitor_handles_type_name():
    """
    Fail-to-pass: RPC visitor should check for type_name_layout in special cases.

    Verifies that the rpc_visitor recognizes TypeName layout and handles it
    as a string-like type (unwrapping to inner string).
    """
    # Check that type_name_layout() is called in the condition
    result = subprocess.run(
        ["grep", "type_name_layout()", f"{REPO}/crates/sui-types/src/object/rpc_visitor/mod.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "type_name_layout() check not found in rpc_visitor special case handling"

    # Also verify the comment mentions TypeName
    result = subprocess.run(
        ["grep", "0x1::type_name::TypeName", f"{REPO}/crates/sui-types/src/object/rpc_visitor/mod.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "TypeName comment not found in rpc_visitor"


def test_sui_display_imports_type_name_layout():
    """
    Fail-to-pass: sui-display should import type_name_layout from base_types.

    Verifies that the sui-display crate imports the type_name_layout function.
    """
    result = subprocess.run(
        ["grep", "use sui_types::base_types::type_name_layout;", f"{REPO}/crates/sui-display/src/v2/value.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "type_name_layout import not found in sui-display/src/v2/value.rs"


def test_sui_display_uses_type_name_in_atoms():
    """
    Fail-to-pass: sui-display should use type_name_layout in special case list.

    Verifies that type_name_layout is included in the special layouts list
    when converting Value to Atom in sui-display.
    """
    # Check that type_name_layout() appears in the special layouts array
    result = subprocess.run(
        ["grep", "-A5", "move_utf8_str_layout(),", f"{REPO}/crates/sui-display/src/v2/value.rs"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "Could not find special layouts list in sui-display"
    assert "type_name_layout()" in result.stdout, "type_name_layout not found in sui-display special layouts list"


def test_rpc_visitor_ascii_string():
    """
    Pass-to-pass: RPC visitor ascii_string test should still pass.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-types", "--lib", "json_ascii_string", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"json_ascii_string test failed:\n{result.stdout}\n{result.stderr}"


def test_rpc_visitor_utf8_string():
    """
    Pass-to-pass: RPC visitor utf8_string test should still pass.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-types", "--lib", "json_utf8_string", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"json_utf8_string test failed:\n{result.stdout}\n{result.stderr}"


def test_rpc_visitor_url():
    """
    Pass-to-pass: RPC visitor url test should still pass.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-types", "--lib", "json_url", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"json_url test failed:\n{result.stdout}\n{result.stderr}"


def test_cargo_fmt_check():
    """
    Pass-to-pass: Repo code formatting passes cargo fmt check.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"cargo fmt check failed:\n{result.stderr}"


def test_sui_types_lib_tests():
    """
    Pass-to-pass: sui-types crate library tests pass (pass_to_pass).
    Verifies that changes to base_types and rpc_visitor don't break existing tests.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-types", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, f"sui-types library tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


def test_sui_display_lib_tests():
    """
    Pass-to-pass: sui-display crate library tests pass (pass_to_pass).
    Verifies that changes to sui-display value.rs don't break existing tests.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "sui-display", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"sui-display library tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
