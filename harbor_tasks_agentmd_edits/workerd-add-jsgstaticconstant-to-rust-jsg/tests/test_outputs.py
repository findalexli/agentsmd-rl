"""
Task: workerd-add-jsgstaticconstant-to-rust-jsg
Repo: cloudflare/workerd @ 8a0534f6ac6363ee564dc1e6b22e6579786f22c3
PR:   6284

Adds #[jsg_static_constant] proc macro attribute to expose Rust const items
as read-only numeric constants on both the JS constructor and prototype.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — existing macros still defined
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_macros_intact():
    """Existing proc macros (jsg_struct, jsg_method, jsg_resource, jsg_oneof) still defined."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    for macro_name in ["jsg_struct", "jsg_method", "jsg_resource", "jsg_oneof"]:
        assert f"pub fn {macro_name}" in lib_rs, \
            f"Existing macro {macro_name} must still be defined in jsg-macros/lib.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code implementation tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_proc_macro_attribute_defined():
    """jsg-macros/lib.rs must export a #[proc_macro_attribute] pub fn jsg_static_constant."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    # Must have the proc_macro_attribute annotation followed by the function
    assert "pub fn jsg_static_constant" in lib_rs, \
        "jsg-macros/lib.rs must define pub fn jsg_static_constant"
    # Must be a proc_macro_attribute, not just any function
    assert re.search(r"#\[proc_macro_attribute\]\s*pub fn jsg_static_constant", lib_rs), \
        "jsg_static_constant must be annotated with #[proc_macro_attribute]"


# [pr_diff] fail_to_pass
def test_constant_registrations_in_resource_impl():
    """generate_resource_impl must collect constant registrations from impl items."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    # The impl must scan for jsg_static_constant-attributed const items
    assert "ImplItem::Const" in lib_rs or "ImplItemConst" in lib_rs, \
        "generate_resource_impl must handle const impl items"
    # Must generate Member::StaticConstant registrations
    assert "StaticConstant" in lib_rs, \
        "Must generate Member::StaticConstant registrations"
    # Must include constant_registrations in the members() vec
    assert "constant_registrations" in lib_rs, \
        "Must collect constant_registrations and include them in members()"


# [pr_diff] fail_to_pass
def test_constant_value_type_and_member_variant():
    """jsg/lib.rs must define ConstantValue enum and Member::StaticConstant variant."""
    jsg_lib = Path(f"{REPO}/src/rust/jsg/lib.rs").read_text()
    # ConstantValue enum with Number variant
    assert "enum ConstantValue" in jsg_lib, \
        "jsg/lib.rs must define ConstantValue enum"
    assert "Number(f64)" in jsg_lib, \
        "ConstantValue must have a Number(f64) variant"
    # Member::StaticConstant variant
    assert re.search(r"StaticConstant\s*\{", jsg_lib), \
        "Member enum must have a StaticConstant variant"
    # Must have From impls for numeric types
    assert "impl From<i32> for ConstantValue" in jsg_lib or \
           "impl_constant_value_from" in jsg_lib, \
        "ConstantValue must implement From for numeric types"


# [pr_diff] fail_to_pass
def test_ffi_registers_constants_on_constructor_and_prototype():
    """ffi.c++ must iterate static_constants and set them on both constructor and prototype."""
    ffi_cpp = Path(f"{REPO}/src/rust/jsg/ffi.c++").read_text()
    assert "static_constants" in ffi_cpp, \
        "ffi.c++ must reference static_constants from the descriptor"
    # Must set on both constructor and prototype
    # Look for both constructor->Set and prototype->Set near the constants loop
    constants_section = ffi_cpp[ffi_cpp.find("static_constants"):]
    assert "constructor->Set" in constants_section or "constructor.Set" in constants_section or \
           "constructor->Set(name, value" in ffi_cpp, \
        "Constants must be set on the constructor"
    assert "prototype->Set" in constants_section or "prototype.Set" in constants_section, \
        "Constants must be set on the prototype"
    # Must be read-only
    assert "ReadOnly" in constants_section, \
        "Constants must be set with ReadOnly attribute"


# [pr_diff] fail_to_pass
def test_static_constant_descriptor_in_v8_ffi():
    """v8.rs must define StaticConstantDescriptor and add static_constants to ResourceDescriptor."""
    v8_rs = Path(f"{REPO}/src/rust/jsg/v8.rs").read_text()
    assert "StaticConstantDescriptor" in v8_rs, \
        "v8.rs must define StaticConstantDescriptor struct"
    # ResourceDescriptor must have a static_constants field
    desc_match = re.search(r"struct ResourceDescriptor\s*\{(.*?)\}", v8_rs, re.DOTALL)
    assert desc_match, "ResourceDescriptor struct must exist in v8.rs"
    desc_body = desc_match.group(1)
    assert "static_constants" in desc_body, \
        "ResourceDescriptor must include a static_constants field"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
