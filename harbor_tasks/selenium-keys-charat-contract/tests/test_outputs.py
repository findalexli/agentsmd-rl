"""Test outputs for Selenium Keys.charAt() fix.

This tests the fix for PR #17166 which ensures Keys.charAt() throws
IndexOutOfBoundsException for invalid indices instead of returning null character.
"""

import subprocess
import os
import re

REPO = "/workspace/selenium"
KEYS_JAVA = f"{REPO}/java/src/org/openqa/selenium/Keys.java"


def _run_bazel(command, timeout=600):
    """Run a bazel command in the selenium repo.

    Args:
        command: List of command arguments after 'bazel'
        timeout: Maximum time to wait in seconds

    Returns:
        CompletedProcess with returncode, stdout, stderr
    """
    return subprocess.run(
        ["bazel"] + command,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _read_keys_java():
    """Read the Keys.java source file."""
    with open(KEYS_JAVA, 'r') as f:
        return f.read()


def _extract_charat_method(content):
    """Extract the charAt method body from Keys.java."""
    # Find the charAt method using proper brace matching
    start = content.find('public char charAt(int index)')
    if start == -1:
        return None

    # Find the opening brace
    brace_start = content.find('{', start)
    if brace_start == -1:
        return None

    brace_count = 1
    end = brace_start + 1

    for i, c in enumerate(content[brace_start + 1:]):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end = brace_start + 2 + i
                break

    return content[start:end]


def test_charat_valid_index_returns_keycode():
    """Verify charAt(0) returns keyCode - the valid index behavior."""
    content = _read_keys_java()
    charat_method = _extract_charat_method(content)

    if not charat_method:
        raise AssertionError("Could not find charAt method in Keys.java")

    # Check that the method returns keyCode for valid input
    # Look for 'return keyCode;' (allowing for whitespace variations)
    if not re.search(r'return\s+keyCode\s*;', charat_method):
        raise AssertionError(
            "charAt() method should return 'keyCode' for valid index. "
            f"Method content: {charat_method[:200]}"
        )

    # Verify the method checks index validity before returning
    if not re.search(r'if\s*\(\s*index\s*!=?\s*0\s*\)', charat_method):
        raise AssertionError(
            "charAt() method should check index before returning. "
            f"Method content: {charat_method[:200]}"
        )


def test_charat_invalid_index_throws_exception():
    """Verify charAt(n != 0) throws IndexOutOfBoundsException - the core fix."""
    content = _read_keys_java()
    charat_method = _extract_charat_method(content)

    if not charat_method:
        raise AssertionError("Could not find charAt method in Keys.java")

    # Check for IndexOutOfBoundsException
    if 'IndexOutOfBoundsException' not in charat_method:
        raise AssertionError(
            "charAt() method should throw IndexOutOfBoundsException for invalid indices. "
            f"Method content: {charat_method[:200]}"
        )

    # Check that we check for invalid index first (index != 0)
    if not re.search(r'if\s*\(\s*index\s*!=\s*0\s*\)', charat_method):
        raise AssertionError(
            "charAt() method should have 'if (index != 0)' check to validate input. "
            f"Method content: {charat_method[:200]}"
        )

    # Verify throw comes before the return keyCode (by position in method)
    throw_pos = charat_method.find('throw')
    # Find the return statement (should be after the throw check)
    return_match = re.search(r'return\s+keyCode\s*;', charat_method)

    if throw_pos == -1:
        raise AssertionError("No 'throw' statement found in charAt method")

    if not return_match:
        raise AssertionError("No 'return keyCode;' found in charAt method")

    return_pos = return_match.start()

    if throw_pos > return_pos:
        raise AssertionError(
            "The throw statement should come BEFORE return keyCode in the method. "
            "Expected: check for invalid index first, then throw or return."
        )


def test_charat_negative_index_throws():
    """Verify charAt(-1) throws IndexOutOfBoundsException."""
    content = _read_keys_java()
    charat_method = _extract_charat_method(content)

    if not charat_method:
        raise AssertionError("Could not find charAt method in Keys.java")

    # The same check (index != 0) handles both positive and negative invalid indices
    if not re.search(r'if\s*\(\s*index\s*!=\s*0\s*\)', charat_method):
        raise AssertionError(
            "charAt() should check 'index != 0' which handles both positive and negative invalid indices. "
            f"Method content: {charat_method[:200]}"
        )

    if 'IndexOutOfBoundsException' not in charat_method:
        raise AssertionError(
            "charAt() should throw IndexOutOfBoundsException for invalid indices like -1"
        )


def test_keys_length_is_one():
    """Verify length() returns 1."""
    content = _read_keys_java()

    # Find the length() method
    pattern = r'public\s+int\s+length\s*\(\s*\)\s*\{\s*return\s+1;\s*\}'
    if not re.search(pattern, content):
        raise AssertionError(
            "length() method should return 1. "
            "This is part of the CharSequence contract that charAt depends on."
        )


def test_charat_code_structure():
    """Verify the charAt method has the correct structure (no 'return 0')."""
    content = _read_keys_java()
    charat_method = _extract_charat_method(content)

    if not charat_method:
        raise AssertionError("Could not find charAt method in Keys.java")

    # The OLD buggy behavior was: if (index == 0) { return keyCode; } return 0;
    # The NEW fixed behavior should NOT have 'return 0;'

    if re.search(r'return\s+0\s*;', charat_method) or re.search(r'return\s*\(\s*char\s*\)\s*0\s*;', charat_method):
        raise AssertionError(
            "BUG NOT FIXED: charAt() method still has 'return 0;' - should throw "
            "IndexOutOfBoundsException instead of returning null character. "
            f"Method content: {charat_method[:200]}"
        )

    # Verify the method has the correct pattern
    # Should check index != 0 first and throw
    pattern = r'if\s*\(\s*index\s*!=\s*0\s*\)\s*\{[^}]*throw\s+new\s+IndexOutOfBoundsException'
    if not re.search(pattern, charat_method):
        raise AssertionError(
            "charAt() method should have pattern: if (index != 0) { throw new IndexOutOfBoundsException(...) }"
        )

    # Verify exception message format includes index and length
    # Should contain something like "Index: " + index or "Index: ${index}"
    msg_pattern = r'Index:\s*["\']?\s*\+?\s*index|\+\s*index\s*\+|Index.*index'
    if not re.search(msg_pattern, charat_method):
        raise AssertionError(
            "Exception message should include the index value (e.g., 'Index: ' + index)"
        )

    if 'Length: 1' not in charat_method:
        raise AssertionError(
            "Exception message should include 'Length: 1'"
        )


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and fixed
# =============================================================================


def test_repo_build_core_lib():
    """Repo's core Java library builds successfully (pass_to_pass)."""
    r = _run_bazel(["build", "//java/src/org/openqa/selenium:core-lib"], timeout=120)
    assert r.returncode == 0, f"Core lib build failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_repo_build_client_combined():
    """Repo's client combined library builds successfully (pass_to_pass)."""
    r = _run_bazel(["build", "//java/src/org/openqa/selenium:client-combined-lib"], timeout=120)
    assert r.returncode == 0, f"Client combined lib build failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


