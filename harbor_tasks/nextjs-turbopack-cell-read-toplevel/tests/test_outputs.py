"""
Task: nextjs-turbopack-cell-read-toplevel
Repo: vercel/next.js @ cbf12d18457cbe62cbb8f57f4e485110b6630e42
PR:   91699

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All checks are source-inspection based because turbopack requires
nightly Rust + 200+ crates to compile; the Docker image (node:22-slim) has
no Rust toolchain.
# AST-only because: Rust code, no Rust toolchain in Docker image
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
MANAGER = Path(REPO) / "turbopack/crates/turbo-tasks/src/manager.rs"
TEST_FILE = (
    Path(REPO)
    / "turbopack/crates/turbo-tasks-backend/tests/top_level_task_consistency.rs"
)


def _strip_comments(src: str) -> str:
    """Strip line comments (//) and block comments (/* ... */) from Rust source."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _find_fn_body(src: str, fn_name: str) -> str | None:
    """Extract a Rust function/method body using brace-counting.

    More reliable than regex lookahead for nested structures.
    Returns the full text from 'fn <name>' through the closing '}'.
    Operates on comment-stripped source to avoid false matches.
    Skips trait method signatures (no body, just `;`).
    """
    clean = _strip_comments(src)
    # Find all occurrences — skip trait signatures (`;` before `{`)
    for match in re.finditer(rf"\bfn\s+{fn_name}\b", clean):
        # Check whether this is a trait signature (no body)
        rest = clean[match.end():]
        brace_idx = rest.find("{")
        semi_idx = rest.find(";")
        if brace_idx == -1:
            continue
        # If semicolon comes before opening brace, it's a trait signature
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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_debug_assert_removed_from_cell_read():
    """debug_assert_not_in_top_level_task must not appear in try_read_task_cell.

    Cell reads are strongly consistent, so the top-level-task guard is wrong.
    Comments are stripped before analysis to reject commented-out code.
    """
    src = MANAGER.read_text()
    body = _find_fn_body(src, "try_read_task_cell")
    assert body is not None, "Could not find try_read_task_cell method in manager.rs"

    assert "debug_assert_not_in_top_level_task" not in body, (
        "debug_assert_not_in_top_level_task must be removed from "
        "try_read_task_cell — cell reads are strongly consistent"
    )


# [pr_diff] fail_to_pass
def test_cell_read_test_expects_success():
    """Cell-read integration test expects success (no #[should_panic]).

    Any test function with 'cell_read' in its name that uses
    resolve_strongly_consistent must NOT have #[should_panic].
    """
    src = TEST_FILE.read_text()

    # Reject: old test name still present with should_panic
    if re.search(
        r"#\[should_panic\].*?fn\s+test_cell_read_in_top_level_task_fails",
        src,
        re.DOTALL,
    ):
        assert False, (
            "test_cell_read_in_top_level_task_fails still has #[should_panic]"
        )

    # Find a cell-read test (uses resolve_strongly_consistent) without should_panic
    found = False
    for m in re.finditer(r"async\s+fn\s+(test_\w*cell_read\w*)", src):
        fn_start = m.start()
        attr_region = src[max(0, fn_start - 300) : fn_start]
        if "should_panic" not in attr_region:
            found = True
            break

    assert found, (
        "No cell-read test found that expects success (without #[should_panic])"
    )


# [pr_diff] fail_to_pass
def test_cell_read_test_asserts_value():
    """Cell-read test asserts the read value instead of discarding with let _.

    The old test used `let _ = cell.await?` (discard). The fix must use the
    value (e.g., assert_eq! on the result).
    """
    src = _strip_comments(TEST_FILE.read_text())

    for m in re.finditer(r"resolve_strongly_consistent", src):
        region = src[m.start() : m.start() + 500]

        # Reject: value discarded
        if re.search(r"let\s+_\s*=\s*\w+\.await", region):
            assert False, (
                "Cell read value is discarded with `let _ = ...await` "
                "— must assert the value"
            )

        # Accept: some form of assertion on the result
        if re.search(r"(assert|assert_eq|assert_ne|expect\()", region):
            return

    assert False, "No assertion found on cell read result in the cell-read test"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_debug_assert_preserved_in_output_methods():
    """debug_assert_not_in_top_level_task preserved in try_read_task_output
    and try_read_local_output — those ARE eventually consistent and must
    keep the guard.
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
    """Eventual-read test still expects panic (#[should_panic]).

    Eventual reads from top-level tasks are NOT strongly consistent and must
    remain forbidden.
    """
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
