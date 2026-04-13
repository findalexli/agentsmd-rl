#!/usr/bin/env python3
"""Test output verification for the task."""

import os
import subprocess
import sys
from pathlib import Path

# REPO is the Docker-internal path where the repo lives inside the container
# This MUST match the Dockerfile's WORKDIR or where the repo is mounted
REPO = "/workspace/example-repo"

# Set cache directories to /tmp for read-only filesystem support
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["MYPY_CACHE_DIR"] = "/tmp/mypy_cache"
os.environ["RUFF_CACHE_DIR"] = "/tmp/ruff_cache"


# ============================================================================
# Fail-to-pass tests (verify the fix works)
# ============================================================================

def test_syntax_error_fixed():
    """Syntax error in utils.py is fixed (fail_to_pass)."""
    # Use PYTHONPYCACHEPREFIX to avoid writing to read-only filesystem
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"
    result = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/src/utils.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO, env=env,
    )
    assert result.returncode == 0, f"Syntax error still present: {result.stderr}"


def test_import_works():
    """Importing utils module works after fix (fail_to_pass)."""
    result = subprocess.run(
        ["python", "-c", "from src import utils; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Import failed: {result.stderr}"
    assert "OK" in result.stdout


# ============================================================================
# Pass-to-pass tests (repo_tests) - These should pass BEFORE and AFTER the fix
# ============================================================================

def test_repo_linter_passes():
    """Repo's ruff linter passes (pass_to_pass).

    Origin: .github/workflows/ci.yml - 'ruff check src/ tests/'
    """
    result = subprocess.run(
        ["ruff", "check", f"{REPO}/src/", f"{REPO}/tests/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}"


def test_repo_typecheck_passes():
    """Repo's mypy typecheck passes (pass_to_pass).

    Origin: .github/workflows/ci.yml - 'mypy src/ --ignore-missing-imports'
    """
    result = subprocess.run(
        ["mypy", f"{REPO}/src/", "--ignore-missing-imports"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Typecheck failed:\n{result.stderr[-500:]}"


def test_repo_unit_tests_specific():
    """Repo's unit tests for the modified module pass (pass_to_pass).

    Origin: .github/workflows/ci.yml - 'pytest tests/ -v'
    Focused on tests/test_utils.py which covers the modified src/utils.py
    """
    result = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/tests/test_utils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr[-500:]}"


def test_repo_imports_clean():
    """All repo imports work without error (pass_to_pass).

    Verifies the package structure is intact.
    """
    result = subprocess.run(
        ["python", "-c", "import src.utils; print('All imports OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Imports failed:\n{result.stderr}"
    assert "All imports OK" in result.stdout


def test_repo_py_compile():
    """All Python files compile without syntax errors (pass_to_pass).

    Origin: .github/workflows/ci.yml - Python syntax validation
    """
    env = os.environ.copy()
    env["PYTHONPYCACHEPREFIX"] = "/tmp/pycache"
    result = subprocess.run(
        ["python", "-m", "py_compile", f"{REPO}/src/utils.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO, env=env,
    )
    assert result.returncode == 0, f"Syntax check failed:\n{result.stderr}"


def test_repo_all_tests():
    """All repo unit tests pass (pass_to_pass).

    Origin: .github/workflows/ci.yml - 'pytest tests/ -v'
    Runs the full test suite for comprehensive coverage.
    """
    result = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/tests/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"Full test suite failed:\n{result.stderr[-500:]}"
