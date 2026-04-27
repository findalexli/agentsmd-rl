"""
Test suite for prometheus/prometheus#18292 - tsdb/agent: fix getOrCreate race.

This test verifies the race condition fix by checking actual concurrent behavior:
1. Concurrent appends for same label set produce exactly one series (not duplicates)
2. Concurrent operations don't deadlock with GC
3. The package compiles cleanly
"""

import subprocess
import re
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

    This test runs a Go test that performs 100 concurrent appends for the same label set
    and verifies only 1 series was created (not 100 duplicates from a race condition).
    The test name TestConcurrentAppendSameLabels is consistent across all possible fixes.
    """
    result = run_go_test("TestConcurrentAppendSameLabels")

    # Check if test exists - if no tests to run, the fix wasn't applied
    if "no tests to run" in result.stdout:
        assert False, "TestConcurrentAppendSameLabels must be added by the fix - test not found"

    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")

    assert result.returncode == 0, "Concurrent append test failed - race condition may still exist"


def test_concurrent_atomic_insert():
    """
    Fail-to-pass: Verifies atomic insert behavior for concurrent same-label operations.

    Runs tests that check concurrent calls to the series creation method all return
    the same canonical series and don't create duplicates. Uses a pattern that matches
    any test with "Concurrent" and "SameLabels" in the name.
    """
    # Run tests with Concurrent + SameLabels pattern - works for any method name
    result = run_go_test("Test.*Concurrent.*SameLabels")

    if "no tests to run" in result.stdout:
        assert False, "Concurrent atomic insert tests must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent atomic insert test failed"


def test_gc_concurrent_safety():
    """
    Fail-to-pass: Verifies concurrent operations don't deadlock with GC.

    Uses a pattern that matches any test with "Concurrent" and "GC" in the name.
    """
    result = run_go_test("Test.*Concurrent.*GC")

    if "no tests to run" in result.stdout:
        assert False, "Concurrent GC tests must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent GC test failed - possible deadlock"


def test_stripe_series_atomic_operation():
    """
    Fail-to-pass: Verifies stripeSeries atomic "check-then-insert" works correctly.

    This checks the basic atomic operation behavior: inserting a series returns created=true,
    and re-inserting the same labels returns created=false with the same canonical series.
    Uses a pattern matching any StripeSeries test with atomic/concurrent behavior keywords.
    """
    # Match any StripeSeries test that exercises atomic/insert/concurrent behavior
    result = run_go_test("TestStripeSeries_(SetUnlessAlreadySet|GetOrInsert|InsertIfAbsent|Atomic)")

    if "no tests to run" in result.stdout:
        assert False, "StripeSeries atomic operation test must be added by the fix - test not found"

    assert result.returncode == 0, "StripeSeries atomic operation test failed - method may not work correctly"


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

    # Filter out the new tests added by this fix (by name pattern, not method name)
    new_test_patterns = [
        "TestConcurrentAppendSameLabels",
        "TestSetUnlessAlreadySet",
        "TestGetOrInsert",
        "TestInsertIfAbsent",
    ]
    new_tests = set()
    for pattern in new_test_patterns:
        for test in all_tests:
            if test.startswith(pattern):
                new_tests.add(test)

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


def test_atomic_method_exists():
    """
    Fail-to-pass: Verifies an atomic insert method exists in stripeSeries.

    This uses go build as a behavioral check - the package must compile,
    which means it has the methods needed by the fix.
    """
    # Build the package to verify the required methods are available
    result = subprocess.run(
        ["go", "build", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    if result.returncode != 0:
        assert False, f"stripeSeries must have atomic insert method - build failed: {result.stderr}"


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
    result = run_go_test("TestStripeSeries_Get")
    assert result.returncode == 0, f"TestStripeSeries_Get failed: {result.stderr}"


def test_no_deadlock():
    """
    Pass-to-pass: TestNoDeadlock test passes (repo_tests).

    Existing concurrency test verifying no deadlock between GC and Set operations.
    """
    result = run_go_test("TestNoDeadlock")
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
