#!/usr/bin/env python3
"""Tests for calculator task.

Fail-to-pass: Tests that should fail before the fix and pass after.
Pass-to-pass: Tests that should pass both before and after the fix.
"""

import subprocess
import sys

REPO = "/workspace/calculator"


def test_divide_by_zero_fix():
    """FAIL_TO_PASS: Divide by zero raises ValueError with correct message."""
    code = '''
import sys
sys.path.insert(0, "/workspace/calculator")
from calculator import divide

try:
    divide(5, 0)
    print("FAIL: No exception raised")
    sys.exit(1)
except ValueError as e:
    if str(e) == "Cannot divide by zero":
        print("PASS: ValueError with correct message raised")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong message: {e}")
        sys.exit(1)
except ZeroDivisionError:
    print("FAIL: ZeroDivisionError raised instead of ValueError")
    sys.exit(1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
    assert r.returncode == 0, f"Test failed: {r.stdout}"


# =============================================================================
# Pass-to-Pass Tests (repo_tests origin - actual CI commands)
# =============================================================================


def test_repo_ruff_lint():
    """PASS_TO_PASS: Repo code passes ruff linter check (repo_tests)."""
    r = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # ruff returns 0 even with warnings, only fails on actual errors
    print(f"ruff stdout: {r.stdout}")
    print(f"ruff stderr: {r.stderr}")
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_unit_test_add():
    """PASS_TO_PASS: Repo unit test for add() passes (repo_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_calculator.py::test_add", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"pytest stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"pytest stderr: {r.stderr}")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_subtract():
    """PASS_TO_PASS: Repo unit test for subtract() passes (repo_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_calculator.py::test_subtract", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"pytest stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"pytest stderr: {r.stderr}")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_multiply():
    """PASS_TO_PASS: Repo unit test for multiply() passes (repo_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_calculator.py::test_multiply", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"pytest stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"pytest stderr: {r.stderr}")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_divide():
    """PASS_TO_PASS: Repo unit test for divide() (non-zero) passes (repo_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_calculator.py::test_divide", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"pytest stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"pytest stderr: {r.stderr}")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


def test_repo_unit_test_power():
    """PASS_TO_PASS: Repo unit test for power() passes (repo_tests)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_calculator.py::test_power", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"pytest stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"pytest stderr: {r.stderr}")
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


def test_repo_mypy_typecheck():
    """PASS_TO_PASS: Repo code passes mypy type check (repo_tests)."""
    r = subprocess.run(
        ["mypy", "calculator.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"mypy stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"mypy stderr: {r.stderr}")
    assert r.returncode == 0, f"Mypy type check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """PASS_TO_PASS: Repo code passes ruff format check (repo_tests)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "."],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    print(f"ruff format stdout: {r.stdout}")
    if r.returncode != 0:
        print(f"ruff format stderr: {r.stderr}")
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"
