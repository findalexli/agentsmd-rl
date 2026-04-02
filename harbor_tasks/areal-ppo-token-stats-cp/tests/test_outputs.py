"""
Task: areal-ppo-token-stats-cp
Repo: inclusionAI/AReaL @ d1cdac3442585565f902f1e69b9d7399c50b9b34
PR:   990

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
from pathlib import Path

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """actor.py and critic.py must parse without errors."""
    for name in ("areal/trainer/ppo/actor.py", "areal/trainer/ppo/critic.py"):
        src = Path(f"{REPO}/{name}").read_text()
        ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for infer_token_denominator
# ---------------------------------------------------------------------------

def _import_helper():
    import sys
    sys.path.insert(0, REPO)
    from areal.trainer.ppo.stats import infer_token_denominator
    return infer_token_denominator


# [pr_diff] fail_to_pass
def test_attention_mask_preferred():
    """infer_token_denominator prefers attention_mask over other metadata."""
    import torch
    infer = _import_helper()

    # 2-D attention mask — shape should come from this, not the fallback
    input_data = {
        "attention_mask": torch.tensor([[1, 1, 0], [1, 1, 1]]),
        "input_ids": torch.tensor([[11, 12], [13, 14]]),
    }
    result = infer(input_data, fallback=torch.zeros(5))
    assert result.shape == torch.Size([2, 3]), f"Expected [2,3], got {result.shape}"
    assert result.dtype == torch.bool
    assert torch.all(result)

    # 1-D attention mask
    input_data_1d = {"attention_mask": torch.tensor([1, 0, 1, 1])}
    result_1d = infer(input_data_1d, fallback=torch.zeros(2))
    assert result_1d.shape == torch.Size([4])


# [pr_diff] fail_to_pass
def test_cu_seqlens_fallback():
    """cu_seqlens used for packed sequences when attention_mask absent."""
    import torch
    infer = _import_helper()

    # cu_seqlens [0, 4] means 4 tokens total
    input_data = {"cu_seqlens": torch.tensor([0, 4], dtype=torch.int32)}
    result = infer(input_data, fallback=torch.zeros(2))
    assert result.shape == torch.Size([4]), f"Expected [4], got {result.shape}"
    assert result.dtype == torch.bool

    # cu_seqlens [0, 3, 7] means 7 tokens total
    input_data2 = {"cu_seqlens": torch.tensor([0, 3, 7], dtype=torch.int32)}
    result2 = infer(input_data2, fallback=torch.zeros(2))
    assert result2.shape == torch.Size([7])


# [pr_diff] fail_to_pass
def test_input_ids_shape_match():
    """input_ids used when shape matches fallback; ignored otherwise."""
    import torch
    infer = _import_helper()

    # Shapes match → use input_ids shape
    input_data = {"input_ids": torch.tensor([[11, 12, 13], [14, 15, 16]])}
    result = infer(input_data, fallback=torch.zeros(2, 3))
    assert result.shape == torch.Size([2, 3])
    assert result.dtype == torch.bool

    # Shapes don't match → fall back to ones_like(fallback)
    result_mismatch = infer(input_data, fallback=torch.zeros(5))
    assert result_mismatch.shape == torch.Size([5])


# [pr_diff] fail_to_pass
def test_final_fallback():
    """Falls back to ones_like(fallback) when no usable metadata."""
    import torch
    infer = _import_helper()

    # No recognized metadata keys
    fallback = torch.zeros(4, 8)
    result = infer({"logprobs": torch.zeros(3)}, fallback)
    assert result.shape == torch.Size([4, 8])
    assert result.dtype == torch.bool
    assert torch.all(result)

    # Empty dict
    result2 = infer({}, torch.zeros(6))
    assert result2.shape == torch.Size([6])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — actor/critic integration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_actor_critic_use_helper():
    """Actor and critic import and use infer_token_denominator, old pattern removed."""
    actor_src = Path(f"{REPO}/areal/trainer/ppo/actor.py").read_text()
    critic_src = Path(f"{REPO}/areal/trainer/ppo/critic.py").read_text()

    # Old buggy patterns must be gone
    assert "torch.ones_like(loss_mask, dtype=torch.bool)" not in actor_src, \
        "Actor still has old buggy n_tokens pattern"
    assert "torch.ones(value.shape[0], dtype=torch.bool" not in critic_src, \
        "Critic still has old buggy n_tokens pattern"

    # Both files must import the helper
    assert "infer_token_denominator" in actor_src, \
        "Actor does not reference infer_token_denominator"
    assert "infer_token_denominator" in critic_src, \
        "Critic does not reference infer_token_denominator"


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """stats.py has a real infer_token_denominator with conditional fallback logic."""
    stats_path = Path(f"{REPO}/areal/trainer/ppo/stats.py")
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "infer_token_denominator":
            body = [n for n in node.body
                    if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
            assert len(body) >= 3, "Function body too small — likely a stub"
            has_if = any(isinstance(n, ast.If) for n in ast.walk(node))
            assert has_if, "No conditional logic — missing fallback chain"
            return

    raise AssertionError("infer_token_denominator function not found in stats.py")


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

PPO_FILES = [
    Path(f"{REPO}/areal/trainer/ppo/actor.py"),
    Path(f"{REPO}/areal/trainer/ppo/critic.py"),
    Path(f"{REPO}/areal/trainer/ppo/stats.py"),
]


# [agent_config] fail_to_pass — AGENTS.md:25 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_no_wildcard_imports():
    """No wildcard imports in modified/new PPO files (AGENTS.md hard rule)."""
    # Gate: stats.py must exist (ensures fail on base commit)
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assert alias.name != "*", \
                        f"Wildcard import in {fpath.name}: from {node.module} import *"


# [agent_config] fail_to_pass — AGENTS.md:84 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_no_print_in_ppo_files():
    """No bare print() calls in modified PPO files; use areal.utils.logging instead."""
    # AST-only because: checking for print() calls at module level, not executing
    # Gate: stats.py must exist (ensures fail on base commit)
    assert PPO_FILES[2].exists(), "stats.py not created"
    for fpath in PPO_FILES:
        tree = ast.parse(fpath.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    raise AssertionError(
                        f"Bare print() in {fpath.name}:{node.lineno} — use areal.utils.logging"
                    )


# [agent_config] fail_to_pass — AGENTS.md:94 @ d1cdac3442585565f902f1e69b9d7399c50b9b34
def test_type_hints_on_helper():
    """infer_token_denominator must have type annotations on parameters and return."""
    # AST-only because: checking signature annotations, not runtime behavior
    stats_path = Path(f"{REPO}/areal/trainer/ppo/stats.py")
    assert stats_path.exists(), "stats.py not created"
    tree = ast.parse(stats_path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "infer_token_denominator":
            assert node.returns is not None, \
                "infer_token_denominator missing return type annotation"
            for arg in node.args.args:
                if arg.arg == "self":
                    continue
                assert arg.annotation is not None, \
                    f"Parameter '{arg.arg}' missing type annotation"
            return
    raise AssertionError("infer_token_denominator not found in stats.py")
