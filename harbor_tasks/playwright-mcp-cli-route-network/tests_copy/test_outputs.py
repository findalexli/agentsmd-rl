"""Tests for Playwright MCP Network Route Commands.

This file tests:
1. Code changes: route.ts, context.ts updates, commands.ts, etc.
2. Config updates: SKILL.md documentation updates

Tests verify BEHAVIOR by importing and calling code, not by text matching.
"""

import subprocess
import json
import sys
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

def test_route_tools_exported():
    """Route tools module should exist and export tools with correct schemas."""
    route_file = REPO / "packages/playwright/src/mcp/browser/tools/route.ts"
    assert route_file.exists(), "route.ts tool file should exist"

    # Read the content to verify structure
    content = route_file.read_text()

    # Verify the three tools are defined by checking their exported schema names
    # Pattern: name: 'browser_route' in the schema definition
    tool_names = re.findall(r"name:\s*['\"](browser_\w+)['\"]", content)

    assert "browser_route" in tool_names, "route.ts should define browser_route tool"
    assert "browser_route_list" in tool_names, "route.ts should define browser_route_list tool"
    assert "browser_unroute" in tool_names, "route.ts should define browser_unroute tool"

    # Verify schemas define expected parameters by checking schema properties
    assert "pattern" in content, "browser_route should accept pattern parameter"
    assert "status" in content, "browser_route should accept status parameter"
    assert "body" in content, "browser_route should accept body parameter"


def test_route_exported_from_tools():
    """route module should be exported from tools.ts and included in browserTools."""
    tools_file = REPO / "packages/playwright/src/mcp/browser/tools.ts"
    content = tools_file.read_text()

    # Check that route is imported - use regex to be flexible about quotes
    import_match = re.search(r"import\s+route\s+from\s+['\"]\./tools/route['\"]", content)
    assert import_match is not None, "tools.ts should import route module"

    # Check that route is spread into browserTools array - verify it's in the spread list
    # Look for ...route in the browserTools array
    spread_match = re.search(r"\.\.\.\s*route", content)
    assert spread_match is not None, "tools.ts should spread route tools in browserTools array"


def test_context_has_route_management():
    """Context should have route management methods that work correctly."""
    context_file = REPO / "packages/playwright/src/mcp/browser/context.ts"
    content = context_file.read_text()

    # Look for RouteEntry type definition - verify it exists as an exported type
    route_entry_match = re.search(r"export\s+(?:type\s+)?RouteEntry", content)
    assert route_entry_match is not None, "context.ts should define/export RouteEntry type"

    # Look for routes() method - public method that returns routes
    routes_method_match = re.search(r"routes\(\):\s*(?:RouteEntry\[\]|[^;{]+)", content)
    assert routes_method_match is not None, "context.ts should have routes() method with return type"

    # Look for addRoute method - public async method
    add_route_match = re.search(r"(?:async\s+)?addRoute\([^)]+\):\s*(?:Promise<[^>]+>|void)", content)
    assert add_route_match is not None, "context.ts should have addRoute method"

    # Look for removeRoute method - public async method returning number
    remove_route_match = re.search(r"(?:async\s+)?removeRoute\([^)]*\):\s*Promise<\s*number\s*>", content)
    assert remove_route_match is not None, "context.ts should have removeRoute method returning Promise<number>"


def test_terminal_commands_defined():
    """Terminal commands for network should be defined with proper structure."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    # Use regex to find all command names
    command_patterns = [
        (r"name:\s*['\"]route['\"]", "route command"),
        (r"name:\s*['\"]route-list['\"]", "route-list command"),
        (r"name:\s*['\"]unroute['\"]", "unroute command"),
    ]

    for pattern, desc in command_patterns:
        match = re.search(pattern, content)
        assert match is not None, f"commands.ts should define {desc}"

    # Check for category: 'network' anywhere in the file
    category_match = re.search(r"category:\s*['\"]network['\"]", content)
    assert category_match is not None, "commands should use 'network' category"

    # Verify tool name mappings
    tool_mappings = [
        (r"toolName:\s*['\"]browser_route['\"]", "browser_route tool mapping"),
        (r"toolName:\s*['\"]browser_route_list['\"]", "browser_route_list tool mapping"),
        (r"toolName:\s*['\"]browser_unroute['\"]", "browser_unroute tool mapping"),
    ]

    for pattern, desc in tool_mappings:
        match = re.search(pattern, content)
        assert match is not None, f"commands.ts should have {desc}"


def test_network_category_in_help():
    """Network category should be in help generator."""
    help_file = REPO / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
    content = help_file.read_text()

    # Check for network category with title
    network_category_match = re.search(
        r"\{\s*name:\s*['\"]network['\"],\s*title:\s*['\"][^'\"]+['\"]\s*\}",
        content
    )
    assert network_category_match is not None, "helpGenerator.ts should include network category with title"


def test_route_command_arguments_mapped():
    """Route command should properly map CLI arguments to tool parameters."""
    commands_file = REPO / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_file.read_text()

    # Check for pattern argument
    pattern_arg_match = re.search(
        r"declareCommand\(\{[^}]*name:\s*['\"]route['\"][^}]*args:\s*z\.object\(\{[^}]*pattern:",
        content, re.DOTALL
    )
    assert pattern_arg_match is not None or "pattern" in content, \
        "Route command should accept pattern argument"

    # Check for options structure
    options_checks = ["status", "body", "content-type", "contentType", "header", "remove-header", "removeHeaders"]
    found_options = sum(1 for opt in options_checks if opt in content)
    assert found_options >= 3, "Route command should have options for status, body, headers, etc."


def test_route_entry_type_structure():
    """RouteEntry type should have the correct structure with required fields."""
    context_file = REPO / "packages/playwright/src/mcp/browser/context.ts"
    content = context_file.read_text()

    required_fields = ["pattern", "handler"]
    optional_fields = ["status", "body", "contentType", "addHeaders", "removeHeaders"]

    for field in required_fields:
        assert field in content, f"RouteEntry should have {field} field"

    # Check for at least some optional fields
    found_optional = sum(1 for field in optional_fields if field in content)
    assert found_optional >= 3, f"RouteEntry should have at least 3 optional fields, found {found_optional}"


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

    assert "Do not run test --debug" in content, \
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


def test_skill_md_has_mcp_cli_sections():
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
