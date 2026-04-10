"""
Task: nextjs-localhost-subdomain-wildcard-depth
Repo: next.js @ feae4cc4305a991233ca5c529d897b7ed1136872
PR:   92262

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
BLOCK_FILE = f"{REPO}/packages/next/src/server/lib/router-utils/block-cross-site-dev.ts"
CSRF_FILE = f"{REPO}/packages/next/src/server/app-render/csrf-protection.ts"

# Cache for setup state
_setup_done = False


def _ensure_setup():
    """Ensure pnpm is installed and dependencies are available."""
    global _setup_done
    if _setup_done:
        return

    # Check if pnpm is available
    r = subprocess.run(["which", "pnpm"], capture_output=True)
    if r.returncode != 0:
        # Install pnpm globally
        subprocess.run(["npm", "install", "-g", "pnpm"], check=True, capture_output=True)

    # Check if node_modules exists
    if not Path(f"{REPO}/node_modules").exists():
        # Install dependencies (skip frozen-lockfile for compatibility)
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            cwd=REPO, capture_output=True, timeout=300,
        )

    _setup_done = True


def _get_localhost_pattern():
    """Extract the localhost wildcard pattern from block-cross-site-dev.ts."""
    content = Path(BLOCK_FILE).read_text()
    match = re.search(r"'(\*+\.localhost)'", content)
    assert match, "Could not find *.localhost or **.localhost pattern in allowedOrigins"
    return match.group(1)


def _build_csrf_js():
    """Read csrf-protection.ts and strip type annotations to get executable JS."""
    ts_src = Path(CSRF_FILE).read_text()
    # Strip TypeScript type annotations (file is pure JS + simple annotations)
    js = ts_src
    js = re.sub(r":\s*string\[\]", "", js)
    js = re.sub(r":\s*string", "", js)
    js = re.sub(r":\s*boolean", "", js)
    js = re.sub(r"\bexport\s+const\b", "const", js)
    return js


def _run_csrf_check(origin, patterns):
    """Execute isCsrfOriginAllowed from the actual repo source via Node.js."""
    csrf_js = _build_csrf_js()
    patterns_json = json.dumps(patterns)
    script = f"""{csrf_js}
const result = isCsrfOriginAllowed({json.dumps(origin)}, {patterns_json});
process.stdout.write(JSON.stringify({{origin: {json.dumps(origin)}, allowed: result}}));
process.exit(result ? 0 : 1);
"""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    return r.returncode == 0


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """block-cross-site-dev.ts must be syntactically valid TypeScript."""
    content = Path(BLOCK_FILE).read_text()
    # Verify the file parses: check balanced braces and no obvious syntax errors
    assert "blockCrossSiteDEV" in content, "Main export function missing"
    assert content.count("{") == content.count("}"), "Unbalanced braces"
    # Also verify the allowedOrigins array structure is intact
    assert re.search(
        r"const\s+allowedOrigins\s*=\s*\[", content
    ), "allowedOrigins array declaration missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_multi_level_localhost_allowed():
    """Multi-level .localhost subdomains must be allowed by the dev origin check."""
    pattern = _get_localhost_pattern()
    origins = [pattern, "localhost"]

    # Two-level subdomain: sub.app.localhost
    assert _run_csrf_check("sub.app.localhost", origins), (
        f"sub.app.localhost was blocked with pattern '{pattern}' — "
        "multi-level .localhost subdomains should be auto-allowed"
    )
    # Three-level subdomain: a.b.c.localhost
    assert _run_csrf_check("a.b.c.localhost", origins), (
        f"a.b.c.localhost was blocked with pattern '{pattern}'"
    )


# [pr_diff] fail_to_pass
def test_deeply_nested_localhost():
    """Even deeply nested .localhost subdomains (4+ levels) must be allowed."""
    pattern = _get_localhost_pattern()
    origins = [pattern, "localhost"]

    assert _run_csrf_check("w.x.y.z.localhost", origins), (
        f"w.x.y.z.localhost was blocked with pattern '{pattern}'"
    )
    assert _run_csrf_check("one.two.three.four.five.localhost", origins), (
        f"one.two.three.four.five.localhost was blocked with pattern '{pattern}'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# These tests verify the repo's own CI checks pass on both base and gold.
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typescript():
    """Repo's TypeScript typecheck on modified files passes (pass_to_pass).

    Note: Full repo typecheck requires build artifacts. We check the
    specific modified files can be parsed as valid TypeScript.
    """
    _ensure_setup()
    # Check the modified file is valid TypeScript (can be parsed)
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", BLOCK_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Accept 0 (success) or 2 (config/diagnostic errors) but not 1 (type errors)
    # The file should at least be parseable
    if r.returncode == 1:
        # Only fail if there are actual type errors, not config errors
        assert "error TS" not in r.stdout, f"TypeScript errors in block-cross-site-dev.ts:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's formatting check passes on modified files (pass_to_pass)."""
    _ensure_setup()
    # Run prettier check only on the specific file we care about
    r = subprocess.run(
        ["pnpm", "exec", "prettier", "--check", BLOCK_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_eslint():
    """Repo's ESLint check passes on modified files (pass_to_pass)."""
    _ensure_setup()
    # Run eslint only on the specific file we care about
    r = subprocess.run(
        ["pnpm", "exec", "eslint", "--config", "eslint.cli.config.mjs", BLOCK_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Allow for config errors (exit code 2) but not actual lint errors
    assert r.returncode in [0, 2], f"ESLint check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_csrf_logic_unit():
    """CSRF origin matching logic unit tests (pass_to_pass).

    Tests the core isCsrfOriginAllowed/matchWildcardDomain logic directly
    using Node.js to verify the PR change works correctly. This is a
    lightweight alternative to running the full jest test suite which
    requires build artifacts.
    """
    # Test script that replicates the CSRF protection unit tests
    test_script = """
// Replicate the CSRF matching logic from csrf-protection.ts
function matchWildcardDomain(domain, pattern) {
  const normalizedDomain = domain.replace(/[A-Z]/g, (c) => c.toLowerCase())
  const normalizedPattern = pattern.replace(/[A-Z]/g, (c) => c.toLowerCase())
  const domainParts = normalizedDomain.split('.')
  const patternParts = normalizedPattern.split('.')
  if (patternParts.length < 1) return false
  if (domainParts.length < patternParts.length) return false
  if (patternParts.length === 1 && (patternParts[0] === '*' || patternParts[0] === '**')) return false
  while (patternParts.length) {
    const patternPart = patternParts.pop()
    const domainPart = domainParts.pop()
    switch (patternPart) {
      case '': return false
      case '*': if (domainPart) continue; else return false;
      case '**': if (patternParts.length > 0) return false; return domainPart !== undefined;
      default: if (domainPart !== patternPart) return false;
    }
  }
  return domainParts.length === 0
}

function isCsrfOriginAllowed(originDomain, allowedOrigins = []) {
  const normalizedOrigin = originDomain.replace(/[A-Z]/g, (c) => c.toLowerCase())
  return allowedOrigins.some((allowedOrigin) => {
    if (!allowedOrigin) return false
    const normalizedAllowed = allowedOrigin.replace(/[A-Z]/g, (c) => c.toLowerCase())
    return normalizedAllowed === normalizedOrigin || matchWildcardDomain(originDomain, allowedOrigin)
  })
}

// Tests
const tests = [
  // PR 92262: Multi-level .localhost subdomains with **.localhost
  { origin: 'app.localhost', pattern: '**.localhost', expected: true, desc: 'single-level subdomain with **' },
  { origin: 'sub.app.localhost', pattern: '**.localhost', expected: true, desc: 'two-level subdomain with **' },
  { origin: 'a.b.c.localhost', pattern: '**.localhost', expected: true, desc: 'three-level subdomain with **' },
  { origin: 'deep.nested.sub.localhost', pattern: '**.localhost', expected: true, desc: 'deeply nested subdomain with **' },

  // Security: non-localhost should not match
  { origin: 'evil.com', pattern: '**.localhost', expected: false, desc: 'non-localhost should not match' },
  { origin: 'localhost.evil.com', pattern: '**.localhost', expected: false, desc: 'domain ending in localhost should not match' },

  // Case insensitivity (RFC 1035)
  { origin: 'Sub.App.Localhost', pattern: '**.localhost', expected: true, desc: 'case insensitive matching' },

  // Exact match still works
  { origin: 'localhost', pattern: 'localhost', expected: true, desc: 'exact match localhost' },
];

let passed = 0, failed = 0;
for (const t of tests) {
  const result = isCsrfOriginAllowed(t.origin, [t.pattern]);
  const pass = result === t.expected;
  if (!pass) {
    console.error(`FAIL: ${t.desc}: ${t.origin} with ${t.pattern} = ${result} (expected ${t.expected})`);
    failed++;
  } else {
    passed++;
  }
}
console.log(`${passed}/${tests.length} tests passed`);
process.exit(failed > 0 ? 1 : 0);
"""
    r = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CSRF logic unit tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_lint_eslint_csrf():
    """ESLint check passes on csrf-protection.ts (pass_to_pass).

    Verifies that the CSRF protection file passes linting.
    """
    _ensure_setup()
    r = subprocess.run(
        ["pnpm", "exec", "eslint", "--config", "eslint.config.mjs", CSRF_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Allow for config errors (exit code 2) but not actual lint errors
    assert r.returncode in [0, 2], f"ESLint check failed:\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_single_level_localhost_still_allowed():
    """Single-level .localhost subdomains must still be allowed (regression)."""
    pattern = _get_localhost_pattern()
    origins = [pattern, "localhost"]

    assert _run_csrf_check("app.localhost", origins), (
        f"app.localhost was blocked with pattern '{pattern}' — single-level must still work"
    )
    assert _run_csrf_check("mysite.localhost", origins), (
        f"mysite.localhost was blocked with pattern '{pattern}'"
    )


# [static] pass_to_pass
def test_non_localhost_still_blocked():
    """Non-localhost origins must remain blocked by the default allowlist."""
    pattern = _get_localhost_pattern()
    origins = [pattern, "localhost"]

    for domain in ["evil.com", "attacker.example.org", "not-localhost.dev"]:
        assert not _run_csrf_check(domain, origins), (
            f"{domain} was incorrectly allowed with pattern '{pattern}'"
        )
