"""
Task: areal-router-gate-dtensor-hook
Repo: inclusionAI/AReaL @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
PR:   1029

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Import strategy: router.py only imports torch — but importing via the package
chain (areal.experimental.models.archon.moe) triggers archon/__init__.py and
moe/__init__.py, which pull in triton/GPU kernels and qwen2/3 model specs that
are not available in the CPU-only Docker image. We load router.py directly with
importlib.util.spec_from_file_location to bypass all __init__.py files.

CPU compatibility note: torch.histc does not support int64 on CPU, but the
router's forward() calls histc on topk indices (int64). We monkeypatch histc
to cast to float where needed.
"""

import importlib.util
import os
import subprocess
from unittest.mock import patch

import torch

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"
REPO = "/workspace/AReaL"

# CPU-safe histc wrapper: torch.histc doesn't support int64 on CPU
_orig_histc = torch.histc


def _safe_histc(input, bins=100, min=0, max=0):
    return _orig_histc(input.float(), bins=bins, min=float(min), max=float(max))


def _load_router():
    """Load router.py directly, skipping the package __init__.py chain."""
    spec = importlib.util.spec_from_file_location("_router", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_router(router_mod, dim=32, num_experts=4, top_k=2, score_func="sigmoid"):
    """Create a router with CPU-safe defaults (router_dtype=None)."""
    return router_mod.TokenChoiceTopKRouter(
        dim=dim, num_experts=num_experts, top_k=top_k, score_func=score_func,
    )


def _run_python(code, timeout=30):
    """Execute Python code in the repo workspace with PYTHONPATH set."""
    env = {**os.environ, "PYTHONPATH": REPO}
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO, env=env,
    )


# Subprocess boilerplate for loading router.py safely on CPU
_LOAD_ROUTER_BOILERPLATE = """
import importlib.util
import torch
from unittest.mock import patch

TARGET = "{target}"
spec = importlib.util.spec_from_file_location("_router", TARGET)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

_orig_histc = torch.histc
def _safe_histc(input, bins=100, min=0, max=0):
    return _orig_histc(input.float(), bins=bins, min=float(min), max=float(max))
"""


# ---------------------------------------------------------------------------
# Static (pass_to_pass) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gate_hook_fires():
    """Forward hooks on router.gate must fire during router.forward(x).

    Core bug: forward() called router_gating_linear(x, self.gate.weight, ...)
    directly, bypassing self.gate(). DTensor hooks attach at module.__call__
    level and only fire when the module is invoked, not when the underlying
    function is called directly.
    """
    code = _LOAD_ROUTER_BOILERPLATE.format(target=TARGET) + """
router = mod.TokenChoiceTopKRouter(dim=32, num_experts=4, top_k=2, score_func="sigmoid")
hook_count = [0]

def hook_fn(module, input, output):
    hook_count[0] += 1

router.gate.register_forward_hook(hook_fn)

x = torch.randn(8, 32)
with patch.object(torch, "histc", _safe_histc):
    router(x)

assert hook_count[0] == 1, (
    f"Expected gate forward hook to fire once, fired {hook_count[0]} times. "
    "forward() likely bypasses self.gate() with a direct function call."
)
print("PASS")
"""
    r = _run_python(code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_gate_hook_with_varied_inputs():
    """Gate hook fires for different input shapes and score functions."""
    code = _LOAD_ROUTER_BOILERPLATE.format(target=TARGET) + """
configs = [
    (1, 16, 4, "softmax"),
    (32, 64, 8, "sigmoid"),
    (4, 32, 4, "softmax"),
]

for n_tokens, dim, n_experts, score_func in configs:
    router = mod.TokenChoiceTopKRouter(
        dim=dim, num_experts=n_experts, top_k=2, score_func=score_func,
    )
    fired = [0]

    def _hook(m, i, o, _d=fired):
        _d[0] += 1

    router.gate.register_forward_hook(_hook)
    x = torch.randn(n_tokens, dim)
    with patch.object(torch, "histc", _safe_histc):
        router(x)
    assert fired[0] == 1, (
        f"Hook not fired for shape ({n_tokens}, {dim}), score_func={score_func}"
    )

print("PASS")
"""
    r = _run_python(code)
    assert r.returncode == 0, f"Test failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_router_gate_linear_class_exists():
    """RouterGateLinear class (nn.Linear subclass) must exist in router.py.

    On base commit: only nn.Linear is used directly — no subclass.
    On fix: RouterGateLinear(nn.Linear) is added to wrap router_gating_linear.
    """
    router_mod = _load_router()
    assert hasattr(router_mod, "RouterGateLinear"), (
        "RouterGateLinear class not found in router.py — fix not applied"
    )
    import torch.nn as nn

    cls = router_mod.RouterGateLinear
    assert issubclass(cls, nn.Linear), (
        f"RouterGateLinear must inherit from nn.Linear, got bases: {cls.__bases__}"
    )


# [pr_diff] fail_to_pass
def test_gate_is_router_gate_linear():
    """After the fix, router.gate must be an instance of RouterGateLinear, not plain nn.Linear."""
    router_mod = _load_router()
    router = _make_router(router_mod)
    cls = getattr(router_mod, "RouterGateLinear", None)
    assert cls is not None, "RouterGateLinear class not found"
    assert isinstance(router.gate, cls), (
        f"router.gate is {type(router.gate).__name__}, expected RouterGateLinear"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) -- regression + structural
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_state_dict_compat():
    """router.gate state_dict keys must match nn.Linear(bias=False) for checkpoints."""
    import torch.nn as nn

    router_mod = _load_router()
    router = _make_router(router_mod, dim=16, num_experts=4)
    ref = nn.Linear(16, 4, bias=False)

    gate_keys = set(router.gate.state_dict().keys())
    ref_keys = set(ref.state_dict().keys())
    assert gate_keys == ref_keys, (
        f"Gate state_dict keys {gate_keys} != nn.Linear keys {ref_keys}"
    )


# [repo_tests] pass_to_pass
def test_router_forward_shapes():
    """TokenChoiceTopKRouter.forward produces correct output shapes and valid values."""
    router_mod = _load_router()

    for dim, n_experts, top_k, n_tokens in [(32, 4, 2, 8), (64, 8, 2, 16), (16, 4, 1, 4)]:
        router = router_mod.TokenChoiceTopKRouter(
            dim=dim, num_experts=n_experts, top_k=top_k, score_func="sigmoid",
        )
        x = torch.randn(n_tokens, dim)
        with patch.object(torch, "histc", _safe_histc):
            top_scores, indices, counts = router(x)

        assert top_scores.shape == (n_tokens, top_k), f"top_scores shape: {top_scores.shape}"
        assert indices.shape == (n_tokens, top_k), f"indices shape: {indices.shape}"
        assert counts.shape == (n_experts,), f"counts shape: {counts.shape}"
        assert not torch.isnan(top_scores).any(), "NaN in top_scores"
        assert (indices >= 0).all() and (indices < n_experts).all(), "Invalid expert indices"


# [static] fail_to_pass
def test_not_stub():
    """RouterGateLinear.forward must have real logic (not just pass/return).

    AST-only because: we need to verify RouterGateLinear.forward has real logic,
    and the class doesn't exist on the base commit — this naturally fails on base.
    """
    import ast

    src = open(TARGET).read()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [
                (b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else "")
                for b in node.bases
            ]
            if "Linear" in bases:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "forward":
                        body = [s for s in item.body if not isinstance(s, (ast.Pass, ast.Expr))]
                        assert len(body) >= 1, f"{node.name}.forward is a stub"
                        return
    raise AssertionError("No nn.Linear subclass with a forward() method found in router.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:30 @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
def test_no_wildcard_imports():
    """No wildcard imports in modified file (AGENTS.md hard rule)."""
    import re

    src = open(TARGET).read()
    wildcards = re.findall(r"^\s*from\s+\S+\s+import\s+\*", src, re.MULTILINE)
    assert not wildcards, f"Wildcard imports found: {wildcards}"


# [agent_config] pass_to_pass -- AGENTS.md:95 @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
def test_no_gpu_cpu_sync_in_hot_path():
    """No GPU-CPU sync calls (.item(), .tolist(), print(tensor)) in router forward path."""
    import re

    src = open(TARGET).read()
    sync_calls = re.findall(r"\.\s*item\s*\(\s*\)|\.\s*tolist\s*\(\s*\)", src)
    assert not sync_calls, f"GPU-CPU sync calls found in router.py: {sync_calls}"


# [agent_config] pass_to_pass -- AGENTS.md:89-91 @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
def test_no_bare_print():
    """No bare print() calls in router.py — must use areal.utils.logging.getLogger."""
    import ast

    src = open(TARGET).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                assert False, f"Bare print() call at line {node.lineno} — use getLogger instead"


# [agent_config] pass_to_pass -- AGENTS.md:99 @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
def test_explicit_type_hints():
    """RouterGateLinear.__init__ and forward must have explicit type annotations (AGENTS.md rule).

    Checks that every parameter (except self) in __init__ and forward has an annotation,
    and that forward declares a return annotation.
    """
    import ast

    src = open(TARGET).read()
    tree = ast.parse(src)

    linear_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "RouterGateLinear":
            linear_class = node
            break

    if linear_class is None:
        return

    for item in linear_class.body:
        if not isinstance(item, ast.FunctionDef) or item.name not in ("__init__", "forward"):
            continue
        for arg in item.args.args:
            if arg.arg == "self":
                continue
            assert arg.annotation is not None, (
                f"RouterGateLinear.{item.name}: parameter '{arg.arg}' missing type annotation"
            )
        if item.name == "forward":
            assert item.returns is not None, (
                "RouterGateLinear.forward: missing return type annotation"
            )


# [agent_config] pass_to_pass -- AGENTS.md:173 @ 8d84d9f933a83ec2130a8873e8fe74d2cee7a742
def test_no_module_level_process_group():
    """No process groups created at module level in router.py (AGENTS.md distributed rule).

    Applies to areal/experimental/**: process group creation must be inside functions/classes,
    never at module top level.
    """
    import ast

    src = open(TARGET).read()
    tree = ast.parse(src)

    for node in ast.iter_child_nodes(tree):
        for subnode in ast.walk(node):
            if isinstance(subnode, ast.Call):
                func = subnode.func
                if isinstance(func, ast.Attribute) and func.attr in (
                    "init_process_group",
                    "new_group",
                ):
                    assert False, (
                        f"Module-level process group creation at line {subnode.lineno} — "
                        "must be inside a function or class (AGENTS.md:173)"
                    )
