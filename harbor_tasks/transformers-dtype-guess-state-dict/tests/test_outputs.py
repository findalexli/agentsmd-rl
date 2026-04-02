"""
Task: transformers-dtype-guess-state-dict
Repo: huggingface/transformers @ 7cd9b985e0698d4f625a18be0125231b6b930390
PR:   44883

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import collections
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/modeling_utils.py"


# ---------------------------------------------------------------------------
# Helpers — extract get_state_dict_dtype without importing torch
# AST-only because: torch is not installed in the test container
# ---------------------------------------------------------------------------

class _MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"torch.{self.name}"
    def __repr__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        return isinstance(other, _MockDtype) and self.name == other.name
    def __hash__(self):
        return hash(self.name)


class _MockTensor:
    """Simulates a torch.Tensor with .dtype and .is_floating_point()."""
    def __init__(self, dtype: _MockDtype):
        self.dtype = dtype
    def is_floating_point(self):
        name = self.dtype.name.lower()
        return "float" in name or "f16" in name or "bf16" in name


# All dtype names used in tests
_DTYPE_NAMES = [
    "float32", "float16", "bfloat16", "float64",
    "float8_e4m3fn", "float8_e5m2", "float4_e2m1fn",
    "int8", "int32", "int64",
]


def _load_get_state_dict_dtype():
    """Extract and exec get_state_dict_dtype with mock torch."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
            lines = source.splitlines()
            func_source = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            attrs = {name: _MockDtype(name) for name in _DTYPE_NAMES}
            torch_ns = type("torch", (), attrs)()
            ns = {"torch": torch_ns, "__builtins__": __builtins__}
            exec(compile(func_source, "<get_state_dict_dtype>", "exec"), ns)
            return ns["get_state_dict_dtype"], torch_ns
    raise RuntimeError("get_state_dict_dtype not found in modeling_utils.py")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """modeling_utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_float8_e4m3fn_skipped():
    """float8_e4m3fn should be skipped, returning next standard dtype."""
    fn, torch_ns = _load_get_state_dict_dtype()
    # Test with float16 as fallback
    sd = collections.OrderedDict([
        ("quant_w", _MockTensor(torch_ns.float8_e4m3fn)),
        ("norm_w", _MockTensor(torch_ns.float16)),
    ])
    assert fn(sd) == torch_ns.float16
    # Test with float32 as fallback
    sd2 = collections.OrderedDict([
        ("a", _MockTensor(torch_ns.float8_e4m3fn)),
        ("b", _MockTensor(torch_ns.float32)),
    ])
    assert fn(sd2) == torch_ns.float32


# [pr_diff] fail_to_pass
def test_float8_e5m2_skipped():
    """float8_e5m2 should be skipped, returning next standard dtype."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict([
        ("layer.attn", _MockTensor(torch_ns.float8_e5m2)),
        ("layer.norm", _MockTensor(torch_ns.bfloat16)),
    ])
    assert fn(sd) == torch_ns.bfloat16
    # Also test with float64 fallback
    sd2 = collections.OrderedDict([
        ("x", _MockTensor(torch_ns.float8_e5m2)),
        ("y", _MockTensor(torch_ns.float64)),
    ])
    assert fn(sd2) == torch_ns.float64


# [pr_diff] fail_to_pass
def test_float4_e2m1fn_skipped():
    """float4_e2m1fn should be skipped, returning next standard dtype."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict([
        ("embed.weight", _MockTensor(torch_ns.float4_e2m1fn)),
        ("lm_head.weight", _MockTensor(torch_ns.float32)),
    ])
    assert fn(sd) == torch_ns.float32
    # Also with bfloat16 fallback
    sd2 = collections.OrderedDict([
        ("w1", _MockTensor(torch_ns.float4_e2m1fn)),
        ("w2", _MockTensor(torch_ns.bfloat16)),
    ])
    assert fn(sd2) == torch_ns.bfloat16


# [pr_diff] fail_to_pass
def test_multiple_quantized_before_standard():
    """Multiple float8/float4 tensors before the first standard float are all skipped."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict([
        ("layer0.w", _MockTensor(torch_ns.float8_e4m3fn)),
        ("layer1.w", _MockTensor(torch_ns.float4_e2m1fn)),
        ("layer2.w", _MockTensor(torch_ns.float8_e5m2)),
        ("final.w", _MockTensor(torch_ns.bfloat16)),
    ])
    assert fn(sd) == torch_ns.bfloat16
    # Same pattern but with float16 at the end
    sd2 = collections.OrderedDict([
        ("a", _MockTensor(torch_ns.float8_e5m2)),
        ("b", _MockTensor(torch_ns.float4_e2m1fn)),
        ("c", _MockTensor(torch_ns.float16)),
    ])
    assert fn(sd2) == torch_ns.float16


# [pr_diff] fail_to_pass
def test_quantized_after_int_tensors():
    """Int tensors followed by float8 then standard float: skips both non-standard."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict([
        ("indices", _MockTensor(torch_ns.int64)),
        ("quant_w", _MockTensor(torch_ns.float8_e4m3fn)),
        ("norm_w", _MockTensor(torch_ns.float16)),
    ])
    assert fn(sd) == torch_ns.float16
    # int32 + float4 + bfloat16
    sd2 = collections.OrderedDict([
        ("ids", _MockTensor(torch_ns.int32)),
        ("w", _MockTensor(torch_ns.float4_e2m1fn)),
        ("b", _MockTensor(torch_ns.bfloat16)),
    ])
    assert fn(sd2) == torch_ns.bfloat16


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: standard dtypes still returned
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_standard_dtypes_returned():
    """float32, float16, bfloat16, float64 as first tensor are returned directly."""
    fn, torch_ns = _load_get_state_dict_dtype()
    for dtype_name in ("float32", "float16", "bfloat16", "float64"):
        dtype = getattr(torch_ns, dtype_name)
        sd = collections.OrderedDict([("w", _MockTensor(dtype))])
        assert fn(sd) == dtype, f"Expected {dtype}, got {fn(sd)}"


# [pr_diff] pass_to_pass
def test_empty_state_dict():
    """Empty state dict returns float32 (both base and fix)."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict()
    assert fn(sd) == torch_ns.float32


# [pr_diff] pass_to_pass
def test_standard_float_before_quantized():
    """When standard float comes first, it is returned immediately (quantized after ignored)."""
    fn, torch_ns = _load_get_state_dict_dtype()
    sd = collections.OrderedDict([
        ("w1", _MockTensor(torch_ns.float32)),
        ("w2", _MockTensor(torch_ns.float8_e4m3fn)),
    ])
    assert fn(sd) == torch_ns.float32
    sd2 = collections.OrderedDict([
        ("w1", _MockTensor(torch_ns.bfloat16)),
        ("w2", _MockTensor(torch_ns.float4_e2m1fn)),
    ])
    assert fn(sd2) == torch_ns.bfloat16
