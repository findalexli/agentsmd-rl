"""
Task: vllm-gemma-rms-norm-dtype-cast
Repo: vllm-project/vllm @ 156405d243924fbede2d4360494a81dea7203334
PR:   #38998

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

import torch

REPO = "/workspace/vllm"

LAYERNORM_IR = f"{REPO}/vllm/ir/ops/layernorm.py"
LAYERNORM_MODEL = f"{REPO}/vllm/model_executor/layers/layernorm.py"
VLLM_C = f"{REPO}/vllm/kernels/vllm_c.py"


def _extract_function(filepath: str, func_name: str):
    """Extract a top-level function from source (skipping decorators) and return callable."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            lines = source.splitlines()
            func_lines = lines[node.lineno - 1 : node.end_lineno]
            func_source = textwrap.dedent("\n".join(func_lines))
            namespace = {"torch": torch, "Tensor": torch.Tensor}
            exec(func_source, namespace)
            return namespace[func_name]
    raise AssertionError(f"Function {func_name} not found in {filepath}")


def _extract_class_method(filepath: str, class_name: str, method_name: str):
    """Extract a method from a class (skipping decorators) and return callable."""
    source = Path(filepath).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == method_name:
                    lines = source.splitlines()
                    method_lines = lines[item.lineno - 1 : item.end_lineno]
                    method_source = textwrap.dedent("\n".join(method_lines))
                    namespace = {"torch": torch, "Tensor": torch.Tensor}
                    exec(method_source, namespace)
                    return namespace[method_name]
    raise AssertionError(f"Method {class_name}.{method_name} not found in {filepath}")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    files = [
        LAYERNORM_IR,
        LAYERNORM_MODEL,
        VLLM_C,
        f"{REPO}/vllm/kernels/aiter_ops.py",
        f"{REPO}/vllm/kernels/xpu_ops.py",
    ]
    for path in files:
        source = Path(path).read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {path}: {e}") from e


# [repo_tests] pass_to_pass - CI lint check
def test_ruff_lint():
    """Ruff linter passes on modified files (pass_to_pass)."""
    files = [
        LAYERNORM_IR,
        LAYERNORM_MODEL,
        VLLM_C,
        f"{REPO}/vllm/kernels/aiter_ops.py",
        f"{REPO}/vllm/kernels/xpu_ops.py",
    ]
    r = subprocess.run(
        ["ruff", "check"] + files,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass - Module import check
def test_modified_modules_import():
    """Modified modules can be imported without errors (pass_to_pass)."""
    # Set up minimal path for imports
    sys.path.insert(0, REPO)

    # Test importing the modified modules
    try:
        # These modules have minimal dependencies
        from vllm.ir.ops import layernorm as ir_layernorm
        from vllm.kernels import vllm_c
        from vllm.kernels import aiter_ops
        from vllm.kernels import xpu_ops

        # Verify key functions/classes are accessible
        assert hasattr(ir_layernorm, "rms_norm"), "rms_norm not found in ir.ops.layernorm"
        assert hasattr(vllm_c, "rms_no_var_size"), "rms_no_var_size not found in vllm_c"
    except Exception as e:
        raise AssertionError(f"Failed to import modified modules: {e}") from e


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rms_norm_output_dtype_with_mismatched_weight():
    """rms_norm must cast x to orig_dtype before weight multiply (x.to(orig_dtype) * w pattern)."""
    rms_norm = _extract_function(LAYERNORM_IR, "rms_norm")

    # Test with multiple dtype combinations to avoid hardcoded-constant gaming
    for shape in [(2, 8), (4, 16), (1, 32)]:
        x = torch.randn(*shape, dtype=torch.float16)
        weight = torch.randn(shape[-1], dtype=torch.float32)
        result = rms_norm(x, weight, 1e-6)

        # Fixed version: x.to(orig_dtype=float16) then x * weight => float16 * float32 = float32
        # Base version: x.to(weight.dtype=float32) * weight then .to(orig_dtype) => float16
        assert result.dtype != torch.float16, (
            f"rms_norm casts result to orig_dtype after weight multiply; "
            f"should cast x to orig_dtype before multiply (got {result.dtype} for shape {shape})"
        )


# [pr_diff] fail_to_pass
def test_dispatch_accepts_mismatched_weight_dtype():
    """vllm_c dispatch predicate must not reject weight with different dtype than x."""
    source = Path(VLLM_C).read_text()
    lines = source.splitlines()

    # Find the rms_no_var_size lambda definition
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("rms_no_var_size") and "lambda" in stripped:
            start = i
            break
    assert start is not None, "rms_no_var_size lambda not found in vllm_c.py"

    # Collect lines until statement is syntactically complete
    defn_lines = []
    for i in range(start, min(start + 10, len(lines))):
        defn_lines.append(lines[i])
        text = "\n".join(defn_lines)
        if text.count("(") <= text.count(")"):
            break

    namespace = {"torch": torch}
    exec("\n".join(defn_lines), namespace)
    pred = namespace["rms_no_var_size"]

    # Test with mismatched dtypes — should be accepted
    for x_dtype, w_dtype in [
        (torch.float16, torch.float32),
        (torch.bfloat16, torch.float32),
        (torch.float16, torch.bfloat16),
    ]:
        x = torch.randn(2, 4, dtype=x_dtype)
        w = torch.randn(4, dtype=w_dtype)
        assert pred(x, w, 1e-6), (
            f"Dispatch predicate rejects x.dtype={x_dtype}, weight.dtype={w_dtype}; "
            f"should only check variance_size"
        )


# [pr_diff] fail_to_pass
def test_gemma_static_no_residual():
    """GemmaRMSNorm must have _forward_static_no_residual with correct Gemma normalization."""
    fn = _extract_class_method(
        LAYERNORM_MODEL, "GemmaRMSNorm", "_forward_static_no_residual"
    )

    # Test with multiple shapes and weight values
    for hidden in (8, 16, 32):
        weight = torch.randn(hidden)
        x = torch.randn(2, hidden, dtype=torch.float16)
        result = fn(weight, 1e-6, x)

        assert result.dtype == torch.float16, f"Expected float16 output, got {result.dtype}"
        assert result.shape == x.shape, f"Expected shape {x.shape}, got {result.shape}"

        # Verify Gemma-style normalization: (x / sqrt(var+eps) * (1+w)).to(orig_dtype)
        xf = x.float()
        var = xf.pow(2).mean(dim=-1, keepdim=True)
        expected = (xf * torch.rsqrt(var + 1e-6) * (1.0 + weight.float())).to(
            torch.float16
        )
        assert torch.allclose(result, expected, atol=1e-3), (
            f"Numerical mismatch for hidden={hidden}: "
            f"max diff={torch.max(torch.abs(result - expected))}"
        )


# [pr_diff] fail_to_pass
def test_gemma_static_with_residual():
    """GemmaRMSNorm must have _forward_static_with_residual handling residual correctly."""
    fn = _extract_class_method(
        LAYERNORM_MODEL, "GemmaRMSNorm", "_forward_static_with_residual"
    )

    for hidden in (8, 16):
        weight = torch.randn(hidden)
        x = torch.randn(2, hidden, dtype=torch.float16)
        residual = torch.randn(2, hidden, dtype=torch.float16)
        result, res_out = fn(weight, 1e-6, x, residual)

        assert result.dtype == torch.float16, f"Expected float16 output, got {result.dtype}"
        assert isinstance(res_out, torch.Tensor), "Should return residual tensor"

        # Verify: for float16 input, x and residual are combined in float32
        combined = x.float() + residual.float()
        var = combined.pow(2).mean(dim=-1, keepdim=True)
        expected = (
            combined * torch.rsqrt(var + 1e-6) * (1.0 + weight.float())
        ).to(torch.float16)
        assert torch.allclose(result, expected, atol=1e-3), (
            f"Numerical mismatch for hidden={hidden}"
        )

        # Verify residual output is the combined tensor
        expected_res = x.float() + residual.float()
        assert torch.allclose(res_out.float(), expected_res, atol=1e-3), (
            "Residual output should be x + residual (combined)"
        )


# [pr_diff] fail_to_pass
def test_gemma_forward_native_no_ir_ops():
    """GemmaRMSNorm.forward_native must not delegate to ir.ops.rms_norm."""
    source = Path(LAYERNORM_MODEL).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GemmaRMSNorm":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "forward_native":
                    method_src = ast.get_source_segment(source, item)
                    if method_src is None:
                        lines = source.splitlines()
                        method_src = "\n".join(
                            lines[item.lineno - 1 : item.end_lineno]
                        )
                    assert "ir.ops.rms_norm" not in method_src, (
                        "forward_native still delegates to ir.ops.rms_norm; "
                        "GemmaRMSNorm needs its own dedicated implementation"
                    )
                    return
    raise AssertionError("GemmaRMSNorm.forward_native not found")


# [pr_diff] fail_to_pass
def test_gemma_forward_cuda_uses_compile():
    """GemmaRMSNorm.forward_cuda must use torch.compile for its static methods."""
    source = Path(LAYERNORM_MODEL).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "GemmaRMSNorm":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "forward_cuda":
                    method_src = ast.get_source_segment(source, item)
                    if method_src is None:
                        lines = source.splitlines()
                        method_src = "\n".join(
                            lines[item.lineno - 1 : item.end_lineno]
                        )
                    assert "torch.compile" in method_src, (
                        "forward_cuda does not use torch.compile; "
                        "GemmaRMSNorm should compile its static forward methods"
                    )
                    return
    raise AssertionError("GemmaRMSNorm.forward_cuda not found")


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_rms_norm_same_dtype_correctness():
    """rms_norm with matching weight dtype still produces correct normalized output."""
    rms_norm = _extract_function(LAYERNORM_IR, "rms_norm")

    for dtype in (torch.float32, torch.float16):
        x = torch.tensor([[1.0, 2.0, 3.0, 4.0]], dtype=dtype)
        weight = torch.ones(4, dtype=dtype)
        result = rms_norm(x, weight, 1e-6)

        # Manual computation
        xf = x.float()
        var = xf.pow(2).mean(dim=-1, keepdim=True)
        expected = (xf * torch.rsqrt(var + 1e-6)).to(dtype) * weight

        assert torch.allclose(result.to(dtype), expected, atol=1e-3), (
            f"rms_norm incorrect for dtype={dtype}: got {result}, expected {expected}"
        )

    # Also verify no-weight case returns orig_dtype
    x_fp16 = torch.randn(2, 8, dtype=torch.float16)
    result_no_weight = rms_norm(x_fp16, None, 1e-6)
    assert result_no_weight.dtype == torch.float16, (
        f"rms_norm without weight should return orig_dtype, got {result_no_weight.dtype}"
    )
