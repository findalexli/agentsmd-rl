"""
Task: pytorch-from-blob-lambda-deleter
Repo: pytorch/pytorch @ 41f8e3e0381395e1669ca4bc6e36a7872d25cdcd
PR:   177048

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/pytorch"

SHIM_H = Path(REPO) / "torch/csrc/stable/c/shim.h"
SHIM_CPP = Path(REPO) / "torch/csrc/shim_common.cpp"
OPS_H = Path(REPO) / "torch/csrc/stable/ops.h"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — C ABI two-arg deleter callback
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_shim_h_two_arg_deleter_callback():
    """shim.h declares a C function with a two-arg deleter: void (*)(void*, void*)."""
    # Structural check because: C++ header requiring full PyTorch build infrastructure
    src = SHIM_H.read_text()

    # Find function-pointer parameters with exactly two void* arguments.
    # Base code only has void (*deleter)(void*) — single arg.
    two_arg_cb = re.findall(
        r'void\s*\(\s*\*\s*\w*\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
        src,
    )
    assert two_arg_cb, (
        "shim.h has no C function-pointer parameter with two void* args "
        "(void (*)(void*, void*))"
    )


# [pr_diff] fail_to_pass
def test_shim_h_context_pointer():
    """shim.h torch_from_blob declaration carries a separate void* context parameter."""
    # Structural check because: C++ header requiring full PyTorch build infrastructure
    src = SHIM_H.read_text()

    # Extract all torch_from_blob-family declarations
    func_decls = re.findall(
        r'AOTI_TORCH_EXPORT\s+AOTITorchError\s+torch_from_blob\w*\s*\([^;]+\)\s*;',
        src,
        re.DOTALL,
    )
    assert func_decls, "No torch_from_blob declaration found in shim.h"

    # At least one declaration must have the two-arg callback followed by
    # a standalone void* context parameter (not inside the callback parens).
    found = False
    for decl in func_decls:
        has_two_arg_cb = bool(
            re.search(
                r'void\s*\(\s*\*\s*\w*\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
                decl,
            )
        )
        # After the callback, there should be a separate void* param (the context)
        has_ctx_after_cb = bool(
            re.search(
                r'void\s*\(\s*\*\s*\w*\s*\)\s*\([^)]*\)\s*,\s*\n?\s*void\s*\*\s*\w+',
                decl,
            )
        )
        if has_two_arg_cb and has_ctx_after_cb:
            found = True
            break
    assert found, (
        "No torch_from_blob declaration has both a two-arg callback and a "
        "separate void* context parameter after it"
    )


# [pr_diff] fail_to_pass
def test_shim_cpp_wraps_two_arg_callback():
    """shim_common.cpp accepts a two-arg callback and wraps it for at::for_blob."""
    # Structural check because: C++ implementation requiring full PyTorch build infrastructure
    src = SHIM_CPP.read_text()

    # 1. Must accept a two-arg callback: void (*xxx)(void*, void*)
    assert re.search(
        r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
        src,
    ), "shim_common.cpp has no function accepting a two-arg deleter callback"

    # 2. The function containing the two-arg callback must use for_blob + .deleter
    #    to connect the wrapped callback to tensor creation.
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found_wrapping = False
    for func_block in funcs:
        has_cb = bool(
            re.search(
                r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
                func_block,
            )
        )
        if has_cb and 'for_blob' in func_block and '.deleter' in func_block:
            found_wrapping = True
            break
    assert found_wrapping, (
        "No function in shim_common.cpp connects a two-arg callback to "
        "for_blob's .deleter()"
    )


# [pr_diff] fail_to_pass
def test_ops_h_generic_callable():
    """ops.h from_blob accepts generic callables (template or std::function), not just DeleterFnPtr."""
    # Structural check because: C++ header requiring full PyTorch build infrastructure
    src = OPS_H.read_text()

    # Base code only has from_blob(..., DeleterFnPtr deleter, ...).
    # A correct fix uses template<class F> or std::function to accept capturing lambdas.
    # Note: [^{;]* instead of [^>]* to handle nested angle brackets like
    # template <class F, std::enable_if_t<std::is_invocable_v<F, void*>, int> = 0>
    has_template = bool(
        re.search(
            r'template\s*<[^{;]*>\s+(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(',
            src,
        )
    )
    has_std_function = bool(
        re.search(r'from_blob\s*\([^)]*std::function[^)]*\)', src, re.DOTALL)
    )
    assert has_template or has_std_function, (
        "ops.h has no mechanism to accept capturing lambdas on from_blob "
        "(no template<class F> or std::function)"
    )


# [pr_diff] fail_to_pass
def test_shim_cpp_context_forwarded():
    """shim_common.cpp forwards the context pointer to the callback invocation."""
    # Structural check because: C++ implementation requiring full PyTorch build infrastructure
    src = SHIM_CPP.read_text()

    # The wrapping lambda must capture and forward the context to the callback.
    # Look for a lambda that calls the callback with both data and ctx arguments.
    # Pattern: callback(data, ctx) or callback_name(some_var, some_var)
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found_forwarding = False
    for func_block in funcs:
        has_two_arg_cb = bool(
            re.search(
                r'void\s*\(\s*\*\s*\w+\s*\)\s*\(\s*void\s*\*\s*\w*\s*,\s*void\s*\*\s*\w*\s*\)',
                func_block,
            )
        )
        if not has_two_arg_cb:
            continue
        # Must have a lambda [...] that calls the callback with two args
        has_lambda_wrap = bool(
            re.search(r'\[.*\]\s*\(\s*void\s*\*\s*\w+\s*\)', func_block)
        )
        # The callback must be invoked with two arguments inside the lambda
        has_two_arg_call = bool(
            re.search(r'\w+\s*\(\s*\w+\s*,\s*\w+\s*\)', func_block)
        )
        if has_lambda_wrap and has_two_arg_call:
            found_forwarding = True
            break
    assert found_forwarding, (
        "shim_common.cpp does not forward the context pointer through a wrapping "
        "lambda to the two-arg callback"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — backward compatibility + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_deleter_overload_preserved():
    """The no-deleter from_blob overload (aoti_torch_create_tensor_from_blob path) still exists."""
    # Structural check because: C++ header requiring full PyTorch build infrastructure
    src = OPS_H.read_text()

    from_blob_defs = re.findall(
        r'(?:inline\s+)?(?:\w+::)*\w+\s+from_blob\s*\(', src
    )
    assert len(from_blob_defs) >= 2, (
        f"Expected >= 2 from_blob overloads, found {len(from_blob_defs)}"
    )
    assert 'aoti_torch_create_tensor_from_blob' in src, (
        "Original no-deleter from_blob (using aoti_torch_create_tensor_from_blob) removed"
    )


# [static] pass_to_pass
def test_files_not_stubbed():
    """Modified files have real implementation, not stubs."""
    # Structural check because: C++ code requiring full PyTorch build infrastructure
    ops_src = OPS_H.read_text()
    ops_lines = ops_src.strip().splitlines()
    assert len(ops_lines) >= 100, f"ops.h too short ({len(ops_lines)} lines)"
    assert "TORCH_ERROR_CODE_CHECK" in ops_src, "ops.h missing TORCH_ERROR_CODE_CHECK"
    assert "AtenTensorHandle" in ops_src, "ops.h missing AtenTensorHandle"

    cpp_src = SHIM_CPP.read_text()
    cpp_lines = cpp_src.strip().splitlines()
    assert len(cpp_lines) >= 100, f"shim_common.cpp too short ({len(cpp_lines)} lines)"
    assert "AOTI_TORCH_CONVERT_EXCEPTION_TO_ERROR_CODE" in cpp_src

    h_src = SHIM_H.read_text()
    h_lines = h_src.strip().splitlines()
    assert len(h_lines) >= 50, f"shim.h too short ({len(h_lines)} lines)"


# [pr_diff] pass_to_pass
def test_shim_cpp_null_callback_guard():
    """shim_common.cpp still guards against nullptr callback (backward compat)."""
    # Structural check because: C++ implementation requiring full PyTorch build infrastructure
    src = SHIM_CPP.read_text()

    # The implementation must check if the callback is null before wrapping.
    # Base code has: if (deleter != nullptr). Fix should keep a similar guard.
    funcs = re.split(r'(?=AOTI_TORCH_EXPORT\s+AOTITorchError)', src)
    found_guard = False
    for func_block in funcs:
        if 'for_blob' not in func_block:
            continue
        # Check for nullptr guard on the callback parameter
        if re.search(r'if\s*\(\s*\w+\s*!=\s*nullptr\s*\)', func_block):
            found_guard = True
            break
    assert found_guard, (
        "shim_common.cpp is missing a nullptr guard for the deleter callback"
    )
