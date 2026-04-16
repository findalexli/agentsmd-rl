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

import pytest

REPO = "/workspace/workers-sdk"
VITE_CONFIG = os.path.join(REPO, "packages/workers-playground/vite.config.ts")
DIST_DIR = os.path.join(REPO, "packages/workers-playground/dist")


# ---------------------------------------------------------------------------
# Shared fixture: build workers-playground once for behavioral output tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def playground_dist():
    """Build workers-playground and return the dist directory path."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm >/dev/null 2>&1 && "
         "pnpm install --frozen-lockfile >/dev/null 2>&1 && "
         "pnpm run build --filter=@cloudflare/workers-playground... 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    return DIST_DIR


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


# [repo_tests] pass_to_pass — Vite-plugin package builds
def test_repo_vite_plugin_build():
    """Vite-plugin package builds successfully (pass_to_pass).

    This builds the @cloudflare/vite-plugin dependency, which is used
    by the workers-playground package. The plugin must compile correctly
    for the workers-playground to build and function properly.
    """
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && "
         "pnpm run build --filter=@cloudflare/vite-plugin 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Vite-plugin build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests verified against BUILD OUTPUT
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_style_provider_cjs_alias(playground_dist):
    """The built bundle must properly include createRenderer from @cloudflare/style-provider.

    When rolldown mishandles the ESM/CJS hybrid package, createRenderer ends up
    in an unreachable module initializer and does not appear in the output bundle.
    Any correct fix (alias to CJS, Vite plugin, etc.) ensures createRenderer is
    properly included in the bundled output.
    """
    bundle_content = ""
    for js_file in Path(playground_dist).rglob("*.js"):
        bundle_content += js_file.read_text()

    assert "createRenderer" in bundle_content, (
        "createRenderer not found in the built bundle — "
        "@cloudflare/style-provider was not properly resolved for rolldown. "
        "The ESM/CJS hybrid package must be configured so rolldown correctly "
        "bundles the createRenderer export."
    )


# [pr_diff] fail_to_pass
def test_no_base_playground_option(playground_dist):
    """Static resource paths in the built HTML must not carry a /playground/ prefix.

    When Vite's base option is set to '/playground', ALL resource URLs
    (including static assets like favicon) get the /playground/ prefix.
    This causes a mismatch with Wrangler's asset serving because Wrangler
    looks up files by their physical dist path. Removing the base option
    (or using an alternative approach) ensures static resources are
    referenced without the incorrect prefix.
    """
    index_html = Path(playground_dist) / "index.html"
    assert index_html.exists(), "No index.html found in dist"
    content = index_html.read_text()

    assert "/playground/favicon" not in content, (
        "index.html references /playground/favicon — the Vite base option "
        "appears to be set to '/playground', which causes Wrangler asset path mismatch. "
        "Static resources must not have the /playground/ prefix."
    )


# [pr_diff] fail_to_pass
def test_assets_dir_playground(playground_dist):
    """Built JS/CSS assets must be physically located under dist/playground/ for Wrangler.

    Wrangler serves assets based on their physical location in the dist directory.
    For the Workers Playground (hosted at /playground), JS and CSS assets must be
    under dist/playground/ so Wrangler serves them at the correct URL paths.
    Any correct approach (assetsDir, post-build move, plugin) must place the
    compiled assets under this directory.
    """
    playground_dir = Path(playground_dist) / "playground"
    assert playground_dir.is_dir(), (
        "No playground/ subdirectory found in dist — "
        "built assets must be under dist/playground/ for correct Wrangler deployment"
    )

    asset_files = list(playground_dir.rglob("*.js")) + list(playground_dir.rglob("*.css"))
    assert len(asset_files) > 0, (
        "No JS/CSS assets found under dist/playground/ — "
        "assets must be physically in this directory for Wrangler to serve them correctly"
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
