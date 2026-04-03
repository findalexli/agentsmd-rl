"""
Task: trigger.dev-allow-selfhosted-deploys-locally-without
Repo: triggerdotdev/trigger.dev @ ad4daa3301f63354745cdcb8e911950d9fa5a93f
PR:   2064

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — API_ORIGIN fallback
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_api_origin_preferred_over_app_origin():
    """Env endpoint must prefer API_ORIGIN over APP_ORIGIN for apiUrl."""
    # Extract the apiUrl expression from the route and evaluate it with mock env
    node_code = r"""
const fs = require('fs');
const src = fs.readFileSync(
  'apps/webapp/app/routes/api.v1.projects.$projectRef.$env.ts', 'utf8'
);
const match = src.match(/apiUrl:\s*(.+?)\s*,/);
if (!match) { console.error('apiUrl assignment not found'); process.exit(1); }
let expr = match[1].trim();
expr = expr.replace(/processEnv\./g, 'env.');

// Case 1: both API_ORIGIN and APP_ORIGIN set — API_ORIGIN should win
let env = { API_ORIGIN: 'https://api.test', APP_ORIGIN: 'https://app.test' };
console.log(eval(expr));

// Case 2: only APP_ORIGIN set — should fall back
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
# Fail-to-pass (pr_diff) — localhost normalization for Docker builds
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_normalize_localhost_darwin():
    """normalizeApiUrlForBuild must replace localhost with host.docker.internal on macOS."""
    node_code = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/cli-v3/src/deploy/buildImage.ts', 'utf8');
const match = src.match(
  /function normalizeApiUrlForBuild\(apiUrl(?::\s*\w+)?\)\s*\{([\s\S]*?)\n\}/
);
if (!match) { console.error('normalizeApiUrlForBuild not found'); process.exit(1); }
const body = match[1];
Object.defineProperty(process, 'platform', { value: 'darwin', configurable: true });
const fn = new Function('apiUrl', body);
console.log(fn('http://localhost:3030'));
console.log(fn('http://localhost:8080'));
console.log(fn('https://api.trigger.dev'));
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
    """normalizeApiUrlForBuild must NOT replace localhost on Linux."""
    node_code = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/cli-v3/src/deploy/buildImage.ts', 'utf8');
const match = src.match(
  /function normalizeApiUrlForBuild\(apiUrl(?::\s*\w+)?\)\s*\{([\s\S]*?)\n\}/
);
if (!match) { console.error('normalizeApiUrlForBuild not found'); process.exit(1); }
const body = match[1];
Object.defineProperty(process, 'platform', { value: 'linux', configurable: true });
const fn = new Function('apiUrl', body);
console.log(fn('http://localhost:3030'));
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
# Fail-to-pass (config_edit) — CONTRIBUTING.md build instructions
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — modified files exist and are non-trivial
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
