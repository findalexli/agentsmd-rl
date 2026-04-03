"""
Task: workers-sdk-createcloudflare-add-nodejs-version-check
Repo: workers-sdk @ 0de69890c8503bb67e391e7ad5578c7001b7798e
PR:   cloudflare/workers-sdk#13243

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
C3 = Path(REPO) / "packages" / "create-cloudflare"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_bin_shim_rejects_old_node():
    """bin/c3.js must exit with error when Node.js version is too old."""
    bin_path = C3 / "bin" / "c3.js"
    # Mock process.versions.node to 18.0.0 and require the shim
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '18.0.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit for old Node, got {result.returncode}"
    )
    assert "requires at least" in result.stderr.lower() or "node.js" in result.stderr.lower(), (
        f"Expected version error message in stderr, got: {result.stderr[:300]}"
    )


def test_bin_shim_error_mentions_user_version():
    """Error message must tell the user which version they are running."""
    bin_path = C3 / "bin" / "c3.js"
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '16.3.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert "16.3.0" in result.stderr, (
        f"Error should mention the user's Node version 16.3.0, got: {result.stderr[:300]}"
    )


def test_bin_shim_suggests_version_manager():
    """Error message should suggest at least one Node version manager."""
    bin_path = C3 / "bin" / "c3.js"
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '18.0.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    stderr_lower = result.stderr.lower()
    assert "volta" in stderr_lower or "nvm" in stderr_lower or "fnm" in stderr_lower, (
        f"Error should suggest a version manager (volta/nvm/fnm), got: {result.stderr[:300]}"
    )


def test_bin_shim_passes_current_node():
    """bin/c3.js must exist and NOT show version error when Node >= 20."""
    bin_path = C3 / "bin" / "c3.js"
    assert bin_path.exists(), "bin/c3.js must exist"
    result = subprocess.run(
        ["node", str(bin_path)],
        capture_output=True, text=True, timeout=15,
        cwd=str(C3),
    )
    # dist/cli.js may not exist so it might error, but NOT with version message
    assert "requires at least" not in result.stderr.lower(), (
        f"Should not show version error on Node >= 20: {result.stderr[:300]}"
    )


def test_package_json_bin_points_to_shim():
    """package.json bin must point to the bin shim, not dist/cli.js directly."""
    pkg = json.loads((C3 / "package.json").read_text())
    bin_val = pkg.get("bin", "")
    if isinstance(bin_val, dict):
        bin_targets = list(bin_val.values())
    else:
        bin_targets = [str(bin_val)]
    assert any("bin/" in t and t.endswith(".js") for t in bin_targets), (
        f"bin should point to a shim in bin/ directory, got: {bin_val}"
    )
    assert not any(t == "./dist/cli.js" for t in bin_targets), (
        f"bin should NOT point directly to dist/cli.js, got: {bin_val}"
    )




# ---------------------------------------------------------------------------
# Config edit (config_edit) — AGENTS.md must document the bin shim
# ---------------------------------------------------------------------------






