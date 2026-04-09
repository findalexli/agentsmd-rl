"""
Task: beam-modernize-terraform-config-for-selfhosted
Repo: apache/beam @ afbbf5355303b60da4cb19085dc2970a7c9f72b1
PR:   37127

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

import hcl2
import pytest

REPO = "/workspace/beam"
ARC_DIR = Path(REPO) / ".github" / "gh-actions-self-hosted-runners" / "arc"


def _run_python(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / parse checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """HCL files parse without errors using python-hcl2."""
    for tf_file in ARC_DIR.glob("*.tf"):
        with open(tf_file) as f:
            hcl2.load(f)  # raises on syntax error


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core Terraform modernization
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_certmanager_set_list_syntax():
    """cert-manager helm release uses set = [] list syntax, verified by HCL parsing."""
    r = _run_python(r"""
import json, hcl2
from pathlib import Path

with open(Path("/workspace/beam/.github/gh-actions-self-hosted-runners/arc/helm.tf")) as f:
    data = hcl2.load(f)

found = False
for rb in data.get("resource", []):
    if "helm_release" not in rb:
        continue
    for name, cfgs in rb["helm_release"].items():
        if name != "cert-manager":
            continue
        for cfg in (cfgs if isinstance(cfgs, list) else [cfgs]):
            s = cfg.get("set")
            assert s is not None, "cert-manager must have 'set' attribute (not block)"
            assert isinstance(s, list), f"'set' must be a list, got {type(s)}"
            found = True
        break
    break

assert found, "cert-manager helm_release resource not found"
print(json.dumps({"ok": True}))
""")
    assert r.returncode == 0, f"cert-manager set check failed: {r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["ok"]


# [pr_diff] fail_to_pass
def test_arc_no_dynamic_set_block():
    """ARC release uses for expression in set=[...] instead of dynamic blocks."""
    r = _run_python(r"""
import json, hcl2
from pathlib import Path

with open(Path("/workspace/beam/.github/gh-actions-self-hosted-runners/arc/helm.tf")) as f:
    data = hcl2.load(f)

found = False
for rb in data.get("resource", []):
    if "helm_release" not in rb:
        continue
    for name, cfgs in rb["helm_release"].items():
        if name != "arc":
            continue
        for cfg in (cfgs if isinstance(cfgs, list) else [cfgs]):
            s = cfg.get("set")
            assert s is not None, "arc must have 'set' attribute (not dynamic block)"
            assert isinstance(s, list), f"'set' must be a list, got {type(s)}"
            found = True
        break
    break

assert found, "arc helm_release resource not found"
print(json.dumps({"ok": True}))
""")
    assert r.returncode == 0, f"ARC set check failed: {r.stderr}"
    # Also verify no dynamic "set" block in raw content
    content = (ARC_DIR / "helm.tf").read_text()
    assert 'dynamic "set"' not in content, (
        "arc release should not contain 'dynamic \"set\"' blocks"
    )


# [pr_diff] fail_to_pass
def test_google_provider_version_upgraded():
    """Google provider version upgraded to >= 6.x, verified by HCL parsing."""
    r = _run_python(r"""
import json, hcl2
from pathlib import Path

with open(Path("/workspace/beam/.github/gh-actions-self-hosted-runners/arc/provider.tf")) as f:
    data = hcl2.load(f)

def find_google_version(obj):
    if isinstance(obj, dict):
        src = str(obj.get("source", ""))
        if "hashicorp/google" in src:
            ver = obj.get("version", "")
            if ver:
                return ver
        for v in obj.values():
            result = find_google_version(v)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_google_version(item)
            if result:
                return result
    return ""

ver = find_google_version(data)
assert ver, "Google provider version not found in parsed HCL"
digits = ''.join(c for c in ver if c.isdigit() or c == '.')
major = int(digits.split('.')[0])
assert major >= 6, f"Google provider must be >= 6, got {major} from '{ver}'"
print(json.dumps({"ok": True, "version": ver}))
""")
    assert r.returncode == 0, f"Google provider version check failed: {r.stderr}"


# [pr_diff] fail_to_pass
def test_helm_kubernetes_assignment_syntax():
    """Helm provider uses kubernetes = {} assignment syntax, verified by HCL parsing."""
    r = _run_python(r"""
import json, hcl2
from pathlib import Path

with open(Path("/workspace/beam/.github/gh-actions-self-hosted-runners/arc/provider.tf")) as f:
    data = hcl2.load(f)

found = False
for pb in data.get("provider", []):
    if "helm" not in pb:
        continue
    for cfg in (pb["helm"] if isinstance(pb["helm"], list) else [pb["helm"]]):
        k8s = cfg.get("kubernetes")
        assert k8s is not None, "helm provider must have 'kubernetes' configuration"
        found = True
        break
    break

assert found, "helm provider block not found"
print(json.dumps({"ok": True}))
""")
    assert r.returncode == 0, f"Helm kubernetes check failed: {r.stderr}"
    # Also verify raw content uses assignment syntax
    content = (ARC_DIR / "provider.tf").read_text()
    helm_match = re.search(
        r'provider\s+"helm"\s*\{(.*?)\n\}',
        content, re.DOTALL,
    )
    assert helm_match, "helm provider block not found"
    assert re.search(r'kubernetes\s*=\s*\{', helm_match.group(1)), (
        "helm provider should use 'kubernetes = {}' assignment syntax"
    )


# ---------------------------------------------------------------------------
# Documentation updates (pr_diff) — README Updating section
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_readme_has_updating_section():
    """README.md has an Updating section."""
    content = (ARC_DIR / "README.md").read_text()
    assert re.search(r'^#\s+Updating', content, re.MULTILINE), (
        "README.md should have an '# Updating' section"
    )


# [pr_diff] fail_to_pass
def test_updating_section_has_plan_apply():
    """Updating section documents terraform plan and apply steps."""
    content = (ARC_DIR / "README.md").read_text()
    updating_match = re.search(r'#\s+Updating\s*\n(.*?)(?=\n#\s|\Z)', content, re.DOTALL)
    assert updating_match, "README.md must have an '# Updating' section"
    updating_section = updating_match.group(1)
    assert "terraform plan" in updating_section.lower(), (
        "Updating section should document 'terraform plan' step"
    )
    assert "terraform apply" in updating_section.lower(), (
        "Updating section should document 'terraform apply' step"
    )


# [pr_diff] fail_to_pass
def test_updating_section_has_gcloud_init():
    """Updating section documents gcloud auth and terraform init steps."""
    content = (ARC_DIR / "README.md").read_text()
    updating_match = re.search(r'#\s+Updating\s*\n(.*?)(?=\n#\s|\Z)', content, re.DOTALL)
    assert updating_match, "README.md must have an '# Updating' section"
    updating_section = updating_match.group(1)
    assert "gcloud auth" in updating_section.lower(), (
        "Updating section should document gcloud authentication steps"
    )
    assert "terraform init" in updating_section.lower(), (
        "Updating section should document terraform init step"
    )


# ---------------------------------------------------------------------------
# P2P Enrichment - CI/CD Checks (pass_to_pass)
# ---------------------------------------------------------------------------


def _install_terraform():
    """Install Terraform binary if not present."""
    terraform_path = Path("/usr/local/bin/terraform")
    if terraform_path.exists():
        return str(terraform_path)

    # Download and install Terraform
    import urllib.request
    import zipfile

    terraform_url = "https://releases.hashicorp.com/terraform/1.9.0/terraform_1.9.0_linux_amd64.zip"
    zip_path = "/tmp/terraform.zip"

    urllib.request.urlretrieve(terraform_url, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extract("terraform", "/tmp/")

    # Try to install to /usr/local/bin
    try:
        subprocess.run(
            ["cp", "/tmp/terraform", str(terraform_path)],
            capture_output=True, check=True, timeout=10
        )
        subprocess.run(
            ["chmod", "+x", str(terraform_path)],
            capture_output=True, check=True, timeout=10
        )
        return str(terraform_path)
    except subprocess.CalledProcessError:
        # Fallback: use /tmp location
        subprocess.run(["chmod", "+x", "/tmp/terraform"], capture_output=True)
        return "/tmp/terraform"


# [repo_ci] pass_to_pass
def test_terraform_fmt_syntax():
    """Terraform files have no syntax errors (pass_to_pass)."""
    terraform = _install_terraform()
    r = subprocess.run(
        [terraform, "fmt", "-list=false", "-write=false"],
        capture_output=True, text=True, timeout=60, cwd=ARC_DIR,
    )
    # Return code 1 indicates syntax error, others are OK (0, 2, 3)
    assert r.returncode != 1, f"Terraform syntax error: {r.stderr}"


# [repo_ci] pass_to_pass  
def test_terraform_validate():
    """Terraform configuration is valid (pass_to_pass)."""
    terraform = _install_terraform()
    # terraform validate requires init first
    init_r = subprocess.run(
        [terraform, "init", "-backend=false"],
        capture_output=True, text=True, timeout=60, cwd=ARC_DIR,
    )
    if init_r.returncode != 0:
        pytest.skip("terraform init requires cloud credentials")
    r = subprocess.run(
        [terraform, "validate"],
        capture_output=True, text=True, timeout=60, cwd=ARC_DIR,
    )
    assert r.returncode == 0, f"Terraform validation failed:\\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_readme_installing_section():
    """README.md has the required Installing section (pass_to_pass)."""
    content = (ARC_DIR / "README.md").read_text()
    assert re.search(r'^#\s+Installing', content, re.MULTILINE), (
        "README.md should have an '# Installing' section"
    )
