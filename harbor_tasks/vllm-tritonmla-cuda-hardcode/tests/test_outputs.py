"""
Task: vllm-tritonmla-cuda-hardcode
Repo: vllm @ 731055548262317579c35189a46cde6932fcc376
PR:   39088

Remove CUDA-hardcoded calls so TritonMLA and MoE work on non-CUDA platforms (XPU).
Tests are AST/source-based — GPU kernels cannot be imported or executed on CPU.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/vllm"

TRITON_MLA = f"{REPO}/vllm/v1/attention/backends/mla/triton_mla.py"
MOE_METHOD = f"{REPO}/vllm/model_executor/layers/fused_moe/unquantized_fused_moe_method.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_triton_mla_valid_python():
    """triton_mla.py must be valid Python syntax."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TRITON_MLA}').read())"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"triton_mla.py has syntax errors:\n{r.stderr.decode()}"


# [static] pass_to_pass
def test_unquantized_moe_valid_python():
    """unquantized_fused_moe_method.py must be valid Python syntax."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{MOE_METHOD}').read())"],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"unquantized_fused_moe_method.py has syntax errors:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_triton_mla_no_cuda_get_device_properties():
    """triton_mla.py must not call torch.cuda.get_device_properties (CUDA hardcode)."""
    src = Path(TRITON_MLA).read_text()
    tree = ast.parse(src)

    # Walk AST looking for attribute chains like torch.cuda.get_device_properties
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # Match: *.get_device_properties(...)
            if isinstance(func, ast.Attribute) and func.attr == "get_device_properties":
                # Check if it's on torch.cuda
                val = func.value
                if isinstance(val, ast.Attribute) and val.attr == "cuda":
                    if isinstance(val.value, ast.Name) and val.value.id == "torch":
                        raise AssertionError(
                            "triton_mla.py still calls torch.cuda.get_device_properties() — "
                            "replace with platform-agnostic current_platform.num_compute_units()"
                        )


# [pr_diff] fail_to_pass
def test_triton_mla_uses_platform_compute_units():
    """triton_mla.py must use num_compute_units() for compute unit count."""
    src = Path(TRITON_MLA).read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            # Match: *.num_compute_units(...)
            if isinstance(func, ast.Attribute) and func.attr == "num_compute_units":
                found = True
                break

    assert found, (
        "triton_mla.py does not call num_compute_units() — "
        "use current_platform.num_compute_units() instead of CUDA-specific API"
    )


# [pr_diff] fail_to_pass
def test_triton_mla_imports_current_platform():
    """triton_mla.py must import current_platform from vllm.platforms."""
    src = Path(TRITON_MLA).read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Match: from vllm.platforms import current_platform
            # or: from vllm.platforms import ..., current_platform, ...
            if node.module and "vllm.platforms" in node.module:
                for alias in node.names:
                    if alias.name == "current_platform":
                        found = True
                        break
        if found:
            break

    assert found, (
        "triton_mla.py does not import current_platform from vllm.platforms — "
        "needed for platform-agnostic num_compute_units()"
    )


# [pr_diff] fail_to_pass
def test_moe_xpu_condition_uses_backend_enum():
    """XPU branch in process_weights_after_loading must use backend enum, not platform check."""
    src = Path(MOE_METHOD).read_text()
    tree = ast.parse(src)

    # Find the process_weights_after_loading method
    method = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "process_weights_after_loading":
            method = node
            break

    assert method is not None, "process_weights_after_loading method not found"

    # Check that the method does NOT use current_platform.is_xpu()
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "is_xpu":
                raise AssertionError(
                    "process_weights_after_loading still uses current_platform.is_xpu() — "
                    "use self.unquantized_backend == UnquantizedMoeBackend.XPU instead"
                )

    # Check that the method DOES reference UnquantizedMoeBackend.XPU
    has_xpu_enum = False
    for node in ast.walk(method):
        if isinstance(node, ast.Attribute) and node.attr == "XPU":
            if isinstance(node.value, ast.Name) and node.value.id == "UnquantizedMoeBackend":
                has_xpu_enum = True
                break
            # Also handle: self.unquantized_backend == X where X has .XPU
            if isinstance(node.value, ast.Attribute) and node.value.attr == "UnquantizedMoeBackend":
                has_xpu_enum = True
                break

    assert has_xpu_enum, (
        "process_weights_after_loading does not use UnquantizedMoeBackend.XPU — "
        "XPU branch must check the backend enum, not platform detection"
    )
