"""Tests for language-benchmarks MISSING_DEPENDENCY fix.

This PR fixes a MISSING_DEPENDENCY panic that occurs when benchmarks use Move stdlib functions.
The root cause: benchmark modules were at address 0x1 (same as stdlib), so publishing
at 0x1 overwrote the stdlib. The fix moves benchmarks to address 0x2 and publishes
stdlib separately at 0x1.
"""

import subprocess
import os
import sys

REPO = "/workspace/sui"
CRATE_PATH = f"{REPO}/external-crates/move/crates/language-benchmarks"


def test_bench_addr_constant_exists():
    """F2P: BENCH_ADDR constant must be defined."""
    with open(f"{CRATE_PATH}/src/move_vm.rs", "r") as f:
        content = f.read()

    assert "const BENCH_ADDR: AccountAddress" in content, "BENCH_ADDR constant not found"
    # Check that the address ends with , 2] which indicates address 0x2
    assert "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2" in content or "0, 2,\n]);" in content, \
        "BENCH_ADDR should be address 0x2"


def test_bench_addr_str_constant_exists():
    """F2P: BENCH_ADDR_STR constant must be defined as '0x2'."""
    result = subprocess.run(
        ["grep", "const BENCH_ADDR_STR: &str", f"{CRATE_PATH}/src/move_vm.rs"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, "BENCH_ADDR_STR constant not found"
    assert '"0x2"' in result.stdout, "BENCH_ADDR_STR should be '0x2'"


def test_publish_stdlib_function_exists():
    """F2P: publish_stdlib function must be defined to load stdlib."""
    with open(f"{CRATE_PATH}/src/move_vm.rs", "r") as f:
        content = f.read()
    assert "fn publish_stdlib(adapter" in content, "publish_stdlib function not found"


def test_named_addresses_insert_bench():
    """F2P: Compiler must use 'bench' named address mapped to 0x2."""
    with open(f"{CRATE_PATH}/src/move_vm.rs", "r") as f:
        content = f.read()

    # Check that named_addresses.insert is called with "bench"
    assert '"bench".to_string()' in content, "bench address name not inserted into named_addresses"


def test_bench_function_calls_publish_stdlib():
    """F2P: bench() function must call publish_stdlib before execute()."""
    with open(f"{CRATE_PATH}/src/move_vm.rs", "r") as f:
        content = f.read()

    # In the bench function, we need publish_stdlib to be called
    assert "publish_stdlib(&mut adapter)" in content, "publish_stdlib call not found"


def test_move_files_use_bench_address():
    """F2P: All .move benchmark files must use 0x2::bench module."""
    move_files = [
        "arith.move", "basic_alloc.move", "branch.move",
        "call.move", "loop.move", "natives.move",
        "transfers.move", "vector.move"
    ]

    for filename in move_files:
        filepath = f"{CRATE_PATH}/tests/{filename}"
        with open(filepath, "r") as f:
            content = f.read()

        assert "module 0x2::bench" in content, f"{filename} should declare module 0x2::bench"
        assert "module 0x1::bench" not in content, f"{filename} should NOT use 0x1::bench"


def test_call_move_uses_bench_xmodule_address():
    """F2P: call.move must use 0x2 for cross-module calls."""
    with open(f"{CRATE_PATH}/tests/call.move", "r") as f:
        content = f.read()

    assert "0x2::bench_xmodule_call" in content, "call.move should use 0x2::bench_xmodule_call"
    assert "module 0x2::bench_xmodule_call" in content, "bench_xmodule_call should be at 0x2"


def test_criterion_bench_function_calls_publish_stdlib():
    """F2P: All benchmarks must work - they compile and run without MISSING_DEPENDENCY."""
    # Run a quick benchmark test to verify no MISSING_DEPENDENCY panic
    result = subprocess.run(
        ["cargo", "bench", "-p", "language-benchmarks", "--", "--test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check for MISSING_DEPENDENCY in stderr
    stderr_lower = result.stderr.lower()
    stdout_lower = result.stdout.lower()

    assert "missing_dependency" not in stderr_lower, f"MISSING_DEPENDENCY error found in stderr: {result.stderr[-500:]}"
    assert "missing_dependency" not in stdout_lower, f"MISSING_DEPENDENCY error found in stdout: {result.stdout[-500:]}"
    assert "panic" not in stderr_lower, f"Panic found in stderr: {result.stderr[-500:]}"


def test_cross_module_disabled():
    """F2P: cross_module benchmark must be disabled (commented out)."""
    with open(f"{CRATE_PATH}/benches/criterion.rs", "r") as f:
        content = f.read()

    # cross_module should be commented out in the criterion_group
    assert "// cross_module" in content or "#[allow(dead_code)]" in content, \
        "cross_module should be commented out or marked dead_code"


def test_cargo_check_passes():
    """P2P: cargo check must pass on the crate."""
    # The package is in a workspace, check from the repo root
    result = subprocess.run(
        ["cargo", "check", "-p", "language-benchmarks"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo check failed: {result.stderr[-500:]}"


def test_move_files_compile():
    """P2P: Move files must compile successfully."""
    result = subprocess.run(
        ["cargo", "test", "-p", "language-benchmarks", "--", "--test-threads=1"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check that there are no actual compilation errors
    # The word "compiling" appears in normal output, but "error:" indicates actual issues
    stderr_lower = result.stderr.lower()
    assert "error:" not in stderr_lower, f"Compilation error: {result.stderr[-500:]}"
    # Also check the test passed (return code 0 means tests ran successfully)
    # Note: If there are no tests, cargo test returns 0, which is fine


def test_cargo_clippy_passes():
    """P2P: cargo clippy must pass on language-benchmarks (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "clippy", "-p", "language-benchmarks"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo clippy failed: {result.stderr[-500:]}"


def test_cargo_test_compile_passes():
    """P2P: cargo test --no-run must compile successfully (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "test", "-p", "language-benchmarks", "--no-run"],
        cwd=f"{REPO}/external-crates/move",
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"cargo test --no-run failed: {result.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
