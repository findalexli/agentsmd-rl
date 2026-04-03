"""
Task: transformers-lfm2-conv-cache-alignment
Repo: huggingface/transformers @ f5e573080ae0838799c1f9a0ba28be8431120b56
PR:   #44950

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys

sys.path.insert(0, "/repo/src")

import torch


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All three affected files must parse without syntax errors."""
    import py_compile

    files = [
        "/repo/src/transformers/models/lfm2/modeling_lfm2.py",
        "/repo/src/transformers/models/lfm2/modular_lfm2.py",
        "/repo/src/transformers/models/lfm2_moe/modeling_lfm2_moe.py",
    ]
    for f in files:
        py_compile.compile(f, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def _make_lfm2_config(**overrides):
    from transformers.models.lfm2.configuration_lfm2 import Lfm2Config

    defaults = dict(
        hidden_size=8,
        num_hidden_layers=4,
        num_attention_heads=2,
        num_key_value_heads=2,
        intermediate_size=16,
        conv_L_cache=3,
        layer_types=["conv", "conv", "full_attention", "conv"],
    )
    defaults.update(overrides)
    return Lfm2Config(**defaults)


# [pr_diff] fail_to_pass
def test_last_conv_layer_computation():
    """last_conv_layer attribute correctly identifies the last conv layer index across configs."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    # Config 1: last conv at index 3
    config1 = _make_lfm2_config(layer_types=["conv", "conv", "full_attention", "conv"])
    cache1 = Lfm2HybridConvCache(config1, max_batch_size=1, dtype=torch.float32)
    assert cache1.last_conv_layer == 3

    # Config 2: last conv at index 1 (attention after all convs)
    config2 = _make_lfm2_config(
        num_hidden_layers=3,
        layer_types=["conv", "conv", "full_attention"],
    )
    cache2 = Lfm2HybridConvCache(config2, max_batch_size=1, dtype=torch.float32)
    assert cache2.last_conv_layer == 1

    # Config 3: single conv layer
    config3 = _make_lfm2_config(
        num_hidden_layers=2,
        layer_types=["conv", "full_attention"],
    )
    cache3 = Lfm2HybridConvCache(config3, max_batch_size=1, dtype=torch.float32)
    assert cache3.last_conv_layer == 0


# [pr_diff] fail_to_pass
def test_update_conv_state_init():
    """update_conv_state(cache_init=True) stores the full state tensor in the cache."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    config = _make_lfm2_config()
    cache = Lfm2HybridConvCache(config, max_batch_size=2, dtype=torch.float32)

    for layer_idx in [0, 1, 3]:
        new_state = torch.randn(2, 8, 3)
        result = cache.update_conv_state(layer_idx, new_state, cache_init=True)
        assert torch.allclose(result, new_state), (
            f"cache_init=True on layer {layer_idx} should store exact state"
        )
        assert torch.allclose(cache.conv_cache[layer_idx], new_state)


# [pr_diff] fail_to_pass
def test_update_conv_state_decode():
    """update_conv_state(cache_init=False) rolls left and updates the last position."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    config = _make_lfm2_config()
    cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

    # Initialize cache with known values
    init_state = torch.tensor([[[1.0, 2.0, 3.0]]]).expand(1, 8, 3).clone()
    cache.update_conv_state(0, init_state, cache_init=True)

    # Decode update: should roll left [1,2,3] -> [2,3,1] then set last to 9 -> [2,3,9]
    decode_input = torch.tensor([[[0.0, 0.0, 9.0]]]).expand(1, 8, 3).clone()
    result = cache.update_conv_state(0, decode_input, cache_init=False)

    assert result[0, 0, -1].item() == 9.0, f"Expected last=9.0, got {result[0, 0, -1].item()}"
    assert result[0, 0, 0].item() == 2.0, f"Expected first=2.0, got {result[0, 0, 0].item()}"

    # Second decode step: [2,3,9] -> roll -> [3,9,2] -> set last to 5 -> [3,9,5]
    decode_input2 = torch.tensor([[[0.0, 0.0, 5.0]]]).expand(1, 8, 3).clone()
    result2 = cache.update_conv_state(0, decode_input2, cache_init=False)
    assert result2[0, 0, 0].item() == 3.0
    assert result2[0, 0, 1].item() == 9.0
    assert result2[0, 0, 2].item() == 5.0


# [pr_diff] fail_to_pass
def test_has_previous_state_lifecycle():
    """has_previous_state starts False, becomes True after last conv layer, clears on reset."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    config = _make_lfm2_config()
    cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

    # Initially False
    assert cache.has_previous_state is False

    # Updating non-last conv layers does not flip the flag
    state = torch.randn(1, 8, 3)
    cache.update_conv_state(0, state, cache_init=True)
    assert cache.has_previous_state is False
    cache.update_conv_state(1, state, cache_init=True)
    assert cache.has_previous_state is False

    # Updating the last conv layer (index 3) flips it to True
    cache.update_conv_state(3, state, cache_init=True)
    assert cache.has_previous_state is True

    # reset() clears the flag
    cache.reset()
    assert cache.has_previous_state is False


# [pr_diff] fail_to_pass
def test_has_previous_state_varied_layouts():
    """has_previous_state flips only after the actual last conv layer for different layer orderings."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    # Layout where last conv is at index 1 (attention is last)
    config = _make_lfm2_config(
        num_hidden_layers=3,
        layer_types=["conv", "conv", "full_attention"],
    )
    cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)
    state = torch.randn(1, 8, 3)

    cache.update_conv_state(0, state, cache_init=True)
    assert cache.has_previous_state is False, "Should not flip after layer 0 (not last conv)"

    cache.update_conv_state(1, state, cache_init=True)
    assert cache.has_previous_state is True, "Should flip after layer 1 (last conv)"


# [pr_diff] fail_to_pass
def test_slow_forward_prefill_decode():
    """slow_forward produces valid output for both prefill and decode paths."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache, Lfm2ShortConv

    config = _make_lfm2_config(hidden_size=16, intermediate_size=32)
    cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

    conv_mod = Lfm2ShortConv(config, layer_idx=0)
    conv_mod.eval()

    # Prefill: sequence of length 5
    x_prefill = torch.randn(1, 5, 16)
    out_prefill = conv_mod.slow_forward(x_prefill, cache, attention_mask=None)
    assert out_prefill.shape == (1, 5, 16), f"Prefill shape: {out_prefill.shape}"

    # Set has_previous_state by updating all conv layers
    for li in [0, 1, 3]:
        cache.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)

    # Decode: single token
    x_decode = torch.randn(1, 1, 16)
    out_decode = conv_mod.slow_forward(x_decode, cache, attention_mask=None)
    assert out_decode.shape == (1, 1, 16), f"Decode shape: {out_decode.shape}"
    assert not torch.isnan(out_decode).any(), "Decode output contains NaN"


# [pr_diff] fail_to_pass
def test_slow_forward_decode_uses_cache():
    """Decode path reads from conv cache — different cache states produce different outputs."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache, Lfm2ShortConv

    torch.manual_seed(42)
    config = _make_lfm2_config(hidden_size=16, intermediate_size=32)
    conv_mod = Lfm2ShortConv(config, layer_idx=0)
    conv_mod.eval()

    x_decode = torch.randn(1, 1, 16)
    x_prefill = torch.randn(1, 5, 16)

    # Run 1: prefill then set cache state A, then decode
    cache1 = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)
    conv_mod.slow_forward(x_prefill, cache1, attention_mask=None)
    for li in [0, 1, 3]:
        cache1.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)
    cache1.conv_cache[0] = torch.ones(1, 16, 3) * 2.0
    out1 = conv_mod.slow_forward(x_decode, cache1, attention_mask=None)

    # Run 2: prefill then set very different cache state B, then decode
    cache2 = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)
    conv_mod.slow_forward(x_prefill, cache2, attention_mask=None)
    for li in [0, 1, 3]:
        cache2.update_conv_state(li, torch.randn(1, 16, 3), cache_init=True)
    cache2.conv_cache[0] = torch.ones(1, 16, 3) * -50.0
    out2 = conv_mod.slow_forward(x_decode, cache2, attention_mask=None)

    assert not torch.allclose(out1, out2, atol=1e-3), (
        "Decode output must depend on cached conv state"
    )


# [pr_diff] fail_to_pass
def test_moe_cache_alignment():
    """lfm2_moe cache also has update_conv_state and has_previous_state with same behavior."""
    from transformers.models.lfm2_moe.modeling_lfm2_moe import Lfm2MoeHybridConvCache
    from transformers.models.lfm2_moe.configuration_lfm2_moe import Lfm2MoeConfig

    config = Lfm2MoeConfig(
        hidden_size=8,
        num_hidden_layers=4,
        num_attention_heads=2,
        num_key_value_heads=2,
        intermediate_size=16,
        conv_L_cache=3,
        layer_types=["conv", "conv", "full_attention", "conv"],
        num_experts=2,
        num_experts_per_tok=1,
    )
    cache = Lfm2MoeHybridConvCache(config, max_batch_size=1, dtype=torch.float32)

    assert cache.has_previous_state is False

    state = torch.randn(1, 8, 3)
    result = cache.update_conv_state(3, state, cache_init=True)
    assert cache.has_previous_state is True
    assert torch.allclose(result, state)

    cache.reset()
    assert cache.has_previous_state is False


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cache_api_preserved():
    """Existing cache API (init, get_seq_length, update, len) still works."""
    from transformers.models.lfm2.modeling_lfm2 import Lfm2HybridConvCache

    config = _make_lfm2_config()
    cache = Lfm2HybridConvCache(config, max_batch_size=2, dtype=torch.float32)

    assert len(cache) == 4
    assert cache.get_seq_length() == 0
    assert len(cache.conv_cache) == 4
    assert cache.conv_cache[0].shape == (2, 8, 3)

    # KV cache update still works
    k = torch.randn(2, 2, 5, 4)
    v = torch.randn(2, 2, 5, 4)
    cache.update(k, v, layer_idx=2)
    assert cache.get_seq_length(2) == 5


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from repo config files
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:15 @ f5e573080ae
def test_modular_file_consistency():
    """modular_lfm2.py must also have update_conv_state and has_previous_state."""
    from transformers.models.lfm2.modular_lfm2 import Lfm2HybridConvCache

    config = _make_lfm2_config()
    cache = Lfm2HybridConvCache(config, max_batch_size=1, dtype=torch.float32)

    assert cache.has_previous_state is False
    state = torch.randn(1, 8, 3)
    cache.update_conv_state(3, state, cache_init=True)
    assert cache.has_previous_state is True


# [agent_config] pass_to_pass — CLAUDE.md:2 @ f5e573080ae
def test_ruff_lint():
    """Changed files pass ruff linting."""
    result = subprocess.run(
        [
            "ruff", "check",
            "src/transformers/models/lfm2/modeling_lfm2.py",
            "src/transformers/models/lfm2/modular_lfm2.py",
            "src/transformers/models/lfm2_moe/modeling_lfm2_moe.py",
        ],
        cwd="/repo",
        capture_output=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"ruff lint failed:\n{result.stdout.decode()}\n{result.stderr.decode()}"
    )
