"""
Task: transformers-dtype-guess-state-dict
Repo: huggingface/transformers @ 7cd9b985e0698d4f625a18be0125231b6b930390
PR:   44883

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import collections
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"
TARGET = f"{REPO}/src/transformers/modeling_utils.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Preamble for subprocess tests: sets up mock torch objects and extracts
# get_state_dict_dtype from the actual source file. Torch is not installed
# in the test container, so we mock just enough to exercise the real function.
_SUBPROCESS_PREAMBLE = r'''
import ast, collections
from pathlib import Path

class _MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        return isinstance(other, _MockDtype) and self.name == other.name
    def __hash__(self):
        return hash(self.name)

class _MockTensor:
    def __init__(self, dtype):
        self.dtype = dtype
    def is_floating_point(self):
        name = self.dtype.name.lower()
        return "float" in name or "f16" in name or "bf16" in name

_NAMES = [
    "float32", "float16", "bfloat16", "float64",
    "float8_e4m3fn", "float8_e5m2", "float4_e2m1fn",
    "int8", "int32", "int64",
]

source = Path("src/transformers/modeling_utils.py").read_text()
tree = ast.parse(source)
fn = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_state_dict_dtype":
        lines = source.splitlines()
        func_src = "\n".join(lines[node.lineno - 1 : node.end_lineno])
        attrs = {n: _MockDtype(n) for n in _NAMES}
        torch_ns = type("torch", (), attrs)()
        ns = {"torch": torch_ns, "__builtins__": __builtins__}
        exec(compile(func_src, "<fn>", "exec"), ns)
        fn = ns["get_state_dict_dtype"]
        T = _MockTensor
        break
if fn is None:
    raise RuntimeError("get_state_dict_dtype not found in modeling_utils.py")
'''


def _run_dtype_test(test_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a test of get_state_dict_dtype in a subprocess with mock torch."""
    script = Path(REPO) / "_eval_dtype_test.py"
    script.write_text(_SUBPROCESS_PREAMBLE + "\n" + test_code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# In-process helpers for pass_to_pass tests

class _MockDtype:
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return f"torch.{self.name}"
    def __eq__(self, other):
        return isinstance(other, _MockDtype) and self.name == other.name
    def __hash__(self):
        return hash(self.name)

class _MockTensor:
    def __init__(self, dtype):
        self.dtype = dtype
    def is_floating_point(self):
        name = self.dtype.name.lower()
        return "float" in name or "f16" in name or "bf16" in name

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
# Pass-to-pass (repo_tests) — CI-style checks using real repo commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/transformers/modeling_utils.py"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_float8_e4m3fn_skipped():
    """float8_e4m3fn should be skipped, returning next standard dtype."""
    r = _run_dtype_test('''
sd = collections.OrderedDict([
    ("quant_w", T(torch_ns.float8_e4m3fn)),
    ("norm_w", T(torch_ns.float16)),
])
result = fn(sd)
assert result == torch_ns.float16, f"Expected float16, got {result}"

sd2 = collections.OrderedDict([
    ("a", T(torch_ns.float8_e4m3fn)),
    ("b", T(torch_ns.float32)),
])
result2 = fn(sd2)
assert result2 == torch_ns.float32, f"Expected float32, got {result2}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_float8_e5m2_skipped():
    """float8_e5m2 should be skipped, returning next standard dtype."""
    r = _run_dtype_test('''
sd = collections.OrderedDict([
    ("layer.attn", T(torch_ns.float8_e5m2)),
    ("layer.norm", T(torch_ns.bfloat16)),
])
result = fn(sd)
assert result == torch_ns.bfloat16, f"Expected bfloat16, got {result}"

sd2 = collections.OrderedDict([
    ("x", T(torch_ns.float8_e5m2)),
    ("y", T(torch_ns.float64)),
])
result2 = fn(sd2)
assert result2 == torch_ns.float64, f"Expected float64, got {result2}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_float4_e2m1fn_skipped():
    """float4_e2m1fn should be skipped, returning next standard dtype."""
    r = _run_dtype_test('''
sd = collections.OrderedDict([
    ("embed.weight", T(torch_ns.float4_e2m1fn)),
    ("lm_head.weight", T(torch_ns.float32)),
])
result = fn(sd)
assert result == torch_ns.float32, f"Expected float32, got {result}"

sd2 = collections.OrderedDict([
    ("w1", T(torch_ns.float4_e2m1fn)),
    ("w2", T(torch_ns.bfloat16)),
])
result2 = fn(sd2)
assert result2 == torch_ns.bfloat16, f"Expected bfloat16, got {result2}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_multiple_quantized_before_standard():
    """Multiple float8/float4 tensors before the first standard float are all skipped."""
    r = _run_dtype_test('''
sd = collections.OrderedDict([
    ("layer0.w", T(torch_ns.float8_e4m3fn)),
    ("layer1.w", T(torch_ns.float4_e2m1fn)),
    ("layer2.w", T(torch_ns.float8_e5m2)),
    ("final.w", T(torch_ns.bfloat16)),
])
result = fn(sd)
assert result == torch_ns.bfloat16, f"Expected bfloat16, got {result}"

sd2 = collections.OrderedDict([
    ("a", T(torch_ns.float8_e5m2)),
    ("b", T(torch_ns.float4_e2m1fn)),
    ("c", T(torch_ns.float16)),
])
result2 = fn(sd2)
assert result2 == torch_ns.float16, f"Expected float16, got {result2}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_quantized_after_int_tensors():
    """Int tensors followed by float8 then standard float: skips both non-standard."""
    r = _run_dtype_test('''
sd = collections.OrderedDict([
    ("indices", T(torch_ns.int64)),
    ("quant_w", T(torch_ns.float8_e4m3fn)),
    ("norm_w", T(torch_ns.float16)),
])
result = fn(sd)
assert result == torch_ns.float16, f"Expected float16, got {result}"

sd2 = collections.OrderedDict([
    ("ids", T(torch_ns.int32)),
    ("w", T(torch_ns.float4_e2m1fn)),
    ("b", T(torch_ns.bfloat16)),
])
result2 = fn(sd2)
assert result2 == torch_ns.bfloat16, f"Expected bfloat16, got {result2}"
print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


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
