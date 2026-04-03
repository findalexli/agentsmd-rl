"""
Task: playwright-chore-add-playwrightcli-config
Repo: microsoft/playwright @ 71e5079b735eda08a72b0fac58a3dd02fde6bb9f
PR:   38971

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"
MCP_TERMINAL = f"{REPO}/packages/playwright/src/mcp/terminal"
MCP_BROWSER = f"{REPO}/packages/playwright/src/mcp/browser"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be readable and non-empty."""
    files = [
        f"{MCP_BROWSER}/config.ts",
        f"{MCP_TERMINAL}/command.ts",
        f"{MCP_TERMINAL}/commands.ts",
        f"{MCP_TERMINAL}/helpGenerator.ts",
        f"{MCP_TERMINAL}/program.ts",
    ]
    for fpath in files:
        p = Path(fpath)
        assert p.exists(), f"File not found: {fpath}"
        content = p.read_text()
        assert len(content) > 100, f"File suspiciously small: {fpath}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_config_command_declared():
    """A 'config' command must be declared in commands.ts with category 'config'."""
    src = Path(f"{MCP_TERMINAL}/commands.ts").read_text()

    # Must declare a command with name 'config'
    assert re.search(r"name:\s*['\"]config['\"]", src), \
        "commands.ts must declare a command with name: 'config'"

    # Must have category 'config'
    assert re.search(r"category:\s*['\"]config['\"]", src), \
        "config command must have category: 'config'"

    # Must be included in the commandsArray
    # Look for 'config' being referenced after commandsArray declaration
    array_start = src.find("commandsArray")
    assert array_start != -1, "commandsArray not found"
    array_section = src[array_start:]
    assert "config" in array_section, \
        "config command must be added to commandsArray"


# [pr_diff] fail_to_pass
def test_config_category_type():
    """Category type must include 'config'."""
    src = Path(f"{MCP_TERMINAL}/command.ts").read_text()

    # Find the Category type union
    cat_match = re.search(r"type Category\s*=\s*([^;]+);", src)
    assert cat_match, "Category type not found in command.ts"
    cat_def = cat_match.group(1)
    assert "'config'" in cat_def or '"config"' in cat_def, \
        "Category type must include 'config'"


# [pr_diff] fail_to_pass
def test_config_category_in_help():
    """Help generator must list 'config' category with title 'Configuration'."""
    src = Path(f"{MCP_TERMINAL}/helpGenerator.ts").read_text()

    # Must have config category in the categories array
    assert re.search(r"name:\s*['\"]config['\"]", src), \
        "helpGenerator must include config in categories"
    assert re.search(r"title:\s*['\"]Configuration['\"]", src), \
        "config category must have title 'Configuration'"


# [pr_diff] fail_to_pass
def test_configure_method_exists():
    """SessionManager must have a configure method that handles config command."""
    src = Path(f"{MCP_TERMINAL}/program.ts").read_text()

    # Must have async configure method
    assert re.search(r"async\s+configure\s*\(", src), \
        "SessionManager must have an async configure() method"

    # configure must reference session connection/reconnection
    configure_start = src.find("async configure")
    assert configure_start != -1
    configure_body = src[configure_start:configure_start + 500]

    # Must stop existing session before reconfiguring
    assert "stop" in configure_body, \
        "configure() should stop existing session before reconfiguring"

    # Must set config from args
    assert "config" in configure_body and "args" in configure_body, \
        "configure() must set config from args"


# [pr_diff] fail_to_pass
def test_program_routes_config_command():
    """Program must route 'config' command to handleSessionCommand."""
    src = Path(f"{MCP_TERMINAL}/program.ts").read_text()

    # The program function should handle 'config' commandName
    program_start = src.find("async function program") or src.find("export async function program")
    assert program_start != -1, "program function not found"
    program_body = src[program_start:]

    # Must check for 'config' command name
    assert re.search(r"commandName\s*===?\s*['\"]config['\"]", program_body), \
        "program must check for commandName === 'config'"


# [pr_diff] fail_to_pass

    # Must have contextOptions with viewport
    assert "contextOptions" in src, \
        "config.ts must include contextOptions"
    assert "viewport" in src, \
        "config.ts must set viewport in contextOptions"

    # Must use 1280x720 for headless
    assert "1280" in src and "720" in src, \
        "Default viewport should be 1280x720 for headless mode"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a Configuration section or mention config command
    lower = skill_md.lower()
    assert "configuration" in lower or "### config" in lower, \
        "SKILL.md should have a Configuration section"

    # Must show the config command usage
    assert "playwright-cli config" in skill_md, \
        "SKILL.md should document 'playwright-cli config' usage"

    # Must show session-scoped config usage
    assert "--session" in skill_md and "config" in skill_md, \
        "SKILL.md should show session-scoped config usage"

    # Must show at least 2 config-related example commands
    config_examples = [
        line.strip() for line in skill_md.split("\n")
        if "playwright-cli" in line and "config" in line.lower()
        and not line.strip().startswith("#")
    ]
    assert len(config_examples) >= 2, \
        f"SKILL.md should have at least 2 config example commands, found {len(config_examples)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_configure_not_stub():
    """configure() method must have real logic, not just pass/return."""
    src = Path(f"{MCP_TERMINAL}/program.ts").read_text()

    configure_match = re.search(r"async\s+configure\s*\([^)]*\)[^{]*\{", src)
    assert configure_match, "configure method not found"

    # Extract method body (count braces)
    start = configure_match.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    body = src[start:i - 1]

    # Must have multiple statements (not just a stub)
    non_empty_lines = [l.strip() for l in body.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(non_empty_lines) >= 4, \
        f"configure() body too short ({len(non_empty_lines)} lines), likely a stub"
