"""
Task: vscode-theme-auto-updated-notification
Repo: microsoft/vscode @ 9d3144bf84f54ab1e886fca20608dd3ddc296f64

Fix: Add one-time notification for existing users whose color theme
changed because the product default was updated (e.g. Dark Modern to
VS Code Dark). Offers browse themes or revert options.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_notification_method_added():
    """showThemeAutoUpdatedNotification method should be added."""
    src = Path(TARGET).read_text()
    assert "showThemeAutoUpdatedNotification" in src, \
        "showThemeAutoUpdatedNotification should be defined"


def test_notification_key_defined():
    """THEME_AUTO_UPDATED_NOTIFICATION_KEY should be defined."""
    src = Path(TARGET).read_text()
    assert "THEME_AUTO_UPDATED_NOTIFICATION_KEY" in src, \
        "THEME_AUTO_UPDATED_NOTIFICATION_KEY should be defined"


def test_notification_called_in_initialize():
    """showThemeAutoUpdatedNotification should be called during initialization."""
    src = Path(TARGET).read_text()
    assert "this.showThemeAutoUpdatedNotification()" in src, \
        "Should call showThemeAutoUpdatedNotification in init"


def test_browse_themes_option():
    """Notification should offer a Browse Themes option."""
    src = Path(TARGET).read_text()
    assert "browseThemes" in src or "Browse Themes" in src, \
        "Should offer Browse Themes option"


def test_revert_option():
    """Notification should offer a Revert option."""
    src = Path(TARGET).read_text()
    assert "revertTheme" in src or "Revert" in src, \
        "Should offer Revert option"


def test_checks_is_new_user():
    """Should skip notification for new users (isNew check)."""
    src = Path(TARGET).read_text()
    assert "isNew" in src, \
        "Should check isNew to skip new users"


def test_checks_default_theme():
    """Should only show for users on the new default theme."""
    src = Path(TARGET).read_text()
    assert "isDefaultColorTheme" in src, \
        "Should check if user is on default theme"
