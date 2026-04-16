"""
Task: playwright-mcp-persistent-context-shared
Repo: microsoft/playwright @ 114f3a296a78dfbc1eb6631bb358e9fe9b1677bb
PR: 39601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/playwright")
MCP_DIR = REPO / "packages" / "playwright-core" / "src" / "mcp"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/playwright-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Filter out only actual errors (lines containing "error TS")
    output = result.stdout + "\n" + result.stderr
    errors = [line for line in output.split('\n') if 'error TS' in line]
    if errors:
        assert False, f"TypeScript compilation errors:\n" + "\n".join(errors[:20])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

def test_shared_browser_context_option_removed_from_program():
    """The --shared-browser-context CLI option must be removed from program.ts."""
    program_ts = MCP_DIR / "program.ts"
    content = program_ts.read_text()

    # Should NOT contain the shared-browser-context option
    assert "--shared-browser-context" not in content, \
        "program.ts still contains --shared-browser-context CLI option"


def test_shared_browser_context_removed_from_config_types():
    """sharedBrowserContext property must be removed from config.d.ts."""
    config_d_ts = MCP_DIR / "config.d.ts"
    content = config_d_ts.read_text()

    # Should NOT contain sharedBrowserContext property
    assert "sharedBrowserContext" not in content, \
        "config.d.ts still contains sharedBrowserContext property"


def test_shared_browser_context_removed_from_config_ts():
    """sharedBrowserContext must be removed from config.ts."""
    config_ts = MCP_DIR / "config.ts"
    content = config_ts.read_text()

    # Should NOT contain sharedBrowserContext
    assert "sharedBrowserContext" not in content, \
        "config.ts still references sharedBrowserContext"


def test_shared_browser_context_removed_from_configIni():
    """sharedBrowserContext must be removed from configIni.ts."""
    configIni_ts = MCP_DIR / "configIni.ts"
    content = configIni_ts.read_text()

    # Should NOT contain sharedBrowserContext
    assert "sharedBrowserContext" not in content, \
        "configIni.ts still contains sharedBrowserContext"


def test_program_ts_has_userdatadir_check():
    """program.ts must use userDataDir to determine shared browser behavior."""
    program_ts = MCP_DIR / "program.ts"
    content = program_ts.read_text()

    # Should contain the new logic for detecting shared browser via userDataDir
    assert "useSharedBrowser" in content, \
        "program.ts missing useSharedBrowser variable"
    assert "userDataDir" in content, \
        "program.ts missing userDataDir reference for auto-sharing"


def test_program_ts_has_lazy_browser_creation():
    """program.ts must lazily create shared browser on first client connection."""
    program_ts = MCP_DIR / "program.ts"
    content = program_ts.read_text()

    # Should contain lazy creation logic
    assert "clientCount === 0" in content, \
        "program.ts missing lazy browser creation check (clientCount === 0)"


def test_program_ts_has_browser_cleanup():
    """program.ts must clear sharedBrowser reference on client disconnect."""
    program_ts = MCP_DIR / "program.ts"
    content = program_ts.read_text()

    # Should contain cleanup logic
    assert "sharedBrowser = undefined" in content, \
        "program.ts missing sharedBrowser cleanup (sharedBrowser = undefined)"


# ---------------------------------------------------------------------------
# Config-derived (pr_diff) - documentation update tests
# ---------------------------------------------------------------------------

def test_claude_md_has_co_authored_by_rule():
    """CLAUDE.md must contain the new rule about Co-Authored-By agents."""
    claude_md = REPO / "CLAUDE.md"
    content = claude_md.read_text()

    # Should contain the new rule about Co-Authored-By
    assert "Co-Authored-By" in content, \
        "CLAUDE.md missing the Co-Authored-By rule"
    assert "Never add Co-Authored-By agents in commit message" in content, \
        "CLAUDE.md missing the exact Co-Authored-By commit message rule"
