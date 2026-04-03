"""
Task: playwright-chorecli-implement-direct-daemon-startup
Repo: microsoft/playwright @ 25d303f03424011dc0ad36d027a7af3368618eab
PR:   39162

Refactors daemon startup to launch browser directly via stdout communication
instead of polling. Renames the CLI session flag from -b to -s. Updates
SKILL.md and session-management reference docs accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"
MCP_DIR = Path(REPO) / "packages" / "playwright" / "src" / "mcp"
SKILL_DIR = Path(REPO) / "packages" / "playwright" / "src" / "skill"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files exist and are non-empty."""
    files = [
        MCP_DIR / "terminal" / "program.ts",
        MCP_DIR / "terminal" / "daemon.ts",
        MCP_DIR / "terminal" / "helpGenerator.ts",
        MCP_DIR / "browser" / "browserContextFactory.ts",
        MCP_DIR / "program.ts",
    ]
    for f in files:
        assert f.exists(), f"Missing file: {f}"
        content = f.read_text()
        assert len(content) > 100, f"File suspiciously small: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_session_flag_renamed_in_arg_parser():
    """program.ts normalizes -s (not -b) to --session."""
    src = (MCP_DIR / "terminal" / "program.ts").read_text()
    # After fix: args.s → args.session, and -s alias
    assert "args.s" in src or "args['s']" in src, \
        "program.ts should reference args.s for the session alias"
    assert "args.session = args.s" in src or "session = args.s" in src, \
        "program.ts should normalize -s to --session"
    # Should NOT have the old -b alias normalization
    lines = src.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if "args.b" in stripped and "session" in stripped:
            assert False, "program.ts still has old -b to --session normalization"


# [pr_diff] fail_to_pass
def test_help_generator_shows_new_flag():
    """Help text uses -s=<session>, not -b=<session>."""
    src = (MCP_DIR / "terminal" / "helpGenerator.ts").read_text()
    assert "-s=" in src, "helpGenerator should show -s= in usage text"
    # Must not have old -b= usage line
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "-b=" in line and "session" in line.lower():
            assert False, "helpGenerator still shows old -b= session usage"


# [pr_diff] fail_to_pass
def test_direct_daemon_startup():
    """daemon.ts creates browser context directly, not via ServerBackendFactory."""
    src = (MCP_DIR / "terminal" / "daemon.ts").read_text()
    # After fix: imports BrowserContextFactory type and calls createContext
    assert "createContext" in src, \
        "daemon.ts should call createContext for direct browser launch"
    assert "BrowserContextFactory" in src or "browserContextFactory" in src, \
        "daemon.ts should reference BrowserContextFactory"
    # Should NOT import ServerBackendFactory
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "ServerBackendFactory" in line and "import" in line:
            assert False, "daemon.ts should not import ServerBackendFactory anymore"


# [pr_diff] fail_to_pass
def test_browser_error_message_includes_channel():
    """browserContextFactory.ts error includes browser channel name, not generic message."""
    src = (MCP_DIR / "browser" / "browserContextFactory.ts").read_text()
    # After fix: throwBrowserIsNotInstalledError helper with channel interpolation
    assert "throwBrowserIsNotInstalledError" in src, \
        "Should have throwBrowserIsNotInstalledError helper function"
    func_match = re.search(
        r'function\s+throwBrowserIsNotInstalledError.*?\{(.*?)\n\}',
        src, re.DOTALL
    )
    assert func_match, "throwBrowserIsNotInstalledError function not found"
    func_body = func_match.group(1)
    assert "channel" in func_body or "browserName" in func_body, \
        "Error function should include browser channel/name in the message"


# [pr_diff] fail_to_pass
def test_daemon_stdout_communication():
    """program.ts uses stdout markers for daemon communication."""
    src = (MCP_DIR / "program.ts").read_text()
    has_success_marker = "### Success" in src
    has_eof_marker = "<EOF>" in src
    assert has_success_marker, "program.ts should output '### Success' marker for daemon"
    assert has_eof_marker, "program.ts should output '<EOF>' marker for daemon communication"


# [pr_diff] fail_to_pass
def test_session_flag_in_error_messages():
    """Error messages and console output use -s= not -b for session references."""
    src = (MCP_DIR / "terminal" / "program.ts").read_text()
    found_s_flag = False
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "-s=" in line and ("open" in line or "session" in line.lower()):
            found_s_flag = True
            break
    assert found_s_flag, "program.ts error messages should reference -s= flag for sessions"


# ---------------------------------------------------------------------------
# Config/documentation update tests (config_edit)
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Agent config compliance (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
