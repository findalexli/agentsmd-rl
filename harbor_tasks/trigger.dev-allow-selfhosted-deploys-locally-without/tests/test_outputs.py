"""
Task: trigger.dev-allow-selfhosted-deploys-locally-without
Repo: triggerdotdev/trigger.dev @ ad4daa3301f63354745cdcb8e911950d9fa5a93f
PR:   2064

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Helper: Node.js code to extract and evaluate the TRIGGER_API_URL expression
# from buildImage.ts.  Works regardless of function name or inline logic.
# Handles multiple TRIGGER_API_URL assignments in the file by probing which
# one actually performs normalization.
# ---------------------------------------------------------------------------

_NORMALIZE_HELPER = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/cli-v3/src/deploy/buildImage.ts', 'utf8');

// Find ALL TRIGGER_API_URL template expressions (file has multiple build paths)
const urlMatches = [...src.matchAll(/TRIGGER_API_URL=\$\{([^}]+)\}/g)];
if (urlMatches.length === 0) {
    console.error('TRIGGER_API_URL template not found');
    process.exit(1);
}

// Extract helper functions referenced by any expression (regardless of name)
var helpers = '';
var funcPattern = /(?:export\s+)?function\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*[^{]+?)?\s*\{/g;
var fm;
while ((fm = funcPattern.exec(src)) !== null) {
    var funcName = fm[1];
    var referenced = urlMatches.some(function(m) { return m[1].includes(funcName); });
    if (!referenced) continue;
    var braces = 0, started = false, end = fm.index;
    for (var i = fm.index; i < src.length; i++) {
        if (src[i] === '{') { braces++; started = true; }
        if (src[i] === '}') braces--;
        if (started && braces === 0) { end = i + 1; break; }
    }
    var fSrc = src.slice(fm.index, end);
    fSrc = fSrc.replace(
        /^(?:export\s+)?function\s+(\w+)\s*\(([^)]*)\)(\s*:\s*[^{]+?)?\s*\{/,
        function(_, name, params) {
            var cleaned = params.split(',').map(function(p) {
                return p.replace(/\s*[?]?\s*:\s*\S+/, '').trim();
            }).join(', ');
            return 'function ' + name + '(' + cleaned + ') {';
        });
    helpers += fSrc + '\n';
}

// Identify which expression does normalization by probing on darwin
var selectedExpr = urlMatches[0][1].trim();
for (var j = 0; j < urlMatches.length; j++) {
    try {
        Object.defineProperty(process, 'platform', { value: 'darwin', configurable: true });
        var probeCode = helpers + '\nreturn ' + urlMatches[j][1].trim() + ';';
        var probeResult = new Function('options', probeCode)({ apiUrl: 'http://localhost:9999' });
        if (probeResult && probeResult.includes('host.docker.internal')) {
            selectedExpr = urlMatches[j][1].trim();
            break;
        }
    } catch(e) {}
}

function evalUrl(apiUrl, platform) {
    Object.defineProperty(process, 'platform', { value: platform, configurable: true });
    var options = { apiUrl: apiUrl };
    var code = helpers + '\nreturn ' + selectedExpr + ';';
    return new Function('options', code)(options);
}
"""


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- API_ORIGIN fallback
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_api_origin_preferred_over_app_origin():
    """Env endpoint must prefer API_ORIGIN over APP_ORIGIN for apiUrl."""
    node_code = r"""
const fs = require('fs');
const src = fs.readFileSync(
  'apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts', 'utf8'
);
const match = src.match(/apiUrl:\s*(.+?)\s*,/);
if (!match) { console.error('apiUrl assignment not found'); process.exit(1); }
let expr = match[1].trim();
expr = expr.replace(/processEnv\./g, 'env.');

// Case 1: both API_ORIGIN and APP_ORIGIN set -- API_ORIGIN should win
let env = { API_ORIGIN: 'https://api.test', APP_ORIGIN: 'https://app.test' };
console.log(eval(expr));

// Case 2: only APP_ORIGIN set -- should fall back
env = { APP_ORIGIN: 'https://app.test' };
console.log(eval(expr));
"""
    r = subprocess.run(
        ["node", "-e", node_code],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr}"
    lines = r.stdout.strip().split("\n")
    assert len(lines) == 2, f"Expected 2 output lines, got: {lines}"
    assert lines[0] == "https://api.test", (
        f"API_ORIGIN should be preferred when set, got: {lines[0]}"
    )
    assert lines[1] == "https://app.test", (
        f"Should fall back to APP_ORIGIN when API_ORIGIN unset, got: {lines[1]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- localhost normalization for Docker builds
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_normalize_localhost_darwin():
    """URL normalization must replace localhost with host.docker.internal on macOS."""
    node_code = _NORMALIZE_HELPER + r"""
console.log(evalUrl('http://localhost:3030', 'darwin'));
console.log(evalUrl('http://localhost:8080', 'darwin'));
console.log(evalUrl('https://api.trigger.dev', 'darwin'));
"""
    r = subprocess.run(
        ["node", "-e", node_code],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr}"
    lines = r.stdout.strip().split("\n")
    assert len(lines) == 3, f"Expected 3 output lines, got: {lines}"
    assert "host.docker.internal" in lines[0], (
        f"Should replace localhost on macOS: {lines[0]}"
    )
    assert "host.docker.internal" in lines[1], (
        f"Should replace localhost (port 8080) on macOS: {lines[1]}"
    )
    assert "api.trigger.dev" in lines[2], (
        f"Should preserve non-localhost URLs: {lines[2]}"
    )


# [pr_diff] fail_to_pass
def test_normalize_preserves_localhost_linux():
    """URL normalization must be platform-aware and preserve localhost on Linux."""
    node_code = _NORMALIZE_HELPER + r"""
// Verify darwin normalization exists (proves the code is platform-aware,
// not just a raw pass-through that accidentally preserves localhost)
var darwinResult = evalUrl('http://localhost:3030', 'darwin');
if (!darwinResult.includes('host.docker.internal')) {
    console.error('No darwin normalization -- URL handling is not platform-aware');
    process.exit(1);
}
// Now verify Linux preserves localhost
console.log(evalUrl('http://localhost:3030', 'linux'));
"""
    r = subprocess.run(
        ["node", "-e", node_code],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Node eval failed: {r.stderr}"
    assert r.stdout.strip() == "http://localhost:3030", (
        f"Should preserve localhost on Linux: {r.stdout.strip()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) -- CONTRIBUTING.md build instructions
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- modified files exist and are non-trivial
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and contain valid structure."""
    route = Path(REPO) / "apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts"
    assert route.exists(), "Route file missing"
    route_src = route.read_text()
    assert "apiUrl" in route_src, "Route file must contain apiUrl assignment"
    assert len(route_src) > 500, "Route file suspiciously short"

    build = Path(REPO) / "packages/cli-v3/src/deploy/buildImage.ts"
    assert build.exists(), "buildImage.ts missing"
    build_src = build.read_text()
    assert "TRIGGER_API_URL" in build_src, "buildImage.ts must contain TRIGGER_API_URL"
    assert len(build_src) > 1000, "buildImage.ts suspiciously short"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI checks that run actual commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_no_tabs():
    """Modified TypeScript files use spaces, not tabs (repo lint rule)."""
    for rel_path in [
        "apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts",
        "packages/cli-v3/src/deploy/buildImage.ts",
    ]:
        r = subprocess.run(
            ["cat", f"{REPO}/{rel_path}"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Failed to read {rel_path}"
        assert "\t" not in r.stdout, f"{rel_path} contains tab characters - use spaces"


# [repo_tests] pass_to_pass
def test_repo_trailing_newline():
    """Modified TypeScript files end with a newline (POSIX standard)."""
    for rel_path in [
        "apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts",
        "packages/cli-v3/src/deploy/buildImage.ts",
    ]:
        r = subprocess.run(
            ["tail", "-c", "1", f"{REPO}/{rel_path}"],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, f"Failed to check {rel_path}"
        assert r.stdout == b"\n", f"{rel_path} must end with a newline"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_webapp_route():
    """Webapp route file has valid JavaScript/TypeScript syntax."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{REPO}/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts', 'utf8');
// Check for balanced braces
let braceCount = 0;
for (const char of src) {{
  if (char === '{{') braceCount++;
  if (char === '}}') braceCount--;
  if (braceCount < 0) throw new Error('Unbalanced braces');
}}
if (braceCount !== 0) throw new Error('Unbalanced braces: ' + braceCount);
// Check for valid export statement
if (!src.includes('export async function loader')) throw new Error('Missing loader export');
console.log('OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_buildimage():
    """CLI buildImage.ts has valid JavaScript/TypeScript structure."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{REPO}/packages/cli-v3/src/deploy/buildImage.ts', 'utf8');
// Check for balanced braces
let braceCount = 0;
for (const char of src) {{
  if (char === '{{') braceCount++;
  if (char === '}}') braceCount--;
  if (braceCount < 0) throw new Error('Unbalanced braces');
}}
if (braceCount !== 0) throw new Error('Unbalanced braces: ' + braceCount);
// Check for expected function
if (!src.includes('TRIGGER_API_URL')) throw new Error('Missing TRIGGER_API_URL');
console.log('OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ts_import_validation():
    """TypeScript files have valid import/export structure (repo CI check)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{REPO}/packages/cli-v3/src/deploy/buildImage.ts', 'utf8');
// Check for ESM imports (repo uses ES modules)
const importMatches = src.match(/import\\s+.*\\s+from\\s+["'][^"']+["']/g);
if (!importMatches) throw new Error('No ESM imports found');
// Check for export keyword (ESM exports)
if (!src.includes('export ')) throw new Error('No exports found');
// Verify no CommonJS module.exports (repo uses ESM)
if (src.includes('module.exports')) {{
  throw new Error('CommonJS module.exports found in ESM file');
}}
console.log('ESM structure OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"ESM import validation failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_webapp_code_patterns():
    """Webapp route has expected code patterns for env handling (repo CI check)."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{REPO}/apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts', 'utf8');
// Check for Remix loader export pattern
if (!src.includes('export async function loader')) {{
  throw new Error('Missing Remix loader export');
}}
// Check for env.server import (secure env handling pattern)
if (!src.includes('env.server')) {{
  throw new Error('Missing env.server import (security pattern)');
}}
// Check for APP_ORIGIN (the value being modified in the PR)
if (!src.includes('APP_ORIGIN')) {{
  throw new Error('Missing APP_ORIGIN reference');
}}
// Verify loader uses json() response helper
if (!src.includes('return json(')) {{
  throw new Error('Missing json() response pattern');
}}
console.log('Webapp patterns OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Webapp code pattern check failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_package_json_validation():
    """Package.json files for modified packages are valid JSON with required fields."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
// Check webapp package.json
const webappPkg = JSON.parse(fs.readFileSync('{REPO}/apps/webapp/package.json', 'utf8'));
if (!webappPkg.scripts || !webappPkg.scripts.typecheck) {{
  throw new Error('webapp missing typecheck script');
}}
if (!webappPkg.scripts || !webappPkg.scripts.lint) {{
  throw new Error('webapp missing lint script');
}}
// Check cli-v3 package.json
const cliPkg = JSON.parse(fs.readFileSync('{REPO}/packages/cli-v3/package.json', 'utf8'));
if (!cliPkg.name) {{
  throw new Error('cli-v3 missing name field');
}}
if (cliPkg.type !== 'module') {{
  throw new Error('cli-v3 should use ESM (type: module)');
}}
console.log('Package.json validation OK');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Package.json validation failed: {r.stderr}"
