"""
Task: react-devtools-activity-reveal
Repo: facebook/react @ 24f215ce8b0e17a230fbb7317919a6ae0c324f35

When an Activity component transitions from hidden to visible, its children
must be mounted into the DevTools fiber tree. The fix adds a
`else if (prevWasHidden && !nextIsHidden)` branch in renderer.js that calls
`mountChildrenRecursively` and sets the ShouldResetChildren flags.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
RENDERER = f"{REPO}/packages/react-devtools-shared/src/backend/fiber/renderer.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_renderer_file_exists():
    """renderer.js must exist and contain Activity/OffscreenComponent handling."""
    src = Path(RENDERER).read_text()
    assert "OffscreenComponent" in src, "OffscreenComponent not found in renderer.js"
    assert "prevWasHidden" in src, "prevWasHidden not found in renderer.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hidden_to_visible_branch_exists():
    """An else-if branch for prevWasHidden && !nextIsHidden must be present."""
    src = Path(RENDERER).read_text()
    # Must be an `else if` branch (not just a comment or unused variable)
    assert re.search(
        r"else\s+if\s*\(\s*prevWasHidden\s*&&\s*!nextIsHidden\s*\)",
        src,
    ), "Missing: else if (prevWasHidden && !nextIsHidden) branch"


# [pr_diff] fail_to_pass
def test_mount_children_called_in_reveal_branch():
    """mountChildrenRecursively must be called inside the hidden->visible branch."""
    src = Path(RENDERER).read_text()
    # Find the reveal branch and check that mountChildrenRecursively appears
    # within its body (before the closing brace of the outer block)
    match = re.search(
        r"else\s+if\s*\(\s*prevWasHidden\s*&&\s*!nextIsHidden\s*\)\s*\{(.+?)(?=\}\s*else|\}\s*\))",
        src,
        re.DOTALL,
    )
    assert match, "Could not locate the prevWasHidden && !nextIsHidden branch body"
    branch_body = match.group(1)
    assert "mountChildrenRecursively" in branch_body, (
        "mountChildrenRecursively not called in hidden->visible branch"
    )


# [pr_diff] fail_to_pass
def test_flags_updated_in_reveal_branch():
    """ShouldResetChildren and ShouldResetSuspenseChildren flags must be set in the reveal branch."""
    src = Path(RENDERER).read_text()
    match = re.search(
        r"else\s+if\s*\(\s*prevWasHidden\s*&&\s*!nextIsHidden\s*\)\s*\{(.+?)(?=\}\s*else|\}\s*\))",
        src,
        re.DOTALL,
    )
    assert match, "Could not locate the prevWasHidden && !nextIsHidden branch body"
    branch_body = match.group(1)
    assert "ShouldResetChildren" in branch_body, (
        "ShouldResetChildren flag not set in hidden->visible branch"
    )
    assert "ShouldResetSuspenseChildren" in branch_body, (
        "ShouldResetSuspenseChildren flag not set in hidden->visible branch"
    )


# [pr_diff] fail_to_pass
def test_reveal_branch_checks_child_not_null():
    """The reveal branch must guard against null children before mounting."""
    src = Path(RENDERER).read_text()
    match = re.search(
        r"else\s+if\s*\(\s*prevWasHidden\s*&&\s*!nextIsHidden\s*\)\s*\{(.+?)(?=\}\s*else|\}\s*\))",
        src,
        re.DOTALL,
    )
    assert match, "Could not locate the prevWasHidden && !nextIsHidden branch body"
    branch_body = match.group(1)
    # Should check child !== null before calling mountChildrenRecursively
    assert re.search(r"\.child\s*!==\s*null|nextChildSet\s*!==\s*null", branch_body), (
        "Missing null-check for fiber.child before calling mountChildrenRecursively"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """The reveal branch has real implementation (not just a comment or empty block)."""
    src = Path(RENDERER).read_text()
    match = re.search(
        r"else\s+if\s*\(\s*prevWasHidden\s*&&\s*!nextIsHidden\s*\)\s*\{(.+?)(?=\}\s*else|\}\s*\))",
        src,
        re.DOTALL,
    )
    assert match, "Missing reveal branch"
    branch_body = match.group(1)
    # Strip comments and whitespace
    stripped = re.sub(r"//[^\n]*", "", branch_body).strip()
    assert len(stripped) > 20, "Branch body appears to be a stub"
    # Must have at least one real statement (assignment or function call)
    assert re.search(r"[a-zA-Z_]\w*\s*\(|updateFlags\s*\|=", stripped), (
        "Branch body has no real statements"
    )
