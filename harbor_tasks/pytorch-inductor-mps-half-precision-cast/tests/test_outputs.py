#!/usr/bin/env python3
"""Test outputs for the task.

This file contains:
- fail_to_pass tests: tests that should FAIL before the fix and PASS after
- pass_to_pass tests: tests that should PASS both before and after the fix
"""

import subprocess
import sys
from pathlib import Path

# REPO is the path inside the Docker container where the repo is mounted
REPO = "/workspace/repo"


def run(cmd, cwd=None, timeout=60):
    """Run a command and return the result."""
    return subprocess.run(
        cmd, shell=True, cwd=cwd or REPO, capture_output=True, text=True, timeout=timeout
    )


# =============================================================================
# FAIL TO PASS TESTS
# These test the actual fix - they should FAIL before and PASS after
# =============================================================================

def test_claude_md_uses_two_space_indent():
    """CLAUDE.md should use 2-space indentation, not 4-space (fail_to_pass)."""
    content = Path(f"{REPO}/CLAUDE.md").read_text()
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        # Check that indentation is not using 4-space as base
        # Lines starting with 4 spaces but not 8 or 12 etc. indicates 4-space base
        # We allow: 0-space, 2-space, 6-space, 10-space, etc. (2 + 4n)
        # We reject: 4-space, 8-space, 12-space, etc. (0 + 4n, where n>=1)
        #
        # Actually, let's simplify: just check no line starts with exactly 4 spaces
        # and that the file has been changed from the original (has some 2-space lines)
        if line.startswith("    ") and not line.startswith("        "):
            assert False, f"Line {i} uses 4-space base indent: {line[:60]}"

    # Verify the file was actually changed (has 2-space indentation)
    has_two_space = any(line.startswith("  ") and not line.startswith("    ") for line in lines)
    assert has_two_space, "File should have 2-space indentation after fix"


# =============================================================================
# PASS TO PASS TESTS
# These test that the repo stays functional - should PASS before AND after
# =============================================================================

def _setup_repo_for_testing():
    """Copy repo to writable location and install dependencies for testing."""
    # Copy repo to writable location inside container
    subprocess.run(["cp", "-r", REPO, "/tmp/writable-repo"], check=True)
    # Install package with test dependencies
    subprocess.run(
        ["pip", "install", "-e", ".[test]", "-q"],
        cwd="/tmp/writable-repo",
        capture_output=True,
    )
    return "/tmp/writable-repo"


def test_repo_harness_utils():
    """Repo harness utility tests pass (pass_to_pass)."""
    writable_repo = _setup_repo_for_testing()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_harness_utils.py", "-v", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=writable_repo,
    )
    assert r.returncode == 0, f"Harness utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_log_parsers_java():
    """Repo Java log parser tests pass (pass_to_pass)."""
    writable_repo = _setup_repo_for_testing()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_log_parsers_java.py", "-v", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=writable_repo,
    )
    assert r.returncode == 0, f"Log parsers tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_cli_smoke():
    """Repo CLI smoke test passes (pass_to_pass)."""
    writable_repo = _setup_repo_for_testing()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_cli.py::test_smoke_test", "-v", "-p", "no:cacheprovider"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=writable_repo,
    )
    assert r.returncode == 0, f"CLI smoke test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_version():
    """Repo package can be imported and has version (pass_to_pass)."""
    writable_repo = _setup_repo_for_testing()
    r = subprocess.run(
        ["python", "-c", "import swebench; print(swebench.__version__)"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=writable_repo,
    )
    assert r.returncode == 0, f"Import/version check failed:\n{r.stderr}"
