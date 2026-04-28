"""Tests for Playwright MCP Network Route Commands.

This file tests:
1. Code changes: route.ts, context.ts updates, commands.ts, etc.
2. Config updates: SKILL.md documentation updates
"""

import subprocess
import os
from pathlib import Path

REPO = Path("/workspace/playwright")


# =============================================================================
# Pass-to-Pass Tests (code should work on both base and gold)
# =============================================================================

def test_typescript_compiles():
    """TypeScript compilation should succeed without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"stdout: {result.stdout[-1500:]}\nstderr: {result.stderr[-1500:]}"
    )


def test_build_succeeds():
    """npm run build should succeed."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Build failed: {result.stderr[-500:]}"


def test_eslint_passes():
    """ESLint should pass on MCP source files present on both commits."""
    mcp_files = [
        "packages/playwright/src/mcp/browser/context.ts",
        "packages/playwright/src/mcp/browser/tools.ts",
        "packages/playwright/src/mcp/terminal/command.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/helpGenerator.ts",
    ]
    result = subprocess.run(
        ["npx", "eslint", "--no-cache"] + mcp_files,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed: {result.stdout[-1000:]}"


# =============================================================================
# Fail-to-Pass Tests (new features should exist after fix)
# =============================================================================

def test_terminal_command_category_exists():
    """The 'network' category should be defined in command.ts Category type."""
    command_file = REPO / "packages/playwright/src/mcp/terminal/command.ts"
    content = command_file.read_text()

    assert "'network'" in content, (
        "Category type should include 'network' literal"
    )


def test_route_tools_file_exists():
    """The route.ts tool file should be created."""
    route_file = REPO / "packages/playwright/src/mcp/browser/tools/route.ts"
    assert route_file.exists(), "route.ts tool file should exist"

    content = route_file.read_text()
    assert "browser_route" in content, "route.ts should define browser_route tool"
    assert "browser_route_list" in content, "route.ts should define browser_route_list tool"
    assert "browser_unroute" in content, "route.ts should define browser_unroute tool"


def test_route_exported_from_tools():
    """route module should be exported from tools.ts browserTools array."""
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
    assert "addRoute" in content, "context.ts should have addRoute method"
    assert "removeRoute" in content, "context.ts should have removeRoute method"
    assert "_routes" in content or "routes()" in content, (
        "context.ts should have routes storage or accessor method"
    )


def test_terminal_commands_defined():
    """Terminal commands for network should be defined in commands.ts."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    assert "name: 'route'" in content, "commands.ts should define route command"
    assert "browser_route" in content, "commands.ts should reference browser_route tool"
    assert "name: 'route-list'" in content or 'name: "route-list"' in content, \
        "commands.ts should define route-list command"
    assert "name: 'unroute'" in content, "commands.ts should define unroute command"
    assert "category: 'network'" in content, "commands should use 'network' category"


def test_network_category_in_help():
    """Network category should be in helpGenerator.ts categories array."""
    help_file = REPO / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
    content = help_file.read_text()

    assert "name: 'network'" in content, "helpGenerator.ts should include network category"


def test_route_command_maps_arguments_correctly():
    """Route command should properly map CLI arguments to tool parameters."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    assert "pattern" in content, "Route command should accept pattern argument"
    assert "status" in content, "Route command should accept status option"
    assert "body" in content, "Route command should accept body option"
    assert "content-type" in content or "contentType" in content, \
        "Route command should accept content-type option"
    assert "header" in content, "Route command should accept header option"
    assert "remove-header" in content or "removeHeaders" in content, \
        "Route command should accept remove-header option"


# =============================================================================
# Fail-to-Pass Tests (SKILL.md documentation should be updated)
# =============================================================================

def test_skill_md_has_building_section():
    """SKILL.md should have '## Building' section with lint instructions."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"
    assert skill_file.exists(), "SKILL.md should exist"
    content = skill_file.read_text()

    assert "## Building" in content, "SKILL.md should have '## Building' section"
    assert "run lint" in content, "Building section should mention running lint"


def test_skill_md_testing_updated():
    """SKILL.md Testing section should warn against --debug flag."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"
    assert skill_file.exists(), "SKILL.md should exist"
    content = skill_file.read_text()

    assert "Do not run test --debug" in content, (
        "Testing section should include 'Do not run test --debug'"
    )


def test_skill_md_lint_command_updated():
    """SKILL.md Lint section should use 'npm run flint' not 'npm run flint:mcp'."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"
    assert skill_file.exists(), "SKILL.md should exist"
    content = skill_file.read_text()

    assert "npm run flint" in content, "Lint command should be 'npm run flint'"
    assert "flint:mcp" not in content, "Old 'flint:mcp' command should be removed"


def test_skill_md_has_both_mcp_and_cli_sections():
    """SKILL.md should have both MCP and CLI sections with Building subsections."""
    skill_file = REPO / ".claude/skills/playwright-mcp-dev/SKILL.md"
    assert skill_file.exists(), "SKILL.md should exist"
    content = skill_file.read_text()

    assert "# MCP" in content, "Should have MCP section"
    assert "# CLI" in content, "Should have CLI section"

    building_count = content.count("## Building")
    assert building_count >= 2, (
        f"Should have Building sections for both MCP and CLI (found {building_count})"
    )
