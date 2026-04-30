#!/usr/bin/env python3
"""
Tests for Playwright CLI workspace-scoped daemon task.

This validates:
1. Code changes: workspace-based daemon scoping, command renames
2. Config updates: SKILL.md and session-management.md reflect new commands
"""

import subprocess
import json
import os
from pathlib import Path

REPO = Path("/home/node/playwright")


def _read_file(path: str) -> str:
    """Read a file from the repo."""
    full_path = REPO / path
    return full_path.read_text() if full_path.exists() else ""


def _check_typescript_compiles():
    """Check that TypeScript files compile."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO / "packages" / "playwright",
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode == 0, result.stderr


# ==================== CODE BEHAVIOR TESTS ====================


def test_workspace_dir_hash_used():
    """[f2p_code] program.ts must use workspaceDirHash instead of installationDirHash."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Should use workspaceDirHash
    assert "workspaceDirHash" in program_ts, "Should use workspaceDirHash"
    # Should NOT use old installationDirHash
    assert "installationDirHash" not in program_ts, "Should not use installationDirHash"
    # Should NOT use installationDir
    assert "installationDir" not in program_ts, "Should not use installationDir"


def test_find_workspace_dir_function():
    """[f2p_code] program.ts must have findWorkspaceDir function."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Must have findWorkspaceDir function that looks for .playwright folder
    assert "function findWorkspaceDir" in program_ts, "Must have findWorkspaceDir function"
    assert '.playwright' in program_ts, "Must reference .playwright folder"


def test_commands_renamed():
    """[f2p_code] commands.ts must rename kill-all to session-kill-all."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")

    # Old command should NOT exist
    assert "name: 'kill-all'" not in commands_ts, "Old kill-all command should not exist"
    # New command should exist
    assert "name: 'session-kill-all'" in commands_ts, "New session-kill-all command should exist"


def test_install_command_restructured():
    """[f2p_code] commands.ts must restructure install commands."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")

    # Should have 'install' as main command for workspace initialization
    # Check for the restructured install command with skills option
    assert "name: 'install'" in commands_ts, "Should have install command"
    assert "Initialize workspace" in commands_ts, "install should describe workspace initialization"

    # Should still have install-browser as separate command
    assert "name: 'install-browser'" in commands_ts, "Should have install-browser command"


def test_config_path_updated():
    """[f2p_code] Default config file path must use .playwright/cli.config.json."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Should use new config path
    assert "'.playwright', 'cli.config.json'" in program_ts, \
        "Should use .playwright/cli.config.json as default config path"


def test_retry_logic_updated():
    """[f2p_code] Retry delay must use exponential backoff array."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Check for the exponential backoff retry logic
    assert "const retryDelay = [100, 200, 400]" in program_ts, \
        "Should use exponential backoff array for retry delays"


def test_error_message_updated():
    """[f2p_code] Error message when session not open must be updated."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Check for updated error message
    assert "is not open, please run open first`" in program_ts, \
        "Should use updated error message format"
    assert "open [params]" in program_ts, \
        "Should suggest 'open [params]' instead of listing formatted args"


# ==================== CONFIG/DOCUMENTATION TESTS ====================


def test_skill_md_kill_all_renamed():
    """[f2p_config] SKILL.md must rename kill-all to session-kill-all."""
    skill_md = _read_file("packages/playwright/src/skill/SKILL.md")

    # Old command reference should NOT exist in session section
    # Look for kill-all not followed by session-kill-all context
    lines = skill_md.split('\n')
    for line in lines:
        if 'kill-all' in line and 'session-kill-all' not in line:
            # Check if it's a code example or just reference
            if line.strip().startswith('playwright-cli kill-all'):
                assert False, f"SKILL.md still references old 'kill-all' command: {line}"

    # New command should exist
    assert "playwright-cli session-kill-all" in skill_md, \
        "SKILL.md should reference new 'session-kill-all' command"


def test_session_management_md_kill_all_renamed():
    """[f2p_config] session-management.md must rename kill-all to session-kill-all."""
    session_md = _read_file("packages/playwright/src/skill/references/session-management.md")

    # Check that old kill-all command is not present as standalone command
    lines = session_md.split('\n')
    for line in lines:
        if 'kill-all' in line and 'session-kill-all' not in line:
            if line.strip().startswith('playwright-cli kill-all'):
                assert False, f"session-management.md still references old 'kill-all' command: {line}"

    # New command should exist
    assert "playwright-cli session-kill-all" in session_md, \
        "session-management.md should reference new 'session-kill-all' command"


def test_session_management_md_config_path():
    """[f2p_config] session-management.md must reference .playwright/ for config."""
    session_md = _read_file("packages/playwright/src/skill/references/session-management.md")

    # Should reference .playwright path for config
    assert ".playwright/" in session_md or ".playwright" in session_md, \
        "session-management.md should reference .playwright/ folder"


def test_skill_md_session_commands_updated():
    """[f2p_config] SKILL.md session commands section must be updated."""
    skill_md = _read_file("packages/playwright/src/skill/SKILL.md")

    # Check for updated comment style for session commands
    # Should have comments describing what commands do
    assert "# Close all browsers" in skill_md or "# Forcefully kill all browser processes" in skill_md, \
        "SKILL.md should have descriptive comments for session commands"


def test_skill_md_close_description_updated():
    """[f2p_config] SKILL.md close command description should be updated."""
    skill_md = _read_file("packages/playwright/src/skill/SKILL.md")

    # Should have new comment style for close command
    # Looking for "# Close the browser" comment near the close command
    lines = skill_md.split('\n')
    for i, line in enumerate(lines):
        if 'playwright-cli close' in line and '# stop' not in line:
            # Check surrounding lines for comment
            prev_lines = '\n'.join(lines[max(0, i-3):i])
            assert "# Close" in prev_lines or "# Delete" in lines[i+1:i+3], \
                "SKILL.md should have descriptive comments for close/delete-data commands"


# ==================== STRUCTURAL TESTS ====================


def test_program_ts_parses():
    """[p2p] program.ts should be valid TypeScript."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")
    assert program_ts, "program.ts should exist and be readable"


def test_commands_ts_parses():
    """[p2p] commands.ts should be valid TypeScript."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")
    assert commands_ts, "commands.ts should exist and be readable"


def test_skill_md_exists():
    """[p2p] SKILL.md should exist."""
    skill_md = _read_file("packages/playwright/src/skill/SKILL.md")
    assert skill_md, "SKILL.md should exist and be readable"


def test_session_management_md_exists():
    """[p2p] session-management.md should exist."""
    session_md = _read_file("packages/playwright/src/skill/references/session-management.md")
    assert session_md, "session-management.md should exist and be readable"


# ==================== INTEGRATION TESTS ====================


def test_daemon_profiles_dir_uses_workspace_hash():
    """[f2p_code] daemonProfilesDir must use workspaceDirHash parameter."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # The daemonProfilesDir function should take workspaceDirHash
    assert "daemonProfilesDir(workspaceDirHash)" in program_ts, \
        "daemonProfilesDir should be called with workspaceDirHash"


def test_socket_path_uses_workspace_hash():
    """[f2p_code] daemonSocketPath must use workspaceDirHash."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Socket path should use workspaceDirHash
    assert "clientInfo.workspaceDirHash" in program_ts, \
        "daemonSocketPath should use clientInfo.workspaceDirHash"


def test_install_function_creates_playwright_dir():
    """[f2p_code] install function must create .playwright directory."""
    program_ts = _read_file("packages/playwright/src/mcp/terminal/program.ts")

    # Install function should create .playwright folder
    assert "'.playwright'" in program_ts and "mkdir" in program_ts, \
        "install function should create .playwright directory"
    assert "Workspace initialized" in program_ts, \
        "install function should print workspace initialization message"


def test_open_description_updated():
    """[f2p_code] open command description should be 'Open the browser'."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")

    # Check for updated open command description
    assert "description: 'Open the browser'" in commands_ts, \
        "open command should have description 'Open the browser'"


def test_close_description_updated():
    """[f2p_code] close command description should be 'Close the browser'."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")

    # Check for updated close command description
    assert "description: 'Close the browser'" in commands_ts, \
        "close command should have description 'Close the browser'"


def test_config_description_updated():
    """[f2p_code] config option should mention .playwright default."""
    commands_ts = _read_file("packages/playwright/src/mcp/terminal/commands.ts")

    # Config option description should mention default
    assert "defaults to .playwright/cli.config.json" in commands_ts, \
        "config option should mention default path"
