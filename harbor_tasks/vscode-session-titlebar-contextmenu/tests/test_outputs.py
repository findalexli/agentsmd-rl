"""
Task: vscode-session-titlebar-contextmenu
Repo: microsoft/vscode @ 6a7e1b4bd33c970a4c5275ab90dbfd6a3cb91aa0
PR:   306419

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""
# AST-only because: TypeScript cannot be executed in Python; all checks
# are structural pattern searches on the source text.

import re
from pathlib import Path

REPO = "/workspace/vscode"
TITLEBAR = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts")
PROVIDER = Path(
    f"{REPO}/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist():
    """Both modified TypeScript files are present in the workspace."""
    assert TITLEBAR.exists(), f"Missing: {TITLEBAR}"
    assert PROVIDER.exists(), f"Missing: {PROVIDER}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioural fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_new_session_guard():
    """Context menu is suppressed for new/unsaved chat sessions.

    The base commit shows the context menu unconditionally; the fix adds an
    IsNewChatSessionContext guard that returns early before opening the menu.
    """
    src = TITLEBAR.read_text()
    assert "IsNewChatSessionContext" in src, (
        "IsNewChatSessionContext not imported — new-session guard is missing"
    )
    assert "IsNewChatSessionContext.key" in src, (
        "IsNewChatSessionContext.key not referenced — guard not applied"
    )
    # The guard must be inside a conditional that causes an early return
    # Look for the pattern: if (...IsNewChatSessionContext...) { return; }
    assert re.search(r"IsNewChatSessionContext\.key[^)]*\)[\s\S]{0,40}return", src), (
        "IsNewChatSessionContext check does not lead to an early return"
    )


# [pr_diff] fail_to_pass
def test_pinned_state_not_hardcoded():
    """IsSessionPinnedContext.key is no longer hardcoded to false.

    Base commit: [IsSessionPinnedContext.key, false]
    Fixed:       [IsSessionPinnedContext.key, isPinned]
    """
    src = TITLEBAR.read_text()
    assert "IsSessionPinnedContext.key, false" not in src, (
        "Bug still present: IsSessionPinnedContext.key is hardcoded to false"
    )


# [pr_diff] fail_to_pass
def test_pinned_state_dynamic():
    """Pinned state is dynamically resolved via IViewsService + isSessionPinned().

    The fix injects IViewsService, retrieves the SessionsView, and calls
    isSessionPinned(sessionData) to obtain the real pinned flag.
    """
    src = TITLEBAR.read_text()
    assert "IViewsService" in src, "IViewsService not injected into SessionsTitleBarWidget"
    assert "SessionsView" in src, "SessionsView not imported — needed for isSessionPinned lookup"
    assert "isSessionPinned(" in src, (
        "isSessionPinned() not called — pinned state still not dynamically fetched"
    )
    # The result must be wired to IsSessionPinnedContext (may span lines)
    assert re.search(
        r"IsSessionPinnedContext\.key.*isSessionPinned|isSessionPinned.*IsSessionPinnedContext\.key",
        src,
        re.DOTALL,
    ), "isSessionPinned() result is not passed to IsSessionPinnedContext.key"


# [pr_diff] fail_to_pass
def test_session_type_icon_method_exists():
    """Private _getSessionTypeIcon method added to AgentSessionAdapter.

    Base commit: no such method.  Fix: switch on session.providerType to
    return the correct ThemeIcon for Background and Cloud providers.
    """
    src = PROVIDER.read_text()
    assert "_getSessionTypeIcon" in src, (
        "_getSessionTypeIcon method not found in copilotChatSessionsProvider.ts"
    )
    assert re.search(r"switch\s*\([^)]*providerType", src), (
        "No switch(providerType) found inside _getSessionTypeIcon"
    )
    assert "AgentSessionProviders.Background" in src, (
        "Background provider case missing from _getSessionTypeIcon"
    )
    assert "AgentSessionProviders.Cloud" in src, (
        "Cloud provider case missing from _getSessionTypeIcon"
    )


# [pr_diff] fail_to_pass
def test_session_icon_uses_method():
    """this.icon is set via _getSessionTypeIcon(), not directly from session.icon.

    Base commit: this.icon = session.icon  (all provider types get the same icon)
    Fixed:       this.icon = this._getSessionTypeIcon(session)
    """
    src = PROVIDER.read_text()
    assert "this.icon = session.icon" not in src, (
        "Bug still present: this.icon assigned directly from session.icon"
    )
    assert "this._getSessionTypeIcon(" in src, (
        "this._getSessionTypeIcon() not called — icon method not wired up"
    )
