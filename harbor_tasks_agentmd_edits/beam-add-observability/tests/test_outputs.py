"""
Task: beam-add-observability
Repo: apache/beam @ 67c3183913af13afa3c98d219f8882e278cdea0b
PR:   37716

Replace StatsD exporter sidecar with native Prometheus metrics exported to
Google Cloud Monitoring, add a deploy helper script, and update the README.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
from pathlib import Path

REPO = "/workspace/beam"
TF_DIR = os.path.join(REPO, "examples", "terraform", "envoy-ratelimiter")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Terraform files have balanced braces (basic HCL syntax sanity)."""
    for name in ("ratelimit.tf", "variables.tf", "prerequisites.tf"):
        path = os.path.join(TF_DIR, name)
        content = Path(path).read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert opens == closes, (
            f"{name}: unbalanced braces (open={opens}, close={closes})"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behaviour
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prometheus_env_configured():
    """ratelimit.tf must set USE_PROMETHEUS env var (replaces USE_STATSD)."""
    content = Path(os.path.join(TF_DIR, "ratelimit.tf")).read_text()
    assert re.search(r'"USE_PROMETHEUS"', content), (
        "ratelimit.tf should configure USE_PROMETHEUS environment variable"
    )
    assert re.search(r'"PROMETHEUS_ADDR"', content) or re.search(r'"PROMETHEUS_PATH"', content), (
        "ratelimit.tf should configure PROMETHEUS_ADDR or PROMETHEUS_PATH"
    )


# [pr_diff] fail_to_pass
def test_statsd_sidecar_removed():
    """ratelimit.tf must not have a statsd-exporter sidecar container."""
    content = Path(os.path.join(TF_DIR, "ratelimit.tf")).read_text()
    assert "statsd-exporter" not in content, (
        "ratelimit.tf should not contain a statsd-exporter sidecar container"
    )
    assert "STATSD_HOST" not in content, (
        "ratelimit.tf should not reference STATSD_HOST"
    )
    assert "STATSD_PORT" not in content, (
        "ratelimit.tf should not reference STATSD_PORT"
    )


# [pr_diff] fail_to_pass
def test_monitoring_api_enabled():
    """prerequisites.tf must include the monitoring API."""
    content = Path(os.path.join(TF_DIR, "prerequisites.tf")).read_text()
    assert '"monitoring"' in content, (
        "prerequisites.tf should include 'monitoring' in the required APIs list"
    )


# [pr_diff] fail_to_pass
def test_pod_monitoring_resource():
    """ratelimit.tf must define a PodMonitoring resource for Cloud Monitoring."""
    content = Path(os.path.join(TF_DIR, "ratelimit.tf")).read_text()
    assert "PodMonitoring" in content, (
        "ratelimit.tf should define a PodMonitoring custom resource"
    )
    assert "monitoring.googleapis.com" in content, (
        "ratelimit.tf PodMonitoring should use monitoring.googleapis.com API"
    )


# [pr_diff] fail_to_pass
def test_metrics_port_9090():
    """Metrics should be exposed on port 9090 (not the old 9102)."""
    content = Path(os.path.join(TF_DIR, "ratelimit.tf")).read_text()
    assert "9090" in content, (
        "ratelimit.tf should expose metrics on port 9090"
    )
    assert "9102" not in content, (
        "ratelimit.tf should not reference old StatsD port 9102"
    )


# [pr_diff] fail_to_pass
def test_deploy_script_exists():
    """deploy.sh must exist and handle apply/destroy commands."""
    deploy_path = os.path.join(TF_DIR, "deploy.sh")
    assert os.path.isfile(deploy_path), "deploy.sh should exist"
    content = Path(deploy_path).read_text()
    assert "apply" in content, "deploy.sh should handle 'apply' command"
    assert "destroy" in content, "deploy.sh should handle 'destroy' command"
    assert "terraform" in content.lower(), "deploy.sh should invoke terraform"
    assert content.startswith("#!/"), "deploy.sh should have a shebang line"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [agent_config] fail_to_pass — .agent/skills/license-compliance/SKILL.md:26-46
def test_deploy_script_has_license_header():
    """New deploy.sh must include Apache 2.0 license header per repo policy."""
    deploy_path = os.path.join(TF_DIR, "deploy.sh")
    assert os.path.isfile(deploy_path), "deploy.sh should exist"
    content = Path(deploy_path).read_text()
    assert "Licensed to the Apache Software Foundation" in content or "Apache License" in content, (
        "deploy.sh must include the Apache 2.0 license header"
    )
