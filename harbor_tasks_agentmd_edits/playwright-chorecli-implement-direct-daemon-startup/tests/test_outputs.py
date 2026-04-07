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

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
MCP_DIR = Path(REPO) / "packages" / "playwright" / "src" / "mcp"
SKILL_DIR = Path(REPO) / "packages" / "playwright" / "src" / "skill"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

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
# Fail-to-pass (pr_diff) -- behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_session_flag_normalization_behavior():
    """The arg parser normalizes -s to --session, verified by executing the logic."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');

// Find the session-alias normalization block (matches both old -b and new -s)
const match = src.match(/\\/\\/ Normalize -[sb] alias to --session[\\s\\S]*?delete args\\.[sb];?\\s*\\}/);
if (!match) {
  console.error('No session alias normalization block found');
  process.exit(1);
}

// Strip comments and execute the block with a test args object
const code = match[0].replace(/\\/\\/.*/g, '');
const args = { s: 'my-session' };
eval(code);

// After fix: the -s flag should be normalized to --session
if (args.session !== 'my-session') {
  console.error('Expected args.session="my-session", got:', args.session);
  process.exit(1);
}
if ('s' in args) {
  console.error('args.s should have been deleted after normalization');
  process.exit(1);
}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_browser_error_includes_channel_name():
    """throwBrowserIsNotInstalledError includes the specific browser channel in the error."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/browserContextFactory.ts', 'utf8');

// Extract the throwBrowserIsNotInstalledError function
const match = src.match(/function\\s+throwBrowserIsNotInstalledError[\\s\\S]*?\\n\\}/);
if (!match) {
  console.error('throwBrowserIsNotInstalledError function not found');
  process.exit(1);
}

// Strip TS type annotations to produce valid JS
let fn = match[0]
  .replace(/\\(config:\\s*FullConfig\\)/g, '(config)')
  .replace(/:\\s*never/g, '');
eval(fn);

// Test: uses launchOptions.channel when available
try {
  throwBrowserIsNotInstalledError({
    browser: { launchOptions: { channel: 'chrome' }, browserName: 'chromium' },
    skillMode: false
  });
} catch (e) {
  if (!e.message.includes('chrome')) {
    console.error('Error should mention "chrome", got:', e.message);
    process.exit(1);
  }
}

// Test: falls back to browserName when no channel specified
try {
  throwBrowserIsNotInstalledError({
    browser: { browserName: 'firefox' },
    skillMode: false
  });
} catch (e) {
  if (!e.message.includes('firefox')) {
    console.error('Error should mention "firefox", got:', e.message);
    process.exit(1);
  }
}

console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- structural tests
# ---------------------------------------------------------------------------

def test_help_generator_shows_new_flag():
    """Help text uses -s=<session>, not -b=<session>."""
    src = (MCP_DIR / "terminal" / "helpGenerator.ts").read_text()
    assert "-s=" in src, "helpGenerator should show -s= in usage text"
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "-b=" in line and "session" in line.lower():
            assert False, "helpGenerator still shows old -b= session usage"


def test_direct_daemon_startup():
    """daemon.ts creates browser context directly, not via ServerBackendFactory."""
    src = (MCP_DIR / "terminal" / "daemon.ts").read_text()
    assert "createContext" in src, \
        "daemon.ts should call createContext for direct browser launch"
    assert "BrowserContextFactory" in src or "browserContextFactory" in src, \
        "daemon.ts should reference BrowserContextFactory"
    for line in src.splitlines():
        if line.strip().startswith("//"):
            continue
        if "ServerBackendFactory" in line and "import" in line:
            assert False, "daemon.ts should not import ServerBackendFactory anymore"


def test_daemon_stdout_communication():
    """program.ts uses stdout markers for daemon communication instead of polling."""
    src = (MCP_DIR / "program.ts").read_text()
    assert "### Success" in src, "program.ts should output '### Success' marker"
    assert "<EOF>" in src, "program.ts should output '<EOF>' marker"


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
    assert found_s_flag, "program.ts error messages should reference -s= flag"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- documentation updates
# ---------------------------------------------------------------------------

def test_skill_md_session_flag_updated():
    """SKILL.md uses -s= for session examples, not -b."""
    src = (SKILL_DIR / "SKILL.md").read_text()
    assert "-s=" in src, "SKILL.md should use -s= for session flag"
    in_code_block = False
    for line in src.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if in_code_block and "playwright-cli -b" in line:
            assert False, f"SKILL.md still uses -b in code: {line.strip()}"


def test_session_management_md_updated():
    """session-management.md uses -s= for session flag, not -b."""
    src = (SKILL_DIR / "references" / "session-management.md").read_text()
    assert "-s=" in src, "session-management.md should use -s= flag"
    in_code_block = False
    for line in src.splitlines():
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
        if in_code_block and "playwright-cli -b" in line:
            assert False, f"session-management.md still uses -b: {line.strip()}"
