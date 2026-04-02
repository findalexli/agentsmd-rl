"""
Task: vscode-changes-view-modal-styles
Repo: microsoft/vscode @ 00356ebc69d09b93830f05eb4eabf872d425abdd

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CHANGESVIEW_TS = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts")
CHANGESVIEW_CSS = Path(f"{REPO}/src/vs/sessions/contrib/changes/browser/media/changesView.css")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript must compile without errors after the fix is applied."""
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_modal_navigation_conditional_on_item_count():
    """openFileItem 6th arg must be items.length > 1, not hardcoded true.

    Single-item lists should open without modal navigation;
    multi-item lists keep modal multi-file navigation enabled.
    """
    content = CHANGESVIEW_TS.read_text()
    assert (
        "openFileItem(e.element, items, e.sideBySide, "
        "!!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, items.length > 1)"
    ) in content, "openFileItem 6th argument must be 'items.length > 1', not hardcoded 'true'"
    assert (
        "openFileItem(e.element, items, e.sideBySide, "
        "!!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, true)"
    ) not in content, "openFileItem must not use hardcoded 'true' for modal navigation parameter"


# [pr_diff] fail_to_pass
def test_css_action_bar_visibility_uses_chat_editing_session_list():
    """CSS action bar hover/focus/select selectors must use .chat-editing-session-list.

    The parent selector must be broad enough to cover modal-editor contexts,
    not just the Changes View pane (.changes-view-body).
    """
    content = CHANGESVIEW_CSS.read_text()
    assert (
        ".chat-editing-session-list .monaco-list-row:hover .chat-collapsible-list-action-bar"
        in content
    ), "CSS hover selector must use .chat-editing-session-list"
    assert (
        ".chat-editing-session-list .monaco-list-row.focused .chat-collapsible-list-action-bar"
        in content
    ), "CSS focused selector must use .chat-editing-session-list"
    assert (
        ".chat-editing-session-list .monaco-list-row.selected .chat-collapsible-list-action-bar"
        in content
    ), "CSS selected selector must use .chat-editing-session-list"


# [pr_diff] fail_to_pass
def test_css_diff_stats_hide_uses_chat_editing_session_list():
    """CSS working-set-line-counts hiding selectors must use .chat-editing-session-list."""
    content = CHANGESVIEW_CSS.read_text()
    assert (
        ".chat-editing-session-list .monaco-list-row:hover "
        ".monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) "
        ".working-set-line-counts"
    ) in content, "CSS diff-stats hover selector must use .chat-editing-session-list"
    assert (
        ".chat-editing-session-list .monaco-list-row.focused "
        ".monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) "
        ".working-set-line-counts"
    ) in content, "CSS diff-stats focused selector must use .chat-editing-session-list"
    assert (
        ".chat-editing-session-list .monaco-list-row.selected "
        ".monaco-icon-label:has(.chat-collapsible-list-action-bar:not(.has-no-actions)) "
        ".working-set-line-counts"
    ) in content, "CSS diff-stats selected selector must use .chat-editing-session-list"


# [pr_diff] fail_to_pass
def test_css_no_changes_view_body_selectors():
    """All .changes-view-body selectors in the action bar / diff-stats blocks must be removed."""
    content = CHANGESVIEW_CSS.read_text()
    assert ".changes-view-body" not in content, (
        "CSS must not contain .changes-view-body selectors; "
        "they should be replaced with .chat-editing-session-list"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_layering_rules():
    """VS Code module layering rules must still pass (no forbidden cross-layer imports)."""
    r = subprocess.run(
        ["npm", "run", "valid-layers-check"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Layering check failed:\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-500:]}"
    )
