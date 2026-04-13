"""Tests for calculator fix - AFTER improvement (behavioral tests).

These tests execute actual code to verify behavior.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/calculator"


def _run_python(code: str, timeout: int = 10) -> subprocess.CompletedProcess:
    """Execute Python code and return the result."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_divide_by_zero_raises_exception():
    """Division by zero raises ZeroDivisionError (fail_to_pass)."""
    r = _run_python("""
from calculator import divide
try:
    divide(10, 0)
    print("ERROR: No exception raised")
except ZeroDivisionError as e:
    print(f"PASS: ZeroDivisionError raised: {e}")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS:" in r.stdout, f"Expected PASS, got: {r.stdout}"


def test_divide_by_zero_error_message():
    """ZeroDivisionError has correct message 'division by zero' (fail_to_pass)."""
    r = _run_python("""
from calculator import divide
try:
    divide(5, 0)
    print("ERROR: No exception raised")
except ZeroDivisionError as e:
    if "division by zero" in str(e):
        print("PASS: Correct error message")
    else:
        print(f"ERROR: Wrong message: {e}")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS:" in r.stdout, f"Expected correct error message, got: {r.stdout}"


def test_divide_normal_operation():
    """Normal division still works correctly (pass_to_pass)."""
    r = _run_python("""
from calculator import divide
result = divide(10, 2)
assert result == 5.0, f"Expected 5.0, got {result}"
print("PASS: Normal division works")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS:" in r.stdout


def test_add_still_works():
    """Addition operation works (pass_to_pass)."""
    r = _run_python("""
from calculator import add
result = add(2, 3)
assert result == 5, f"Expected 5, got {result}"
print("PASS: Addition works")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"


def test_subtract_still_works():
    """Subtraction operation works (pass_to_pass)."""
    r = _run_python("""
from calculator import subtract
result = subtract(5, 3)
assert result == 2, f"Expected 2, got {result}"
print("PASS: Subtraction works")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"


def test_multiply_still_works():
    """Multiplication operation works (pass_to_pass)."""
    r = _run_python("""
from calculator import multiply
result = multiply(3, 4)
assert result == 12, f"Expected 12, got {result}"
print("PASS: Multiplication works")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"


def test_python_syntax_valid():
    """Calculator module has valid Python syntax (static gate)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", f"{REPO}/calculator.py"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"
