"""
Task: prime-rl-quack-sft-loss-rmsnorm
Repo: PrimeIntellect-ai/prime-rl @ d7afbaa6f39930f801912e1ebb78e0c04ba18ff8
PR:   2102

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import sys
import types
from pathlib import Path

# ---------------------------------------------------------------------------
# Import chain fix: prime_rl.trainer.models.__init__.py imports heavy model
# classes (NemotronH, GLM-MoE, etc.) that pull in GPU-only deps (flash_attn,
# mamba_ssm, triton). Register a lightweight namespace package to bypass it.
# ---------------------------------------------------------------------------
for _pkg in ("prime_rl.trainer.models",):
    if _pkg not in sys.modules:
        _mod = types.ModuleType(_pkg)
        _mod.__path__ = [f"/repo/src/{_pkg.replace('.', '/')}"]
        _mod.__package__ = _pkg
        sys.modules[_pkg] = _mod

import torch
import torch.nn as nn

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    files = [
        "src/prime_rl/configs/sft.py",
        "src/prime_rl/trainer/model.py",
        "src/prime_rl/trainer/models/layers/lm_head.py",
        "src/prime_rl/trainer/models/layers/norms.py",
        "src/prime_rl/trainer/sft/train.py",
    ]
    for f in files:
        p = Path(REPO) / f
        if p.exists():
            source = p.read_text()
            ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_quack_fused_ce_class_and_interface():
    """QuackFusedCrossEntropyOutputLinear exists, is nn.Linear subclass,
    shares FUSED_CE_IGNORE_INDEX constant, labels=None returns logits."""
    from prime_rl.trainer.models.layers.lm_head import (
        FUSED_CE_IGNORE_INDEX,
        QuackFusedCrossEntropyOutputLinear,
    )

    assert issubclass(QuackFusedCrossEntropyOutputLinear, torch.nn.Linear)
    assert QuackFusedCrossEntropyOutputLinear.IGNORE_INDEX == -100
    assert FUSED_CE_IGNORE_INDEX == -100
    assert QuackFusedCrossEntropyOutputLinear.IGNORE_INDEX == FUSED_CE_IGNORE_INDEX

    # labels=None path returns logits on CPU (no quack needed)
    for in_f, out_f in [(16, 32), (64, 128), (8, 16)]:
        layer = QuackFusedCrossEntropyOutputLinear(in_features=in_f, out_features=out_f)
        hidden = torch.randn(2, 4, in_f)
        out = layer(hidden, labels=None)
        assert "logits" in out, "labels=None should return logits"
        assert out["logits"].shape == (2, 4, out_f), f"wrong shape: {out['logits'].shape}"


# [pr_diff] fail_to_pass
def test_quack_fused_ce_labels_path():
    """When labels are provided, forward invokes quack chunked_linear_cross_entropy.
    Since quack is not installed, we expect ImportError referencing quack."""
    from prime_rl.trainer.models.layers.lm_head import QuackFusedCrossEntropyOutputLinear

    layer = QuackFusedCrossEntropyOutputLinear(in_features=16, out_features=32)
    hidden = torch.randn(2, 4, 16)
    labels = torch.randint(0, 32, (2, 4))

    try:
        out = layer(hidden, labels=labels)
        # If it somehow succeeds, verify it returns a loss
        assert "loss" in out, "labels provided should return loss"
    except (ImportError, ModuleNotFoundError) as e:
        assert "quack" in str(e).lower(), f"Import error should reference quack: {e}"


# [pr_diff] fail_to_pass
def test_inject_lm_head_dispatches_quack():
    """inject_prime_lm_head installs QuackFusedCrossEntropyOutputLinear
    for fused_cross_entropy='quack', FusedCrossEntropyOutputLinear for True/'liger'."""
    from prime_rl.trainer.models.layers.lm_head import (
        FusedCrossEntropyOutputLinear,
        QuackFusedCrossEntropyOutputLinear,
        inject_prime_lm_head,
    )

    class FakeConfig:
        final_logit_softcapping = None
        vocab_size = 32

    class FakeBackbone(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed_tokens = nn.Embedding(32, 16)

    class FakeModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.config = FakeConfig()
            self.model = FakeBackbone()
            self.lm_head = nn.Linear(16, 32, bias=False)

    # quack dispatch
    model_q = FakeModel()
    inject_prime_lm_head(model_q, chunk_size=None, fused_cross_entropy="quack")
    assert isinstance(model_q.lm_head, QuackFusedCrossEntropyOutputLinear)

    # liger dispatch (True)
    model_l = FakeModel()
    inject_prime_lm_head(model_l, chunk_size=None, fused_cross_entropy=True)
    assert isinstance(model_l.lm_head, FusedCrossEntropyOutputLinear)

    # liger dispatch ("liger" string variant)
    model_l2 = FakeModel()
    inject_prime_lm_head(model_l2, chunk_size=None, fused_cross_entropy="liger")
    assert isinstance(model_l2.lm_head, FusedCrossEntropyOutputLinear)


# [pr_diff] fail_to_pass
def test_gemma_softcapping_rejects_quack():
    """quack + Gemma softcapping raises ValueError with informative message."""
    import pytest

    from prime_rl.trainer.models.layers.lm_head import inject_prime_lm_head

    class FakeConfig:
        final_logit_softcapping = 30.0  # Gemma-style
        vocab_size = 32

    class FakeBackbone(nn.Module):
        def __init__(self):
            super().__init__()
            self.embed_tokens = nn.Embedding(32, 16)

    class FakeModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.config = FakeConfig()
            self.model = FakeBackbone()
            self.lm_head = nn.Linear(16, 32, bias=False)

    # Different softcapping values should all raise
    for softcap_val in [30.0, 50.0, 1.0]:
        model = FakeModel()
        model.config.final_logit_softcapping = softcap_val
        with pytest.raises(ValueError, match=r"(?i)(softcapping|gemma|quack)"):
            inject_prime_lm_head(model, chunk_size=None, fused_cross_entropy="quack")


# [pr_diff] fail_to_pass
def test_rmsnorm_quack_fallback_cpu():
    """_get_quack_rmsnorm returns None on CPU; RMSNorm forward still works on CPU."""
    from prime_rl.trainer.models.layers.norms import (
        RMSNorm,
        RMSNormConfig,
        _get_quack_rmsnorm,
    )

    assert _get_quack_rmsnorm() is None, "Should return None on CPU"

    # RMSNorm forward with CPU tensors using torch fallback
    for hidden_size in [16, 64, 128]:
        config = RMSNormConfig(hidden_size=hidden_size, eps=1e-5)
        norm = RMSNorm(config)
        x = torch.randn(2, 4, hidden_size)
        out = norm(x)
        assert out.shape == (2, 4, hidden_size)
        assert not torch.isnan(out).any()
        assert out.abs().sum() > 0


# [pr_diff] fail_to_pass
def test_contiguous_grad_identity():
    """_contiguous_grad is identity in forward for both grad and non-grad tensors."""
    from prime_rl.trainer.models.layers.norms import _contiguous_grad

    # With requires_grad=True
    x = torch.randn(3, 4, requires_grad=True)
    y = _contiguous_grad(x)
    assert torch.equal(x, y), "Should be identity in forward"

    # With requires_grad=False -- should return same object (no-op)
    x2 = torch.randn(3, 4, requires_grad=False)
    y2 = _contiguous_grad(x2)
    assert torch.equal(x2, y2)
    assert y2 is x2, "Should return same tensor when requires_grad=False"

    # Verify with different shapes
    x3 = torch.randn(5, 6, 7, requires_grad=True)
    y3 = _contiguous_grad(x3)
    assert torch.equal(x3, y3)


# [pr_diff] fail_to_pass
def test_config_accepts_quack_fused():
    """SFT config loss_impl field accepts 'quack_fused' alongside existing values."""
    # AST-only because: SFTConfig import chain pulls in pydantic-config + many
    # config submodules; parsing the Literal annotation is reliable and direct.
    source = Path(f"{REPO}/src/prime_rl/configs/sft.py").read_text()
    tree = ast.parse(source)

    # Find the Literal annotation for loss_impl
    literal_values = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            # Look for Literal[...] subscripts
            if isinstance(node.value, ast.Name) and node.value.id == "Literal":
                if isinstance(node.slice, ast.Tuple):
                    for elt in node.slice.elts:
                        if isinstance(elt, ast.Constant):
                            literal_values.add(elt.value)

    assert "quack_fused" in literal_values, \
        f"'quack_fused' not in Literal values found: {literal_values}"
    for val in ("liger", "torch", "liger_fused"):
        assert val in literal_values, \
            f"'{val}' should still be in Literal values: {literal_values}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_lm_head_cpu():
    """Existing FusedOutputLinear / VanillaOutputLinear still work on CPU."""
    from prime_rl.trainer.models.layers.lm_head import FusedOutputLinear, VanillaOutputLinear

    h, v = 8, 37
    hidden = torch.randn(2, 4, h, dtype=torch.float32)

    # VanillaOutputLinear returns logits
    lm = VanillaOutputLinear(in_features=h, out_features=v)
    out = lm(hidden, labels=None, temperature=None)
    assert out.get("logits") is not None
    assert out["logits"].shape == (2, 4, v)

    # FusedOutputLinear requires labels (should raise without them)
    import pytest

    lm2 = FusedOutputLinear(in_features=h, out_features=v, chunk_size=3)
    with pytest.raises(AssertionError):
        lm2(hidden, labels=None, temperature=torch.ones(2, 4))


# ---------------------------------------------------------------------------
# Structural (pr_diff) -- packaging check (no behavioral way to test this)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pyproject_quack_extra():
    """pyproject.toml has quack optional extra with quack-kernels>=0.3.3."""
    # AST-only because: TOML packaging metadata, no executable code
    content = Path(f"{REPO}/pyproject.toml").read_text()
    match = re.search(r"quack-kernels\s*[>~=!]+=?\s*([\d.]+)", content)
    assert match, "quack-kernels dependency with version constraint not found in pyproject.toml"
    parts = [int(x) for x in match.group(1).split(".")]
    assert parts >= [0, 3, 3], f"quack-kernels version must be >= 0.3.3, got {match.group(1)}"


# ---------------------------------------------------------------------------
# Structural (pr_diff) -- train.py wiring (AST; can't call train() on CPU)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_train_wiring_quack():
    """train.py references FUSED_CE_IGNORE_INDEX and handles quack_fused in dispatch."""
    # AST-only because: train.py imports torch.distributed, torchtitan, and
    # other GPU-only modules that aren't available in the test environment
    source = Path(f"{REPO}/src/prime_rl/trainer/sft/train.py").read_text()
    tree = ast.parse(source)

    names_used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert "FUSED_CE_IGNORE_INDEX" in names_used, \
        "train.py should reference FUSED_CE_IGNORE_INDEX as a variable"

    quack_constants = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and node.value == "quack_fused"
    ]
    assert len(quack_constants) > 0, \
        "train.py should handle quack_fused as a string constant in dispatch logic"
