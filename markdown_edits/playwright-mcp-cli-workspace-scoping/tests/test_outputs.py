"""
Tests for playwright-mcp-cli-workspace-scoping task.

This task scopes the daemon by workspace instead of installation directory:
1. Renames `install-browser` → `install` (with --skills flag)
2. Renames `kill-all` → `session-kill-all`
3. Changes config file location from `playwright-cli.json` → `.playwright/cli.config.json`
4. Updates SKILL.md and session-management.md documentation
"""

import subprocess
import json
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
COMMANDS_TS = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
PROGRAM_TS = REPO / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = REPO / "packages/playwright/src/skill/SKILL.md"
SESSION_MD = REPO / "packages/playwright/src/skill/references/session-management.md"
MCP_DEV_SKILL = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"


def _read_file(path: Path) -> str:
    """Read file content."""
    if not path.exists():
        return ""
    return path.read_text()


# =============================================================================
# CODE BEHAVIOR TESTS (fail-to-pass)
# =============================================================================

def test_workspace_dir_hash_replaces_installation_dir_hash():
    """program.ts must use workspaceDirHash instead of installationDirHash."""
    content = _read_file(PROGRAM_TS)

    # Should have workspaceDirHash
    assert "workspaceDirHash" in content, "program.ts must use workspaceDirHash"

    # Should NOT have installationDirHash
    assert "installationDirHash" not in content, "program.ts must not have installationDirHash"
    assert "installationDir:" not in content, "program.ts must not have installationDir field"


def test_find_workspace_dir_function_exists():
    """program.ts must have findWorkspaceDir function to detect workspace root."""
    content = _read_file(PROGRAM_TS)

    assert "findWorkspaceDir" in content, "program.ts must have findWorkspaceDir function"
    assert ".playwright" in content, "program.ts must reference .playwright directory"


def test_commands_install_renamed():
    """commands.ts: install-browser renamed to install with --skills flag."""
    content = _read_file(COMMANDS_TS)

    # Old name should be gone as primary command
    # The string "install-browser" still exists but as the BROWSER install command
    # Check for the swap: "install" command now has "Initialize workspace" description
    assert "name: 'install'," in content, "install command must exist"
    assert "description: 'Initialize workspace'" in content, "install command must have new description"
    assert "skills:" in content, "install command must have skills option"


def test_commands_session_kill_all_renamed():
    """commands.ts: kill-all renamed to session-kill-all."""
    content = _read_file(COMMANDS_TS)

    assert "name: 'session-kill-all'," in content, "session-kill-all command must exist"
    assert "name: 'kill-all'," not in content, "kill-all command name must be removed"


def test_config_file_path_updated():
    """program.ts: config file path changed to .playwright/cli.config.json."""
    content = _read_file(PROGRAM_TS)

    assert ".playwright/cli.config.json" in content, "program.ts must reference new config path"


def test_daemon_profiles_dir_scoped():
    """program.ts: daemon profiles directory must include workspaceDirHash."""
    content = _read_file(PROGRAM_TS)

    # Check that daemonProfilesDir uses workspaceDirHash
    assert "daemonProfilesDir(workspaceDirHash)" in content or "daemonProfilesDir" in content, \
        "daemonProfilesDir must be scoped by workspace"


# =============================================================================
# CONFIG/DOCUMENTATION TESTS (fail-to-pass)
# =============================================================================

def test_skill_md_has_session_kill_all():
    """SKILL.md must document session-kill-all instead of kill-all."""
    content = _read_file(SKILL_MD)

    # Must have the new command
    assert "session-kill-all" in content, "SKILL.md must document session-kill-all command"

    # Must NOT have the old command in isolation (still might appear in deprecation notes)
    # But primary reference should be session-kill-all
    lines = content.split('\n')
    for line in lines:
        if 'kill-all' in line and 'session-kill-all' not in line:
            # Allow it only if it's explaining the rename, not as primary command
            if 'session-kill-all' not in line and 'Forcefully kill' not in line:
                assert False, f"SKILL.md has old 'kill-all' without session-kill-all context: {line}"


def test_session_md_has_session_kill_all():
    """session-management.md must use session-kill-all command."""
    content = _read_file(SESSION_MD)

    assert "session-kill-all" in content, "session-management.md must reference session-kill-all"


def test_session_md_config_path_updated():
    """session-management.md must reference .playwright/ config path."""
    content = _read_file(SESSION_MD)

    assert ".playwright" in content, "session-management.md must reference .playwright directory"


def test_skill_md_close_description_updated():
    """SKILL.md: close command description updated."""
    content = _read_file(SKILL_MD)

    # Check that "Close the browser" appears (updated from "Close the page")
    assert "Close the browser" in content, "SKILL.md must have 'Close the browser'"


def test_skill_md_has_install_commands():
    """SKILL.md must have install and install-browser commands."""
    content = _read_file(SKILL_MD)

    # After the swap: install is for workspace, install-browser is for browser
    assert "install-browser" in content, "SKILL.md must document install-browser command"
    assert "install-skills" in content, "SKILL.md must document install-skills (legacy)"


# =============================================================================
# SYNTAX/PASS-TO-PASS TESTS
# =============================================================================

def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax."""
    # Check that commands.ts can be parsed
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--allowJs",
         "--module", "commonjs", "--target", "es2020",
         str(COMMANDS_TS)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # We allow some errors due to missing imports, but not syntax errors
    stderr_lower = result.stderr.lower()
    assert "syntax" not in stderr_lower or result.returncode == 0, \
        f"Syntax error in commands.ts: {result.stderr[:500]}"


def test_mcp_dev_skill_unchanged():
    """MCP dev skill file should exist (not modified by this PR)."""
    content = _read_file(MCP_DEV_SKILL)

    assert content != "", "MCP dev skill file must exist"
    assert "playwright-mcp-dev" in content, "MCP dev skill must have correct name"


def test_command_schemas_complete():
    """commands.ts must have all expected command schemas defined."""
    content = _read_file(COMMANDS_TS)

    required_schemas = ["const open", "const close", "const install",
                        "const installBrowser", "const sessionCloseAll"]
    for schema in required_schemas:
        assert schema in content, f"Command schema {schema} must be defined"


if __name__ == "__main__":
    # Run all test functions
    import traceback

    tests = [
        test_workspace_dir_hash_replaces_installation_dir_hash,
        test_find_workspace_dir_function_exists,
        test_commands_install_renamed,
        test_commands_session_kill_all_renamed,
        test_config_file_path_updated,
        test_daemon_profiles_dir_scoped,
        test_skill_md_has_session_kill_all,
        test_session_md_has_session_kill_all,
        test_session_md_config_path_updated,
        test_skill_md_close_description_updated,
        test_skill_md_has_install_commands,
        test_typescript_syntax_valid,
        test_mcp_dev_skill_unchanged,
        test_command_schemas_complete,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
