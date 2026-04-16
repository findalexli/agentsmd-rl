#!/usr/bin/env python3
"""
Test suite for playwright-cli config command addition.

Tests both:
1. Code behavior: config command exists and works correctly
2. Config update: SKILL.md documents the new config command
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/playwright")


def run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    script_path = REPO / "_eval_tmp.js"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO)
        )
    finally:
        script_path.unlink(missing_ok=True)


def test_config_command_exists_in_commands():
    """The config command must be declared in commands.ts"""
    commands_path = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_path.read_text()

    # Check for config command declaration
    assert "const config = declareCommand({" in content, "config command not declared"
    assert "name: 'config'," in content, "config command name not found"
    assert "category: 'config'," in content, "config category not set"


def test_config_category_in_types():
    """Category type must include 'config'"""
    command_path = REPO / "packages/playwright/src/mcp/terminal/command.ts"
    content = command_path.read_text()

    # Check Category type includes 'config'
    assert "'config'" in content, "config category not in Category type"


def test_config_in_help_generator():
    """Help generator must include config category"""
    help_path = REPO / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
    content = help_path.read_text()

    # Check for config category in categories list
    assert "{ name: 'config', title: 'Configuration' }" in content, \
        "config category not in helpGenerator categories"


def test_session_list_returns_map():
    """Session list must return Map<string, boolean> instead of array"""
    program_path = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_path.read_text()

    # Check that list() returns Map
    assert "Promise<Map<string, boolean>>" in content, \
        "Session list return type should be Map<string, boolean>"
    assert "new Map<string, boolean>()" in content, \
        "Session list should create Map instance"
    assert "sessions.set(sessionName, live)" in content, \
        "Session list should use Map.set()"
    assert "for (const [sessionName, live] of sessions.entries())" in content, \
        "Should iterate Map with .entries()"
    assert "sessions.size === 0" in content, \
        "Should check Map.size instead of array.length"


def test_config_method_exists():
    """SessionManager must have configure() method"""
    program_path = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_path.read_text()

    # Check for configure method
    assert "async configure(args: any): Promise<void>" in content, \
        "configure() method not found"
    assert "await sessionManager.configure(args)" in content, \
        "configure() not called in command handler"


def test_config_uses_relative_path():
    """Config file path should be displayed as relative path"""
    program_path = REPO / "packages/playwright/src/mcp/terminal/program.ts"
    content = program_path.read_text()

    # Check that path.relative is used for config file display
    assert "path.relative(process.cwd(), configFile)" in content, \
        "Config file path should use path.relative()"


def test_daemon_config_has_viewport():
    """Default daemon config must include viewport contextOptions"""
    config_path = REPO / "packages/playwright/src/mcp/browser/config.ts"
    content = config_path.read_text()

    # Check for viewport configuration in daemon config
    assert "contextOptions:" in content, "contextOptions not in daemon config"
    assert "viewport:" in content, "viewport not in contextOptions"
    assert "cliOptions.daemonHeaded" in content, \
        "viewport should respect daemonHeaded option"


def test_skill_md_documents_config_command():
    """SKILL.md must document the new config command"""
    skill_path = REPO / "packages/playwright/src/mcp/terminal/SKILL.md"
    content = skill_path.read_text()

    # Check for Configuration section
    assert "### Configuration" in content, \
        "SKILL.md missing Configuration section header"

    # Check for specific config command examples
    assert "playwright-cli config" in content, \
        "SKILL.md missing 'playwright-cli config' example"
    assert "playwright-cli --session=mysession config" in content, \
        "SKILL.md missing session-specific config example"
    assert "playwright-cli open --config=my-config.json" in content, \
        "SKILL.md missing --config option example"


def test_skill_md_has_config_examples():
    """SKILL.md Configuration section must have bash code block examples"""
    skill_path = REPO / "packages/playwright/src/mcp/terminal/SKILL.md"
    content = skill_path.read_text()

    # Find Configuration section
    lines = content.split("\n")
    config_section_idx = None
    for i, line in enumerate(lines):
        if "### Configuration" in line:
            config_section_idx = i
            break

    assert config_section_idx is not None, "Configuration section not found"

    # Check that there's a bash code block after Configuration section
    # Look for ```bash within the next 20 lines
    section_lines = lines[config_section_idx:config_section_idx + 20]
    section_text = "\n".join(section_lines)

    assert "```bash" in section_text, \
        "Configuration section must have bash code block examples"


def test_typescript_compiles():
    """TypeScript must compile without errors"""
    result = subprocess.run(
        ["npm", "run", "tsc"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=180
    )

    # TSC may return warnings but should not have type errors in the modified files
    # Filter for errors in mcp/terminal files
    if result.returncode != 0:
        error_output = result.stderr + result.stdout
        mcp_errors = [line for line in error_output.split("\n")
                      if "mcp/terminal" in line or "mcp/browser" in line]
        assert len(mcp_errors) == 0, f"TypeScript errors in MCP files: {mcp_errors}"


def test_cli_help_shows_config_category():
    """CLI help must show Configuration category"""
    result = subprocess.run(
        ["node", "packages/playwright/lib/mcp/terminal/cli.js", "--help"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30
    )

    output = result.stdout + result.stderr

    # Should show Configuration category
    assert "Configuration" in output, \
        "CLI help should show 'Configuration' category"
