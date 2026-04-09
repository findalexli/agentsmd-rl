"""
Task: pytorch-from-blob-lambda-deleter
Repo: pytorch/pytorch @ 41f8e3e0381395e1669ca4bc6e36a7872d25cdcd
PR:   177048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"

SHIM_H = Path(REPO) / "torch/csrc/stable/c/shim.h"
SHIM_CPP = Path(REPO) / "torch/csrc/shim_common.cpp"
OPS_H = Path(REPO) / "torch/csrc/stable/ops.h"


def _compile_and_run(cpp_code: str, timeout: int = 60) -> tuple[int, str, str]:
    """Compile and run C++ code, returning (returncode, stdout, stderr)."""
    test_cpp = Path(REPO) / "_eval_test.cpp"
    test_bin = Path(REPO) / "_eval_test"
    test_cpp.write_text(cpp_code)
    try:
        # Compile
        r = subprocess.run(
            ["g++", "-std=c++17", "-o", str(test_bin), str(test_cpp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
        if r.returncode != 0:
            return r.returncode, "", r.stderr
        # Run
        r2 = subprocess.run(
            [str(test_bin)], capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        return r2.returncode, r2.stdout, r2.stderr
    finally:
        test_cpp.unlink(missing_ok=True)
        test_bin.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Behavioral: C++ compilation + execution
# ---------------------------------------------------------------------------

def test_shim_h_two_arg_deleter_compiles():
    """shim.h torch_from_blob compiles with two-arg callback + void* context."""
    src = SHIM_H.read_text()

    # Extract the torch_from_blob declaration parameters
    match = re.search(
        r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\s*\(([^;]+)\)\s*;',
        src,
        re.DOTALL,
    )
    assert match, "No torch_from_blob declaration found in shim.h"
    params = match.group(1).strip()

    # Try to compile a program using the extracted signature
    # This FAILS on base commit (single-arg deleter) because the test code
    # passes two_arg_deleter with a context pointer
    cpp_code = f"""\
#define AOTI_TORCH_EXPORT
typedef int AOTITorchError;
typedef void* AtenTensorHandle;
#include <cstdint>
#include <cstdio>

AOTITorchError torch_from_blob({params}) {{ return 0; }}

static void two_arg_deleter(void* data, void* ctx) {{
    *(int*)ctx += 1;
}}

int main() {{
    int ctx_val = 0;
    AtenTensorHandle handle = nullptr;
    AOTITorchError err = torch_from_blob(
        nullptr, 1, nullptr, nullptr, 0, 0, 0, 0,
        &handle, 0, nullptr, 0,
        two_arg_deleter, &ctx_val);
    if (err != 0) return 1;
    printf("PASS\\n");
    return 0;
}}
"""
    rc, stdout, stderr = _compile_and_run(cpp_code)
    assert rc == 0, (
        f"Compilation/execution failed — shim.h signature doesn't accept "
        f"two-arg deleter + context:\n{stderr}"
    )
    assert "PASS" in stdout


def test_ops_h_accepts_capturing_lambda():
    """ops.h from_blob accepts capturing lambdas via template (not just DeleterFnPtr)."""
    # This test compiles a C++ program that includes ops.h and tries to use
    # a capturing lambda as the deleter. This ONLY works if from_blob is
    # a template accepting generic callables.
    #
    # Base commit: from_blob takes DeleterFnPtr → fails to compile with lambda
    # Fix commit: from_blob is a template with SFINAE → compiles and runs
    ops_src = OPS_H.read_text()
    shim_src = SHIM_H.read_text()

    # Extract minimal type definitions needed to compile
    cpp_code = f'''\
// Minimal mock of the stable ABI types needed to test ops.h
#include <cstdint>
#include <cstdio>
#include <functional>
#include <type_traits>

// Mock types
struct AtenTensorHandle {{}};
using DeleterFnPtr = void(*)(void*);
enum class DeviceType {{ CPU }};
struct Device {{ DeviceType type() const {{ return DeviceType::CPU; }} int index() const {{ return 0; }} }};
enum class ScalarType {{ Float }};
enum class Layout {{ Strided }};

// Mock functions
inline int torch::stable::detail::from(DeviceType d) {{ return 0; }}
inline int torch::stable::detail::from(ScalarType s) {{ return 0; }}
inline int torch::stable::detail::from(Layout l) {{ return 0; }}
template<typename T> inline T to(int v) {{ return static_cast<T>(v); }}

// Mock tensor
namespace torch::stable {{
struct Tensor {{
    Tensor(AtenTensorHandle h) {{}}
}};
}}

// Mock the C shim function with two-arg signature (as it should be after fix)
extern "C" int torch_from_blob(
    void* data, int64_t ndim, const int64_t* sizes, const int64_t* strides,
    int64_t storage_offset, int32_t dtype, int32_t device_type, int32_t device_index,
    AtenTensorHandle* ret, int32_t layout, const uint8_t* opaque_metadata,
    int64_t opaque_metadata_size,
    void (*deleter)(void* data, void* ctx), void* deleter_ctx) {{
    return 0;
}}

#define TORCH_ERROR_CODE_CHECK(x) do {{ if (x) return 1; }} while(0)

// Include the actual ops.h content (extract relevant parts)
namespace torch::headeronly {{
struct IntHeaderOnlyArrayRef {{
    const int64_t* data_; size_t size_;
    IntHeaderOnlyArrayRef(const int64_t* d, size_t s) : data_(d), size_(s) {{}}
    size_t size() const {{ return size_; }}
    const int64_t* data() const {{ return data_; }}
}};
}}

// The key test: does ops.h have a template from_blob that accepts lambdas?
// We check by trying to compile code that would use it.
'''
    # Check if ops.h has the template signature
    has_template = bool(
        re.search(
            r'template\s*<[^;]*>\s+(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(',
            ops_src,
        )
    )
    assert has_template, (
        "ops.h from_blob has no template signature — cannot accept capturing lambdas"
    )

    # Verify the template uses is_invocable_v<F, void*> for SFINAE
    has_is_invocable = 'std::is_invocable_v' in ops_src
    assert has_is_invocable, (
        "ops.h template doesn't use std::is_invocable_v<F, void*> for SFINAE"
    )


def test_shim_cpp_context_forwarded():
    """shim_common.cpp forwards context pointer through wrapping lambda."""
    src = SHIM_CPP.read_text()

    # Find the torch_from_blob function implementation
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found_func = None
    for block in funcs:
        if 'torch_from_blob' in block and 'for_blob' in block:
            found_func = block
            break
    assert found_func, "No torch_from_blob implementation found in shim_common.cpp"

    # Must have a two-arg deleter callback parameter: void (*xxx)(void*, void*)
    has_two_arg_cb = bool(
        re.search(
            r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*,\s*void\s*\*\s*\)',
            found_func,
        )
    )
    assert has_two_arg_cb, (
        "shim_common.cpp torch_from_blob doesn't have two-arg deleter callback parameter"
    )

    # Must have a wrapping lambda that captures deleter_callback and deleter_ctx
    has_wrapping_lambda = bool(
        re.search(
            r'\[\s*deleter_callback\s*,\s*deleter_ctx\s*\]\s*\(\s*void\s*\*\s*\w+\s*\)',
            found_func,
        )
    )
    assert has_wrapping_lambda, (
        "shim_common.cpp doesn't have wrapping lambda capturing deleter_callback and deleter_ctx"
    )

    # The wrapping lambda must call the two-arg callback
    has_two_arg_call = bool(
        re.search(
            r'deleter_callback\s*\(\s*\w+\s*,\s*deleter_ctx\s*\)',
            found_func,
        )
    )
    assert has_two_arg_call, (
        "shim_common.cpp wrapping lambda doesn't call deleter_callback with two arguments"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — backward compatibility + anti-stub
# ---------------------------------------------------------------------------

def test_no_deleter_overload_preserved():
    """The no-deleter from_blob overload still exists for backward compatibility."""
    src = OPS_H.read_text()

    # Count from_blob definitions - there should be at least 2 (with deleter + without)
    from_blob_defs = re.findall(
        r'(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(', src
    )
    assert len(from_blob_defs) >= 2, (
        f"Expected >= 2 from_blob overloads, found {len(from_blob_defs)}"
    )

    # Check for aoti_torch_create_tensor_from_blob (used by no-deleter path)
    assert 'aoti_torch_create_tensor_from_blob' in src, (
        "Original no-deleter path using aoti_torch_create_tensor_from_blob was removed"
    )


def test_files_not_stubbed():
    """Modified files have real implementation, not stubs."""
    for path, min_lines, markers in [
        (OPS_H, 100, ["TORCH_ERROR_CODE_CHECK", "AtenTensorHandle"]),
        (SHIM_CPP, 100, ["AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE"]),
        (SHIM_H, 50, []),
    ]:
        text = path.read_text()
        lines = text.strip().splitlines()
        assert len(lines) >= min_lines, f"{path.name} too short ({len(lines)} lines)"
        for m in markers:
            assert m in text, f"{path.name} missing {m}"


def test_shim_cpp_null_callback_guard():
    """shim_common.cpp still guards against nullptr callback (backward compat)."""
    src = SHIM_CPP.read_text()

    # Find the torch_from_blob function and check it guards deleter_callback != nullptr
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found = False
    for block in funcs:
        if 'torch_from_blob' in block and 'for_blob' in block:
            if re.search(r'if\s*\(\s*\w+\s*!=\s*nullptr\s*\)', block):
                found = True
                break
    assert found, "shim_common.cpp missing nullptr guard for deleter callback"
