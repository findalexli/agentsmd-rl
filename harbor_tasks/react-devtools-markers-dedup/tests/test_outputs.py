"""
Task: react-devtools-markers-dedup
Repo: facebook/react @ 70890e7c58abccef35a6498f7ee702d608be79d6
PR:   35737

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """renderer.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", RENDERER],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"renderer.js has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_suspense_boundary_dedup():
    """Inner Suspense boundary retains uniqueSuspenders=false when only some of the parent's suspenders are removed."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "--no-watchman",
            "continues to consider Suspense boundary as blocking if some child still is suspended on removed io",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
        text=True,
    )
    assert r.returncode == 0, (
        f"Suspense dedup regression test failed:\n{r.stdout[-3000:]}\n{r.stderr[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_unblock_placement():
    """unblockSuspendedBy must be called inside the block that decrements environmentCounts."""
    # AST-only because: JavaScript renderer, no Python AST available
    content = Path(RENDERER).read_text()
    lines = content.splitlines()

    # Find environmentCounts.set(env, count - 1) — the decrement line
    set_idx = next(
        (i for i, l in enumerate(lines) if "environmentCounts.set(env, count - 1)" in l),
        None,
    )
    assert set_idx is not None, "environmentCounts.set(env, count - 1) not found in renderer.js"

    # Find the call to unblockSuspendedBy(suspenseNode within 25 lines of the decrement
    nearby = lines[set_idx : set_idx + 25]
    unblock_line = next(
        (l for l in nearby if "unblockSuspendedBy(suspenseNode" in l),
        None,
    )
    assert unblock_line is not None, (
        "unblockSuspendedBy(suspenseNode not found within 25 lines after "
        "environmentCounts.set — the fix requires it to be inside the count-check block"
    )

    # In the fixed code the call is nested one level deeper (14+ spaces).
    # In the buggy code it is at 12 spaces (outside the count-check block).
    indent = len(unblock_line) - len(unblock_line.lstrip())
    assert indent >= 14, (
        f"unblockSuspendedBy(suspenseNode is at indent={indent} spaces "
        f"(expected >= 14). The fix requires nesting it inside the "
        f"suspender-count check block."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_suspense_store_tests():
    """Existing Suspense-related store tests must still pass."""
    r = subprocess.run(
        ["yarn", "test", "--no-watchman", "Store.*Suspense"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
        text=True,
    )
    assert r.returncode == 0, (
        f"Existing Suspense store tests failed:\n{r.stdout[-3000:]}\n{r.stderr[-1000:]}"
    )


# [static] pass_to_pass
def test_not_stub():
    """renderer.js has substantial content with key suspense-tracking identifiers."""
    content = Path(RENDERER).read_text()
    assert len(content) > 50_000, "renderer.js appears empty or stripped"
    assert "unblockSuspendedBy" in content, "unblockSuspendedBy missing from renderer.js"
    assert "environmentCounts" in content, "environmentCounts missing from renderer.js"
    assert "hasUniqueSuspenders" in content, "hasUniqueSuspenders missing from renderer.js"
