"""
Task: vscode-theme-rename-dark-2026
Repo: microsoft/vscode @ f91019e7676ab34ef03e1ccb550a7a6c949fa4cd

Fix: Rename "VS Code Dark"/"VS Code Light" themes to "Dark 2026"/"Light 2026",
update migration logic, and update default configuration.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path
import json
import subprocess

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


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD Checks)
# These verify the repo's own quality checks pass on both base and fixed code.
# =============================================================================


def test_repo_stylelint():
    """Repo's Stylelint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "stylelint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-500:]}"


def test_repo_valid_layers():
    """Repo's valid-layers-check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "valid-layers-check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Valid-layers-check failed:\n{r.stderr[-500:]}"


def test_repo_precommit():
    """Repo's precommit/hygiene checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "precommit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Precommit hygiene failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests_node():
    """Repo's Node unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Node unit tests failed:\n{r.stderr[-500:]}"


def test_repo_monaco_compile_check():
    """Repo's Monaco compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "monaco-compile-check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Monaco compile check failed:\n{r.stderr[-500:]}"


def test_repo_tsec_compile_check():
    """Repo's tsec compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsec-compile-check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"tsec compile check failed:\n{r.stderr[-500:]}"


def test_repo_vscode_dts_compile_check():
    """Repo's vscode-dts compile check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "vscode-dts-compile-check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"vscode-dts compile check failed:\n{r.stderr[-500:]}"
