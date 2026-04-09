"""
Task: vllm-cuda13-swap-blocks-compile
Repo: vllm @ 81994e1d0ea6e0486cfbdad02e00942614c55264
PR:   38915

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is CUDA C++ code that cannot be compiled/run without a GPU.
Tests use source-level analysis (explicit exception for GPU kernels).
"""

import re
from pathlib import Path

REPO = "/workspace/vllm"
CACHE_KERNELS = Path(REPO) / "csrc" / "cache_kernels.cu"


def _read_source():
    return CACHE_KERNELS.read_text()


def _extract_swap_blocks_batch(content):
    """Extract the swap_blocks_batch function body from the source."""
    start = content.find("void swap_blocks_batch(")
    assert start != -1, "swap_blocks_batch function not found in cache_kernels.cu"
    # Extract a generous chunk — function is ~60 lines
    return content[start:start + 4000]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_swap_blocks_batch_exists():
    """swap_blocks_batch function must still be defined."""
    content = _read_source()
    assert re.search(r'void\s+swap_blocks_batch\s*\(', content), \
        "swap_blocks_batch function definition not found in cache_kernels.cu"


# [static] pass_to_pass
def test_memcpy_batch_async_still_used():
    """cuMemcpyBatchAsync must still be called within swap_blocks_batch."""
    content = _read_source()
    func_body = _extract_swap_blocks_batch(content)
    assert 'cuMemcpyBatchAsync' in func_body, \
        "cuMemcpyBatchAsync should still be called in swap_blocks_batch"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cuda13_version_conditional():
    """swap_blocks_batch must have a CUDA 13 version guard to handle the
    changed cuMemcpyBatchAsync API signature in CUDA 13."""
    content = _read_source()
    func_body = _extract_swap_blocks_batch(content)
    # Accept either CUDA_VERSION >= 13000 or __CUDACC_VER_MAJOR__ >= 13
    has_guard = bool(re.search(r'CUDA_VERSION\s*>=\s*13000', func_body)) or \
                bool(re.search(r'__CUDACC_VER_MAJOR__\s*>=\s*13', func_body))
    assert has_guard, \
        "Missing CUDA 13 version conditional in swap_blocks_batch — " \
        "cuMemcpyBatchAsync changed signature in CUDA 13"


# [pr_diff] fail_to_pass
def test_dual_memcpy_batch_paths():
    """swap_blocks_batch needs two separate cuMemcpyBatchAsync call sites
    to handle both CUDA 13+ (8-arg) and older CUDA (9-arg) API signatures."""
    content = _read_source()
    func_body = _extract_swap_blocks_batch(content)
    calls = re.findall(r'cuMemcpyBatchAsync\s*\(', func_body)
    assert len(calls) >= 2, \
        f"Expected >=2 cuMemcpyBatchAsync calls for CUDA version branching, " \
        f"found {len(calls)}"


# [pr_diff] fail_to_pass
def test_cuda13_branch_no_fail_idx():
    """The CUDA 13+ code path must NOT pass fail_idx to cuMemcpyBatchAsync,
    as CUDA 13 removed that parameter from the API."""
    content = _read_source()
    func_body = _extract_swap_blocks_batch(content)
    # Find the CUDA 13+ conditional block — look for the guard and extract
    # content up to the next #else or #endif
    match = re.search(
        r'(?:CUDA_VERSION\s*>=\s*13000|__CUDACC_VER_MAJOR__\s*>=\s*13)'
        r'(.*?)#\s*(?:else|endif)',
        func_body, re.DOTALL
    )
    assert match, "CUDA 13+ conditional block not found in swap_blocks_batch"
    cuda13_block = match.group(1)
    assert 'cuMemcpyBatchAsync' in cuda13_block, \
        "cuMemcpyBatchAsync not called in the CUDA 13+ branch"
    assert 'fail_idx' not in cuda13_block, \
        "CUDA 13+ branch must not reference fail_idx — " \
        "this parameter was removed from cuMemcpyBatchAsync in CUDA 13"
