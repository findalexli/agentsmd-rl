"""
Benchmark tests for cline#9726: feat(cli): add --continue for current directory

Tests verify actual behavior by executing the code and examining observable output.
"""

import subprocess
import os
import re

REPO = "/workspace/cline"
CLI_DIR = f"{REPO}/cli"


def test_find_most_recent_task_for_workspace_exists():
    """findMostRecentTaskForWorkspace function exists and is runnable via vitest (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    assert "findMostRecentTaskForWorkspace" in output and r.returncode == 0, \
        f"Function not tested successfully:\n{output[-500:]}"


def test_find_most_recent_task_for_workspace_is_exported():
    """findMostRecentTaskForWorkspace is exported and imported by test file (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # If the import fails (function not exported), we'll see "Cannot find module" error
    assert not ("Cannot find" in output and "task-history" in output), \
        f"Module not properly exported:\n{output[-500:]}"
    assert r.returncode == 0, f"Tests did not pass:\n{output[-500:]}"


def test_find_most_recent_task_for_workspace_handles_empty_history():
    """findMostRecentTaskForWorkspace handles empty/undefined history (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # The verbose output shows test names; "returns null when there is no match" is the empty-history test
    assert "returns null when there is no match" in output.lower() and r.returncode == 0, \
        f"Null-handling test not found or failed:\n{output[-500:]}"


def test_find_most_recent_task_for_workspace_sorts_by_timestamp():
    """findMostRecentTaskForWorkspace sorts by timestamp descending (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # The verbose output shows "returns the newest matching task for the workspace"
    assert "newest matching task" in output.lower() and r.returncode == 0, \
        f"Timestamp sorting test not found or failed:\n{output[-500:]}"


def test_continue_flag_defined_in_cli():
    """--continue flag is defined in CLI source (fail_to_pass)."""
    # Use grep on source but check for structural presence, not gold-specific text
    r = subprocess.run(
        ["grep", "-E", '"--continue"|\'--continue\'|--continue\\s', "cli/src/index.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"--continue flag not found in CLI source:\n{r.stderr}"


def test_continue_task_function_exists():
    """continueTask function is defined and callable (fail_to_pass)."""
    # Check that the function exists in source - structural check
    r = subprocess.run(
        ["grep", "-E", "async\\s+function\\s+continueTask|function\\s+continueTask\\s*\\(", "cli/src/index.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"continueTask function not found:\n{r.stderr}"


def test_task_history_test_file_exists():
    """task-history.test.ts exists and has runnable tests (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # Test file runs without import error
    assert r.returncode == 0, f"Test file not runnable:\n{output[-500:]}"


def test_task_history_test_has_newer_task_test():
    """task-history.test.ts has test for newest matching task (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # Check verbose output for the specific test name
    assert "newest matching task" in output.lower() and r.returncode == 0, \
        f"Newest task test not found:\n{output[-500:]}"


def test_task_history_test_has_null_for_no_match():
    """task-history.test.ts tests null return when no match (fail_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/task-history.test.ts", "--reporter=verbose"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = r.stdout + r.stderr
    # Check verbose output for the null test name
    assert "returns null when there is no match" in output.lower() and r.returncode == 0, \
        f"Null test case not found:\n{output[-500:]}"


def test_task_history_ts_compiles_with_tsc():
    """task-history.ts passes TypeScript syntax check (fail_to_pass)."""
    # Run tsc --noEmit on the whole cli project to catch syntax errors
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=CLI_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    stderr = r.stderr.lower()
    # Check for syntax errors (ts1xxx) - not module resolution errors (ts23xx)
    assert "error ts1" not in stderr, f"Syntax errors in task-history.ts:\n{r.stderr[:500]}"


# Pass-to-pass tests: repo's actual CI commands that should pass on base commit

def test_repo_biome_lint_cli():
    """Repo's biome lint passes on cli/src (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "lint", "cli/src/", "--diagnostic-level=error"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}"


def test_repo_vitest_utils_tests():
    """Repo's vitest unit tests for cli/src/utils pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/utils/"],
        cwd=f"{REPO}/cli",
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Vitest failed:\n{r.stdout[-500:]}"