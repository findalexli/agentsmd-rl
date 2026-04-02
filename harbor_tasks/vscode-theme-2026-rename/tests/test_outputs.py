"""
Task: vscode-theme-2026-rename
Repo: microsoft/vscode @ 573fb0a665c269634b8eb30759b6f2584c0ff127
PR:   306356

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TS_SERVICE = f"{REPO}/src/vs/workbench/services/themes/common/workbenchThemeService.ts"
CONTRIB = f"{REPO}/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts"
PKG_JSON = f"{REPO}/extensions/theme-defaults/package.json"
PKG_NLS = f"{REPO}/extensions/theme-defaults/package.nls.json"


def _read_theme_service() -> str:
    return Path(TS_SERVICE).read_text()


def _extract_constant(src: str, name: str) -> str:
    m = re.search(rf"export\s+const\s+{name}\s*=\s*'([^']*)'", src)
    assert m, f"ThemeSettingDefaults.{name} constant not found in workbenchThemeService.ts"
    return m.group(1)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — ThemeSettingDefaults constants renamed
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_constant_color_theme_dark():
    """ThemeSettingDefaults.COLOR_THEME_DARK must equal 'Dark 2026' after the rename."""
    src = _read_theme_service()
    val = _extract_constant(src, "COLOR_THEME_DARK")
    assert val == "Dark 2026", f"Expected 'Dark 2026', got '{val}'"


# [pr_diff] fail_to_pass
def test_constant_color_theme_light():
    """ThemeSettingDefaults.COLOR_THEME_LIGHT must equal 'Light 2026' after the rename."""
    src = _read_theme_service()
    val = _extract_constant(src, "COLOR_THEME_LIGHT")
    assert val == "Light 2026", f"Expected 'Light 2026', got '{val}'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — migrateThemeSettingsId handles renamed IDs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_migrate_handles_vscode_dark():
    """migrateThemeSettingsId must have a case for 'VS Code Dark' to migrate old settings."""
    src = _read_theme_service()
    assert "case 'VS Code Dark':" in src, \
        "migrateThemeSettingsId is missing a case for 'VS Code Dark'"


# [pr_diff] fail_to_pass
def test_migrate_handles_vscode_light():
    """migrateThemeSettingsId must have a case for 'VS Code Light' to migrate old settings."""
    src = _read_theme_service()
    assert "case 'VS Code Light':" in src, \
        "migrateThemeSettingsId is missing a case for 'VS Code Light'"


# [pr_diff] fail_to_pass
def test_migrate_uses_constant_reference():
    """Migration cases must return ThemeSettingDefaults constants, not old string literals."""
    src = _read_theme_service()
    # After fix: cases return the constant reference
    assert "return ThemeSettingDefaults.COLOR_THEME_DARK" in src, \
        "Migration should return ThemeSettingDefaults.COLOR_THEME_DARK (not a string literal)"
    assert "return ThemeSettingDefaults.COLOR_THEME_LIGHT" in src, \
        "Migration should return ThemeSettingDefaults.COLOR_THEME_LIGHT (not a string literal)"
    # After fix: no migration should return the old literal strings
    assert "return 'VS Code Dark'" not in src, \
        "Migration must not return hardcoded string 'VS Code Dark'"
    assert "return 'VS Code Light'" not in src, \
        "Migration must not return hardcoded string 'VS Code Light'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — package metadata updated
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_json_has_dark_2026_id():
    """extensions/theme-defaults/package.json must declare a theme with id 'Dark 2026'."""
    data = json.loads(Path(PKG_JSON).read_text())
    theme_ids = [t.get("id") for t in data.get("contributes", {}).get("themes", [])]
    assert "Dark 2026" in theme_ids, \
        f"package.json themes do not include 'Dark 2026'. Found: {theme_ids}"


# [pr_diff] fail_to_pass
def test_package_json_has_light_2026_id():
    """extensions/theme-defaults/package.json must declare a theme with id 'Light 2026'."""
    data = json.loads(Path(PKG_JSON).read_text())
    theme_ids = [t.get("id") for t in data.get("contributes", {}).get("themes", [])]
    assert "Light 2026" in theme_ids, \
        f"package.json themes do not include 'Light 2026'. Found: {theme_ids}"


# [pr_diff] fail_to_pass
def test_package_nls_json_new_keys():
    """package.nls.json must have new localization keys for Dark 2026 and Light 2026."""
    nls = json.loads(Path(PKG_NLS).read_text())
    assert "dark2026ThemeLabel" in nls, \
        "package.nls.json missing key 'dark2026ThemeLabel'"
    assert "light2026ThemeLabel" in nls, \
        "package.nls.json missing key 'light2026ThemeLabel'"
    assert nls.get("dark2026ThemeLabel") == "Dark 2026", \
        f"Expected nls['dark2026ThemeLabel'] == 'Dark 2026', got '{nls.get('dark2026ThemeLabel')}'"
    assert nls.get("light2026ThemeLabel") == "Light 2026", \
        f"Expected nls['light2026ThemeLabel'] == 'Light 2026', got '{nls.get('light2026ThemeLabel')}'"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — use constant instead of hardcoded string
# Source: .github/copilot-instructions.md:143 @ 573fb0a665c269634b8eb30759b6f2584c0ff127
# "Do not duplicate code. Always look for existing utility functions, helpers,
#  or patterns in the codebase before implementing new functionality."
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:143 @ 573fb0a665c269634b8eb30759b6f2584c0ff127
def test_configuration_no_hardcoded_theme_string():
    """configuration.contribution.ts must use ThemeSettingDefaults.COLOR_THEME_DARK, not a hardcoded string."""
    src = Path(CONTRIB).read_text()
    # Must reference the constant (not be absent entirely)
    assert "ThemeSettingDefaults.COLOR_THEME_DARK" in src, \
        "configuration.contribution.ts must use ThemeSettingDefaults.COLOR_THEME_DARK"
    # Must not duplicate the constant value as a string literal
    assert "'VS Code Dark'" not in src, \
        "configuration.contribution.ts still contains hardcoded string 'VS Code Dark'"
    assert "'Dark 2026'" not in src, \
        "configuration.contribution.ts must not hardcode 'Dark 2026' — use ThemeSettingDefaults.COLOR_THEME_DARK"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — legacy migrations must not be broken
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_legacy_migrations_preserved():
    """Existing Default Dark/Light Modern/Plus migrations must still be present."""
    src = _read_theme_service()
    legacy = [
        ("case 'Default Dark Modern': return 'Dark Modern';",  "Default Dark Modern → Dark Modern"),
        ("case 'Default Light Modern': return 'Light Modern';", "Default Light Modern → Light Modern"),
        ("case 'Default Dark+': return 'Dark+';",              "Default Dark+ → Dark+"),
        ("case 'Default Light+': return 'Light+';",            "Default Light+ → Light+"),
    ]
    for pattern, label in legacy:
        assert pattern in src, f"Legacy migration broken: {label}"
