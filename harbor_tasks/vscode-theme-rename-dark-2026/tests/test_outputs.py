"""
Task: vscode-theme-rename-dark-2026
Repo: microsoft/vscode @ f91019e7676ab34ef03e1ccb550a7a6c949fa4cd

Fix: Rename "VS Code Dark"/"VS Code Light" themes to "Dark 2026"/"Light 2026",
update migration logic, and update default configuration.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path
import json

REPO = "/workspace/vscode"


def test_package_json_dark_2026():
    """package.json should reference Dark 2026 theme ID."""
    src = Path(f"{REPO}/extensions/theme-defaults/package.json").read_text()
    assert "Dark 2026" in src, "package.json should have Dark 2026 theme"


def test_package_json_light_2026():
    """package.json should reference Light 2026 theme ID."""
    src = Path(f"{REPO}/extensions/theme-defaults/package.json").read_text()
    assert "Light 2026" in src, "package.json should have Light 2026 theme"


def test_package_json_no_old_names():
    """package.json should not have old VS Code Dark/Light IDs."""
    src = Path(f"{REPO}/extensions/theme-defaults/package.json").read_text()
    data = json.loads(src)
    themes = data.get("contributes", {}).get("themes", [])
    ids = [t.get("id") for t in themes]
    assert "VS Code Dark" not in ids, "Old 'VS Code Dark' ID should be removed"
    assert "VS Code Light" not in ids, "Old 'VS Code Light' ID should be removed"


def test_nls_labels_updated():
    """package.nls.json should have 2026 theme labels."""
    src = Path(f"{REPO}/extensions/theme-defaults/package.nls.json").read_text()
    assert "dark2026ThemeLabel" in src or "Dark 2026" in src, \
        "NLS should have dark2026 label"
    assert "light2026ThemeLabel" in src or "Light 2026" in src, \
        "NLS should have light2026 label"


def test_theme_setting_defaults_updated():
    """ThemeSettingDefaults should use Dark 2026/Light 2026."""
    src = Path(f"{REPO}/src/vs/workbench/services/themes/common/workbenchThemeService.ts").read_text()
    assert "Dark 2026" in src, "COLOR_THEME_DARK should be 'Dark 2026'"
    assert "Light 2026" in src, "COLOR_THEME_LIGHT should be 'Light 2026'"


def test_migration_handles_old_names():
    """migrateThemeSettingsId should map old names to new names."""
    src = Path(f"{REPO}/src/vs/workbench/services/themes/common/workbenchThemeService.ts").read_text()
    assert "'VS Code Dark'" in src and "'VS Code Light'" in src, \
        "Migration should handle old VS Code Dark/Light names"


def test_configuration_uses_constant():
    """Sessions configuration should use ThemeSettingDefaults constant."""
    src = Path(f"{REPO}/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts").read_text()
    assert "ThemeSettingDefaults" in src, \
        "Configuration should use ThemeSettingDefaults constant"


def test_test_file_updated():
    """Test file should be updated with new theme names."""
    src = Path(f"{REPO}/src/vs/workbench/services/themes/test/common/workbenchThemeService.test.ts").read_text()
    assert "ThemeSettingDefaults" in src or "Dark 2026" in src, \
        "Test should reference new theme names"
