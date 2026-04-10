"""
Task: nextjs-turbopack-task-cancel-stability
Repo: vercel/next.js @ cc79ef8cda9725008aacc9071aed423a584253d4
PR:   92254

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust crate (turbo-tasks-backend) — no Rust toolchain in Docker image,
so tests use source analysis and subprocess (git diff) to verify
behavioral patterns.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
MOD_RS = Path(REPO) / "turbopack/crates/turbo-tasks-backend/src/backend/mod.rs"
OP_MOD_RS = Path(REPO) / "turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs"


def _strip_comments(src: str) -> str:
    """Strip line comments (//) and block comments (/* ... */) from Rust source."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _find_fn_body(src: str, fn_name: str) -> str | None:
    """Extract a Rust function/method body using brace-counting."""
    clean = _strip_comments(src)
    for match in re.finditer(rf"\bfn\s+{fn_name}\b", clean):
        rest = clean[match.end():]
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
                    return clean[match.start():i + 1]
    return None


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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_cell_max_index_guarded_on_error():
    """cell_type_max_index update must be skipped on task error.

    On the base commit, iter_cell_type_max_index/insert_cell_type_max_index
    calls run unconditionally in task_execution_completed_prepare. The fix
    wraps them in an `if result.is_ok()` guard.
    """
    src = MOD_RS.read_text()
    clean = _strip_comments(src)

    # Find the task_execution_completed_prepare function region
    fn_start = clean.find("fn task_execution_completed_prepare")
    assert fn_start != -1, "task_execution_completed_prepare not found in mod.rs"

    # Find approximate end (next fn at similar indent level)
    next_fn = re.search(r"\n    fn [a-z]", clean[fn_start:])
    if next_fn:
        fn_region = clean[fn_start:fn_start + next_fn.start()]
    else:
        fn_region = clean[fn_start:fn_start + 5000]

    # Locate iter_cell_type_max_index in the function
    idx = fn_region.find("iter_cell_type_max_index")
    assert idx != -1, "iter_cell_type_max_index not found in task_execution_completed_prepare"

    # Look backwards from iter_cell_type_max_index for a result.is_ok() guard
    preceding = fn_region[:idx]
    assert re.search(r"result\s*\.\s*is_ok\s*\(\s*\)", preceding), (
        "iter_cell_type_max_index must be inside an `if result.is_ok()` guard "
        "to skip cell counter updates on error"
    )


# [pr_diff] fail_to_pass
def test_cancel_bail_before_listen_to_cell():
    """is_cancelled bail must come BEFORE listen_to_cell in try_read_task_cell.

    On the base commit, the bail happens AFTER listen_to_cell, which inserts
    phantom InProgressCellState events that never resolve. The fix moves the
    bail before listen_to_cell.

    Simplified check: verify the pattern exists in mod.rs:
    - The bail check `if is_cancelled { bail!(...) }` BEFORE
    - A subsequent `listen_to_cell` call in the same function
    """
    src = MOD_RS.read_text()
    clean = _strip_comments(src)

    # Find the try_read_task_cell function region (from fn declaration to next fn at same indent)
    fn_start = clean.find("fn try_read_task_cell")
    assert fn_start != -1, "try_read_task_cell not found in mod.rs"

    # Find where the next function at the same level starts (approximate)
    next_fn = clean.find("\n    fn listen_to_cell", fn_start)
    assert next_fn != -1, "Could not find end of try_read_task_cell region"

    fn_region = clean[fn_start:next_fn]

    # Find the is_cancelled bail pattern
    bail_match = re.search(r"if\s+is_cancelled\s*\{[^}]*bail!", fn_region)
    assert bail_match, "is_cancelled bail block not found in try_read_task_cell"
    bail_pos = bail_match.start()

    # Find all listen_to_cell calls after the bail
    listen_matches = list(re.finditer(r"listen_to_cell\s*\(", fn_region))
    assert listen_matches, "listen_to_cell call not found in try_read_task_cell"

    # Find first listen_to_cell after the bail
    listen_after_bail = None
    for m in listen_matches:
        if m.start() > bail_pos:
            listen_after_bail = m
            break

    assert listen_after_bail is not None, (
        "No listen_to_cell found after is_cancelled bail in try_read_task_cell"
    )

    assert bail_pos < listen_after_bail.start(), (
        "is_cancelled bail must come BEFORE listen_to_cell in try_read_task_cell"
    )


# [pr_diff] fail_to_pass
def test_cancel_uses_all_data_category():
    """task_execution_canceled must use TaskDataCategory::All, not ::Data.

    The base commit uses TaskDataCategory::Data, which doesn't give access
    to dirty state metadata needed for marking cancelled tasks dirty.
    """
    src = MOD_RS.read_text()
    clean = _strip_comments(src)

    # Find the task_execution_canceled function region
    fn_start = clean.find("fn task_execution_canceled")
    assert fn_start != -1, "task_execution_canceled not found in mod.rs"

    # Find approximate end (next fn at similar indent level)
    next_fn = re.search(r"\n    fn [a-z]", clean[fn_start:])
    if next_fn:
        fn_region = clean[fn_start:fn_start + next_fn.start()]
    else:
        fn_region = clean[fn_start:fn_start + 2000]

    assert "TaskDataCategory::All" in fn_region, (
        "task_execution_canceled must use TaskDataCategory::All "
        "(not TaskDataCategory::Data) to access dirty state metadata"
    )


# [pr_diff] fail_to_pass
def test_cancel_notifies_in_progress_cells():
    """task_execution_canceled must drain and notify in-progress cell events.

    On the base commit, when a task is cancelled, readers waiting on
    in-progress cells never get notified, causing stop_and_wait to hang.
    The fix takes in_progress_cells and notifies all pending events.
    """
    src = MOD_RS.read_text()
    clean = _strip_comments(src)

    # Find the task_execution_canceled function region
    fn_start = clean.find("fn task_execution_canceled")
    assert fn_start != -1, "task_execution_canceled not found in mod.rs"

    # Find approximate end (next fn at similar indent level)
    next_fn = re.search(r"\n    fn [a-z]", clean[fn_start:])
    if next_fn:
        fn_region = clean[fn_start:fn_start + next_fn.start()]
    else:
        fn_region = clean[fn_start:fn_start + 2000]

    # Must take in-progress cells
    assert "take_in_progress_cells" in fn_region, (
        "task_execution_canceled must call take_in_progress_cells() "
        "to drain pending cell events"
    )

    # Must notify the events
    assert re.search(r"\.notify\s*\(", fn_region), (
        "task_execution_canceled must notify pending in-progress cell events "
        "so listeners resolve and foreground jobs finish"
    )


# [pr_diff] fail_to_pass
def test_cancel_marks_session_dependent_dirty():
    """task_execution_canceled must mark the task as session-dependent dirty.

    On the base commit, cancelled tasks are not marked dirty, causing
    'was canceled' errors to be persisted and poison subsequent builds.
    The fix marks cancelled tasks as SessionDependent dirty.
    """
    src = MOD_RS.read_text()
    clean = _strip_comments(src)

    # Find the task_execution_canceled function region
    fn_start = clean.find("fn task_execution_canceled")
    assert fn_start != -1, "task_execution_canceled not found in mod.rs"

    # Find approximate end (next fn at similar indent level)
    next_fn = re.search(r"\n    fn [a-z]", clean[fn_start:])
    if next_fn:
        fn_region = clean[fn_start:fn_start + next_fn.start()]
    else:
        fn_region = clean[fn_start:fn_start + 2000]

    # Must reference SessionDependent dirty state
    assert "SessionDependent" in fn_region, (
        "task_execution_canceled must mark the task as SessionDependent dirty "
        "to prevent cache poisoning from cancelled task errors"
    )

    # Must actually set/update the dirty state (via update_dirty_state or set_dirty)
    has_update = "update_dirty_state" in fn_region or "set_dirty" in fn_region
    assert has_update, (
        "task_execution_canceled must update the dirty state "
        "(via update_dirty_state or set_dirty)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_mod_rs_not_stub():
    """mod.rs has substantial content (not a stub or truncated file)."""
    line_count = len(MOD_RS.read_text().splitlines())
    assert line_count > 2000, (
        f"mod.rs has only {line_count} lines — expected >2000 for the "
        "turbo-tasks-backend main module"
    )


# [static] pass_to_pass
def test_operation_mod_has_task_guard():
    """operation/mod.rs contains the TaskGuard trait with dirty_state method."""
    src = OP_MOD_RS.read_text()
    clean = _strip_comments(src)

    assert "trait TaskGuard" in clean, (
        "TaskGuard trait not found in operation/mod.rs"
    )
    assert "fn dirty_state" in clean, (
        "dirty_state method not found on TaskGuard trait"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — real CI commands via subprocess
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_git_status_clean():
    """Git repository is in a valid state (pass_to_pass).

    Verifies the repo was properly cloned and git commands work.
    After applying a patch, the working tree will have changes - that's expected.
    This test ensures the git repository is functional.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    # Note: We don't assert that stdout is empty here because:
    # 1. On the base commit, the repo should be clean (passes)
    # 2. After applying the gold fix, files will be modified (also OK)
    # This test just ensures git is functional in the container


# [repo_tests] pass_to_pass
def test_repo_no_whitespace_errors():
    """No trailing whitespace or merge conflict markers (pass_to_pass).

    CI often runs git diff --check to catch whitespace errors and
    conflict markers before merging. This test verifies the base
    commit is clean.
    """
    r = subprocess.run(
        ["git", "diff", "--check"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    # git diff --check returns 0 if no issues found
    assert r.returncode == 0, (
        f"Whitespace errors or conflict markers found:\n{r.stdout}{r.stderr}"
    )


# [repo_tests] pass_to_pass
def test_repo_files_exist():
    """Modified files exist and are tracked in git (pass_to_pass).

    Verifies that the files modified by the PR exist and are properly
    tracked in the git repository.
    """
    # Check that critical files exist
    files_to_check = [
        "turbopack/crates/turbo-tasks-backend/src/backend/mod.rs",
        "turbopack/crates/turbo-tasks-backend/src/backend/operation/mod.rs",
    ]

    for file_path in files_to_check:
        full_path = Path(REPO) / file_path
        assert full_path.exists(), f"File does not exist: {file_path}"

    # Verify files are tracked in git (actual CI-like check)
    r = subprocess.run(
        ["git", "ls-files", "--error-unmatch", *files_to_check],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"Files are not tracked in git:\n{r.stderr}"
    )
