"""
Task: remix-routepattern-benchmark-types
Repo: remix-run/remix @ 3921f065331f6b28e0c29750f1e757a4e09feebc
PR:   11045

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------


def test_type_benchmark_files_exist():
    """bench/types/ directory must contain at least 3 type benchmark .ts files."""
    r = _node("""
const fs = require('fs');
const path = require('path');
const dir = path.join(process.cwd(), 'packages/route-pattern/bench/types');
if (!fs.existsSync(dir)) { console.error('bench/types/ directory missing'); process.exit(1); }
const files = fs.readdirSync(dir).filter(f => f.endsWith('.ts'));
if (files.length < 3) {
  console.error('Expected >= 3 .ts files in bench/types/, got ' + files.length);
  process.exit(1);
}
console.log(JSON.stringify(files));
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_type_benchmarks_use_attest():
    """Type benchmark files must use @ark/attest bench() with .types() assertions, covering href and params."""
    r = _node("""
const fs = require('fs');
const path = require('path');
const dir = path.join(process.cwd(), 'packages/route-pattern/bench/types');
if (!fs.existsSync(dir)) { console.error('bench/types/ missing'); process.exit(1); }
const files = fs.readdirSync(dir).filter(f => f.endsWith('.ts'));
let hasHref = false, hasParams = false;
for (const f of files) {
  const content = fs.readFileSync(path.join(dir, f), 'utf-8');
  if (!content.includes('@ark/attest')) {
    console.error(f + ' missing @ark/attest import'); process.exit(1);
  }
  if (!content.includes('bench(')) {
    console.error(f + ' missing bench() call'); process.exit(1);
  }
  if (!content.includes('.types(')) {
    console.error(f + ' missing .types() assertion'); process.exit(1);
  }
  if (/href/i.test(content)) hasHref = true;
  if (/params/i.test(content)) hasParams = true;
}
if (!hasHref) { console.error('No type benchmark covers href'); process.exit(1); }
if (!hasParams) { console.error('No type benchmark covers params'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_runtime_benchmarks_moved_to_src():
    """Existing runtime .bench.ts files must be in bench/src/, not in bench/ root."""
    r = _node("""
const fs = require('fs');
const path = require('path');
const benchDir = path.join(process.cwd(), 'packages/route-pattern/bench');
const srcDir = path.join(benchDir, 'src');
if (!fs.existsSync(srcDir)) { console.error('bench/src/ directory missing'); process.exit(1); }
const expected = ['comparison.bench.ts', 'href.bench.ts', 'pathological.bench.ts', 'simple.bench.ts'];
for (const f of expected) {
  if (!fs.existsSync(path.join(srcDir, f))) {
    console.error(f + ' missing from bench/src/'); process.exit(1);
  }
  if (fs.existsSync(path.join(benchDir, f))) {
    console.error(f + ' still in bench/ root (should be moved to src/)'); process.exit(1);
  }
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_bench_package_json_updated():
    """bench/package.json must have bench:types script and @ark/attest devDependency."""
    r = _node("""
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('packages/route-pattern/bench/package.json', 'utf-8'));
if (!pkg.scripts || !pkg.scripts['bench:types']) {
  console.error('Missing bench:types script'); process.exit(1);
}
if (!pkg.devDependencies || !pkg.devDependencies['@ark/attest']) {
  console.error('Missing @ark/attest devDependency'); process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_attest_moved_from_parent_package():
    """@ark/attest must be removed from route-pattern/package.json devDependencies."""
    r = _node("""
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('packages/route-pattern/package.json', 'utf-8'));
if (pkg.devDependencies && pkg.devDependencies['@ark/attest']) {
  console.error('@ark/attest should not be in route-pattern devDependencies');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_readme_documents_type_benchmarks():
    """bench/README.md must distinguish runtime vs type benchmarks with src/ and types/ refs."""
    r = _node("""
const fs = require('fs');
const content = fs.readFileSync('packages/route-pattern/bench/README.md', 'utf-8');
const lower = content.toLowerCase();
if (!lower.includes('type benchmark')) {
  console.error('README missing type benchmarks section'); process.exit(1);
}
if (!lower.includes('attest')) {
  console.error('README missing ArkType Attest reference'); process.exit(1);
}
if (!lower.includes('runtime')) {
  console.error('README missing runtime benchmarks label'); process.exit(1);
}
if (!content.includes('src/')) {
  console.error('README missing src/ reference'); process.exit(1);
}
if (!content.includes('types/')) {
  console.error('README missing types/ reference'); process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_existing_bench_deps_maintained():
    """Existing bench dependencies (vitest, path-to-regexp) still present."""
    r = _node("""
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('packages/route-pattern/bench/package.json', 'utf-8'));
const deps = pkg.dependencies || {};
const devDeps = pkg.devDependencies || {};
if (!devDeps['vitest']) { console.error('vitest devDep missing'); process.exit(1); }
if (!deps['path-to-regexp']) { console.error('path-to-regexp dep missing'); process.exit(1); }
if (!deps['@remix-run/route-pattern']) { console.error('@remix-run/route-pattern dep missing'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"


def test_route_pattern_package_json_valid():
    """packages/route-pattern/package.json core fields preserved."""
    r = _node("""
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('packages/route-pattern/package.json', 'utf-8'));
if (pkg.name !== '@remix-run/route-pattern') {
  console.error('Package name changed: ' + pkg.name); process.exit(1);
}
if (!pkg.exports) { console.error('exports field missing'); process.exit(1); }
console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
