"""Tests for Playwright MCP Network Route Commands.

This file tests:
1. Code changes: route.ts, context.ts updates, commands.ts, etc.
2. Config updates: SKILL.md documentation updates
"""

import subprocess
import json
from pathlib import Path
import re

REPO = Path("/workspace/playwright")


def _run_ts_check() -> subprocess.CompletedProcess:
    """Run TypeScript type check."""
    return subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _run_lint() -> subprocess.CompletedProcess:
    """Run ESLint on modified files."""
    return subprocess.run(
        ["npm", "run", "flint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )


# =============================================================================
# Pass-to-Pass Tests (code should work on both base and gold)
# =============================================================================

def test_typescript_syntax_valid():
    """TypeScript files should parse without syntax errors."""
    files_to_check = [
        REPO / "packages/playwright/src/mcp/browser/context.ts",
        REPO / "packages/playwright/src/mcp/browser/tools.ts",
        REPO / "packages/playwright/src/mcp/terminal/command.ts",
        REPO / "packages/playwright/src/mcp/terminal/commands.ts",
        REPO / "packages/playwright/src/mcp/terminal/helpGenerator.ts",
    ]

    for file_path in files_to_check:
        assert file_path.exists(), f"File {file_path} should exist"
        content = file_path.read_text()
        # Basic TypeScript syntax checks
        assert "export" in content or "import" in content or "const" in content, f"{file_path} should have TypeScript content"


def test_terminal_command_category_exists():
    """The 'network' category should be defined in command.ts."""
    command_file = REPO / "packages/playwright/src/mcp/terminal/command.ts"
    content = command_file.read_text()

    # Check for network in Category type
    assert "'network'" in content or "network" in content, "Category type should include 'network'"


# =============================================================================
# Fail-to-Pass Tests (code - new features should exist)
# =============================================================================

def test_route_tools_file_exists():
    """The route.ts tool file should be created."""
    route_file = REPO / "packages/playwright/src/mcp/browser/tools/route.ts"
    assert route_file.exists(), "route.ts tool file should exist"

    content = route_file.read_text()
    assert "browser_route" in content, "route.ts should define browser_route tool"
    assert "browser_route_list" in content, "route.ts should define browser_route_list tool"
    assert "browser_unroute" in content, "route.ts should define browser_unroute tool"


def test_route_exported_from_tools():
    """route module should be exported from tools.ts."""
    tools_file = REPO / "packages/playwright/src/mcp/browser/tools.ts"
    content = tools_file.read_text()

    assert "import route from './tools/route'" in content or 'import route from "./tools/route"' in content, \
        "tools.ts should import route module"
    assert "...route" in content, "tools.ts should spread route tools in browserTools array"


def test_context_has_route_entry_type():
    """Context should have RouteEntry type and route management methods."""
    context_file = REPO / "packages/playwright/src/mcp/browser/context.ts"
    content = context_file.read_text()

    assert "RouteEntry" in content, "context.ts should define RouteEntry type"
    assert "routes()" in content or "routes():" in content, "context.ts should have routes() method"
    assert "addRoute" in content, "context.ts should have addRoute method"
    assert "removeRoute" in content, "context.ts should have removeRoute method"


def test_terminal_commands_defined():
    """Terminal commands for network should be defined."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    # Check for route command
    assert "name: 'route'" in content, "commands.ts should define route command"
    assert "browser_route" in content, "commands.ts should reference browser_route tool"

    # Check for route-list command
    assert "name: 'route-list'" in content or 'name: "route-list"' in content, \
        "commands.ts should define route-list command"

    # Check for unroute command
    assert "name: 'unroute'" in content, "commands.ts should define unroute command"

    # Check category is network
    assert "category: 'network'" in content, "commands should use 'network' category"


def test_network_category_in_help():
    """Network category should be in help generator."""
    help_file = REPO / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
    content = help_file.read_text()

    assert "{ name: 'network', title:" in content or "name: 'network'" in content, \
        "helpGenerator.ts should include network category"


def test_route_command_maps_arguments_correctly():
    """Route command should properly map CLI arguments to tool parameters."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    # Check that arguments are properly mapped
    assert "pattern" in content, "Route command should accept pattern argument"
    assert "status" in content, "Route command should accept status option"
    assert "body" in content, "Route command should accept body option"
    assert "content-type" in content or "contentType" in content, \
        "Route command should accept content-type option"
    assert "header" in content, "Route command should accept header option"
    assert "remove-header" in content or "removeHeaders" in content, \
        "Route command should accept remove-header option"


# =============================================================================
# Fail-to-Pass Tests (config - SKILL.md should be updated)
# =============================================================================

def test_skill_md_has_building_section():
    """SKILL.md should have '## Building' section with correct content."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"

    # If skill file doesn't exist, check alternative location
    if not skill_file.exists():
        skill_file = REPO / "packages/playwright/src/mcp/sdk/README.md"

    assert skill_file.exists(), "SKILL.md or README.md should exist"
    content = skill_file.read_text()

    assert "## Building" in content, "SKILL.md should have '## Building' section"
    assert "run lint" in content.lower() or "npm run flint" in content, \
        "Building section should mention running lint"


def test_skill_md_testing_updated():
    """SKILL.md Testing section should include 'Do not run test --debug'."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"

    # If skill file doesn't exist, check alternative location
    if not skill_file.exists():
        skill_file = REPO / "packages/playwright/src/mcp/sdk/README.md"

    assert skill_file.exists(), "SKILL.md or README.md should exist"
    content = skill_file.read_text()

    assert "Do not run test --debug" in content or "Do not run test --debug" in content, \
        "Testing section should warn against --debug flag"


def test_skill_md_lint_command_updated():
    """SKILL.md Lint section should use 'npm run flint' (not flint:mcp)."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"

    # If skill file doesn't exist, check alternative location
    if not skill_file.exists():
        skill_file = REPO / "packages/playwright/src/mcp/sdk/README.md"

    assert skill_file.exists(), "SKILL.md or README.md should exist"
    content = skill_file.read_text()

    # Check that it uses flint (not flint:mcp)
    assert "npm run flint" in content, "Lint command should be 'npm run flint'"

    # Make sure old command is not present
    assert "flint:mcp" not in content, "Should not use old 'flint:mcp' command"


def test_skill_md_has_both_mcp_and_cli_sections():
    """SKILL.md should have both MCP and CLI sections with Building subsections."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"

    # If skill file doesn't exist, check alternative location
    if not skill_file.exists():
        skill_file = REPO / "packages/playwright/src/mcp/sdk/README.md"

    assert skill_file.exists(), "SKILL.md or README.md should exist"
    content = skill_file.read_text()

    # Check for MCP and CLI sections
    assert "# MCP" in content, "Should have MCP section"
    assert "# CLI" in content, "Should have CLI section"

    # Count Building sections - should be at least 2 (one for MCP, one for CLI)
    building_count = content.count("## Building")
    assert building_count >= 2, f"Should have Building sections for both MCP and CLI (found {building_count})"


# =============================================================================
# Build/Type Tests
# =============================================================================

def test_build_succeeds():
    """npm run build should succeed."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # Allow warnings but not errors
    assert result.returncode == 0, f"Build failed: {result.stderr[:500]}"


def test_lint_succeeds():
    """npm run flint should pass for modified files."""
    result = subprocess.run(
        ["npm", "run", "flint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Lint may have warnings but should not fail
    assert result.returncode == 0, f"Lint failed: {result.stdout[-500:]}"
