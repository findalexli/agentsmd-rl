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
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_manager_not_stub():
    """manager.rs has substantial content (not a stub or truncated file)."""
    line_count = len(MANAGER.read_text().splitlines())
    assert line_count > 1000, (
        f"manager.rs has only {line_count} lines — expected >1000"
    )
