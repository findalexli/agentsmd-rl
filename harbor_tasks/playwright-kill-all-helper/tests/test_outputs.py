"""
Tests for playwright kill-all CLI command task.

This task tests both:
1. Code changes: Adding kill-all command implementation
2. Config changes: Updating SKILL.md and session-management.md documentation
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")


def _run_typescript_check() -> subprocess.CompletedProcess:
    """Run TypeScript compiler to check for syntax errors."""
    return subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright/src/mcp/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_typescript_compiles():
    """TypeScript files must compile without errors."""
    result = _run_typescript_check()
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_kill_all_command_declared():
    """killAll command must be declared in commands.ts with correct properties."""
    commands_path = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_path.read_text()

    # Check killAll is declared
    assert "const killAll = declareCommand" in content, "killAll command not declared"

    # Check properties
    assert "name: 'kill-all'" in content, "kill-all name not found"
    assert "Forcefully kill all daemon processes" in content, "kill-all description not found"
    assert "category: 'session'" in content, "kill-all category not set to 'session'"


def test_kill_all_in_commands_array():
    """killAll must be included in the commandsArray."""
    commands_path = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_path.read_text()

    # Find the commandsArray section
    array_match = content.find("const commandsArray: AnyCommandSchema[] = [")
    assert array_match != -1, "commandsArray not found"

    array_section = content[array_match:array_match + 2000]
    assert "killAll," in array_section or "  killAll" in array_section, "killAll not in commandsArray"


def test_kill_all_implemented_in_program():
    """killAllDaemons function must be implemented in program.ts."""
    program_path = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_path.read_text()

    # Check function exists
    assert "async function killAllDaemons" in content or "function killAllDaemons" in content, \
        "killAllDaemons function not found"

    # Check it handles the subcommand
    assert "subcommand === 'kill-all'" in content or "'kill-all'" in content, \
        "kill-all subcommand handling not found"

    # Check execSync is imported (used for killing processes)
    assert "execSync" in content, "execSync not imported for process management"

    # Check platform-specific handling (win32 vs others)
    assert "platform === 'win32'" in content or "os.platform()" in content, \
        "Platform-specific handling not found"

    # Check daemon process detection patterns
    assert "run-mcp-server" in content, "run-mcp-server pattern not found for process detection"
    assert "daemon-session" in content or "--daemon-session" in content, \
        "daemon-session pattern not found for process detection"


def test_skill_md_documents_kill_all():
    """SKILL.md must document the kill-all command in the Sessions section."""
    skill_path = REPO / "packages/playwright/src/skill/SKILL.md"
    content = skill_path.read_text()

    # Check kill-all is documented in the sessions section
    session_section = content.find("### Sessions")
    assert session_section != -1, "Sessions section not found in SKILL.md"

    session_content = content[session_section:session_section + 1500]
    assert "kill-all" in session_content, "kill-all not documented in Sessions section"

    # Check it mentions daemon processes
    assert "daemon" in content.lower() or "zombie" in content.lower() or "stale" in content.lower(), \
        "kill-all documentation should mention daemon/zombie/stale processes"


def test_session_management_md_documents_kill_all():
    """session-management.md reference must document kill-all usage."""
    ref_path = REPO / "packages/playwright/src/skill/references/session-management.md"
    content = ref_path.read_text()

    # Check kill-all is documented
    assert "kill-all" in content, "kill-all not documented in session-management.md"

    # Check it appears in session commands section
    assert "playwright-cli kill-all" in content, "kill-all command example not found"

    # Check it mentions the use case (zombie/stale processes)
    assert any(phrase in content.lower() for phrase in ["zombie", "stale", "unresponsive", "forcefully"]), \
        "kill-all documentation should explain when to use it (zombie/stale/unresponsive processes)"


def test_skill_md_follows_existing_format():
    """SKILL.md kill-all entry must follow the same format as other session commands."""
    skill_path = REPO / "packages/playwright/src/skill/SKILL.md"
    content = skill_path.read_text()

    # Find the Sessions code block
    lines = content.split('\n')
    in_sessions_block = False
    session_commands = []

    for line in lines:
        if 'playwright-cli session-list' in line or 'playwright-cli session-stop' in line:
            in_sessions_block = True
        if in_sessions_block:
            if line.strip().startswith('playwright-cli'):
                session_commands.append(line.strip())
            if line.strip() == '```':
                break

    # Check kill-all follows the same pattern (playwright-cli kill-all ...)
    kill_all_lines = [cmd for cmd in session_commands if 'kill-all' in cmd]
    assert len(kill_all_lines) > 0, "kill-all not found in session commands block"

    # Check format matches other commands
    for cmd in kill_all_lines:
        assert cmd.startswith('playwright-cli kill-all'), \
            f"kill-all command format incorrect: {cmd}"


def test_session_management_includes_use_case():
    """session-management.md must include specific use case for kill-all."""
    ref_path = REPO / "packages/playwright/src/skill/references/session-management.md"
    content = ref_path.read_text()

    # Look for common patterns section that shows when to use kill-all
    lines = content.split('\n')

    # Find line with kill-all and check context
    for i, line in enumerate(lines):
        if 'kill-all' in line and 'playwright-cli' in line:
            # Check surrounding context (previous 3 lines should explain the use case)
            context_start = max(0, i - 3)
            context = '\n'.join(lines[context_start:i])

            # Should have some explanatory text before the command
            has_context = any(phrase in context.lower() for phrase in [
                'if', 'when', 'zombie', 'stale', 'unresponsive', 'remain', 'force'
            ])
            assert has_context, "kill-all should have explanatory context about when to use it"
            break
    else:
        assert False, "kill-all command not found in session-management.md"
