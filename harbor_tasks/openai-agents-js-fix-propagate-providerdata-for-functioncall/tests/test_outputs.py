"""Tests for CaseInsensitiveDict pop() fix."""

import subprocess
import sys

REPO = "/workspace/requests"


# ────────────────────────────────────────────────────────────────────────────
# Pass-to-Pass Tests (repo_tests) - These tests should pass BEFORE and AFTER fix
# ────────────────────────────────────────────────────────────────────────────

def test_repo_structures_unit_tests():
    """Repo's unit tests for structures.py pass (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_structures.py", "-v"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Structures unit tests failed:\n{r.stderr[-1000:]}"


def test_repo_ruff_check():
    """Ruff linting passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/requests/structures.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


def test_repo_ruff_format():
    """Ruff formatting check passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/requests/structures.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


# ────────────────────────────────────────────────────────────────────────────
# Fail-to-Pass Tests (pr_diff) - These tests should FAIL before fix, PASS after
# ────────────────────────────────────────────────────────────────────────────

def test_case_insensitive_dict_pop_returns_default():
    """pop() should return default when key is not found (fail_to_pass)."""
    test_code = '''
import sys
sys.path.insert(0, "/workspace/requests/src")
from requests.structures import CaseInsensitiveDict

d = CaseInsensitiveDict()
d['Key'] = 'value'

# This should return 'default' instead of raising KeyError
result = d.pop('nonexistent', 'default')
assert result == 'default', f"Expected 'default', got {result!r}"

# Test that existing keys still work
result2 = d.pop('key')
assert result2 == 'value', f"Expected 'value', got {result2!r}"

print("All tests passed!")
'''
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr}\n{r.stdout}"


def test_case_insensitive_dict_pop_no_default():
    """pop() with no default should raise KeyError for missing key (fail_to_pass)."""
    test_code = '''
import sys
sys.path.insert(0, "/workspace/requests/src")
from requests.structures import CaseInsensitiveDict

d = CaseInsensitiveDict()

try:
    d.pop('nonexistent')
    print("ERROR: Should have raised KeyError")
    sys.exit(1)
except KeyError as e:
    print(f"Correctly raised KeyError: {e}")
    sys.exit(0)
'''
    r = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr}\n{r.stdout}"
