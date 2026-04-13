"""
Task: sglang-lora-auto-detect-target-modules
Repo: sgl-project/sglang @ 9b29131961bb6c167e6956dae60a6269232ca694

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/sglang"


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    for f in ["python/sglang/srt/lora/utils.py",
              "python/sglang/srt/lora/lora_manager.py"]:
        source = Path(f"{REPO}/{f}").read_text()
        ast.parse(source)


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI-style checks
# -----------------------------------------------------------------------------

def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    # Only check for critical errors (F821 undefined names, F401 unused imports)
    # Ignore F541 (f-string without placeholders) as it's pre-existing in the repo
    r = subprocess.run(
        ["ruff", "check", "python/sglang/srt/lora/utils.py", "--select=F401,F821"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed on utils.py:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_ruff_check_lora_manager():
    """Repo's ruff linter passes on lora_manager.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr[-500:]}"

    # Only check for critical errors (F821 undefined names, F401 unused imports)
    r = subprocess.run(
        ["ruff", "check", "python/sglang/srt/lora/lora_manager.py", "--select=F401,F821"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed on lora_manager.py:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_isort_check():
    """Repo's isort check passes on modified LoRA files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install isort: {r.stderr[-500:]}"

    # Check isort compliance for both modified files
    for f in ["python/sglang/srt/lora/utils.py", "python/sglang/srt/lora/lora_manager.py"]:
        r = subprocess.run(
            ["isort", "--check-only", f],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"isort check failed on {f}:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_black_check():
    """Repo's black formatter check passes on modified LoRA files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to install black: {r.stderr[-500:]}"

    # Check black formatting for both modified files
    for f in ["python/sglang/srt/lora/utils.py", "python/sglang/srt/lora/lora_manager.py"]:
        r = subprocess.run(
            ["black", "--check", f],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"black check failed on {f}:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_lora_manager_structure():
    """lora_manager.py has correct imports and structure pre-fix (pass_to_pass)."""
    source = Path(f"{REPO}/python/sglang/srt/lora/lora_manager.py").read_text()
    tree = ast.parse(source)

    # Check that get_normalized_target_modules is imported from sglang.srt.lora.utils
    # (this exists in base commit and is the foundation for the new functionality)
    has_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            # The module can be sglang.srt.lora.utils or .utils depending on Python version
            if "utils" in node.module and "lora" in node.module:
                for alias in node.names:
                    if alias.name == "get_normalized_target_modules":
                        has_import = True
                        break

    # Also check for the import by looking for the pattern in the source
    if not has_import:
        if "from sglang.srt.lora.utils import" in source and "get_normalized_target_modules" in source:
            has_import = True

    assert has_import, "get_normalized_target_modules not found in imports"

    # Verify init_lora_shapes function exists
    has_init_lora_shapes = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_lora_shapes":
            has_init_lora_shapes = True
            break

    assert has_init_lora_shapes, "init_lora_shapes function not found"


def test_repo_import_utils():
    """LoRA utils module can be imported without errors (pass_to_pass)."""
    # Use the same mocked import approach as the other tests
    code = '''
# Verify we can load the module and its key functions work
assert callable(_utils.get_normalized_target_modules), "get_normalized_target_modules not callable"
assert callable(_utils.get_hidden_dim), "get_hidden_dim not callable"
assert callable(_utils.get_stacked_multiply), "get_stacked_multiply not callable"
assert callable(_utils.get_target_module_name), "get_target_module_name not callable"

# Test that the dataclass and enum are importable (they're defined at module level)
assert _utils.LoRABatchInfo is not None, "LoRABatchInfo not found"
assert _utils.LoRAType is not None, "LoRAType not found"

# Verify the key function works with basic input
result = _utils.get_normalized_target_modules(["q_proj", "v_proj"])
assert "qkv_proj" in result, f"Expected 'qkv_proj' in result, got {result}"
print("PASS")
'''
    _run_subprocess_test(code)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: auto_detect_lora_target_modules
#
# These use subprocess.run() to execute Python code that loads utils.py
# with mocked dependencies (avoiding GPU requirements).
# -----------------------------------------------------------------------------

def _build_test_script(test_code: str) -> str:
    """Build a Python script that mocks sglang layers, loads utils.py, and runs test code."""
    return f'''
import importlib.util
import sys
import types
import torch.nn as nn

REPO = "{REPO}"

# Mock classes — stand-ins for sglang layer types
class _LinearBase(nn.Module):
    pass

class _FusedMoE(nn.Module):
    pass

class _ParallelLMHead(nn.Module):
    pass

# Stub heavy sglang submodules
def _mock_module(path, **attrs):
    parts = path.split(".")
    for i in range(1, len(parts) + 1):
        key = ".".join(parts[:i])
        if key not in sys.modules:
            sys.modules[key] = types.ModuleType(key)
    mod = sys.modules[path]
    for k, v in attrs.items():
        setattr(mod, k, v)

_mock_module("sglang.srt.model_executor.forward_batch_info",
             ForwardBatch=type("ForwardBatch", (), {{}}))
_mock_module("sglang.srt.utils.hf_transformers_utils",
             AutoConfig=type("AutoConfig", (), {{}}))
_mock_module("sglang.srt.layers.linear", LinearBase=_LinearBase)
_mock_module("sglang.srt.layers.moe.fused_moe_triton.layer", FusedMoE=_FusedMoE)
_mock_module("sglang.srt.layers.vocab_parallel_embedding",
             ParallelLMHead=_ParallelLMHead)

# Load utils.py
def _load_utils():
    mod_name = "sglang.srt.lora.utils"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    _mock_module("sglang.srt.lora")
    spec = importlib.util.spec_from_file_location(
        mod_name,
        f"{{REPO}}/python/sglang/srt/lora/utils.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod

_utils = _load_utils()

{test_code}
'''


def _run_subprocess_test(test_code: str, timeout: int = 30) -> None:
    """Run test code in a subprocess and assert success."""
    script = _build_test_script(test_code)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )
    if result.returncode != 0:
        raise AssertionError(f"Subprocess test failed: stdout={{result.stdout}}, stderr={{result.stderr}}")


def test_auto_detect_dense_model():
    """auto_detect returns correct modules for a full dense transformer model."""
    code = '''
auto_detect = _utils.auto_detect_lora_target_modules

model = nn.Module()
inner = nn.Module()
layer = nn.Module()

attn = nn.Module()
attn.qkv_proj = _LinearBase()
attn.o_proj = _LinearBase()
layer.self_attn = attn

mlp = nn.Module()
mlp.gate_up_proj = _LinearBase()
mlp.down_proj = _LinearBase()
layer.mlp = mlp

inner.layers = nn.ModuleList([layer])
inner.embed_tokens = nn.Embedding(10, 8)  # NOT LinearBase — excluded
model.model = inner
model.lm_head = _ParallelLMHead()

detected = auto_detect(model)
expected = {"qkv_proj", "o_proj", "gate_up_proj", "down_proj", "lm_head"}
assert detected == expected, f"detected={sorted(detected)}, expected={sorted(expected)}"
print("PASS")
'''
    _run_subprocess_test(code)


def test_auto_detect_single_module():
    """Anti-hardcoding: single-module model returns only that module."""
    code = '''
auto_detect = _utils.auto_detect_lora_target_modules

model = nn.Module()
inner = nn.Module()
layer = nn.Module()
attn = nn.Module()
attn.o_proj = _LinearBase()
layer.self_attn = attn
inner.layers = nn.ModuleList([layer])
model.model = inner

detected = auto_detect(model)
assert detected == {"o_proj"}, f"detected={sorted(detected)}"
print("PASS")
'''
    _run_subprocess_test(code)


def test_auto_detect_filters_unknown_modules():
    """Unknown-named linear modules are excluded from detection."""
    code = '''
auto_detect = _utils.auto_detect_lora_target_modules

model = nn.Module()
layer = nn.Module()
layer.weird_custom_proj = _LinearBase()
layer.another_unknown = _LinearBase()
model.layers = nn.ModuleList([layer])

detected = auto_detect(model)
assert detected == set(), f"unknown modules not filtered: {sorted(detected)}"
print("PASS")
'''
    _run_subprocess_test(code)


def test_auto_detect_includes_lm_head():
    """ParallelLMHead module is detected as lm_head."""
    code = '''
auto_detect = _utils.auto_detect_lora_target_modules

model = nn.Module()
inner = nn.Module()
inner.layers = nn.ModuleList([])
model.model = inner
model.lm_head = _ParallelLMHead()

detected = auto_detect(model)
assert "lm_head" in detected, f"lm_head not in {sorted(detected)}"
print("PASS")
'''
    _run_subprocess_test(code)


def test_auto_detect_moe_modules():
    """FusedMoE module produces gate_up_proj and down_proj."""
    code = '''
auto_detect = _utils.auto_detect_lora_target_modules

model = nn.Module()
layer = nn.Module()
layer.moe = _FusedMoE()
model.layers = nn.ModuleList([layer])

detected = auto_detect(model)
assert "gate_up_proj" in detected, f"gate_up_proj not in {sorted(detected)}"
assert "down_proj" in detected, f"down_proj not in {sorted(detected)}"
print("PASS")
'''
    _run_subprocess_test(code)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: get_normalized_target_modules
# -----------------------------------------------------------------------------

def test_normalize_rejects_invalid_string():
    """ValueError raised for unrecognized string shorthand."""
    code = '''
for bad_input in ["some-invalid-shorthand", "linear", "custom-target"]:
    try:
        _utils.get_normalized_target_modules(bad_input)
        raise AssertionError(f"Should have raised ValueError for {bad_input}")
    except ValueError as e:
        if "all" not in str(e).lower() or "all-linear" not in str(e).lower():
            raise AssertionError(f"Expected error message mentioning 'all' and 'all-linear', got: {e}")
print("PASS")
'''
    _run_subprocess_test(code)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural (can't instantiate LoRAManager without GPU)
# -----------------------------------------------------------------------------

def test_init_lora_shapes_no_raise():
    """init_lora_shapes must not raise ValueError('cannot be resolved automatically')."""
    source = Path(f"{REPO}/python/sglang/srt/lora/lora_manager.py").read_text()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_lora_shapes":
            func_node = node
            break
    assert func_node is not None, "init_lora_shapes not found"

    for node in ast.walk(func_node):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) \
                    and exc.func.id == "ValueError":
                for arg in exc.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        assert "cannot be resolved automatically" not in arg.value, \
                            "Old ValueError for 'all-linear' still present"
                    if isinstance(arg, ast.JoinedStr):
                        for val in arg.values:
                            if isinstance(val, ast.Constant) and isinstance(val.value, str):
                                assert "cannot be resolved automatically" not in val.value, \
                                    "Old ValueError (f-string) still present"


def test_init_lora_modules_none_guard():
    """init_lora_modules must guard against get_layer_id returning None."""
    source = Path(f"{REPO}/python/sglang/srt/lora/lora_manager.py").read_text()
    tree = ast.parse(source)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "init_lora_modules":
            func_node = node
            break
    assert func_node is not None, "init_lora_modules not found"

    has_none_guard = False
    for node in ast.walk(func_node):
        if isinstance(node, ast.Compare):
            left_is_layer_id = (isinstance(node.left, ast.Name)
                                and node.left.id == "layer_id")
            has_none_comp = any(
                isinstance(c, ast.Constant) and c.value is None
                for c in node.comparators
            )
            if left_is_layer_id and has_none_comp:
                has_none_guard = True
                break
            left_is_none = (isinstance(node.left, ast.Constant)
                            and node.left.value is None)
            comp_is_layer_id = any(
                isinstance(c, ast.Name) and c.id == "layer_id"
                for c in node.comparators
            )
            if left_is_none and comp_is_layer_id:
                has_none_guard = True
                break

    assert has_none_guard, "No None guard for layer_id in init_lora_modules"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# -----------------------------------------------------------------------------

def test_normalize_list_input():
    """List inputs are still normalized correctly."""
    code = '''
result = _utils.get_normalized_target_modules(
    ["q_proj", "v_proj", "gate_proj", "down_proj"]
)
expected = {"qkv_proj", "gate_up_proj", "down_proj"}
assert result == expected, f"{result} != {expected}"
print("PASS")
'''
    _run_subprocess_test(code)


def test_normalize_sentinel():
    """'all-linear' and 'all' return sentinel {'all'}."""
    code = '''
for shorthand in ["all-linear", "all"]:
    result = _utils.get_normalized_target_modules(shorthand)
    assert result == {"all"}, f"For '{shorthand}': expected {{'all'}}, got {result}"
print("PASS")
'''
    _run_subprocess_test(code)
