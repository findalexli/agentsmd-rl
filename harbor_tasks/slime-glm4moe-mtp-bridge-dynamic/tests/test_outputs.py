"""
Task: slime-glm4moe-mtp-bridge-dynamic
Repo: THUDM/slime @ 57e76686346beeaaec4010ebefc56b9949686457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
BRIDGE_PATH = f"{REPO}/slime_plugins/mbridge/glm4moe_lite.py"
PROVIDER_PATH = f"{REPO}/slime/backends/megatron_utils/model_provider.py"

_MOCK_PREAMBLE = """
import sys, types
from pathlib import Path

BRIDGE_PATH = "/workspace/slime/slime_plugins/mbridge/glm4moe_lite.py"

_torch = types.ModuleType("torch")
class _FakeTensor: pass
_torch.Tensor = _FakeTensor
sys.modules["torch"] = _torch

for _m in ["mbridge", "mbridge.core", "mbridge.models", "mbridge.core.safetensor_io"]:
    sys.modules[_m] = types.ModuleType(_m)

def _register_model(name):
    def dec(cls):
        cls._registered_name = name
        return cls
    return dec
sys.modules["mbridge.core"].register_model = _register_model

class MockSafeTensorIO:
    def __init__(self, path): self.path = path
sys.modules["mbridge.core.safetensor_io"].SafeTensorIO = MockSafeTensorIO

class _MockBridgeBase:
    def _weight_to_hf_format(self, name, weights):
        return [name], [weights]

class MockDeepseekV3Bridge(_MockBridgeBase):
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
        _d = {
            "mtp.layers.0.enorm.weight": "model.layers.61.enorm.weight",
            "mtp.layers.0.hnorm.weight": "model.layers.61.hnorm.weight",
            "mtp.layers.0.eh_proj.weight": "model.layers.61.eh_proj.weight",
            "mtp.layers.0.final_layernorm.weight": "model.layers.61.shared_head.norm.weight",
        }
        if name in _d:
            return [_d[name]]
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
            hf = self._SHARED_STATE_DICT_MAPPING[name]
            return hf, [weights] * len(hf)
        return [name], [weights]

sys.modules["mbridge.models"].DeepseekV3Bridge = MockDeepseekV3Bridge

_ns = {}
_src = Path(BRIDGE_PATH).read_text()
exec(compile(_src, BRIDGE_PATH, "exec"), _ns)
Bridge = _ns["GLM4MoELiteBridge"]

def make_config(num_hidden_layers=47, num_nextn_predict_layers=1,
                rope_parameters=None, rope_theta=None):
    cfg = types.SimpleNamespace(
        num_hidden_layers=num_hidden_layers,
        num_nextn_predict_layers=num_nextn_predict_layers,
    )
    if rope_parameters is not None:
        cfg.rope_parameters = rope_parameters
    if rope_theta is not None:
        cfg.rope_theta = rope_theta
    return cfg

def make_bridge(num_hidden_layers=47, rope_theta_val=500000):
    cfg = make_config(
        num_hidden_layers=num_hidden_layers,
        rope_parameters={"rope_theta": rope_theta_val},
    )
    return Bridge(cfg)
"""


def _run_bridge_test(test_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute test code in a subprocess with mocked torch/mbridge deps."""
    script = Path(REPO) / "_eval_bridge_test.py"
    script.write_text(_MOCK_PREAMBLE + "\n" + test_code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def test_syntax_check():
    """Modified files must parse without errors."""
    for path in [BRIDGE_PATH, PROVIDER_PATH]:
        source = Path(path).read_text()
        ast.parse(source)


def test_rope_theta_from_rope_parameters():
    """Bridge __init__ must extract rope_theta from rope_parameters dict."""
    r = _run_bridge_test("""
for theta_val in [500000, 1000000, 10000]:
    bridge = make_bridge(rope_theta_val=theta_val)
    cfg = bridge.hf_config
    assert hasattr(cfg, "rope_theta"), "rope_theta not patched"
    assert cfg.rope_theta == theta_val, f"Expected {theta_val}, got {cfg.rope_theta}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_rope_theta_default_when_missing():
    """Bridge must handle missing rope_parameters gracefully."""
    r = _run_bridge_test("""
cfg = make_config(rope_parameters=None)
bridge = Bridge(cfg)
assert hasattr(bridge.hf_config, "rope_theta"), "rope_theta not set when missing"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_shared_mapping_dynamic_layer():
    """_SHARED_STATE_DICT_MAPPING must use num_hidden_layers, not hardcoded 61."""
    r = _run_bridge_test("""
for n in [47, 32, 60]:
    bridge = make_bridge(num_hidden_layers=n)
    mapping = bridge._SHARED_STATE_DICT_MAPPING
    assert "embedding.word_embeddings.weight" in mapping
    assert "output_layer.weight" in mapping
    for key, values in mapping.items():
        for v in values:
            assert ".61." not in v, f"Hardcoded 61 in mapping: {v}"
        layer_refs = [v for v in values if f".{n}." in v]
        assert len(layer_refs) >= 1, f"No layer-{n} ref for {key}: {values}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_convert_mtp_param_dynamic():
    """_convert_mtp_param must produce layer names matching num_hidden_layers."""
    r = _run_bridge_test("""
for n in [47, 32]:
    bridge = make_bridge(num_hidden_layers=n)
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
        assert f".{n}." in joined, f"Expected layer {n} for {name}, got: {result}"
        assert ".61." not in joined, f"Hardcoded 61 for {name}: {result}"
    proxy = bridge._convert_mtp_param(
        "mtp.layers.0.transformer_layer.self_attention.proj.weight"
    )
    assert ".61." not in " ".join(proxy), f"Hardcoded 61 in proxy: {proxy}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_safetensor_io_standard_loader():
    """Bridge must use SafeTensorIO (bf16), not parent's FP8 dequant loader."""
    r = _run_bridge_test("""
for path in ["/fake/weights/path", "/other/model/dir"]:
    bridge = make_bridge()
    result = bridge._get_safetensor_io(path)
    assert result != "FP8_DEQUANT_LOADER", "Still using parent FP8 dequant loader"
    assert hasattr(result, "path"), f"Expected SafeTensorIO with .path, got {type(result)}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_weight_to_hf_format_shared():
    """_weight_to_hf_format returns dynamic layer mappings for shared weights."""
    r = _run_bridge_test("""
for n in [47, 32, 60]:
    bridge = make_bridge(num_hidden_layers=n)
    names, tensors = bridge._weight_to_hf_format("embedding.word_embeddings.weight", "TENSOR")
    assert len(names) >= 2, f"Expected >=2 HF names, got {names}"
    assert len(tensors) == len(names), "Name/tensor count mismatch"
    joined = " ".join(names)
    assert f".{n}." in joined, f"Missing layer {n} in: {names}"
    assert ".61." not in joined, f"Hardcoded 61 in: {names}"
    names2, tensors2 = bridge._weight_to_hf_format("output_layer.weight", "TENSOR")
    assert len(names2) >= 2, f"Expected >=2 HF names for output, got {names2}"
    joined2 = " ".join(names2)
    assert f".{n}." in joined2, f"Missing layer {n} in: {names2}"
    assert ".61." not in joined2, f"Hardcoded 61 in: {names2}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_critic_wrapper_in_bridge_path():
    """Bridge path in get_model_provider_func must handle critic role."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
from pathlib import Path

source = Path("/workspace/slime/slime/backends/megatron_utils/model_provider.py").read_text()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_model_provider_func":
        for child in ast.walk(node):
            if not isinstance(child, ast.If):
                continue
            test = child.test
            if not isinstance(test, ast.Compare):
                continue
            if not (isinstance(test.left, ast.Name) and test.left.id == "role"):
                continue
            if not (len(test.comparators) == 1
                    and isinstance(test.comparators[0], ast.Constant)
                    and test.comparators[0].value == "critic"):
                continue
            has_func = any(isinstance(c, ast.FunctionDef) for c in child.body)
            has_ret = any(isinstance(c, ast.Return) for c in child.body)
            if has_func and has_ret:
                print("PASS")
                exit(0)
raise AssertionError("No critic wrapper pattern in bridge path")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

PIP_DEPS = ["pytest", "numpy", "packaging", "pyyaml", "omegaconf", "tqdm", "httpx", "pybase64", "pylatexenc", "sympy", "aiohttp"]


def _install_deps():
    """Install test dependencies."""
    subprocess.run(["pip", "install", "-q"] + PIP_DEPS, capture_output=True, cwd=REPO)
    subprocess.run(["pip", "install", "-e", ".", "--no-deps", "-q"], capture_output=True, cwd=REPO)


def test_repo_ruff_check():
    """Ruff lint check passes on slime and slime_plugins (pass_to_pass)."""
    subprocess.run(["pip", "install", "-q", "ruff"], capture_output=True, cwd=REPO)
    r = subprocess.run(
        ["ruff", "check", "slime", "slime_plugins", "--output-format=concise"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_repo_test_chunked_gae():
    """Core GAE test passes (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/test_chunked_gae.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"test_chunked_gae failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_repo_plugin_contracts_generate():
    """Plugin contracts - generate tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/test_plugin_generate_contracts.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin generate contracts failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_repo_plugin_contracts_path_loading():
    """Plugin contracts - path loading tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/test_plugin_path_loading_contracts.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin path loading contracts failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_repo_plugin_contracts_runtime_hook():
    """Plugin contracts - runtime hook tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/test_plugin_runtime_hook_contracts.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin runtime hook contracts failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_repo_plugin_contracts_rollout():
    """Plugin contracts - rollout tests pass (pass_to_pass)."""
    _install_deps()
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/test_plugin_rollout_contracts.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin rollout contracts failed:\\n{r.stdout[-500:]}\\n{r.stderr[-500:]}"


def test_inherits_deepseek_v3_bridge():
    """GLM4MoELiteBridge must inherit DeepseekV3Bridge and be registered."""
    r = _run_bridge_test("""
parent = sys.modules["mbridge.models"].DeepseekV3Bridge
assert issubclass(Bridge, parent), f"Must inherit DeepseekV3Bridge, bases: {Bridge.__bases__}"
assert hasattr(Bridge, "_registered_name"), "Missing @register_model"
assert Bridge._registered_name == "glm4_moe_lite", f"Wrong name: {Bridge._registered_name}"
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_not_stub():
    """GLM4MoELiteBridge must have >=4 meaningful class members (not just pass)."""
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
                    continue
                meaningful += 1
            assert meaningful >= 4, (
                f"Class too small ({meaningful} members) - likely a stub"
            )
            return
    raise AssertionError("GLM4MoELiteBridge not found")
