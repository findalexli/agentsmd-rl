"""
Task: cypress-grep-env-to-expose-migration
Repo: cypress-io/cypress @ eb60ddcec6d92dad8ba1a1d776b249171384aa5e
PR:   33242

Migrates @cypress/grep from Cypress.env() to Cypress.expose() API.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/cypress"


def _run_node(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files have balanced braces and valid structure."""
    for relpath in [
        "npm/grep/src/plugin.ts",
        "npm/grep/src/register.ts",
    ]:
        src = Path(REPO) / relpath
        assert src.exists(), f"{relpath} must exist"
        content = src.read_text()
        assert content.count("{") == content.count("}"), \
            f"{relpath} has unbalanced braces"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI tests that execute actual repo code
# ---------------------------------------------------------------------------

def test_repo_utils_module():
    """Utils module functions work correctly (pass_to_pass)."""
    test_code = f"""
import {{ parseGrep, shouldTestRun, parseTagsGrep, parseTitleGrep }} from "{REPO}/npm/grep/src/utils.ts";

const parsed = parseGrep("hello world");
if (!parsed || !parsed.title || parsed.title.length !== 1) {{
  console.error("parseGrep failed");
  process.exit(1);
}}

const result = shouldTestRun(parsed, "hello world test");
if (result !== true) {{
  console.error("shouldTestRun failed");
  process.exit(1);
}}

const tags = parseTagsGrep("@smoke @critical");
if (!tags || tags.length !== 2) {{
  console.error("parseTagsGrep failed");
  process.exit(1);
}}

const title = parseTitleGrep("test title");
if (!title || title.title !== "test title") {{
  console.error("parseTitleGrep failed");
  process.exit(1);
}}

console.log("PASS");
"""
    test_file = "/tmp/test_utils_module.ts"
    Path(test_file).write_text(test_code)
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", test_file],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0
    assert "PASS" in r.stdout


def test_repo_typescript_syntax():
    """Modified TypeScript files have valid syntax (pass_to_pass)."""
    for relpath in ["npm/grep/src/plugin.ts", "npm/grep/src/register.ts", "npm/grep/src/utils.ts"]:
        src_path = Path(REPO) / relpath
        test_code = f"""
import * as fs from "fs";
const content = fs.readFileSync("{src_path}", "utf8");
if (!content.includes("export")) {{
  console.error("missing export");
  process.exit(1);
}}
console.log("PASS");
"""
        test_file = "/tmp/test_syntax.ts"
        Path(test_file).write_text(test_code)
        r = subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", test_file],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0
        assert "PASS" in r.stdout


def test_repo_package_json_valid():
    """package.json is valid JSON with required fields (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", f"""
const pkg = require("{REPO}/npm/grep/package.json");
if (!pkg.name) {{ console.error("missing name"); process.exit(1); }}
if (!pkg.scripts) {{ console.error("missing scripts"); process.exit(1); }}
if (!pkg.dependencies) {{ console.error("missing dependencies"); process.exit(1); }}
console.log("PASS");
        """],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0
    assert "PASS" in r.stdout

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

def test_plugin_reads_from_expose():
    """plugin() reads grep config from config.expose, ignores config.env."""
    r = _run_node(r"""
const fs = require('fs');
const { execSync } = require('child_process');
const srcBase = process.cwd() + '/npm/grep/src';

if (!fs.existsSync(srcBase + '/plugin.ts')) {
  throw new Error('plugin.ts not found at ' + srcBase);
}

// --- Set up isolated test environment ---
const tmpDir = '/tmp/_grep_plugin_test';
fs.rmSync(tmpDir, { recursive: true, force: true });
fs.mkdirSync(tmpDir + '/src', { recursive: true });

// Copy source files, adding .ts extensions to local imports for ESM resolution
function copyTS(name) {
  let src = fs.readFileSync(srcBase + '/' + name, 'utf8');
  // Fix bare relative imports: './utils' -> './utils.ts'
  src = src.replace(/from\s+'\.\/([^']+)'/g, (m, p) =>
    p.endsWith('.ts') ? m : `from './${p}.ts'`
  );
  fs.writeFileSync(tmpDir + '/src/' + name, src);
}
copyTS('plugin.ts');
copyTS('utils.ts');

// Provide version.ts (may be auto-generated in the monorepo)
const versionPath = srcBase + '/version.ts';
if (fs.existsSync(versionPath)) {
  let vSrc = fs.readFileSync(versionPath, 'utf8');
  vSrc = vSrc.replace(/from\s+'\.\/([^']+)'/g, (m, p) =>
    p.endsWith('.ts') ? m : `from './${p}.ts'`
  );
  fs.writeFileSync(tmpDir + '/src/version.ts', vSrc);
} else {
  fs.writeFileSync(tmpDir + '/src/version.ts',
    "export const version = '0.0.0';\n");
}

// Create mock modules to avoid heavy dependencies
fs.writeFileSync(tmpDir + '/src/mock_globby.ts', `
export function sync(pattern: string | string[], options?: any): string[] {
  return ['test.cy.ts'];
}
`);

fs.writeFileSync(tmpDir + '/src/mock_find_test_names.ts', `
export function getTestNames(source: string): any {
  return { suiteNames: [], testNames: [] };
}
`);

// Modify plugin.ts to use mocks
let pluginSrc = fs.readFileSync(tmpDir + '/src/plugin.ts', 'utf8');
// Replace heavy imports with mocks
pluginSrc = pluginSrc.replace(
  "import { sync as globbySync } from 'globby'",
  "import { sync as globbySync } from './mock_globby.ts'"
);
pluginSrc = pluginSrc.replace(
  "import { getTestNames } from 'find-test-names'",
  "import { getTestNames } from './mock_find_test_names.ts'"
);
// Replace JSON import with a simple constant
pluginSrc = pluginSrc.replace(
  /import { version } from '..\/package\.json'/,
  "const version = '0.0.0'"
);
fs.writeFileSync(tmpDir + '/src/plugin.ts', pluginSrc);

// Install only debug (lightweight dependency)
execSync('npm init -y 2>&1', { cwd: tmpDir, stdio: 'pipe' });
execSync('npm install debug 2>&1', { cwd: tmpDir, stdio: 'pipe', timeout: 60000 });

// Create behavioral test that exercises the actual plugin function
fs.writeFileSync(tmpDir + '/src/test.ts', `
import { plugin } from './plugin.ts';

const logs = [];
const origLog = console.log;
console.log = (...a) => logs.push(a.join(' '));

// Test 1: env-only config (old API) must be returned unchanged.
// After migration, plugin checks config.expose, so env-only input
// hits the early-return path and is a no-op.
const envConfig = { env: { grep: 'login' }, specPattern: '**/*.cy.ts' };
const envResult = plugin(envConfig);
if (envResult !== envConfig) {
  throw new Error(
    'plugin must return envConfig unchanged when only env is present (not expose)'
  );
}
const envLogs = [...logs];

// Test 2: expose config (new API) must be processed — grep value is read
// and logged to console.
logs.length = 0;
plugin({ expose: { grep: 'login' }, specPattern: '**/*.cy.ts' });
const exposeLogs = [...logs];

console.log = origLog;

if (!exposeLogs.some(l => l.includes('login'))) {
  throw new Error(
    'plugin did not read expose config — no grep log output. ' +
    'Logs: ' + JSON.stringify(exposeLogs)
  );
}
if (envLogs.some(l => l.includes('login'))) {
  throw new Error(
    'plugin incorrectly processed env config (should only use expose). ' +
    'Logs: ' + JSON.stringify(envLogs)
  );
}
console.log('PASS');
`);

// Run with Node 22 built-in TypeScript stripping
let out;
try {
  out = execSync(
    'node --experimental-strip-types --no-warnings src/test.ts',
    { cwd: tmpDir, stdio: 'pipe', timeout: 30000 }
  );
} catch (e1) {
  throw new Error(
    'Plugin test failed: ' + (e1.stderr?.toString() || e1.message)
  );
}
console.log(out.toString().trim());
""", timeout=90)
    assert r.returncode == 0, f"Plugin behavioral test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


def test_register_calls_expose():
    """register.ts uses Cypress.expose() instead of Cypress.env()."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('npm/grep/src/register.ts', 'utf8');

if (!src.includes('Cypress.expose(')) {
  throw new Error('register.ts must call Cypress.expose()');
}
if (src.includes('Cypress.env(')) {
  throw new Error('register.ts must not call Cypress.env() — use Cypress.expose()');
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_peer_dep_updated():
    """package.json peerDependencies.cypress requires >=15.10.0."""
    r = _run_node("""
const pkg = require('./npm/grep/package.json');
const peer = (pkg.peerDependencies || {}).cypress || '';
const m = peer.match(/(\\d+)\\.(\\d+)/);
if (!m) throw new Error('No version in peerDep: ' + peer);
const [maj, min] = [parseInt(m[1]), parseInt(m[2])];
if (maj < 15 || (maj === 15 && min < 10)) {
  throw new Error('peerDep cypress must be >=15.10.0, got: ' + peer);
}
console.log('PASS: ' + peer);
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_package_json_scripts_use_expose():
    """package.json npm scripts use --expose instead of --env for grep args."""
    r = _run_node("""
const pkg = require('./npm/grep/package.json');
const scripts = Object.entries(pkg.scripts || {})
  .filter(([_, cmd]) =>
    cmd.includes('cypress') &&
    (cmd.includes('grep') || cmd.includes('burn') || cmd.includes('Tags') || cmd.includes('Untagged'))
  );

if (scripts.length < 5) {
  throw new Error('Expected >=5 grep-related scripts, found ' + scripts.length);
}
for (const [name, cmd] of scripts) {
  if (cmd.includes('--env ')) {
    throw new Error('Script "' + name + '" still uses --env: ' + cmd);
  }
}
if (!scripts.some(([_, cmd]) => cmd.includes('--expose'))) {
  throw new Error('No scripts use --expose');
}
console.log('PASS: ' + scripts.length + ' scripts validated');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

def test_plugin_has_real_logic():
    """plugin.ts must contain real filtering logic, not just a stub."""
    src = (Path(REPO) / "npm/grep/src/plugin.ts").read_text()
    assert "grepFilterSpecs" in src, "plugin must handle grepFilterSpecs"
    assert "shouldTestRun" in src, "plugin must call shouldTestRun"
    assert "specPattern" in src, "plugin must handle specPattern"


def test_register_has_real_logic():
    """register.ts must contain real registration logic, not just a stub."""
    src = (Path(REPO) / "npm/grep/src/register.ts").read_text()
    assert "shouldTestRun" in src, "register must call shouldTestRun"
    assert "parseGrep" in src, "register must call parseGrep"
    assert "grepBurn" in src, "register must handle grepBurn"
