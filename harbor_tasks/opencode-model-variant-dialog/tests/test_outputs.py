#!/usr/bin/env python3
"""Tests for the calculator module fix.

This file contains:
- Fail-to-pass tests: verify the bug fix works
- Pass-to-pass tests: verify existing functionality still works
"""

import subprocess
import sys
from pathlib import Path

# REPO path inside Docker container
REPO = "/workspace/calc-repo"


def test_divide_by_zero_raises_error():
    """divide() must raise ValueError when b is 0 (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/calc-repo/src')
from calc import divide
try:
    divide(10, 0)
    print("FAIL: No exception raised")
    sys.exit(1)
except ValueError as e:
    print("PASS: ValueError raised")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: Wrong exception type: {type(e).__name__}")
    sys.exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}"


def test_divide_error_message():
    """divide() must have correct error message (fail_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/calc-repo/src')
from calc import divide
try:
    divide(10, 0)
    print("FAIL: No exception raised")
    sys.exit(1)
except ValueError as e:
    if "Cannot divide by zero" in str(e):
        print("PASS: Correct error message")
        sys.exit(0)
    else:
        print(f"FAIL: Wrong message: {e}")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: Wrong exception type: {type(e).__name__}")
    sys.exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}"


def test_add_still_works():
    """add() must continue to work correctly (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/calc-repo/src')
from calc import add
result = add(2, 3)
if result == 5:
    print("PASS: add works")
    sys.exit(0)
else:
    print(f"FAIL: add(2, 3) = {result}, expected 5")
    sys.exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}"


def test_subtract_still_works():
    """subtract() must continue to work correctly (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/calc-repo/src')
from calc import subtract
result = subtract(5, 3)
if result == 2:
    print("PASS: subtract works")
    sys.exit(0)
else:
    print(f"FAIL: subtract(5, 3) = {result}, expected 2")
    sys.exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}"


def test_multiply_still_works():
    """multiply() must continue to work correctly (pass_to_pass)."""
    code = """
import sys
sys.path.insert(0, '/workspace/calc-repo/src')
from calc import multiply
result = multiply(4, 5)
if result == 20:
    print("PASS: multiply works")
    sys.exit(0)
else:
    print(f"FAIL: multiply(4, 5) = {result}, expected 20")
    sys.exit(1)
"""
    r = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stdout}"


def test_repo_pytest_add():
    """Repo's pytest for add() passes (pass_to_pass)."""
    r = subprocess.run(
        ["pytest", "tests/test_calc.py::test_add", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo test_add failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_pytest_subtract():
    """Repo's pytest for subtract() passes (pass_to_pass)."""
    r = subprocess.run(
        ["pytest", "tests/test_calc.py::test_subtract", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo test_subtract failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_pytest_multiply():
    """Repo's pytest for multiply() passes (pass_to_pass)."""
    r = subprocess.run(
        ["pytest", "tests/test_calc.py::test_multiply", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo test_multiply failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_pytest_divide():
    """Repo's pytest for divide() passes (pass_to_pass)."""
    r = subprocess.run(
        ["pytest", "tests/test_calc.py::test_divide", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo test_divide failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_pytest_all():
    """All repo pytest tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pytest", "tests/", "-v"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo pytest failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ruff_lint():
    """Repo's ruff linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "--no-cache", "src/"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"

