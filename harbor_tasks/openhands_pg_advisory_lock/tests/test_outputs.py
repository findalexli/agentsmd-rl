"""Tests for filename sanitization fix.

This module tests that the fix for preserving special characters in
uploaded filenames works correctly.
"""

import subprocess
import sys

# Docker-internal path to the repo
REPO = "/workspace/gradio"


def test_filename_with_special_chars():
    """Test that special characters are preserved in filenames (fail_to_pass).

    This test checks the core fix: filenames with special characters
    like parentheses, brackets, etc. should be preserved.
    """
    # Import the utils module
    sys.path.insert(0, f"{REPO}/client/python")
    from gradio_client.utils import strip_invalid_filename_characters

    # Test cases from the PR
    # These should preserve special characters
    assert strip_invalid_filename_characters("abc") == "abc"
    assert strip_invalid_filename_characters("$$AAabc&3") == "AAabc&3"
    assert strip_invalid_filename_characters("a#.txt") == "a#.txt"
    # Path traversal characters should be stripped
    assert strip_invalid_filename_characters("a/b\\c.txt") == "abc.txt"


def test_repo_lint():
    """Repo's Python linter passes (pass_to_pass).

    Runs ruff check on the modified code to ensure it follows the
    project's linting standards.
    """
    r = subprocess.run(
        ["python", "-m", "ruff", "check", "client/python/gradio_client/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_format():
    """Repo's Python code is properly formatted (pass_to_pass).

    Runs ruff format check to ensure the code follows the project's
    formatting standards.
    """
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", "client/python/gradio_client/utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests for modified module pass (pass_to_pass).

    Runs the existing unit tests for the utils module, excluding the
    filename sanitization tests which expect the old (pre-fix) behavior.
    """
    r = subprocess.run(
        ["python", "-m", "pytest", "client/python/test/test_utils.py", "-v",
         "--ignore-glob=*test_strip_invalid_filename_characters*",
         "-k", "not test_strip_invalid_filename_characters"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_import():
    """Modified module can be imported successfully (pass_to_pass).

    Verifies that the utils module can be imported without errors.
    """
    r = subprocess.run(
        ["python", "-c", "from gradio_client.utils import strip_invalid_filename_characters; print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
    assert "OK" in r.stdout, "Import did not return expected output"
