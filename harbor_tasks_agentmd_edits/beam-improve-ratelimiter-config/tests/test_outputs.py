"""
Task: beam-improve-ratelimiter-config
Repo: apache/beam @ bab2374552da7a1f7fbe783408c3b4159e3f0391
PR:   37630

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/beam"
TF_DIR = Path(REPO) / "examples" / "terraform" / "envoy-ratelimiter"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Terraform files have balanced braces (basic structural validation)."""
    for tf_file in ["ratelimit.tf", "variables.tf", "gke.tf"]:
        content = (TF_DIR / tf_file).read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert opens == closes, (
            f"{tf_file}: unbalanced braces — {opens} opening vs {closes} closing"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core Terraform changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_namespace_variable_defined():
    """variables.tf must define a 'namespace' variable with string type."""
    content = (TF_DIR / "variables.tf").read_text()
    # Match a variable block named "namespace"
    assert re.search(r'variable\s+"namespace"\s*\{', content), (
        "variables.tf must define a 'namespace' variable"
    )
    # Check it has string type
    ns_match = re.search(
        r'variable\s+"namespace"\s*\{([^}]*)\}', content, re.DOTALL
    )
    assert ns_match, "Could not parse namespace variable block"
    block = ns_match.group(1)
    assert "string" in block, "namespace variable must be of type string"


# [pr_diff] fail_to_pass
def test_enable_metrics_variable_defined():
    """variables.tf must define an 'enable_metrics' variable with bool type."""
    content = (TF_DIR / "variables.tf").read_text()
    assert re.search(r'variable\s+"enable_metrics"\s*\{', content), (
        "variables.tf must define an 'enable_metrics' variable"
    )
    em_match = re.search(
        r'variable\s+"enable_metrics"\s*\{([^}]*)\}', content, re.DOTALL
    )
    assert em_match, "Could not parse enable_metrics variable block"
    block = em_match.group(1)
    assert "bool" in block, "enable_metrics variable must be of type bool"


# [pr_diff] fail_to_pass
def test_namespace_resource_created():
    """ratelimit.tf must create a kubernetes_namespace resource."""
    content = (TF_DIR / "ratelimit.tf").read_text()
    assert re.search(
        r'resource\s+"kubernetes_namespace"', content
    ), "ratelimit.tf must define a kubernetes_namespace resource"
    # The namespace resource should reference var.namespace
    assert "var.namespace" in content, (
        "kubernetes_namespace resource should use var.namespace"
    )


# [pr_diff] fail_to_pass
def test_resources_use_namespace():
    """Kubernetes resources in ratelimit.tf must set namespace = var.namespace."""
    content = (TF_DIR / "ratelimit.tf").read_text()
    # Count how many metadata blocks set namespace — should be at least 6
    # (configmap, redis deploy, redis svc, ratelimit deploy, ratelimit svc,
    #  ratelimit external svc, HPA)
    namespace_refs = re.findall(r'namespace\s*=\s*var\.namespace', content)
    assert len(namespace_refs) >= 6, (
        f"Expected at least 6 resources with namespace = var.namespace, "
        f"found {len(namespace_refs)}"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — README.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
