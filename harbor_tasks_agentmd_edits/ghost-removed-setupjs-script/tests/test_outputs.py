"""
Task: ghost-removed-setupjs-script
Repo: TryGhost/Ghost @ c1e86e6dd150e7ab1a226cfce8f73bc4ee441787
PR:   #26507

The old .github/scripts/setup.js handled MySQL Docker setup and config
writing during `yarn setup`. Since `yarn dev` now handles this, setup.js
is removed, the package.json setup script is simplified, and docs/README.md
is updated to reflect the new workflow.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/Ghost"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_package_json_valid():
    """package.json must be valid JSON."""
    pkg = Path(REPO) / "package.json"
    data = json.loads(pkg.read_text())
    assert "scripts" in data, "package.json must have scripts"
    assert "setup" in data["scripts"], "package.json must have a setup script"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior
# ---------------------------------------------------------------------------

def test_setup_script_removed():
    """The .github/scripts/setup.js file must be deleted."""
    setup_js = Path(REPO) / ".github" / "scripts" / "setup.js"
    assert not setup_js.exists(), \
        ".github/scripts/setup.js should be removed — yarn dev now handles MySQL/config setup"


def test_package_json_setup_no_setup_js():
    """package.json setup script must not invoke setup.js."""
    pkg = json.loads((Path(REPO) / "package.json").read_text())
    setup_cmd = pkg["scripts"]["setup"]
    assert "setup.js" not in setup_cmd, \
        f"setup script still references setup.js: {setup_cmd}"
    assert "NODE_ENV" not in setup_cmd, \
        f"setup script still sets NODE_ENV (leftover from setup.js): {setup_cmd}"




# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — docs/README.md updates
# ---------------------------------------------------------------------------







# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

