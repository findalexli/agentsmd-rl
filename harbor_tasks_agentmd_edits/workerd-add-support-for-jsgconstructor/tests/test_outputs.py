"""
Task: workerd-add-support-for-jsgconstructor
Repo: cloudflare/workerd @ dce7afd9ef1c45cd56bda8ac393358d381e41dd5
PR:   6353

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust files have balanced braces (basic structural check)."""
    files = [
        "src/rust/jsg-macros/lib.rs",
        "src/rust/jsg/resource.rs",
        "src/rust/jsg/v8.rs",
    ]
    for f in files:
        path = Path(REPO) / f
        assert path.exists(), f"{f} does not exist"
        content = path.read_text()
        # Basic brace balance check
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) < 5, (
            f"{f}: brace imbalance ({opens} open vs {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: proc macro implementation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_constructor_proc_macro_defined():
    """lib.rs must define a #[proc_macro_attribute] pub fn jsg_constructor."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # Must have the proc_macro_attribute + pub fn jsg_constructor
    assert "proc_macro_attribute" in lib_rs, "Missing #[proc_macro_attribute] for jsg_constructor"
    assert re.search(r"pub\s+fn\s+jsg_constructor", lib_rs), (
        "Missing pub fn jsg_constructor in lib.rs"
    )


# [pr_diff] fail_to_pass
def test_constructor_registration_logic():
    """lib.rs must scan impl blocks for #[jsg_constructor] and generate registration code."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # Must handle constructor detection in resource impl scanning (beyond just the macro def)
    # Remove the macro definition occurrence to check it's referenced elsewhere in codegen
    without_macro_def = lib_rs.replace("pub fn jsg_constructor", "")
    assert "jsg_constructor" in without_macro_def, (
        "lib.rs must reference jsg_constructor attribute when scanning impl blocks"
    )
    # Must generate a Constructor member variant or equivalent registration
    assert "Constructor" in lib_rs, (
        "lib.rs must generate a Constructor member registration"
    )
    # Must enforce single-constructor-per-impl-block rule
    assert re.search(r"only\s+one|single.*constructor|constructors\.len\(\)\s*>\s*1", lib_rs.lower()), (
        "Must enforce single-constructor-per-impl-block rule"
    )


# [pr_diff] fail_to_pass
def test_constructor_validates_no_self_receiver():
    """Constructor code generation must validate static method and return Self requirements."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    # The constructor codegen must emit compile errors for invalid signatures.
    # Check for error messages specific to constructor validation (not existing jsg_method code).
    has_constructor_self_error = re.search(
        r"jsg_constructor.*static|jsg_constructor.*self|constructor.*no\s+self|constructor.*static",
        lib_rs.lower(),
    )
    assert has_constructor_self_error, (
        "Constructor codegen must validate that the method has no self receiver"
    )
    # Must validate return type is Self — check for constructor-specific return validation
    has_return_self_check = re.search(
        r"jsg_constructor.*return.*Self|returns?_self|must return Self",
        lib_rs,
    )
    assert has_return_self_check, (
        "Constructor codegen must validate return type is Self"
    )


# [pr_diff] fail_to_pass
def test_ffi_attach_wrapper_function():
    """C++ FFI must provide a function to attach a Wrappable to the constructor's this object."""
    ffi_cpp = (Path(REPO) / "src/rust/jsg/ffi.c++").read_text()
    ffi_h = (Path(REPO) / "src/rust/jsg/ffi.h").read_text()

    # Must have a NEW C++ function for constructor attachment (distinct from existing wrap_resource).
    # The new function takes a FunctionCallbackInfo& (not Isolate* + Global&) because
    # constructors receive their target object via args.This() rather than creating one.
    # Count functions that take both Wrappable and FunctionCallbackInfo params.
    has_new_attach_fn = re.search(
        r"(?:void|Local)\s+\w+\(.*Wrappable.*FunctionCallbackInfo|"
        r"(?:void|Local)\s+\w+\(.*FunctionCallbackInfo.*Wrappable",
        ffi_cpp,
    )
    assert has_new_attach_fn, (
        "ffi.c++ must define a new function taking Wrappable + FunctionCallbackInfo "
        "for constructor attachment (separate from existing wrap_resource)"
    )
    # Header must also declare a function with Wrappable + FunctionCallbackInfo
    has_new_h_decl = re.search(
        r"Wrappable.*FunctionCallbackInfo|FunctionCallbackInfo.*Wrappable",
        ffi_h,
    )
    assert has_new_h_decl, (
        "ffi.h must declare the new constructor attach function"
    )


# [pr_diff] fail_to_pass
def test_rc_attach_to_this_method():
    """resource.rs must expose an attach_to_this method on Rc for constructor use."""
    resource_rs = (Path(REPO) / "src/rust/jsg/resource.rs").read_text()
    assert "attach_to_this" in resource_rs, (
        "resource.rs must have attach_to_this method on Rc"
    )
    assert "pub fn attach_to_this" in resource_rs, (
        "attach_to_this must be a public method"
    )


# [pr_diff] fail_to_pass
def test_v8_ffi_binding_for_attach():
    """v8.rs must declare the FFI binding for the attach wrapper function."""
    v8_rs = (Path(REPO) / "src/rust/jsg/v8.rs").read_text()
    # Must have the FFI declaration
    assert "attach" in v8_rs.lower(), (
        "v8.rs must declare the FFI function for attaching wrappable"
    )
    # Must have the WrappableRc method
    assert "attach_to_this" in v8_rs, (
        "v8.rs must implement attach_to_this on WrappableRc"
    )


# [pr_diff] fail_to_pass
def test_constructor_tests_added():
    """Test file must include constructor-related tests using jsg_constructor."""
    test_file = Path(REPO) / "src/rust/jsg-test/tests/resource_callback.rs"
    content = test_file.read_text()
    assert "jsg_constructor" in content, (
        "Test file must import/use jsg_constructor"
    )
    # Must have at least one test exercising the constructor
    assert "constructor" in content.lower(), (
        "Test file must have constructor tests"
    )
    # Must test that resources without constructor throw
    assert "without" in content.lower() or "illegal" in content.lower() or "throw" in content.lower(), (
        "Must test that resources without #[jsg_constructor] throw on new"
    )


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a section about jsg_constructor
    assert "jsg_constructor" in readme, (
        "jsg-macros/README.md must document #[jsg_constructor]"
    )
    # Must describe what it does — marks a method as JS constructor
    assert "constructor" in content_lower and "javascript" in content_lower, (
        "README must explain that jsg_constructor creates a JavaScript constructor"
    )
    # Must document the static method requirement
    assert "static" in content_lower or "no self" in content_lower or "no `self`" in readme, (
        "README must document that the method must be static (no self receiver)"
    )
    # Must document the return Self requirement
    assert "return" in content_lower and "self" in content_lower, (
        "README must document that the method must return Self"
    )
    # Must include a code example
    assert "```rust" in readme or "```" in readme, (
        "README must include a code example"
    )


# [config_edit] fail_to_pass

    # Must have a Constructors heading or section
    assert re.search(r"##\s+constructor", content_lower), (
        "jsg/README.md must have a Constructors section heading"
    )
    # Must document jsg_constructor attribute
    assert "jsg_constructor" in readme, (
        "jsg/README.md must reference #[jsg_constructor]"
    )
    # Must document the one-per-impl-block rule
    assert "one" in content_lower and "impl block" in content_lower, (
        "jsg/README.md must document one constructor per impl block rule"
    )
    # Must document illegal constructor behavior when missing
    assert "illegal" in content_lower or "throws" in content_lower or "error" in content_lower, (
        "jsg/README.md must document what happens without a constructor"
    )
    # Must include a code example with the attribute
    assert "```" in readme and "#[jsg_constructor]" in readme, (
        "jsg/README.md must include a code example using #[jsg_constructor]"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_macros_preserved():
    """Existing proc macros (jsg_struct, jsg_method, jsg_resource, etc.) still present."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()
    for macro_name in ["jsg_struct", "jsg_method", "jsg_resource", "jsg_static_constant", "jsg_oneof"]:
        assert f"pub fn {macro_name}" in lib_rs, (
            f"Existing macro {macro_name} must still be present in lib.rs"
        )


# [static] pass_to_pass
def test_not_stub():
    """The jsg_constructor proc macro function and registration logic are not stubs."""
    lib_rs = (Path(REPO) / "src/rust/jsg-macros/lib.rs").read_text()

    # Find the generate_constructor_registration function (or equivalent constructor logic)
    # It must have meaningful content — at least 20 lines of logic
    constructor_logic_markers = [
        "jsg_constructor",
        "Constructor",
        "callback",
        "attach_to_this",
    ]
    matched = sum(1 for m in constructor_logic_markers if m in lib_rs)
    assert matched >= 3, (
        f"Constructor implementation appears to be a stub — only {matched}/4 key markers found"
    )

    # The registration must generate a callback function
    assert "callback" in lib_rs.lower() and "fn" in lib_rs, (
        "Constructor registration must generate a callback function"
    )
