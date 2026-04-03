"""
Task: playwright-chorecli-session-b
Repo: microsoft/playwright @ 605d93d732c5ab752ae314ac47fdd6ad3abc11de
PR:   39156

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"
COMMAND_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
HELP_GEN_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
SESSION_MGMT_MD = Path(REPO) / "packages/playwright/src/skill/references/session-management.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files have balanced braces."""
    for ts_file in [COMMAND_TS, COMMANDS_TS, HELP_GEN_TS, PROGRAM_TS]:
        content = ts_file.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {ts_file.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: command renames
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_command_names_renamed():
    """Session commands must be renamed: session-list -> list, session-close-all -> close-all, session-kill-all -> kill-all."""
    content = COMMANDS_TS.read_text()
    # New names must exist
    assert re.search(r"name:\s*['\"]list['\"]", content), \
        "commands.ts must declare command name 'list'"
    assert re.search(r"name:\s*['\"]close-all['\"]", content), \
        "commands.ts must declare command name 'close-all'"
    assert re.search(r"name:\s*['\"]kill-all['\"]", content), \
        "commands.ts must declare command name 'kill-all'"
    # Old names must be gone
    assert "session-list" not in content, \
        "commands.ts must not contain old 'session-list' command name"
    assert "session-close-all" not in content, \
        "commands.ts must not contain old 'session-close-all' command name"
    assert "session-kill-all" not in content, \
        "commands.ts must not contain old 'session-kill-all' command name"


# [pr_diff] fail_to_pass
def test_category_renamed_to_browsers():
    """The 'session' category must be renamed to 'browsers' in both command.ts and commands.ts."""
    cmd_content = COMMAND_TS.read_text()
    cmds_content = COMMANDS_TS.read_text()
    # Category type must include 'browsers', not 'session'
    assert "'browsers'" in cmd_content, \
        "command.ts Category type must include 'browsers'"
    assert "'session'" not in cmd_content, \
        "command.ts Category type must not include 'session' (should be 'browsers')"
    # Commands must use 'browsers' category
    assert re.search(r"category:\s*['\"]browsers['\"]", cmds_content), \
        "commands.ts session commands must use category 'browsers'"


# [pr_diff] fail_to_pass
def test_program_switch_uses_new_names():
    """program.ts switch statement must use 'list', 'close-all', 'kill-all' instead of old names."""
    content = PROGRAM_TS.read_text()
    assert "case 'list'" in content, \
        "program.ts must have case 'list'"
    assert "case 'close-all'" in content, \
        "program.ts must have case 'close-all'"
    assert "case 'kill-all'" in content, \
        "program.ts must have case 'kill-all'"
    assert "case 'session-list'" not in content, \
        "program.ts must not have old case 'session-list'"


# [pr_diff] fail_to_pass
def test_b_flag_alias():
    """program.ts must normalize -b flag to --session."""
    content = PROGRAM_TS.read_text()
    # Must have logic to handle args.b
    assert "args.b" in content, \
        "program.ts must handle -b flag (args.b)"
    assert "args.session" in content, \
        "program.ts must assign args.b to args.session"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md and session-management.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_session_mgmt_md_heading_updated():
    """session-management.md title must reference 'Browser' in heading."""
    content = SESSION_MGMT_MD.read_text()
    first_line = content.strip().split("\n")[0]
    assert "browser" in first_line.lower(), \
        "session-management.md heading should mention 'Browser'"


# [static] pass_to_pass


# [static] pass_to_pass
def test_program_still_handles_open_close():
    """program.ts must still handle 'open' and 'close' commands."""
    content = PROGRAM_TS.read_text()
    assert "case 'open'" in content, "program.ts must handle 'open' command"
    assert "case 'close'" in content, "program.ts must handle 'close' command"
    assert "case 'delete-data'" in content, "program.ts must handle 'delete-data' command"
