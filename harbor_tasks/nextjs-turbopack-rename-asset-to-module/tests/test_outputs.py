"""
Task: nextjs-turbopack-rename-asset-to-module
Repo: vercel/next.js @ d84e3bb56ecfdd9ff6ab5ee479e85be2780b8ba9
PR:   92028

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/nextjs"
TARGET = f"{REPO}/turbopack/crates/turbopack-core/src/reference/mod.rs"


def _src():
    return Path(TARGET).read_text()


def _struct_block(src):
    """Return the SingleModuleReference struct body (between { and })."""
    m = re.search(
        r"pub struct SingleModuleReference\s*\{([^}]+)\}", src
    )
    assert m, "SingleModuleReference struct not found"
    return m.group(1)


def _value_impl_block(src):
    """Return the full #[turbo_tasks::value_impl] impl block for SingleModuleReference."""
    # Find impl SingleModuleReference { ... } that contains new()
    pattern = r"impl SingleModuleReference \{(.*?)\n\}"
    matches = list(re.finditer(pattern, src, re.DOTALL))
    for m in matches:
        if "pub fn new(" in m.group(0):
            return m.group(0)
    assert False, "impl SingleModuleReference with new() not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_struct_field_named_module():
    """SingleModuleReference struct field is 'module', not 'asset'."""
    src = _src()
    block = _struct_block(src)
    assert re.search(r"\bmodule\s*:", block), (
        f"Expected 'module:' field in SingleModuleReference struct, got:\n{block}"
    )
    assert not re.search(r"\basset\s*:", block), (
        f"Old 'asset:' field still present in struct:\n{block}"
    )


def test_no_asset_getter_in_impl():
    """The asset() getter method is removed from SingleModuleReference impl."""
    src = _src()
    block = _value_impl_block(src)
    assert not re.search(r"pub fn asset\(", block), (
        "Old asset() getter still exists in SingleModuleReference impl"
    )


def test_constructor_param_named_module():
    """The new() constructor takes 'module' as parameter name, not 'asset'."""
    src = _src()
    block = _value_impl_block(src)
    m = re.search(r"pub fn new\(([^)]+)\)", block)
    assert m, "new() not found in SingleModuleReference impl"
    params = m.group(1)
    assert re.search(r"\bmodule\s*:", params), (
        f"Expected 'module:' parameter in new(), got: {params}"
    )
    assert not re.search(r"\basset\s*:", params), (
        f"Old 'asset:' parameter still in new(): {params}"
    )


def test_resolve_reference_uses_module_field():
    """resolve_reference uses self.module, not self.asset."""
    src = _src()
    pattern = (
        r"impl ModuleReference for SingleModuleReference.*?"
        r"fn resolve_reference.*?"
        r"ModuleResolveResult::module\(self\.(\w+)\)"
    )
    m = re.search(pattern, src, re.DOTALL)
    assert m, "resolve_reference for SingleModuleReference not found"
    field = m.group(1)
    assert field == "module", (
        f"resolve_reference uses self.{field} instead of self.module"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / regression
# ---------------------------------------------------------------------------


def test_rust_syntax_valid():
    """The modified file has balanced braces and valid structure."""
    src = _src()
    assert len(src) > 100, "File is too short"
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open vs {close_braces} close"
    )


def test_description_field_preserved():
    """The description field is preserved in SingleModuleReference."""
    src = _src()
    block = _struct_block(src)
    assert "description:" in block, f"description field missing from struct:\n{block}"


def test_new_returns_cell():
    """new() still uses Self::cell to construct the value."""
    src = _src()
    block = _value_impl_block(src)
    assert "Self::cell(SingleModuleReference" in block, (
        "new() doesn't construct SingleModuleReference via Self::cell"
    )
