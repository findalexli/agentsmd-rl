"""
Task: playwright-featmcp-add-cdp-option-to
Repo: playwright @ 9d81a6754d9426295ac10bd33278fb2af476c8a9
PR:   microsoft/playwright#40017

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
    ts_files = [
        Path(REPO) / "packages/playwright-core/src/tools/cli-client/program.ts",
        Path(REPO) / "packages/playwright-core/src/tools/cli-client/session.ts",
        Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts",
        Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/program.ts",
        Path(REPO) / "packages/playwright-core/src/tools/mcp/config.ts",
    ]
    for f in ts_files:
        content = f.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {f.name}"
        assert content.count("(") == content.count(")"), \
            f"Unbalanced parentheses in {f.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_attach_command_has_cdp_option():
    """The attach command declaration must have a 'cdp' option for CDP endpoint URL."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    # Find the attach command's options block
    attach_match = re.search(r"const\s+attach\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;?", content)
    assert attach_match, "Could not find attach command declaration"
    attach_block = attach_match.group(1)
    assert "cdp" in attach_block, \
        "attach command must have a 'cdp' option"
    assert re.search(r"cdp.*CDP", attach_block, re.IGNORECASE), \
        "cdp option must describe CDP endpoint connection"


# [pr_diff] fail_to_pass
def test_attach_name_arg_optional():
    """The attach command's 'name' argument must be optional."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    attach_match = re.search(r"const\s+attach\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;?", content)
    assert attach_match, "Could not find attach command declaration"
    attach_block = attach_match.group(1)
    # The name arg should be z.string().optional()
    assert re.search(r"name.*optional", attach_block), \
        "attach command name argument must be optional (was previously required)"


# [pr_diff] fail_to_pass
def test_open_command_no_extension_option():
    """The open command must NOT have an 'extension' option (moved to attach)."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    open_match = re.search(r"const\s+open\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;", content)
    assert open_match, "Could not find open command declaration"
    open_block = open_match.group(1)
    assert "extension" not in open_block, \
        "open command must not have 'extension' option (should be moved to attach)"


# [pr_diff] fail_to_pass
def test_attach_command_has_extension_option():
    """The attach command must have an 'extension' option."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    attach_match = re.search(r"const\s+attach\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;?", content)
    assert attach_match, "Could not find attach command declaration"
    attach_block = attach_match.group(1)
    assert "extension" in attach_block, \
        "attach command must have 'extension' option"


# [pr_diff] fail_to_pass
def test_session_passes_cdp_arg():
    """Session must pass --cdp argument to the daemon process."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-client/session.ts").read_text()
    assert re.search(r"cliArgs\.cdp", content), \
        "session.ts must check cliArgs.cdp"
    assert re.search(r"--cdp=", content), \
        "session.ts must pass --cdp=<value> to daemon args"


# [pr_diff] fail_to_pass
def test_config_passes_cdp_endpoint():
    """Config resolution must pass cdpEndpoint from CLI options."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/mcp/config.ts").read_text()
    assert "cdpEndpoint" in content, \
        "config.ts must pass cdpEndpoint in configFromCLIOptions"
    # cdpEndpoint should factor into the isolated browser check
    assert re.search(r"cdpEndpoint.*isolated|isolated.*cdpEndpoint", content, re.DOTALL), \
        "cdpEndpoint must be considered in the isolated browser check"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_open_command_still_has_browser_option():
    """The open command must still have its browser option."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    open_match = re.search(r"const\s+open\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;", content)
    assert open_match, "Could not find open command declaration"
    open_block = open_match.group(1)
    assert "browser" in open_block, "open command must still have browser option"
    assert "headed" in open_block, "open command must still have headed option"
    assert "persistent" in open_block, "open command must still have persistent option"


# [static] pass_to_pass
def test_attach_command_has_endpoint_option():
    """The attach command must also have an 'endpoint' option."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts").read_text()
    attach_match = re.search(r"const\s+attach\s*=\s*declareCommand\s*\(\s*\{([\s\S]*?)\}\s*\)\s*;?", content)
    assert attach_match, "Could not find attach command declaration"
    attach_block = attach_match.group(1)
    assert re.search(r"endpoint.*optional", attach_block), \
        "attach command must have endpoint option"
