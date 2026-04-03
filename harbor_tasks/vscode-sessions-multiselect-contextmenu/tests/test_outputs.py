"""
Task: vscode-sessions-multiselect-contextmenu
Repo: microsoft/vscode @ 0705ebef87428a3a1d38df65b38da286a7b9174c

Context menu multi-select: right-clicking on a multi-selection in the Sessions
view should apply actions to all selected sessions, not just the one clicked.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
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
# Helpers
# ---------------------------------------------------------------------------

def _class_body(src: str, class_name: str) -> str:
    """Return a window of text starting from the class declaration (~2000 chars)."""
    idx = src.find(f"class {class_name}")
    if idx == -1:
        return ""
    return src[idx : idx + 2000]


def _run_method_body(src: str, class_name: str) -> str:
    """Extract the run() method body from a class."""
    body = _class_body(src, class_name)
    idx = body.find("\trun(")
    if idx == -1:
        idx = body.find("\tasync run(")
    if idx == -1:
        return ""
    return body[idx : idx + 800]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# AST-only because: VS Code TypeScript modules require full VS Code DI to run
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sessions_list_collects_selection():
    """sessionsList.ts reads the current tree selection before building the context menu."""
    src = Path(SESSIONS_LIST).read_text()
    assert "this.tree.getSelection()" in src, (
        "sessionsList.ts must call this.tree.getSelection() to collect the multi-selection"
    )
    # Must filter out non-session items (sections, show-more placeholders)
    after_get_sel = src.split("getSelection()")[1][:300]
    assert "isSessionSection" in after_get_sel or "filter" in after_get_sel, (
        "getSelection() result must be filtered to exclude non-session items"
    )


# [pr_diff] fail_to_pass
def test_sessions_list_computes_selected_sessions():
    """sessionsList.ts computes a selectedSessions array with right-clicked element first."""
    src = Path(SESSIONS_LIST).read_text()
    assert "selectedSessions" in src, (
        "sessionsList.ts must define a selectedSessions variable"
    )
    assert "selection.includes(element)" in src or "selection.indexOf(element)" in src, (
        "sessionsList.ts must check whether element is in the selection"
    )


# [pr_diff] fail_to_pass
def test_context_menu_passes_selected_sessions():
    """Context menu getActions call uses selectedSessions as arg, not the bare element."""
    src = Path(SESSIONS_LIST).read_text()
    assert "arg: selectedSessions" in src, (
        "sessionsList.ts must pass selectedSessions (not element) as the menu arg"
    )
    assert "arg: element," not in src, (
        "sessionsList.ts must not pass bare 'element' as the menu arg anymore"
    )


# [pr_diff] fail_to_pass
def test_actions_accept_array_parameter():
    """All 7 session actions accept ISession | ISession[] in their run() signature."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = []
    for a in ACTIONS:
        run_body = _run_method_body(src, a)
        assert run_body, f"Could not find run() method in {a}"
        if "ISession[]" not in run_body:
            missing.append(a)
    assert not missing, (
        f"These actions still only accept a single ISession (need ISession | ISession[]): {missing}"
    )


# [pr_diff] fail_to_pass
def test_actions_use_array_isarray_pattern():
    """All 7 actions normalize context to an array with Array.isArray."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = []
    for a in ACTIONS:
        run_body = _run_method_body(src, a)
        if "Array.isArray" not in run_body:
            missing.append(a)
    assert not missing, (
        f"These actions are missing the Array.isArray normalization: {missing}"
    )


# [pr_diff] fail_to_pass
def test_actions_iterate_over_sessions():
    """All 7 actions iterate over every session."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = []
    for a in ACTIONS:
        run_body = _run_method_body(src, a)
        has_iteration = (
            "for " in run_body and " of " in run_body
        ) or "forEach" in run_body or ".map(" in run_body
        if not has_iteration:
            missing.append(a)
    assert not missing, (
        f"These actions are missing iteration over sessions: {missing}"
    )


# [pr_diff] fail_to_pass
def test_copilot_bridge_accepts_array():
    """CopilotSessionContextMenuBridge wrapper accepts ISession | ISession[]."""
    src = Path(COPILOT_ACTIONS).read_text()
    assert "ISession[]" in src, (
        "copilotChatSessionsActions.ts bridge must accept ISession[] context"
    )
    assert "Array.isArray" in src, (
        "copilotChatSessionsActions.ts bridge must use Array.isArray to normalize"
    )


# [pr_diff] fail_to_pass
def test_copilot_bridge_uses_coalesce():
    """Bridge imports coalesce and uses it to map sessions, filtering nulls."""
    src = Path(COPILOT_ACTIONS).read_text()
    assert "coalesce" in src, (
        "copilotChatSessionsActions.ts must import and use coalesce() for null-safe mapping"
    )
    assert "agentSessions" in src, (
        "copilotChatSessionsActions.ts bridge must build an agentSessions array"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_backward_compatible_single_session():
    """Array.isArray ternary preserves single-session callers in all 7 actions."""
    src = Path(SESSIONS_ACTIONS).read_text()
    missing = []
    for a in ACTIONS:
        run_body = _run_method_body(src, a)
        if "Array.isArray" not in run_body or "[context]" not in run_body:
            missing.append(a)
    assert not missing, (
        f"These actions are missing backward-compat Array.isArray ternary: {missing}"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified files have real implementation bodies, not empty stubs."""
    for path in [SESSIONS_LIST, SESSIONS_ACTIONS, COPILOT_ACTIONS]:
        src = Path(path).read_text()
        assert len(src) > 5000, f"{path} looks like a stub (only {len(src)} bytes)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# These are pass_to_pass: they verify the fix follows VS Code coding standards.
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:35 @ 0705ebef
def test_tabs_not_spaces():
    """New code in sessionsViewActions.ts uses tabs for indentation, not spaces."""
    actions_src = Path(SESSIONS_ACTIONS).read_text()
    for a in ACTIONS:
        run_body = _run_method_body(actions_src, a)
        for line in run_body.splitlines():
            if line and not line.isspace():
                # Every indented line must start with tab, not space
                if line != line.lstrip():
                    assert line[0] == '\t', (
                        f"In {a}, indented line must use tab, not space: {line[:60]!r}"
                    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:42 @ 0705ebef
def test_curly_braces_on_loops():
    """Loop bodies in the fix are surrounded with curly braces."""
    actions_src = Path(SESSIONS_ACTIONS).read_text()
    for a in ACTIONS:
        run_body = _run_method_body(actions_src, a)
        lines = run_body.splitlines()
        for i, line in enumerate(lines):
            if re.search(r'\bfor\s*\(', line):
                # The for statement or next line must have an opening brace
                rest = "".join(lines[i:i+2])
                assert "{" in rest, (
                    f"In {a}, for loop must have curly braces: {line.strip()}"
                )
