"""
Task: react-devtools-resizeobserver-overflow
Repo: facebook/react @ 3aaab92a265ebeb43b15e7c30c2f1dfb9fcd5961
PR:   35694

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
HOOKS_FILE = REPO + "/packages/react-devtools-shared/src/devtools/views/hooks.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """hooks.js must be syntactically valid JavaScript."""
    r = subprocess.run(
        ["node", "--check", HOOKS_FILE],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in hooks.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_uses_resizeobserver():
    """useIsOverflowing must use ResizeObserver instead of window resize events."""
    content = Path(HOOKS_FILE).read_text()
    assert "ResizeObserver" in content, (
        "ResizeObserver not found in hooks.js — must replace window resize listener"
    )


# [pr_diff] fail_to_pass
def test_observes_container():
    """ResizeObserver must call observe() on the container element."""
    content = Path(HOOKS_FILE).read_text()
    assert "observer.observe" in content, (
        "observer.observe() not found — ResizeObserver must observe the container"
    )


# [pr_diff] fail_to_pass
def test_uses_contentRect_width():
    """Overflow detection must use ResizeObserver entry's contentRect.width."""
    content = Path(HOOKS_FILE).read_text()
    assert "contentRect.width" in content, (
        "contentRect.width not found — must use ResizeObserver entry width for measurement"
    )


# [pr_diff] fail_to_pass
def test_no_window_resize_listener():
    """Window resize event listener must be removed (replaced by ResizeObserver)."""
    content = Path(HOOKS_FILE).read_text()
    # Old code: ownerWindow.addEventListener('resize', handleResize)
    assert not re.search(r"addEventListener\s*\(\s*['\"]resize['\"]", content), (
        "addEventListener('resize', ...) still present — must be replaced by ResizeObserver"
    )


# [pr_diff] fail_to_pass
def test_disconnect_cleanup():
    """ResizeObserver must be disconnected on cleanup (replaces removeEventListener)."""
    content = Path(HOOKS_FILE).read_text()
    assert "disconnect" in content, (
        "disconnect() not found — ResizeObserver must be disconnected in cleanup return"
    )


# [pr_diff] fail_to_pass
def test_owner_document_resizeobserver():
    """ResizeObserver must be obtained from container's owner document for browser extension support."""
    content = Path(HOOKS_FILE).read_text()
    # The fix uses container.ownerDocument.defaultView.ResizeObserver so that it works
    # in browser extensions where portals may be in a different window/document.
    assert "ownerDocument" in content, (
        "ownerDocument not found — ResizeObserver must be sourced from "
        "container.ownerDocument.defaultView to support browser extension portals"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guards
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_uselayouteffect_preserved():
    """useLayoutEffect must still be used to avoid flash of overflowed content."""
    content = Path(HOOKS_FILE).read_text()
    assert "useLayoutEffect" in content, (
        "useLayoutEffect removed — must be preserved to avoid flash of overflowed content"
    )
