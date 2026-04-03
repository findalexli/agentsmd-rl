"""
Task: playwright-chorecli-add-network-route
Repo: microsoft/playwright @ 824f63da57edf990c6eeab6301d5f1b65dcb4ca8
PR:   39071

Add network route mocking tools (browser_route, browser_route_list, browser_unroute)
to MCP browser tools and CLI, plus update SKILL.md with building/testing guidance.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified/new TypeScript files must parse without syntax errors."""
    files_to_check = [
        "packages/playwright/src/mcp/browser/tools/route.ts",
        "packages/playwright/src/mcp/browser/context.ts",
        "packages/playwright/src/mcp/browser/tools.ts",
        "packages/playwright/src/mcp/terminal/command.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/helpGenerator.ts",
    ]
    for f in files_to_check:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        content = p.read_text()
        # Basic syntax: check balanced braces (rough but catches gross errors)
        assert content.count("{") > 0, f"{f} appears empty or malformed"
        # Check it's valid-ish TypeScript (not a stub or empty export)
        assert len(content.strip()) > 100, f"{f} is suspiciously short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_route_tool_definitions():
    """route.ts must define browser_route, browser_route_list, browser_unroute tools."""
    route_file = Path(REPO) / "packages/playwright/src/mcp/browser/tools/route.ts"
    assert route_file.exists(), "route.ts tool file must exist"
    content = route_file.read_text()

    # All three tool names must be defined
    assert "'browser_route'" in content or '"browser_route"' in content, \
        "route.ts must define a tool named 'browser_route'"
    assert "'browser_route_list'" in content or '"browser_route_list"' in content, \
        "route.ts must define a tool named 'browser_route_list'"
    assert "'browser_unroute'" in content or '"browser_unroute"' in content, \
        "route.ts must define a tool named 'browser_unroute'"

    # Tool must handle pattern parameter
    assert "pattern" in content, "browser_route must accept a 'pattern' parameter"
    # Tool must support body/status for mocking
    assert "body" in content, "browser_route must support 'body' parameter"
    assert "status" in content, "browser_route must support 'status' parameter"

    # Must export an array (default export of tools)
    assert "export default" in content, "route.ts must have a default export"


# [pr_diff] fail_to_pass
def test_context_route_management():
    """context.ts must export RouteEntry type and have addRoute/removeRoute methods."""
    ctx_file = Path(REPO) / "packages/playwright/src/mcp/browser/context.ts"
    content = ctx_file.read_text()

    # RouteEntry type must be exported
    assert "RouteEntry" in content, "context.ts must define RouteEntry type"
    assert re.search(r"export\s+type\s+RouteEntry", content), \
        "RouteEntry must be an exported type"

    # Must have route management methods
    assert "addRoute" in content, "Context must have an addRoute method"
    assert "removeRoute" in content, "Context must have a removeRoute method"
    assert "routes()" in content or "routes (" in content, \
        "Context must have a routes() accessor"

    # RouteEntry must have a pattern field
    assert re.search(r"pattern\s*:", content), "RouteEntry must have a pattern field"


# [pr_diff] fail_to_pass
def test_route_tools_registered():
    """tools.ts must import route module and include it in browserTools array."""
    tools_file = Path(REPO) / "packages/playwright/src/mcp/browser/tools.ts"
    content = tools_file.read_text()

    # Must import route
    assert re.search(r"import\s+route\s+from\s+['\"]./tools/route['\"]", content), \
        "tools.ts must import route from './tools/route'"

    # Must spread route into browserTools
    assert "...route" in content, "browserTools array must include ...route"


# [pr_diff] fail_to_pass
def test_network_category_and_cli_commands():
    """CLI must have 'network' category with route/route-list/unroute commands."""
    # Check command.ts has 'network' in Category type
    cmd_file = Path(REPO) / "packages/playwright/src/mcp/terminal/command.ts"
    cmd_content = cmd_file.read_text()
    assert "'network'" in cmd_content or '"network"' in cmd_content, \
        "command.ts Category type must include 'network'"

    # Check commands.ts has route commands
    cmds_file = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
    cmds_content = cmds_file.read_text()

    # Must declare route, route-list, unroute commands
    assert re.search(r"name:\s*['\"]route['\"]", cmds_content), \
        "commands.ts must declare a 'route' command"
    assert re.search(r"name:\s*['\"]route-list['\"]", cmds_content), \
        "commands.ts must declare a 'route-list' command"
    assert re.search(r"name:\s*['\"]unroute['\"]", cmds_content), \
        "commands.ts must declare an 'unroute' command"

    # Commands must reference the correct tool names
    assert "browser_route" in cmds_content, \
        "route command must reference browser_route tool"
    assert "browser_route_list" in cmds_content, \
        "route-list command must reference browser_route_list tool"
    assert "browser_unroute" in cmds_content, \
        "unroute command must reference browser_unroute tool"

    # Commands must be in network category
    network_section = cmds_content[cmds_content.find("'route'"):cmds_content.find("'unroute'") + 200] \
        if "'route'" in cmds_content else ""
    assert "network" in cmds_content, "Route commands must use 'network' category"

    # Check helpGenerator.ts has network category
    help_file = Path(REPO) / "packages/playwright/src/mcp/terminal/helpGenerator.ts"
    help_content = help_file.read_text()
    assert "'network'" in help_content or '"network"' in help_content, \
        "helpGenerator.ts must include 'network' category"


# [pr_diff] fail_to_pass

    # Must handle fulfill (mock response)
    assert "fulfill" in content, "route handler must call route.fulfill() for mocking"

    # Must handle continue (header modification)
    assert "continue" in content, "route handler must call route.continue() for header modification"

    # Must support contentType
    assert "contentType" in content, "route must support contentType parameter"

    # Must support header addition and removal
    assert "headers" in content.lower(), "route must support header manipulation"
    assert "removeHeaders" in content or "remove" in content.lower(), \
        "route must support removing headers"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — SKILL.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have Building section(s)
    assert re.search(r"##\s*Building", content), \
        "SKILL.md must have a '## Building' section"

    # Must mention watch + lint workflow
    assert "watch" in content.lower(), \
        "Building section should mention watch is running"
    assert "lint" in content.lower(), \
        "Building section should mention using lint for type errors"


# [config_edit] fail_to_pass

    # Must have the corrected lint command
    assert "npm run flint" in content, \
        "SKILL.md must reference 'npm run flint' lint command"

    # Must NOT have the old incorrect command
    assert "flint:mcp" not in content, \
        "SKILL.md must not use the old 'flint:mcp' command — it should be 'flint'"


# [config_edit] fail_to_pass

    # Must explicitly warn about not running test --debug
    # (The frontmatter mentions "debug" in a different context, so check specifically)
    assert re.search(r"(do not|don't|avoid|never).*--debug|--debug.*(do not|don't|avoid|never)", content, re.IGNORECASE), \
        "SKILL.md testing section should warn against using 'test --debug'"
