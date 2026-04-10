"""
Task: nextjs-turbopack-cell-read-toplevel
Repo: vercel/next.js @ cbf12d18457cbe62cbb8f57f4e485110b6630e42
PR:   91699

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

f2p tests use subprocess (git diff) to verify actual code changes were applied.
p2p tests use structural analysis of current file state.
No Rust toolchain in Docker image — compilation tests not possible.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MANAGER_REL = "turbopack/crates/turbo-tasks/src/manager.rs"
TEST_REL = (
    "turbopack/crates/turbo-tasks-backend/tests/"
    "top_level_task_consistency.rs"
)
MANAGER = Path(REPO) / MANAGER_REL
TEST_FILE = Path(REPO) / TEST_REL


def _git_diff(*rel_paths: str) -> str:
    """Get diff between HEAD and working tree via subprocess."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", *rel_paths],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    return r.stdout


def _diff_lines(diff: str, kind: str) -> list[str]:
    """Extract stripped added (+) or removed (-) lines from a unified diff."""
    prefix = "+" if kind == "added" else "-"
    skip = "+++" if kind == "added" else "---"
    return [
        line[1:].strip()
        for line in diff.splitlines()
        if line.startswith(prefix) and not line.startswith(skip)
    ]


def _strip_comments(src: str) -> str:
    """Strip line comments (//) and block comments (/* ... */) from Rust source."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _find_fn_body(src: str, fn_name: str) -> str | None:
    """Extract a Rust function/method body using brace-counting."""
    clean = _strip_comments(src)
    for match in re.finditer(rf"\bfn\s+{fn_name}\b", clean):
        rest = clean[match.end() :]
        brace_idx = rest.find("{")
        semi_idx = rest.find(";")
        if brace_idx == -1:
            continue
        if 0 <= semi_idx < brace_idx:
            continue
        brace_pos = match.end() + brace_idx
        depth = 0
        for i in range(brace_pos, len(clean)):
            if clean[i] == "{":
                depth += 1
            elif clean[i] == "}":
                depth -= 1
                if depth == 0:
                    return clean[match.start() : i + 1]
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via git diff
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_debug_assert_removed_from_cell_read():
    """debug_assert_not_in_top_level_task removed from try_read_task_cell.

    Uses git diff to verify the actual code was removed.
    """
    diff = _git_diff(MANAGER_REL)
    assert diff.strip(), f"{MANAGER_REL} was not modified"

    removed = _diff_lines(diff, "removed")
    assert any(
        "debug_assert_not_in_top_level_task" in line and "read_task_cell" in line
        for line in removed
    ), (
        "debug_assert_not_in_top_level_task(\"read_task_cell\") "
        "must be removed from try_read_task_cell"
    )


# [pr_diff] fail_to_pass
def test_cell_read_test_expects_success():
    """Cell-read test renamed and no longer expects panic.

    Uses git diff to verify #[should_panic] removed and test renamed.
    """
    diff = _git_diff(TEST_REL)
    assert diff.strip(), f"{TEST_REL} was not modified"

    removed = _diff_lines(diff, "removed")
    added = _diff_lines(diff, "added")

    assert any("should_panic" in line for line in removed), (
        "#[should_panic] must be removed from the cell-read test"
    )
    assert any("test_cell_read_in_top_level_task_fails" in line for line in removed), (
        "Old test name test_cell_read_in_top_level_task_fails must be removed"
    )
    assert any("test_cell_read_in_top_level_task_succeeds" in line for line in added), (
        "Test must be renamed to test_cell_read_in_top_level_task_succeeds"
    )


# [pr_diff] fail_to_pass
def test_cell_read_test_asserts_value():
    """Cell-read test asserts the read value instead of discarding.

    Uses git diff to verify the discard pattern was replaced with an assertion.
    """
    diff = _git_diff(TEST_REL)
    assert diff.strip(), f"{TEST_REL} was not modified"

    removed = _diff_lines(diff, "removed")
    added = _diff_lines(diff, "added")

    assert any("let _" in line and "cell.await" in line for line in removed), (
        "The discard pattern `let _ = cell.await?` must be removed"
    )
    assert any(
        "let value" in line and "cell.await" in line for line in added
    ), "The result must be bound to a variable (let value = cell.await?)"
    assert any(
        "assert_eq" in line and "value" in line and "42" in line for line in added
    ), "Must assert the cell value (e.g., assert_eq!(value.value, 42))"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_debug_assert_preserved_in_output_methods():
    """debug_assert_not_in_top_level_task preserved in try_read_task_output
    and try_read_local_output — those ARE eventually consistent.
    """
    src = MANAGER.read_text()
    stripped = _strip_comments(src)

    count = stripped.count("debug_assert_not_in_top_level_task")
    assert count >= 2, (
        f"Expected >=2 remaining debug_assert_not_in_top_level_task calls, "
        f"found {count}. The assert must be preserved in "
        "try_read_task_output and try_read_local_output."
    )

    body = _find_fn_body(src, "try_read_task_output")
    assert body is not None, "Could not find try_read_task_output in manager.rs"
    assert "debug_assert_not_in_top_level_task" in body, (
        "debug_assert_not_in_top_level_task missing from try_read_task_output"
    )


# [pr_diff] pass_to_pass
def test_eventual_read_test_expects_panic():
    """Eventual-read test still expects panic (#[should_panic])."""
    src = TEST_FILE.read_text()

    found = False
    for m in re.finditer(r"async\s+fn\s+(test_\w*eventual\w*)", src, re.IGNORECASE):
        fn_start = m.start()
        attr_region = src[max(0, fn_start - 300) : fn_start]
        if "should_panic" in attr_region:
            found = True
            break

    assert found, (
        "No eventual-read test found that expects panic (#[should_panic])"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub and repo structure
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_manager_not_stub():
    """manager.rs has substantial content (not a stub or truncated file)."""
    line_count = len(MANAGER.read_text().splitlines())
    assert line_count > 1000, (
        f"manager.rs has only {line_count} lines — expected >1000"
    )


# [static] pass_to_pass
def test_manager_readable():
    """manager.rs is readable and contains expected function definitions (pass_to_pass)."""
    src = MANAGER.read_text()
    # Verify file is valid Rust source with expected functions
    assert "fn try_read_task_cell" in src, (
        "try_read_task_cell function not found in manager.rs"
    )
    assert "fn try_read_task_output" in src, (
        "try_read_task_output function not found in manager.rs"
    )
    assert "impl<B: Backend + 'static> TurboTasksApi for TurboTasks<B>" in src, (
        "TurboTasksApi impl not found in manager.rs"
    )


# [static] pass_to_pass
def test_backend_test_file_readable():
    """top_level_task_consistency.rs test file is readable and has tests (pass_to_pass)."""
    src = TEST_FILE.read_text()
    # Verify file has the expected test functions
    assert "async fn test_eventual_read_in_top_level_task_fails" in src, (
        "test_eventual_read_in_top_level_task_fails not found"
    )
    assert "async fn test_cell_read_in_top_level_task_fails" in src or \
           "async fn test_cell_read_in_top_level_task_succeeds" in src, (
        "test_cell_read test not found"
    )


# [static] pass_to_pass
def test_turbo_tasks_backend_crates_exist():
    """Required turbo-tasks backend crates exist and have content (pass_to_pass)."""
    backend_dir = Path(REPO) / "turbopack/crates/turbo-tasks-backend"
    tests_dir = backend_dir / "tests"
    src_dir = backend_dir / "src"

    assert backend_dir.is_dir(), "turbo-tasks-backend crate directory missing"
    assert tests_dir.is_dir(), "turbo-tasks-backend/tests directory missing"
    assert src_dir.is_dir(), "turbo-tasks-backend/src directory missing"

    # Verify there are test files
    test_files = list(tests_dir.glob("*.rs"))
    assert len(test_files) > 5, f"Expected >5 test files, found {len(test_files)}"


# [static] pass_to_pass
def test_repo_git_state_valid():
    """Repo has valid git state with expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert r.returncode == 0, f"Git HEAD not valid: {r.stderr}"
    commit = r.stdout.strip()
    assert len(commit) == 40, f"Invalid commit hash: {commit}"


# [static] pass_to_pass
def test_debug_assert_function_exists():
    """debug_assert_not_in_top_level_task function exists in manager.rs (pass_to_pass)."""
    src = MANAGER.read_text()
    # The function should exist (it's used by the asserts)
    assert "fn debug_assert_not_in_top_level_task" in src or \
           "debug_assert_not_in_top_level_task" in src, (
        "debug_assert_not_in_top_level_task not found in manager.rs"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_git_info():
    """Repo's git-info script runs successfully (pass_to_pass).

    Validates that the git-info Node.js script executes without errors.
    This script extracts git metadata used by CI pipelines.
    """
    r = subprocess.run(
        ["node", "scripts/git-info.mjs"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git-info script failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_run_for_change():
    """Repo's run-for-change script runs successfully (pass_to_pass).

    Validates that the change detection script executes without errors.
    This script is used by CI to determine which tests to run based on changed files.
    """
    r = subprocess.run(
        ["node", "scripts/run-for-change.mjs", "--not", "--type", "docs", "--exec", "echo", "test"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"run-for-change script failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_scripts_executable():
    """Repo's Node.js CI scripts are present and executable (pass_to_pass).

    Verifies that key Node.js scripts used in CI pipelines exist and are runnable.
    Uses subprocess to check file existence and git tracking status.
    """
    scripts = [
        "scripts/git-info.mjs",
        "scripts/run-for-change.mjs",
        "scripts/check-is-release.js",
        "scripts/check-unused-turbo-tasks.mjs",
        "scripts/git-configure.mjs",
    ]

    for script in scripts:
        script_path = Path(REPO) / script
        assert script_path.exists(), f"Script {script} must exist"
        assert script_path.stat().st_size > 0, f"Script {script} must not be empty"

    # Verify using git ls-files that the files are tracked
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch"] + scripts,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Scripts must be tracked by git: {r.stderr}"
