"""
Task: playwright-cli-split-open-goto-skill
Repo: microsoft/playwright @ 0f542ecb2d37ec5bcf4e987d20ac379ccdba9033
PR:   39164

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
CLI_TEST = Path(REPO) / "tests/mcp/cli-misc.spec.ts"


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
# pass_to_pass (static) — gates
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    for ts_file in [PROGRAM_TS, CLI_TEST]:
        content = ts_file.read_text()
        opens = content.count("{") + content.count("(") + content.count("[")
        closes = content.count("}") + content.count(")") + content.count("]")
        diff = abs(opens - closes)
        assert diff < 5, f"{ts_file.name}: bracket imbalance of {diff}"
        assert len(content) > 100, f"{ts_file.name}: file too short"


def test_program_ts_not_stub():
    """program.ts install function has real logic, not just stubs."""
    src = PROGRAM_TS.read_text()
    assert "async function install" in src
    assert "fs.promises.mkdir" in src
    assert "fs.promises.cp" in src
    assert "console.log" in src


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral: console output formatting
# ---------------------------------------------------------------------------

def test_console_output_emoji_format():
    """Install flow console.log calls render with emoji status prefixes."""
    r = _run_node("""
import fs from 'fs';

const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');
const lines = src.split('\\n');

// Install-flow success messages that should have check-mark prefix
const targets = ['Workspace initialized', 'Skills installed', 'Created default config', 'Found '];
const cwd = '/mock/cwd';
const channel = 'chromium';
const path = { relative: () => '.claude/skills/playwright-cli' };
const skillDestDir = '/mock/dest';

let checked = 0;
for (const line of lines) {
    const t = line.trim();
    if (!t.startsWith('console.log(')) continue;
    if (!targets.some(k => t.includes(k))) continue;

    const first = t.indexOf('`');
    const last = t.lastIndexOf('`');
    if (first === -1 || first === last) continue;

    // Evaluate the template literal with mock variables
    let rendered;
    try {
        const fn = new Function('cwd', 'channel', 'path', 'skillDestDir',
            'return `' + t.slice(first + 1, last) + '`');
        rendered = fn(cwd, channel, path, skillDestDir);
    } catch { continue; }

    if (!rendered.startsWith('\\u2705')) {
        console.error('FAIL: missing check-mark prefix: ' + JSON.stringify(rendered));
        process.exit(1);
    }
    checked++;
}

// Verify console.error uses cross-mark prefix
const errLine = lines.find(l => l.trim().startsWith('console.error(') && l.includes('not found'));
if (!errLine) {
    console.error('FAIL: console.error "not found" line missing');
    process.exit(1);
}
if (!errLine.includes('\\u274C')) {
    console.error('FAIL: error message missing cross-mark prefix');
    process.exit(1);
}

if (checked < 2) {
    console.error('FAIL: expected >=2 prefixed success messages, found ' + checked);
    process.exit(1);
}
console.log('PASS: ' + checked + ' success messages verified');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_console_output_backtick_paths():
    """Workspace init message wraps the directory path in literal backticks."""
    r = _run_node("""
import fs from 'fs';

const src = fs.readFileSync('packages/playwright/src/mcp/terminal/program.ts', 'utf8');
const lines = src.split('\\n');

// Find the workspace-init console.log line
const initLine = lines.find(l =>
    l.trim().startsWith('console.log(') && l.includes('Workspace initialized'));
if (!initLine) {
    console.error('FAIL: no workspace init log found');
    process.exit(1);
}

const t = initLine.trim();
const first = t.indexOf('`');
const last = t.lastIndexOf('`');

// Evaluate the template literal with a mock cwd
const cwd = '/test/workspace';
let rendered;
try {
    const fn = new Function('cwd', 'return `' + t.slice(first + 1, last) + '`');
    rendered = fn(cwd);
} catch (e) {
    console.error('FAIL: could not evaluate template: ' + e.message);
    process.exit(1);
}

// After the fix, rendered output wraps the path in literal backtick characters
// e.g. "... at \\`/test/workspace\\`."
if (!rendered.includes('`/test/workspace`')) {
    console.error('FAIL: path not wrapped in backticks. Got: ' + JSON.stringify(rendered));
    process.exit(1);
}
console.log('PASS: path wrapped in backticks: ' + JSON.stringify(rendered));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral: SKILL.md documentation
# ---------------------------------------------------------------------------

def test_skill_md_open_goto_split():
    """SKILL.md quick start documents 'open' and 'goto' as separate commands."""
    r = _run_node("""
import fs from 'fs';

const content = fs.readFileSync('packages/playwright/src/skill/SKILL.md', 'utf8');

// Extract the Quick start code block
const qsMatch = content.match(/## Quick start[\\s\\S]*?```bash\\n([\\s\\S]*?)```/);
if (!qsMatch) { console.error('FAIL: no Quick start code block'); process.exit(1); }

const commands = qsMatch[1].split('\\n')
    .map(l => l.trim())
    .filter(l => l.startsWith('playwright-cli'));

// 'open' without URL must be present as a standalone command
const hasOpen = commands.some(c => c === 'playwright-cli open');
if (!hasOpen) {
    console.error('FAIL: quick start missing standalone "playwright-cli open"');
    process.exit(1);
}

// 'goto' must be present as a separate navigation command
const hasGoto = commands.some(c => c.startsWith('playwright-cli goto'));
if (!hasGoto) {
    console.error('FAIL: quick start missing "playwright-cli goto"');
    process.exit(1);
}

console.log('PASS: quick start has separate open and goto commands');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_skill_md_close_in_examples():
    """SKILL.md examples (multi-tab, debugging) end with 'playwright-cli close'."""
    r = _run_node("""
import fs from 'fs';

const content = fs.readFileSync('packages/playwright/src/skill/SKILL.md', 'utf8');

// Check multi-tab example
const multiTab = content.match(/## Example: Multi-tab workflow[\\s\\S]*?```bash\\n([\\s\\S]*?)```/);
if (!multiTab) { console.error('FAIL: no Multi-tab workflow example'); process.exit(1); }
if (!multiTab[1].includes('playwright-cli close')) {
    console.error('FAIL: Multi-tab example missing close');
    process.exit(1);
}

// Check first debugging example
const debug = content.match(/## Example: Debugging with DevTools[\\s\\S]*?```bash\\n([\\s\\S]*?)```/);
if (!debug) { console.error('FAIL: no Debugging example'); process.exit(1); }
if (!debug[1].includes('playwright-cli close')) {
    console.error('FAIL: Debugging example missing close');
    process.exit(1);
}

console.log('PASS: examples end with close');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_skill_md_install_syntax():
    """SKILL.md install section uses 'install --skills' instead of 'install-skills'."""
    r = _run_node("""
import fs from 'fs';

const content = fs.readFileSync('packages/playwright/src/skill/SKILL.md', 'utf8');

const installSection = content.match(/### Install[\\s\\S]*?```bash\\n([\\s\\S]*?)```/);
if (!installSection) { console.error('FAIL: no Install code block'); process.exit(1); }

const block = installSection[1];
if (block.includes('install-skills')) {
    console.error('FAIL: still uses old "install-skills" syntax');
    process.exit(1);
}
if (!block.includes('install --skills')) {
    console.error('FAIL: missing "install --skills" in install section');
    process.exit(1);
}

console.log('PASS: install section uses --skills flag');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (repo_tests) — upstream test expectations
# ---------------------------------------------------------------------------

def test_upstream_test_matches_output():
    """Upstream cli-misc test expects backtick-wrapped skill install output."""
    r = _run_node("""
import fs from 'fs';
import path from 'path';

const content = fs.readFileSync('tests/mcp/cli-misc.spec.ts', 'utf8');

// Find the install w/skills test and its toContain assertion
const match = content.match(/install workspace w\\/skills[\\s\\S]*?toContain\\(([\\s\\S]*?)\\)/);
if (!match) { console.error('FAIL: toContain assertion not found'); process.exit(1); }

// Evaluate the assertion argument (a template literal referencing path.sep)
const arg = match[1].trim();
let expected;
try {
    expected = eval(arg);
} catch (e) {
    console.error('FAIL: could not evaluate expect argument: ' + e.message);
    process.exit(1);
}

// After fix, the expected string contains literal backtick characters around the path
if (!expected.includes('`')) {
    console.error('FAIL: expected string has no backtick chars: ' + JSON.stringify(expected));
    process.exit(1);
}

// And ends with backtick + period
if (!expected.endsWith('`.')) {
    console.error('FAIL: expected string does not end with backtick+period: ' + JSON.stringify(expected));
    process.exit(1);
}

console.log('PASS: upstream test expects backtick-wrapped output: ' + JSON.stringify(expected));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
