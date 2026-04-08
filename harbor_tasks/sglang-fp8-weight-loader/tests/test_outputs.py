"""
Task: sglang-fp8-weight-loader
Repo: sgl-project/sglang @ e6071e60c0975e6c47f056e96d324918c3e5aed5
PR:   #21662

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

TARGET = Path("/workspace/sglang/python/sglang/srt/models/qwen3_next.py")
REPO = "/workspace/sglang"

# Shared preamble: extracts _override_weight_loader from source via AST+exec
# (can't import sglang directly — torch/vllm not installed in test image).
_EXTRACT = """\
import ast, textwrap
from pathlib import Path

source = Path("/workspace/sglang/python/sglang/srt/models/qwen3_next.py").read_text()
tree = ast.parse(source)
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_override_weight_loader":
        func_node = node
        break
assert func_node is not None, "_override_weight_loader not found"
lines = source.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno - 1 : func_node.end_lineno]))
ns = {}
exec(func_src, ns)
override = ns["_override_weight_loader"]
"""


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_override_property_backed_param():
    """_override_weight_loader sets the loader on a property-backed param (ModelWeightParameter)."""
    r = _run_py(_EXTRACT + """\
class PropertyParam:
    def __init__(self):
        self._weight_loader = "original"
    @property
    def weight_loader(self):
        return self._weight_loader

class Mod:
    def __init__(self):
        self.weight = PropertyParam()

for i, loader in enumerate([
    lambda p, w, sid=None: f"l{i}",
    lambda p, w: "second",
    lambda p, w, **kw: "third",
]):
    m = Mod()
    override(m, loader)
    assert m.weight._weight_loader is loader, f"Failed loader {i}"
    assert m.weight.weight_loader is loader, f"Property getter broken {i}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_override_plain_attribute_param():
    """_override_weight_loader sets the loader on a plain attribute param (non-quantized)."""
    r = _run_py(_EXTRACT + """\
class PlainParam:
    def __init__(self):
        self.weight_loader = "original"

class Mod:
    def __init__(self):
        self.weight = PlainParam()

for i, loader in enumerate([
    lambda p, w, sid=None: f"l{i}",
    lambda p, w: "second",
    lambda p, w, **kw: "third",
]):
    m = Mod()
    override(m, loader)
    assert m.weight.weight_loader is loader, f"Failed loader {i}"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_override_plain_then_property():
    """_override_weight_loader handles mixed param types in sequence."""
    r = _run_py(_EXTRACT + """\
class PropertyParam:
    def __init__(self):
        self._weight_loader = "original"
    @property
    def weight_loader(self):
        return self._weight_loader

class PlainParam:
    def __init__(self):
        self.weight_loader = "original"

class ModA:
    def __init__(self):
        self.weight = PlainParam()

class ModB:
    def __init__(self):
        self.weight = PropertyParam()

loader_plain = lambda p, w: "plain"
loader_prop = lambda p, w: "prop"
ma = ModA()
mb = ModB()
override(ma, loader_plain)
override(mb, loader_prop)
assert ma.weight.weight_loader is loader_plain, "plain attr failed"
assert mb.weight.weight_loader is loader_prop, "property param failed"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_override_independent_across_modules():
    """Calling _override_weight_loader on two modules doesn't cross-contaminate."""
    r = _run_py(_EXTRACT + """\
class PropertyParam:
    def __init__(self):
        self._weight_loader = "original"
    @property
    def weight_loader(self):
        return self._weight_loader

class Module:
    def __init__(self):
        self.weight = PropertyParam()

m1, m2, m3 = Module(), Module(), Module()
la = lambda p, w: "a"
lb = lambda p, w: "b"
lc = lambda p, w: "c"
override(m1, la)
override(m2, lb)
override(m3, lc)
assert m1.weight.weight_loader is la, "m1 contaminated"
assert m2.weight.weight_loader is lb, "m2 contaminated"
assert m3.weight.weight_loader is lc, "m3 contaminated"

print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_make_packed_weight_loader_exists():
    """_make_packed_weight_loader must still be defined (regression)."""
    source = TARGET.read_text()
    tree = ast.parse(source)
    found = any(
        isinstance(node, ast.FunctionDef) and node.name == "_make_packed_weight_loader"
        for node in ast.walk(tree)
    )
    assert found, "_make_packed_weight_loader function not found"


# [static] pass_to_pass
def test_not_stub():
    """Target file must not be stubbed out or emptied."""
    size = TARGET.stat().st_size
    assert size > 5000, f"File suspiciously small ({size} bytes)"
