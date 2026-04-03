"""
Task: playwright-chorecli-scope-daemon-by-workspace
Repo: playwright @ 08752e9a9be05e5d11173977c8651cf105c1aace
PR:   microsoft/playwright#39144

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"

COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
SESSION_MGMT_MD = Path(REPO) / "packages/playwright/src/skill/references/session-management.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_command_names(src: str) -> list[str]:
    """Extract all declared command names from commands.ts source."""
    return re.findall(r"name:\s*['\"]([^'\"]+)['\"]", src)


# ---------------------------------------------------------------------------
# Code behavior tests (fail_to_pass) — core refactoring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_kill_all_renamed_to_session_kill_all():
    """The kill-all command must be renamed to session-kill-all in commands.ts."""
    src = COMMANDS_TS.read_text()
    names = _extract_command_names(src)
    assert "session-kill-all" in names, \
        "commands.ts must declare a command named 'session-kill-all'"
    assert "kill-all" not in names, \
        "commands.ts must not have old 'kill-all' command name"


# [pr_diff] fail_to_pass
def test_install_command_initializes_workspace():
    """The 'install' command must exist and be described as workspace initialization."""
    src = COMMANDS_TS.read_text()
    names = _extract_command_names(src)
    assert "install" in names, \
        "commands.ts must declare an 'install' command (not just install-browser)"
    # The install command description should reference workspace
    install_match = re.search(
        r"name:\s*['\"]install['\"].*?description:\s*['\"]([^'\"]+)['\"]",
        src, re.DOTALL
    )
    assert install_match, "Could not find install command declaration"
    desc = install_match.group(1).lower()
    assert "workspace" in desc or "initialize" in desc, \
        f"Install command description should mention workspace initialization, got: '{install_match.group(1)}'"


# [pr_diff] fail_to_pass
def test_workspace_scoping_replaces_installation_dir():
    """program.ts must use workspace-based scoping instead of installation-dir."""
    src = PROGRAM_TS.read_text()
    # Must have workspaceDirHash (new)
    assert "workspaceDirHash" in src, \
        "program.ts must use workspaceDirHash for workspace-scoped daemon isolation"
    # Must NOT have installationDirHash (old)
    assert "installationDirHash" not in src, \
        "program.ts must not reference old installationDirHash"


# [pr_diff] fail_to_pass
def test_find_workspace_dir_function():
    """program.ts must have a findWorkspaceDir function that looks for .playwright marker."""
    src = PROGRAM_TS.read_text()
    assert "findWorkspaceDir" in src, \
        "program.ts must define findWorkspaceDir function"
    # The function should look for .playwright directory
    assert ".playwright" in src, \
        "findWorkspaceDir should detect .playwright directory as workspace marker"


# [pr_diff] fail_to_pass
def test_config_path_updated():
    """Default config file path must be .playwright/cli.config.json (not playwright-cli.json)."""
    src = PROGRAM_TS.read_text()
    assert "cli.config.json" in src, \
        "program.ts must reference cli.config.json as the config file name"
    # Old path should be gone
    assert "playwright-cli.json" not in src, \
        "program.ts must not reference old playwright-cli.json config path"


# [pr_diff] fail_to_pass
def test_install_creates_playwright_dir():
    """The install function in program.ts must create a .playwright directory."""
    src = PROGRAM_TS.read_text()
    # Look for the install function creating .playwright
    install_fn = re.search(
        r"(?:async\s+)?function\s+install\s*\(",
        src
    )
    assert install_fn, \
        "program.ts must define an install() function (separate from installSkills)"
    # After the function definition, check it creates .playwright
    fn_start = install_fn.start()
    fn_region = src[fn_start:fn_start + 800]
    assert ".playwright" in fn_region, \
        "install() function must create .playwright workspace marker directory"


# [pr_diff] fail_to_pass
def test_session_kill_all_in_switch():
    """program.ts switch/case must route 'session-kill-all' (not 'kill-all')."""
    src = PROGRAM_TS.read_text()
    assert "session-kill-all" in src, \
        "program.ts must handle 'session-kill-all' command in the switch"
    # Check it's used as a case label, not just any string
    case_match = re.search(r"case\s+['\"]session-kill-all['\"]", src)
    assert case_match, \
        "program.ts must have case 'session-kill-all' in the command switch"


# ---------------------------------------------------------------------------
# Config/documentation update tests (config_edit) — REQUIRED
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_commands_ts_has_install_browser():
    """install-browser command must still exist (was renamed from old install)."""
    src = COMMANDS_TS.read_text()
    names = _extract_command_names(src)
    assert "install-browser" in names, \
        "commands.ts must still have 'install-browser' command for browser installation"


# [static] pass_to_pass
