"""
Task: trigger.dev-helm-split-ingress-and-update-readme
Repo: triggerdotdev/trigger.dev @ dc568e7f3edc168defc0a7e9afab382eba770bf1
PR:   2212

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

import yaml

REPO = "/workspace/trigger.dev"
HELM = Path(REPO) / "hosting" / "k8s" / "helm"


def _load_values():
    return yaml.safe_load((HELM / "values.yaml").read_text())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — YAML validity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_values_yaml_valid():
    """values.yaml must be valid YAML."""
    r = subprocess.run(
        ["python3", "-c", "import yaml, sys; yaml.safe_load(open(sys.argv[1]))", str(HELM / "values.yaml")],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"values.yaml is not valid YAML:\n{r.stderr}"


# [static] pass_to_pass
def test_production_example_valid():
    """values-production-example.yaml must be valid YAML."""
    r = subprocess.run(
        ["python3", "-c", "import yaml, sys; yaml.safe_load(open(sys.argv[1]))", str(HELM / "values-production-example.yaml")],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"values-production-example.yaml is not valid YAML:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_webapp_origin_in_values():
    """Origin config (appOrigin, loginOrigin, apiOrigin) must be under webapp, not config."""
    vals = _load_values()
    assert "config" not in vals or vals.get("config") is None, \
        "Top-level 'config' key should be removed; origins belong under 'webapp'"
    webapp = vals.get("webapp", {})
    assert "appOrigin" in webapp, "webapp.appOrigin missing from values.yaml"
    assert "loginOrigin" in webapp, "webapp.loginOrigin missing from values.yaml"
    assert "apiOrigin" in webapp, "webapp.apiOrigin missing from values.yaml"


# [pr_diff] fail_to_pass
def test_webapp_ingress_in_values():
    """Ingress config must be nested under webapp.ingress, not top-level ingress."""
    vals = _load_values()
    assert "ingress" not in vals or vals.get("ingress") is None, \
        "Top-level 'ingress' key should be removed; use webapp.ingress instead"
    webapp = vals.get("webapp", {})
    ingress = webapp.get("ingress", {})
    assert "enabled" in ingress, "webapp.ingress.enabled missing"
    assert "hosts" in ingress, "webapp.ingress.hosts missing"
    assert "className" in ingress, "webapp.ingress.className missing"


# [pr_diff] fail_to_pass
def test_registry_ingress_in_values():
    """Registry must have its own ingress section in values.yaml."""
    vals = _load_values()
    registry = vals.get("registry", {})
    ingress = registry.get("ingress", {})
    assert "enabled" in ingress, "registry.ingress.enabled missing"
    assert "hosts" in ingress, "registry.ingress.hosts missing"
    assert "className" in ingress, "registry.ingress.className missing"


# [pr_diff] fail_to_pass
def test_registry_ingress_template_exists():
    """A separate registry-ingress.yaml template must exist."""
    template = HELM / "templates" / "registry-ingress.yaml"
    assert template.exists(), "hosting/k8s/helm/templates/registry-ingress.yaml not found"
    content = template.read_text()
    assert ".Values.registry.ingress" in content, \
        "registry-ingress.yaml must reference .Values.registry.ingress"
    assert "registry" in content.lower(), \
        "registry-ingress.yaml must be for the registry service"


# [pr_diff] fail_to_pass
def test_webapp_ingress_template_references():
    """webapp-ingress.yaml must reference .Values.webapp.ingress, not .Values.ingress."""
    template = HELM / "templates" / "webapp-ingress.yaml"
    assert template.exists(), "hosting/k8s/helm/templates/webapp-ingress.yaml not found"
    content = template.read_text()
    assert ".Values.webapp.ingress" in content, \
        "webapp-ingress.yaml must reference .Values.webapp.ingress"
    # Must NOT still reference the old top-level .Values.ingress
    # (excluding lines that reference .Values.webapp.ingress)
    lines = content.splitlines()
    for line in lines:
        if ".Values.ingress" in line and ".Values.webapp.ingress" not in line and ".Values.registry.ingress" not in line:
            assert False, f"webapp-ingress.yaml still references old .Values.ingress: {line.strip()}"


# [pr_diff] fail_to_pass
def test_webapp_template_uses_webapp_origin():
    """webapp.yaml must reference .Values.webapp.appOrigin, not .Values.config.appOrigin."""
    template = HELM / "templates" / "webapp.yaml"
    content = template.read_text()
    assert ".Values.webapp.appOrigin" in content, \
        "webapp.yaml must use .Values.webapp.appOrigin"
    assert ".Values.config.appOrigin" not in content, \
        "webapp.yaml must not reference the old .Values.config.appOrigin"


# [pr_diff] fail_to_pass
def test_helpers_split_annotations():
    """_helpers.tpl must define separate annotation helpers for webapp and registry ingress."""
    helpers = (HELM / "templates" / "_helpers.tpl").read_text()
    assert "trigger-v4.webapp.ingress.annotations" in helpers, \
        "_helpers.tpl must define trigger-v4.webapp.ingress.annotations"
    assert "trigger-v4.registry.ingress.annotations" in helpers, \
        "_helpers.tpl must define trigger-v4.registry.ingress.annotations"
    assert 'define "trigger-v4.ingress.annotations"' not in helpers, \
        "_helpers.tpl must not still define the old trigger-v4.ingress.annotations"


# [pr_diff] fail_to_pass
def test_registry_host_no_port_concat():
    """Registry host helper must not concatenate host:port; host includes port if needed."""
    helpers = (HELM / "templates" / "_helpers.tpl").read_text()
    # Find the registry.host define block
    assert ".Values.registry.external.port" not in helpers, \
        "_helpers.tpl should not reference .Values.registry.external.port anymore"


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_webapp_ingress():
    """Helm README must document webapp.ingress config (not top-level ingress)."""
    readme = (HELM / "README.md").read_text()
    # The README should show the new nested ingress pattern
    assert "webapp:" in readme, "README should show webapp: section"
    # Must document webapp.ingress, not bare ingress:
    # Look for the pattern where ingress is nested under webapp
    assert "ingress:" in readme, "README should document ingress configuration"
    # Check it shows the new split pattern — webapp ingress block
    lines = readme.splitlines()
    found_webapp_ingress = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "webapp:" or stripped.startswith("webapp:"):
            # Look ahead for ingress nested under it
            for j in range(i + 1, min(i + 10, len(lines))):
                if "ingress:" in lines[j] and lines[j].startswith("  "):
                    found_webapp_ingress = True
                    break
    assert found_webapp_ingress, \
        "README must show ingress nested under webapp (webapp.ingress pattern)"


# [pr_diff] fail_to_pass
def test_readme_documents_registry_ingress():
    """Helm README must document separate registry ingress configuration."""
    readme = (HELM / "README.md").read_text()
    # Must document registry ingress as a separate block
    lines = readme.splitlines()
    found_registry_ingress = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "registry:" or stripped.startswith("registry:"):
            for j in range(i + 1, min(i + 10, len(lines))):
                if "ingress:" in lines[j]:
                    found_registry_ingress = True
                    break
    assert found_registry_ingress, \
        "README must document registry.ingress configuration"


# [pr_diff] fail_to_pass
def test_readme_no_toplevel_ingress_example():
    """README must not show the old top-level ingress config pattern as the primary example."""
    readme = (HELM / "README.md").read_text()
    lines = readme.splitlines()
    # In the Ingress Configuration section, the old pattern was:
    #   ingress:
    #     enabled: true
    # (at column 0 - bare top-level, not nested under webapp/registry)
    in_ingress_section = False
    for line in lines:
        if "### Ingress Configuration" in line:
            in_ingress_section = True
            continue
        if in_ingress_section and line.startswith("### "):
            break
        # Only flag bare 'ingress:' at column 0 (not indented/nested)
        if in_ingress_section and line.startswith("ingress:"):
            assert False, "README Ingress Configuration section still shows bare 'ingress:' at top level"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Helm chart structure validation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_chart_yaml_valid():
    """Chart.yaml must be valid YAML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import yaml, sys; yaml.safe_load(open(sys.argv[1]))",
         str(HELM / "Chart.yaml")],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Chart.yaml is not valid YAML:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_chart_has_required_fields():
    """Chart.yaml must have required fields (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import yaml, sys; c = yaml.safe_load(open(sys.argv[1])); "
         "assert c['apiVersion'] == 'v2', 'apiVersion must be v2'; "
         "assert 'dependencies' in c, 'must have dependencies'; "
         "print('OK')",
         str(HELM / "Chart.yaml")],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Chart.yaml missing required fields:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_values_has_required_sections():
    """values.yaml must have required top-level sections (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import yaml, sys; v = yaml.safe_load(open(sys.argv[1])); "
         "required = ['webapp', 'registry', 'supervisor', 'postgres', 'redis']; "
         "missing = [r for r in required if r not in v]; "
         "assert not missing, f'Missing sections: {missing}'; "
         "print('OK')",
         str(HELM / "values.yaml")],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"values.yaml missing required sections:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_templates_have_balanced_braces():
    """Go template files must have balanced braces (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import os, sys\n"
         "errors = []\n"
         "templates_dir = 'hosting/k8s/helm/templates'\n"
         "for root, _, files in os.walk(templates_dir):\n"
         "    for p in files:\n"
         "        path = os.path.join(root, p)\n"
         "        content = open(path).read()\n"
         "        if content.count('{{') != content.count('}}'):\n"
         "            errors.append(f'{p}: unbalanced braces')\n"
         "if errors:\n"
         "    print('Errors:', errors)\n"
         "    sys.exit(1)\n"
         "print('OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Template syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_helpers_has_required_patterns():
    """_helpers.tpl must define required helper patterns (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c",
         "import sys; content = open(sys.argv[1]).read(); "
         "required = ['trigger-v4.fullname', 'trigger-v4.labels', 'trigger-v4.registry.host']; "
         "missing = [r for r in required if r not in content]; "
         "assert not missing, f'Missing patterns: {missing}'; "
         "print('OK')",
         str(HELM / "templates" / "_helpers.tpl")],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"_helpers.tpl missing required patterns:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — validation template correctness
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_validation_template_no_port():
    """validate-external-config.yaml must not require registry.external.port."""
    validate = (HELM / "templates" / "validate-external-config.yaml").read_text()
    assert ".Values.registry.external.port" not in validate, \
        "Validation template should not check for registry.external.port"
    assert ".Values.registry.external.host" in validate, \
        "Validation template should still check for registry.external.host"
