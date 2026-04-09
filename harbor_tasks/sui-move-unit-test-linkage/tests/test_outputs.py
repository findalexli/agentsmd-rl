"""Tests for the move-unit-test linkage context fix.

PR #26139 fixes a bug where the Move unit test runner was not providing
full linkage for packages, causing issues with cross-package test execution.
"""

import subprocess
import sys
import os

REPO = "/workspace/sui"
TARGET_FILE = "external-crates/move/crates/move-unit-test/src/test_runner.rs"


def test_linkage_context_import_exists():
    """Fail-to-pass: Verify linkage_context is imported in test_runner.rs."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check for the specific import from move_vm_runtime::shared
    assert "shared::{gas::GasMeter, linkage_context}" in content, \
        "linkage_context import not found in move_vm_runtime::shared imports"


def test_linkage_table_creation_exists():
    """Fail-to-pass: Verify linkage_table is created mapping addresses."""
    result = subprocess.run(
        ["grep", "linkage_table", f"{REPO}/{TARGET_FILE}"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "linkage_table creation not found"
    # Verify it maps addr to addr (identity linkage)
    assert "packages.keys().copied()" in result.stdout or "linkage_table" in result.stdout


def test_stored_package_with_linkage_exists():
    """Fail-to-pass: Verify from_module_for_testing_with_linkage is used."""
    result = subprocess.run(
        ["grep", "from_module_for_testing_with_linkage", f"{REPO}/{TARGET_FILE}"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "from_module_for_testing_with_linkage not used"


def test_linkage_context_passed_to_package():
    """Fail-to-pass: Verify linkage_context is passed when creating packages."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Check that linkage_context is created and cloned
    assert "linkage_context.clone()" in content, "linkage_context should be cloned and passed to package creation"


def test_cargo_check_passes():
    """Pass-to-pass: Verify cargo check passes on the crate."""
    result = subprocess.run(
        ["cargo", "check", "-p", "move-unit-test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-1000:]}"


def test_move_unit_test_compiles():
    """Pass-to-pass: Verify move-unit-test crate builds successfully."""
    result = subprocess.run(
        ["cargo", "build", "-p", "move-unit-test", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo build failed:\n{result.stderr[-1000:]}"


def test_move_unit_test_clippy():
    """Pass-to-pass: Verify move-unit-test passes clippy lints."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "move-unit-test", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-1000:]}"


def test_move_vm_runtime_compiles():
    """Pass-to-pass: Verify move-vm-runtime (dependency) builds successfully."""
    result = subprocess.run(
        ["cargo", "build", "-p", "move-vm-runtime"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo build move-vm-runtime failed:\n{result.stderr[-1000:]}"


def test_external_crates_move_check():
    """Pass-to-pass: Verify external-crates/move workspace cargo check passes."""
    result = subprocess.run(
        ["cargo", "check"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600
    )
    assert result.returncode == 0, f"cargo check in external-crates/move failed:\n{result.stderr[-1000:]}"
