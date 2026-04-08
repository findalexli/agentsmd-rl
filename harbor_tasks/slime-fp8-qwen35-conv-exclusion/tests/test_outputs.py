"""
Task: slime-fp8-qwen35-conv-exclusion
Repo: THUDM/slime @ f9f7b566cca476aeeb963b67a44d663da79e0484
PR:   1769

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
from pathlib import Path

REPO = "/workspace/slime"
TARGET = f"{REPO}/tools/convert_hf_to_fp8.py"

# ---------------------------------------------------------------------------
# Mock harness for subprocess execution (torch/safetensors not installed)
# ---------------------------------------------------------------------------

_MOCK_HARNESS = r'''
import sys
import types
import json
from pathlib import Path

TARGET = "/workspace/slime/tools/convert_hf_to_fp8.py"

class FakeTensor:
    def __init__(self, shape=(1,)):
        self._shape = shape
    def to(self, *a, **kw): return self
    def float(self): return self
    def half(self): return self
    def reshape(self, *a): return self
    def view(self, *a): return self
    def contiguous(self): return self
    def clone(self): return self
    def abs(self): return self
    def max(self): return FakeTensor()
    def item(self): return 1.0
    @property
    def shape(self): return self._shape
    @property
    def dtype(self): return "fake_dtype"
    def __truediv__(self, other): return self
    def __mul__(self, other): return self

mock_torch = types.ModuleType("torch")
mock_torch.float8_e4m3fn = "fake_dtype"
mock_torch.float16 = "fake_f16"
mock_torch.bfloat16 = "fake_bf16"
mock_torch.float32 = "fake_f32"
mock_torch.Tensor = FakeTensor
mock_torch.zeros = lambda *a, **kw: FakeTensor()
mock_torch.ones = lambda *a, **kw: FakeTensor()
mock_torch.tensor = lambda *a, **kw: FakeTensor()
mock_torch.empty = lambda *a, **kw: FakeTensor()
mock_torch.amax = lambda *a, **kw: FakeTensor()

mock_cuda = types.ModuleType("torch.cuda")
mock_cuda.memory_allocated = lambda: 0
mock_torch.cuda = mock_cuda

mock_nn = types.ModuleType("torch.nn")
mock_nn_functional = types.ModuleType("torch.nn.functional")
mock_nn_functional.pad = lambda *a, **kw: FakeTensor()
mock_nn.functional = mock_nn_functional
mock_nn.F = mock_nn_functional
mock_torch.nn = mock_nn

class FakeFinfo:
    def __init__(self, dtype=None):
        self.max = 448.0
        self.min = -448.0
mock_torch.finfo = FakeFinfo

sys.modules["torch"] = mock_torch
sys.modules["torch.cuda"] = mock_cuda
sys.modules["torch.nn"] = mock_nn
sys.modules["torch.nn.functional"] = mock_nn_functional

mock_tqdm = types.ModuleType("tqdm")
mock_tqdm.tqdm = lambda x, **kw: x
sys.modules["tqdm"] = mock_tqdm

_test_weights = {}
_saved_data = {}

mock_sf = types.ModuleType("safetensors")

class FakeSafeOpen:
    def __init__(self, path, framework=None, device=None):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *a):
        pass
    def keys(self):
        return list(_test_weights.keys())
    def get_tensor(self, k):
        return _test_weights[k]

mock_sf.safe_open = FakeSafeOpen
mock_sf_torch = types.ModuleType("safetensors.torch")

def _fake_save(data, path, **kw):
    _saved_data.clear()
    _saved_data.update(data)

mock_sf_torch.save_file = _fake_save
mock_sf.torch = mock_sf_torch
sys.modules["safetensors"] = mock_sf
sys.modules["safetensors.torch"] = mock_sf_torch

source = Path(TARGET).read_text()
ns = {"__builtins__": __builtins__, "__name__": "__not_main__", "__file__": TARGET}
exec(compile(source, TARGET, "exec"), ns)

def mock_quant_fp8(tensor, strategy, block_size):
    return FakeTensor(), FakeTensor()
ns["quant_fp8"] = mock_quant_fp8

class FakeCollector:
    def __init__(self):
        self.q_weights = {}
        self.modules = []
    def add_result(self, filename, q_weights, module_names):
        self.q_weights.update(q_weights)
        self.modules.extend(module_names)

def run_with_keys(test_keys):
    _test_weights.clear()
    for k in test_keys:
        _test_weights[k] = FakeTensor()
    _saved_data.clear()
    process_file = ns["process_file"]
    collector = FakeCollector()
    process_file("/fake/input", "/fake/output", "test.safetensors", "tensor", None, collector)
    quantized_keys = []
    for k in test_keys:
        scale_a = k.replace(".weight", ".weight_scale_inv")
        scale_b = k.replace(".weight", ".weight_scale")
        has_scale = (scale_a != k and scale_a in _saved_data) or \
                    (scale_b != k and scale_b in _saved_data)
        if has_scale:
            quantized_keys.append(k)
    return quantized_keys, sorted(_saved_data.keys())
'''


def _run_fp8_quantization(test_keys: list) -> tuple:
    """Execute process_file with given keys via subprocess.

    Returns (set of quantized keys, set of all saved keys).
    """
    script = _MOCK_HARNESS + "\n" + (
        f"test_keys = {test_keys!r}\n"
        "quantized, saved = run_with_keys(test_keys)\n"
        "print(json.dumps({'quantized': quantized, 'saved': saved}))\n"
    )
    script_path = Path(REPO) / "_eval_fp8_test.py"
    script_path.write_text(script)
    try:
        r = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Subprocess failed:\n{r.stderr}"
        result = json.loads(r.stdout.strip())
        return set(result["quantized"]), set(result["saved"])
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """convert_hf_to_fp8.py must be valid Python."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mamba_keys_excluded():
    """Mamba-style keys (conv1d, A_log, dt_bias, in_proj_a, in_proj_b) must be excluded from FP8."""
    test_keys = [
        "model.layers.0.self_attn.q_proj.weight",       # normal -> quantized
        "model.layers.0.mamba.conv1d.weight",            # Mamba -> excluded
        "model.layers.5.mamba.A_log",                    # Mamba -> excluded
        "model.layers.3.mamba.dt_bias",                  # Mamba -> excluded
        "model.layers.1.mamba.in_proj_a.weight",         # Mamba -> excluded
        "model.layers.2.mamba.in_proj_b.weight",         # Mamba -> excluded
    ]
    quantized, _ = _run_fp8_quantization(test_keys)

    mamba_keys = {k for k in test_keys if "mamba" in k}
    for k in mamba_keys:
        assert k not in quantized, f"Mamba key incorrectly quantized: {k}"

    normal = "model.layers.0.self_attn.q_proj.weight"
    assert normal in quantized, f"Normal weight should be quantized: {normal}"


# [pr_diff] fail_to_pass
def test_mamba_keys_varied_layers():
    """Mamba exclusions work across different layer indices (not hardcoded)."""
    test_keys = [
        "model.layers.17.mamba.conv1d.weight",
        "model.layers.42.mamba.A_log",
        "model.layers.99.mamba.dt_bias",
        "model.layers.0.mamba.in_proj_a.weight",
        "model.layers.31.mamba.in_proj_b.weight",
        "model.layers.17.self_attn.v_proj.weight",      # normal -> quantized
    ]
    quantized, _ = _run_fp8_quantization(test_keys)

    mamba_keys = {k for k in test_keys if "mamba" in k}
    for k in mamba_keys:
        assert k not in quantized, f"Mamba key quantized at different index: {k}"

    assert "model.layers.17.self_attn.v_proj.weight" in quantized, \
        "Normal weight should be quantized"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_preexisting_exclusions_preserved():
    """Pre-existing exclusions (layernorm, embed, gate, lm_head) still work."""
    test_keys = [
        "model.layers.0.input_layernorm.weight",              # excluded
        "model.embed_tokens.weight",                           # excluded
        "model.layers.0.mlp.gate.weight",                      # excluded
        "lm_head.weight",                                      # excluded
        "model.layers.0.post_attention_layernorm.weight",      # excluded
        "model.layers.0.self_attn.k_proj.weight",              # quantized
        "model.layers.0.mlp.up_proj.weight",                   # quantized
    ]
    quantized, _ = _run_fp8_quantization(test_keys)

    must_exclude = [
        "model.layers.0.input_layernorm.weight",
        "model.embed_tokens.weight",
        "model.layers.0.mlp.gate.weight",
        "lm_head.weight",
        "model.layers.0.post_attention_layernorm.weight",
    ]
    must_quantize = [
        "model.layers.0.self_attn.k_proj.weight",
        "model.layers.0.mlp.up_proj.weight",
    ]

    for k in must_exclude:
        assert k not in quantized, f"Should be excluded but was quantized: {k}"
    for k in must_quantize:
        assert k in quantized, f"Should be quantized but was not: {k}"


# [pr_diff] pass_to_pass
def test_nonweight_keys_skipped():
    """Keys without 'weight' (e.g., bias) must not be quantized."""
    test_keys = [
        "model.layers.0.self_attn.q_proj.bias",        # non-weight -> excluded
        "model.layers.3.self_attn.o_proj.bias",         # non-weight -> excluded
        "model.layers.0.self_attn.q_proj.weight",       # weight -> quantized
    ]
    quantized, _ = _run_fp8_quantization(test_keys)

    assert "model.layers.0.self_attn.q_proj.bias" not in quantized, \
        "Bias key was incorrectly quantized"
    assert "model.layers.3.self_attn.o_proj.bias" not in quantized, \
        "Bias key was incorrectly quantized"
    assert "model.layers.0.self_attn.q_proj.weight" in quantized, \
        "Normal weight should be quantized"


# [pr_diff] pass_to_pass
def test_excluded_keys_preserved_in_output():
    """All keys (quantized and excluded) must appear in the output file."""
    test_keys = [
        "model.layers.0.mamba.conv1d.weight",
        "model.layers.0.input_layernorm.weight",
        "model.layers.0.self_attn.q_proj.weight",
    ]
    _, saved = _run_fp8_quantization(test_keys)

    for k in test_keys:
        assert k in saved, f"Key missing from output: {k}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_process_file_not_stub():
    """process_file must have non-trivial implementation (not a stub)."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_file":
            stmts = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.Assign, ast.AugAssign, ast.For, ast.If, ast.With, ast.Return, ast.Call))
            )
            assert stmts >= 8, f"process_file has only {stmts} statements -- likely a stub"
            return
    raise AssertionError("process_file function not found")
