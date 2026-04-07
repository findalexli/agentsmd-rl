"""
Task: playwright-feat-pwpausecli-exposes-a-playwrightcli
Repo: microsoft/playwright @ 982b9b279557229b12d049ebd3063da408ba5253
PR:   39408

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_modified_files_exist():
    """Key modified TypeScript source files exist and are non-empty."""
    files = [
        "packages/playwright-core/src/server/utils/network.ts",
        "packages/playwright/src/worker/testInfo.ts",
        "packages/playwright/src/program.ts",
        "packages/playwright/src/cli/daemon/daemon.ts",
        "packages/playwright/src/mcp/test/browserBackend.ts",
        "packages/playwright/src/index.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 0, f"{f} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

def test_decorate_server_exported():
    """decorateServer is exported from network.ts so daemon.ts can import it."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright-core/src/server/utils/network.ts', 'utf-8');
if (!/^export\\s+function\\s+decorateServer\\b/m.test(src)) {
    console.error('decorateServer is not exported from network.ts');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_session_config_exported():
    """sessionConfigFromArgs is exported from cli/client/program.ts."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright/src/cli/client/program.ts', 'utf-8');
if (!/^export\\s+function\\s+sessionConfigFromArgs\\b/m.test(src)) {
    console.error('sessionConfigFromArgs is not exported');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_finish_callbacks_is_set():
    """_onDidFinishTestFunctionCallbacks uses a Set to support multiple callbacks."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright/src/worker/testInfo.ts', 'utf-8');

if (!src.includes('_onDidFinishTestFunctionCallbacks')) {
    console.error('Missing _onDidFinishTestFunctionCallbacks (plural) property');
    process.exit(1);
}
if (!/new\\s+Set\\s*</.test(src)) {
    console.error('_onDidFinishTestFunctionCallbacks must be initialized as a Set');
    process.exit(1);
}
if (!/for\\s*\\(\\s*const\\s+\\w+\\s+of\\s+this\\._onDidFinishTestFunctionCallbacks\\s*\\)/.test(src)) {
    console.error('Must iterate over callbacks with for...of');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_pwpause_cli_overrides():
    """PWPAUSE=cli sets timeout=0 and actionTimeout=5000 in program.ts."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync('packages/playwright/src/program.ts', 'utf-8');

if (!/process\\.env\\.PWPAUSE\\s*===?\\s*['"]cli['"]/.test(src)) {
    console.error('program.ts must check for PWPAUSE === "cli"');
    process.exit(1);
}
if (!/overrides\\.timeout\\s*=\\s*0/.test(src)) {
    console.error('PWPAUSE=cli must set overrides.timeout = 0');
    process.exit(1);
}
if (!/actionTimeout\\s*[:=]\\s*5000/.test(src)) {
    console.error('PWPAUSE=cli must set actionTimeout = 5000');
    process.exit(1);
}
if (!/else\\s+if\\s*\\(\\s*process\\.env\\.PWPAUSE\\s*\\)/.test(src)) {
    console.error('Non-cli PWPAUSE must still set pause via else-if');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_run_daemon_for_context_exported():
    """runDaemonForContext is defined and exported from browserBackend.ts."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright/src/mcp/test/browserBackend.ts', 'utf-8');

if (!/export\\s+async\\s+function\\s+runDaemonForContext\\b/.test(src)) {
    console.error('runDaemonForContext must be an exported async function');
    process.exit(1);
}
if (!/process\\.env\\.PWPAUSE/.test(src)) {
    console.error('runDaemonForContext must check PWPAUSE env var');
    process.exit(1);
}
if (!src.includes('startMcpDaemonServer')) {
    console.error('runDaemonForContext must call startMcpDaemonServer');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_daemon_accepts_no_shutdown():
    """startMcpDaemonServer accepts a noShutdown parameter."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright/src/cli/daemon/daemon.ts', 'utf-8');

// Extract the full function signature (spans multiple lines)
const fnMatch = src.match(/export\\s+async\\s+function\\s+startMcpDaemonServer\\s*\\([^)]*\\)/s);
if (!fnMatch) {
    console.error('startMcpDaemonServer export not found');
    process.exit(1);
}
if (!fnMatch[0].includes('noShutdown')) {
    console.error('startMcpDaemonServer must accept a noShutdown parameter');
    process.exit(1);
}
if (!/if\\s*\\(\\s*!noShutdown\\s*\\)/.test(src)) {
    console.error('Must guard browser close shutdown behind !noShutdown check');
    process.exit(1);
}
if (!src.includes('decorateServer')) {
    console.error('daemon.ts must import and use decorateServer');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — SKILL.md and reference doc tests
# ---------------------------------------------------------------------------

def test_skill_md_updated():
    """SKILL.md allowed-tools includes npx/npm and links to playwright-tests reference."""
    r = _run_node("""
import fs from 'node:fs';
const src = fs.readFileSync(
    'packages/playwright/src/skill/SKILL.md', 'utf-8');

// Extract frontmatter
const fmMatch = src.match(/^---\\n([\\s\\S]*?)\\n---/);
if (!fmMatch) {
    console.error('SKILL.md has no frontmatter');
    process.exit(1);
}
const fm = fmMatch[1];

if (!fm.includes('Bash(npx:*)')) {
    console.error('allowed-tools must include Bash(npx:*)');
    process.exit(1);
}
if (!fm.includes('Bash(npm:*)')) {
    console.error('allowed-tools must include Bash(npm:*)');
    process.exit(1);
}
if (!src.includes('references/playwright-tests.md')) {
    console.error('Specific tasks must link to references/playwright-tests.md');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_playwright_tests_reference_created():
    """playwright-tests.md reference doc exists and documents PWPAUSE=cli workflow."""
    r = _run_node("""
import fs from 'node:fs';
const refPath = 'packages/playwright/src/skill/references/playwright-tests.md';
if (!fs.existsSync(refPath)) {
    console.error('references/playwright-tests.md does not exist');
    process.exit(1);
}
const src = fs.readFileSync(refPath, 'utf-8');

if (!src.includes('PWPAUSE=cli')) {
    console.error('Must document PWPAUSE=cli env var');
    process.exit(1);
}
if (!src.includes('playwright-cli')) {
    console.error('Must mention playwright-cli for connecting');
    process.exit(1);
}
if (!/--session=/.test(src)) {
    console.error('Must show --session= flag for connecting to test session');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"
