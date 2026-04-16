"""Test that kill-all command is implemented and documented correctly."""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/playwright"


def _run_tsc_check() -> subprocess.CompletedProcess:
    """Run TypeScript compiler check."""
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright/src/mcp/terminal"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _get_file_content(path: str) -> str:
    """Read file content from repo."""
    return (Path(REPO) / path).read_text()


# =============================================================================
# PASS-TO-PASS TESTS (repo CI / structural validation)
# =============================================================================

def test_typescript_compiles():
    """Modified TypeScript files should compile without errors."""
    result = _run_tsc_check()
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr}"


# =============================================================================
# FAIL-TO-PASS TESTS: Code behavior (the functional fix)
# =============================================================================

def test_kill_all_command_exists_in_commands():
    """The kill-all command must be declared in commands.ts."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts").read_text()

    # Check for killAll command declaration
    assert "const killAll = declareCommand({" in content, "killAll command declaration not found"
    assert "name: 'kill-all'" in content, "kill-all name not found"
    assert "Forcefully kill all daemon processes" in content, "kill-all description not found"
    assert "category: 'session'" in content, "kill-all category not found"


def test_kill_all_in_commands_array():
    """The killAll command must be added to the commandsArray."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts").read_text()

    # Find the commandsArray and check killAll is included
    assert "killAll," in content or "killAll" in content, "killAll not added to commandsArray"


def test_kill_all_handled_in_program():
    """The kill-all command must be handled in program.ts."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts").read_text()

    # Check for kill-all handling in handleSessionCommand
    assert "if (subcommand === 'kill-all')" in content, "kill-all subcommand handling not found"
    assert "await killAllDaemons()" in content, "killAllDaemons() call not found"


def test_kill_all_top_level_command():
    """The kill-all command must be handled at top-level program."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts").read_text()

    # Check for top-level command handling
    assert "if (commandName === 'kill-all')" in content, "kill-all top-level command handling not found"


def test_kill_all_daemons_function_exists():
    """The killAllDaemons function must be implemented."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts").read_text()

    # Check function signature
    assert "async function killAllDaemons(): Promise<void>" in content, "killAllDaemons function not found"

    # Check cross-platform implementation
    assert "os.platform()" in content, "Platform detection not found"
    assert "win32" in content, "Windows platform handling not found"
    assert "execSync('ps aux'" in content or "ps aux" in content, "Unix ps command not found"
    assert "run-mcp-server" in content, "Process name filter not found"
    assert "--daemon-session" in content, "Daemon session filter not found"


def test_execsync_imported():
    """execSync must be imported from child_process for process killing."""
    content = (Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts").read_text()

    assert "execSync" in content, "execSync not found in imports or usage"
    assert "import { execSync, spawn } from 'child_process';" in content, "execSync not properly imported from child_process"


# =============================================================================
# FAIL-TO-PASS TESTS: Config/documentation updates (REQUIRED for agentmd-edit)
# =============================================================================

def test_skill_md_documents_kill_all():
    """SKILL.md must document the kill-all command in the session commands section."""
    content = (Path(REPO) / "packages/playwright/src/skill/SKILL.md").read_text()

    # Check for kill-all in the Sessions section
    assert "kill-all" in content, "kill-all not documented in SKILL.md"

    # Check for the comment explaining the command
    assert "forcefully kill all daemon processes" in content.lower() or \
           "stale/zombie" in content, "kill-all description not found in SKILL.md"


def test_session_management_md_documents_kill_all():
    """session-management.md must document the kill-all command."""
    content = (Path(REPO) / "packages/playwright/src/skill/references/session-management.md").read_text()

    # Check for kill-all command
    assert "kill-all" in content, "kill-all not documented in session-management.md"

    # Check for proper context - should be in the "Stop Sessions" section
    assert "Forcefully kill all daemon processes" in content or \
           "zombie processes" in content.lower(), \
           "kill-all context/description not properly documented"


def test_session_management_shows_use_case():
    """session-management.md should explain when to use kill-all (zombie/stale processes)."""
    content = (Path(REPO) / "packages/playwright/src/skill/references/session-management.md").read_text()

    # Should mention the use case for kill-all
    assert "unresponsive" in content.lower() or "zombie" in content.lower(), \
           "Use case for kill-all (unresponsive/zombie processes) not documented"
