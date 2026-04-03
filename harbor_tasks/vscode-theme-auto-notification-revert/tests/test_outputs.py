"""
Task: vscode-theme-auto-notification-revert
Repo: microsoft/vscode @ d4b002af75f1878ead5b608beed470b9ae25b6f8
PR:   306341

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
THEME_FILE = f"{REPO}/src/vs/workbench/services/themes/browser/workbenchThemeService.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified file has no obvious syntax errors (balanced braces, no stray tokens)."""
    content = Path(THEME_FILE).read_text()
    # Basic sanity: file is non-empty and braces are roughly balanced
    assert len(content) > 1000, "File appears truncated or empty"
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert abs(open_braces - close_braces) < 5, (
        f"Brace mismatch: {open_braces} open vs {close_braces} close — likely a syntax error"
    )
    # Check that the file still has the class declaration
    assert "class WorkbenchThemeService" in content, "WorkbenchThemeService class missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_notification_method_removed():
    """showThemeAutoUpdatedNotification method must not exist after the fix."""
    content = Path(THEME_FILE).read_text()
    # Check both the method declaration and any references
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


# [pr_diff] fail_to_pass
def test_revert_notification_string_removed():
    """The notification localization string for auto-updated theme must be removed."""
    content = Path(THEME_FILE).read_text()
    assert "newDefaultThemeAutoUpdated" not in content, \
        "The 'newDefaultThemeAutoUpdated' localization key was not removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_new_default_notification_preserved():
    """showNewDefaultThemeNotification must still exist (not accidentally removed)."""
    content = Path(THEME_FILE).read_text()
    assert "showNewDefaultThemeNotification" in content, \
        "showNewDefaultThemeNotification was incorrectly removed"


# [pr_diff] pass_to_pass
def test_new_theme_notification_key_preserved():
    """NEW_THEME_NOTIFICATION_KEY constant must still exist."""
    content = Path(THEME_FILE).read_text()
    assert "NEW_THEME_NOTIFICATION_KEY" in content, \
        "NEW_THEME_NOTIFICATION_KEY was incorrectly removed"


# [pr_diff] pass_to_pass
def test_initialize_method_intact():
    """The initialize() method must still call showNewDefaultThemeNotification."""
    content = Path(THEME_FILE).read_text()
    # Find the initialize method and verify it still has the new default notification call
    init_match = re.search(
        r'async\s+initialize\b.*?^\t\}',
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert init_match, "Could not find initialize() method"
    init_body = init_match.group(0)
    assert "showNewDefaultThemeNotification" in init_body, \
        "initialize() no longer calls showNewDefaultThemeNotification()"
    assert "showThemeAutoUpdatedNotification" not in init_body, \
        "initialize() still calls showThemeAutoUpdatedNotification()"


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
    """Use tabs, not spaces for indentation."""
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
