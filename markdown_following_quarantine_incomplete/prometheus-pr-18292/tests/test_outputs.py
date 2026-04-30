"""
Test suite for prometheus/prometheus#18292 - tsdb/agent: fix getOrCreate race.

This test verifies the race condition fix by checking actual concurrent behavior:
1. Concurrent appends for same label set produce exactly one series (not duplicates)
2. Concurrent operations do not deadlock with GC
3. The package compiles cleanly
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

    Runs a Go test that performs 100 concurrent appends for the same label set
    and verifies only 1 series was created (not 100 duplicates from a race condition).
    """
    result = run_go_test("TestConcurrentAppendSameLabels")

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
    the same canonical series and do not create duplicates.
    """
    result = run_go_test("Test.*Concurrent.*SameLabels")

    if "no tests to run" in result.stdout:
        assert False, "Concurrent atomic insert tests must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent atomic insert test failed"


def test_gc_concurrent_safety():
    """
    Fail-to-pass: Verifies concurrent operations do not deadlock with GC.

    Uses a pattern that matches any test with "Concurrent" and "GC" in the name.
    """
    result = run_go_test("Test.*Concurrent.*GC")

    if "no tests to run" in result.stdout:
        assert False, "Concurrent GC tests must be added by the fix - test not found"

    assert result.returncode == 0, "Concurrent GC test failed - possible deadlock"


def test_stripe_series_atomic_operation():
    """
    Fail-to-pass: Verifies stripeSeries atomic "check-then-insert" works correctly.

    Checks the basic atomic operation behavior: inserting a series returns created=true,
    and re-inserting the same labels returns created=false with the same canonical series.
    """
    result = run_go_test("TestStripeSeries_(SetUnlessAlreadySet|GetOrInsert|InsertIfAbsent|Atomic)")

    if "no tests to run" in result.stdout:
        assert False, "StripeSeries atomic operation test must be added by the fix - test not found"

    assert result.returncode == 0, "StripeSeries atomic operation test failed - method may not work correctly"


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
    result = subprocess.run(
        ["go", "test", "-list", ".", "./tsdb/agent/"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )

    if result.returncode != 0:
        assert False, f"Failed to list tests: {result.stderr}"

    all_tests = result.stdout.strip().split("\n")

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
    assert result.returncode == 0, f"go fmt failed: {result.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_ui_tests_make():
    """pass_to_pass | CI job 'UI tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make assets-tarball'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_ui_tests_make_2():
    """pass_to_pass | CI job 'UI tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make ui-lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_ui_tests_make_3():
    """pass_to_pass | CI job 'UI tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make ui-test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_golangci_lint_get_golangci_lint_version():
    """pass_to_pass | CI job 'golangci-lint' → step 'Get golangci-lint version'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "version=$(make print-golangci-lint-version)" >> $GITHUB_OUTPUT'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Get golangci-lint version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_go_tests_on_windows_make():
    """pass_to_pass | CI job 'Go tests on Windows' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make GO_ONLY=1 SKIP_GOLANGCI_LINT=1'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_go_tests_on_windows_go():
    """pass_to_pass | CI job 'Go tests on Windows' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'go test ./tsdb/ -test.tsdb-isolation=false'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_go_tests_on_windows_make_2():
    """pass_to_pass | CI job 'Go tests on Windows' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make -C documentation/examples/remote_storage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_go_tests_on_windows_make_3():
    """pass_to_pass | CI job 'Go tests on Windows' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make -C documentation/examples'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_generated_parser_make():
    """pass_to_pass | CI job 'Check generated parser' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make install-goyacc check-generated-parser'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_generated_parser_make_2():
    """pass_to_pass | CI job 'Check generated parser' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make check-generated-promql-functions'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_mixins_tests_make():
    """pass_to_pass | CI job 'Mixins tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make -C documentation/prometheus-mixin clean'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_mixins_tests_make_2():
    """pass_to_pass | CI job 'Mixins tests' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'make -C documentation/prometheus-mixin jb_install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")