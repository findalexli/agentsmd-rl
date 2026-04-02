"""
Task: transformers-mistral-query-scaling-positions
Repo: huggingface/transformers @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
PR:   44860

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import math
import textwrap
from pathlib import Path

import torch

REPO = "/workspace/transformers"

AFFECTED_FILES = [
    "src/transformers/models/ministral3/modeling_ministral3.py",
    "src/transformers/models/ministral3/modular_ministral3.py",
    "src/transformers/models/mistral4/modeling_mistral4.py",
    "src/transformers/models/mistral4/modular_mistral4.py",
]

MODELING_FILES = {
    "ministral3": "src/transformers/models/ministral3/modeling_ministral3.py",
    "mistral4": "src/transformers/models/mistral4/modeling_mistral4.py",
}

MODULAR_FILES = {
    "ministral3": "src/transformers/models/ministral3/modular_ministral3.py",
    "mistral4": "src/transformers/models/mistral4/modular_mistral4.py",
}


def _extract_function(filepath: str, func_name: str):
    """Extract a function by name from a Python file via AST, exec it, return the callable.

    # AST-only because: importing modeling files pulls the full transformers import
    # chain which may fail with missing optional deps; the target function only needs torch.
    """
    src = Path(filepath).read_text()
    tree = ast.parse(src)
    lines = src.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_src = textwrap.dedent("\n".join(func_lines))
            ns = {"torch": torch, "math": math}
            exec(compile(func_src, filepath, "exec"), ns)
            return ns[func_name]
    raise ValueError(f"{func_name} not found in {filepath}")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four affected files parse without syntax errors."""
    for f in AFFECTED_FILES:
        src = Path(f"{REPO}/{f}").read_text()
        ast.parse(src)


# [static] pass_to_pass
def test_not_stub():
    """get_llama_4_attn_scale in both modeling files has real computation (not a stub)."""
    for model, f in MODELING_FILES.items():
        src = Path(f"{REPO}/{f}").read_text()
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "get_llama_4_attn_scale":
                found = True
                real_stmts = [
                    s for s in node.body
                    if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))
                ]
                assert len(real_stmts) >= 2, (
                    f"{model}: get_llama_4_attn_scale appears stubbed ({len(real_stmts)} statements)"
                )
                break
        assert found, f"{model}: get_llama_4_attn_scale not found in {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core shape tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ministral3_modeling_scale_shape():
    """get_llama_4_attn_scale in ministral3/modeling returns 4D tensor (B, 1, S, 1) for varied shapes."""
    fn = _extract_function(f"{REPO}/{MODELING_FILES['ministral3']}", "get_llama_4_attn_scale")

    for pos in [
        torch.tensor([[0, 1, 4]]),                        # (1, 3)
        torch.tensor([[0, 1, 4, 8], [0, 4, 8, 16]]),     # (2, 4)
        torch.tensor([[0], [4], [8]]),                     # (3, 1)
    ]:
        B, S = pos.shape
        result = fn(pos, beta=0.1, max_position_embeddings=4)
        assert result.ndim == 4, (
            f"pos shape {pos.shape}: expected 4D, got {result.ndim}D with shape {result.shape}"
        )
        assert result.shape == (B, 1, S, 1), f"Expected ({B}, 1, {S}, 1), got {result.shape}"


# [pr_diff] fail_to_pass
def test_mistral4_modeling_scale_shape():
    """get_llama_4_attn_scale in mistral4/modeling returns 4D tensor (B, 1, S, 1) for varied shapes."""
    fn = _extract_function(f"{REPO}/{MODELING_FILES['mistral4']}", "get_llama_4_attn_scale")

    for pos in [
        torch.tensor([[0, 1, 2]]),                         # (1, 3)
        torch.tensor([[0, 64, 128], [64, 128, 256]]),      # (2, 3)
        torch.tensor([[0], [64]]),                          # (2, 1)
    ]:
        B, S = pos.shape
        result = fn(pos, beta=0.1, max_position_embeddings=64)
        assert result.ndim == 4, (
            f"pos shape {pos.shape}: expected 4D, got {result.ndim}D with shape {result.shape}"
        )
        assert result.shape == (B, 1, S, 1), f"Expected ({B}, 1, {S}, 1), got {result.shape}"


# [pr_diff] fail_to_pass
def test_scaling_formula_values():
    """Scaling formula 1 + beta*log(1+floor(pos/max_pos)) is correct with diverse inputs."""
    fn = _extract_function(f"{REPO}/{MODELING_FILES['ministral3']}", "get_llama_4_attn_scale")

    beta = 0.1
    max_pos = 64
    pos = torch.tensor([[0, 64, 128, 256, 384]])

    result = fn(pos, beta=beta, max_position_embeddings=max_pos)

    assert result.shape == (1, 1, 5, 1), f"Expected (1,1,5,1), got {result.shape}"

    expected = [
        1.0,                          # floor(0/64)=0,   log(1+0)=0
        1.0 + 0.1 * math.log(2),     # floor(64/64)=1,  log(1+1)=ln(2)
        1.0 + 0.1 * math.log(3),     # floor(128/64)=2, log(1+2)=ln(3)
        1.0 + 0.1 * math.log(5),     # floor(256/64)=4, log(1+4)=ln(5)
        1.0 + 0.1 * math.log(7),     # floor(384/64)=6, log(1+6)=ln(7)
    ]
    for i, exp in enumerate(expected):
        got = result[0, 0, i, 0].item()
        assert abs(got - exp) < 1e-4, f"pos={pos[0, i].item()}: expected {exp:.4f}, got {got:.4f}"


# [pr_diff] fail_to_pass
def test_per_batch_scaling_differs():
    """Different position_ids per batch item produce different scaling values (checks 4D shape too)."""
    fn = _extract_function(f"{REPO}/{MODELING_FILES['mistral4']}", "get_llama_4_attn_scale")

    # Batch 0: positions 0-3 < 64 → scale = 1.0
    # Batch 1: positions 100-103 >> 64 → scale > 1.0
    pos = torch.tensor([[0, 1, 2, 3], [100, 101, 102, 103]])
    result = fn(pos, beta=0.1, max_position_embeddings=64)

    assert result.ndim == 4, f"Expected 4D, got {result.ndim}D"
    assert result.shape == (2, 1, 4, 1), f"Expected (2,1,4,1), got {result.shape}"

    batch0 = result[0, 0, :, 0]
    batch1 = result[1, 0, :, 0]

    assert (batch0 - 1.0).abs().max() < 1e-5, f"Batch 0 (pos 0-3) should all be 1.0, got {batch0}"
    assert (batch1 > 1.0).all(), f"Batch 1 (pos 100-103) should all be >1.0, got {batch1}"
    assert not torch.allclose(batch0, batch1), "Batches must produce different scaling values"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — modular file requirement from .ai/AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_ministral3_modular_scale_shape():
    """get_llama_4_attn_scale in ministral3/modular is also fixed (returns 4D tensor, not 3D).

    modular_ministral3.py defines get_llama_4_attn_scale directly and must be updated;
    generated modeling files are derived from modular files via make fix-repo.
    """
    # AST-only because: modular file imports from other models which pulls large dep chain
    fn = _extract_function(f"{REPO}/{MODULAR_FILES['ministral3']}", "get_llama_4_attn_scale")

    for pos in [
        torch.tensor([[0, 1, 2]]),              # (1, 3)
        torch.tensor([[0, 4], [8, 16]]),        # (2, 2)
        torch.tensor([[0, 1, 2, 3, 4]]),        # (1, 5)
    ]:
        B, S = pos.shape
        result = fn(pos, beta=0.1, max_position_embeddings=4)
        assert result.ndim == 4, (
            f"ministral3 modular: expected 4D, got {result.ndim}D ({result.shape}) for pos {pos.shape}"
        )
        assert result.shape == (B, 1, S, 1), (
            f"ministral3 modular: expected ({B},1,{S},1), got {result.shape}"
        )


# [agent_config] fail_to_pass — .ai/AGENTS.md:66 @ e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
def test_modular_forward_no_absolute_positions():
    """Both modular forward() methods pass position_ids directly (not absolute_positions from cache).

    The old pattern computed absolute_positions from cache length, which is wrong for padded/packed
    sequences. The fix passes position_ids directly to get_llama_4_attn_scale.
    """
    for model, path in MODULAR_FILES.items():
        src = Path(f"{REPO}/{path}").read_text()
        assert "absolute_positions" not in src, (
            f"modular_{model}.py still uses old absolute_positions pattern — "
            "edit the modular file to pass position_ids directly to get_llama_4_attn_scale"
        )
