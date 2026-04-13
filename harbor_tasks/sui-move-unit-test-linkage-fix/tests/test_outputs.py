#!/usr/bin/env python3
"""Tests for move-unit-test linkage fix.

This module validates that the PR fix for package linkage in the
move-unit-test runner has been properly applied.
"""

import subprocess
import os
import sys

REPO = "/workspace/sui"
TARGET_FILE = "external-crates/move/crates/move-unit-test/src/test_runner.rs"
FULL_TARGET_PATH = f"{REPO}/{TARGET_FILE}"


def test_compilation_move_unit_test():
    """FAIL_TO_PASS: move-unit-test crate compiles successfully.

    The fix must be applied for the code to compile correctly with
    the proper linkage context.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-unit-test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Compilation failed:\nstdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_linkage_context_import_present():
    """FAIL_TO_PASS: LinkageContext import is present in test_runner.rs.

    The fix adds the linkage_context import to properly handle package linkage.
    """
    with open(FULL_TARGET_PATH, "r") as f:
        content = f.read()

    # Check that linkage_context is imported
    assert "linkage_context" in content, (
        f"Missing linkage_context import in {TARGET_FILE}. "
        "The fix requires importing linkage_context from move_vm_runtime::shared."
    )

    # Check that LinkageContext is used
    assert "LinkageContext::new" in content, (
        f"Missing LinkageContext::new call in {TARGET_FILE}. "
        "The fix requires creating a LinkageContext with proper linkage table."
    )


def test_from_module_for_testing_with_linkage_used():
    """FAIL_TO_PASS: from_module_for_testing_with_linkage is used.

    The old from_modules_for_testing call must be replaced with
    from_module_for_testing_with_linkage.
    """
    with open(FULL_TARGET_PATH, "r") as f:
        content = f.read()

    # The new function should be present
    assert "from_module_for_testing_with_linkage" in content, (
        f"Missing from_module_for_testing_with_linkage call in {TARGET_FILE}. "
        "The fix must use this function instead of from_modules_for_testing."
    )

    # The old function should NOT be present (ensures replacement happened)
    assert "from_modules_for_testing(" not in content, (
        f"Old from_modules_for_testing call still present in {TARGET_FILE}. "
        "This function must be replaced with from_module_for_testing_with_linkage."
    )


def test_linkage_table_creation():
    """FAIL_TO_PASS: Linkage table is properly constructed.

    The fix creates a linkage table mapping package addresses to themselves
    for proper package linkage during testing.
    """
    with open(FULL_TARGET_PATH, "r") as f:
        content = f.read()

    # Check that linkage_table variable is created
    assert "linkage_table" in content, (
        f"Missing linkage_table variable in {TARGET_FILE}. "
        "The fix requires creating a linkage table from package addresses."
    )

    # Check that packages.keys() is used to build the table
    assert "packages.keys()" in content, (
        f"Missing packages.keys() usage in {TARGET_FILE}. "
        "The linkage table must be built from the package addresses."
    )


def test_repo_cargo_check_all():
    """PASS_TO_PASS: Cargo check passes for the move-unit-test crate.

    This test verifies the repository's own CI-style check passes.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-unit-test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo check failed:\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_cargo_clippy():
    """PASS_TO_PASS: Cargo clippy passes for the move-unit-test crate.

    This test verifies the repository's clippy linting passes.
    """
    result = subprocess.run(
        ["cargo", "clippy", "-p", "move-unit-test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo clippy failed:\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_cargo_test():
    """PASS_TO_PASS: Cargo test passes for the move-unit-test crate.

    This test verifies the repository's unit tests pass.
    Run from external-crates/move directory where move-unit-test is a workspace member.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "move-unit-test", "--", "--test-threads=4"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo test failed:\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_cargo_fmt():
    """PASS_TO_PASS: Cargo fmt check passes for move crates.

    This test verifies the repository's code formatting passes.
    Run from external-crates/move directory where move-unit-test is a workspace member.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo fmt check failed:\nstderr: {result.stderr[-500:]}"
    )


def test_repo_cargo_test_move_unit_test():
    """PASS_TO_PASS: Cargo test for move-unit-test crate passes (CI ref external.yml).

    This test runs the unit tests for the move-unit-test crate specifically,
    as referenced in the external.yml CI workflow.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "move-unit-test", "--", "--test-threads=4"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo test for move-unit-test failed:\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_cargo_check_move_vm_runtime():
    """PASS_TO_PASS: Cargo check for move-vm-runtime passes (PR dependency).

    The PR fix depends on linkage_context from move-vm-runtime.
    This test verifies the runtime crate compiles correctly.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-vm-runtime"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo check for move-vm-runtime failed:\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_cargo_check_move_stdlib():
    """PASS_TO_PASS: Cargo check for move-stdlib passes (test dependency).

    The move-unit-test crate depends on move-stdlib.
    This test verifies the stdlib crate compiles correctly.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-stdlib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Cargo check for move-stdlib failed:\nstderr: {result.stderr[-2000:]}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
