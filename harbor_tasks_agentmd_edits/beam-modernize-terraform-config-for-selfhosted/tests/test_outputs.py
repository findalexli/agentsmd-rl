"""
Task: beam-modernize-terraform-config-for-selfhosted
Repo: apache/beam @ afbbf5355303b60da4cb19085dc2970a7c9f72b1
PR:   37127

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/beam"
ARC_DIR = Path(REPO) / ".github" / "gh-actions-self-hosted-runners" / "arc"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / parse checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """HCL files parse without errors using python-hcl2."""
    import hcl2

    for tf_file in ARC_DIR.glob("*.tf"):
        with open(tf_file) as f:
            hcl2.load(f)  # raises on syntax error


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core Terraform modernization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_certmanager_set_list_syntax():
    """cert-manager helm release uses set = [] list syntax, not set {} blocks."""
    content = (ARC_DIR / "helm.tf").read_text()

    # Find the cert-manager resource block and check it uses set = [
    cm_match = re.search(
        r'resource\s+"helm_release"\s+"cert-manager"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    assert cm_match, "cert-manager helm_release resource not found"
    cm_block = cm_match.group(1)

    # Must use list assignment syntax
    assert "set = [" in cm_block, (
        "cert-manager should use 'set = [...]' list syntax instead of 'set {}' block syntax"
    )


# [pr_diff] fail_to_pass
def test_arc_no_dynamic_set_block():
    """ARC helm release uses for expression instead of dynamic set block."""
    content = (ARC_DIR / "helm.tf").read_text()

    arc_match = re.search(
        r'resource\s+"helm_release"\s+"arc"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    assert arc_match, "arc helm_release resource not found"
    arc_block = arc_match.group(1)

    # Must NOT contain dynamic "set" block
    assert 'dynamic "set"' not in arc_block, (
        "arc release should not use dynamic set blocks; use 'set = [for ...]' instead"
    )
    # Must use set = [ with for expression
    assert "set = [" in arc_block, (
        "arc release should use 'set = [for ...]' list comprehension syntax"
    )


# [pr_diff] fail_to_pass
def test_google_provider_version_upgraded():
    """Google provider version must be >= 6.0 (upgraded from 4.x)."""
    content = (ARC_DIR / "provider.tf").read_text()

    version_match = re.search(
        r'google\s*=?\s*\{[^}]*version\s*=\s*"([^"]+)"',
        content,
        re.DOTALL,
    )
    assert version_match, "Google provider version constraint not found"
    version_str = version_match.group(1)

    # Extract the major version number from constraint like "~> 6.7.0"
    major_match = re.search(r'(\d+)\.', version_str)
    assert major_match, f"Cannot parse version from: {version_str}"
    major = int(major_match.group(1))
    assert major >= 6, (
        f"Google provider major version should be >= 6, got {major} from '{version_str}'"
    )


# [pr_diff] fail_to_pass

    # Find the helm provider block
    helm_match = re.search(
        r'provider\s+"helm"\s*\{(.*?)\n\}',
        content,
        re.DOTALL,
    )
    assert helm_match, "helm provider block not found"
    helm_block = helm_match.group(1)

    # Must use assignment syntax: kubernetes = {
    assert re.search(r'kubernetes\s*=\s*\{', helm_block), (
        "helm provider should use 'kubernetes = {}' assignment syntax, "
        "not 'kubernetes {}' block syntax"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have an Updating heading
    assert re.search(r'^#\s+Updating', content, re.MULTILINE), (
        "README.md should have an '# Updating' section"
    )


# [config_edit] fail_to_pass

    # Extract content after "# Updating" heading
    updating_match = re.search(r'#\s+Updating\s*\n(.*?)(?=\n#\s|\Z)', content, re.DOTALL)
    assert updating_match, "README.md must have an '# Updating' section"
    updating_section = updating_match.group(1)

    assert "terraform plan" in updating_section.lower(), (
        "Updating section should document 'terraform plan' step"
    )
    assert "terraform apply" in updating_section.lower(), (
        "Updating section should document 'terraform apply' step"
    )


# [config_edit] fail_to_pass

    updating_match = re.search(r'#\s+Updating\s*\n(.*?)(?=\n#\s|\Z)', content, re.DOTALL)
    assert updating_match, "README.md must have an '# Updating' section"
    updating_section = updating_match.group(1)

    assert "gcloud auth" in updating_section.lower(), (
        "Updating section should document gcloud authentication steps"
    )
    assert "terraform init" in updating_section.lower(), (
        "Updating section should document terraform init step"
    )
