"""
Task: trigger-helm-registry-ingress-split
Repo: trigger.dev @ dc568e7f3edc168defc0a7e9afab382eba770bf1
PR:   2212

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import yaml
from pathlib import Path

REPO = "/workspace/trigger.dev"
HELM = Path(REPO) / "hosting" / "k8s" / "helm"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / YAML validity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified YAML files must parse without errors."""
    for fname in ["values.yaml", "values-production-example.yaml", "Chart.yaml"]:
        path = HELM / fname
        assert path.exists(), f"{fname} missing"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), f"{fname} did not parse as a YAML mapping"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_values_webapp_origin():
    """Origin config (appOrigin, loginOrigin, apiOrigin) must be under webapp, not config."""
    with open(HELM / "values.yaml") as f:
        vals = yaml.safe_load(f)
    # Must NOT have top-level config with origins
    if "config" in vals:
        assert "appOrigin" not in vals["config"], \
            "appOrigin should not be under top-level config"
    # Must have origins under webapp
    webapp = vals.get("webapp", {})
    assert "appOrigin" in webapp, "webapp.appOrigin missing from values.yaml"
    assert "loginOrigin" in webapp, "webapp.loginOrigin missing from values.yaml"
    assert "apiOrigin" in webapp, "webapp.apiOrigin missing from values.yaml"


# [pr_diff] fail_to_pass
def test_values_webapp_ingress():
    """Ingress must be under webapp.ingress, not top-level ingress."""
    with open(HELM / "values.yaml") as f:
        vals = yaml.safe_load(f)
    # Must NOT have top-level ingress
    assert "ingress" not in vals, \
        "Top-level 'ingress' key should be removed from values.yaml"
    # Must have webapp.ingress
    webapp = vals.get("webapp", {})
    ingress = webapp.get("ingress", {})
    assert "enabled" in ingress, "webapp.ingress.enabled missing"
    assert "hosts" in ingress, "webapp.ingress.hosts missing"


# [pr_diff] fail_to_pass
def test_values_registry_ingress():
    """Registry must have its own ingress configuration."""
    with open(HELM / "values.yaml") as f:
        vals = yaml.safe_load(f)
    registry = vals.get("registry", {})
    ingress = registry.get("ingress", {})
    assert "enabled" in ingress, "registry.ingress.enabled missing"
    assert "hosts" in ingress, "registry.ingress.hosts missing"
    assert "className" in ingress, "registry.ingress.className missing"


# [pr_diff] fail_to_pass
def test_registry_ingress_template():
    """A separate registry-ingress.yaml template must exist."""
    path = HELM / "templates" / "registry-ingress.yaml"
    assert path.exists(), "registry-ingress.yaml template missing"
    content = path.read_text()
    assert "registry.ingress" in content, \
        "registry-ingress.yaml should reference registry.ingress values"
    assert "Ingress" in content, \
        "registry-ingress.yaml should define a Kubernetes Ingress resource"


# [pr_diff] fail_to_pass
def test_webapp_ingress_template_uses_webapp_values():
    """The webapp ingress template must use .Values.webapp.ingress, not .Values.ingress."""
    # Accept either the old filename or the renamed one
    candidates = [
        HELM / "templates" / "webapp-ingress.yaml",
        HELM / "templates" / "ingress.yaml",
    ]
    path = None
    for c in candidates:
        if c.exists():
            path = c
            break
    assert path is not None, "No webapp ingress template found"
    content = path.read_text()
    assert ".Values.webapp.ingress" in content, \
        "Webapp ingress template must reference .Values.webapp.ingress"
    # Should NOT reference the old top-level .Values.ingress (without webapp prefix)
    # Count occurrences: .Values.ingress that are NOT .Values.webapp.ingress
    import re
    old_refs = re.findall(r'\.Values\.ingress(?!\.)', content)
    # Filter out any that are part of .Values.webapp.ingress
    old_refs = [r for r in re.findall(r'\.Values(?:\.webapp)?\.ingress', content)
                if '.Values.webapp.ingress' not in r]
    assert len(old_refs) == 0, \
        f"Webapp ingress template still references old .Values.ingress ({len(old_refs)} occurrences)"


# [pr_diff] fail_to_pass
def test_helpers_separate_ingress_annotations():
    """_helpers.tpl must define separate webapp and registry ingress annotation helpers."""
    helpers = (HELM / "templates" / "_helpers.tpl").read_text()
    assert "trigger-v4.webapp.ingress.annotations" in helpers, \
        "_helpers.tpl should define trigger-v4.webapp.ingress.annotations"
    assert "trigger-v4.registry.ingress.annotations" in helpers, \
        "_helpers.tpl should define trigger-v4.registry.ingress.annotations"
    # Old combined helper should be removed
    assert "trigger-v4.ingress.annotations" not in helpers.replace(
        "trigger-v4.webapp.ingress.annotations", ""
    ).replace(
        "trigger-v4.registry.ingress.annotations", ""
    ), "Old combined trigger-v4.ingress.annotations helper should be removed"


# [pr_diff] fail_to_pass
def test_webapp_template_uses_webapp_origin():
    """webapp.yaml must use .Values.webapp.appOrigin, not .Values.config.appOrigin."""
    content = (HELM / "templates" / "webapp.yaml").read_text()
    assert ".Values.webapp.appOrigin" in content, \
        "webapp.yaml should use .Values.webapp.appOrigin"
    assert ".Values.config.appOrigin" not in content, \
        "webapp.yaml should not reference .Values.config.appOrigin"


# [pr_diff] fail_to_pass
def test_validate_external_no_port_required():
    """validate-external-config.yaml must not require registry.external.port."""
    content = (HELM / "templates" / "validate-external-config.yaml").read_text()
    assert "registry.external.port" not in content, \
        "Validation should not require registry.external.port"
    assert "registry.external.host" in content, \
        "Validation should still require registry.external.host"


# ---------------------------------------------------------------------------
# Config-edit tests — README documentation must reflect the new structure
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # The section must show webapp.ingress nesting (indented ingress under webapp)
    assert "webapp:" in ingress_section, \
        "Ingress section should show webapp: block"
    assert "registry:" in ingress_section, \
        "Ingress section should show registry: block"
    # Must show ingress nested under both webapp and registry
    # Look for the pattern: "webapp:\n  ingress:" or "registry:\n  ingress:"
    assert re.search(r'webapp:\s*\n\s+ingress:', ingress_section), \
        "Ingress section should show ingress nested under webapp"
    assert re.search(r'registry:\s*\n\s+ingress:', ingress_section), \
        "Ingress section should show ingress nested under registry"


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_values_production_example_valid():
    """Production example values file must parse and have correct structure."""
    with open(HELM / "values-production-example.yaml") as f:
        vals = yaml.safe_load(f)
    assert isinstance(vals, dict), "values-production-example.yaml must be valid YAML"
    # Should have secrets, webapp, etc.
    assert "secrets" in vals, "Production example should have secrets"
    assert "webapp" in vals, "Production example should have webapp"
