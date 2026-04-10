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

# Docker-internal path to the repo (from Dockerfile WORKDIR)
# NOTE: This is the path INSIDE the Docker container, not /workspace/repo/
REPO = "/workspace/ClickHouse"
REPO_ROOT = Path(REPO)
TARGET_FILE = REPO_ROOT / "src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp"


# =============================================================================
# PASS-TO-PASS TESTS (Repo CI/CD checks)
# These tests verify the repo's own CI checks pass on the base commit
# =============================================================================

def test_repo_cpp_style_no_tabs():
    """Repo C++ files have no tabs (pass_to_pass) - ClickHouse CI style check."""
    # Uses the same logic as ci/jobs/scripts/check_style/check_cpp.sh
    EXCLUDE = r'build/|integration/|widechar_width/|glibc-compatibility/|poco/|memcpy/|consistent-hashing|benchmark|tests/.*\.cpp$|programs/keeper-bench/example\.yaml|base/base/openpty\.h|src/Storages/System/StorageSystemDashboards\.cpp|src/Storages/ObjectStorage/DataLakes/Iceberg/AvroSchema\.h'
    cmd = (
        f"find ./src ./base ./programs ./utils -name '*.h' -o -name '*.cpp' 2>/dev/null | "
        f"grep -vP '{EXCLUDE}' | xargs grep -l $'\\t' 2>/dev/null || true"
    )
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found tabs in C++ source files:\n{r.stdout}"


def test_repo_cpp_style_no_dos_newlines():
    """Target file has no DOS newlines (pass_to_pass) - ClickHouse CI style check."""
    # Check only the target file, not the whole repo (base commit has pre-existing issues)
    cmd = f"grep -l $'\\r' {TARGET_FILE} 2>/dev/null || true"
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found DOS newlines in target file"


def test_repo_no_conflict_markers():
    """Repo files have no git conflict markers (pass_to_pass) - ClickHouse CI check."""
    # Uses the same logic as ci/jobs/scripts/check_style/various_checks.sh
    r = subprocess.run(
        [
            "bash", "-c",
            r"find ./src ./base ./programs ./utils ./tests ./docs ./cmake -name '*.cpp' -o -name '*.h' -o -name '*.md' | xargs grep -P '^(<<<<<<<|=======|>>>>>>>)$' 2>/dev/null || true"
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found conflict markers in:\n{r.stdout}"


def test_repo_no_utf8_bom():
    """Repo files have no UTF-8 BOM (pass_to_pass) - ClickHouse CI check."""
    # Uses the same logic as ci/jobs/scripts/check_style/various_checks.sh
    r = subprocess.run(
        [
            "bash", "-c",
            r"find ./src ./base ./programs ./utils ./tests ./docs ./cmake -name '*.md' -o -name '*.cpp' -o -name '*.h' | xargs grep -l -F $'\xEF\xBB\xBF' 2>/dev/null || true"
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found UTF-8 BOM in files:\n{r.stdout}"


def test_repo_no_trailing_whitespace():
    """Target file has no trailing whitespace (pass_to_pass) - ClickHouse CI style check."""
    # Check only the target file, not the whole repo (base commit has pre-existing issues)
    cmd = f"grep -n -P ' $' {TARGET_FILE} 2>/dev/null || true"
    r = subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Found trailing whitespace in target file:\n{r.stdout}"


def test_repo_target_file_exists():
    """Target file exists and is readable (pass_to_pass)."""
    r = subprocess.run(
        ["test", "-f", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Target file not found: {TARGET_FILE}"


def test_repo_git_track_branch():
    """Repo is on correct base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git command failed: {r.stderr}"
    commit = r.stdout.strip()
    # Just verify it's a valid commit hash and git works
    assert len(commit) == 40, f"Invalid commit hash: {commit}"


def test_repo_no_executable_source_files():
    """Repo source files are not executable (pass_to_pass) - ClickHouse CI check."""
    # Uses the same logic as ci/jobs/scripts/check_style/various_checks.sh
    r = subprocess.run(
        [
            "bash", "-c",
            r"git ls-files -s ./src ./base ./programs ./utils ./tests ./docs ./cmake | awk '\$1 != \"120000\" && \$1 != \"100644\" { print \$4 }' | grep -E '\.(cpp|h|sql|j2|xml|txt|md)\$' || true"
        ],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.stdout.strip() == "", f"Source files should not be executable:\n{r.stdout}"


# =============================================================================
# FAIL-TO-PASS TESTS (Structural checks for the fix)
# These tests verify the fix is correctly applied
# =============================================================================

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
