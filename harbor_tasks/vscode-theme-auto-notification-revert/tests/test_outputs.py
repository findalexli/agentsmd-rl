"""
Task: vscode-theme-auto-notification-revert
Repo: microsoft/vscode @ d4b002af75f1878ead5b608beed470b9ae25b6f8
PR:   306341

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
THEME_FILE = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified file compiles without TypeScript errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "src/vs/workbench/services/themes/browser/workbenchThemeService.ts"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_notification_method_removed():
    """showThemeAutoUpdatedNotification method must not exist after the fix."""
    content = Path(THEME_FILE).read_text()
    assert "showThemeAutoUpdatedNotification" not in content, \
        "showThemeAutoUpdatedNotification method was not removed"


# [pr_diff] fail_to_pass
def test_notification_key_removed():
    """THEME_AUTO_UPDATED_NOTIFICATION_KEY constant must not exist after the fix."""
    content = Path(THEME_FILE).read_text()
    assert "THEME_AUTO_UPDATED_NOTIFICATION_KEY" not in content, \
        "THEME_AUTO_UPDATED_NOTIFICATION_KEY constant was not removed"


# [pr_diff] fail_to_pass
def test_notification_call_removed():
    """The call to showThemeAutoUpdatedNotification() must not exist in initialize()."""
    content = Path(THEME_FILE).read_text()
    assert "this.showThemeAutoUpdatedNotification()" not in content, \
        "showThemeAutoUpdatedNotification() call was not removed from initialize()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_new_default_notification_preserved():
    """showNewDefaultThemeNotification must still exist (not accidentally removed)."""
    content = Path(THEME_FILE).read_text()
    assert "showNewDefaultThemeNotification" in content, \
        "showNewDefaultThemeNotification was incorrectly removed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:130 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_copyright_header():
    """All files must include Microsoft copyright header."""
    lines = Path(THEME_FILE).read_text().splitlines()
    header_region = "\n".join(lines[:5]).lower()
    assert "microsoft" in header_region, \
        "Missing Microsoft copyright header in first 5 lines of file"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_tabs_indentation():
    """We use tabs, not spaces for indentation."""
    lines = Path(THEME_FILE).read_text().splitlines()
    # Count lines that start with 4+ spaces but no leading tab (space-indented)
    space_indented = sum(1 for l in lines if l.startswith("    ") and not l.startswith("\t"))
    assert space_indented < 20, \
        f"File has {space_indented} space-indented lines; tabs should be used instead of spaces"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:138 @ d4b002af75f1878ead5b608beed470b9ae25b6f8
def test_no_duplicate_imports():
    """Never duplicate imports. Always reuse existing imports if they are present."""
    import_lines = [
        l.strip() for l in Path(THEME_FILE).read_text().splitlines()
        if l.strip().startswith("import ")
    ]
    duplicates = {l for l in import_lines if import_lines.count(l) > 1}
    assert not duplicates, f"Duplicate import statements found: {duplicates}"
