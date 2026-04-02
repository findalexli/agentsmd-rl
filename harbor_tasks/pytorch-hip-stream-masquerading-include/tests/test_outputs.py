"""
Task: pytorch-hip-stream-masquerading-include
Repo: pytorch/pytorch @ 4b8a514606230b60bb8f27be5f11612f21b4aec1
PR:   175159

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: These are C++ headers requiring the full PyTorch build toolchain + GPU
hardware to compile. All checks are structural (regex on source) — this is the
only viable approach for CPU-only verification of C++ header changes.
"""

import re
from pathlib import Path

REPO = "/workspace/pytorch"
CUDA_STREAM_H = Path(REPO) / "c10/cuda/CUDAStream.h"
HIP_MASQ_H = Path(REPO) / "aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h"


def _strip_cpp_comments(text: str) -> str:
    """Remove // line comments and /* block comments */ from C++ source."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _extract_rocm_block(text: str) -> str:
    """Extract content between #ifdef USE_ROCM and matching #endif."""
    m = re.search(r"#ifdef\s+USE_ROCM\b(.*?)#endif", text, re.DOTALL)
    return m.group(1) if m else ""


def _is_include_approach(rocm_block: str) -> bool:
    """Detect if fix uses #include of masquerading header."""
    return bool(re.search(r"#include\s*[<\"].*HIPStreamMasqueradingAsCUDA", rocm_block))


def _check_function_accessible(func_name: str, delegate_re: str):
    """
    Verify a masquerading function is declared and delegates to the correct
    underlying c10::cuda function. Supports two approaches:
      A) #include of the masquerading header inside USE_ROCM
      B) Inline wrapper/alias in CUDAStream.h USE_ROCM block
    """
    cuda_h = _strip_cpp_comments(CUDA_STREAM_H.read_text())
    hip_masq = _strip_cpp_comments(HIP_MASQ_H.read_text())
    rocm_block = _extract_rocm_block(cuda_h)

    if _is_include_approach(rocm_block):
        has_decl = bool(re.search(rf"{func_name}\s*[\(=]", hip_masq))
        has_delegate = bool(re.search(delegate_re, hip_masq))
        assert has_decl, f"{func_name} not found in included masquerading header"
        assert has_delegate, f"{func_name} declared but no delegation in included header"
    else:
        has_decl = bool(re.search(rf"{func_name}\s*[\(=]", rocm_block))
        has_delegate = bool(re.search(delegate_re, rocm_block))
        assert has_decl, f"{func_name} not declared in USE_ROCM block of CUDAStream.h"
        assert has_delegate, f"{func_name} declared but no delegation to underlying function"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_files_exist():
    """Both CUDAStream.h and HIPStreamMasqueradingAsCUDA.h must exist."""
    assert CUDA_STREAM_H.is_file(), f"Missing: {CUDA_STREAM_H}"
    assert HIP_MASQ_H.is_file(), f"Missing: {HIP_MASQ_H}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — each masquerading function accessible via public header
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_getCurrentHIPStreamMasqueradingAsCUDA():
    """getCurrentHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h."""
    _check_function_accessible(
        "getCurrentHIPStreamMasqueradingAsCUDA", r"getCurrentCUDAStream"
    )


# [pr_diff] fail_to_pass
def test_getDefaultHIPStreamMasqueradingAsCUDA():
    """getDefaultHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h."""
    _check_function_accessible(
        "getDefaultHIPStreamMasqueradingAsCUDA", r"getDefaultCUDAStream"
    )


# [pr_diff] fail_to_pass
def test_getStreamFromPoolMasqueradingAsCUDA():
    """getStreamFromPoolMasqueradingAsCUDA accessible via CUDAStream.h."""
    _check_function_accessible(
        "getStreamFromPoolMasqueradingAsCUDA", r"getStreamFromPool(?!Masq)"
    )


# [pr_diff] fail_to_pass
def test_getStreamFromExternalMasqueradingAsCUDA():
    """getStreamFromExternalMasqueradingAsCUDA accessible via CUDAStream.h."""
    _check_function_accessible(
        "getStreamFromExternalMasqueradingAsCUDA", r"getStreamFromExternal(?!Masq)"
    )


# [pr_diff] fail_to_pass
def test_setCurrentHIPStreamMasqueradingAsCUDA():
    """setCurrentHIPStreamMasqueradingAsCUDA accessible via CUDAStream.h."""
    _check_function_accessible(
        "setCurrentHIPStreamMasqueradingAsCUDA", r"setCurrentCUDAStream"
    )


# [pr_diff] fail_to_pass
def test_getStreamFromPool_both_overloads():
    """Both overloads of getStreamFromPoolMasqueradingAsCUDA must be accessible (bool and int priority)."""
    cuda_h = _strip_cpp_comments(CUDA_STREAM_H.read_text())
    hip_masq = _strip_cpp_comments(HIP_MASQ_H.read_text())
    rocm_block = _extract_rocm_block(cuda_h)

    source = hip_masq if _is_include_approach(rocm_block) else rocm_block

    has_bool = bool(re.search(r"getStreamFromPoolMasqueradingAsCUDA\s*\([^)]*\bbool\b", source))
    has_int = bool(re.search(r"getStreamFromPoolMasqueradingAsCUDA\s*\([^)]*\bint\b", source))

    assert has_bool, "Missing bool overload of getStreamFromPoolMasqueradingAsCUDA"
    assert has_int, "Missing int priority overload of getStreamFromPoolMasqueradingAsCUDA"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_masquerading_class_preserved():
    """HIPStreamMasqueradingAsCUDA class must still exist in original header."""
    src = HIP_MASQ_H.read_text()
    assert "class HIPStreamMasqueradingAsCUDA" in src, (
        "HIPStreamMasqueradingAsCUDA class removed from original header"
    )


# [pr_diff] pass_to_pass
def test_operator_ostream_preserved():
    """operator<< for HIPStreamMasqueradingAsCUDA preserved in original header."""
    src = HIP_MASQ_H.read_text()
    assert re.search(r"operator\s*<<.*HIPStreamMasqueradingAsCUDA", src), (
        "operator<< for HIPStreamMasqueradingAsCUDA removed"
    )


# [pr_diff] pass_to_pass
def test_nonmasquerading_hip_aliases_preserved():
    """Non-masquerading HIP aliases (getCurrentHIPStream, setCurrentHIPStream) still present."""
    cuda_h = _strip_cpp_comments(CUDA_STREAM_H.read_text())
    assert re.search(r"getCurrentHIPStream(?!Masq)\s*[\(=]", cuda_h), (
        "getCurrentHIPStream alias missing from CUDAStream.h"
    )
    assert re.search(r"setCurrentHIPStream(?!Masq)\s*[\(=]", cuda_h), (
        "setCurrentHIPStream alias missing from CUDAStream.h"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:57 @ 4b8a514606230b60bb8f27be5f11612f21b4aec1
def test_functions_in_hip_namespace():
    """Masquerading functions must be in c10::hip namespace (matching existing pattern)."""
    cuda_h = _strip_cpp_comments(CUDA_STREAM_H.read_text())
    rocm_block = _extract_rocm_block(cuda_h)

    if _is_include_approach(rocm_block):
        return  # include approach inherits namespace from original header

    # Verify c10::hip namespace exists and contains masquerading content
    ns_match = re.search(
        r"namespace\s+c10\s*(?:::\s*hip|[^{]*\{[^}]*namespace\s+hip)",
        cuda_h, re.DOTALL,
    )
    assert ns_match, "c10::hip namespace not found in CUDAStream.h"
    ns_region = cuda_h[ns_match.start() : ns_match.start() + 3000]
    assert "MasqueradingAsCUDA" in ns_region, (
        "Masquerading functions not placed in c10::hip namespace"
    )
