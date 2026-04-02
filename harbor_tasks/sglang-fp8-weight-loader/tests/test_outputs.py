"""
Task: sglang-fp8-weight-loader
Repo: sgl-project/sglang @ e6071e60c0975e6c47f056e96d324918c3e5aed5
PR:   #21662

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import textwrap
from pathlib import Path

TARGET = Path("/workspace/sglang/python/sglang/srt/models/qwen3_next.py")


def _extract_function(name: str):
    """Extract a standalone function from qwen3_next.py by name and return it.
    AST-only because: module imports torch/triton/vllm which are not installed."""
    source = TARGET.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            lines = source.splitlines(keepends=True)
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_src = textwrap.dedent("".join(func_lines))
            ns = {}
            exec(func_src, ns)
            return ns[name]
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse without syntax errors."""
    source = TARGET.read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_override_property_backed_param():
    """_override_weight_loader sets the loader on a property-backed param (ModelWeightParameter)."""
    override = _extract_function("_override_weight_loader")
    assert override is not None, "_override_weight_loader function not found"

    class PropertyParam:
        def __init__(self):
            self._weight_loader = "original"

        @property
        def weight_loader(self):
            return self._weight_loader

    # Test with 3 different loaders to prevent hardcoding
    for i, loader in enumerate([
        lambda p, w, shard_id=None: f"loader_{i}",
        lambda p, w: "second",
        lambda p, w, **kw: "third",
    ]):

        class Mod:
            def __init__(self):
                self.weight = PropertyParam()

        m = Mod()
        override(m, loader)
        assert m.weight._weight_loader is loader, f"Failed on loader {i}"
        assert m.weight.weight_loader is loader, f"Property getter broken on loader {i}"


# [pr_diff] fail_to_pass
def test_override_plain_attribute_param():
    """_override_weight_loader sets the loader on a plain attribute param (non-quantized)."""
    override = _extract_function("_override_weight_loader")
    assert override is not None, "_override_weight_loader function not found"

    # Test with 3 different loaders
    for i, loader in enumerate([
        lambda p, w, shard_id=None: f"loader_{i}",
        lambda p, w: "second",
        lambda p, w, **kw: "third",
    ]):

        class PlainParam:
            def __init__(self):
                self.weight_loader = "original"

        class Mod:
            def __init__(self):
                self.weight = PlainParam()

        m = Mod()
        override(m, loader)
        assert m.weight.weight_loader is loader, f"Failed on loader {i}"


# [pr_diff] fail_to_pass
def test_override_plain_then_property():
    """_override_weight_loader handles mixed param types in sequence."""
    override = _extract_function("_override_weight_loader")
    assert override is not None, "_override_weight_loader function not found"

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

    # Apply to plain first, then property — both must work
    ma = ModA()
    mb = ModB()
    override(ma, loader_plain)
    override(mb, loader_prop)

    assert ma.weight.weight_loader is loader_plain
    assert mb.weight.weight_loader is loader_prop


# [pr_diff] fail_to_pass
def test_override_independent_across_modules():
    """Calling _override_weight_loader on two modules doesn't cross-contaminate."""
    override = _extract_function("_override_weight_loader")
    assert override is not None, "_override_weight_loader function not found"

    class PropertyParam:
        def __init__(self):
            self._weight_loader = "original"

        @property
        def weight_loader(self):
            return self._weight_loader

    class Module:
        def __init__(self):
            self.weight = PropertyParam()

    m1 = Module()
    m2 = Module()
    m3 = Module()
    loader_a = lambda p, w: "a"
    loader_b = lambda p, w: "b"
    loader_c = lambda p, w: "c"

    override(m1, loader_a)
    override(m2, loader_b)
    override(m3, loader_c)

    assert m1.weight.weight_loader is loader_a
    assert m2.weight.weight_loader is loader_b
    assert m3.weight.weight_loader is loader_c


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
