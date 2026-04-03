"""
Task: playwright-chorecli-allow-installing-skills-locally
Repo: microsoft/playwright @ 6a928b02f4de1efc633a8fae0331cd1fa821950e
PR:   39078

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must have balanced braces and no obvious syntax errors."""
    files = [
        "packages/playwright/src/mcp/browser/tools/route.ts",
        "packages/playwright/src/mcp/config.d.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/program.ts",
        "packages/playwright/src/mcp/terminal/helpGenerator.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} appears truncated"
        assert content.count("{") == content.count("}"), f"{f} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_route_tools_use_network_capability():
    """Route, routeList, and unroute tools must use 'network' capability, not 'core'."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/browser/tools/route.ts").read_text()
    caps = re.findall(r"capability:\s*['\"](\w+)['\"]", content)
    assert len(caps) >= 3, f"Expected at least 3 capability declarations, found {len(caps)}"
    for cap in caps:
        assert cap == "network", f"Route tool capability should be 'network', got '{cap}'"


# [pr_diff] fail_to_pass
def test_network_in_tool_capability_type():
    """The ToolCapability type in config.d.ts must include 'network'."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/config.d.ts").read_text()
    assert "'network'" in content, "config.d.ts must declare 'network' as a ToolCapability"


# [pr_diff] fail_to_pass
def test_install_command_renamed_to_install_browser():
    """The 'install' command must be renamed to 'install-browser'."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/terminal/commands.ts").read_text()
    assert re.search(r"name:\s*['\"]install-browser['\"]", content), (
        "commands.ts should have a command named 'install-browser'"
    )


# [pr_diff] fail_to_pass
def test_install_skills_command_declared():
    """A new 'install-skills' command must be declared in commands.ts."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/terminal/commands.ts").read_text()
    assert re.search(r"name:\s*['\"]install-skills['\"]", content), (
        "commands.ts should declare an 'install-skills' command"
    )
    assert "installSkills" in content, "installSkills must be registered in commandsArray"


# [pr_diff] fail_to_pass
def test_install_skills_implementation():
    """program.ts must implement the installSkills function that copies skill directory."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/terminal/program.ts").read_text()
    assert "install-skills" in content, "program.ts must handle the 'install-skills' command"
    assert re.search(r"(async\s+)?function\s+installSkills", content), (
        "program.ts must define an installSkills function"
    )
    assert ".claude" in content and "skills" in content and "playwright" in content, (
        "installSkills must target .claude/skills/playwright directory"
    )


# [pr_diff] fail_to_pass
def test_help_generator_uses_in_memory():
    """helpGenerator.ts must use '--in-memory' instead of '--isolated'."""
    content = Path(f"{REPO}/packages/playwright/src/mcp/terminal/helpGenerator.ts").read_text()
    assert "--in-memory" in content, "helpGenerator.ts should reference --in-memory flag"
    assert "--isolated" not in content, "helpGenerator.ts should not reference --isolated flag"


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — documentation/skill file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [agent_config] pass_to_pass
