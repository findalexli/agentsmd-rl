"""
Task: pytorch-hip-stream-masquerading-include
Repo: pytorch/pytorch @ 4b8a514606230b60bb8f27be5f11612f21b4aec1
PR:   175159

Behavioral tests: C++ compilation (g++ -fsyntax-only) verifies masquerading
function declarations are syntactically valid and accessible through the
public CUDAStream.h header's USE_ROCM block.
"""

import functools
import re
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/workspace/pytorch"
CUDA_STREAM_H = Path(REPO) / "c10/cuda/CUDAStream.h"
HIP_MASQ_H = Path(REPO) / "aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h"

# Minimal C++ type stubs so the extracted USE_ROCM block compiles standalone
CPP_STUBS = textwrap.dedent("""\
    using DeviceIndex = int;
    using hipStream_t = void*;
    namespace c10 { namespace cuda {
    struct CUDAStream {};
    inline CUDAStream getStreamFromPool(bool, DeviceIndex = -1) { return {}; }
    inline CUDAStream getStreamFromPool(int, DeviceIndex = -1) { return {}; }
    inline CUDAStream getStreamFromExternal(hipStream_t, DeviceIndex) { return {}; }
    inline CUDAStream getDefaultCUDAStream(DeviceIndex = -1) { return {}; }
    inline CUDAStream getCurrentCUDAStream(DeviceIndex = -1) { return {}; }
    inline void setCurrentCUDAStream(CUDAStream) {}
    }} // namespace c10::cuda
""")

# Stub for the masquerading class (only added when not already in the block)
MASQ_CLASS_STUB = textwrap.dedent("""\
    namespace c10 { namespace hip {
    struct HIPStreamMasqueradingAsCUDA : public c10::cuda::CUDAStream {
        HIPStreamMasqueradingAsCUDA() = default;
        HIPStreamMasqueradingAsCUDA(c10::cuda::CUDAStream) {}
        c10::cuda::CUDAStream hip_stream() const { return {}; }
    };
    }} // namespace c10::hip
""")


def _strip_cpp_comments(text: str) -> str:
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _extract_rocm_block(text: str) -> str:
    """Extract the last #ifdef USE_ROCM ... #endif block."""
    matches = re.findall(r"#ifdef\s+USE_ROCM\b(.*?)#endif", text, re.DOTALL)
    return matches[-1] if matches else ""


def _is_include_approach(rocm_block: str) -> bool:
    return bool(re.search(r"#include\s*[<\"].*HIPStreamMasqueradingAsCUDA", rocm_block))


@functools.lru_cache(maxsize=1)
def _get_compilable_block() -> str:
    """Extract USE_ROCM block content, ready for standalone compilation.

    Handles both the inline-wrapper approach and the #include approach.
    """
    cuda_src = CUDA_STREAM_H.read_text()
    block = _extract_rocm_block(cuda_src)

    if _is_include_approach(block):
        # Inline the masquerading header content (strip its own preprocessor guards)
        hip_src = HIP_MASQ_H.read_text()
        hip_clean = re.sub(r"#(?:include|pragma|ifndef|define|endif)[^\n]*", "", hip_src)
        block = re.sub(
            r'#include\s*[<"].*HIPStreamMasqueradingAsCUDA[^">\n]*[">]',
            hip_clean, block,
        )

    # Strip remaining includes that can't be resolved without full build tree
    block = re.sub(r'#include\s*[<"][^">\n]*[">]', "", block)
    return block


def _compile_fn_test(fn_call: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Build a C++ test file calling a masquerading function and compile it."""
    block = _get_compilable_block()

    code = CPP_STUBS
    if "class HIPStreamMasqueradingAsCUDA" not in block:
        code += MASQ_CLASS_STUB
    code += "\n" + block + "\n"
    code += f"int main() {{ {fn_call}; return 0; }}\n"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", dir=REPO, delete=False,
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        return subprocess.run(
            ["g++", "-fsyntax-only", "-std=c++17", tmp_path],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _compile_namespace_test(namespace_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Build a C++ test file checking namespace structure."""
    block = _get_compilable_block()

    code = CPP_STUBS + "\n"
    if "class HIPStreamMasqueradingAsCUDA" not in block:
        code += MASQ_CLASS_STUB + "\n"
    code += block + "\n"
    code += namespace_code

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", dir=REPO, delete=False,
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        return subprocess.run(
            ["g++", "-fsyntax-only", "-std=c++17", tmp_path],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def _compile_removed_functions_test(timeout: int = 30) -> subprocess.CompletedProcess:
    """Compile a test that would fail if masquerading functions are still in HIP header."""
    hip_src = HIP_MASQ_H.read_text()

    # Build code that includes the HIP header and tries to use the functions
    # If they're still there, this will compile (which is the wrong state)
    # If they're removed, the USE_ROCM block in CUDAStream.h provides them instead
    code = textwrap.dedent("""\
        #include \"aten/src/ATen/hip/impl/HIPStreamMasqueradingAsCUDA.h\"
        // The functions should NOT be directly callable from just this header
        // They should only be available via c10/cuda/CUDAStream.h
    """)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", dir=REPO, delete=False,
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        return subprocess.run(
            ["g++", "-fsyntax-only", "-std=c++17", tmp_path],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_source_files_exist():
    """Both CUDAStream.h and HIPStreamMasqueradingAsCUDA.h must exist."""
    assert CUDA_STREAM_H.is_file(), f"Missing: {CUDA_STREAM_H}"
    assert HIP_MASQ_H.is_file(), f"Missing: {HIP_MASQ_H}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass before and after fix
# ---------------------------------------------------------------------------

def test_header_compiles_standalone():
    """Extracted USE_ROCM block compiles without errors (pass_to_pass)."""
    # This tests that the syntax of the modified headers is valid
    # by extracting and compiling just the USE_ROCM block
    block = _get_compilable_block()
    
    code = CPP_STUBS
    if "class HIPStreamMasqueradingAsCUDA" not in block:
        code += MASQ_CLASS_STUB
    code += "\n" + block + "\n"
    code += "int main() { return 0; }\n"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cpp", dir=REPO, delete=False,
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        r = subprocess.run(
            ["g++", "-fsyntax-only", "-std=c++17", tmp_path],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Header syntax error:\n{r.stderr[:500]}"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_aten_hip_header_exists():
    """ATen HIP masquerading header exists and is readable (pass_to_pass)."""
    assert HIP_MASQ_H.is_file(), f"HIP header missing: {HIP_MASQ_H}"
    content = HIP_MASQ_H.read_text()
    assert "HIPStreamMasqueradingAsCUDA" in content, "HIP header missing expected class"


def test_no_trailing_whitespace_in_modified_files():
    """Modified header files have no trailing whitespace (pass_to_pass)."""
    files_to_check = [
        CUDA_STREAM_H,
        HIP_MASQ_H,
    ]
    for filepath in files_to_check:
        if not filepath.exists():
            continue
        content = filepath.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            # Allow empty lines, but not lines with trailing whitespace
            if line != line.rstrip():
                assert False, f"Trailing whitespace in {filepath}:{i}"


def test_header_guards_present():
    """Header files have proper include guards or pragma once (pass_to_pass)."""
    files_to_check = [
        CUDA_STREAM_H,
        HIP_MASQ_H,
    ]
    for filepath in files_to_check:
        if not filepath.exists():
            continue
        content = filepath.read_text()
        # Check for #pragma once or traditional include guards
        has_pragma_once = "#pragma once" in content
        has_ifndef_guard = re.search(r"#ifndef\s+\w+_H", content) is not None
        assert has_pragma_once or has_ifndef_guard, (
            f"{filepath} missing include guard (#pragma once or #ifndef)"
        )


def test_file_ends_with_newline():
    """Source files end with a single newline (pass_to_pass)."""
    files_to_check = [
        CUDA_STREAM_H,
        HIP_MASQ_H,
    ]
    for filepath in files_to_check:
        if not filepath.exists():
            continue
        content = filepath.read_text()
        if not content:
            continue
        # File should end with exactly one newline, not multiple
        if content.endswith("\n\n"):
            assert False, f"{filepath} ends with multiple newlines"
        if not content.endswith("\n"):
            assert False, f"{filepath} does not end with newline"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — C++ compilation verifies declarations accessible
# ---------------------------------------------------------------------------

def test_getCurrentHIPStreamMasqueradingAsCUDA():
    """getCurrentHIPStreamMasqueradingAsCUDA compiles when accessed via CUDAStream.h."""
    r = _compile_fn_test("(void)c10::hip::getCurrentHIPStreamMasqueradingAsCUDA(-1)")
    assert r.returncode == 0, f"Not accessible:\n{r.stderr[:500]}"


def test_getDefaultHIPStreamMasqueradingAsCUDA():
    """getDefaultHIPStreamMasqueradingAsCUDA compiles when accessed via CUDAStream.h."""
    r = _compile_fn_test("(void)c10::hip::getDefaultHIPStreamMasqueradingAsCUDA(-1)")
    assert r.returncode == 0, f"Not accessible:\n{r.stderr[:500]}"


def test_getStreamFromPoolMasqueradingAsCUDA():
    """getStreamFromPoolMasqueradingAsCUDA compiles when accessed via CUDAStream.h."""
    r = _compile_fn_test("(void)c10::hip::getStreamFromPoolMasqueradingAsCUDA(true, -1)")
    assert r.returncode == 0, f"Not accessible:\n{r.stderr[:500]}"


def test_getStreamFromExternalMasqueradingAsCUDA():
    """getStreamFromExternalMasqueradingAsCUDA compiles when accessed via CUDAStream.h."""
    r = _compile_fn_test(
        "(void)c10::hip::getStreamFromExternalMasqueradingAsCUDA(nullptr, 0)"
    )
    assert r.returncode == 0, f"Not accessible:\n{r.stderr[:500]}"


def test_setCurrentHIPStreamMasqueradingAsCUDA():
    """setCurrentHIPStreamMasqueradingAsCUDA compiles when accessed via CUDAStream.h."""
    r = _compile_fn_test(
        "c10::hip::setCurrentHIPStreamMasqueradingAsCUDA(c10::cuda::CUDAStream{})"
    )
    assert r.returncode == 0, f"Not accessible:\n{r.stderr[:500]}"


def test_getStreamFromPool_both_overloads():
    """Both overloads of getStreamFromPoolMasqueradingAsCUDA (bool and int) compile."""
    r = _compile_fn_test(
        "(void)c10::hip::getStreamFromPoolMasqueradingAsCUDA(true, -1), "
        "(void)c10::hip::getStreamFromPoolMasqueradingAsCUDA(1, -1)"
    )
    assert r.returncode == 0, f"Overloads not accessible:\n{r.stderr[:500]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

def test_masquerading_class_preserved():
    """HIPStreamMasqueradingAsCUDA class must still exist in original header."""
    src = HIP_MASQ_H.read_text()
    assert "class HIPStreamMasqueradingAsCUDA" in src, (
        "HIPStreamMasqueradingAsCUDA class removed from original header"
    )


def test_operator_ostream_preserved():
    """operator<< for HIPStreamMasqueradingAsCUDA preserved in original header."""
    src = HIP_MASQ_H.read_text()
    assert re.search(r"operator\s*<<.*HIPStreamMasqueradingAsCUDA", src), (
        "operator<< for HIPStreamMasqueradingAsCUDA removed"
    )


def test_nonmasquerading_hip_aliases_preserved():
    """Non-masquerading HIP aliases still present in CUDAStream.h."""
    cuda_h = _strip_cpp_comments(CUDA_STREAM_H.read_text())
    assert re.search(r"getCurrentHIPStream(?!Masq)\s*[\(=]", cuda_h), (
        "getCurrentHIPStream alias missing"
    )
    assert re.search(r"setCurrentHIPStream(?!Masq)\s*[\(=]", cuda_h), (
        "setCurrentHIPStream alias missing"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — code style rules via behavioral checks
# ---------------------------------------------------------------------------

def test_masquerading_fns_removed_from_hip_header():
    """Masquerading functions moved from HIPStreamMasqueradingAsCUDA.h to CUDAStream.h.

    Verifies by compiling code that relies on the functions being accessible only
    via the public CUDAStream.h header, not defined in the internal ATen header.
    """
    # Test that the functions are accessible (they're now in CUDAStream.h)
    r = _compile_fn_test("(void)c10::hip::getCurrentHIPStreamMasqueradingAsCUDA(-1)")
    assert r.returncode == 0, f"Functions not accessible via CUDAStream.h:\n{r.stderr[:500]}"

    # Also verify the HIP header doesn't have duplicate definitions
    # by checking that including just the HIP header doesn't provide the functions
    hip_src = HIP_MASQ_H.read_text()
    stripped = _strip_cpp_comments(hip_src)
    fns = [
        "getCurrentHIPStreamMasqueradingAsCUDA",
        "getDefaultHIPStreamMasqueradingAsCUDA",
        "getStreamFromPoolMasqueradingAsCUDA",
        "getStreamFromExternalMasqueradingAsCUDA",
        "setCurrentHIPStreamMasqueradingAsCUDA",
    ]
    for fn in fns:
        # Check that function definitions (not just mentions in comments) are gone
        assert not re.search(rf"\b{fn}\s*\(", stripped), (
            f"{fn} still defined in HIPStreamMasqueradingAsCUDA.h"
        )


def test_functions_in_hip_namespace():
    """Masquerading functions placed in c10::hip namespace (matching existing pattern).

    Verifies by compiling code that explicitly references c10::hip:: namespace
    for all masquerading functions, confirming proper namespace placement.
    """
    # Test all functions in c10::hip namespace
    test_code = """
        using c10::hip::getCurrentHIPStreamMasqueradingAsCUDA;
        using c10::hip::getDefaultHIPStreamMasqueradingAsCUDA;
        using c10::hip::getStreamFromPoolMasqueradingAsCUDA;
        using c10::hip::getStreamFromExternalMasqueradingAsCUDA;
        using c10::hip::setCurrentHIPStreamMasqueradingAsCUDA;
    """
    r = _compile_namespace_test(test_code)
    assert r.returncode == 0, f"Functions not in c10::hip namespace:\n{r.stderr[:500]}"
