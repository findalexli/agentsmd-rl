"""
Test suite for playwright-cli workspace scoping changes.

This PR changes the daemon from being scoped by installation directory
to being scoped by workspace directory (detected via .playwright folder).
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
PROGRAM_TS = REPO / "packages/playwright/src/mcp/terminal/program.ts"
COMMANDS_TS = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
SKILL_MD = REPO / "packages/playwright/src/skill/SKILL.md"
SESSION_MD = REPO / "packages/playwright/src/skill/references/session-management.md"


def _run_npx_tsc_check() -> subprocess.CompletedProcess:
    """Run TypeScript compiler check on the modified files."""
    pkg_dir = REPO / "packages/playwright"
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "src/mcp/terminal/program.ts", "src/mcp/terminal/commands.ts"],
        cwd=pkg_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax."""
    result = _run_npx_tsc_check()
    # We allow some lib check errors but not syntax errors
    if "error TS" in result.stdout or "error TS" in result.stderr:
        # Filter out only syntax/parse errors, ignore type/lib errors
        syntax_errors = [
            line for line in (result.stdout + result.stderr).split("\n")
            if "error TS" in line and any(x in line for x in ["TS1005", "TS1109", "TS1110", "TS1126", "TS1161", "TS17002"])
        ]
        assert not syntax_errors, f"Syntax errors found:\n{chr(10).join(syntax_errors)}"


def test_workspace_dir_hash_used():
    """program.ts must use workspaceDirHash instead of installationDirHash."""
    content = PROGRAM_TS.read_text()
    assert "workspaceDirHash" in content, "program.ts should use workspaceDirHash"
    assert "installationDirHash" not in content, "program.ts should not use installationDirHash (replaced by workspaceDirHash)"


def test_find_workspace_dir_function_exists():
    """program.ts must have findWorkspaceDir function."""
    content = PROGRAM_TS.read_text()
    assert "function findWorkspaceDir" in content, "findWorkspaceDir function must exist"
    assert '.playwright' in content, "findWorkspaceDir should look for .playwright folder"


def test_installation_dir_removed_from_client_info():
    """ClientInfo type must not have installationDir field."""
    content = PROGRAM_TS.read_text()
    # Check type definition
    client_info_section = content[content.find("type ClientInfo"):content.find("type ClientInfo") + 500]
    assert "workspaceDirHash" in client_info_section, "ClientInfo should have workspaceDirHash"
    assert "installationDir" not in client_info_section, "ClientInfo should not have installationDir"
    assert "installationDirHash" not in client_info_section, "ClientInfo should not have installationDirHash"


def test_config_file_path_updated():
    """Default config file path must be .playwright/cli.config.json."""
    content = PROGRAM_TS.read_text()
    assert ".playwright/cli.config.json" in content, "Default config path should be .playwright/cli.config.json"
    # Should not reference old path in the config resolution logic
    old_pattern_check = "playwright-cli.json"
    lines = content.split("\n")
    config_lines = [l for l in lines if "config" in l.lower() and ".json" in l]
    assert any(".playwright" in l for l in config_lines), f"Config resolution should use .playwright folder: {config_lines}"


def test_session_kill_all_command():
    """commands.ts must have session-kill-all instead of kill-all."""
    content = COMMANDS_TS.read_text()
    assert "name: 'session-kill-all'" in content, "Command should be renamed to 'session-kill-all'"
    # Check it's used in the program switch statement too
    program_content = PROGRAM_TS.read_text()
    assert "case 'session-kill-all':" in program_content, "program.ts switch case should use 'session-kill-all'"


def test_install_command_restructured():
    """commands.ts must have restructured install commands."""
    content = COMMANDS_TS.read_text()
    # New structure: 'install' is for workspace init, 'install-browser' is separate
    assert "name: 'install'," in content, "Should have 'install' command"
    assert "name: 'install-browser'," in content, "Should have 'install-browser' command"
    # The 'install' command should have 'skills' option
    install_section = content[content.find("const install = declareCommand"):content.find("const installBrowser = declareCommand")]
    assert "skills" in install_section, "install command should have 'skills' option"
    # install-skills should be removed
    assert "install-skills" not in content, "install-skills command should be removed"


def test_open_description_updated():
    """commands.ts open command description must be updated."""
    content = COMMANDS_TS.read_text()
    # Find the open command description
    open_section = content[content.find("const open = declareCommand"):content.find("const close = declareCommand")]
    assert "description: 'Open the browser'" in open_section, "Open command description should be 'Open the browser'"
    # Config option description updated
    assert "defaults to .playwright/cli.config.json" in open_section, "Config option should mention default path"


def test_close_description_updated():
    """commands.ts close command description must be updated."""
    content = COMMANDS_TS.read_text()
    close_section = content[content.find("const close = declareCommand"):content[content.find("const close = declareCommand") + 300]
    assert "description: 'Close the browser'" in close_section, "Close command description should be 'Close the browser'"


def test_skill_md_documents_session_kill_all():
    """SKILL.md must document session-kill-all instead of kill-all."""
    content = SKILL_MD.read_text()
    # Check that session-kill-all is documented in the Sessions section
    session_section = content[content.find("### Sessions"):content.find("## Example")]
    assert "session-kill-all" in session_section, "SKILL.md Sessions section should document session-kill-all"
    assert "kill-all" not in session_section, "SKILL.md should not have old 'kill-all' command"


def test_skill_md_documents_close_and_delete_data():
    """SKILL.md Configuration section must document close and delete-data."""
    content = SKILL_MD.read_text()
    config_section = content[content.find("### Configuration"):content.find("### Sessions")]
    assert "# Close the browser" in content, "SKILL.md should document close command with description"
    assert "# Delete user data" in content, "SKILL.md should document delete-data command"


def test_session_management_md_updated():
    """session-management.md must reference session-kill-all and .playwright path."""
    content = SESSION_MD.read_text()
    assert "session-kill-all" in content, "session-management.md should use session-kill-all"
    assert "kill-all" not in content, "session-management.md should not have old kill-all command"
    # Config file path updated
    assert ".playwright" in content, "session-management.md should reference .playwright folder for config"


def test_daemon_profiles_dir_scoped():
    """daemonProfilesDir must include workspace hash subdirectory."""
    content = PROGRAM_TS.read_text()
    # When PLAYWRIGHT_DAEMON_SESSION_DIR is set, path should include workspace hash
    assert "path.join(process.env.PLAYWRIGHT_DAEMON_SESSION_DIR, workspaceDirHash)" in content, \
        "daemonProfilesDir should include workspace hash in custom dir path"


def test_socket_path_uses_workspace_hash():
    """Socket path must use workspaceDirHash instead of installationDirHash."""
    content = PROGRAM_TS.read_text()
    daemon_socket_fn = content[content.find("function daemonSocketPath"):content.find("function sessionConfigFromArgs")]
    assert "workspaceDirHash" in daemon_socket_fn, "daemonSocketPath must use workspaceDirHash"
    assert "installationDirHash" not in daemon_socket_fn, "daemonSocketPath should not use installationDirHash"


def test_install_function_handles_skills_flag():
    """install function must conditionally install skills based on flag."""
    content = PROGRAM_TS.read_text()
    install_fn = content[content.find("async function install("):content.find("function daemonSocketPath")]
    assert "if (args.skills)" in install_fn, "install function should check args.skills flag"
    assert ".playwright" in install_fn, "install function should create .playwright folder"
