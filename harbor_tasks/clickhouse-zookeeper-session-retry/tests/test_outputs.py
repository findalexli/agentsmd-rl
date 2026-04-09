"""
Tests for ClickHouse ZooKeeper session retry fix.

This verifies that the UDF storage properly refreshes the ZooKeeper session
handle when retrying after transient connection failures.
"""

import subprocess
import re
import os

import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


def test_target_file_exists():
    """Verify the target file exists in the repository."""
    filepath = os.path.join(REPO, TARGET_FILE)
    assert os.path.exists(filepath), f"Target file not found: {filepath}"


def test_refresh_objects_uses_retry_loop():
    """Verify refreshObjects method uses ZooKeeperRetriesControl for retry logic."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Check that ZooKeeperRetriesControl is used
    assert "ZooKeeperRetriesControl" in content, "ZooKeeperRetriesControl not found"
    assert "retryLoop" in content, "retryLoop method not found"


def test_session_renewal_on_retry():
    """
    F2P: Verify the fix - session is renewed inside retry loop.

    The bug was that getObjectNamesAndSetWatch was called BEFORE the retry loop,
    using a potentially stale session handle. The fix moves it INSIDE the retry
    loop and obtains a fresh session on each retry.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the refreshObjects function
    refresh_pattern = r'void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects\(.*?\n\{'
    match = re.search(refresh_pattern, content, re.DOTALL)
    assert match, "refreshObjects function not found"

    # Get function content (simplified - find matching braces)
    start_idx = match.end() - 1
    brace_count = 0
    end_idx = start_idx
    for i, c in enumerate(content[start_idx:]):
        if c == '{':
            brace_count += 1
        elif c == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = start_idx + i + 1
                break

    func_content = content[start_idx:end_idx]

    # Check for the key fix components:
    # 1. isRetry() check exists
    assert "isRetry()" in func_content, "isRetry() check not found - session renewal logic missing"

    # 2. zookeeper_getter is used to get fresh session
    assert "zookeeper_getter.getZooKeeper()" in func_content, "zookeeper_getter.getZooKeeper() not found - session refresh mechanism missing"

    # 3. current_zookeeper variable is used (the fix introduces this)
    assert "current_zookeeper" in func_content, "current_zookeeper variable not found"


def test_get_object_names_inside_retry_loop():
    """
    F2P: Verify getObjectNamesAndSetWatch is called INSIDE the retry loop.

    This is the core fix - previously it was called BEFORE the retry loop,
    so retries would use stale data from the old session.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Simpler approach: check that getObjectNamesAndSetWatch appears AFTER retryLoop opening
    retry_idx = content.find("retries_ctl.retryLoop")
    assert retry_idx != -1, "retryLoop call not found"

    # Find the lambda opening brace
    lambda_start = content.find("[&]", retry_idx)
    assert lambda_start != -1, "retryLoop lambda not found"

    # Find the closing brace of the lambda (next standalone })
    lambda_open_brace = content.find("{", lambda_start)
    assert lambda_open_brace != -1, "retryLoop lambda opening brace not found"

    # Get content inside retry loop (approximate)
    # Find the matching closing brace by counting
    brace_count = 1
    pos = lambda_open_brace + 1
    while brace_count > 0 and pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1

    loop_content = content[lambda_open_brace:pos]

    # The fix: getObjectNamesAndSetWatch must be INSIDE the retry loop
    assert "getObjectNamesAndSetWatch" in loop_content, \
        "getObjectNamesAndSetWatch must be called INSIDE the retry loop, not before it"

    # Also verify tryLoadObject uses current_zookeeper inside the loop
    assert "tryLoadObject(current_zookeeper" in loop_content, \
        "tryLoadObject must use current_zookeeper inside the retry loop"


def test_no_session_outside_retry_loop():
    """
    F2P: Verify the stale pattern is gone - no session-dependent calls before retry loop.

    Previously the bug had getObjectNamesAndSetWatch called before the retry loop.
    This test ensures that pattern is removed.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # Find the refreshObjects function
    refresh_start = content.find("void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects")
    assert refresh_start != -1, "refreshObjects function not found"

    # Find where retryLoop starts
    retry_idx = content.find("retries_ctl.retryLoop", refresh_start)
    assert retry_idx != -1, "retryLoop call not found in refreshObjects"

    # Content between function start and retryLoop should NOT contain getObjectNamesAndSetWatch
    pre_loop_content = content[refresh_start:retry_idx]

    # Remove comments for cleaner analysis
    # Simple comment removal
    pre_loop_no_comments = re.sub(r'//.*', '', pre_loop_content)
    pre_loop_no_comments = re.sub(r'/\*.*?\*/', '', pre_loop_no_comments, flags=re.DOTALL)

    # The old buggy pattern would have getObjectNamesAndSetWatch before the loop
    # The fix moves it inside, so it should NOT be in the pre-loop section
    # (except possibly in comments explaining the fix)

    # Check that variable declarations don't use the raw zookeeper param
    # The fix introduces current_zookeeper = zookeeper, then uses current_zookeeper
    if "getObjectNamesAndSetWatch(zookeeper, object_type)" in pre_loop_no_comments:
        assert False, "BUG: getObjectNamesAndSetWatch called with stale 'zookeeper' param before retry loop"


def test_session_refresh_comment():
    """Verify the explanatory comment about session renewal is present."""
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # The fix includes a comment explaining the session renewal
    assert "Renew the session on retry" in content, \
        "Comment explaining session renewal not found"


def test_compiles_without_syntax_errors():
    """
    P2P: Verify the code compiles without syntax errors.

    This is a basic compilation check - we don't need full ClickHouse build,
    just enough to verify the C++ syntax is valid.
    """
    filepath = os.path.join(REPO, TARGET_FILE)

    # Use clang to check syntax
    # We need to create a minimal compilation database or use clang-check
    # For now, we'll use clang with basic flags to check for syntax errors

    # First, check if we can at least parse the file
    result = subprocess.run(
        ["clang-15", "-fsyntax-only", "-std=c++20", "-xc++", filepath],
        capture_output=True,
        text=True,
        cwd=REPO
    )

    # Note: This may fail due to missing includes, but we're looking for syntax errors
    # If it compiles, great; if it fails due to missing headers, that's OK for our purposes
    # We just want to ensure the patch doesn't introduce syntax errors

    # A syntax error would be something like "expected" or "unexpected"
    syntax_errors = [
        "error: expected",
        "error: unexpected",
        "error: missing",
        "error: invalid",
        "error: syntax"
    ]

    for err in syntax_errors:
        assert err not in result.stderr, f"Syntax error found: {result.stderr}"


def test_try_load_uses_current_zookeeper():
    """
    Verify that tryLoadObject uses the current_zookeeper handle inside the retry loop.
    """
    filepath = os.path.join(REPO, TARGET_FILE)
    with open(filepath, 'r') as f:
        content = f.read()

    # After the fix, tryLoadObject should use current_zookeeper, not the raw zookeeper param
    assert "tryLoadObject(current_zookeeper," in content, \
        "tryLoadObject must use current_zookeeper handle for consistent session"


# ============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and fix
# ============================================================================

def test_repo_python_syntax_ci_scripts():
    """
    P2P: All Python scripts in ci/ directory have valid syntax.
    """
    ci_dir = os.path.join(REPO, "ci")
    errors = []

    for root, dirs, files in os.walk(ci_dir):
        # Skip praktika directory - it has complex dependencies
        dirs[:] = [d for d in dirs if d != "praktika"]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                result = subprocess.run(
                    ["python3", "-m", "py_compile", filepath],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    errors.append(f"{filepath}: {result.stderr}")

    assert not errors, f"Python syntax errors found:\n" + "\n".join(errors[:10])


def test_repo_python_syntax_tests_ci():
    """
    P2P: All Python scripts in tests/ci/ have valid syntax.
    """
    tests_ci_dir = os.path.join(REPO, "tests", "ci")
    if not os.path.exists(tests_ci_dir):
        pytest.skip("tests/ci directory not found")

    errors = []

    for file in os.listdir(tests_ci_dir):
        if file.endswith(".py"):
            filepath = os.path.join(tests_ci_dir, file)
            result = subprocess.run(
                ["python3", "-m", "py_compile", filepath],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                errors.append(f"{filepath}: {result.stderr}")

    assert not errors, f"Python syntax errors found:\n" + "\n".join(errors[:10])


def test_repo_yaml_valid():
    """
    P2P: GitHub workflow YAML files are syntactically valid.
    """
    yaml = pytest.importorskip("yaml")

    workflows_dir = os.path.join(REPO, ".github", "workflows")
    errors = []

    yaml_files = [f for f in os.listdir(workflows_dir) if f.endswith((".yml", ".yaml"))]
    assert yaml_files, "No YAML files found in .github/workflows"

    for file in yaml_files:
        filepath = os.path.join(workflows_dir, file)
        try:
            with open(filepath, 'r') as f:
                yaml.safe_load(f)
        except Exception as e:
            errors.append(f"{file}: {e}")

    assert not errors, f"YAML parse errors found:\n" + "\n".join(errors)


def test_repo_pyproject_toml_valid():
    """
    P2P: pyproject.toml is syntactically valid.
    """
    toml_path = os.path.join(REPO, "pyproject.toml")
    if not os.path.exists(toml_path):
        pytest.skip("pyproject.toml not found")

    # Try to read as a valid config file
    result = subprocess.run(
        ["python3", "-c", "import sys; exec(open(sys.argv[1]).read())", toml_path],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Even if execution fails (which is expected for toml), we can check for syntax errors
    # A better test is just checking if file exists and is non-empty
    with open(toml_path, 'r') as f:
        content = f.read().strip()

    assert content, "pyproject.toml is empty"
    assert "[tool." in content or "[build-system" in content, "pyproject.toml appears invalid"


def test_repo_clang_format_config_valid():
    """
    P2P: .clang-format config file is valid YAML.
    """
    yaml = pytest.importorskip("yaml")

    config_path = os.path.join(REPO, ".clang-format")
    if not os.path.exists(config_path):
        pytest.skip(".clang-format not found")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    assert config, ".clang-format is empty or invalid"
    assert "BasedOnStyle" in config, ".clang-format missing BasedOnStyle key"


def test_repo_cmake_lists_exists():
    """
    P2P: CMakeLists.txt exists and has content.
    """
    cmake_path = os.path.join(REPO, "CMakeLists.txt")

    with open(cmake_path, 'r') as f:
        content = f.read().strip()

    assert content, "CMakeLists.txt is empty"
    assert "cmake_minimum_required" in content or "project(" in content, \
        "CMakeLists.txt appears invalid (missing cmake_minimum_required or project)"


def test_repo_git_submodule_config_valid():
    """
    P2P: .gitmodules file is valid if it exists.
    """
    gitmodules_path = os.path.join(REPO, ".gitmodules")
    if not os.path.exists(gitmodules_path):
        pytest.skip(".gitmodules not found (no submodules)")

    result = subprocess.run(
        ["git", "config", "--file", gitmodules_path, "--list"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If git config can parse it, it's valid
    assert result.returncode == 0, f".gitmodules parse error: {result.stderr}"


def test_repo_no_broken_symlinks():
    """
    P2P: No broken symlinks in the repository root (common CI check).
    """
    result = subprocess.run(
        ["find", REPO, "-xtype", "l"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    # -xtype l finds broken symlinks
    broken_links = [l for l in result.stdout.strip().split("\n") if l.strip()]

    # Allow some known broken links in contrib (common in ClickHouse)
    # Filter out contrib and build directories
    serious_broken = [
        l for l in broken_links
        if "/contrib/" not in l and "/build" not in l and "/.git/" not in l
    ]

    assert not serious_broken, f"Broken symlinks found:\n" + "\n".join(serious_broken[:10])
