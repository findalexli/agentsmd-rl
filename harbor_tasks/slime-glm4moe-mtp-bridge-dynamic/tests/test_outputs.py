"""
Task: slime-glm4moe-mtp-bridge-dynamic
Repo: THUDM/slime @ 57e76686346beeaaec4010ebefc56b9949686457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import sys
import types
from pathlib import Path

REPO = "/workspace/slime"
BRIDGE_PATH = f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py"
PROVIDER_PATH = f"{REPO}/slime/backends/megatron_utils/model_provider.py"


# ---------------------------------------------------------------------------
# Mock infrastructure — mbridge/torch are heavy; we mock them and exec the
# actual bridge file so tests exercise the real code, not imports.
# ---------------------------------------------------------------------------

def _setup_mocks():
    """Install mocks for torch, mbridge, etc. into sys.modules. Idempotent."""
    if "mbridge" in sys.modules and hasattr(sys.modules["mbridge"], "_test_mocked"):
        return
    _torch = types.ModuleType("torch")

    class _FakeTensor:
        pass

    _torch.Tensor = _FakeTensor
    sys.modules["torch"] = _torch

    for mod_name in ["mbridge", "mbridge.core", "mbridge.models",
                     "mbridge.core.safetensor_io"]:
        sys.modules[mod_name] = types.ModuleType(mod_name)

    sys.modules["mbridge"]._test_mocked = True

    def _register_model(name):
        def decorator(cls):
            cls._registered_name = name
            return cls
        return decorator

    sys.modules["mbridge.core"].register_model = _register_model

    class MockSafeTensorIO:
        """Standard bf16 loader mock."""
        def __init__(self, path):
            self.path = path

    sys.modules["mbridge.core.safetensor_io"].SafeTensorIO = MockSafeTensorIO

    class MockBridgeBase:
        """Grandparent (mbridge Bridge base) — simple passthrough for weight mapping."""
        def _weight_to_hf_format(self, name, weights):
            return [name], [weights]

    class MockDeepseekV3Bridge(MockBridgeBase):
        """Parent with hardcoded layer 61 — the exact bug the task fixes."""
        _SHARED_STATE_DICT_MAPPING = {
            "embedding.word_embeddings.weight": [
                "model.embed_tokens.weight",
                "model.layers.61.embed_tokens.weight",
            ],
            "output_layer.weight": [
                "lm_head.weight",
                "model.layers.61.shared_head.head.weight",
            ],
        }

        def __init__(self, hf_config, **kwargs):
            self.hf_config = hf_config
            self.config = types.SimpleNamespace(
                num_layers=hf_config.num_hidden_layers,
                mtp_num_layers=getattr(hf_config, "num_nextn_predict_layers", 0),
                hidden_size=4096,
            )

        def _convert_mtp_param(self, name):
            _direct = {
                "mtp.layers.0.enorm.weight": "model.layers.61.enorm.weight",
                "mtp.layers.0.hnorm.weight": "model.layers.61.hnorm.weight",
                "mtp.layers.0.eh_proj.weight": "model.layers.61.eh_proj.weight",
                "mtp.layers.0.final_layernorm.weight": "model.layers.61.shared_head.norm.weight",
            }
            if name in _direct:
                return [_direct[name]]
            return [name.replace("mtp.layers.0.transformer_layer", "decoder.layers.61")]

        def _get_safetensor_io(self, path):
            return "FP8_DEQUANT_LOADER"

        def _get_actual_hf_path(self, path):
            return path

        def _weight_name_mapping_attention(self, name):
            return [name]

        def _weight_name_mapping_mlp(self, name):
            return [name]

        def _weight_to_hf_format(self, name, weights):
            if name in self._SHARED_STATE_DICT_MAPPING:
                hf_names = self._SHARED_STATE_DICT_MAPPING[name]
                return hf_names, [weights] * len(hf_names)
            return [name], [weights]

    sys.modules["mbridge.models"].DeepseekV3Bridge = MockDeepseekV3Bridge


def _load_bridge_class():
    """Load GLM4MoELiteBridge from the actual source file with mocked deps."""
    _setup_mocks()
    ns = {}
    source = Path(BRIDGE_PATH).read_text()
    exec(compile(source, BRIDGE_PATH, "exec"), ns)
    cls = ns.get("GLM4MoELiteBridge")
    assert cls is not None, "GLM4MoELiteBridge class not found in source"
    return cls


def _make_config(num_hidden_layers=47, num_nextn_predict_layers=1,
                 rope_parameters=None, rope_theta=None):
    """Build a test HF config. By default mimics GLM-4.7-Flash."""
    cfg = types.SimpleNamespace(
        num_hidden_layers=num_hidden_layers,
        num_nextn_predict_layers=num_nextn_predict_layers,
    )
    if rope_parameters is not None:
        cfg.rope_parameters = rope_parameters
    if rope_theta is not None:
        cfg.rope_theta = rope_theta
    return cfg


def _make_bridge(num_hidden_layers=47, rope_theta_val=500000):
    """Instantiate GLM4MoELiteBridge with a test config."""
    cls = _load_bridge_class()
    cfg = _make_config(
        num_hidden_layers=num_hidden_layers,
        rope_parameters={"rope_theta": rope_theta_val},
    )
    return cls(cfg)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [BRIDGE_PATH, PROVIDER_PATH]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rope_theta_from_rope_parameters():
    """Bridge __init__ must extract rope_theta from rope_parameters dict."""
    for theta_val in [500000, 1000000, 10000]:
        bridge = _make_bridge(rope_theta_val=theta_val)
        cfg = bridge.hf_config
        assert hasattr(cfg, "rope_theta"), "rope_theta was not patched onto config"
        assert cfg.rope_theta == theta_val, (
            f"Expected rope_theta={theta_val}, got {cfg.rope_theta}"
        )


# [pr_diff] fail_to_pass
def test_rope_theta_default_when_missing():
    """Bridge must handle missing rope_parameters gracefully."""
    cls = _load_bridge_class()
    # Config with neither rope_theta nor rope_parameters
    cfg = _make_config(rope_parameters=None)
    bridge = cls(cfg)
    assert hasattr(bridge.hf_config, "rope_theta"), "rope_theta not set when rope_parameters missing"


# [pr_diff] fail_to_pass
def test_shared_mapping_dynamic_layer():
    """_SHARED_STATE_DICT_MAPPING must use num_hidden_layers, not hardcoded 61."""
    for n_layers in [47, 32, 60]:
        bridge = _make_bridge(num_hidden_layers=n_layers)
        mapping = bridge._SHARED_STATE_DICT_MAPPING

        assert "embedding.word_embeddings.weight" in mapping
        assert "output_layer.weight" in mapping

        for key, values in mapping.items():
            for v in values:
                assert ".61." not in v, f"Hardcoded layer 61 in mapping: {v}"
            layer_refs = [v for v in values if f".{n_layers}." in v]
            assert len(layer_refs) >= 1, (
                f"No layer-{n_layers} reference for {key}: {values}"
            )


# [pr_diff] fail_to_pass
def test_convert_mtp_param_dynamic():
    """_convert_mtp_param must produce layer names matching num_hidden_layers."""
    for n_layers in [47, 32]:
        bridge = _make_bridge(num_hidden_layers=n_layers)

        direct_names = [
            "mtp.layers.0.enorm.weight",
            "mtp.layers.0.hnorm.weight",
            "mtp.layers.0.eh_proj.weight",
            "mtp.layers.0.final_layernorm.weight",
        ]
        for name in direct_names:
            result = bridge._convert_mtp_param(name)
            assert isinstance(result, list) and len(result) >= 1
            joined = " ".join(result)
            assert f".{n_layers}." in joined, (
                f"Expected layer {n_layers} for {name}, got: {result}"
            )
            assert ".61." not in joined, f"Hardcoded 61 for {name}: {result}"

        # Transformer-layer proxy (self_attention path)
        proxy = bridge._convert_mtp_param(
            "mtp.layers.0.transformer_layer.self_attention.proj.weight"
        )
        proxy_joined = " ".join(proxy)
        assert ".61." not in proxy_joined, f"Hardcoded 61 in proxy: {proxy}"


# [pr_diff] fail_to_pass
def test_safetensor_io_standard_loader():
    """Bridge must use SafeTensorIO (bf16), not parent's FP8 dequant loader."""
    for path in ["/fake/weights/path", "/other/model/dir"]:
        bridge = _make_bridge()
        result = bridge._get_safetensor_io(path)
        assert result != "FP8_DEQUANT_LOADER", "Still using parent FP8 dequant loader"
        assert hasattr(result, "path"), (
            f"Expected SafeTensorIO-like object with .path, got {type(result)}"
        )


# [pr_diff] fail_to_pass
def test_weight_to_hf_format_shared():
    """_weight_to_hf_format returns dynamic layer mappings for shared weights."""
    for n_layers in [47, 32, 60]:
        bridge = _make_bridge(num_hidden_layers=n_layers)
        fake_weight = "TENSOR"

        # Embedding weight → should map to both base and MTP layer
        names, tensors = bridge._weight_to_hf_format(
            "embedding.word_embeddings.weight", fake_weight
        )
        assert len(names) >= 2, f"Expected >=2 HF names for embedding, got {names}"
        assert len(tensors) == len(names), "Name/tensor count mismatch"
        joined = " ".join(names)
        assert f".{n_layers}." in joined, f"Missing layer {n_layers} in: {names}"
        assert ".61." not in joined, f"Hardcoded 61 in: {names}"

        # Output layer weight → should also map dynamically
        names2, tensors2 = bridge._weight_to_hf_format(
            "output_layer.weight", fake_weight
        )
        assert len(names2) >= 2, f"Expected >=2 HF names for output, got {names2}"
        joined2 = " ".join(names2)
        assert f".{n_layers}." in joined2, f"Missing layer {n_layers} in: {names2}"
        assert ".61." not in joined2, f"Hardcoded 61 in: {names2}"


# [pr_diff] fail_to_pass
def test_critic_wrapper_in_bridge_path():
    """Bridge path in get_model_provider_func must handle critic role (wrapper pattern)."""
    # AST-only because: model_provider.py imports megatron internals (GPTModel,
    # MegatronModule, LinearForLastLayer) that require a full megatron install
    source = Path(PROVIDER_PATH).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_model_provider_func":
            for child in ast.walk(node):
                if not isinstance(child, ast.If):
                    continue
                # Match exactly: if role == "critic": (simple Compare, not BoolOp)
                test = child.test
                if not isinstance(test, ast.Compare):
                    continue
                if not (isinstance(test.left, ast.Name) and test.left.id == "role"):
                    continue
                if not (len(test.comparators) == 1
                        and isinstance(test.comparators[0], ast.Constant)
                        and test.comparators[0].value == "critic"):
                    continue
                # Found "if role == 'critic':" — verify wrapper pattern
                has_func_def = any(
                    isinstance(c, ast.FunctionDef) for c in child.body
                )
                has_return = any(
                    isinstance(c, ast.Return) for c in child.body
                )
                if has_func_def and has_return:
                    return  # PASS
    raise AssertionError(
        "No critic wrapper pattern found in get_model_provider_func bridge path"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_inherits_deepseek_v3_bridge():
    """GLM4MoELiteBridge must inherit DeepseekV3Bridge and be registered."""
    _setup_mocks()
    cls = _load_bridge_class()
    parent = sys.modules["mbridge.models"].DeepseekV3Bridge
    assert issubclass(cls, parent), (
        f"GLM4MoELiteBridge must inherit DeepseekV3Bridge, bases: {cls.__bases__}"
    )
    assert hasattr(cls, "_registered_name"), "Missing @register_model decorator"
    assert cls._registered_name == "glm4_moe_lite", (
        f"Expected registration name 'glm4_moe_lite', got '{cls._registered_name}'"
    )


# [static] fail_to_pass
def test_not_stub():
    """GLM4MoELiteBridge must have >=4 meaningful class members (not just pass)."""
    # AST-only because: counting meaningful class body members (excluding pass
    # and docstrings) cannot be done behaviorally without leaking required method names
    source = Path(BRIDGE_PATH).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and "GLM4MoELite" in node.name:
            meaningful = 0
            for item in node.body:
                if isinstance(item, ast.Pass):
                    continue
                if isinstance(item, ast.Expr) and isinstance(
                    item.value, ast.Constant
                ) and isinstance(item.value.value, str):
                    continue  # docstring
                meaningful += 1
            assert meaningful >= 4, (
                f"Class too small ({meaningful} members) - likely a stub"
            )
            return  # PASS
    raise AssertionError("GLM4MoELiteBridge not found")
