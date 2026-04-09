"""
Task: playwright-fixmcp-persistent-context-is-always
Repo: microsoft/playwright @ 114f3a296a78dfbc1eb6631bb358e9fe9b1677bb
PR:   39601

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    script_path = Path(REPO) / "_eval_tmp.mjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CLI flag and config option removal
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cli_flag_removed():
    """program.ts must not register --shared-browser-context as a CLI option."""
    result = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/mcp/program.ts', 'utf8');

// Extract all .option() definitions
const optionRe = /\\.option\\('([^']+)'/g;
const options = [];
let m;
while ((m = optionRe.exec(src)) !== null) options.push(m[1]);

if (options.some(o => o.startsWith('--shared-browser-context'))) {
    console.error('FAIL: --shared-browser-context still registered as CLI option');
    process.exit(1);
}

// Sanity: other nearby options still present
for (const expected of ['--sandbox', '--save-session', '--snapshot-mode']) {
    if (!options.some(o => o.startsWith(expected))) {
        console.error('FAIL: expected option ' + expected + ' missing');
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert result.returncode == 0, f"CLI flag check failed:\n{result.stderr}\n{result.stdout}"


# [pr_diff] fail_to_pass
def test_config_type_removed():
    """config.d.ts Config type must not define sharedBrowserContext."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/config.d.ts").read_text()
    assert "sharedBrowserContext" not in content, \
        "sharedBrowserContext should be removed from Config type definition"


# [pr_diff] fail_to_pass
def test_config_ts_removed():
    """config.ts CLIOptions and configFromCLIOptions must not reference sharedBrowserContext."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/config.ts").read_text()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "sharedBrowserContext" not in stripped, \
            f"sharedBrowserContext still referenced in config.ts: {stripped}"


# [pr_diff] fail_to_pass
def test_config_ini_removed():
    """configIni.ts longhandTypes must not include sharedBrowserContext."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/configIni.ts").read_text()
    assert "sharedBrowserContext" not in content, \
        "sharedBrowserContext should be removed from configIni longhandTypes"


# [pr_diff] fail_to_pass
def test_auto_detect_user_data_dir():
    """program.ts must use userDataDir to auto-detect shared browser mode."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/program.ts").read_text()
    assert "config.browser.userDataDir" in content, \
        "program.ts should use config.browser.userDataDir for shared browser auto-detection"
    assert "config.sharedBrowserContext" not in content, \
        "program.ts should not reference config.sharedBrowserContext"


# [pr_diff] fail_to_pass
def test_lazy_browser_lifecycle():
    """Shared browser must be lazily created on first client and cleaned up on last disconnect."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/program.ts").read_text()
    assert "clientCount === 0" in content, \
        "Should lazily create shared browser when first client connects (clientCount === 0)"
    assert "sharedBrowser = undefined" in content, \
        "Should reset sharedBrowser to undefined when last client disconnects"


# ---------------------------------------------------------------------------
# Config file update checks — fail_to_pass
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_coauthored_by_rule():
    """CLAUDE.md must include a rule prohibiting Co-Authored-By in commit messages."""
    claude_md = (Path(REPO) / "CLAUDE.md").read_text()
    lower = claude_md.lower()
    assert "co-authored-by" in lower, \
        "CLAUDE.md should contain a rule about Co-Authored-By in commit messages"
    # Verify the rule is prohibitive
    lines_with_coauthor = [
        line for line in claude_md.splitlines()
        if "co-authored-by" in line.lower()
    ]
    assert any("never" in line.lower() or "don't" in line.lower() or "do not" in line.lower()
               for line in lines_with_coauthor), \
        "CLAUDE.md rule should prohibit Co-Authored-By (e.g., 'Never add Co-Authored-By')"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_program_still_creates_browsers():
    """program.ts must still use createBrowser for browser instantiation."""
    content = (Path(REPO) / "packages/playwright-core/src/mcp/program.ts").read_text()
    assert "createBrowser" in content, \
        "program.ts should still call createBrowser"
    assert "sharedBrowser" in content, \
        "program.ts should still have sharedBrowser variable"
