"""
Task: trigger.dev-chorerepo-add-agentcrumbsdev-support
Repo: triggerdotdev/trigger.dev @ d4d8d9fabc45c48c75b7d89f3d2773b426dc5b28
PR:   3206

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_remix_config_valid_js():
    """remix.config.js must be valid JavaScript that Node can evaluate."""
    r = subprocess.run(
        ["node", "-e", "require('./apps/webapp/remix.config.js')"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    assert r.returncode == 0, (
        f"remix.config.js failed to parse:\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_package_json_valid():
    """Root package.json must be valid JSON."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    assert "dependencies" in pkg, "package.json must have dependencies"


# [repo_tests] pass_to_pass
def test_webapp_lint():
    """Webapp linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.23.0 --activate && pnpm install --frozen-lockfile && pnpm run lint --filter webapp"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_webapp_typecheck():
    """Webapp TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.23.0 --activate && pnpm install --frozen-lockfile && pnpm run generate && pnpm run typecheck --filter webapp"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_webapp_unit_tests_simple():
    """Webapp simple unit tests pass (pass_to_pass) - tests that don't need Docker."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.23.0 --activate && pnpm install --frozen-lockfile && pnpm run generate && cd apps/webapp && npx vitest run test/detectbadJsonStrings.test.ts test/calculateNextSchedule.test.ts test/validateGitBranchName.test.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_webapp_build():
    """Webapp build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.23.0 --activate && pnpm install --frozen-lockfile && pnpm run generate && pnpm run build --filter webapp"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code / build config changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_remix_config_bundles_agentcrumbs():
    """remix.config.js must include agentcrumbs in serverDependenciesToBundle."""
    r = subprocess.run(
        [
            "node", "-e",
            "const c = require('./apps/webapp/remix.config.js');"
            "const deps = c.serverDependenciesToBundle;"
            "const found = deps.some(d => typeof d === 'string' && d === 'agentcrumbs');"
            "if (!found) process.exit(1);",
        ],
        cwd=REPO, capture_output=True, timeout=10,
    )
    assert r.returncode == 0, (
        "agentcrumbs not found in serverDependenciesToBundle"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
