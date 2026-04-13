#!/usr/bin/env python3
"""Test file for string_utils module bug fix validation."""

import subprocess
import sys
from pathlib import Path

# Docker-internal path to repo
REPO = "/workspace/repo"


# --- Fail-to-pass tests (from PR diff) ---

def test_normalize_whitespace_tabs():
    """The bug fix: normalize_whitespace should handle tabs correctly.

    This is a fail-to-pass test - it fails on the buggy code and passes after the fix.
    """
    # Run a test that exercises the bug
    r = subprocess.run(
        ["python", "-c",
         "import string_utils; result = string_utils.normalize_whitespace('hello\\tworld'); " +
         "assert result == 'hello world', f'Expected hello world, got {result}'; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Tab handling test failed: {r.stderr}"


def test_normalize_whitespace_newlines():
    """The bug fix: normalize_whitespace should handle newlines correctly."""
    r = subprocess.run(
        ["python", "-c",
         "import string_utils; result = string_utils.normalize_whitespace('hello\\n\\nworld'); " +
         "assert result == 'hello world', f'Expected hello world, got {result}'; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Newline handling test failed: {r.stderr}"


# --- Pass-to-pass tests (should pass before AND after the fix) ---

def test_module_imports():
    """Module can be imported (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import string_utils; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Import failed: {r.stderr}"


def test_to_title_case_works():
    """to_title_case function works correctly (pass_to_pass).

    This tests functionality that was not affected by the bug fix.
    """
    r = subprocess.run(
        ["python", "-c",
         "import string_utils; result = string_utils.to_title_case('hello world'); " +
         "assert result == 'Hello World', f'Expected Hello World, got {result}'; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"to_title_case test failed: {r.stderr}"


def test_normalize_whitespace_basic():
    """normalize_whitespace handles single spaces (pass_to_pass).

    This tests basic functionality that works both before and after the fix.
    Single spaces should pass through unchanged in both versions.
    """
    r = subprocess.run(
        ["python", "-c",
         "import string_utils; result = string_utils.normalize_whitespace('hello world'); " +
         "assert result == 'hello world', f'Expected hello world, got {result}'; print('OK')"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Single space test failed: {r.stderr}"


if __name__ == "__main__":
    tests = [
        # f2p tests - these should fail before fix, pass after
        test_normalize_whitespace_tabs,
        test_normalize_whitespace_newlines,
        # p2p tests - these should pass both before and after
        test_module_imports,
        test_to_title_case_works,
        test_normalize_whitespace_basic,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
