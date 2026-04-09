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
    body = _find_fn_body(src, "task_execution_completed_prepare")
    assert body is not None, "Could not find task_execution_completed_prepare in mod.rs"

    # The cell_type_max_index update block must be guarded by a result success check.
    # Find the region that contains iter_cell_type_max_index and verify it's inside
    # a result.is_ok() conditional.
    clean = _strip_comments(body)

    # Locate iter_cell_type_max_index in the function
    idx = clean.find("iter_cell_type_max_index")
    assert idx != -1, "iter_cell_type_max_index not found in task_execution_completed_prepare"

    # Look backwards from iter_cell_type_max_index for a result.is_ok() guard
    preceding = clean[:idx]
    # Find the last `if` block before iter_cell_type_max_index that checks result success
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
    """
    src = MOD_RS.read_text()
    body = _find_fn_body(src, "try_read_task_cell")
    assert body is not None, "Could not find try_read_task_cell in mod.rs"

    clean = _strip_comments(body)

    # Find positions of the cancel bail and listen_to_cell.
    # Look for `if is_cancelled` which guards the bail! macro.
    bail_matches = list(re.finditer(r"if\s+is_cancelled\b", clean))
    assert bail_matches, "No is_cancelled check found in try_read_task_cell"

    listen_match = re.search(r"listen_to_cell\s*\(", clean)
    assert listen_match, "listen_to_cell call not found in try_read_task_cell"

    # The first is_cancelled bail must come before listen_to_cell
    first_bail_pos = bail_matches[0].start()
    listen_pos = listen_match.start()

    assert first_bail_pos < listen_pos, (
        f"is_cancelled bail (pos {first_bail_pos}) must come BEFORE "
        f"listen_to_cell (pos {listen_pos}) to avoid phantom listener "
        f"registrations on cancelled tasks"
    )


# [pr_diff] fail_to_pass
def test_cancel_uses_all_data_category():
    """task_execution_canceled must use TaskDataCategory::All, not ::Data.

    The base commit uses TaskDataCategory::Data, which doesn't give access
    to dirty state metadata needed for marking cancelled tasks dirty.
    """
    src = MOD_RS.read_text()
    body = _find_fn_body(src, "task_execution_canceled")
    assert body is not None, "Could not find task_execution_canceled in mod.rs"

    clean = _strip_comments(body)

    assert "TaskDataCategory::All" in clean, (
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
    body = _find_fn_body(src, "task_execution_canceled")
    assert body is not None, "Could not find task_execution_canceled in mod.rs"

    clean = _strip_comments(body)

    # Must take in-progress cells
    assert "take_in_progress_cells" in clean, (
        "task_execution_canceled must call take_in_progress_cells() "
        "to drain pending cell events"
    )

    # Must notify the events
    assert re.search(r"\.notify\s*\(", clean), (
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
    body = _find_fn_body(src, "task_execution_canceled")
    assert body is not None, "Could not find task_execution_canceled in mod.rs"

    clean = _strip_comments(body)

    # Must reference SessionDependent dirty state
    assert "SessionDependent" in clean, (
        "task_execution_canceled must mark the task as SessionDependent dirty "
        "to prevent cache poisoning from cancelled task errors"
    )

    # Must actually set/update the dirty state (via update_dirty_state or set_dirty)
    has_update = "update_dirty_state" in clean or "set_dirty" in clean
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
