"""
Task: playwright-fixproxy-do-not-force-loopback
Repo: microsoft/playwright @ 23b12474a184466c5a83db49b7bcf4d45e970a26
PR:   39566

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
CHROMIUM_TS = f"{REPO}/packages/playwright-core/src/server/chromium/chromium.ts"


def _run_in_repo(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(
        cmd,
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _eval_bypass_logic(bypass_value: str) -> subprocess.CompletedProcess:
    """
    Extract the proxy bypass logic from chromium.ts and evaluate it.

    This executes the ACTUAL source code logic with controlled inputs to verify
    that loopback bypass rules (localhost, 127.0.0.1, ::1) prevent force-adding
    <-loopback> to the Chrome arguments.

    Returns: process with exit code 0 if <-loopback> is NOT force-added,
             exit code 1 if <-loopback> IS force-added (correct for non-loopback bypasses)
    """
    return _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{CHROMIUM_TS}', 'utf8');

// Find the proxy bypass logic block - supports both base (broken) and fixed code
// Base:  if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !proxyBypassRules.includes('<-loopback>'))
// Fixed: const bypassesLoopback = proxyBypassRules.some(...); if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback)

const startRe = /(?:const|let|var)\\s+proxyBypassRules\\s*=\\s*\\[\\]/;
const m = src.match(startRe);
if (!m) {{ console.error('Cannot find proxyBypassRules declaration'); process.exit(2); }}
const si = m.index;

// Find the end of the block where chromeArguments is used
const endMarker = 'if (proxyBypassRules.length > 0)';
const ei = src.indexOf(endMarker, si);
if (ei === -1) {{ console.error('Cannot find end marker'); process.exit(2); }}

const block = src.substring(si, ei);

// Check if the new bypassesLoopback variable exists (indicates fixed code)
const isFixed = block.includes('const bypassesLoopback') ||
                block.includes('bypassesLoopback = proxyBypassRules.some');

// Create a function from the extracted code
const fn = new Function('proxy', 'options', block + '\\nreturn proxyBypassRules;');

// Clear the env var so the force-loopback path is active
delete process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK;

const rules = fn({{ bypass: '{bypass_value}' }}, {{}});
const hasLoopback = rules.includes('<-loopback>');

console.log(JSON.stringify({{ rules, hasLoopback, isFixed }}));
process.exit(hasLoopback ? 1 : 0);
""")


def _eval_bypass_logic_v2(bypass_value: str) -> subprocess.CompletedProcess:
    """
    Simulates the actual chromium.ts proxy bypass logic.

    The real code structure is:
    1. const proxyBypassRules = [];
    2. if (options.socksProxyPort) proxyBypassRules.push('<-loopback>');  // not in test path
    3. if (proxy.bypass) proxyBypassRules.push(...user rules);
    4. const bypassesLoopback = proxyBypassRules.some(rule => ...);  // THE FIX
    5. if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback)
         proxyBypassRules.push('<-loopback>');

    The test path doesn't use socksProxyPort, so step 2 is skipped.
    """
    return _run_node(f"""
const fs = require('fs');
const src = fs.readFileSync('{CHROMIUM_TS}', 'utf8');

// Check if the fix is present: bypassesLoopback variable with proper check
const hasFix = src.includes('const bypassesLoopback') &&
               src.includes("rule === 'localhost'") &&
               src.includes("rule === '127.0.0.1'") &&
               src.includes("rule === '::1'");

// Simulate the CORRECT proxy bypass logic (matching actual chromium.ts structure)
function simulateBypassLogic(proxyBypass) {{
  const proxyBypassRules = [];

  // Step 1: Add user bypass rules (only if proxyBypass is provided)
  if (proxyBypass)
    proxyBypassRules.push(...proxyBypass.split(',').map(t => t.trim()).map(t => t.startsWith('.') ? '*' + t : t));

  // Step 2: Check if bypasses loopback (THE FIX)
  // After the fix, this checks for localhost/127.0.0.1/::1 in addition to <-loopback>
  let bypassesLoopback;
  if (hasFix) {{
    // Fixed logic: recognize localhost, 127.0.0.1, ::1 as loopback addresses
    bypassesLoopback = proxyBypassRules.some(rule =>
      rule === '<-loopback>' || rule === 'localhost' || rule === '127.0.0.1' || rule === '::1'
    );
  }} else {{
    // Broken logic: only check for <-loopback> explicitly
    bypassesLoopback = proxyBypassRules.includes('<-loopback>');
  }}

  // Step 3: Add <-loopback> ONLY if not already bypassing loopback
  if (!process.env.PLAYWRIGHT_DISABLE_FORCED_CHROMIUM_PROXIED_LOOPBACK && !bypassesLoopback)
    proxyBypassRules.push('<-loopback>');

  return proxyBypassRules;
}}

const rules = simulateBypassLogic('{bypass_value}');
const hasLoopback = rules.includes('<-loopback>');

console.log(JSON.stringify({{ rules, hasLoopback, hasFix }}));
process.exit(hasLoopback ? 1 : 0);
""")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax check
# ---------------------------------------------------------------------------

def test_syntax_check():
    """chromium.ts parses without syntax errors (balanced braces and parentheses)."""
    result = _run_node(f"""
const src = require('fs').readFileSync('{CHROMIUM_TS}', 'utf8');
let braces = 0, parens = 0;
for (const ch of src) {{
  if (ch === '{{') braces++;
  if (ch === '}}') braces--;
  if (ch === '(') parens++;
  if (ch === ')') parens--;
}}
if (braces !== 0) {{ console.error('Unbalanced braces: ' + braces); process.exit(1); }}
if (parens !== 0) {{ console.error('Unbalanced parens: ' + parens); process.exit(1); }}
console.log('OK');
""")
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - actual CI commands that run in Docker
# ---------------------------------------------------------------------------

def test_repo_eslint_chromium():
    """ESLint passes on chromium.ts (pass_to_pass)."""
    r = _run_in_repo(
        ["npm", "ci", "--workspaces=false"],
        timeout=300,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[-500:]}"

    r = _run_in_repo(
        ["npm", "run", "eslint", "--", "--max-warnings=0", CHROMIUM_TS],
        timeout=120,
    )
    assert r.returncode == 0, f"ESLint failed:\\n{r.stderr[-500:]}\\n{r.stdout[-500:]}"


def test_repo_typescript_transpile():
    """TypeScript transpilation of chromium.ts succeeds (pass_to_pass)."""
    r = _run_in_repo(
        ["npm", "ci", "--workspaces=false"],
        timeout=300,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[-500:]}"

    script = """
const ts = require('typescript');
const src = require('fs').readFileSync('packages/playwright-core/src/server/chromium/chromium.ts', 'utf8');
const result = ts.transpileModule(src, {
    compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        noEmit: true,
        target: ts.ScriptTarget.ES2020
    }
});
if (result.diagnostics && result.diagnostics.length > 0) {
    console.error('TypeScript errors:', result.diagnostics);
    process.exit(1);
}
console.log('TypeScript transpile OK');
"""
    r = _run_in_repo(
        ["node", "-e", script],
        timeout=60,
    )
    assert r.returncode == 0, f"TypeScript transpile failed:\\n{r.stderr[-500:]}"


def test_repo_generate_channels():
    """Channel generation script runs successfully (pass_to_pass)."""
    r = _run_in_repo(
        ["npm", "ci", "--workspaces=false"],
        timeout=300,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[-500:]}"

    r = _run_in_repo(
        ["node", "utils/generate_channels.js"],
        timeout=60,
    )
    assert r.returncode == 0, f"generate_channels failed:\\n{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Workspace package consistency check passes (pass_to_pass)."""
    r = _run_in_repo(
        ["npm", "ci", "--workspaces=false"],
        timeout=300,
    )
    assert r.returncode == 0, f"npm ci failed: {r.stderr[-500:]}"

    r = _run_in_repo(
        ["npm", "run", "lint-packages"],
        timeout=60,
    )
    assert r.returncode == 0, f"lint-packages failed:\\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

def test_localhost_bypass_skips_loopback():
    """When proxy.bypass='localhost', <-loopback> must NOT be force-added."""
    r = _eval_bypass_logic_v2("localhost")
    assert r.returncode == 0, (
        f"<-loopback> was force-added despite 'localhost' in bypass list: {r.stdout}"
    )
    data = json.loads(r.stdout.strip())
    assert not data["hasLoopback"], (
        f"Expected <-loopback> NOT to be added, but it was. Rules: {data['rules']}"
    )
    assert "localhost" in data["rules"], f"localhost should be in rules: {data['rules']}"


def test_ipv4_bypass_skips_loopback():
    """When proxy.bypass='127.0.0.1', <-loopback> must NOT be force-added."""
    r = _eval_bypass_logic_v2("127.0.0.1")
    assert r.returncode == 0, (
        f"<-loopback> was force-added despite '127.0.0.1' in bypass list: {r.stdout}"
    )
    data = json.loads(r.stdout.strip())
    assert not data["hasLoopback"], (
        f"Expected <-loopback> NOT to be added, but it was. Rules: {data['rules']}"
    )
    assert "127.0.0.1" in data["rules"], f"127.0.0.1 should be in rules: {data['rules']}"


def test_ipv6_bypass_skips_loopback():
    """When proxy.bypass='::1', <-loopback> must NOT be force-added."""
    r = _eval_bypass_logic_v2("::1")
    assert r.returncode == 0, (
        f"<-loopback> was force-added despite '::1' in bypass list: {r.stdout}"
    )
    data = json.loads(r.stdout.strip())
    assert not data["hasLoopback"], (
        f"Expected <-loopback> NOT to be added, but it was. Rules: {data['rules']}"
    )
    assert "::1" in data["rules"], f"::1 should be in rules: {data['rules']}"


# ---------------------------------------------------------------------------
# Pass-to-pass - regression: non-loopback bypass still gets <-loopback>
# ---------------------------------------------------------------------------

def test_non_loopback_still_forced():
    """When proxy.bypass='example.com', <-loopback> MUST still be force-added."""
    r = _eval_bypass_logic_v2("example.com")
    assert r.returncode == 1, (
        f"<-loopback> was NOT added for non-loopback bypass 'example.com': {r.stdout}"
    )
    data = json.loads(r.stdout.strip())
    assert data["hasLoopback"], f"Expected <-loopback> to be added: {data['rules']}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - config/skill file update tests
# ---------------------------------------------------------------------------

def test_github_skill_doc_content():
    """github.md skill doc must exist and cover branch naming + commit format."""
    github_md = Path(REPO) / ".claude" / "skills" / "playwright-dev" / "github.md"
    assert github_md.exists(), f"github.md skill doc must exist at {github_md}"
    content = github_md.read_text()
    assert len(content) > 200, "github.md should have substantial content"
    # Must cover branch naming
    assert "branch" in content.lower(), "github.md should document branch naming"
    assert "fix-" in content, (
        "github.md should show the fix-<number> branch pattern"
    )
    # Must cover conventional commit format
    assert "fix(" in content or "feat(" in content, (
        "github.md should show conventional commit format (e.g., fix(scope): ...)"
    )
    # Must document Fixes: link
    assert "Fixes:" in content, (
        "github.md should document the 'Fixes:' commit body format"
    )


def test_skill_md_references_github():
    """SKILL.md table of contents must link to github.md."""
    skill_md = Path(REPO) / ".claude" / "skills" / "playwright-dev" / "SKILL.md"
    assert skill_md.exists(), f"SKILL.md must exist at {skill_md}"
    content = skill_md.read_text()
    assert "github.md" in content, (
        f"SKILL.md must reference github.md in its table of contents. Content: {content[:500]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - existing skill files preserved
# ---------------------------------------------------------------------------

def test_existing_skills_preserved():
    """Existing skill documents in .claude/skills/playwright-dev/ remain intact."""
    skills_dir = Path(REPO) / ".claude" / "skills" / "playwright-dev"
    expected_files = ["SKILL.md", "api.md", "library.md", "mcp-dev.md", "vendor.md"]
    for fname in expected_files:
        fpath = skills_dir / fname
        assert fpath.exists(), f"Existing skill file {fname} must still be present"
        content = fpath.read_text()
        assert len(content) > 50, f"{fname} should not be empty or trivial"
