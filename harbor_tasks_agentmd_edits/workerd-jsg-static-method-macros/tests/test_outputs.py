"""
Task: workerd-jsg-static-method-macros
Repo: cloudflare/workerd @ d7dc27c438f7ea1fd5eb28a0258d5dbae265a99d
PR:   6279

Add static method support to Rust JSG macros. Methods without a receiver
(&self/&mut self) should be registered as static methods on the constructor
instead of instance methods on the prototype.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — basic file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust and C++ files exist and are non-empty."""
    files = [
        "src/rust/jsg-macros/lib.rs",
        "src/rust/jsg/v8.rs",
        "src/rust/jsg/ffi.h",
        "src/rust/jsg/ffi.c++",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must not be empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_method_detects_receiver():
    """jsg_method macro must detect whether a method has a self receiver."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # The macro must inspect function arguments for a receiver (FnArg::Receiver)
    # to distinguish instance methods from static methods.
    assert "Receiver" in lib_rs, \
        "jsg_method must check for FnArg::Receiver to detect self parameter"
    # Must track receiver presence in a variable
    assert re.search(r"has_self|is_static|is_instance|has_receiver", lib_rs), \
        "jsg_method must store receiver detection result in a variable"


# [pr_diff] fail_to_pass
def test_static_method_invocation_uses_type_call():
    """Static method callbacks must invoke via Self:: not via self_."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # For static methods, the generated callback must call Self::fn_name(args)
    # rather than self_.fn_name(args). Check that Self:: appears in the
    # code generation for method invocation.
    assert re.search(r"Self\s*::\s*#", lib_rs), \
        "Static methods must use Self::fn_name invocation pattern in quote! block"
    # Must have conditional logic that branches on receiver presence
    assert re.search(
        r"if\s+(has_self|!is_static|is_instance|has_receiver)\s*\{",
        lib_rs,
    ), "Must conditionally generate different invocation based on receiver"


# [pr_diff] fail_to_pass
def test_member_static_method_variant():
    """Resource impl generation must use Member::StaticMethod for receiver-less methods."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # The generate_resource_impl function must produce StaticMethod members
    assert "StaticMethod" in lib_rs, \
        "Must use a StaticMethod member variant for methods without receiver"
    # Must appear in a quote! block constructing a Member
    assert re.search(r"Member\s*::\s*StaticMethod\s*\{", lib_rs), \
        "Must construct Member::StaticMethod { name, callback } in quote! block"


# [pr_diff] fail_to_pass
def test_ffi_function_template_get_function():
    """FFI layer must expose a way to get a Function from a FunctionTemplate."""
    ffi_h = (Path(REPO) / "src/rust/jsg/ffi.h").read_text()
    # There must be a C++ function that extracts a Function from a FunctionTemplate.
    # The canonical V8 API is FunctionTemplate::GetFunction().
    assert re.search(r"function_template_get_function|get_constructor_function", ffi_h), \
        "ffi.h must declare a function to get constructor from FunctionTemplate"

    ffi_cpp = (Path(REPO) / "src/rust/jsg/ffi.c++").read_text()
    assert "GetFunction" in ffi_cpp, \
        "ffi.c++ must call V8's GetFunction to materialize the constructor"


# [pr_diff] fail_to_pass
def test_v8_function_type_and_conversion():
    """v8.rs must define a Function type with conversion to Value."""
    v8_rs = (Path(REPO) / "src/rust/jsg/v8.rs").read_text()
    # Must define Function as a Rust type (not FunctionTemplate or FunctionCallbackInfo)
    assert re.search(r"pub\s+struct\s+Function\s*;", v8_rs), \
        "v8.rs must define a public Function struct"
    # Must have a way to convert Global<FunctionTemplate> to a local Function
    assert re.search(
        r"(as_local_function|to_function|get_function|into_function)",
        v8_rs,
    ), "Must provide a method to get a local Function from FunctionTemplate"
    # Must have From<Local<Function>> for Local<Value> conversion
    # Use Function>> to exclude FunctionTemplate which already exists at base
    assert re.search(r"From<Local.*Function>>.*for.*Local.*Value", v8_rs), \
        "Must implement From<Local<Function>> for Local<Value>"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation/config update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
