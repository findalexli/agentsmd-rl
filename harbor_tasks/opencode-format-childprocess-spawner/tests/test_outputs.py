"""Test outputs validation for taskforge sample task."""

import subprocess
import sys

# Docker-internal path to the repo
REPO = "/workspace/taskforge"


def test_edge_case_handling():
    """Fail-to-pass: is_code_file handles files without extensions (PR fix)."""
    from taskforge.config import is_code_file

    # Files without extensions should be considered code (e.g., executable scripts)
    assert is_code_file("Makefile") is True, "Makefile should be a code file"
    assert is_code_file("script") is True, "script without extension should be a code file"


def test_no_regression():
    """Pass-to-pass: existing is_code_file tests still work (repo_tests)."""
    from taskforge.config import is_code_file, is_config_file

    # Standard cases that should work before and after the fix
    assert is_code_file("src/main.py") is True
    assert is_config_file("CLAUDE.md") is True
    assert is_code_file("README.md") is False
    assert is_code_file("docs/guide.md") is False


# ============================================================================
# CI/CD Pass-to-Pass Tests (origin: repo_tests)
# These tests run actual CI commands that should pass on both base and fix.
# ============================================================================


def test_repo_python_syntax():
    """Python syntax check passes on all taskforge modules (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-m", "py_compile",
            f"{REPO}/taskforge/config.py",
            f"{REPO}/taskforge/models.py",
            f"{REPO}/taskforge/judge.py",
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_import_config():
    """taskforge.config module imports successfully (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            "from taskforge.config import is_code_file, is_config_file, "
            "is_agent_instruction_file, is_doc_file; print('OK')",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"
    assert "OK" in r.stdout, f"Expected 'OK' output, got: {r.stdout}"


def test_repo_is_code_file_logic():
    """is_code_file logic works correctly (pass_to_pass)."""
    r = subprocess.run(
        [
            "python", "-c",
            "from taskforge.config import is_code_file, is_config_file; "
            "assert is_code_file('src/main.py') == True; "
            "assert is_config_file('CLAUDE.md') == True; "
            "assert is_code_file('README.md') == False; "
            "assert is_code_file('docs/guide.md') == False; "
            "print('All assertions passed')",
        ],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Logic test failed:\n{r.stderr}"
    assert "All assertions passed" in r.stdout, f"Expected success output, got: {r.stdout}"
