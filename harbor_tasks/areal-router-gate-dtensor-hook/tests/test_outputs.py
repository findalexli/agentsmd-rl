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
"""

import importlib.util
import sys

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"


def _load_router():
    """Load router.py directly, skipping the package __init__.py chain."""
    spec = importlib.util.spec_from_file_location("_router", TARGET)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified file must parse without errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gate_hook_fires():
    """Forward hooks on router.gate must fire during router.forward(x).

    Core bug: forward() called router_gating_linear(x, self.gate.weight, ...)
    directly, bypassing self.gate(). DTensor hooks attach at module.__call__
    level and only fire when the module is invoked, not when the underlying
    function is called directly.
    """
    import torch

    router_mod = _load_router()
    TokenChoiceTopKRouter = router_mod.TokenChoiceTopKRouter

    router = TokenChoiceTopKRouter(dim=32, num_experts=4, top_k=2, score_func="sigmoid")
    hook_called = {"count": 0}

    def hook_fn(module, input, output):
        hook_called["count"] += 1

    router.gate.register_forward_hook(hook_fn)

    x = torch.randn(8, 32)
    router(x)
    assert hook_called["count"] == 1, (
        f"Expected gate forward hook to fire once, fired {hook_called['count']} times. "
        "forward() likely bypasses self.gate() with a direct function call."
    )


# [pr_diff] fail_to_pass
def test_gate_hook_with_varied_inputs():
    """Gate hook fires for different input shapes and score functions."""
    import torch

    router_mod = _load_router()
    TokenChoiceTopKRouter = router_mod.TokenChoiceTopKRouter

    for n_tokens, dim, n_experts, score_func in [
        (1, 16, 4, "softmax"),
        (32, 64, 8, "sigmoid"),
        (4, 32, 4, "softmax"),
    ]:
        router = TokenChoiceTopKRouter(
            dim=dim, num_experts=n_experts, top_k=2, score_func=score_func,
        )
        fired = {"n": 0}

        def _hook(m, i, o, _d=fired):
            _d["n"] += 1

        router.gate.register_forward_hook(_hook)
        x = torch.randn(n_tokens, dim)
        router(x)
        assert fired["n"] == 1, (
            f"Hook not fired for shape ({n_tokens}, {dim}), score_func={score_func}"
        )


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


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) -- regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_state_dict_compat():
    """router.gate state_dict keys must match nn.Linear(bias=False) for checkpoints."""
    import torch.nn as nn

    router_mod = _load_router()
    TokenChoiceTopKRouter = router_mod.TokenChoiceTopKRouter

    router = TokenChoiceTopKRouter(dim=16, num_experts=4, top_k=2)
    ref = nn.Linear(16, 4, bias=False)

    gate_keys = set(router.gate.state_dict().keys())
    ref_keys = set(ref.state_dict().keys())
    assert gate_keys == ref_keys, (
        f"Gate state_dict keys {gate_keys} != nn.Linear keys {ref_keys}"
    )


# [repo_tests] pass_to_pass
def test_router_forward_shapes():
    """TokenChoiceTopKRouter.forward produces correct output shapes and valid values."""
    import torch

    router_mod = _load_router()
    TokenChoiceTopKRouter = router_mod.TokenChoiceTopKRouter

    for dim, n_experts, top_k, n_tokens in [(32, 4, 2, 8), (64, 8, 2, 16), (16, 4, 1, 4)]:
        router = TokenChoiceTopKRouter(
            dim=dim, num_experts=n_experts, top_k=top_k, score_func="sigmoid",
        )
        x = torch.randn(n_tokens, dim)
        top_scores, indices, counts = router(x)

        assert top_scores.shape == (n_tokens, top_k), f"top_scores shape: {top_scores.shape}"
        assert indices.shape == (n_tokens, top_k), f"indices shape: {indices.shape}"
        assert counts.shape == (n_experts,), f"counts shape: {counts.shape}"
        assert not torch.isnan(top_scores).any(), "NaN in top_scores"
        assert (indices >= 0).all() and (indices < n_experts).all(), "Invalid expert indices"


# [static] fail_to_pass
# AST-only because: we need to verify RouterGateLinear.forward has real logic,
# and the class doesn't exist on the base commit — this naturally fails on base.
def test_not_stub():
    """RouterGateLinear.forward must have real logic (not just pass/return)."""
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
