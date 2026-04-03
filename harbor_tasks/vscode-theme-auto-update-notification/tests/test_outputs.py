"""
Task: vscode-theme-auto-update-notification
Repo: microsoft/vscode @ d527672704494fd0cf3cc546dbcb259db37cc5ab

Fix: Remove the showThemeAutoUpdatedNotification method and its call,
reverting a premature auto-update notification feature.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_notification_method_removed():
    """showThemeAutoUpdatedNotification method should be removed."""
    src = Path(TARGET).read_text()
    assert "showThemeAutoUpdatedNotification" not in src, \
        "showThemeAutoUpdatedNotification should be removed"


def test_notification_key_removed():
    """THEME_AUTO_UPDATED_NOTIFICATION_KEY constant should be removed."""
    src = Path(TARGET).read_text()
    assert "THEME_AUTO_UPDATED_NOTIFICATION_KEY" not in src, \
        "THEME_AUTO_UPDATED_NOTIFICATION_KEY should be removed"


def test_show_new_default_remains():
    """showNewDefaultThemeNotification should still be called."""
    src = Path(TARGET).read_text()
    assert "showNewDefaultThemeNotification" in src, \
        "showNewDefaultThemeNotification should still exist"


def test_no_auto_updated_text():
    """The auto-updated notification message text should be removed."""
    src = Path(TARGET).read_text()
    assert "newDefaultThemeAutoUpdated" not in src, \
        "newDefaultThemeAutoUpdated localization key should be removed"
