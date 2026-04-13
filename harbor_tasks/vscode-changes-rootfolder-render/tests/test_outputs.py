#!/usr/bin/env python3
"""Fail-to-pass tests for ruff repository fixes.

These tests verify that solve.sh correctly fixes:
- Formatting issues in the parser crate
- Unused variable warnings (clippy)
- Code that doesn't compile properly
"""

import subprocess
import sys
from pathlib import Path

# REPO path inside the Docker container
REPO = "/workspace/ruff"


def test_parser_no_fmt_issues():
    """Parser crate has no formatting issues after fix (fail_to_pass).

    origin: solve_fix
    type: fail_to_pass
    """
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --all --check found issues:\n{r.stderr[-2000:]}\n{r.stdout[-2000:]}"


def test_parser_no_clippy_warnings():
    """Parser crate has no clippy warnings after fix (fail_to_pass).

    origin: solve_fix
    type: fail_to_pass
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ruff_python_parser", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p ruff_python_parser found warnings:\n{r.stderr[-2000:]}\n{r.stdout[-2000:]}"


def test_parser_compiles():
    """Parser crate compiles successfully after fix (fail_to_pass).

    origin: solve_fix
    type: fail_to_pass
    """
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_python_parser"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ruff_python_parser failed:\n{r.stderr[-2000:]}\n{r.stdout[-2000:]}"


def test_no_bad_code_in_lib():
    """Badly formatted code has been removed from lib.rs (fail_to_pass).

    origin: solve_fix
    type: fail_to_pass
    """
    lib_rs = Path(f"{REPO}/crates/ruff_python_parser/src/lib.rs")
    content = lib_rs.read_text()
    # Check that the badly formatted code is not present
    assert "badly_formatted" not in content, "Found badly_formatted function that should have been removed"
    assert "let unused=1" not in content, "Found badly formatted code that should have been removed"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
