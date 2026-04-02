"""
Task: vscode-sessions-multiselect-contextmenu
Repo: microsoft/vscode @ 0705ebef87428a3a1d38df65b38da286a7b9174c

Context menu multi-select: right-clicking on a multi-selection in the Sessions
view should apply actions to all selected sessions, not just the one clicked.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/vscode"

SESSIONS_LIST = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts"
SESSIONS_ACTIONS = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts"
COPILOT_ACTIONS = f"{REPO}/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts"

ACTIONS = [
    "PinSessionAction",
    "UnpinSessionAction",
    "ArchiveSessionAction",
    "UnarchiveSessionAction",
    "MarkSessionReadAction",
    "MarkSessionUnreadAction",
    "OpenSessionInNewWindowAction",
]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sessions_list_collects_selection():
    """sessionsList.ts reads the current tree selection before building the context menu."""
    src = Path(SESSIONS_LIST).read_text()
    assert "this.tree.getSelection()" in src, (
        "sessionsList.ts must call this.tree.getSelection() to collect the multi-selection"
    )


# [pr_diff] fail_to_pass
def test_sessions_list_computes_selected_sessions():
    """sessionsList.ts computes a selectedSessions array that puts the right-clicked element first."""
    src = Path(SESSIONS_LIST).read_text()
    # The fix builds selectedSessions: element first if it's in the selection, otherwise just [element]
    assert "selectedSessions" in src, (
        "sessionsList.ts must define a selectedSessions variable"
    )
    assert "selection.includes(element)" in src, (
        "sessionsList.ts must check whether element is in the selection (selection.includes(element))"
    )


# [pr_diff] fail_to_pass
def test_context_menu_passes_selected_sessions():
    """Context menu getActions call uses selectedSessions as arg, not the bare element."""
    src = Path(SESSIONS_LIST).read_text()
    # After fix: arg: selectedSessions
    assert "arg: selectedSessions" in src, (
        "sessionsList.ts must pass selectedSessions (not element) as the menu arg"
    )
    # Negative: the old single-element arg should no longer be passed raw
    # (selectedSessions supersedes element in the arg position)
    assert "arg: element," not in src, (
        "sessionsList.ts must not pass bare 'element' as the menu arg anymore"
    )


# [pr_diff] fail_to_pass
def test_actions_accept_array_parameter():
    """All 7 session actions in sessionsViewActions.ts accept ISession | ISession[]."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = [a for a in ACTIONS if f"ISession | ISession[]" not in _class_body(src, a)]
    assert not missing, (
        f"These actions still only accept a single ISession (need ISession | ISession[]): {missing}"
    )


# [pr_diff] fail_to_pass
def test_actions_use_array_isarray_pattern():
    """All 7 actions normalize context to an array with Array.isArray(context) ? context : [context]."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = [a for a in ACTIONS if "Array.isArray(context)" not in _class_body(src, a)]
    assert not missing, (
        f"These actions are missing the Array.isArray(context) normalization: {missing}"
    )


# [pr_diff] fail_to_pass
def test_actions_iterate_over_sessions():
    """All 7 actions iterate over every session with a for-of loop."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = [a for a in ACTIONS if "for (const session of sessions)" not in _class_body(src, a)]
    assert not missing, (
        f"These actions are missing 'for (const session of sessions)' loop: {missing}"
    )


# [pr_diff] fail_to_pass
def test_copilot_bridge_accepts_array():
    """CopilotSessionContextMenuBridge wrapper command accepts ISession | ISession[]."""
    src = Path(COPILOT_ACTIONS).read_text()
    # The registerCommand callback signature must accept array
    assert "ISession | ISession[]" in src, (
        "copilotChatSessionsActions.ts bridge must accept ISession | ISession[] context"
    )
    assert "Array.isArray(context)" in src, (
        "copilotChatSessionsActions.ts bridge must use Array.isArray(context) to normalize"
    )


# [pr_diff] fail_to_pass
def test_copilot_bridge_uses_coalesce():
    """Bridge imports coalesce and uses it to map sessions, filtering nulls."""
    src = Path(COPILOT_ACTIONS).read_text()
    assert "coalesce" in src, (
        "copilotChatSessionsActions.ts must import and use coalesce() for null-safe session mapping"
    )
    assert "agentSessions" in src, (
        "copilotChatSessionsActions.ts bridge must build an agentSessions array (not a single agentSession)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_backward_compatible_single_session():
    """Array.isArray ternary preserves single-session callers in all 7 actions."""
    src = Path(SESSIONS_ACTIONS).read_text()
    # Every action must contain both branches of the ternary
    missing = [
        a for a in ACTIONS
        if "Array.isArray(context) ? context : [context]" not in _class_body(src, a)
    ]
    assert not missing, (
        f"These actions are missing the backward-compat ternary: {missing}"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified files have real implementation bodies, not empty stubs."""
    for path in [SESSIONS_LIST, SESSIONS_ACTIONS, COPILOT_ACTIONS]:
        src = Path(path).read_text()
        # A stub file would be tiny; real files are large TypeScript modules
        assert len(src) > 5000, f"{path} looks like a stub (only {len(src)} bytes)"
        # The fix must not reduce behavior to empty returns
        assert "for (const session of sessions)" in src or path == SESSIONS_LIST, (
            f"{path} is missing iteration logic"
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _class_body(src: str, class_name: str) -> str:
    """Return a window of text starting from the class declaration (~50 lines)."""
    idx = src.find(f"class {class_name}")
    if idx == -1:
        return ""
    return src[idx : idx + 2000]
