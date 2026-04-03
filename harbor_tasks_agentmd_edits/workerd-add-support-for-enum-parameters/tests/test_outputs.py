"""
Task: workerd-add-support-for-enum-parameters
Repo: cloudflare/workerd @ 13c36cb69dbfa695bb8862c0eb2b2a7c0be51d0e
PR:   5857

Adds #[jsg_oneof] proc macro attribute for union/enum parameter types in Rust JSG,
plus try_from_js_exact on FromJS trait and impl FromJS for &T.

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
    """Existing proc macros (jsg_struct, jsg_method, jsg_resource) still defined."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    for macro_name in ["jsg_struct", "jsg_method", "jsg_resource"]:
        assert f"pub fn {macro_name}" in lib_rs, \
            f"Existing macro {macro_name} must still be defined in jsg-macros/lib.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code implementation tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_oneof_proc_macro_defined():
    """jsg-macros/lib.rs must export a #[proc_macro_attribute] pub fn jsg_oneof."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    assert "pub fn jsg_oneof" in lib_rs, \
        "jsg-macros/lib.rs must define pub fn jsg_oneof"
    assert re.search(r"#\[proc_macro_attribute\]\s*pub fn jsg_oneof", lib_rs), \
        "jsg_oneof must be annotated with #[proc_macro_attribute]"


# [pr_diff] fail_to_pass
def test_oneof_validates_enum_and_variants():
    """jsg_oneof must validate input is an enum with single-field tuple variants."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    # Must check that the input is an enum
    assert "Data::Enum" in lib_rs or "DataEnum" in lib_rs, \
        "jsg_oneof must check that input is an enum"
    # Must validate variants are tuple variants with one field
    assert "Unnamed" in lib_rs or "unnamed" in lib_rs, \
        "jsg_oneof must check for tuple variants"
    # Must reject non-enum types
    assert "can only be applied to enum" in lib_rs.lower() or \
           "only.*enum" in lib_rs.lower(), \
        "jsg_oneof must produce an error for non-enum types"


# [pr_diff] fail_to_pass
def test_oneof_generates_type_and_fromjs_impls():
    """jsg_oneof must generate both jsg::Type and jsg::FromJS implementations."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    # Find the jsg_oneof function body (after the function definition)
    oneof_start = lib_rs.find("pub fn jsg_oneof")
    assert oneof_start != -1, "jsg_oneof function must exist"
    oneof_body = lib_rs[oneof_start:]
    # Must generate Type impl with class_name and is_exact
    assert "class_name" in oneof_body, \
        "jsg_oneof must generate class_name() in Type impl"
    assert "is_exact" in oneof_body, \
        "jsg_oneof must generate is_exact() in Type impl"
    # Must generate FromJS impl with from_js
    assert "from_js" in oneof_body, \
        "jsg_oneof must generate from_js() in FromJS impl"
    # Must produce a TypeError when no variant matches
    assert "type_error" in oneof_body.lower() or "TypeError" in oneof_body or \
           "new_type_error" in oneof_body, \
        "jsg_oneof must throw TypeError when no variant matches"


# [pr_diff] fail_to_pass
def test_try_from_js_exact_in_fromjs_trait():
    """FromJS trait must have a try_from_js_exact default method for exact type matching."""
    wrappable_rs = Path(f"{REPO}/src/rust/jsg/wrappable.rs").read_text()
    assert "try_from_js_exact" in wrappable_rs, \
        "wrappable.rs must define try_from_js_exact"
    # Must be inside the FromJS trait (check it's a method with correct signature)
    assert re.search(r"fn try_from_js_exact\s*\(", wrappable_rs), \
        "try_from_js_exact must be a function with proper signature"
    # Must check is_exact before converting
    assert "is_exact" in wrappable_rs, \
        "try_from_js_exact must use is_exact() for type checking"
    # Must return Option to signal match/no-match
    assert "Option<Result<" in wrappable_rs or "Option<Result <" in wrappable_rs, \
        "try_from_js_exact must return Option<Result<...>>"


# [pr_diff] fail_to_pass
def test_ref_fromjs_impl():
    """wrappable.rs must implement FromJS for &T to support reference parameters."""
    wrappable_rs = Path(f"{REPO}/src/rust/jsg/wrappable.rs").read_text()
    # Must have a blanket impl for references
    assert re.search(r"impl\s*<\s*T.*>\s*FromJS\s+for\s+&\s*T", wrappable_rs), \
        "wrappable.rs must implement FromJS for &T"


# [pr_diff] fail_to_pass
def test_oneof_test_module_registered():
    """jsg-test/tests/mod.rs must register the jsg_oneof test module."""
    mod_rs = Path(f"{REPO}/src/rust/jsg-test/tests/mod.rs").read_text()
    assert "jsg_oneof" in mod_rs, \
        "mod.rs must include jsg_oneof test module"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_oneof_has_real_logic():
    """jsg_oneof function has substantial implementation, not a stub."""
    lib_rs = Path(f"{REPO}/src/rust/jsg-macros/lib.rs").read_text()
    oneof_start = lib_rs.find("pub fn jsg_oneof")
    assert oneof_start != -1, "jsg_oneof must exist"
    # Count substantive lines in the function body (rough check)
    # The function should have at least 30 lines of real logic
    oneof_body = lib_rs[oneof_start:]
    # Find the end by tracking brace depth
    depth = 0
    end_pos = 0
    started = False
    for i, ch in enumerate(oneof_body):
        if ch == '{':
            depth += 1
            started = True
        elif ch == '}':
            depth -= 1
            if started and depth == 0:
                end_pos = i
                break
    func_body = oneof_body[:end_pos]
    non_empty_lines = [l.strip() for l in func_body.splitlines() if l.strip() and not l.strip().startswith("//")]
    assert len(non_empty_lines) >= 20, \
        f"jsg_oneof must have substantial logic (found {len(non_empty_lines)} non-empty lines, expected >= 20)"
