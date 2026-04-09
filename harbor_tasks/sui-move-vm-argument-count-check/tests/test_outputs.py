#!/usr/bin/env python3
"""Tests for Move VM argument count validation.

This module tests that the Move VM properly validates argument counts
before executing functions. The fix adds a check in `execute_function` that
verifies the number of value arguments matches the function signature.
"""

import subprocess
import sys
import os

REPO = "/workspace/sui"
# The move-vm-runtime crate is not a workspace member, so we must run from its directory
CRATE_DIR = f"{REPO}/external-crates/move/crates/move-vm-runtime"


def check_patch_applied() -> bool:
    """Check if the gold patch has been applied by looking for the arg count check."""
    vm_file = f"{CRATE_DIR}/src/execution/vm.rs"
    try:
        with open(vm_file, 'r') as f:
            content = f.read()
            return "NUMBER_OF_ARGUMENTS_MISMATCH" in content and "args.len() != function.to_ref().parameters.len()" in content
    except Exception:
        return False


def run_cargo_test(test_name: str = None, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run cargo test for the move-vm-runtime function_arg_tests."""
    cmd = ["cargo", "test", "--lib"]
    if test_name:
        cmd.append(test_name)
    cmd.extend(["--", "--nocapture"])

    return subprocess.run(
        cmd,
        cwd=CRATE_DIR,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def run_cargo_check() -> subprocess.CompletedProcess:
    """Run cargo check on the move-vm-runtime package."""
    return subprocess.run(
        ["cargo", "check"],
        cwd=CRATE_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )


def test_compilation():
    """FAIL-TO-PASS: Code compiles successfully.

    The fix modifies vm.rs and function_arg_tests.rs - both must compile.
    This catches any syntax or type errors introduced by the fix.
    """
    result = run_cargo_check()
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr[-2000:]}"


def test_argument_count_validation_in_code():
    """FAIL-TO-PASS: The NUMBER_OF_ARGUMENTS_MISMATCH check exists in vm.rs.

    This test verifies that the fix has been applied by checking that
    the argument count validation code exists in the VM.

    Before fix: The check is missing from vm.rs
    After fix: vm.rs contains the args.len() vs parameters.len() check
    """
    vm_file = f"{CRATE_DIR}/src/execution/vm.rs"
    with open(vm_file, 'r') as f:
        content = f.read()

    # Check that the argument count validation exists
    has_check = "args.len() != function.to_ref().parameters.len()" in content
    has_error = "NUMBER_OF_ARGUMENTS_MISMATCH" in content

    assert has_check, "Argument count check not found in vm.rs - fix not applied"
    assert has_error, "NUMBER_OF_ARGUMENTS_MISMATCH error not found in vm.rs - fix not applied"


def test_type_argument_count_validation_in_code():
    """FAIL-TO-PASS: The NUMBER_OF_TYPE_ARGUMENTS_MISMATCH check exists in vm.rs.

    This test verifies that the fix has been applied by checking that
    the type argument count validation code exists in the VM.
    """
    vm_file = f"{CRATE_DIR}/src/execution/vm.rs"
    with open(vm_file, 'r') as f:
        content = f.read()

    # Check that the type argument count validation exists
    has_check = "type_arguments.len() != function.to_ref().type_parameters().len()" in content
    has_error = "INTERNAL_TYPE_ERROR" in content

    assert has_check, "Type argument count check not found in vm.rs - fix not applied"
    assert has_error, "INTERNAL_TYPE_ERROR not found in vm.rs - fix not applied"


def test_unit_test_updated_to_direct_call():
    """FAIL-TO-PASS: Unit tests call execute_function_bypass_visibility directly.

    This test verifies that the unit tests have been updated to bypass
    the ValueFrame::serialized_call wrapper and test the VM directly.
    """
    test_file = f"{CRATE_DIR}/src/unit_tests/function_arg_tests.rs"
    with open(test_file, 'r') as f:
        content = f.read()

    # Check that tests use direct VM call (execute_function_bypass_visibility)
    has_direct_call = "execute_function_bypass_visibility" in content
    # Check that ValueFrame import was removed
    no_valueframe = "ValueFrame" not in content
    # Check that MoveValue import was removed (replaced with Value)
    no_movevalue = "MoveValue" not in content
    # Check that Value is imported
    has_value = "Value::" in content or "execution::{interpreter::locals::BaseHeap, values::Value}" in content

    assert has_direct_call, "Tests should call execute_function_bypass_visibility directly"
    assert has_value, "Tests should use Value instead of MoveValue"


def test_new_type_argument_tests_exist():
    """FAIL-TO-PASS: New type argument count mismatch tests exist.

    These tests are new tests added by the PR to test type argument validation.
    They don't exist on base commit.
    """
    test_file = f"{CRATE_DIR}/src/unit_tests/function_arg_tests.rs"
    with open(test_file, 'r') as f:
        content = f.read()

    # Check that the new type argument tests exist
    has_expected_0_ty_args_got_1 = "fn expected_0_ty_args_got_1" in content
    has_expected_1_ty_arg_got_0 = "fn expected_1_ty_arg_got_0" in content
    has_expected_1_ty_arg_got_2 = "fn expected_1_ty_arg_got_2" in content
    has_expected_2_ty_args_got_1 = "fn expected_2_ty_args_got_1" in content
    has_expected_2_ty_args_got_3 = "fn expected_2_ty_args_got_3" in content

    assert has_expected_0_ty_args_got_1, "New test expected_0_ty_args_got_1 not found"
    assert has_expected_1_ty_arg_got_0, "New test expected_1_ty_arg_got_0 not found"
    assert has_expected_1_ty_arg_got_2, "New test expected_1_ty_arg_got_2 not found"
    assert has_expected_2_ty_args_got_1, "New test expected_2_ty_args_got_1 not found"
    assert has_expected_2_ty_args_got_3, "New test expected_2_ty_args_got_3 not found"


def test_argument_count_test_behavior():
    """FAIL-TO-PASS: The expected_0_args_got_1 test passes and validates mismatch.

    This test verifies that the behavior test itself works correctly
    and validates NUMBER_OF_ARGUMENTS_MISMATCH.
    """
    result = run_cargo_test("expected_0_args_got_1")
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Test failed to run:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-2000:]}"


def test_type_argument_count_test_behavior():
    """FAIL-TO-PASS: The expected_0_ty_args_got_1 test passes and validates mismatch."""
    result = run_cargo_test("expected_0_ty_args_got_1")
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Test failed to run:\n{output[-2000:]}"
    assert "test result: ok" in output, f"Test did not pass:\n{output[-2000:]}"


def test_happy_path_u64_arg():
    """PASS-TO-PASS: Correct u64 argument passes validation.

    Verifies that valid argument counts still work correctly after the fix.
    """
    result = run_cargo_test("expected_u64_got_u64")
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Happy path test failed:\n{output[-2000:]}"


def test_happy_path_generic_T():
    """PASS-TO-PASS: Generic T=T with correct type arg passes.

    Verifies that generic function calls with correct type arguments
    still work correctly after the fix.
    """
    result = run_cargo_test("expected_T__T_got_u64__u64")
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Generic happy path test failed:\n{output[-2000:]}"


def test_function_arg_tests_suite():
    """PASS-TO-PASS: Full function_arg_tests test suite passes.

    Runs the complete test suite to ensure all tests pass after the fix.
    This validates both the new argument count checks and existing functionality.
    """
    result = run_cargo_test()
    output = result.stdout + result.stderr

    assert result.returncode == 0, f"Test suite failed:\n{output[-2000:]}"
    assert "test result: ok" in output, \
        f"Expected 'test result: ok' in output:\n{output[-1000:]}"


def run_cargo_check_repo() -> subprocess.CompletedProcess:
    """Run cargo check on the move-vm-runtime package (repo P2P)."""
    return subprocess.run(
        ["cargo", "check"],
        cwd=CRATE_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )


def run_cargo_clippy_repo() -> subprocess.CompletedProcess:
    """Run cargo clippy on the move-vm-runtime package (repo P2P)."""
    return subprocess.run(
        ["cargo", "clippy", "--all-targets"],
        cwd=CRATE_DIR,
        capture_output=True,
        text=True,
        timeout=300
    )


def run_cargo_fmt_check_repo() -> subprocess.CompletedProcess:
    """Run cargo fmt --check on the repo (repo P2P)."""
    return subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )


def test_repo_cargo_check():
    """PASS-TO-PASS: Repo CI cargo check passes on move-vm-runtime.

    Ensures the code compiles without errors per the repo's CI standards.
    Mirrors the check done in .github/workflows/external.yml.
    """
    result = run_cargo_check_repo()
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-2000:]}"


def test_repo_cargo_clippy():
    """PASS-TO-PASS: Repo CI cargo clippy passes on move-vm-runtime.

    Ensures the code passes linting per the repo's CI standards.
    Mirrors the check done in .github/workflows/external.yml.
    """
    result = run_cargo_clippy_repo()
    # Clippy may have warnings but should not fail (return non-zero)
    # On base commit, there are warnings but it should still pass
    assert result.returncode == 0, f"cargo clippy failed:\n{result.stderr[-2000:]}"


def test_repo_cargo_fmt():
    """PASS-TO-PASS: Repo CI cargo fmt --check passes.

    Ensures the code follows the repo's formatting standards.
    Mirrors the check done in .github/workflows/rust.yml and external.yml.
    """
    result = run_cargo_fmt_check_repo()
    assert result.returncode == 0, f"cargo fmt --check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
