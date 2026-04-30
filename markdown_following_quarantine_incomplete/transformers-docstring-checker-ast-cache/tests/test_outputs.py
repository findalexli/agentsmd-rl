#!/usr/bin/env python3
"""Test suite for calculator bug fix task.

This task involves fixing a divide-by-zero bug in calculator.py.
The fail_to_pass tests verify the fix works.
The pass_to_pass tests verify the repo's CI still passes.
"""

import subprocess
import sys
from pathlib import Path

# Docker-internal repo path - determined by Dockerfile WORKDIR
REPO = "/workspace/calculator"


def run_in_repo(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# =============================================================================
# FAIL TO PASS TESTS (must fail before fix, pass after fix)
# =============================================================================

def test_divide_by_zero_raises_error():
    """Division by zero should raise ValueError, not crash (fail_to_pass)."""
    result = run_in_repo([sys.executable, "-c",
        "from calculator import divide; divide(10, 0)"])
    # Before fix: this would crash with ZeroDivisionError
    # After fix: should get clean error message
    assert "ValueError" in result.stderr or "cannot divide" in result.stderr.lower(), \
        f"Expected ValueError for divide by zero, got: {result.stderr}"


def test_divide_normal_operation():
    """Normal division should work correctly (fail_to_pass)."""
    result = run_in_repo([sys.executable, "-c",
        "from calculator import divide; print(divide(10, 2))"])
    assert result.returncode == 0, f"Divide failed: {result.stderr}"
    assert "5" in result.stdout, f"Expected 5, got: {result.stdout}"


# =============================================================================
# PASS TO PASS TESTS (must pass before AND after fix)
# =============================================================================

def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass - repo_tests).

    Verifies that existing tests (except the divide-by-zero test) pass
    on the base commit. The test_divide_by_zero test will fail until
    the fix is applied, but the other 4 tests should pass.
    """
    result = run_in_repo([
        sys.executable, "-m", "pytest",
        "test_calculator.py",
        "-k", "not divide_by_zero",  # Exclude the failing test
        "-v"
    ], timeout=120)
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_repo_mypy_typecheck():
    """Repo's typecheck passes (pass_to_pass - repo_tests).

    Runs mypy to verify type annotations are correct.
    This is a lightweight check from the repo's actual CI.
    """
    result = run_in_repo([
        sys.executable, "-m", "mypy",
        ".",
        "--ignore-missing-imports",
    ], timeout=120)
    assert result.returncode == 0, f"mypy typecheck failed:\n{result.stderr[-500:]}"


def test_repo_ruff_lint():
    """Repo's linter passes (pass_to_pass - repo_tests).

    Runs ruff to check for Python linting issues.
    This matches the repo's actual CI workflow.
    """
    result = run_in_repo([
        "ruff", "check", "."
    ], timeout=120)
    assert result.returncode == 0, f"ruff lint failed:\n{result.stderr[-500:]}"


def test_repo_calculator_imports():
    """Calculator module can be imported without errors (pass_to_pass - repo_tests).

    Basic smoke test that the module loads correctly.
    """
    result = run_in_repo([
        sys.executable, "-c",
        "import calculator; print('calculator imported successfully')"
    ], timeout=30)
    assert result.returncode == 0, f"Import failed:\n{result.stderr[-500:]}"
    assert "successfully" in result.stdout, f"Import did not complete: {result.stdout}"


def test_repo_python_syntax():
    """Python syntax check passes (pass_to_pass - repo_tests).

    Verifies that calculator.py compiles without syntax errors.
    This is a basic smoke test for code validity.
    """
    result = run_in_repo([
        sys.executable, "-m", "py_compile",
        "calculator.py"
    ], timeout=30)
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr[-500:]}"


def test_repo_unit_test_add():
    """Unit test for add() passes (pass_to_pass - repo_tests).

    Runs the specific test for the add function to verify basic operation.
    """
    result = run_in_repo([
        sys.executable, "-m", "pytest",
        "test_calculator.py::TestCalculator::test_add",
        "-v"
    ], timeout=60)
    assert result.returncode == 0, f"add test failed:\n{result.stderr[-500:]}"


def test_repo_unit_test_subtract():
    """Unit test for subtract() passes (pass_to_pass - repo_tests).

    Runs the specific test for the subtract function to verify basic operation.
    """
    result = run_in_repo([
        sys.executable, "-m", "pytest",
        "test_calculator.py::TestCalculator::test_subtract",
        "-v"
    ], timeout=60)
    assert result.returncode == 0, f"subtract test failed:\n{result.stderr[-500:]}"


def test_repo_unit_test_multiply():
    """Unit test for multiply() passes (pass_to_pass - repo_tests).

    Runs the specific test for the multiply function to verify basic operation.
    """
    result = run_in_repo([
        sys.executable, "-m", "pytest",
        "test_calculator.py::TestCalculator::test_multiply",
        "-v"
    ], timeout=60)
    assert result.returncode == 0, f"multiply test failed:\n{result.stderr[-500:]}"


def test_repo_unit_test_divide_normal():
    """Unit test for divide() (normal case) passes (pass_to_pass - repo_tests).

    Runs the specific test for normal divide operation (not divide_by_zero).
    """
    result = run_in_repo([
        sys.executable, "-m", "pytest",
        "test_calculator.py::TestCalculator::test_divide",
        "-v"
    ], timeout=60)
    assert result.returncode == 0, f"divide test failed:\n{result.stderr[-500:]}"


# =============================================================================
# STATIC CHECKS (file existence, structure - origin: static)
# =============================================================================

def test_repo_structure():
    """Basic repo structure check (pass_to_pass - static)."""
    assert Path(f"{REPO}/calculator.py").exists(), "calculator.py not found"
    assert Path(f"{REPO}/test_calculator.py").exists(), "test_calculator.py not found"


def test_requirements_txt_exists():
    """Requirements file exists (pass_to_pass - static)."""
    assert Path(f"{REPO}/requirements.txt").exists(), "requirements.txt not found"


def test_pyproject_toml_exists():
    """pyproject.toml exists (pass_to_pass - static)."""
    assert Path(f"{REPO}/pyproject.toml").exists(), "pyproject.toml not found"


if __name__ == "__main__":
    # Run all tests
    import inspect

    tests = [obj for name, obj in inspect.getmembers(sys.modules[__name__])
             if inspect.isfunction(obj) and name.startswith("test_")]

    failed = []
    passed = []

    for test in tests:
        try:
            test()
            passed.append(test.__name__)
            print(f"PASS: {test.__name__}")
        except AssertionError as e:
            failed.append((test.__name__, str(e)))
            print(f"FAIL: {test.__name__}: {e}")
        except Exception as e:
            failed.append((test.__name__, str(e)))
            print(f"ERROR: {test.__name__}: {e}")

    print(f"\n{len(passed)} passed, {len(failed)} failed")
    sys.exit(0 if not failed else 1)
