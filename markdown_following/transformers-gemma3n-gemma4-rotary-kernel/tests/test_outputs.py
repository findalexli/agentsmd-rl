"""Behavioral tests for huggingface/transformers#45564.

The bug: Gemma3nTextAttention and Gemma4TextAttention were decorated with
`@use_kernelized_func(apply_rotary_pos_emb)`. This decorator wraps __init__
to register apply_rotary_pos_emb in `_hidden_kernels`, marking it for
runtime substitution by a kernel that applies rotary to BOTH q and k.

These attention layers, however, apply rotary to q and k separately (and
some sub-paths apply it to q only), so the kernelized substitution is
incompatible with their forward pass. The fix is to remove the decorator
(and the now-unused import) from the four affected files.

We verify this by instantiating the attention layers and checking that
no instance has registered apply_rotary_pos_emb in `_hidden_kernels`.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/transformers")
sys.path.insert(0, str(REPO / "src"))


def _make_gemma3n_attention():
    from transformers.models.gemma3n.configuration_gemma3n import Gemma3nTextConfig
    from transformers.models.gemma3n.modeling_gemma3n import Gemma3nTextAttention

    config = Gemma3nTextConfig(
        num_hidden_layers=2,
        num_kv_shared_layers=0,
        hidden_size=64,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=32,
        intermediate_size=128,
        vocab_size=10,
        vocab_size_per_layer_input=10,
    )
    return Gemma3nTextAttention(config, layer_idx=0)


def _make_gemma4_attention():
    from transformers.models.gemma4.configuration_gemma4 import Gemma4TextConfig
    from transformers.models.gemma4.modeling_gemma4 import Gemma4TextAttention

    config = Gemma4TextConfig()
    return Gemma4TextAttention(config, layer_idx=0)


# ----- f2p: behavioral tests on the decorator's runtime effect -----

def test_gemma3n_attention_does_not_register_rotary_kernel():
    """A live Gemma3nTextAttention instance must not have apply_rotary_pos_emb
    registered in `_hidden_kernels`. The decorator is what populates that dict
    (via a wrapped __init__); removing the decorator removes the registration."""
    attn = _make_gemma3n_attention()
    hidden_kernels = getattr(attn, "_hidden_kernels", {}) or {}
    assert "apply_rotary_pos_emb" not in hidden_kernels, (
        f"Gemma3nTextAttention should not register apply_rotary_pos_emb as a kernelizable "
        f"function. Found _hidden_kernels = {hidden_kernels!r}"
    )


def test_gemma4_attention_does_not_register_rotary_kernel():
    """Same property for Gemma4TextAttention."""
    attn = _make_gemma4_attention()
    hidden_kernels = getattr(attn, "_hidden_kernels", {}) or {}
    assert "apply_rotary_pos_emb" not in hidden_kernels, (
        f"Gemma4TextAttention should not register apply_rotary_pos_emb as a kernelizable "
        f"function. Found _hidden_kernels = {hidden_kernels!r}"
    )


def test_gemma3n_attention_init_not_wrapped_by_kernel_decorator():
    """The decorator replaces __init__ with `new_init` defined inside
    `use_kernelized_func.<locals>.decorator`. Verify the unwrapped class
    method is exposed."""
    from transformers.models.gemma3n.modeling_gemma3n import Gemma3nTextAttention
    qualname = Gemma3nTextAttention.__init__.__qualname__
    assert "use_kernelized_func" not in qualname, (
        f"Gemma3nTextAttention.__init__.__qualname__ = {qualname!r} indicates the class is "
        f"still decorated with use_kernelized_func."
    )


def test_gemma4_attention_init_not_wrapped_by_kernel_decorator():
    """Same property for Gemma4TextAttention."""
    from transformers.models.gemma4.modeling_gemma4 import Gemma4TextAttention
    qualname = Gemma4TextAttention.__init__.__qualname__
    assert "use_kernelized_func" not in qualname, (
        f"Gemma4TextAttention.__init__.__qualname__ = {qualname!r} indicates the class is "
        f"still decorated with use_kernelized_func."
    )


def test_attention_classes_run_forward_without_kernel_marker():
    """End-to-end behavioral test: a Gemma3nTextAttention forward pass must
    succeed on CPU and produce a tensor with the expected shape, with no
    kernel-substitution machinery left dangling on the module."""
    import torch

    attn = _make_gemma3n_attention()
    attn.eval()

    batch, seq_len = 2, 4
    hidden = torch.randn(batch, seq_len, attn.config.hidden_size)
    head_dim = attn.config.head_dim
    cos = torch.ones(batch, seq_len, head_dim)
    sin = torch.zeros(batch, seq_len, head_dim)
    attention_mask = torch.zeros(batch, 1, seq_len, seq_len)
    shared_kv: dict = {}

    with torch.no_grad():
        out, _ = attn(
            hidden_states=hidden,
            position_embeddings=(cos, sin),
            attention_mask=attention_mask,
            past_key_values=None,
            shared_kv_states=shared_kv,
        )

    assert out.shape == (batch, seq_len, attn.config.hidden_size)
    # `_hidden_kernels` should also be empty on a fully-initialized module
    hk = getattr(attn, "_hidden_kernels", {}) or {}
    assert "apply_rotary_pos_emb" not in hk


# ----- p2p: repository CI checks that should keep passing -----

def test_modular_conversion_consistent():
    """The repo's modular-conversion check verifies that every modeling_*.py
    file is consistent with its modular_*.py source. If the agent edits only
    one file in a (modular, modeling) pair, this fails. Always passes at base
    commit; should also pass after a correct fix."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO / "src")
    r = subprocess.run(
        [sys.executable, "utils/check_modular_conversion.py"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"check_modular_conversion.py failed:\nstdout:\n{r.stdout[-1500:]}\n"
        f"stderr:\n{r.stderr[-1500:]}"
    )


def test_ruff_check_on_touched_files():
    """The repo enforces ruff in CI. Touched files must be lint-clean — in
    particular, removing the decorator without removing the now-unused
    `use_kernelized_func` import would trigger F401."""
    files = [
        "src/transformers/models/gemma3n/modeling_gemma3n.py",
        "src/transformers/models/gemma3n/modular_gemma3n.py",
        "src/transformers/models/gemma4/modeling_gemma4.py",
        "src/transformers/models/gemma4/modular_gemma4.py",
    ]
    r = subprocess.run(
        ["ruff", "check", *files],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ruff check failed on touched files:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_tiny_models_create_all_tiny_models_locally():
    """pass_to_pass | CI job 'Check tiny models' → step 'Create all tiny models (locally)'"""
    r = subprocess.run(
        ["bash", "-lc", 'python utils/create_dummy_models.py tiny_local_models --all --num_workers 4'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Create all tiny models (locally)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")