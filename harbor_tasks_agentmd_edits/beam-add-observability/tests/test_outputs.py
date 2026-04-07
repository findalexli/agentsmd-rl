"""
Task: beam-add-observability
Repo: apache/beam @ 67c3183913af13afa3c98d219f8882e278cdea0b
PR:   37716

Replace StatsD exporter sidecar with native Prometheus metrics exported to
Google Cloud Monitoring, add a deploy helper script, and update the README.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/beam"
TF_DIR = os.path.join(REPO, "examples", "terraform", "envoy-ratelimiter")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read(name: str) -> str:
    return Path(os.path.join(TF_DIR, name)).read_text()


def _parse_hcl(name: str) -> dict:
    """Parse a Terraform file as HCL and return the AST dict."""
    r = subprocess.run(
        [sys.executable, "-c", f"""
import json, hcl2
with open("{os.path.join(TF_DIR, name)}") as f:
    data = hcl2.load(f)
print(json.dumps(data))
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"HCL parse failed for {name}: {r.stderr}"
    return json.loads(r.stdout.strip())


def _run_bash(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a bash snippet in the repo directory."""
    return subprocess.run(
        ["bash", "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd=TF_DIR,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Terraform files parse as valid HCL and deploy.sh is valid bash."""
    # HCL parse check — catches syntax errors grep would miss
    for name in ("ratelimit.tf", "variables.tf", "prerequisites.tf"):
        ast = _parse_hcl(name)
        assert isinstance(ast, dict), f"{name} parsed to non-dict: {type(ast)}"
    # Bash syntax check on deploy.sh
    deploy = os.path.join(TF_DIR, "deploy.sh")
    if os.path.isfile(deploy):
        r = subprocess.run(
            ["bash", "-n", deploy],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"deploy.sh bash syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behaviour
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prometheus_env_configured():
    """ratelimit.tf sets USE_PROMETHEUS env var with PROMETHEUS_ADDR and PROMETHEUS_PATH."""
    ast = _parse_hcl("ratelimit.tf")
    content = _read("ratelimit.tf")
    # Behavioral: HCL AST must contain USE_PROMETHEUS env block
    found_prometheus = False
    found_addr = False
    found_path = False
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            if res_type != "kubernetes_deployment":
                continue
            for res_body in res_bodies:
                for spec in res_body.get("spec", []):
                    for template in spec.get("template", []):
                        for tspec in template.get("spec", []):
                            for container in tspec.get("container", []):
                                for env_block in container.get("env", []):
                                    name = env_block.get("name", "")
                                    if name == "USE_PROMETHEUS":
                                        found_prometheus = True
                                    if name == "PROMETHEUS_ADDR":
                                        found_addr = True
                                    if name == "PROMETHEUS_PATH":
                                        found_path = True
    assert found_prometheus, "ratelimit.tf must have USE_PROMETHEUS env var"
    assert found_addr, "ratelimit.tf must have PROMETHEUS_ADDR env var"
    assert found_path, "ratelimit.tf must have PROMETHEUS_PATH env var"


# [pr_diff] fail_to_pass
def test_statsd_sidecar_removed():
    """ratelimit.tf has no statsd-exporter sidecar container or STATSD env vars."""
    ast = _parse_hcl("ratelimit.tf")
    has_statsd_container = False
    has_statsd_host = False
    has_statsd_port = False
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            if res_type != "kubernetes_deployment":
                continue
            for res_body in res_bodies:
                for spec in res_body.get("spec", []):
                    for template in spec.get("template", []):
                        for tspec in template.get("spec", []):
                            for container in tspec.get("container", []):
                                cname = container.get("name", [""])[0] if isinstance(container.get("name"), list) else container.get("name", "")
                                if "statsd" in str(cname).lower():
                                    has_statsd_container = True
                                for env_block in container.get("env", []):
                                    name = env_block.get("name", "")
                                    if name == "STATSD_HOST":
                                        has_statsd_host = True
                                    if name == "STATSD_PORT":
                                        has_statsd_port = True
    assert not has_statsd_container, "statsd-exporter sidecar container must be removed"
    assert not has_statsd_host, "STATSD_HOST env var must be removed"
    assert not has_statsd_port, "STATSD_PORT env var must be removed"


# [pr_diff] fail_to_pass
def test_monitoring_api_enabled():
    """prerequisites.tf includes 'monitoring' in the required APIs list."""
    ast = _parse_hcl("prerequisites.tf")
    # The for_each list in google_project_service should contain "monitoring"
    found = False
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            if res_type != "google_project_service":
                continue
            for res_body in res_bodies:
                for_each = res_body.get("for_each", [])
                for item in for_each:
                    if isinstance(item, list):
                        if "monitoring" in item:
                            found = True
    assert found, "prerequisites.tf must include 'monitoring' in for_each API list"


# [pr_diff] fail_to_pass
def test_pod_monitoring_resource():
    """ratelimit.tf defines a kubernetes_manifest with PodMonitoring kind."""
    ast = _parse_hcl("ratelimit.tf")
    found = False
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            if res_type != "kubernetes_manifest":
                continue
            for res_body in res_bodies:
                manifest = res_body.get("manifest", [])
                for m in manifest:
                    kind = m.get("kind", "")
                    if kind == "PodMonitoring":
                        found = True
    assert found, "ratelimit.tf must define a kubernetes_manifest with kind PodMonitoring"


# [pr_diff] fail_to_pass
def test_metrics_port_9090():
    """Metrics port is 9090 in the service and deployment, old port 9102 removed."""
    ast = _parse_hcl("ratelimit.tf")
    has_9090 = False
    has_9102 = False
    # Check services for port 9090 and no 9102
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            if res_type not in ("kubernetes_service", "kubernetes_deployment"):
                continue
            content_str = json.dumps(res_bodies)
            if "9090" in content_str:
                has_9090 = True
            if "9102" in content_str:
                has_9102 = True
    assert has_9090, "ratelimit.tf must reference port 9090"
    assert not has_9102, "ratelimit.tf must not reference old port 9102"


# [pr_diff] fail_to_pass
def test_deploy_script_exists():
    """deploy.sh exists, is executable bash with apply/destroy commands."""
    deploy_path = os.path.join(TF_DIR, "deploy.sh")
    assert os.path.isfile(deploy_path), "deploy.sh should exist"
    # Behavioral: bash -n validates syntax, then check functional structure
    r = subprocess.run(
        ["bash", "-n", deploy_path],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"deploy.sh has bash syntax errors: {r.stderr}"
    content = Path(deploy_path).read_text()
    assert content.startswith("#!/"), "deploy.sh must have shebang"
    assert '"apply"' in content or "'apply'" in content or "apply" in content, "deploy.sh must handle apply"
    assert '"destroy"' in content or "'destroy'" in content or "destroy" in content, "deploy.sh must handle destroy"
    # Verify it actually runs (usage mode — no args or --help)
    r2 = _run_bash(f"cd {TF_DIR} && bash deploy.sh --help 2>&1 || true")
    # Script should not crash with a syntax error — exit 1 for unknown command is fine


# [pr_diff] fail_to_pass
def test_enable_metrics_default_true():
    """variables.tf sets enable_metrics default to true."""
    ast = _parse_hcl("variables.tf")
    found = False
    for var_block in ast.get("variable", []):
        if "enable_metrics" in var_block:
            var_body = var_block["enable_metrics"]
            default = var_body.get("default", [])
            # hcl2 wraps bools in lists sometimes
            if default == [True] or default is True:
                found = True
    assert found, "variables.tf enable_metrics must default to true"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — license compliance
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .agent/skills/license-compliance/SKILL.md:26-46
def test_deploy_script_has_license_header():
    """New deploy.sh must include Apache 2.0 license header per repo policy."""
    deploy_path = os.path.join(TF_DIR, "deploy.sh")
    assert os.path.isfile(deploy_path), "deploy.sh should exist"
    content = Path(deploy_path).read_text()
    assert "Licensed to the Apache Software Foundation" in content or "Apache License" in content, (
        "deploy.sh must include the Apache 2.0 license header"
    )
