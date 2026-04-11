"""
Task: workers-sdk-playground-vite8-createrenderer
Repo: workers-sdk @ 49d063396f4c87bc7323be84fbd961b010a09460
PR:   13105

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
VITE_CONFIG = os.path.join(REPO, "packages/workers-playground/vite.config.ts")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_vite_config_valid_structure():
    """vite.config.ts must exist, export a defineConfig, and have balanced braces."""
    assert os.path.isfile(VITE_CONFIG), f"Missing: {VITE_CONFIG}"
    content = Path(VITE_CONFIG).read_text()
    assert "defineConfig" in content, "Missing defineConfig call"
    assert "export default" in content, "Missing default export"
    # Balanced braces (basic structural sanity)
    assert content.count("{") == content.count("}"), (
        f"Unbalanced braces: {{ = {content.count('{')}, }} = {content.count('}')}"
    )


# [static] pass_to_pass
def test_jsx_runtime_alias_preserved():
    """The existing react/jsx-runtime.js alias must still be present."""
    content = Path(VITE_CONFIG).read_text()
    assert "react/jsx-runtime.js" in content, (
        "Missing react/jsx-runtime.js alias — existing alias was removed"
    )
    assert "react/jsx-runtime" in content, (
        "Missing react/jsx-runtime target in alias"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — CI checks that exercise the repo tooling
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo linting passes
def test_repo_lint():
    """Repo's linter (oxlint) passes on all files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run check:lint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo formatting passes
def test_repo_format():
    """Repo's formatter (oxfmt) passes on all files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run check:format"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Workers-playground package checks pass
def test_repo_workers_playground_check():
    """Workers-playground package check passes (pass_to_pass).

    This runs check:default-hashes and check:type on the package,
    which exercises the vite.config.ts TypeScript compilation.
    """
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && "
         "pnpm run build --filter=@cloudflare/workers-editor-shared... >/dev/null 2>&1 && "
         "cd packages/workers-playground && pnpm run check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Workers-playground check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Workers-playground package build succeeds
def test_repo_workers_playground_build():
    """Workers-playground package builds successfully (pass_to_pass).

    This runs the full Vite build on the workers-playground package,
    which exercises vite.config.ts with the actual Vite 8 bundler.
    The build would fail if the style-provider alias or assetsDir config
    were misconfigured, causing rolldown to crash or assets to be misplaced.
    """
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && "
         "pnpm run build --filter=@cloudflare/workers-playground... 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Workers-playground build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Workers-editor-shared package builds
def test_repo_workers_editor_shared_build():
    """Workers-editor-shared package builds successfully (pass_to_pass).

    This builds the @cloudflare/workers-editor-shared dependency,
    which is a prerequisite for the workers-playground build. This
    test ensures the shared components compile correctly.
    """
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && "
         "pnpm run build --filter=@cloudflare/workers-editor-shared 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Workers-editor-shared build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_style_provider_cjs_alias():
    """@cloudflare/style-provider must be aliased to its CJS build to avoid rolldown crash."""
    # Use node to parse the config file and extract the alias value
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');

// Look for the style-provider alias in resolve.alias
const aliasPattern = /["']@cloudflare\/style-provider["']\s*:\s*["']([^"']+)["']/;
const match = content.match(aliasPattern);

if (!match) {
    console.error('FAIL: No @cloudflare/style-provider alias found in resolve.alias');
    process.exit(1);
}

const target = match[1];
// The alias must point to the CJS build (lib/ directory), not the ESM build (es/ directory)
if (!target.includes('lib/')) {
    console.error('FAIL: style-provider alias points to ' + target + ' — must use CJS build (lib/)');
    process.exit(1);
}

console.log('OK: @cloudflare/style-provider aliased to ' + target);
"""
    r = subprocess.run(
        ["node", "-e", script, VITE_CONFIG],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"style-provider CJS alias check failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_no_base_playground_option():
    """base: '/playground' must NOT be used — it causes asset path mismatch with Wrangler."""
    # Use node to check the config does NOT set base to /playground
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');

// Strip comments to avoid false positives from commented-out code
const stripped = content.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Check for base: "/playground" or base: '/playground' in the active config
if (/\bbase\s*:\s*["']\/playground["']/.test(stripped)) {
    console.error('FAIL: base is set to "/playground" — this causes Wrangler asset path mismatch');
    process.exit(1);
}

console.log('OK: base is not set to /playground');
"""
    r = subprocess.run(
        ["node", "-e", script, VITE_CONFIG],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"base:/playground check failed:\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_assets_dir_playground():
    """assetsDir must route built assets under playground/ for correct Wrangler deployment."""
    # Use node to verify assetsDir is configured with a playground path
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf8');

// Strip comments
const stripped = content.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

// Check that assetsDir contains 'playground'
const match = stripped.match(/assetsDir\s*:\s*["']([^"']+)["']/);
if (!match) {
    console.error('FAIL: No assetsDir found in build config');
    process.exit(1);
}

const dir = match[1];
if (!dir.includes('playground')) {
    console.error('FAIL: assetsDir is "' + dir + '" — must include "playground" for correct deployment');
    process.exit(1);
}

console.log('OK: assetsDir = ' + dir);
"""
    r = subprocess.run(
        ["node", "-e", script, VITE_CONFIG],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"assetsDir check failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:100,161 @ 49d063396f4c87bc7323be84fbd961b010a09460
def test_changeset_for_workers_playground():
    """AGENTS.md requires a changeset for every change to a published package."""
    # Check that at least one .changeset/*.md file references workers-playground
    r = subprocess.run(
        ["bash", "-c",
         r"grep -rl '@cloudflare/workers-playground' .changeset/*.md 2>/dev/null | head -1"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    found = r.stdout.decode().strip()
    assert found, (
        "No changeset found for @cloudflare/workers-playground — "
        "AGENTS.md requires changesets for all published package changes"
    )
