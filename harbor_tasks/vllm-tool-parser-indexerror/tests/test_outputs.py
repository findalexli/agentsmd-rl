"""Tests for sum_numbers fix - AFTER improvement (behavioral version).

This version uses subprocess.run() to actually execute the code and verify
runtime behavior, not just grep for string patterns.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/task_repo"


def _run_python_code(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code and return the result."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ============================================================================
# FAIL-TO-PASS TESTS (must use subprocess.run() to execute actual code)
# These should FAIL on the base commit (broken) and PASS on the fix
# ============================================================================


def test_sum_numbers_returns_zero_for_empty_list():
    """sum_numbers([]) should return 0 (fail_to_pass - behavioral)."""
    # GOOD: Actually executes the function and checks the return value
    r = _run_python_code("""
import json
from mymath import sum_numbers
result = sum_numbers([])
print(json.dumps({"result": result, "type": type(result).__name__}))
""")
    assert r.returncode == 0, f"Code execution failed: {r.stderr}"

    # Parse the output and verify the actual behavior
    output = r.stdout.strip()
    data = json.loads(output.split("\n")[-1])  # Get last line

    # The core assertion: empty list must return 0, not None
    assert data["result"] == 0, f"Expected 0 for empty list, got {data['result']}"
    assert data["type"] == "int", f"Expected int type, got {data['type']}"


def test_sum_numbers_with_values_still_works():
    """sum_numbers with values should still work correctly (fail_to_pass)."""
    # GOOD: Verifies the fix doesn't break normal operation
    r = _run_python_code("""
from mymath import sum_numbers
# Test various inputs
test_cases = [
    ([1, 2, 3], 6),
    ([10], 10),
    ([-1, 1], 0),
    ([5, 5, 5], 15),
]
for inp, expected in test_cases:
    result = sum_numbers(inp)
    assert result == expected, f"sum_numbers({inp}) = {result}, expected {expected}"
print("PASS")
""")
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# ============================================================================
# PASS-TO-PASS TESTS (repo's own test suite or structural checks)
# These should pass on BOTH base commit AND the fix
# ============================================================================


def test_python_syntax_valid():
    """mymath.py has valid Python syntax (pass_to_pass - repo_tests)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/mymath.py"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


def test_function_exists():
    """sum_numbers function exists and is callable (pass_to_pass - static)."""
    r = _run_python_code("""
from mymath import sum_numbers
import inspect
assert callable(sum_numbers), "sum_numbers should be callable"
assert inspect.isfunction(sum_numbers), "sum_numbers should be a function"
print("PASS")
""")
    assert r.returncode == 0, f"Function check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_average_function_still_works():
    """average function should still work after the fix (pass_to_pass)."""
    r = _run_python_code("""
from mymath import average
# average uses sum_numbers internally, so this verifies compatibility
result = average([2, 4, 6])
assert result == 4.0, f"average([2, 4, 6]) = {result}, expected 4.0"
# Empty list for average should still return None (unchanged behavior)
empty_result = average([])
assert empty_result is None, f"average([]) should be None, got {empty_result}"
print("PASS")
""")
    assert r.returncode == 0, f"average test failed: {r.stderr}"
    assert "PASS" in r.stdout
