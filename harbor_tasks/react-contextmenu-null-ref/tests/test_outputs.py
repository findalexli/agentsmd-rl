"""
Task: react-contextmenu-null-ref
Repo: facebook/react @ 93882bd40ee48dc6d072dfc0b6cc7801fac1be31
PR:   35923

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
CONTEXT_MENU = Path(REPO) / "packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js"

# NOTE: Tests use regex/text checks rather than `node --check` because ContextMenu.js
# uses Flow type annotations (e.g. `(maybeMenu: HTMLDivElement)`) which are not
# valid vanilla JavaScript and would cause node --check to fail on all commits.


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_structure():
    """ContextMenu.js must exist and export a ContextMenu function with useLayoutEffect."""
    assert CONTEXT_MENU.exists(), f"File not found: {CONTEXT_MENU}"
    src = CONTEXT_MENU.read_text()
    assert len(src) > 200, "File appears empty or near-empty"
    assert "function ContextMenu" in src, "ContextMenu function not found in file"
    assert "useLayoutEffect" in src, "useLayoutEffect not found — core hook removed"
    assert "createPortal" in src, "createPortal not found — portal rendering removed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_createref_not_used_as_default():
    """createRef() must not be used as a default value for the ref prop.

    Root cause of the bug: `ref = createRef()` in the function signature creates a
    new ref object on every render. Because the new ref's .current is always null
    until after the DOM attaches, useLayoutEffect crashes immediately. The fix
    removes this default entirely and uses a stable internal ref instead.
    """
    src = CONTEXT_MENU.read_text()
    assert "ref = createRef()" not in src, (
        "createRef() is still used as default for ref prop — this causes a new ref "
        "to be created on every render, so ref.current is always null in the effect."
    )


# [pr_diff] fail_to_pass
def test_hidemenu_variable_and_early_return_in_effect():
    """useLayoutEffect must guard against early-render using a hideMenu variable.

    The fix extracts the early-return condition into `hideMenu` and checks it at
    the top of useLayoutEffect, returning early before attempting to access
    ref.current when the component is about to render nothing.
    """
    src = CONTEXT_MENU.read_text()
    # hideMenu variable must be defined
    assert "hideMenu" in src, (
        "hideMenu variable not found — early-return condition not extracted"
    )
    # useLayoutEffect must check hideMenu before accessing ref
    assert re.search(r"if\s*\(\s*hideMenu\s*\)", src), (
        "useLayoutEffect must check `if (hideMenu)` and return early "
        "before accessing menuRef.current"
    )


# [pr_diff] fail_to_pass
def test_null_check_before_using_ref():
    """menuRef.current must be null-checked before use in useLayoutEffect.

    Even after the hideMenu guard, the fix adds an explicit null assertion:
    `const maybeMenu = menuRef.current; if (maybeMenu === null) { throw ... }`
    This makes programming errors visible instead of silently crashing with a
    cryptic "cannot read property of null" error.
    """
    src = CONTEXT_MENU.read_text()
    # The fix captures menuRef.current in a local variable and null-checks it.
    # Accept either the exact pattern from the PR or a semantically equivalent guard.
    has_null_check = (
        re.search(r"menuRef\.current\s*===\s*null", src) or
        re.search(r"maybeMenu\s*===\s*null", src) or
        re.search(r"if\s*\(\s*!\s*menuRef\.current\s*\)", src)
    )
    assert has_null_check, (
        "No null check found for menuRef.current — the effect must guard against "
        "a null ref before calling methods like contains() on the element"
    )


# [pr_diff] fail_to_pass
def test_hidemenu_in_dependency_array():
    """useLayoutEffect dependency array must include hideMenu, not be empty.

    The base commit uses `[]` (empty deps), meaning the effect fires once on mount
    and never again. After the fix, the effect must re-run when hideMenu changes
    so that event listeners are properly added/removed when menu visibility toggles.
    """
    src = CONTEXT_MENU.read_text()
    # Must NOT have the buggy empty dep array
    # (use DOTALL so the regex can span the multi-line effect body)
    buggy_empty_deps = re.search(
        r"useLayoutEffect\s*\(.*?\},\s*\[\s*\]\s*\)",
        src,
        re.DOTALL,
    )
    assert not buggy_empty_deps, (
        "useLayoutEffect still has an empty dependency array `[]` — "
        "it must use `[hideMenu]` so the effect re-runs on visibility changes"
    )
    assert re.search(r"},\s*\[hideMenu\]\s*\)", src), (
        "useLayoutEffect dependency array must be `[hideMenu]`"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_internal_ref_replaces_prop_ref():
    """Component must use an internal React.useRef instead of the external ref prop.

    The fix replaces `<div ref={ref}>` (where ref came from props) with
    `<div ref={menuRef}>` (an internal ref created via React.useRef).
    This ensures the ref is stable across renders.
    """
    src = CONTEXT_MENU.read_text()
    assert "menuRef" in src, (
        "menuRef not found — internal ref not introduced"
    )
    # The JSX must attach menuRef (not the old prop ref) to the div
    assert re.search(r"ref=\{menuRef\}", src), (
        "Internal menuRef is not attached to the ContextMenu div element"
    )
    # The prop ref default should be gone
    assert "ref = createRef()" not in src, (
        "Old prop ref default still present alongside menuRef"
    )
