"""
Tests for ClickHouse ZooKeeper UDF retry fix.

This validates that the fix for stale ZooKeeper session in UDF retry loop
is correctly applied. The fix ensures:
1. A fresh ZooKeeper session is obtained on retry
2. Object names are re-fetched inside the retry loop
3. The correct session handle is used for loading objects
"""

import subprocess
import sys
import os
import re
from pathlib import Path

# Path to the modified file
REPO_ROOT = Path("/workspace/ClickHouse")
TARGET_FILE = REPO_ROOT / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD checks)
# These tests verify the repo's own CI checks pass on the base commit
# =============================================================================

def test_repo_submodules_check():
    """Repo submodules check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_submodules.sh"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"Submodules check failed:\n{r.stderr[-500:]}"


def test_repo_git_track_branch():
    """Repo is on correct base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO_ROOT,
    )
    assert r.returncode == 0, f"Git command failed: {r.stderr}"
    commit = r.stdout.strip()
    # Just verify it's a valid commit hash and git works
    assert len(commit) == 40, f"Invalid commit hash: {commit}"


def test_repo_target_file_exists():
    """Target file exists and is readable (pass_to_pass)."""
    assert TARGET_FILE.exists(), f"Target file not found: {TARGET_FILE}"
    content = TARGET_FILE.read_text()
    assert "UserDefinedSQLObjectsZooKeeperStorage" in content, "Target file content unexpected"


def test_repo_no_conflict_markers():
    """Repo files have no git conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "find ./src ./base ./programs ./utils ./tests ./docs ./cmake -name '*.cpp' -o -name '*.h' -o -name '*.md' | xargs grep -P '^(<<<<<<<|=======|>>>>>>>)$' 2>/dev/null || true"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.stdout.strip() == "", f"Found conflict markers in:\n{r.stdout}"


def test_repo_no_dos_newlines():
    """Repo C++ files have no DOS/Windows newlines in ClickHouse code (pass_to_pass)."""
    # Excludes: build/, integration/, contrib/ paths
    EXCLUDE='build/|integration/|contrib/|widechar_width/|glibc-compatibility/|poco/|memcpy/|consistent-hashing'
    r = subprocess.run(
        ["bash", "-c", f"find ./src ./base ./programs ./utils ./docs -name '*.md' -o -name '*.h' -o -name '*.cpp' -o -name '*.js' -o -name '*.py' -o -name '*.html' 2>/dev/null | grep -vP '{EXCLUDE}' | xargs grep -l '\r' 2>/dev/null || true"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.stdout.strip() == "", f"Found DOS newlines in:\n{r.stdout}"


def test_repo_no_tabs_in_source():
    """Repo C++ files have no tabs in ClickHouse code (pass_to_pass)."""
    # Excludes: build/, third-party libs (poco, glibc-compatibility, etc.), and specific files
    EXCLUDE='build/|integration/|widechar_width/|glibc-compatibility/|poco/|memcpy/|consistent-hashing|benchmark|tests/.*\\.cpp$|programs/keeper-bench/example\\.yaml|base/base/openpty\\.h|src/Storages/System/StorageSystemDashboards\\.cpp|src/Storages/ObjectStorage/DataLakes/Iceberg/AvroSchema\\.h'
    r = subprocess.run(
        ["bash", "-c", f"find ./src ./base ./programs ./utils -name '*.h' -o -name '*.cpp' 2>/dev/null | grep -vP '{EXCLUDE}' | xargs grep -l $'\\t' 2>/dev/null || true"],
        capture_output=True, text=True, timeout=120, cwd=REPO_ROOT,
    )
    assert r.stdout.strip() == "", f"Found tabs in:\n{r.stdout}"


def test_repo_git_working_tree_clean():
    """Repo working tree is clean (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO_ROOT,
    )
    # Allow the target file to be modified (it may have been patched)
    lines = [l for l in r.stdout.strip().split('\n') if l.strip() and 'UserDefinedSQLObjectsZooKeeperStorage.cpp' not in l]
    assert len(lines) == 0, f"Working tree has unexpected changes:\n{r.stdout}"


def get_refreshObjects_function_content():
    """Extract the refreshObjects function content from the file."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")

    content = TARGET_FILE.read_text()

    # Try simpler approach - find from function signature to end of function
    start = content.find('void UserDefinedSQLObjectsZooKeeperStorage::refreshObjects')
    if start == -1:
        raise ValueError("refreshObjects function not found")

    # Find matching closing brace (accounting for nested braces)
    brace_count = 0
    in_function = False
    end = start
    for i, char in enumerate(content[start:]):
        if char == '{':
            brace_count += 1
            in_function = True
        elif char == '}':
            brace_count -= 1
            if in_function and brace_count == 0:
                end = start + i + 1
                break

    return content[start:end]


def test_current_zookeeper_variable_exists():
    """Check that current_zookeeper variable is declared and used."""
    func_content = get_refreshObjects_function_content()

    # Check for declaration of current_zookeeper
    assert "zkutil::ZooKeeperPtr current_zookeeper = zookeeper;" in func_content, \
        "current_zookeeper variable should be declared and initialized with zookeeper"

    # Check that current_zookeeper is used in tryLoadObject
    assert "tryLoadObject(current_zookeeper," in func_content, \
        "tryLoadObject should use current_zookeeper, not the original zookeeper parameter"


def test_session_renewal_on_retry():
    """Check that session is renewed when retrying."""
    func_content = get_refreshObjects_function_content()

    # Check for retry conditional and session renewal
    assert "if (retries_ctl.isRetry())" in func_content, \
        "Should check if this is a retry using retries_ctl.isRetry()"

    assert "current_zookeeper = zookeeper_getter.getZooKeeper().first;" in func_content, \
        "Should obtain fresh ZooKeeper session on retry via zookeeper_getter"


def test_object_names_inside_retry_loop():
    """Check that object_names is fetched inside the retry loop."""
    func_content = get_refreshObjects_function_content()

    # Find the retryLoop lambda
    retry_loop_match = re.search(r'retries_ctl\.retryLoop\(\[&\]\s*\{(.*?)\}\s*\);', func_content, re.DOTALL)
    if not retry_loop_match:
        retry_loop_match = re.search(r'retryLoop\(\[&\].*?\{(.*?)\}\s*\);', func_content, re.DOTALL)

    assert retry_loop_match, "retryLoop call with lambda not found"

    retry_body = retry_loop_match.group(1)

    # Check that object_names is fetched inside the retry loop
    assert "getObjectNamesAndSetWatch(current_zookeeper, object_type)" in retry_body, \
        "getObjectNamesAndSetWatch should be called inside the retry loop with current_zookeeper"

    # Check that Strings object_names is declared inside the lambda (not before)
    assert "Strings object_names" in retry_body, \
        "object_names should be declared inside the retry loop lambda"


def test_no_object_names_before_retry_loop():
    """Check that object_names is not fetched before the retry loop."""
    func_content = get_refreshObjects_function_content()

    # Find retryLoop position
    retry_pos = func_content.find('retryLoop')
    assert retry_pos != -1, "retryLoop not found in function"

    # Check the content before retryLoop
    before_retry = func_content[:retry_pos]

    # The original bug had: Strings object_names = getObjectNamesAndSetWatch(zookeeper, object_type);
    # before the retry loop. This should NOT exist.
    old_pattern = r'Strings\s+object_names\s*=\s*getObjectNamesAndSetWatch\s*\(\s*zookeeper\s*,\s*object_type\s*\)'
    match = re.search(old_pattern, before_retry)

    assert match is None, \
        "BUG: Object names should NOT be fetched before the retry loop with the original zookeeper parameter"


def test_updated_comment_explains_fix():
    """Check that the comment explains the session renewal behavior."""
    func_content = get_refreshObjects_function_content()

    # Check for updated comment explaining the fix
    assert "zookeeper_getter" in func_content, \
        "Comment or code should mention zookeeper_getter for session renewal"

    assert "fresh session" in func_content or "expired session" in func_content or "live session" in func_content, \
        "Comment should explain that a fresh session is obtained on retry"


def test_distinctive_line_pattern():
    """Verify the distinctive fix line is present (for idempotency)."""
    content = TARGET_FILE.read_text()

    # This is the key distinctive line from the patch
    distinctive = "if (retries_ctl.isRetry())"
    assert distinctive in content, \
        f"Distinctive fix line '{distinctive}' not found"

    # Also check the zookeeper_getter call inside the retry check
    assert "current_zookeeper = zookeeper_getter.getZooKeeper().first;" in content, \
        "Session renewal via zookeeper_getter not found"
