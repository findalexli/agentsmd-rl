"""
Task: playwright-feat-add-cdp-option-to-attach
Repo: microsoft/playwright @ 9d81a6754d9426295ac10bd33278fb2af476c8a9
PR:   40017

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

CLI_CLIENT = f"{REPO}/packages/playwright-core/src/tools/cli-client"
CLI_DAEMON = f"{REPO}/packages/playwright-core/src/tools/cli-daemon"
MCP = f"{REPO}/packages/playwright-core/src/tools/mcp"
SKILL_MD = f"{CLI_CLIENT}/skill/SKILL.md"


def _run_js(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using node
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_global_options_includes_cdp():
    """globalOptions array includes 'cdp' for CLI argument parsing."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/cli-client/program.ts', 'utf-8');

// Extract the globalOptions array definition
const match = src.match(/const globalOptions[^=]*=\s*\[([\s\S]*?)\];/);
if (!match) {
    process.stderr.write('globalOptions array not found in program.ts');
    process.exit(1);
}

// Parse string literal entries from the array
const entries = match[1].match(/'(\w+)'/g);
if (!entries) {
    process.stderr.write('No entries found in globalOptions array');
    process.exit(1);
}
const options = entries.map(s => s.slice(1, -1));
if (!options.includes('cdp')) {
    process.stderr.write('cdp not in globalOptions: ' + JSON.stringify(options));
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_attach_schema_has_cdp_option():
    """attach command zod schema declares cdp option."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf-8');

// Find the attach command declaration
const attachIdx = src.indexOf('const attach');
if (attachIdx === -1) {
    process.stderr.write('attach command declaration not found');
    process.exit(1);
}

// Extract from attach to the next top-level declaration
const rest = src.slice(attachIdx);
const endMatch = rest.match(/\n(?:const |export )/);
const block = endMatch ? rest.slice(0, endMatch.index) : rest;

// Verify cdp option exists in the options zod schema
if (!/options:\s*z\.object\(\{[\s\S]*?cdp:\s*z\./.test(block)) {
    process.stderr.write('cdp option not found in attach command zod schema');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_attach_conflict_detection():
    """attach command detects conflicting target + --cdp/--endpoint/--extension."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/cli-client/program.ts', 'utf-8');

// Find the 'case attach' block
const caseIdx = src.indexOf("case 'attach':");
if (caseIdx === -1) {
    process.stderr.write('case attach not found in program.ts');
    process.exit(1);
}

// Extract until 'return;'
const rest = src.slice(caseIdx);
const returnIdx = rest.indexOf('return;');
if (returnIdx === -1) {
    process.stderr.write('no return statement found in attach case');
    process.exit(1);
}
const block = rest.slice(0, returnIdx);

// Must check args.cdp for conflict detection
if (!block.includes('args.cdp')) {
    process.stderr.write('attach block does not check args.cdp for conflicts');
    process.exit(1);
}

// Must exit on conflict
if (!block.includes('process.exit')) {
    process.stderr.write('attach block does not exit on conflict');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_daemon_registers_cdp_flag():
    """daemon program.ts registers --cdp CLI flag via .option()."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/cli-daemon/program.ts', 'utf-8');

// Check for .option('--cdp ...') registration
if (!/\.option\(\s*'--cdp\b/.test(src)) {
    process.stderr.write('--cdp option not registered in daemon program.ts');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_session_passes_cdp_to_daemon():
    """session.ts passes --cdp flag value to daemon arguments."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/cli-client/session.ts', 'utf-8');

// Verify --cdp= is pushed to args array
if (!src.includes('--cdp=')) {
    process.stderr.write('session.ts does not pass --cdp= to daemon args');
    process.exit(1);
}

// Verify it reads from cliArgs.cdp
if (!src.includes('cliArgs.cdp')) {
    process.stderr.write('session.ts does not read cliArgs.cdp');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_config_cdp_endpoint_in_isolation():
    """config.ts maps cdpEndpoint and uses it in browser isolation logic."""
    r = _run_js(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/mcp/config.ts', 'utf-8');

// Verify cdpEndpoint is mapped from CLI options
if (!src.includes('cdpEndpoint')) {
    process.stderr.write('cdpEndpoint not found in config.ts');
    process.exit(1);
}

// Verify it's used in isolation check (result.browser.cdpEndpoint)
if (!src.includes('result.browser.cdpEndpoint')) {
    process.stderr.write('cdpEndpoint not used in browser isolation logic');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_attach_has_extension():
    """SKILL.md documents 'attach --extension' (moved from open)."""
    content = Path(SKILL_MD).read_text()
    assert "attach --extension" in content, \
        "SKILL.md must document 'playwright-cli attach --extension'"


# [pr_diff] fail_to_pass
def test_skill_md_open_no_extension():
    """SKILL.md no longer documents 'open --extension'."""
    content = Path(SKILL_MD).read_text()
    assert "open --extension" not in content, \
        "SKILL.md must not contain 'open --extension' (moved to attach)"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_balanced_braces():
    """Modified TypeScript files have balanced braces."""
    files = [
        f"{CLI_CLIENT}/program.ts",
        f"{CLI_CLIENT}/registry.ts",
        f"{CLI_CLIENT}/session.ts",
        f"{CLI_DAEMON}/commands.ts",
        f"{CLI_DAEMON}/program.ts",
        f"{MCP}/config.ts",
    ]
    for fpath in files:
        content = Path(fpath).read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced braces in {fpath}"


# [static] pass_to_pass
def test_resolve_session_name_has_logic():
    """resolveSessionName function has real logic, not a stub."""
    src = Path(f"{CLI_CLIENT}/registry.ts").read_text()
    assert "resolveSessionName" in src, "resolveSessionName must exist"
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if "function resolveSessionName" in line:
            body_lines = []
            for j in range(i + 1, min(i + 20, len(lines))):
                body_lines.append(lines[j])
                if lines[j].strip().startswith("}"):
                    break
            body = "\n".join(body_lines)
            assert "explicitSessionName" in body or "return" in body, \
                "resolveSessionName must have real logic"
            return
    assert False, "resolveSessionName function not found"
