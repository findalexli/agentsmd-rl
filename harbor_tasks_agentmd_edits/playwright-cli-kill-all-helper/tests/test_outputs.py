"""Tests for kill-all command implementation and documentation."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")
COMMANDS_TS = REPO / "packages" / "playwright" / "src" / "mcp" / "terminal" / "commands.ts"
PROGRAM_TS = REPO / "packages" / "playwright" / "src" / "mcp" / "terminal" / "program.ts"
SKILL_MD = REPO / "packages" / "playwright" / "src" / "skill" / "SKILL.md"
SESSION_MD = REPO / "packages" / "playwright" / "src" / "skill" / "references" / "session-management.md"


def _parse_ts_file(file_path: Path) -> str:
    """Read TypeScript file content."""
    if not file_path.exists():
        return ""
    return file_path.read_text()


def test_kill_all_command_registered():
    """Verify kill-all command is registered in commands.ts with correct metadata."""
    content = _parse_ts_file(COMMANDS_TS)

    # Check killAll declaration exists
    assert "const killAll = declareCommand({" in content, \
        "killAll command declaration not found in commands.ts"

    # Check command name is 'kill-all'
    assert "name: 'kill-all'" in content, \
        "kill-all command name not found"

    # Check description mentions daemon processes
    assert "description: 'Forcefully kill all daemon processes" in content, \
        "kill-all command description not found or incorrect"

    # Check category is 'session'
    assert "category: 'session'" in content, \
        "kill-all command should be in 'session' category"

    # Check killAll is added to commandsArray
    assert "killAll," in content and "commandsArray" in content, \
        "killAll not added to commandsArray"


def test_kill_all_handler_implemented():
    """Verify kill-all handler is implemented in program.ts."""
    content = _parse_ts_file(PROGRAM_TS)

    # Check killAllDaemons function exists
    assert "async function killAllDaemons(): Promise<void>" in content, \
        "killAllDaemons function not found in program.ts"

    # Check execSync is imported
    assert "execSync" in content, \
        "execSync should be imported from child_process"

    # Check handler routes for 'kill-all' subcommand
    assert "if (subcommand === 'kill-all')" in content, \
        "kill-all subcommand handler not found in handleSessionCommand"

    # Check top-level command handler
    assert "if (commandName === 'kill-all')" in content, \
        "kill-all command handler not found in program function"

    # Check platform-specific implementations
    assert "os.platform()" in content, \
        "Platform detection not found"
    assert "run-mcp-server" in content, \
        "Process identification for 'run-mcp-server' not found"
    assert "--daemon-session" in content, \
        "Process identification for '--daemon-session' not found"


def test_skill_md_documents_kill_all():
    """Verify SKILL.md documents the kill-all command."""
    content = SKILL_MD.read_text()

    # Check kill-all is documented in the Sessions section
    assert "playwright-cli kill-all" in content, \
        "kill-all command not documented in SKILL.md"

    # Check it mentions the purpose (daemon/zombie processes)
    assert "daemon" in content.lower() or "zombie" in content.lower() or "stale" in content.lower(), \
        "SKILL.md should mention daemon, zombie, or stale processes for kill-all"


def test_session_management_md_documents_kill_all():
    """Verify session-management.md documents kill-all in appropriate sections."""
    content = SESSION_MD.read_text()

    # Check kill-all appears in the document
    assert "playwright-cli kill-all" in content, \
        "kill-all command not documented in session-management.md"

    # Check it appears in the Session Commands section
    session_commands_section = content.split("## Session Commands")[1] if "## Session Commands" in content else content
    assert "kill-all" in session_commands_section, \
        "kill-all should be documented in Session Commands section"

    # Check it appears in a Common Patterns / troubleshooting section
    # The PR adds it to "2. Always Clean Up" section
    assert "unresponsive" in content.lower() or "zombie" in content.lower(), \
        "session-management.md should mention when to use kill-all (unresponsive/zombie processes)"


def test_skill_md_follows_existing_format():
    """Verify kill-all documentation follows the format of other session commands."""
    content = SKILL_MD.read_text()

    # Find the Sessions code block and verify kill-all is in the right place
    lines = content.split('\n')
    session_lines = []
    in_session_block = False

    for line in lines:
        if 'playwright-cli session-list' in line or 'playwright-cli session-stop' in line:
            in_session_block = True
        if in_session_block:
            session_lines.append(line)
            if line.strip() == '```':
                break

    kill_all_line = None
    for i, line in enumerate(session_lines):
        if 'kill-all' in line:
            kill_all_line = i
            break

    # kill-all should be documented in the sessions code block
    assert kill_all_line is not None, \
        "kill-all should be in the Sessions code block in SKILL.md"

    # Check format includes comment explanation
    kill_all_full_line = session_lines[kill_all_line] if kill_all_line is not None else ""
    assert "#" in kill_all_full_line or "forcefully" in kill_all_full_line.lower(), \
        "kill-all documentation should include a comment explaining its purpose"


def test_commands_file_compiles():
    """Verify commands.ts has valid TypeScript syntax by checking for syntax errors."""
    content = _parse_ts_file(COMMANDS_TS)

    # Basic syntax checks
    open_braces = content.count('{')
    close_braces = content.count('}')
    open_parens = content.count('(')
    close_parens = content.count(')')

    assert open_braces == close_braces, \
        f"Mismatched braces in commands.ts: {open_braces} open, {close_braces} close"
    assert open_parens == close_parens, \
        f"Mismatched parentheses in commands.ts: {open_parens} open, {close_parens} close"

    # Check that killAll is properly comma-separated in the array
    assert "killAll,\n" in content or "killAll,\r\n" in content or "killAll," in content, \
        "killAll should be followed by comma in commandsArray"
