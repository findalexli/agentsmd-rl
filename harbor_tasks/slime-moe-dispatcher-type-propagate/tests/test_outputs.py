"""
Task: slime-moe-dispatcher-type-propagate
Repo: THUDM/slime @ 7f2a03b5d390f93a90776b8d99ace6b82fa61738
PR:   1737

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

REPO = "/workspace/slime"
TARGET = f"{REPO}/slime/backends/megatron_utils/model_provider.py"


class _FakeLinear:
    """Minimal stand-in for torch.nn.Linear (allows subclassing)."""

    def __init__(self, *args, **kwargs):
        pass


def _make_args(**overrides):
    """Create a mock args namespace with bridge-mode defaults."""
    defaults = dict(
        megatron_to_hf_mode="bridge",
        custom_model_provider_path=None,
        hf_checkpoint="/fake/checkpoint",
        tensor_model_parallel_size=1,
        pipeline_model_parallel_size=1,
        expert_model_parallel_size=1,
        expert_tensor_parallel_size=1,
        sequence_parallel=False,
        context_parallel_size=1,
        variable_seq_lengths=True,
    )
    defaults.update(overrides)
    return type("Args", (), defaults)()


def _call_bridge_mode(args):
    """Load model_provider with mocked deps and call get_model_provider_func.

    Returns (mock_provider, result) so tests can inspect what was set on the provider.
    """
    mock_provider = MagicMock()
    mock_bridge = MagicMock()
    mock_bridge.to_megatron_provider.return_value = mock_provider

    mock_auto_bridge = MagicMock()
    mock_auto_bridge.from_hf_pretrained.return_value = mock_bridge

    torch_mock = MagicMock()
    torch_mock.nn.Linear = _FakeLinear

    megatron_bridge_mock = MagicMock()
    megatron_bridge_mock.AutoBridge = mock_auto_bridge

    auto_mock_names = [
        "megatron", "megatron.core", "megatron.core.tensor_parallel",
        "megatron.core.models", "megatron.core.models.gpt",
        "megatron.core.models.gpt.gpt_layer_specs",
        "megatron.core.transformer", "megatron.core.transformer.spec_utils",
        "megatron.core.transformer.transformer_config",
        "megatron.training", "megatron.training.arguments",
        "slime_plugins", "slime_plugins.megatron_bridge",
        "slime", "slime.utils", "slime.utils.misc",
        "slime.backends", "slime.backends.megatron_utils",
    ]

    saved = {}
    for name in auto_mock_names:
        saved[name] = sys.modules.get(name)
        sys.modules[name] = MagicMock()

    explicit = {
        "torch": torch_mock,
        "torch.nn": torch_mock.nn,
        "megatron.bridge": megatron_bridge_mock,
    }
    for name, mock in explicit.items():
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mock

    mod_key = "slime.backends.megatron_utils.model_provider"
    saved[mod_key] = sys.modules.get(mod_key)

    try:
        sys.modules.pop(mod_key, None)
        spec = importlib.util.spec_from_file_location(mod_key, TARGET)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        result = module.get_model_provider_func(args)
        return mock_provider, result
    finally:
        for name, orig in saved.items():
            if orig is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = orig


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """model_provider.py must parse without syntax errors."""
    import ast

    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_moe_dispatcher_propagated():
    """Bridge provider receives moe_token_dispatcher_type from args."""
    args = _make_args(moe_token_dispatcher_type="alltoall")
    provider, _ = _call_bridge_mode(args)
    assert provider.moe_token_dispatcher_type == "alltoall", (
        f"Expected 'alltoall', got {provider.moe_token_dispatcher_type!r}"
    )


# [pr_diff] fail_to_pass
def test_moe_dispatcher_various_values():
    """Propagation works for different dispatcher type values."""
    for value in ["alltoall", "allgather", "custom_dispatch"]:
        args = _make_args(moe_token_dispatcher_type=value)
        provider, _ = _call_bridge_mode(args)
        assert provider.moe_token_dispatcher_type == value, (
            f"Expected {value!r}, got {provider.moe_token_dispatcher_type!r}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_moe_dispatcher_absent_no_error():
    """No error when args lacks moe_token_dispatcher_type."""
    args = _make_args()
    assert not hasattr(args, "moe_token_dispatcher_type")
    provider, result = _call_bridge_mode(args)
    assert result is not None, "get_model_provider_func should return a callable"


# [pr_diff] pass_to_pass
def test_existing_attrs_preserved():
    """Existing provider attribute assignments are not broken."""
    args = _make_args(
        tensor_model_parallel_size=4,
        pipeline_model_parallel_size=2,
        sequence_parallel=True,
        variable_seq_lengths=True,
    )
    provider, _ = _call_bridge_mode(args)
    assert provider.tensor_model_parallel_size == 4
    assert provider.pipeline_model_parallel_size == 2
    assert provider.sequence_parallel is True
    assert provider.variable_seq_lengths is True
