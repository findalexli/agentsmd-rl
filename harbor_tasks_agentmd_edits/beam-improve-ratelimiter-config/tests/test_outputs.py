"""
Task: beam-improve-ratelimiter-config
Repo: apache/beam @ bab2374552da7a1f7fbe783408c3b4159e3f0391
PR:   37630

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/beam"
TF_DIR = Path(REPO) / "examples" / "terraform" / "envoy-ratelimiter"


def _extract_brace_content(text: str, start: int) -> str:
    """Extract content between matched braces starting after an opening brace."""
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def _parse_variable_blocks(text: str) -> list[dict]:
    """Parse all variable blocks from HCL text -> [{name, body}]."""
    blocks = []
    for m in re.finditer(r'variable\s+"(\w+)"\s*\{', text):
        name = m.group(1)
        body = _extract_brace_content(text, m.end())
        blocks.append({"name": name, "body": body})
    return blocks


def _parse_resource_blocks(text: str) -> list[dict]:
    """Parse all resource blocks from HCL text -> [{type, name, body}]."""
    blocks = []
    for m in re.finditer(r'resource\s+"(\w+)"\s+"(\w+)"\s*\{', text):
        rtype, rname = m.group(1), m.group(2)
        body = _extract_brace_content(text, m.end())
        blocks.append({"type": rtype, "name": rname, "body": body})
    return blocks


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


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
# Fail-to-pass (pr_diff) — behavioral tests with HCL block parsing
# ---------------------------------------------------------------------------


def test_namespace_variable_defined():
    """variables.tf defines a namespace variable with string type and envoy-ratelimiter default."""
    content = (TF_DIR / "variables.tf").read_text()
    blocks = _parse_variable_blocks(content)
    ns = [b for b in blocks if b["name"] == "namespace"]
    assert len(ns) == 1, (
        f"Expected exactly 1 namespace variable block, found {len(ns)}"
    )
    body = ns[0]["body"]
    assert "string" in body, f"namespace must have type=string, got: {body}"
    assert "envoy-ratelimiter" in body, (
        f"namespace default must be envoy-ratelimiter, got: {body}"
    )
    assert "description" in body, "namespace variable must have a description"


def test_enable_metrics_variable_defined():
    """variables.tf defines an enable_metrics variable with bool type and false default."""
    content = (TF_DIR / "variables.tf").read_text()
    blocks = _parse_variable_blocks(content)
    em = [b for b in blocks if b["name"] == "enable_metrics"]
    assert len(em) == 1, (
        f"Expected exactly 1 enable_metrics variable block, found {len(em)}"
    )
    body = em[0]["body"]
    assert "bool" in body, f"enable_metrics must have type=bool, got: {body}"
    default_match = re.search(r"default\s*=\s*(\w+)", body)
    assert default_match is not None, f"enable_metrics must have a default, got: {body}"
    assert default_match.group(1) == "false", (
        f"enable_metrics default must be false, got: {default_match.group(1)}"
    )
    assert "description" in body, "enable_metrics variable must have a description"


def test_kubernetes_namespace_resource():
    """ratelimit.tf creates a kubernetes_namespace resource that uses var.namespace."""
    content = (TF_DIR / "ratelimit.tf").read_text()
    blocks = _parse_resource_blocks(content)
    ns_res = [b for b in blocks if b["type"] == "kubernetes_namespace"]
    assert len(ns_res) == 1, (
        f"Expected exactly 1 kubernetes_namespace resource, found {len(ns_res)}"
    )
    body = ns_res[0]["body"]
    assert "var.namespace" in body, (
        f"kubernetes_namespace must reference var.namespace for its name, got: {body}"
    )


def test_all_k8s_resources_use_namespace():
    """All Kubernetes resources (excluding namespace itself) set namespace = var.namespace."""
    r = subprocess.run(
        [
            "python3",
            "-c",
            r"""
import re
from pathlib import Path


def extract_brace_content(text, start):
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def parse_resource_blocks(text):
    blocks = []
    for m in re.finditer(r'resource\s+"(\w+)"\s+"(\w+)"\s*\{', text):
        rtype, rname = m.group(1), m.group(2)
        body = extract_brace_content(text, m.end())
        blocks.append((rtype, rname, body))
    return blocks


tf_dir = Path("/workspace/beam/examples/terraform/envoy-ratelimiter")
content = (tf_dir / "ratelimit.tf").read_text()
blocks = parse_resource_blocks(content)

k8s = [
    (t, n, b)
    for t, n, b in blocks
    if t.startswith("kubernetes_") and t != "kubernetes_namespace"
]

assert len(k8s) >= 6, f"Expected >= 6 namespaced k8s resources, found {len(k8s)}"

missing = []
for rtype, rname, body in k8s:
    if "var.namespace" not in body:
        missing.append(f"{rtype}.{rname}")

assert len(missing) == 0, f"Resources missing namespace = var.namespace: {missing}"
print("PASS")
""",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_use_statsd_is_conditional():
    """USE_STATSD env var is conditional on enable_metrics, not hardcoded true."""
    content = (TF_DIR / "ratelimit.tf").read_text()
    # Terraform env blocks don't nest, so [^}]* captures the full block
    env_blocks = re.findall(r"env\s*\{([^}]*)\}", content, re.DOTALL)
    statsd_envs = [b for b in env_blocks if '"USE_STATSD"' in b]
    assert len(statsd_envs) == 1, (
        f"Expected 1 USE_STATSD env block, found {len(statsd_envs)}"
    )
    block = statsd_envs[0]
    assert "var.enable_metrics" in block, (
        f"USE_STATSD value must reference var.enable_metrics, got: {block.strip()}"
    )


def test_statsd_sidecar_is_conditional():
    """StatsD exporter sidecar uses dynamic block gated on enable_metrics."""
    content = (TF_DIR / "ratelimit.tf").read_text()
    # Verify dynamic "container" block exists
    assert re.search(r'dynamic\s+"container"\s*\{', content), (
        "ratelimit.tf must use a dynamic container block for conditional sidecar"
    )
    # Verify the for_each is gated on enable_metrics
    assert re.search(r"for_each\s*=\s*var\.enable_metrics", content), (
        "Dynamic block must use for_each gated on var.enable_metrics"
    )
    # Verify statsd-exporter is still referenced in the file
    assert "statsd-exporter" in content, "statsd-exporter name should appear in the file"
