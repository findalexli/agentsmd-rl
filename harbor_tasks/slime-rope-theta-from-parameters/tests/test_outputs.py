"""
Task: slime-rope-theta-from-parameters
Repo: THUDM/slime @ 73a1f4d935baf1619bf764eadd199a77cecf55cf
PR:   1734

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
TARGET = Path(f"{REPO}/slime_plugins/mbridge/deepseek_v32.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# Shared helper: AST-extract DeepseekV32Bridge.__init__ and exec with mock parent.
# The full module depends on torch so we can't import it directly; instead we
# extract just the __init__ and run it against a lightweight mock.
_BRIDGE_HELPER = r"""
import ast, textwrap

class _MockParent:
    def __init__(self, hf_config, **kwargs):
        self.hf_config = hf_config

def _extract_bridge():
    src = open("slime_plugins/mbridge/deepseek_v32.py").read()
    tree = ast.parse(src)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    lines = src.splitlines()
                    init_src = "\n".join(lines[item.lineno - 1:item.end_lineno])
                    init_ded = textwrap.dedent(init_src)
                    cls_code = "class DeepseekV32Bridge(_MockParent):\n" + textwrap.indent(init_ded, "    ")
                    ns = {"_MockParent": _MockParent}
                    exec(cls_code, ns)
                    return ns["DeepseekV32Bridge"]
            class _Bare(_MockParent):
                pass
            return _Bare
    raise RuntimeError("DeepseekV32Bridge class not found")
"""


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """Target file parses without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_rope_theta_from_parameters():
    """rope_theta resolved from rope_parameters dict when top-level absent (transformers 5.x)."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

class C:
    rope_parameters = {"rope_theta": 500000}

c = C()
assert not hasattr(c, "rope_theta"), "precondition: rope_theta should not exist"
Bridge(c)
assert hasattr(c, "rope_theta"), "rope_theta not set on config"
assert c.rope_theta == 500000, f"Expected 500000, got {c.rope_theta}"

# Also test a different value
class D:
    rope_parameters = {"rope_theta": 1234567}

d = D()
Bridge(d)
assert d.rope_theta == 1234567, f"Expected 1234567, got {d.rope_theta}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rope_theta_default_when_missing():
    """rope_theta defaults to 1000000 when neither rope_theta nor rope_parameters exists."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

class C:
    pass

c = C()
Bridge(c)
assert hasattr(c, "rope_theta"), "rope_theta not set on config"
assert c.rope_theta == 1000000, f"Expected default 1000000, got {c.rope_theta}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rope_theta_empty_rope_parameters():
    """rope_theta defaults to 1000000 when rope_parameters is an empty dict."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

class C:
    rope_parameters = {}

c = C()
Bridge(c)
assert hasattr(c, "rope_theta"), "rope_theta not set on config"
assert c.rope_theta == 1000000, f"Expected default 1000000, got {c.rope_theta}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_rope_theta_none_rope_parameters():
    """rope_theta defaults to 1000000 when rope_parameters is None."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

class C:
    rope_parameters = None

c = C()
Bridge(c)
assert hasattr(c, "rope_theta"), "rope_theta not set on config"
assert c.rope_theta == 1000000, f"Expected default 1000000, got {c.rope_theta}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + backward compat
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_rope_theta_preserved_when_present():
    """Existing rope_theta not overwritten (transformers 4.x backward compat)."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

for val in [10000, 250000, 1000000]:
    class C:
        rope_theta = val

    c = C()
    Bridge(c)
    assert c.rope_theta == val, f"rope_theta changed from {val} to {c.rope_theta}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] pass_to_pass
def test_super_init_called():
    """super().__init__ is called, preserving parent initialization."""
    r = _run_py(_BRIDGE_HELPER + r"""
Bridge = _extract_bridge()

class C:
    rope_theta = 10000

c = C()
bridge = Bridge(c)
assert bridge.hf_config is c, "super().__init__ not called (hf_config not stored)"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [static] pass_to_pass
def test_class_members_preserved():
    """Original class attributes (_DSA_ATTENTION_MAPPING) and methods not removed."""
    source = TARGET.read_text()
    tree = ast.parse(source)

    cls_node = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef) and node.name == "DeepseekV32Bridge":
            cls_node = node
            break

    assert cls_node is not None, "DeepseekV32Bridge class not found"

    member_names = set()
    for item in cls_node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name):
                    member_names.add(target.id)
        elif isinstance(item, ast.FunctionDef):
            member_names.add(item.name)

    assert "_DSA_ATTENTION_MAPPING" in member_names, "_DSA_ATTENTION_MAPPING removed"
    assert "_weight_to_hf_format" in member_names, "_weight_to_hf_format removed"
    assert "_weight_to_mcore_format" in member_names, "_weight_to_mcore_format removed"
