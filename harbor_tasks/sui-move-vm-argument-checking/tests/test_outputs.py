#!/usr/bin/env python3
"""
Test suite for Move VM argument checking fix.

This tests that the Move VM correctly validates:
1. Number of value arguments matches function parameters
2. Number of type arguments matches function type parameters
"""

import subprocess
import sys

REPO = "/workspace/sui"
MOVE_CRATES = "/workspace/sui/external-crates/move"
MOVE_VM_RUNTIME = "external-crates/move/crates/move-vm-runtime"


def run_cargo_test(test_filter, timeout=600):
    """Run cargo test with a specific filter."""
    cmd = [
        "cargo", "test",
        "-p", "move-vm-runtime",
        "--lib",
        "--", test_filter,
        "--nocapture"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=MOVE_CRATES)
    return result


def run_cargo_check(timeout=300):
    """Run cargo check on move-vm-runtime."""
    cmd = ["cargo", "check", "-p", "move-vm-runtime"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=MOVE_CRATES)
    return result


def run_cargo_check_all(timeout=300):
    """Run cargo check on all move crates."""
    cmd = ["cargo", "check", "--all"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=MOVE_CRATES)
    return result


def run_cargo_test_move_vm_runtime(timeout=600):
    """Run cargo test on move-vm-runtime --lib."""
    cmd = ["cargo", "test", "-p", "move-vm-runtime", "--lib"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=MOVE_CRATES)
    return result


def test_compilation():
    """Verify move-vm-runtime compiles successfully (p2p)."""
    result = run_cargo_check()
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_repo_cargo_check():
    """Repo's cargo check on move-vm-runtime passes (pass_to_pass)."""
    result = run_cargo_check(timeout=120)
    assert result.returncode == 0, f"cargo check failed:\n{result.stderr[-500:]}"


def test_repo_cargo_check_all():
    """Repo's cargo check on all move crates passes (pass_to_pass)."""
    result = run_cargo_check_all(timeout=180)
    assert result.returncode == 0, f"cargo check --all failed:\n{result.stderr[-500:]}"


def test_repo_cargo_test_move_vm_runtime():
    """Repo's cargo test on move-vm-runtime --lib passes (pass_to_pass)."""
    result = run_cargo_test_move_vm_runtime(timeout=120)
    assert result.returncode == 0, f"cargo test failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_argument_count_mismatch_0_expected_1_got():
    """Test that calling a function expecting 0 args with 1 arg fails (f2p)."""
    result = run_cargo_test("expected_0_args_got_1")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_argument_count_mismatch_1_expected_0_got():
    """Test that calling a function expecting 1 arg with 0 args fails (f2p)."""
    result = run_cargo_test("expected_1_arg_got_0")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_argument_count_mismatch_2_expected_1_got():
    """Test that calling a function expecting 2 args with 1 arg fails (f2p)."""
    result = run_cargo_test("expected_2_arg_got_1")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_argument_count_mismatch_2_expected_3_got():
    """Test that calling a function expecting 2 args with 3 args fails (f2p)."""
    result = run_cargo_test("expected_2_arg_got_3")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_type_argument_count_mismatch_0_expected_1_got():
    """Test that calling a generic function with 0 type args fails (f2p)."""
    result = run_cargo_test("expected_1_ty_arg_got_0")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_type_argument_count_mismatch_1_expected_2_got():
    """Test that calling a generic function expecting 1 type arg with 2 fails (f2p)."""
    result = run_cargo_test("expected_1_ty_arg_got_2")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_type_argument_count_mismatch_non_generic_with_args():
    """Test that calling a non-generic function with type args fails (f2p)."""
    result = run_cargo_test("expected_0_ty_args_got_1")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_type_argument_count_mismatch_2_expected_1_got():
    """Test that calling a function expecting 2 type args with 1 fails (f2p)."""
    result = run_cargo_test("expected_2_ty_args_got_1")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_type_argument_count_mismatch_2_expected_3_got():
    """Test that calling a function expecting 2 type args with 3 fails (f2p)."""
    result = run_cargo_test("expected_2_ty_args_got_3")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_argument_count_happy_path_0_args():
    """Test that calling a function with correct 0 args succeeds (p2p)."""
    result = run_cargo_test("expected_0_args_got_0")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_argument_count_happy_path_1_arg():
    """Test that calling a function with correct 1 arg succeeds (p2p)."""
    result = run_cargo_test("expected_u64_got_u64")
    assert result.returncode == 0, f"Test failed:\n{result.stdout}\n{result.stderr}"


def test_vm_code_present():
    """Verify the VM argument checking code is present."""
    vm_file = f"{REPO}/{MOVE_VM_RUNTIME}/src/execution/vm.rs"
    with open(vm_file, 'r') as f:
        content = f.read()

    # Check for the distinctive lines from the patch
    assert "argument length mismatch: expected" in content, \
        "Argument length check not found in vm.rs"
    assert "type argument length mismatch: expected" in content, \
        "Type argument length check not found in vm.rs"
    assert "NUMBER_OF_ARGUMENTS_MISMATCH" in content, \
        "NUMBER_OF_ARGUMENTS_MISMATCH error not found"
    assert "INTERNAL_TYPE_ERROR" in content, \
        "INTERNAL_TYPE_ERROR error not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
