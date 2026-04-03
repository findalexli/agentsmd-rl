"""
Task: sim-improvementworker-configuration-defaults
Repo: simstudioai/sim @ 8f3e8647512febc6156b66e8f6ea1961e15f589a
PR:   3821

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

import yaml

REPO = "/workspace/sim"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_yaml_syntax():
    """Docker compose and helm values YAML files must parse without errors."""
    for rel in [
        "docker-compose.local.yml",
        "docker-compose.prod.yml",
        "helm/sim/values.yaml",
    ]:
        p = Path(REPO) / rel
        content = p.read_text()
        parsed = yaml.safe_load(content)
        assert parsed is not None, f"{rel} parsed to None"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_worker_esm_bundle_path():
    """Worker command must reference the ESM bundle (worker/index.js), not CJS."""
    for rel in ["docker-compose.local.yml", "docker-compose.prod.yml"]:
        content = (Path(REPO) / rel).read_text()
        assert "worker/index.js" in content, (
            f"{rel}: worker command should use worker/index.js (ESM), not worker.cjs"
        )
        assert "worker.cjs" not in content, (
            f"{rel}: stale reference to worker.cjs found"
        )


# [pr_diff] fail_to_pass
def test_worker_not_profile_gated():
    """The sim-worker service in docker-compose.local.yml must not be behind a profile."""
    content = (Path(REPO) / "docker-compose.local.yml").read_text()
    parsed = yaml.safe_load(content)
    worker_svc = parsed.get("services", {}).get("sim-worker", {})
    assert "profiles" not in worker_svc, (
        "sim-worker should not have a 'profiles' key — it must start by default"
    )


# [pr_diff] fail_to_pass
def test_healthchecks_no_wget():
    """Healthchecks in docker-compose files must not use wget (not available in image)."""
    for rel in ["docker-compose.local.yml", "docker-compose.prod.yml"]:
        content = (Path(REPO) / rel).read_text()
        parsed = yaml.safe_load(content)
        for svc_name, svc in parsed.get("services", {}).items():
            hc = svc.get("healthcheck", {})
            test_cmd = hc.get("test", [])
            if isinstance(test_cmd, list):
                cmd_str = " ".join(str(x) for x in test_cmd)
            else:
                cmd_str = str(test_cmd)
            assert "wget" not in cmd_str, (
                f"{rel}: {svc_name} healthcheck still uses wget"
            )


# [pr_diff] fail_to_pass
def test_helm_worker_enabled_by_default():
    """Helm values.yaml must set worker.enabled to true."""
    content = (Path(REPO) / "helm/sim/values.yaml").read_text()
    parsed = yaml.safe_load(content)
    worker_cfg = parsed.get("worker", {})
    assert worker_cfg.get("enabled") is True, (
        "worker.enabled should be true in values.yaml"
    )


# [pr_diff] fail_to_pass
def test_helm_no_redis_required_for_worker():
    """Helm _helpers.tpl must not fail when worker is enabled without REDIS_URL."""
    content = (Path(REPO) / "helm/sim/templates/_helpers.tpl").read_text()
    assert "REDIS_URL is required when worker" not in content, (
        "_helpers.tpl should not enforce REDIS_URL requirement for worker"
    )


# [pr_diff] fail_to_pass
def test_helm_worker_command_path():
    """Helm deployment-worker.yaml must use ESM worker path."""
    content = (Path(REPO) / "helm/sim/templates/deployment-worker.yaml").read_text()
    assert "worker/index.js" in content, (
        "deployment-worker.yaml should reference worker/index.js"
    )
    assert "worker.cjs" not in content, (
        "deployment-worker.yaml still references worker.cjs"
    )


# [pr_diff] fail_to_pass
def test_build_worker_esm_format():
    """package.json build:worker script must use ESM format, not CJS."""
    content = (Path(REPO) / "apps/sim/package.json").read_text()
    pkg = json.loads(content)
    build_worker = pkg.get("scripts", {}).get("build:worker", "")
    assert "--format=esm" in build_worker or "format=esm" in build_worker, (
        "build:worker should use --format=esm"
    )
    assert "--format=cjs" not in build_worker, (
        "build:worker should not use --format=cjs"
    )


# [pr_diff] fail_to_pass
def test_isolated_vm_additional_paths():
    """isolated-vm.ts must include candidate paths for the ESM worker context."""
    content = (Path(REPO) / "apps/sim/lib/execution/isolated-vm.ts").read_text()
    # The worker running from dist/worker/ needs to resolve the isolated-vm-worker
    # via parent directory traversal — look for a path that goes up two levels
    has_parent_traversal = (
        "'..', '..', 'lib'" in content
        or "'apps', 'sim', 'lib'" in content
    )
    assert has_parent_traversal, (
        "isolated-vm.ts should have additional candidate paths for parent traversal"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation update tests
# ---------------------------------------------------------------------------


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_app_dockerfile_copies_worker_bundle():
    """app.Dockerfile must copy the worker bundle artifacts."""
    content = (Path(REPO) / "docker/app.Dockerfile").read_text()
    # Both before and after the fix, the Dockerfile copies worker artifacts
    assert "dist/worker" in content, (
        "app.Dockerfile should copy the worker bundle"
    )
