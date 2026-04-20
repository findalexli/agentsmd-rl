"""
Benchmark test_outputs.py for mantinedev/mantine#8622
TimePicker: Fix TimePicker clearing in uncontrolled mode not propagating empty value

Fail-to-pass tests:
  - test_new_backspace_test_exists_and_passes: The new test added by the fix
    ("calls onChange when cleared with backspace in uncontrolled mode") must exist
    and pass. On base commit: test does not exist → jest reports "0 of 1 total"
    with all skipped → FAIL. After fix: test runs and passes → PASS.

Pass-to-pass tests:
  - test_timepicker_full_suite_passes: TimePicker test suite passes (sanity check)
  - test_dates_package_tests_pass: Full dates package tests pass (68 suites, 1926 tests)
  - test_repo_prettier_check: Prettier code style check on modified files passes
  - test_repo_eslint_check: ESLint on modified files passes
  - test_repo_syncpack_check: syncpack package.json consistency passes
"""

import subprocess

REPO = "/workspace/mantine_repo"


def test_new_backspace_test_exists_and_passes():
    """
    The fix for mantinedev/mantine#8622 adds a new test:
    'calls onChange when cleared with backspace in uncontrolled mode'

    On the base commit (a6f627b), this test does not exist. Jest's --testNamePattern
    filter matches 0 tests, so it reports "0 of 1 total" with all skipped. We detect
    this and FAIL.

    After applying the fix, the test exists and passes (✓ shown in output).

    This is a fail-to-pass test: base=FAIL(0 passing tests), fixed=PASS(1 passing test).
    """
    r = subprocess.run(
        [
            "yarn", "jest",
            "packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx",
            "--testNamePattern", "calls onChange when cleared with backspace in uncontrolled mode",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Check that the test actually ran and passed (not skipped)
    # Jest reports "0 of 1 total" when no tests match the filter
    assert "0 of 1 total" not in r.stderr, (
        f"Test 'calls onChange when cleared with backspace in uncontrolled mode' "
        f"does not exist on base commit (0 tests matched filter).\n"
        f"stderr: {r.stderr[-500:]}"
    )
    # Verify the test passed
    assert "✓ calls onChange when cleared with backspace in uncontrolled mode" in r.stderr, (
        f"Test did not pass as expected.\n"
        f"stderr: {r.stderr[-500:]}"
    )


def test_timepicker_full_suite_passes():
    """
    Pass-to-pass sanity check: the full TimePicker test suite runs and passes.
    This verifies the repo's test infrastructure is working correctly.
    """
    r = subprocess.run(
        [
            "yarn", "jest",
            "packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"TimePicker test suite failed to pass.\n"
        f"stderr: {r.stderr[-500:]}"
    )
    # Sanity check: at least some tests should pass
    assert "1 passed" in r.stderr or "passed, 1 total" in r.stderr or "Test Suites: 1 passed" in r.stderr, (
        f"Unexpected jest output format:\n{r.stderr[-500:]}"
    )


def test_dates_package_tests_pass():
    """
    Repo dates package tests pass (pass_to_pass).
    Covers the modified TimePicker module in the context of the broader dates package.
    """
    r = subprocess.run(
        ["yarn", "jest", "packages/@mantine/dates", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"dates package tests failed.\n"
        f"stderr: {r.stderr[-500:]}"
    )
    assert "Test Suites:" in r.stderr and "passed" in r.stderr, (
        f"Unexpected jest output:\n{r.stderr[-500:]}"
    )


def test_repo_prettier_check():
    """
    Repo code style (prettier) check passes on modified files (pass_to_pass).
    """
    r = subprocess.run(
        [
            "npx", "prettier", "--check",
            "packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx",
            "packages/@mantine/dates/src/components/TimePicker/use-time-picker.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"prettier check failed on modified files.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}"
    )


def test_repo_eslint_check():
    """
    Repo linter (eslint) passes on modified files (pass_to_pass).
    """
    r = subprocess.run(
        [
            "npx", "eslint", "--cache",
            "packages/@mantine/dates/src/components/TimePicker/TimePicker.test.tsx",
            "packages/@mantine/dates/src/components/TimePicker/use-time-picker.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"eslint check failed on modified files.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}"
    )


def test_repo_syncpack_check():
    """
    Repo package.json consistency (syncpack) passes (pass_to_pass).
    """
    r = subprocess.run(
        ["npm", "run", "syncpack"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"syncpack check failed.\n"
        f"stdout: {r.stdout[-500:]}\n"
        f"stderr: {r.stderr[-500:]}"
    )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])