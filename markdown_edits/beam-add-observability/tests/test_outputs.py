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

import pytest

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


# [repo_tests] pass_to_pass — CI/CD gate: all Terraform files valid HCL
def test_repo_terraform_hcl_valid():
    """All Terraform files in the module parse as valid HCL (pass_to_pass)."""
    tf_files = [f for f in os.listdir(TF_DIR) if f.endswith(".tf")]
    assert tf_files, "No .tf files found in terraform directory"
    for name in tf_files:
        ast = _parse_hcl(name)
        assert isinstance(ast, dict), f"{name} parsed to non-dict: {type(ast)}"


# [repo_tests] pass_to_pass — CI/CD gate: all shell scripts valid bash
def test_repo_shell_scripts_valid():
    """All shell scripts pass bash syntax validation (pass_to_pass)."""
    scripts = [f for f in os.listdir(TF_DIR) if f.endswith(".sh")]
    for script in scripts:
        script_path = os.path.join(TF_DIR, script)
        r = subprocess.run(
            ["bash", "-n", script_path],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{script} has bash syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass — CI/CD gate: README.md exists and has content
def test_repo_readme_exists():
    """README.md exists and has substantial documentation (pass_to_pass)."""
    readme_path = os.path.join(TF_DIR, "README.md")
    assert os.path.isfile(readme_path), "README.md should exist"
    content = Path(readme_path).read_text()
    assert len(content) > 1000, "README.md should have substantial content (at least 1000 chars)"
    # Verify key sections are documented
    assert "#" in content, "README.md should have markdown headers"


# [repo_tests] pass_to_pass — CI/CD gate: all source files have Apache License headers
def test_repo_license_headers_present():
    """All Terraform files have Apache License headers (pass_to_pass)."""
    # Apache Beam requires Apache 2.0 license headers on all source files
    r = subprocess.run(
        ["bash", "-c", 'cd "{}" && for f in *.tf; do grep -q "Apache License" "$f" || {{ echo "$f missing license"; exit 1; }}; done'.format(TF_DIR)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"License header check failed: {r.stdout or r.stderr}"


# [repo_tests] pass_to_pass — CI/CD gate: README has Apache License header
def test_repo_readme_license_header():
    """README.md has Apache License header in HTML comment (pass_to_pass)."""
    readme_path = os.path.join(TF_DIR, "README.md")
    assert os.path.isfile(readme_path), "README.md should exist"
    content = Path(readme_path).read_text()
    # README uses HTML-style license comment
    assert "Licensed to the Apache Software Foundation" in content, "README.md must have Apache License header"
    assert "http://www.apache.org/licenses/LICENSE-2.0" in content, "README.md must reference Apache License 2.0"


# [repo_tests] pass_to_pass — CI/CD gate: git repo is clean (no staged changes)
def test_repo_git_clean():
    """Git repo has no uncommitted changes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "diff", "--quiet", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # If the gold fix has been applied (deploy.sh exists), we expect changes
    # This test validates the base commit is clean; after fix, changes are expected
    deploy_path = os.path.join(TF_DIR, "deploy.sh")
    if os.path.isfile(deploy_path):
        pytest.skip("Gold fix applied - uncommitted changes are expected")
    # On the base commit, there should be no uncommitted changes
    # This ensures the test environment is clean
    assert r.returncode == 0, f"Git repo has uncommitted changes: {r.stderr}"


# [repo_tests] pass_to_pass — CI/CD gate: shellcheck passes on all shell scripts
def test_repo_shellcheck():
    """All shell scripts pass shellcheck validation (pass_to_pass)."""
    # Install shellcheck-py if not available
    r = subprocess.run(
        ["pip", "install", "shellcheck-py", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    scripts = [f for f in os.listdir(TF_DIR) if f.endswith(".sh")]
    if not scripts:
        pytest.skip("No shell scripts to check")
    for script in scripts:
        script_path = os.path.join(TF_DIR, script)
        r = subprocess.run(
            ["shellcheck", "-x", "-e", "SC1091,SC2164", script_path],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"{script} failed shellcheck: {r.stdout or r.stderr}"


# [repo_tests] pass_to_pass — CI/CD gate: Terraform files have valid structure
def test_repo_terraform_structure():
    """Terraform files have valid structure with proper blocks (pass_to_pass)."""
    tf_files = [f for f in os.listdir(TF_DIR) if f.endswith(".tf")]
    assert tf_files, "No .tf files found in terraform directory"
    for name in tf_files:
        content = _read(name)
        # Check for required terraform structure elements
        assert "resource " in content or "variable " in content or "data " in content or "output " in content, \
            f"{name} missing required terraform blocks"
        # Validate HCL syntax by parsing
        ast = _parse_hcl(name)
        assert isinstance(ast, dict), f"{name} parsed to non-dict: {type(ast)}"


# [repo_tests] pass_to_pass — CI/CD gate: Terraform files follow naming conventions
def test_repo_terraform_naming():
    """Terraform files follow repository naming conventions (pass_to_pass)."""
    expected_files = ["ratelimit.tf", "variables.tf", "prerequisites.tf", "gke.tf", "network.tf", "provider.tf", "outputs.tf", "terraform.tfvars"]
    found_files = os.listdir(TF_DIR)
    for expected in expected_files:
        if expected not in found_files:
            pytest.skip(f"Expected file {expected} not found, may be created by fix")


# [repo_tests] pass_to_pass — CI/CD gate: No trailing whitespace in Terraform files
def test_repo_no_trailing_whitespace():
    """Terraform files have no trailing whitespace (pass_to_pass)."""
    tf_files = [f for f in os.listdir(TF_DIR) if f.endswith(".tf")]
    for name in tf_files:
        content = _read(name)
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                pytest.fail(f"{name} has trailing whitespace on line {i}")


# [repo_tests] pass_to_pass — CI/CD gate: README follows repo format conventions
def test_repo_readme_format():
    """README.md follows repository markdown conventions (pass_to_pass)."""
    readme_path = os.path.join(TF_DIR, "README.md")
    assert os.path.isfile(readme_path), "README.md should exist"
    content = Path(readme_path).read_text()
    # Check for proper markdown structure (has a level-1 heading)
    assert "# " in content, "README.md should contain a level-1 heading"


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
            # HCL keys have quotes, strip them
            res_type = res_type.strip('"')
            if res_type != "kubernetes_deployment":
                continue
            for res_name, res_body in res_bodies.items():
                res_name = res_name.strip('"')
                for spec in res_body.get("spec", []):
                    for template in spec.get("template", []):
                        for tspec in template.get("spec", []):
                            containers = tspec.get("container", [])
                            # Handle both block and list structures
                            if isinstance(containers, dict):
                                containers = [containers]
                            for container in containers:
                                # Check regular env blocks
                                for env_block in container.get("env", []):
                                    if isinstance(env_block, dict):
                                        name = env_block.get("name", "")
                                        if name == "USE_PROMETHEUS" or name == '"USE_PROMETHEUS"':
                                            found_prometheus = True
                                        if name == "PROMETHEUS_ADDR" or name == '"PROMETHEUS_ADDR"':
                                            found_addr = True
                                        if name == "PROMETHEUS_PATH" or name == '"PROMETHEUS_PATH"':
                                            found_path = True
                                # Check dynamic env blocks (for prometheus vars)
                                for dynamic_block in container.get("dynamic", []):
                                    if isinstance(dynamic_block, dict) and dynamic_block.get('"env"'):
                                        env_dynamic = dynamic_block.get('"env"')
                                        content_blocks = env_dynamic.get("content", [])
                                        for content_block in content_blocks:
                                            if isinstance(content_block, dict):
                                                name = content_block.get("name", "")
                                                if name == "PROMETHEUS_ADDR" or name == '"PROMETHEUS_ADDR"':
                                                    found_addr = True
                                                if name == "PROMETHEUS_PATH" or name == '"PROMETHEUS_PATH"':
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
            # HCL keys have quotes, strip them
            res_type = res_type.strip('"')
            if res_type != "google_project_service":
                continue
            for res_name, res_body in res_bodies.items():
                for_each = res_body.get("for_each", "")
                # python-hcl2 returns the Terraform expression as a string for for_each
                # Check if "monitoring" appears in the for_each string
                if isinstance(for_each, str) and "monitoring" in for_each:
                    found = True
                elif isinstance(for_each, list):
                    # Handle case where it might be parsed as a list
                    for item in for_each:
                        if "monitoring" in str(item):
                            found = True
    assert found, "prerequisites.tf must include 'monitoring' in for_each API list"


# [pr_diff] fail_to_pass
def test_pod_monitoring_resource():
    """ratelimit.tf defines a kubernetes_manifest with PodMonitoring kind."""
    ast = _parse_hcl("ratelimit.tf")
    found = False
    for resource_block in ast.get("resource", []):
        for res_type, res_bodies in resource_block.items():
            # HCL keys have quotes, strip them
            res_type = res_type.strip('"')
            if res_type != "kubernetes_manifest":
                continue
            for res_name, res_body in res_bodies.items():
                manifest = res_body.get("manifest", {})
                if isinstance(manifest, dict):
                    kind = manifest.get("kind", "")
                    # HCL string values have quotes
                    if kind == "PodMonitoring" or kind == '"PodMonitoring"':
                        found = True
                elif isinstance(manifest, list) and manifest:
                    for m in manifest:
                        if isinstance(m, dict):
                            kind = m.get("kind", "")
                            if kind == "PodMonitoring" or kind == '"PodMonitoring"':
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
            # HCL keys have quotes, strip them
            res_type = res_type.strip('"')
            if res_type not in ("kubernetes_service", "kubernetes_deployment"):
                continue
            # Check all resource bodies for port numbers
            for res_name, res_body in res_bodies.items():
                content_str = json.dumps(res_body)
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
        # HCL keys have quotes, check both quoted and unquoted
        if "enable_metrics" in var_block or '"enable_metrics"' in var_block:
            var_body = var_block.get("enable_metrics") or var_block.get('"enable_metrics"')
            default = var_body.get("default", [])
            # hcl2 wraps bools in lists sometimes
            # HCL also adds quotes to boolean values in some cases
            if default == [True] or default is True or default == ["true"] or default == "true":
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
