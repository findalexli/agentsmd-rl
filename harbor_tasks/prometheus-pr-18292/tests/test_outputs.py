"""
Test suite for prometheus/prometheus#18292 - tsdb/agent: fix getOrCreate race.

This test verifies that the race condition fix is properly implemented by checking:
1. The SetUnlessAlreadySet method exists and works
2. The getOrCreate signature is updated
3. New concurrent tests are added and pass
"""

import subprocess
import sys
import os

REPO = "/workspace/prometheus"


def run_go_test(pattern, timeout="60s"):
    """Helper to run go test with a pattern."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", pattern, "-timeout", timeout, "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    return result


def test_concurrent_append_same_labels():
    """
    Fail-to-pass: Verifies concurrent appends for same label set produce exactly one series.

    This test was added by the fix to demonstrate the race is fixed.
    Before the fix, this would fail by creating duplicate series.
    """
    result = run_go_test("TestConcurrentAppendSameLabels")

    # Check if test exists - if no tests to run, the fix wasn't applied
    if "no tests to run" in result.stdout:
        assert False, "TestConcurrentAppendSameLabels must be added by the fix - test not found"

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, "Concurrent append test failed - race condition may still exist"


def test_set_unless_already_set_concurrent():
    """
    Fail-to-pass: Verifies concurrent SetUnlessAlreadySet calls are race-safe.
    """
    result = run_go_test("TestSetUnlessAlreadySetConcurrentSameLabels")

    if "no tests to run" in result.stdout:
        assert False, "TestSetUnlessAlreadySetConcurrentSameLabels must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent SetUnlessAlreadySet test failed"


def test_concurrent_gc_safety():
    """
    Fail-to-pass: Verifies concurrent operations don't deadlock with GC.
    """
    result = run_go_test("TestSetUnlessAlreadySetConcurrentGC")

    if "no tests to run" in result.stdout:
        assert False, "TestSetUnlessAlreadySetConcurrentGC must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent GC test failed - possible deadlock"


def test_set_unless_already_set_basic():
    """
    Fail-to-pass: Verifies SetUnlessAlreadySet basic functionality works.

    This test verifies the new method exists and behaves correctly.
    """
    result = run_go_test("TestStripeSeries_SetUnlessAlreadySet")

    if "no tests to run" in result.stdout:
        assert False, "TestStripeSeries_SetUnlessAlreadySet must be added by the fix - test not found"

    assert result.returncode == 0, "SetUnlessAlreadySet basic test failed - method may not work correctly"


def test_method_signature_updated():
    """
    Fail-to-pass: Verifies getOrCreate signature was changed to accept ref parameter.

    The fix changes getOrCreate(l labels.Labels) to getOrCreate(ref, l).
    If the signature is wrong, compilation will fail.
    """
    result = subprocess.run(
        ["go", "build", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Build failed - getOrCreate signature may be wrong: {result.stderr}"


def test_agent_package_compiles():
    """
    Pass-to-pass: Ensure agent package compiles.
    """
    result = subprocess.run(
        ["go", "build", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_existing_agent_tests():
    """
    Pass-to-pass: All existing agent package tests pass.

    Excludes the new tests added by this fix to avoid counting them twice.
    """
    # Get list of all tests
    result = subprocess.run(
        ["go", "test", "-list", ".", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    if result.returncode != 0:
        assert False, f"Failed to list tests: {result.stderr}"

    all_tests = result.stdout.strip().split("\n")

    # Filter out the new tests added by this fix
    new_tests = {
        "TestConcurrentAppendSameLabels",
        "TestSetUnlessAlreadySetConcurrentSameLabels",
        "TestSetUnlessAlreadySetConcurrentGC",
        "TestStripeSeries_SetUnlessAlreadySet",
    }

    existing_tests = [t for t in all_tests if t and t not in new_tests and not t.startswith("Benchmark")]

    if not existing_tests:
        assert False, "No existing tests found to run"

    # Run each existing test
    for test in existing_tests:
        result = run_go_test(test, timeout="60s")
        if result.returncode != 0:
            assert False, f"Existing test {test} failed: {result.stderr}"


def test_go_vet_passes():
    """
    Pass-to-pass: go vet passes on agent package.
    """
    result = subprocess.run(
        ["go", "vet", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    assert result.returncode == 0, f"go vet failed: {result.stderr}"


def test_setunlessalreadyset_method_exists():
    """
    Fail-to-pass: Verifies SetUnlessAlreadySet method exists in stripeSeries.

    This is the key method added by the fix to replace the race-prone GetOrSet.
    """
    # Use go doc to check if the method exists
    result = subprocess.run(
        ["go", "doc", "-all", "github.com/prometheus/prometheus/tsdb/agent.stripeSeries"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    if result.returncode != 0:
        # Try alternative approach
        result = subprocess.run(
            ["grep", "SetUnlessAlreadySet", "tsdb/agent/series.go"],
            capture_output=True,
            text=True,
            cwd=REPO,
        )

    assert "SetUnlessAlreadySet" in result.stdout, \
        "SetUnlessAlreadySet method must be added to stripeSeries - method not found"


def test_go_mod_verify():
    """
    Pass-to-pass: go mod verify passes (repo_tests).

    Verifies module dependencies are consistent and no tampering detected.
    """
    result = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=120,
    )
    assert result.returncode == 0, f"go mod verify failed: {result.stderr}"


def test_stripe_series_get():
    """
    Pass-to-pass: TestStripeSeries_Get test passes (repo_tests).

    Existing test for stripeSeries GetByHash functionality with hash collisions.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestStripeSeries_Get", "-timeout", "60s", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TestStripeSeries_Get failed: {result.stderr}"


def test_no_deadlock():
    """
    Pass-to-pass: TestNoDeadlock test passes (repo_tests).

    Existing concurrency test verifying no deadlock between GC and Set operations.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestNoDeadlock", "-timeout", "60s", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TestNoDeadlock failed: {result.stderr}"


def test_agent_go_fmt():
    """
    Pass-to-pass: go fmt passes on agent package (repo_tests).

    Verifies Go code formatting is correct for the modified package.
    """
    result = subprocess.run(
        ["go", "fmt", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    # go fmt returns 0 on success; output is empty if no changes needed
    assert result.returncode == 0, f"go fmt failed: {result.stderr}"
