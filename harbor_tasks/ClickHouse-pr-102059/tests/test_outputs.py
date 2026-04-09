"""Tests for ClickHouse ZooKeeper session renewal fix.

This validates that the UDF refreshObjects function properly renews
the ZooKeeper session on retry iterations.
"""

import subprocess
import re
import sys
import ast
from pathlib import Path

import pytest

REPO = Path("/workspace/clickhouse")
TARGET_FILE = REPO / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def read_target_file():
    """Read the target C++ file."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def test_session_renewal_in_retry_loop():
    """
    Fail-to-pass: The retry loop must renew ZooKeeper session via zookeeper_getter.

    The fix ensures that on retry, a fresh session is obtained via
    zookeeper_getter.getZooKeeper().first instead of reusing the expired one.
    """
    content = read_target_file()

    # Find the retryLoop lambda and check its contents
    # Look for the pattern: current_zookeeper = zookeeper_getter.getZooKeeper().first
    # inside the retryLoop lambda
    retry_loop_pattern = r'retries_ctl\.retryLoop\(\[\&\]\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\)'
    retry_loop_match = re.search(retry_loop_pattern, content, re.DOTALL)

    if retry_loop_match:
        lambda_body = retry_loop_match.group(1)
        # Check for session renewal
        assert "zookeeper_getter.getZooKeeper().first" in lambda_body, \
            "Missing session renewal via zookeeper_getter.getZooKeeper().first in retry loop"
    else:
        # Fallback: just check it exists anywhere in the function
        assert "zookeeper_getter.getZooKeeper().first" in content, \
            "Missing session renewal via zookeeper_getter.getZooKeeper().first"


def test_current_zookeeper_variable_usage():
    """
    Fail-to-pass: The fix must declare and use current_zookeeper variable.

    Instead of using the passed-in 'zookeeper' parameter directly inside
    the retry loop, the fix uses 'current_zookeeper' which gets renewed.
    """
    content = read_target_file()

    # Check that current_zookeeper is declared
    assert "zkutil::ZooKeeperPtr current_zookeeper" in content, \
        "Missing declaration of current_zookeeper variable"

    # Check that current_zookeeper is initialized with zookeeper
    assert "current_zookeeper = zookeeper" in content or "current_zookeeper(zookeeper)" in content, \
        "current_zookeeper should be initialized with the zookeeper parameter"


def test_is_retry_conditional():
    """
    Fail-to-pass: Session renewal must only happen on retry (not first attempt).

    The fix adds: if (retries_ctl.isRetry()) current_zookeeper = ...
    """
    content = read_target_file()

    # Check for isRetry() conditional
    assert "retries_ctl.isRetry()" in content, \
        "Missing isRetry() check for conditional session renewal"


def test_object_names_fetch_inside_retry_loop():
    """
    Fail-to-pass: getObjectNamesAndSetWatch must be called inside the retry loop.

    Previously this was called before the retry loop. The fix moves it inside
    so that watches are re-established on the fresh session.
    """
    content = read_target_file()

    # Find the retryLoop lambda
    retry_loop_pattern = r'retries_ctl\.retryLoop\(\[\&\]\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\)'
    retry_loop_match = re.search(retry_loop_pattern, content, re.DOTALL)

    if retry_loop_match:
        lambda_body = retry_loop_match.group(1)
        # Check that getObjectNamesAndSetWatch is inside the loop
        assert "getObjectNamesAndSetWatch" in lambda_body, \
            "getObjectNamesAndSetWatch must be called inside the retry loop"
    else:
        pytest.skip("Could not locate retryLoop lambda for analysis")


def test_try_load_object_uses_current_zookeeper():
    """
    Fail-to-pass: tryLoadObject must use current_zookeeper, not the original zookeeper.

    This ensures we're using the potentially renewed session.
    """
    content = read_target_file()

    # Find the retryLoop lambda
    retry_loop_pattern = r'retries_ctl\.retryLoop\(\[\&\]\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\)'
    retry_loop_match = re.search(retry_loop_pattern, content, re.DOTALL)

    if retry_loop_match:
        lambda_body = retry_loop_match.group(1)
        # Check that tryLoadObject uses current_zookeeper inside the loop
        try_load_pattern = r'tryLoadObject\(\s*current_zookeeper\s*,'
        assert re.search(try_load_pattern, lambda_body), \
            "tryLoadObject should use current_zookeeper inside the retry loop"

        # Make sure it's NOT using the original zookeeper parameter
        old_pattern = r'tryLoadObject\(\s*zookeeper\s*,'
        if re.search(old_pattern, lambda_body):
            assert False, "tryLoadObject should NOT use 'zookeeper' parameter inside retry loop"
    else:
        # Fallback: check in full content
        assert "tryLoadObject(current_zookeeper" in content, \
            "tryLoadObject should use current_zookeeper"


def test_clang_syntax_check():
    """
    Pass-to-pass: The modified file should have valid C++ syntax.

    Uses clang to check for syntax errors without full compilation.
    """
    # Create a minimal compile commands approach or just check with clang -fsyntax-only
    # We need to handle includes properly
    cmd = [
        "clang", "-fsyntax-only", "-std=c++20",
        "-I" + str(REPO / "src"),
        "-I" + str(REPO / "base"),
        "-I" + str(REPO / "contrib"),
        "-Wno-everything",  # Suppress warnings, we only care about errors
        str(TARGET_FILE)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(REPO)
    )

    # Check return code - allow it to fail due to missing includes
    # but not due to actual syntax errors in our code
    # A return code of 0 means clean syntax
    # Non-zero could be due to missing headers which is OK for this test
    # We need to check stderr for actual syntax errors in our file

    stderr = result.stderr

    # Look for syntax errors specifically in our target file
    syntax_error_pattern = rf"{re.escape(str(TARGET_FILE))}:\d+:\d+: error:"
    syntax_errors = re.findall(syntax_error_pattern, stderr)

    # Filter out "file not found" errors which are OK (missing contrib deps)
    file_not_found_pattern = r"error: .* file not found"
    file_not_found_errors = re.findall(file_not_found_pattern, stderr)

    # If we have syntax errors that are NOT file-not-found errors, fail
    non_include_errors = [e for e in syntax_errors if not any(fnf in e for fnf in file_not_found_errors)]

    # This is a soft check - if we can't compile due to missing deps, skip
    if result.returncode != 0 and len(non_include_errors) == 0:
        pytest.skip(f"Syntax check skipped due to missing dependencies: {stderr[:500]}")

    assert len(non_include_errors) == 0, \
        f"C++ syntax errors found:\n{stderr}"


def test_repo_yaml_lint():
    """Repo's workflow YAML files pass yamllint (pass_to_pass)."""
    # Install yamllint if not present
    subprocess.run(
        ["pip3", "install", "yamllint", "-q", "--break-system-packages"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # Use relaxed yamllint config since the repo's .yamllint has a duplicate key
    yaml_config = """
extends: default
rules:
    document-start: disable
    line-length: disable
    trailing-spaces: disable
    truthy: disable
    indentation: disable
    comments: disable
    braces: disable
    brackets: disable
    colons: disable
    commas: disable
    empty-lines: disable
    empty-values: disable
    hyphens: disable
    key-duplicates: disable
    new-line-at-end-of-file: disable
    new-lines: disable
    octal-values: disable
    quoted-strings: disable
"""

    yaml_files = [
        ".github/workflows/pull_request.yml",
        ".github/workflows/master.yml",
    ]

    for yaml_file in yaml_files:
        file_path = REPO / yaml_file
        if not file_path.exists():
            continue
        r = subprocess.run(
            ["yamllint", "-d", yaml_config, str(file_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO)
        )
        assert r.returncode == 0, f"yamllint failed for {yaml_file}:\n{r.stdout}{r.stderr}"


def test_repo_python_syntax():
    """Repo's CI Python files have valid syntax (pass_to_pass)."""
    ci_dir = REPO / "ci"
    for py_file in ci_dir.rglob("*.py"):
        content = py_file.read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            assert False, f"Syntax error in {py_file}: {e}"


def test_target_file_no_trailing_whitespace():
    """Target C++ file has no trailing whitespace (pass_to_pass)."""
    content = TARGET_FILE.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        assert not line.endswith(" "), f"Trailing whitespace on line {i}"
        assert not line.endswith("\t"), f"Trailing tab on line {i}"


def test_target_file_final_newline():
    """Target C++ file ends with a newline (pass_to_pass)."""
    content = TARGET_FILE.read_text()
    assert content.endswith("\n"), "File must end with a newline"


def test_target_file_no_tabs():
    """Target C++ file uses spaces for indentation, not tabs (pass_to_pass)."""
    content = TARGET_FILE.read_text()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # Allow tabs in string literals but not in indentation
        stripped = line.lstrip()
        if stripped and not line.startswith(stripped):  # Has leading whitespace
            leading = line[:len(line) - len(stripped)]
            assert "\t" not in leading, f"Tab used for indentation on line {i}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
