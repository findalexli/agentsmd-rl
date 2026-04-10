"""
Task: playwright-featmcp-add-cdp-option-to
Repo: playwright @ 9d81a6754d9426295ac10bd33278fb2af476c8a9
PR:   microsoft/playwright#40017

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_npm_ci():
    """Install dependencies."""
    r = subprocess.run(
        ["npm", "ci", "--include-dev"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"


def _run_build():
    """Build the repo."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD commands that should pass on base commit
# ---------------------------------------------------------------------------


def test_repo_eslint():
    """Repo's ESLint passes on the codebase (pass_to_pass)."""
    _run_npm_ci()
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    _run_npm_ci()
    _run_build()


def test_repo_lint_packages():
    """Repo's package linting passes (pass_to_pass)."""
    _run_npm_ci()
    _run_build()
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass)."""
    _run_npm_ci()
    _run_build()
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-tests failed:\n{r.stderr[-500:]}"


def test_repo_test_types():
    """Repo's TypeScript type checking passes (pass_to_pass)."""
    _run_npm_ci()
    _run_build()
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"test-types failed:\n{r.stderr[-500:]}"


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a JavaScript snippet via Node.js in the repo directory."""
    script_path = Path(REPO) / "_eval_test.mjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_global_options_includes_cdp():
    """The globalOptions array in program.ts must include 'cdp'."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-client/program.ts', 'utf8');

// Extract the globalOptions array literal and evaluate it
const match = src.match(/const\s+globalOptions[^=]*=\s*\[([\s\S]*?)\]/);
if (!match) { console.error('Cannot find globalOptions array'); process.exit(1); }

// Parse quoted identifiers from the array
const items = match[1].match(/'(\w+)'/g);
if (!items) { console.error('Cannot parse array items'); process.exit(1); }
const options = items.map(s => s.replace(/'/g, ''));

if (!options.includes('cdp')) {
    console.error('globalOptions does not include cdp. Found: ' + options.join(', '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"globalOptions missing 'cdp': {r.stderr}"
    assert "PASS" in r.stdout


def test_attach_schema_has_cdp_option():
    """Attach command Zod schema declares a 'cdp' string option."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8');

// Find attach declareCommand block
const attachIdx = src.indexOf('const attach');
if (attachIdx === -1) { console.error('No attach command found'); process.exit(1); }
const slice = src.slice(attachIdx, attachIdx + 2000);

// Find the options z.object block within attach
const optMatch = slice.match(/options:\s*z\.object\(\{([\s\S]*?)\}\)/);
if (!optMatch) { console.error('No options block in attach'); process.exit(1); }
const optionsBlock = optMatch[1];

// Verify cdp option exists with z.string().optional()
if (!/cdp:\s*z\.string\(\)\.optional\(\)/.test(optionsBlock)) {
    console.error('attach options missing cdp: z.string().optional()');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"attach schema missing cdp option: {r.stderr}"
    assert "PASS" in r.stdout


def test_attach_name_arg_optional():
    """Attach command's 'name' argument is z.string().optional()."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8');

const attachIdx = src.indexOf('const attach');
if (attachIdx === -1) { console.error('No attach command found'); process.exit(1); }
const slice = src.slice(attachIdx, attachIdx + 2000);

// Find the args z.object block
const argsMatch = slice.match(/args:\s*z\.object\(\{([\s\S]*?)\}\)/);
if (!argsMatch) { console.error('No args block in attach'); process.exit(1); }

// Verify name is optional
if (!/name:\s*z\.string\(\)\.optional\(\)/.test(argsMatch[1])) {
    console.error('attach name arg is not z.string().optional()');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"attach name arg not optional: {r.stderr}"
    assert "PASS" in r.stdout


def test_open_no_extension_option():
    """The open command must NOT have an 'extension' option (moved to attach)."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8');

// Find open command block (up to where attach starts)
const openIdx = src.indexOf('const open');
if (openIdx === -1) { console.error('No open command found'); process.exit(1); }
const attachIdx = src.indexOf('const attach', openIdx + 10);
const openBlock = src.slice(openIdx, attachIdx > -1 ? attachIdx : openIdx + 3000);

// Find the options z.object block within open
const optMatch = openBlock.match(/options:\s*z\.object\(\{([\s\S]*?)\}\)/);
if (!optMatch) { console.error('No options block in open'); process.exit(1); }

if (optMatch[1].includes('extension')) {
    console.error('open command still has extension option — should be moved to attach');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"open still has extension: {r.stderr}"
    assert "PASS" in r.stdout


def test_attach_has_extension_option():
    """The attach command must have an 'extension' option."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-daemon/commands.ts', 'utf8');

const attachIdx = src.indexOf('const attach');
if (attachIdx === -1) { console.error('No attach command found'); process.exit(1); }
const slice = src.slice(attachIdx, attachIdx + 2000);

const optMatch = slice.match(/options:\s*z\.object\(\{([\s\S]*?)\}\)/);
if (!optMatch) { console.error('No options block in attach'); process.exit(1); }

if (!optMatch[1].includes('extension')) {
    console.error('attach command missing extension option');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"attach missing extension: {r.stderr}"
    assert "PASS" in r.stdout


def test_attach_rejects_target_with_flags():
    """Attach handler errors when target name used with --cdp/--endpoint/--extension."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-client/program.ts', 'utf8');

// Find the attach case handler
const attachIdx = src.indexOf("case 'attach':");
if (attachIdx === -1) { console.error('No attach case found'); process.exit(1); }
const returnIdx = src.indexOf('return;', attachIdx);
const attachBlock = src.slice(attachIdx, returnIdx > -1 ? returnIdx + 10 : attachIdx + 1500);

// The fix adds conflict detection: target name + cdp/endpoint/extension
if (!attachBlock.includes('args.cdp')) {
    console.error('attach handler does not reference args.cdp for conflict check');
    process.exit(1);
}
if (!attachBlock.includes('cannot use target name')) {
    console.error('attach handler missing error message for target+flags conflict');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"attach conflict check missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_session_forwards_cdp():
    """Session must forward --cdp argument to daemon process."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/cli-client/session.ts', 'utf8');

// Check for cliArgs.cdp guard and --cdp= push
const hasCdpCheck = /cliArgs\.cdp/.test(src);
const hasCdpPush = /--cdp=/.test(src);

if (!hasCdpCheck) { console.error('session.ts missing cliArgs.cdp check'); process.exit(1); }
if (!hasCdpPush) { console.error('session.ts missing --cdp= arg push'); process.exit(1); }

// Verify --cdp= is pushed before --endpoint= (matches the PR ordering)
const cdpPos = src.indexOf('--cdp=');
const endpointPos = src.indexOf('--endpoint=');
if (endpointPos > -1 && cdpPos > endpointPos) {
    console.error('--cdp= should appear before --endpoint= in session arg list');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"session cdp forwarding issue: {r.stderr}"
    assert "PASS" in r.stdout


def test_config_cdp_endpoint():
    """Config must pass cdpEndpoint from options.cdp and include it in isolated check."""
    r = _run_node(r"""
import { readFileSync } from 'fs';
const src = readFileSync('packages/playwright-core/src/tools/mcp/config.ts', 'utf8');

// Check cdpEndpoint is passed in configFromCLIOptions
if (!/cdpEndpoint\s*:\s*options\.cdp/.test(src)) {
    console.error('config.ts missing cdpEndpoint: options.cdp');
    process.exit(1);
}

// Check cdpEndpoint is considered in the isolated browser check
const lines = src.split('\n');
const isolatedLines = lines.filter(l => l.includes('.isolated') && l.includes('='));
const joined = isolatedLines.join(' ');
if (!joined.includes('cdpEndpoint')) {
    console.error('isolated browser check does not consider cdpEndpoint');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"config cdpEndpoint issue: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — SKILL.md documentation
# ---------------------------------------------------------------------------

def test_skill_extension_under_attach():
    """SKILL.md documents 'attach --extension' and no longer has 'open --extension'."""
    content = (Path(REPO) / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md").read_text()
    assert "attach --extension" in content, \
        "SKILL.md must document 'playwright-cli attach --extension'"
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "open --extension" in line:
            assert False, f"SKILL.md still has 'open --extension' at line {i + 1}"
