"""
Task: nextjs-waitforelement-cross-router-timeout
Repo: vercel/next.js @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
PR:   #91918

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TEST_FILE = f"{REPO}/test/e2e/app-dir/interoperability-with-pages/navigation.test.ts"


def _read_test_file() -> str:
    return Path(TEST_FILE).read_text()


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Test file must parse without TypeScript syntax errors."""
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{TEST_FILE}', 'utf8')"],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, f"Cannot read test file: {r.stderr.decode()}"
    src = _read_test_file()
    assert len(src.splitlines()) >= 30, "Test file is too short — likely a stub"


# [static] pass_to_pass
def test_anti_stub_real_waitfor_calls():
    """At least 6 real .waitForElementByCss calls in non-comment code."""
    r = _run_node(
        f"const fs = require('fs'); "
        f"const src = fs.readFileSync('{TEST_FILE}', 'utf8'); "
        f"const lines = src.split('\\n'); "
        f"const codeLines = lines.filter(l => {{ const t = l.trim(); "
        f"return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*'); }}); "
        f"const count = codeLines.join('\\n').split('.waitForElementByCss(').length - 1; "
        f"if (count < 6) {{ console.error('Only ' + count + '/6 calls found'); process.exit(1); }} "
        f"console.log(count + ' waitForElementByCss calls found');"
    )
    assert r.returncode == 0, f"Anti-stub check failed: {r.stderr.strip()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess execution
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_all_waitfor_calls_have_timeout():
    """Every .waitForElementByCss call must have an explicit timeout >= 15000ms."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync(process.argv[1] || 'TESTFILE', 'utf8');
const lines = src.split('\\n');

// Collect non-comment lines with their original line numbers
const codeLines = [];
for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();
    if (!t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*')) {
        codeLines.push({ idx: i, line: lines[i] });
    }
}

let callCount = 0;
let withTimeout = 0;
const failures = [];

for (const { idx, line } of codeLines) {
    if (!line.includes('.waitForElementByCss(')) continue;
    callCount++;

    // Gather multiline context: this line + next 4
    const context = lines.slice(idx, Math.min(idx + 5, lines.length)).join('\\n');

    // Pattern 1: inline { timeout: N }
    const inlineMatch = context.match(/waitForElementByCss\\s*\\([^)]*\\{[^}]*timeout\\s*:\\s*(\\d[\\d_]*)/);
    if (inlineMatch) {
        const val = parseInt(inlineMatch[1].replace(/_/g, ''));
        if (val < 15000) { failures.push(`Line ${idx+1}: timeout=${val} < 15000`); continue; }
        withTimeout++;
        continue;
    }

    // Pattern 2: numeric second arg waitForElementByCss('#sel', 30000)
    const numericMatch = context.match(/waitForElementByCss\\s*\\(\\s*['"`][^'"`]*['"`]\\s*,\\s*(\\d+)\\s*\\)/);
    if (numericMatch) {
        const val = parseInt(numericMatch[1]);
        if (val < 15000) { failures.push(`Line ${idx+1}: timeout=${val} < 15000`); continue; }
        withTimeout++;
        continue;
    }

    // Pattern 3: check for any { timeout: in the context (multiline object)
    const anyTimeout = context.match(/\\{[^}]*timeout\\s*:/);
    if (anyTimeout) {
        const valMatch = context.match(/timeout\\s*:\\s*(\\d[\\d_]*)/);
        if (valMatch) {
            const val = parseInt(valMatch[1].replace(/_/g, ''));
            if (val < 15000) { failures.push(`Line ${idx+1}: timeout=${val} < 15000`); continue; }
        }
        withTimeout++;
        continue;
    }

    failures.push(`Line ${idx+1}: no timeout option found`);
}

if (callCount === 0) { console.error('No .waitForElementByCss calls found'); process.exit(1); }
if (withTimeout !== callCount) {
    console.error(`${withTimeout}/${callCount} have timeout. Issues: ${failures.join('; ')}`);
    process.exit(1);
}
console.log(`All ${callCount} waitForElementByCss calls have timeout >= 15000`);
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Timeout check failed: {r.stderr.strip()}"


# [pr_diff] fail_to_pass
def test_at_least_6_calls_with_timeout():
    """At least 6 waitForElementByCss calls have explicit timeout argument."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const lines = src.split('\\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const codeText = codeLines.join('\\n');

// Count waitForElementByCss calls with a second argument (timeout)
const callsWithArg = codeText.match(/\\.waitForElementByCss\\(\\s*['"`#][^)]*,\\s*(?:\\{|[0-9])/g);
const count = callsWithArg ? callsWithArg.length : 0;

if (count < 6) {
    console.error(`Only ${count}/6 waitForElementByCss calls have timeout arg`);
    process.exit(1);
}
console.log(`${count} calls with timeout found`);
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Call count check failed: {r.stderr.strip()}"


# [pr_diff] fail_to_pass
def test_explanatory_comment_present():
    """A comment near waitForElementByCss explaining why timeout is increased."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const lines = src.split('\\n');

for (let i = 0; i < lines.length; i++) {
    const t = lines[i].trim();
    if (!t.startsWith('//')) continue;
    const lower = t.toLowerCase();

    // Must mention reason (compilation/CI/on-demand/slow/cross-router/dev)
    if (!/(?:compil|on.?demand|cross.?router|dev.?mode|ci\\b|resource|load|slow|flak|build|longer|increas)/.test(lower)) continue;
    // Must mention timeout/wait
    if (!/(?:timeout|wait|time)/.test(lower)) continue;

    // Must be within 10 lines of a waitForElementByCss call
    for (let j = Math.max(0, i - 10); j < Math.min(lines.length, i + 10); j++) {
        if (j !== i && lines[j].includes('waitForElementByCss')) {
            console.log('Explanatory comment found at line ' + (i + 1));
            process.exit(0);
        }
    }
}
console.error('No explanatory comment found near waitForElementByCss about increased timeout');
process.exit(1);
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Comment check failed: {r.stderr.strip()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: test structure preserved
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_all_four_test_cases_present():
    """All 4 navigation test cases (app->pages, pages->app, + back/forward variants) present."""
    src = _read_test_file()
    assert re.search(r"it\s*\(['\"`][^'\"`]*app[^'\"`]*pages", src, re.IGNORECASE), (
        "Missing app->pages test case"
    )
    assert re.search(r"it\s*\(['\"`][^'\"`]*pages[^'\"`]*app", src, re.IGNORECASE), (
        "Missing pages->app test case"
    )
    it_blocks = len(re.findall(r"it\s*\(['\"`]", src))
    assert it_blocks >= 4, f"Only {it_blocks}/4 test cases found"


# [pr_diff] pass_to_pass
def test_infrastructure_intact():
    """Core test infrastructure (describe, webdriver import, createNext) present."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const codeLines = src.split('\\n').filter(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const codeText = codeLines.join('\\n');

if (!/describe\\s*\\(/.test(codeText)) { console.error('Missing describe() block'); process.exit(1); }
if (!codeText.includes('webdriver') || !/import|require/.test(codeText)) { console.error('Missing webdriver import'); process.exit(1); }
if (!codeText.includes('createNext')) { console.error('Missing createNext call'); process.exit(1); }
console.log('Infrastructure intact');
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Infrastructure check failed: {r.stderr.strip()}"


# [pr_diff] pass_to_pass
def test_navigation_logic_intact():
    """Navigation actions (click, back, forward) and element checks present."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const codeLines = src.split('\\n').filter(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
const codeText = codeLines.join('\\n');

if (!/\\.click\\s*\\(/.test(codeText)) { console.error('Missing .click() calls'); process.exit(1); }
if (!/\\.back\\s*\\(/.test(codeText) && !/\\.forward\\s*\\(/.test(codeText)) { console.error('Missing .back()/.forward() calls'); process.exit(1); }
if (!/elementByCss|waitForElementByCss/.test(codeText)) { console.error('Missing element check calls'); process.exit(1); }
console.log('Navigation logic intact');
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Navigation logic check failed: {r.stderr.strip()}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:180 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_settimeout_for_waiting():
    """No setTimeout or manual Promise delays used for waiting (use retry/waitFor helpers)."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const codeLines = src.split('\\n').filter(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
for (const line of codeLines) {
    if (/setTimeout|new\\s+Promise\\s*\\(\\s*\\(?\\s*resolve\\b/.test(line)) {
        console.error('setTimeout/Promise delay found: ' + line.trim());
        process.exit(1);
    }
}
console.log('No setTimeout/Promise delays');
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"setTimeout check failed: {r.stderr.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:194 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_deprecated_check():
    """No deprecated check() usage (use retry() + expect() instead)."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync('TESTFILE', 'utf8');
const codeLines = src.split('\\n').filter(l => {
    const t = l.trim();
    return !t.startsWith('//') && !t.startsWith('*') && !t.startsWith('/*');
});
for (const line of codeLines) {
    if (/(?<!\\w)check\\s*\\(/.test(line)) {
        console.error('Deprecated check() found: ' + line.trim());
        process.exit(1);
    }
}
console.log('No deprecated check() usage');
""".replace("TESTFILE", TEST_FILE)
    )
    assert r.returncode == 0, f"Deprecated check() found: {r.stderr.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:207-220 @ ad65b1bdcf3d10e5213c80bea56a73038bbf1c99
def test_no_inline_fixture_files():
    """createNext/nextTestSetup must use a real fixture directory, not an inline files object."""
    src = _read_test_file()
    assert not re.search(
        r"(?:createNext|nextTestSetup)\s*\(\s*\{[^}]*files\s*:\s*\{",
        src,
        re.DOTALL,
    ), "Inline files object found in createNext/nextTestSetup — use files: __dirname instead"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------


# [repo_ci] pass_to_pass — Repo code formatting check via prettier
def test_repo_prettier_formatting():
    """Repo's prettier formatting check passes on test file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier formatting check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — TypeScript compiler can parse the test file
def test_repo_typescript_syntax():
    """TypeScript compiler can parse test file without syntax errors (pass_to_pass)."""
    # Install TypeScript globally first, then run tsc
    r = subprocess.run(
        ["npm", "install", "-g", "typescript"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Run tsc with --noEmit to check for syntax errors only
    r = subprocess.run(
        ["tsc", "--noEmit", "--skipLibCheck", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    # Exit 0 = no errors, Exit 2 = has errors (type or syntax)
    assert r.returncode != 2, f"TypeScript syntax check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — Test file can be read and parsed by Node.js
def test_repo_node_parseable():
    """Test file is readable and parseable as JavaScript/TypeScript by Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{TEST_FILE}', 'utf8')"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Node.js file read failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass — Import statements use valid syntax
def test_repo_import_syntax():
    """Test file has valid import/export syntax (pass_to_pass)."""
    r = _run_node(
        f"""
const fs = require('fs');
const src = fs.readFileSync('{TEST_FILE}', 'utf8');

// Check for valid import statement patterns
const importPattern = /import\\s+(?:(?:{{[^}}]*}}|\\*\\s+as\\s+\\w+|\\w+)\\s+from\\s+)?['"`][^'"`]+['"`]|import\\s*\\(['"`][^'"`]+['"`]\\)/g;
const imports = src.match(importPattern) || [];

// Check for valid export patterns
const exportPattern = /export\\s+(?:default\\s+|(?:const|let|var|function|class|interface|type|enum)\\s+\\w+|{{[^}}]*}})/g;
const exports = src.match(exportPattern) || [];

// Check for unclosed string literals in import/export lines
const lines = src.split('\\n');
for (let i = 0; i < lines.length; i++) {{
    const line = lines[i];
    // Check for imports that don't close properly
    if (line.trim().startsWith('import')) {{
        const singleQuotes = (line.match(/'/g) || []).length;
        const doubleQuotes = (line.match(/"/g) || []).length;
        const backticks = (line.match(/`/g) || []).length;
        // String quotes should be balanced within the line
        if (singleQuotes % 2 !== 0 && doubleQuotes % 2 !== 0 && backticks % 2 !== 0) {{
            console.error('Unclosed string in import at line ' + (i+1));
            process.exit(1);
        }}
    }}
}}

console.log('Found ' + imports.length + ' imports, ' + exports.length + ' exports');
console.log('Import/export syntax OK');
"""
    )
    assert r.returncode == 0, f"Import syntax check failed: {r.stderr.strip()}"
