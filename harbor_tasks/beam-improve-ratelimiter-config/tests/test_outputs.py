"""
Task: beam-improve-ratelimiter-config
Repo: apache/beam @ bab2374552da7a1f7fbe783408c3b4159e3f0391
PR:   37630

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/beam"
TF_DIR = Path(REPO) / "examples" / "terraform" / "envoy-ratelimiter"


def _install_terraform():
    """Install terraform binary to /tmp/terraform."""
    install_cmd = """
        apt-get update -qq && apt-get install -y -qq unzip >/dev/null 2>&1 &&
        curl -fsSL -o /tmp/terraform.zip
        https://releases.hashicorp.com/terraform/1.6.6/terraform_1.6.6_linux_amd64.zip &&
        unzip -qo /tmp/terraform.zip -d /tmp/
    """.strip().replace("\n        ", " ")
    r = subprocess.run(
        ["bash", "-c", install_cmd],
        capture_output=True, text=True, timeout=120, cwd="/tmp"
    )
    if r.returncode != 0:
        raise RuntimeError(f"Terraform installation failed: {r.stderr}")


def _terraform_init():
    """Initialize terraform in the TF_DIR."""
    r = subprocess.run(
        ["/tmp/terraform", "init", "-backend=false", "-input=false"],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    if r.returncode != 0:
        raise RuntimeError(f"Terraform init failed: {r.stderr}")


def _terraform_plan(vars_dict=None, out_path="/tmp/plan.tfplan"):
    """Run terraform plan with optional variables, output to out_path."""
    cmd = ["/tmp/terraform", "plan", f"-out={out_path}"]
    if vars_dict:
        for k, v in vars_dict.items():
            if isinstance(v, bool):
                val = "true" if v else "false"
            else:
                val = str(v)
            cmd.append(f"-var={k}={val}")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=TF_DIR)
    if r.returncode != 0:
        raise RuntimeError(f"Terraform plan failed: {r.stderr}")
    return out_path


def _terraform_show_json(plan_path="/tmp/plan.tfplan"):
    """Convert terraform plan to JSON and return parsed dict."""
    r = subprocess.run(
        ["/tmp/terraform", "show", "-json", plan_path],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    if r.returncode != 0:
        raise RuntimeError(f"Terraform show failed: {r.stderr}")
    return json.loads(r.stdout)


def _get_planned_resources(plan_json):
    """Extract planned resources from terraform plan JSON."""
    resources = {}
    # Check resource_changes
    for rc in plan_json.get("resource_changes", []):
        addr = rc.get("address", "")
        change = rc.get("change", {})
        actions = rc.get("change", {}).get("actions", [])
        # Include resources being created, updated, or no-op (existing)
        if any(a in actions for a in ["create", "update", "no-op"]):
            resources[addr] = {
                "type": rc.get("type", ""),
                "name": rc.get("name", ""),
                "actions": actions,
                "after": change.get("after", {}),
            }
    return resources


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------


def test_repo_terraform_readme_has_variable_table():
    """README.md contains the expected Terraform variables table section (pass_to_pass, repo_tests)."""
    readme = (TF_DIR / "README.md").read_text()

    # Check for the variables table header
    assert "| Name |" in readme or "|Variable" in readme or "|variable" in readme.lower(), (
        "README.md missing variables table header"
    )
    # Check for project_id in the table (required variable that should be documented)
    assert "project_id" in readme, "README.md should document project_id variable"
    # Check for ratelimit_config_yaml (key required variable)
    assert "ratelimit_config_yaml" in readme, "README.md should document ratelimit_config_yaml"


def test_repo_terraform_readme_has_examples_section():
    """README.md has the Beam pipeline examples section (pass_to_pass, repo_tests)."""
    readme = (TF_DIR / "README.md").read_text()

    # Check for examples section structure
    assert "Example" in readme and "Pipeline" in readme, (
        "README.md missing Beam pipeline examples section"
    )
    # Check for the rate limiter example links
    assert "rate_limiter" in readme.lower() or "RateLimiter" in readme, (
        "README.md should reference rate limiter examples"
    )


def test_repo_gke_tf_structure():
    """gke.tf has the expected GKE cluster resource structure (pass_to_pass, repo_tests)."""
    content = (TF_DIR / "gke.tf").read_text()

    # Check for the GKE cluster resource
    assert "google_container_cluster" in content, (
        "gke.tf missing google_container_cluster resource"
    )
    # Check for private cluster configuration (key feature)
    assert "private_cluster_config" in content, (
        "gke.tf missing private_cluster_config"
    )
    # Check for required variables being used (cluster_name, control_plane_cidr, deletion_protection)
    assert "var.cluster_name" in content, "gke.tf should reference var.cluster_name"
    assert "var.control_plane_cidr" in content, "gke.tf should reference var.control_plane_cidr"
    assert "var.deletion_protection" in content, "gke.tf should reference var.deletion_protection"


def test_repo_ratelimit_tf_has_k8s_resources():
    """ratelimit.tf contains the expected Kubernetes resources (pass_to_pass, repo_tests)."""
    content = (TF_DIR / "ratelimit.tf").read_text()

    # Check for key Kubernetes resources
    assert "kubernetes_deployment" in content, "ratelimit.tf missing kubernetes_deployment"
    assert "kubernetes_service" in content, "ratelimit.tf missing kubernetes_service"
    assert "kubernetes_config_map" in content, "ratelimit.tf missing kubernetes_config_map"
    assert "kubernetes_horizontal_pod_autoscaler_v2" in content, (
        "ratelimit.tf missing kubernetes_horizontal_pod_autoscaler_v2"
    )


def test_repo_variables_tf_has_required_vars():
    """variables.tf defines the expected required variables (pass_to_pass, repo_tests)."""
    content = (TF_DIR / "variables.tf").read_text()

    # Required variables that must exist
    required_vars = ["project_id", "vpc_name", "subnet_name", "ratelimit_config_yaml"]
    for var in required_vars:
        pattern = rf'variable\s+"{var}"'
        assert re.search(pattern, content), f"variables.tf missing required variable: {var}"


def test_repo_prerequisites_tf_structure():
    """prerequisites.tf enables required GCP APIs (pass_to_pass, repo_tests)."""
    content = (TF_DIR / "prerequisites.tf").read_text()

    # Check for service enablement resources
    assert "google_project_service" in content, (
        "prerequisites.tf missing google_project_service resources"
    )
    # Check for essential APIs
    essential_apis = ["container", "iam", "compute"]
    for api in essential_apis:
        assert api in content, f"prerequisites.tf should enable {api} API"


def test_syntax_check():
    """Terraform files have balanced braces (basic structural validation)."""
    for tf_file in ["ratelimit.tf", "variables.tf", "gke.tf"]:
        content = (TF_DIR / tf_file).read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert opens == closes, (
            f"{tf_file}: unbalanced braces — {opens} opening vs {closes} closing"
        )


def test_terraform_validate():
    """Terraform configuration passes validation (pass_to_pass)."""
    _install_terraform()

    # Initialize terraform
    r = subprocess.run(
        ["/tmp/terraform", "init", "-backend=false", "-input=false"],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    assert r.returncode == 0, f"Terraform init failed:\n{r.stderr[-500:]}"

    # Validate terraform
    r = subprocess.run(
        ["/tmp/terraform", "validate"],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    assert r.returncode == 0, f"Terraform validate failed:\n{r.stderr[-500:]}" + \
                              f"\nstdout:\n{r.stdout[-500:]}"


def test_terraform_files_exist():
    """Required Terraform files exist and are readable (pass_to_pass)."""
    required_files = ["ratelimit.tf", "variables.tf", "gke.tf", "provider.tf"]
    for tf_file in required_files:
        fpath = TF_DIR / tf_file
        assert fpath.exists(), f"Required file {tf_file} does not exist"
        assert fpath.stat().st_size > 0, f"Required file {tf_file} is empty"


def test_terraform_providers():
    """Terraform providers are correctly configured (pass_to_pass)."""
    _install_terraform()

    # Initialize terraform
    r = subprocess.run(
        ["/tmp/terraform", "init", "-backend=false", "-input=false"],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    assert r.returncode == 0, f"Terraform init failed:\n{r.stderr[-500:]}"

    # Check providers
    r = subprocess.run(
        ["/tmp/terraform", "providers"],
        capture_output=True, text=True, timeout=60, cwd=TF_DIR
    )
    assert r.returncode == 0, f"Terraform providers check failed:\n{r.stderr[-500:]}"
    # Verify required providers are present
    assert "hashicorp/google" in r.stdout, "Missing required provider: hashicorp/google"
    assert "hashicorp/kubernetes" in r.stdout, "Missing required provider: hashicorp/kubernetes"


def test_required_variables_exist():
    """Required variables are defined in variables.tf (pass_to_pass, static)."""
    content = (TF_DIR / "variables.tf").read_text()
    required_vars = ["project_id", "vpc_name", "subnet_name", "ratelimit_config_yaml"]
    for var in required_vars:
        pattern = rf'variable\s+"{var}"'
        assert re.search(pattern, content), f"Required variable '{var}' not found in variables.tf"


def test_outputs_configured():
    """Outputs are defined in outputs.tf (pass_to_pass, static)."""
    content = (TF_DIR / "outputs.tf").read_text()
    required_outputs = ["cluster_name", "load_balancer_ip"]
    for output in required_outputs:
        pattern = rf'output\s+"{output}"'
        assert re.search(pattern, content), f"Required output '{output}' not found in outputs.tf"


def test_prerequisites_configured():
    """Prerequisites.tf has required API services (pass_to_pass, static)."""
    content = (TF_DIR / "prerequisites.tf").read_text()
    required_services = ["container", "iam", "compute"]
    for service in required_services:
        assert service in content, f"Required service '{service}' not found in prerequisites.tf"


def test_terraform_fmt_clean_files():
    """Terraform formatting is correct for clean files (pass_to_pass, repo_tests)."""
    _install_terraform()

    # Check formatting for files that are clean in base commit
    clean_files = ["outputs.tf", "provider.tf", "prerequisites.tf", "network.tf"]
    for tf_file in clean_files:
        r = subprocess.run(
            ["/tmp/terraform", "fmt", "-check", str(TF_DIR / tf_file)],
            capture_output=True, text=True, timeout=60, cwd="/tmp"
        )
        assert r.returncode == 0, (
            f"Terraform fmt check failed for {tf_file}:\n{r.stderr[-500:]}"
        )


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using terraform plan
# -----------------------------------------------------------------------------


def test_namespace_variable_defined():
    """variables.tf defines a namespace variable that accepts and applies custom values."""
    _install_terraform()
    _terraform_init()

    # Plan with default namespace value - should create resources in that namespace
    plan_path = _terraform_plan(vars_dict={"enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Find the kubernetes_namespace resource
    ns_resources = {k: v for k, v in resources.items() if v["type"] == "kubernetes_namespace"}
    assert len(ns_resources) >= 1, (
        "Expected at least 1 kubernetes_namespace resource to be planned"
    )

    # Check that at least one namespace resource has a name defined
    ns_found = False
    for addr, res in ns_resources.items():
        after = res.get("after", {})
        metadata = after.get("metadata", {})
        if metadata.get("name"):
            ns_found = True
            break
    assert ns_found, "kubernetes_namespace resource must have a name defined"


def test_namespace_variable_accepts_custom_value():
    """The namespace variable accepts custom values and resources use that namespace."""
    _install_terraform()
    _terraform_init()

    # Plan with custom namespace
    custom_ns = "custom-ratelimit-ns"
    plan_path = _terraform_plan(vars_dict={"namespace": custom_ns, "enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Verify the namespace resource itself uses the custom value
    ns_resources = {k: v for k, v in resources.items() if v["type"] == "kubernetes_namespace"}
    assert len(ns_resources) >= 1, "Expected kubernetes_namespace resource"

    custom_ns_used = False
    for addr, res in ns_resources.items():
        after = res.get("after", {})
        metadata = after.get("metadata", {})
        if metadata.get("name") == custom_ns:
            custom_ns_used = True
            break
    assert custom_ns_used, f"kubernetes_namespace should use the custom namespace value '{custom_ns}'"


def test_enable_metrics_variable_defined():
    """variables.tf defines an enable_metrics boolean variable with false default."""
    _install_terraform()
    _terraform_init()

    # Plan with enable_metrics=false (should be default behavior)
    plan_path = _terraform_plan(vars_dict={"enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # When metrics are disabled, the ratelimit deployment should NOT have statsd-exporter container
    deployment = None
    for addr, res in resources.items():
        if res["type"] == "kubernetes_deployment" and res["name"] == "ratelimit":
            deployment = res
            break

    assert deployment is not None, "ratelimit deployment should be planned"

    # Check containers in the deployment
    after = deployment.get("after", {})
    spec = after.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})
    containers = pod_spec.get("container", [])

    # Verify deployment structure is valid
    assert isinstance(containers, list), "containers should be a list"
    assert len(containers) >= 1, "ratelimit deployment should have at least 1 container"


def test_enable_metrics_true_includes_sidecar():
    """When enable_metrics=true, the statsd-exporter sidecar is included in plan."""
    _install_terraform()
    _terraform_init()

    # Plan with enable_metrics=true
    plan_path = _terraform_plan(vars_dict={"enable_metrics": True})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Find ratelimit deployment
    deployment = None
    for addr, res in resources.items():
        if res["type"] == "kubernetes_deployment" and res["name"] == "ratelimit":
            deployment = res
            break

    assert deployment is not None, "ratelimit deployment should be planned"

    # Check for statsd-exporter container
    after = deployment.get("after", {})
    spec = after.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})
    containers = pod_spec.get("container", [])

    container_names = [c.get("name", "") for c in containers]
    assert "statsd-exporter" in container_names, (
        "When enable_metrics=true, ratelimit deployment should include statsd-exporter container"
    )


def test_enable_metrics_false_excludes_sidecar():
    """When enable_metrics=false, the statsd-exporter sidecar is NOT in plan."""
    _install_terraform()
    _terraform_init()

    # Plan with enable_metrics=false
    plan_path = _terraform_plan(vars_dict={"enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Find ratelimit deployment
    deployment = None
    for addr, res in resources.items():
        if res["type"] == "kubernetes_deployment" and res["name"] == "ratelimit":
            deployment = res
            break

    assert deployment is not None, "ratelimit deployment should be planned"

    # Check containers - statsd-exporter should NOT be present
    after = deployment.get("after", {})
    spec = after.get("spec", {})
    template = spec.get("template", {})
    pod_spec = template.get("spec", {})
    containers = pod_spec.get("container", [])

    container_names = [c.get("name", "") for c in containers]
    assert "statsd-exporter" not in container_names, (
        "When enable_metrics=false, ratelimit deployment should NOT include statsd-exporter container"
    )


def test_kubernetes_namespace_resource():
    """ratelimit.tf creates a kubernetes_namespace resource when planned."""
    _install_terraform()
    _terraform_init()

    plan_path = _terraform_plan(vars_dict={"enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Verify at least one kubernetes_namespace resource exists
    ns_count = sum(1 for res in resources.values() if res["type"] == "kubernetes_namespace")
    assert ns_count >= 1, f"Expected at least 1 kubernetes_namespace resource, found {ns_count}"


def test_all_k8s_resources_use_configured_namespace():
    """All Kubernetes resources are planned to be created in the configured namespace."""
    _install_terraform()
    _terraform_init()

    # Test with a custom namespace to verify its applied consistently
    custom_ns = "test-ns-123"
    plan_path = _terraform_plan(vars_dict={"namespace": custom_ns, "enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Collect all kubernetes resources (except namespace itself)
    k8s_resources = {}
    for addr, res in resources.items():
        if res["type"].startswith("kubernetes_") and res["type"] != "kubernetes_namespace":
            k8s_resources[addr] = res

    # Verify we have the expected number of k8s resources
    assert len(k8s_resources) >= 5, f"Expected at least 5 namespaced k8s resources, found {len(k8s_resources)}"

    # Verify each resource has the namespace set correctly
    incorrect = []
    for addr, res in k8s_resources.items():
        after = res.get("after", {})
        metadata = after.get("metadata", {})
        ns = metadata.get("namespace", "")
        if ns != custom_ns:
            incorrect.append(f"{addr}: namespace='{ns}' (expected '{custom_ns}')")

    assert len(incorrect) == 0, f"Resources with incorrect namespace: {incorrect}"


def test_use_statsd_env_conditional():
    """USE_STATSD env var changes based on enable_metrics variable value."""
    _install_terraform()
    _terraform_init()

    # Plan with enable_metrics=true
    plan_path_true = _terraform_plan(vars_dict={"enable_metrics": True}, out_path="/tmp/plan_true.tfplan")
    plan_json_true = _terraform_show_json(plan_path_true)
    resources_true = _get_planned_resources(plan_json_true)

    # Plan with enable_metrics=false
    plan_path_false = _terraform_plan(vars_dict={"enable_metrics": False}, out_path="/tmp/plan_false.tfplan")
    plan_json_false = _terraform_show_json(plan_path_false)
    resources_false = _get_planned_resources(plan_json_false)

    # Extract USE_STATSD value from both plans
    def get_use_statsd_value(resources):
        for addr, res in resources.items():
            if res["type"] == "kubernetes_deployment" and res["name"] == "ratelimit":
                after = res.get("after", {})
                spec = after.get("spec", {})
                template = spec.get("template", {})
                pod_spec = template.get("spec", {})
                containers = pod_spec.get("container", [])
                for container in containers:
                    if container.get("name") == "ratelimit":
                        env_list = container.get("env", [])
                        for env in env_list:
                            if env.get("name") == "USE_STATSD":
                                return env.get("value")
        return None

    value_true = get_use_statsd_value(resources_true)
    value_false = get_use_statsd_value(resources_false)

    # Verify values are different and correct
    assert value_true == "true", f"USE_STATSD should be 'true' when enable_metrics=true, got: {value_true}"
    assert value_false == "false", f"USE_STATSD should be 'false' when enable_metrics=false, got: {value_false}"


def test_metrics_ports_conditional():
    """Metrics ports are only exposed when enable_metrics=true."""
    _install_terraform()
    _terraform_init()

    # Plan with enable_metrics=false
    plan_path = _terraform_plan(vars_dict={"enable_metrics": False})
    plan_json = _terraform_show_json(plan_path)
    resources = _get_planned_resources(plan_json)

    # Check ratelimit service - should not have metrics port when disabled
    svc = None
    for addr, res in resources.items():
        if res["type"] == "kubernetes_service" and res["name"] == "ratelimit":
            svc = res
            break

    if svc:
        after = svc.get("after", {})
        spec = after.get("spec", {})
        ports = spec.get("port", [])
        port_names = [p.get("name", "") for p in ports]
        assert "metrics" not in port_names, (
            "metrics port should not exist in ratelimit service when enable_metrics=false"
        )

    # Now test with enable_metrics=true - should have metrics port
    plan_path_true = _terraform_plan(vars_dict={"enable_metrics": True}, out_path="/tmp/plan_metrics.tfplan")
    plan_json_true = _terraform_show_json(plan_path_true)
    resources_true = _get_planned_resources(plan_json_true)

    svc_true = None
    for addr, res in resources_true.items():
        if res["type"] == "kubernetes_service" and res["name"] == "ratelimit":
            svc_true = res
            break

    if svc_true:
        after = svc_true.get("after", {})
        spec = after.get("spec", {})
        ports = spec.get("port", [])
        port_names = [p.get("name", "") for p in ports]
        assert "metrics" in port_names, (
            "metrics port should exist in ratelimit service when enable_metrics=true"
        )
