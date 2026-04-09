"""
Task: slime-glm4-mtp-bridge
Repo: slime @ 57e76686346beeaaec4010ebefc56b9949686457
PR:   1712

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

REPO = "/workspace/slime"

# ---------------------------------------------------------------------------
# Mock megatron (unavailable in CPU-only container) before importing mbridge.
# mbridge imports megatron at module level throughout; we only need the mock
# to let imports succeed — no megatron code is exercised in our tests.
# ---------------------------------------------------------------------------

class _MockImporter:
    """Meta path finder that intercepts megatron/transformer_engine imports."""

    def find_module(self, fullname, path=None):
        if fullname.startswith(("megatron", "transformer_engine")):
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mock = MagicMock()
        mock.__path__ = []
        mock.__name__ = fullname
        sys.modules[fullname] = mock
        return mock


sys.meta_path.insert(0, _MockImporter())

# Ensure the repo plugin directory is importable
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Lazy-load helpers (deferred so the mock is active before any import)
# ---------------------------------------------------------------------------

def _get_bridge_class():
    from slime_plugins.mbridge.glm4moe_lite import GLM4MoELiteBridge
    return GLM4MoELiteBridge


def _get_bridge_base():
    from mbridge.core.bridge import Bridge
    return Bridge


def _make_bridge_skip_init(hf_config):
    """Create a GLM4MoELiteBridge, patching Bridge.__init__ to skip
    full initialisation (which requires megatron parallel states)."""
    from unittest.mock import patch as mock_patch

    Bridge = _get_bridge_base()
    Cls = _get_bridge_class()
    with mock_patch.object(Bridge, "__init__", lambda self, *a, **kw: None):
        return Cls(hf_config)


def _make_bridge_raw(config_ns):
    """Create a GLM4MoELiteBridge via __new__ (no __init__), then set
    the minimal attributes a method needs."""
    Cls = _get_bridge_class()
    bridge = object.__new__(Cls)
    bridge.config = config_ns
    return bridge


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    import py_compile

    py_compile.compile(f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py", doraise=True)
    py_compile.compile(
        f"{REPO}/slime/backends/megatron_utils/model_provider.py", doraise=True
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rope_theta_patched():
    """GLM4MoELiteBridge.__init__ must extract rope_theta from
    rope_parameters dict when rope_theta is not a direct attribute."""
    for theta_value in [500000, 1000000, 250000]:
        cfg = SimpleNamespace(
            rope_parameters={"rope_theta": theta_value},
            num_hidden_layers=47,
            num_nextn_predict_layers=1,
        )
        assert not hasattr(cfg, "rope_theta"), "precondition: no rope_theta yet"
        _make_bridge_skip_init(cfg)
        assert cfg.rope_theta == theta_value, (
            f"Expected rope_theta={theta_value}, got {cfg.rope_theta}"
        )

    # When rope_parameters is empty/missing, should default to 1_000_000
    cfg_default = SimpleNamespace(
        num_hidden_layers=47,
        num_nextn_predict_layers=1,
    )
    _make_bridge_skip_init(cfg_default)
    assert cfg_default.rope_theta == 1000000, (
        f"Expected default rope_theta=1000000, got {cfg_default.rope_theta}"
    )


# [pr_diff] fail_to_pass
def test_shared_mapping_dynamic_layers():
    """_SHARED_STATE_DICT_MAPPING must use num_hidden_layers (e.g. 47)
    instead of hardcoded 61."""
    for n_layers in [47, 30, 60]:
        cfg = SimpleNamespace(
            rope_theta=1000000,
            num_hidden_layers=n_layers,
            num_nextn_predict_layers=1,
        )
        bridge = _make_bridge_skip_init(cfg)
        mapping = bridge._SHARED_STATE_DICT_MAPPING

        embed_names = mapping["embedding.word_embeddings.weight"]
        assert f"model.layers.{n_layers}.embed_tokens.weight" in embed_names, (
            f"Expected dynamic layer {n_layers} in embed mapping, got {embed_names}"
        )

        output_names = mapping["output_layer.weight"]
        assert f"model.layers.{n_layers}.shared_head.head.weight" in output_names, (
            f"Expected dynamic layer {n_layers} in output mapping, got {output_names}"
        )


# [pr_diff] fail_to_pass
def test_convert_mtp_direct_names():
    """_convert_mtp_param must map direct MTP param names using the
    dynamic layer count, not the hardcoded 61."""
    for n_layers in [47, 30]:
        bridge = _make_bridge_raw(
            SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)
        )
        expected = {
            "mtp.layers.0.enorm.weight": [f"model.layers.{n_layers}.enorm.weight"],
            "mtp.layers.0.hnorm.weight": [f"model.layers.{n_layers}.hnorm.weight"],
            "mtp.layers.0.eh_proj.weight": [f"model.layers.{n_layers}.eh_proj.weight"],
            "mtp.layers.0.final_layernorm.weight": [
                f"model.layers.{n_layers}.shared_head.norm.weight"
            ],
        }
        for mcore_name, hf_names in expected.items():
            result = bridge._convert_mtp_param(mcore_name)
            assert result == hf_names, (
                f"n_layers={n_layers}, name={mcore_name}: "
                f"expected {hf_names}, got {result}"
            )


# [pr_diff] fail_to_pass
def test_convert_mtp_transformer_delegation():
    """_convert_mtp_param must delegate transformer-layer MTP params
    via _weight_name_mapping_attention / _weight_name_mapping_mlp
    using the dynamic layer count."""
    for n_layers in [47, 30]:
        bridge = _make_bridge_raw(
            SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)
        )

        # Attention param — maps through DeepseekV3Bridge._ATTENTION_MAPPING
        attn_result = bridge._convert_mtp_param(
            "mtp.layers.0.transformer_layer.self_attention.linear_proj.weight"
        )
        assert attn_result == [f"model.layers.{n_layers}.self_attn.o_proj.weight"], (
            f"n_layers={n_layers}: expected o_proj mapping, got {attn_result}"
        )

        # MLP param — maps through DeepseekV3Bridge._MLP_MAPPING
        mlp_result = bridge._convert_mtp_param(
            "mtp.layers.0.transformer_layer.mlp.linear_fc2.weight"
        )
        assert mlp_result == [
            f"model.layers.{n_layers}.mlp.down_proj.weight"
        ], f"n_layers={n_layers}: expected down_proj mapping, got {mlp_result}"


# [pr_diff] fail_to_pass
def test_safetensor_io_type():
    """_get_safetensor_io must return standard SafeTensorIO, not the
    FP8-dequant variant used by DeepSeekV3."""
    import torch
    from mbridge.core.safetensor_io import SafeTensorIO

    Cls = _get_bridge_class()
    bridge = object.__new__(Cls)
    bridge.dtype = torch.bfloat16
    bridge._get_actual_hf_path = lambda path: "/tmp"

    io = bridge._get_safetensor_io("/tmp")
    assert type(io) is SafeTensorIO, (
        f"Expected SafeTensorIO, got {type(io).__name__}"
    )


# [pr_diff] fail_to_pass
def test_weight_to_hf_shared():
    """_weight_to_hf_format must return both base and MTP-layer names
    for shared weights (embedding, output) using dynamic layer count."""
    import torch

    for n_layers in [47, 30]:
        cfg = SimpleNamespace(
            rope_theta=1000000,
            num_hidden_layers=n_layers,
            num_nextn_predict_layers=1,
        )
        bridge = _make_bridge_skip_init(cfg)
        bridge.config = SimpleNamespace(mtp_num_layers=1, num_layers=n_layers)
        bridge.make_vocab_size_divisible_by = None

        tensor = torch.ones(10)
        names, tensors = bridge._weight_to_hf_format(
            "embedding.word_embeddings.weight", tensor
        )
        assert "model.embed_tokens.weight" in names, (
            f"Missing base embed name in {names}"
        )
        assert f"model.layers.{n_layers}.embed_tokens.weight" in names, (
            f"Missing MTP embed name for layer {n_layers} in {names}"
        )
        assert len(tensors) == 2, f"Expected 2 tensors, got {len(tensors)}"

        names_out, _ = bridge._weight_to_hf_format("output_layer.weight", tensor)
        assert "lm_head.weight" in names_out, (
            f"Missing lm_head in {names_out}"
        )
        assert f"model.layers.{n_layers}.shared_head.head.weight" in names_out, (
            f"Missing MTP output name for layer {n_layers} in {names_out}"
        )
