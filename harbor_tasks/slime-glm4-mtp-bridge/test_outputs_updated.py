"""
Task: slime-glm4-mtp-bridge
Repo: slime @ 57e76686346beeaaec4010ebefc56b9949686457
PR:   1712

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
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

# First pre-populate sys.modules with mocks for the problematic imports
# Create comprehensive megatron mocks to satisfy all imports

class MockModule(MagicMock):
    """MagicMock that behaves like a module with __path__"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__path__ = []
        self.__file__ = "mock.py"

# Build complete megatron module hierarchy
_megatron = MockModule()
_megatron.core = MockModule()
_megatron.core.models = MockModule()
_megatron.core.models.gpt = MockModule()
_megatron.core.models.gpt.gpt_model = MockModule()
_megatron.core.models.gpt.gpt_layer_specs = MockModule()
_megatron.core.transformer = MockModule()
_megatron.core.transformer.transformer_config = MockModule()
_megatron.core.transformer.dot_product_attention = MockModule()
_megatron.core.transformer.enums = MockModule()

# Pre-populate sys.modules before any import
sys.modules["megatron"] = _megatron
sys.modules["megatron.core"] = _megatron.core
sys.modules["megatron.core.models"] = _megatron.core.models
sys.modules["megatron.core.models.gpt"] = _megatron.core.models.gpt
sys.modules["megatron.core.models.gpt.gpt_model"] = _megatron.core.models.gpt.gpt_model
sys.modules["megatron.core.models.gpt.gpt_layer_specs"] = _megatron.core.models.gpt.gpt_layer_specs
sys.modules["megatron.core.transformer"] = _megatron.core.transformer
sys.modules["megatron.core.transformer.transformer_config"] = _megatron.core.transformer.transformer_config
sys.modules["megatron.core.transformer.dot_product_attention"] = _megatron.core.transformer.dot_product_attention
sys.modules["megatron.core.transformer.enums"] = _megatron.core.transformer.enums
sys.modules["transformer_engine"] = MockModule()
sys.modules["transformer_engine.common"] = MockModule()
sys.modules["transformer_engine.common.recipe"] = MockModule()
sys.modules["transformer_engine.pytorch"] = MockModule()
sys.modules["transformer_engine.pytorch.export"] = MockModule()

# Mock transformers as well
def _setup_transformers_mock():
    """Set up comprehensive transformers mock."""
    import types
    transformers_mod = types.ModuleType("transformers")
    transformers_mod.__path__ = []
    transformers_mod.__spec__ = types.SimpleNamespace(name="transformers", loader=None)
    transformers_mod.__file__ = "transformers/__init__.py"

    # Create submodules
    utils_mod = types.ModuleType("transformers.utils")
    utils_mod.__path__ = []
    utils_mod.__spec__ = types.SimpleNamespace(name="transformers.utils", loader=None)
    hub_mod = types.ModuleType("transformers.utils.hub")
    hub_mod.__spec__ = types.SimpleNamespace(name="transformers.utils.hub", loader=None)
    hub_mod.cached_file = lambda *args, **kwargs: None

    modeling_utils_mod = types.ModuleType("transformers.modeling_utils")
    modeling_utils_mod.__spec__ = types.SimpleNamespace(name="transformers.modeling_utils", loader=None)
    modeling_utils_mod.PreTrainedModel = type("PreTrainedModel", (), {})

    # Wire up hierarchy
    utils_mod.hub = hub_mod
    transformers_mod.utils = utils_mod
    transformers_mod.modeling_utils = modeling_utils_mod
    transformers_mod.AutoConfig = type("AutoConfig", (), {})
    transformers_mod.AutoModel = type("AutoModel", (), {})
    transformers_mod.AutoModelForCausalLM = type("AutoModelForCausalLM", (), {})
    transformers_mod.AutoTokenizer = type("AutoTokenizer", (), {})

    sys.modules["transformers"] = transformers_mod
    sys.modules["transformers.utils"] = utils_mod
    sys.modules["transformers.utils.hub"] = hub_mod
    sys.modules["transformers.modeling_utils"] = modeling_utils_mod

_setup_transformers_mock()


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
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo CI: Python syntax check for glm4moe_lite.py
def test_repo_syntax_glm4moe_lite():
    """Repo CI: glm4moe_lite.py must have valid Python syntax."""
    import py_compile

    py_compile.compile(f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py", doraise=True)


# [repo_tests] pass_to_pass — Repo CI: Python syntax check for model_provider.py
def test_repo_syntax_model_provider():
    """Repo CI: model_provider.py must have valid Python syntax."""
    import py_compile

    py_compile.compile(
        f"{REPO}/slime/backends/megatron_utils/model_provider.py", doraise=True
    )


# [repo_tests] pass_to_pass — Repo CI: ruff linting checks pass
def test_repo_ruff_check():
    """Repo CI: ruff linting passes on repo code (pass_to_pass)."""
    # Install ruff if needed
    r = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120,
    )
    # Run ruff check on slime/ and slime_plugins/
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/slime/", f"{REPO}/slime_plugins/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Repo CI: plugin contract tests pass
def test_repo_plugin_contracts():
    """Repo CI: plugin contract tests pass (pass_to_pass)."""
    # Install pytest and dependencies
    deps = ["pytest", "numpy", "packaging", "pyyaml", "omegaconf", "tqdm",
            "httpx", "pybase64", "pylatexenc", "sympy", "aiohttp"]
    r = subprocess.run(
        ["pip", "install"] + deps + ["--quiet"],
        capture_output=True, text=True, timeout=180,
    )
    # Install slime in editable mode
    r = subprocess.run(
        ["pip", "install", "-e", REPO, "--no-deps", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Run plugin contract tests
    r = subprocess.run(
        ["python", "-m", "pytest", f"{REPO}/tests/plugin_contracts/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin contract tests failed:\n{r.stdout[-1000:]}{r.stderr[-1000:]}"


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
