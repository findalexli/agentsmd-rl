"""
Task: vscode-theme-auto-notification
Repo: microsoft/vscode @ af50a47c13e23e0b3c46719dbd92fe00144362a5

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This is a TypeScript repo. Tests inspect source files directly since the
codebase cannot be compiled/executed in the minimal verifier environment.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
TARGET_FILE = Path(REPO) / "src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


def _src() -> str:
    return TARGET_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_method_exists():
    """showThemeAutoUpdatedNotification method must be defined in the service."""
    src = _src()
    # Must define the private method (any return type annotation)
    assert re.search(r"private\s+showThemeAutoUpdatedNotification\s*\(", src), (
        "showThemeAutoUpdatedNotification method not defined"
    )


# [pr_diff] fail_to_pass
def test_method_called_in_init():
    """showThemeAutoUpdatedNotification must be called during theme initialization."""
    src = _src()
    # The method must be invoked (not just defined)
    assert re.search(r"this\.showThemeAutoUpdatedNotification\s*\(\s*\)", src), (
        "showThemeAutoUpdatedNotification is never called"
    )


# [pr_diff] fail_to_pass
def test_storage_key_for_one_time_notification():
    """A storage key constant must exist to track whether the notification was shown."""
    src = _src()
    # Must have a static/const key for the auto-updated notification
    assert re.search(r"THEME_AUTO_UPDATED_NOTIFICATION_KEY", src), (
        "No storage key constant for the auto-updated notification"
    )
    # Must actually read from storage to guard against repeat display
    assert re.search(r"storageService\.getBoolean\s*\(.*THEME_AUTO_UPDATED_NOTIFICATION_KEY", src), (
        "Storage key not used in a getBoolean guard"
    )


# [pr_diff] fail_to_pass
def test_skips_new_users():
    """Notification must be suppressed for new (first-time) users."""
    src = _src()
    # Must check isNew before deciding to show the notification
    assert re.search(r"storageService\.isNew\s*\(", src), (
        "No storageService.isNew check — new users would incorrectly see the notification"
    )


# [pr_diff] fail_to_pass
def test_skips_explicit_theme_choice():
    """Notification must not show when the user explicitly chose their current theme."""
    src = _src()
    # Must guard with isDefaultColorTheme() so explicit picks are excluded
    assert re.search(r"isDefaultColorTheme\s*\(\s*\)", src), (
        "No isDefaultColorTheme() guard — users who explicitly chose a theme would see the notification"
    )


# [pr_diff] fail_to_pass
def test_has_browse_themes_action():
    """Notification must include an action to browse / pick a different theme."""
    src = _src()
    # Check for the browse-themes command (workbench.action.selectTheme) or a 'browseThemes' label key
    has_select_theme = "workbench.action.selectTheme" in src
    has_browse_label = bool(re.search(r"['\"]browseThemes['\"]", src))
    assert has_select_theme or has_browse_label, (
        "No Browse Themes action found in the notification"
    )


# [pr_diff] fail_to_pass
def test_has_revert_action():
    """Notification must include an action to revert to the previous default theme."""
    src = _src()
    # Check for setColorTheme call inside the notification handler (the revert logic)
    # and a revert/revertTheme label
    has_revert_label = bool(re.search(r"['\"]revertTheme['\"]", src))
    has_set_theme = bool(re.search(r"setColorTheme\s*\(", src))
    assert has_revert_label or has_set_theme, (
        "No Revert action found in the notification"
    )


# [pr_diff] fail_to_pass
def test_stores_shown_flag_on_close():
    """After the notification is dismissed, the shown flag must be persisted to storage."""
    src = _src()
    # Must write the notification key back to storage when the notification closes
    assert re.search(
        r"storageService\.store\s*\([^)]*THEME_AUTO_UPDATED_NOTIFICATION_KEY",
        src,
    ), (
        "Notification flag not stored on close — user would see notification again on restart"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — config-derived coding rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:132 @ af50a47c13e23e0b3c46719dbd92fe00144362a5
def test_nls_localize_used_for_notification():
    """User-facing notification message must use nls.localize (all visible strings must be externalized)."""
    # AST-only because: TypeScript cannot be executed in the verifier environment
    src = _src()
    method_match = re.search(
        r"private\s+showThemeAutoUpdatedNotification[\s\S]*?(?=\n\t(?:private|public|protected|\}))",
        src,
    )
    assert method_match, "showThemeAutoUpdatedNotification method not found"
    method_body = method_match.group(0)
    assert "nls.localize" in method_body, (
        "Notification strings must use nls.localize for localization "
        "(copilot-instructions.md:132)"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:144 @ af50a47c13e23e0b3c46719dbd92fe00144362a5
def test_disposable_registered_with_register():
    """Event listener on notification handle must be registered via _register / this._register."""
    # AST-only because: TypeScript cannot be executed in the verifier environment
    src = _src()
    method_match = re.search(
        r"private\s+showThemeAutoUpdatedNotification[\s\S]*?(?=\n\t(?:private|public|protected|\}))",
        src,
    )
    assert method_match, "showThemeAutoUpdatedNotification method not found"
    method_body = method_match.group(0)
    assert re.search(r"this\._register\s*\(", method_body), (
        "Disposable event listener not registered via this._register "
        "(copilot-instructions.md:144)"
    )
