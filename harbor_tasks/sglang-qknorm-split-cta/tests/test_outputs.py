"""
Task: sglang-qknorm-split-cta
Repo: sgl-project/sglang @ 8a56a7b04d553ecb76fca04eb89bbc20772e2051
PR:   21503

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

All tests use regex/text analysis because the target is a CUDA C++ kernel header
(.cuh) — no GPU or CUDA compiler is available in the test environment.
"""

import re
from pathlib import Path

REPO = "/workspace/sglang"
TARGET = Path(REPO) / "python/sglang/jit_kernel/csrc/elementwise/qknorm_across_heads.cuh"


def _strip_comments(src: str) -> str:
    """Remove C/C++ block and line comments."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


def _read_stripped() -> str:
    """Read the target file with comments stripped."""
    assert TARGET.exists(), f"{TARGET} does not exist"
    return _strip_comments(TARGET.read_text())


def _read_raw() -> str:
    """Read the target file with comments intact."""
    assert TARGET.exists(), f"{TARGET} does not exist"
    return TARGET.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Target file must be substantial (>= 80 non-empty lines), not a stub."""
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    nonempty = sum(1 for line in src.splitlines() if line.strip())
    assert nonempty >= 80, f"Only {nonempty} non-empty lines -- expected >= 80 for a real kernel"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_blockidx_y_dispatch():
    """Kernel must use blockIdx.y to dispatch between Q and K processing.

    The base code processes both Q and K in a single CTA with no blockIdx.y usage.
    After the fix, blockIdx.y selects which tensor (Q or K) each block handles.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    bidy_refs = re.findall(r"blockIdx\s*\.\s*y", src)
    assert len(bidy_refs) >= 1, "blockIdx.y not found in kernel code"
    # Must be used in a conditional or assignment, not just mentioned
    bidy_in_context = re.findall(r"(if|switch|=|==|\?)\s*.*blockIdx\s*\.\s*y", src)
    assert len(bidy_in_context) >= 1, (
        f"blockIdx.y found {len(bidy_refs)} time(s) but not in a conditional or assignment"
    )


# [pr_diff] fail_to_pass
def test_shared_memory_halved():
    """Shared memory must be reduced from 64 to <= 32.

    Base code: __shared__ float shared_memory[64] (32 for Q + 32 for K).
    After fix: only one buffer needed since each CTA handles one tensor.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    matches = re.findall(
        r"__shared__\s+float\s+\w+\s*\[\s*(\d+)\s*\]", src
    )
    assert len(matches) >= 1, "No __shared__ float array found"
    sizes = [int(m) for m in matches]
    assert all(s <= 32 for s in sizes), (
        f"Shared memory buffer size(s) {sizes} -- expected all <= 32 (base uses 64)"
    )


# [pr_diff] fail_to_pass
def test_register_vectors_unified():
    """Dual Q/K register vectors must be replaced with unified generic vectors.

    Base code declares 6 vec_t variables: v_q, v_k, v_q_weight, v_k_weight, v_q_out, v_k_out.
    After fix, each CTA handles only one tensor, so <= 3 vec_t vars needed.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    decls = re.findall(r"\bvec_t\s+(\w+)\s*;", src)
    assert len(decls) <= 3, (
        f"{len(decls)} vec_t declarations ({', '.join(decls)}) -- expected <= 3 (base has 6)"
    )
    # Also verify the old dual names are gone
    for old_name in ("v_q", "v_k", "v_q_weight", "v_k_weight", "v_q_out", "v_k_out"):
        assert old_name not in decls, f"Old dual variable '{old_name}' still declared"


# [pr_diff] fail_to_pass
def test_2d_grid_launch():
    """LaunchKernel must use a 2D grid (dim3 with y=2) instead of 1D.

    Base code: LaunchKernel(static_cast<uint>(N.unwrap()), threads, device.unwrap())
    After fix: dim3(N, 2) -- second dimension dispatches Q vs K blocks.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    has_dim3_2 = re.search(r"dim3\s*[\({]\s*[^,]+,\s*2\s*[\)}]", src)
    assert has_dim3_2, "No 2D grid launch (dim3 with y=2) found"


# [pr_diff] fail_to_pass
def test_rms_const_params():
    """rms() helper parameters must be const-qualified (read-only).

    Base code: rms(packed_t& val, packed_t& weight, float rsqrt_square_sum)
    After fix: rms(const packed_t& val, const packed_t& weight, ...)
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    match = re.search(r"\brms\s*\(([^)]+)\)", src)
    assert match, "rms() function signature not found"
    params = [p.strip() for p in match.group(1).split(",")]
    const_count = sum(1 for p in params if "const" in p)
    assert const_count >= 2, (
        f"Only {const_count} const-qualified param(s) in rms() -- expected >= 2"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_rms_helper_exists():
    """rms() helper function must still exist with a real body (not removed)."""
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    assert re.search(r"\brms\s*\(", src), "rms() function not found"
    assert re.search(r"\brms\s*\([^)]*\)\s*\{[^}]+\}", src, re.DOTALL), (
        "rms() function has no body"
    )


# [pr_diff] pass_to_pass
def test_launcher_struct_exists():
    """QKNormAcrossHeadsKernel struct with run() method must still exist."""
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    assert re.search(r"struct\s+QKNormAcrossHeadsKernel", src), (
        "QKNormAcrossHeadsKernel struct not found"
    )
    assert re.search(r"\bvoid\s+run\s*\(", src), (
        "run() method not found in launcher struct"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from .claude/skills/add-jit-kernel/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- .claude/skills/add-jit-kernel/SKILL.md:51 @ 8a56a7b0
def test_sgl_device_macro():
    """Device helper functions must use SGL_DEVICE macro (not raw __device__).

    SKILL.md line 51: "SGL_DEVICE -- Expands to __forceinline__ __device__. Use on all device functions."
    The rms() helper is a device function and must retain SGL_DEVICE.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_raw()
    # Find the rms function definition (template line + SGL_DEVICE line)
    rms_match = re.search(r"SGL_DEVICE\s+\w+\s+rms\s*\(", src)
    assert rms_match, "rms() function must use SGL_DEVICE macro"


# [agent_config] pass_to_pass -- .claude/skills/add-jit-kernel/SKILL.md:300 @ 8a56a7b0
def test_uses_launch_kernel():
    """Kernel must be launched via LaunchKernel helper, not raw <<<>>> syntax.

    SKILL.md line 300: "Use LaunchKernel -- it resolves the stream and checks errors automatically."
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    assert re.search(r"\bLaunchKernel\b", src), "LaunchKernel not found -- must use it for kernel launches"
    # Ensure no raw CUDA <<<>>> launch syntax
    assert not re.search(r"<<<.*>>>", src), "Raw <<<>>> kernel launch found -- use LaunchKernel instead"


# [agent_config] pass_to_pass -- .claude/skills/add-jit-kernel/SKILL.md:304 @ 8a56a7b0
def test_device_cast_used():
    """Type conversions must use device::cast, not raw C-style casts in kernel code.

    SKILL.md line 304: "device::cast<To, From> or dtype_trait<T>::from(val) for cross-type conversions."
    The kernel converts between packed_t and fp32x2_t -- must use device::cast.
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    # The kernel body (inside qknorm_across_heads_reg_kernel) must use device::cast
    kernel_match = re.search(
        r"__global__\s+void\s+qknorm_across_heads_reg_kernel.*?\{(.+?)^struct",
        src, re.DOTALL | re.MULTILINE,
    )
    assert kernel_match, "Kernel function body not found"
    kernel_body = kernel_match.group(1)
    casts = re.findall(r"device::cast\s*<", kernel_body)
    assert len(casts) >= 1, "No device::cast<> found in kernel body -- must use project cast abstractions"


# [agent_config] pass_to_pass -- .claude/skills/add-jit-kernel/SKILL.md:156 @ 8a56a7b0
def test_syncthreads_after_smem_write():
    """__syncthreads() must be called after writing to shared memory before reading it.

    SKILL.md line 156: "Caller is responsible for a __syncthreads() after if the result
    in smem[0] is needed."
    """
    # AST-only because: CUDA C++ kernel, no GPU/compiler in test env
    src = _read_stripped()
    # After shared memory buffer write, must have __syncthreads before reading
    assert re.search(r"__syncthreads\s*\(\s*\)", src), (
        "No __syncthreads() found -- required after shared memory write before read"
    )
    # Should have at least 2 sync points (after warp reduce write, after CTA reduce)
    syncs = re.findall(r"__syncthreads\s*\(\s*\)", src)
    assert len(syncs) >= 2, (
        f"Only {len(syncs)} __syncthreads() call(s) -- expected >= 2 for shared memory coordination"
    )
