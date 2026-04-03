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
