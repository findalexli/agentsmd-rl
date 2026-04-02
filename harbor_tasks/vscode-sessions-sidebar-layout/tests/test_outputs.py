"""
Task: vscode-sessions-sidebar-layout
Repo: microsoft/vscode @ 837894c2410fb23371e591be89f64f9a89f73efe

Fix: Sessions sidebar re-layout when toolbar items change dynamically.
Three files changed: aiCustomizationShortcutsWidget.ts, sessionsViewPane.css, sessionsView.ts.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only because: TypeScript cannot be imported; VS Code deps not available in container.
from pathlib import Path

REPO = "/workspace/vscode"
WIDGET = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/aiCustomizationShortcutsWidget.ts")
SESSIONS_VIEW = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts")
CSS = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/media/sessionsViewPane.css")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_toolbar_listens_for_menu_item_changes():
    """Widget subscribes to toolbar.onDidChangeMenuItems to re-layout when items appear/disappear."""
    content = WIDGET.read_text()
    assert "toolbar.onDidChangeMenuItems" in content, (
        "Widget must subscribe to toolbar.onDidChangeMenuItems so that dynamic toolbar changes "
        "(e.g. Plugins item appearing after extension activation) trigger a re-layout"
    )


# [pr_diff] fail_to_pass
def test_toolbar_stored_in_variable():
    """Toolbar instance must be captured in a variable so onDidChangeMenuItems can be wired up."""
    content = WIDGET.read_text()
    assert "const toolbar = " in content, (
        "The MenuWorkbenchToolBar instance must be stored in a const variable "
        "(e.g. 'const toolbar = this._register(...)') before subscribing to its events"
    )


# [pr_diff] fail_to_pass
def test_interface_option_renamed_to_on_did_change_layout():
    """Interface option onDidToggleCollapse renamed to onDidChangeLayout in widget."""
    content = WIDGET.read_text()
    assert "onDidChangeLayout" in content, (
        "IAICustomizationShortcutsWidgetOptions must expose onDidChangeLayout "
        "as the callback for re-layout (rename from onDidToggleCollapse)"
    )
    assert "onDidToggleCollapse" not in content, (
        "Old onDidToggleCollapse option must be fully removed from the widget; "
        "all references should use onDidChangeLayout"
    )


# [pr_diff] fail_to_pass
def test_sessions_view_passes_on_did_change_layout():
    """SessionsView must pass onDidChangeLayout callback (not the old onDidToggleCollapse)."""
    content = SESSIONS_VIEW.read_text()
    assert "onDidChangeLayout:" in content, (
        "SessionsView must pass 'onDidChangeLayout:' when constructing AICustomizationShortcutsWidget"
    )
    assert "onDidToggleCollapse:" not in content, (
        "SessionsView must not use the old 'onDidToggleCollapse:' key; rename to onDidChangeLayout"
    )


# [pr_diff] fail_to_pass
def test_css_margin_bottom_reduced():
    """CSS margin-bottom for the sessions list container reduced from 12px to 6px."""
    content = CSS.read_text()
    assert "margin-bottom: 6px" in content, (
        "sessionsViewPane.css must use 'margin-bottom: 6px' "
        "(reduced from 12px) for the sessions list container"
    )
    assert "margin-bottom: 12px" not in content, (
        "Old 'margin-bottom: 12px' must be removed from sessionsViewPane.css"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_sidebar_customizations_menu_preserved():
    """Menus.SidebarCustomizations must still be used — toolbar menu ID must not change."""
    content = WIDGET.read_text()
    assert "SidebarCustomizations" in content, (
        "Widget must continue to use Menus.SidebarCustomizations as the toolbar menu; "
        "this identifier should not be removed or renamed by the fix"
    )
