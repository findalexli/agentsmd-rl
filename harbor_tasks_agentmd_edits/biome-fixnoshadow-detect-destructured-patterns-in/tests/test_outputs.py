"""
Task: biome-fixnoshadow-detect-destructured-patterns-in
Repo: biomejs/biome @ 4509fc654f90cc007689c9e46bc3d172016ae039
PR:   9344

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/biome"
NO_SHADOW = Path(REPO) / "crates/biome_js_analyze/src/lint/nursery/no_shadow.rs"
SPEC_DIR = Path(REPO) / "crates/biome_js_analyze/tests/specs/nursery/noShadow"
SKILL_MD = Path(REPO) / ".claude/skills/testing-codegen/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_shadow_structure_preserved():
    """Core functions in no_shadow.rs are preserved."""
    content = NO_SHADOW.read_text()
    assert "fn is_declaration" in content, "is_declaration function missing"
    assert "fn is_on_initializer" in content, "is_on_initializer function missing"
    assert "fn is_inside_type_parameter" in content, "is_inside_type_parameter function missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_declaration_handles_destructuring():
    """is_declaration must use the declaration() API to walk through destructuring patterns.

    On the base commit, is_declaration uses parent::<JsVariableDeclarator>() which
    only works for direct variable bindings, not bindings inside destructuring.
    The fix uses binding.tree().declaration() + parent_binding_pattern_declaration()
    to properly resolve through destructuring patterns.
    """
    content = NO_SHADOW.read_text()
    # Extract the is_declaration function body (from fn signature to next fn or EOF)
    match = re.search(
        r'fn is_declaration\b.*?\{(.*?)(?=\nfn |\Z)',
        content,
        re.DOTALL,
    )
    assert match, "Could not find is_declaration function"
    fn_body = match.group(1)

    # The fix must use .declaration() to get the binding declaration
    assert ".declaration()" in fn_body, (
        "is_declaration must use .declaration() API to handle destructuring patterns"
    )
    # The fix must use parent_binding_pattern_declaration to unwrap through patterns
    assert "parent_binding_pattern_declaration" in fn_body, (
        "is_declaration must use parent_binding_pattern_declaration() "
        "to resolve bindings inside destructuring"
    )


# [pr_diff] fail_to_pass
def test_is_on_initializer_handles_destructuring():
    """is_on_initializer must handle destructuring patterns via declaration() API.

    On the base commit, is_on_initializer directly calls parent::<JsVariableDeclarator>()
    which doesn't work for destructured bindings. The fix uses declaration() +
    parent_binding_pattern_declaration().
    """
    content = NO_SHADOW.read_text()
    match = re.search(
        r'fn is_on_initializer\b.*?\{(.*?)(?=\nfn |\Z)',
        content,
        re.DOTALL,
    )
    assert match, "Could not find is_on_initializer function"
    fn_body = match.group(1)

    assert "parent_binding_pattern_declaration" in fn_body, (
        "is_on_initializer must use parent_binding_pattern_declaration() "
        "to handle destructured bindings"
    )


# [pr_diff] fail_to_pass
def test_imports_binding_declaration_type():
    """no_shadow.rs must import AnyJsBindingDeclaration for destructuring support.

    The fix replaces direct JsVariableDeclarator parent lookups with
    AnyJsBindingDeclaration pattern matching. This type must be imported.
    """
    content = NO_SHADOW.read_text()
    assert "AnyJsBindingDeclaration" in content, (
        "no_shadow.rs must import AnyJsBindingDeclaration "
        "to match against destructuring declaration types"
    )


# [pr_diff] fail_to_pass

    The noShadow rule now detects shadowing in destructuring patterns, so
    there must be test cases covering object, array, nested, and rest patterns.
    """
    spec_file = SPEC_DIR / "invalidDestructuring.js"
    assert spec_file.exists(), (
        "invalidDestructuring.js test spec must exist in noShadow test directory"
    )
    content = spec_file.read_text()

    # Must have the diagnostic expectation comment
    assert "should generate diagnostics" in content, (
        "invalidDestructuring.js must declare 'should generate diagnostics'"
    )
    # Must test object destructuring
    assert "const {" in content or "const{" in content, (
        "Must include object destructuring shadow test case"
    )
    # Must test array destructuring
    assert "const [" in content or "const[" in content, (
        "Must include array destructuring shadow test case"
    )
    # Must have multiple test cases (at least 3 functions)
    functions = re.findall(r'function \w+', content)
    assert len(functions) >= 3, (
        f"Expected at least 3 test functions, found {len(functions)}"
    )


# [pr_diff] fail_to_pass

    Destructuring in sibling scopes should NOT trigger noShadow. There must be
    test cases verifying this (the original bug was false positives here).
    """
    spec_file = SPEC_DIR / "validDestructuring.js"
    assert spec_file.exists(), (
        "validDestructuring.js test spec must exist in noShadow test directory"
    )
    content = spec_file.read_text()

    # Must have the no-diagnostic expectation comment
    assert "should not generate diagnostics" in content, (
        "validDestructuring.js must declare 'should not generate diagnostics'"
    )
    # Must include destructuring patterns
    assert "const {" in content or "const{" in content, (
        "Must include object destructuring in sibling scope test"
    )
    assert "const [" in content or "const[" in content, (
        "Must include array destructuring in sibling scope test"
    )
    # Must have multiple test functions
    functions = re.findall(r'function \w+', content)
    assert len(functions) >= 3, (
        f"Expected at least 3 test functions, found {len(functions)}"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — SKILL.md documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    The testing-codegen skill must explain that files/folders with 'valid' in the
    name produce no diagnostics and files with 'invalid' produce diagnostics.
    This is critical for agents writing tests — without this guidance they may
    name test files incorrectly.
    """
    content = SKILL_MD.read_text()
    content_lower = content.lower()

    # Must document the naming convention (not just use the words in examples)
    assert "naming convention" in content_lower or "file and folder naming" in content_lower, (
        "SKILL.md must have a section about file/folder naming conventions"
    )
    # Must explain what valid means (no diagnostics)
    assert "no diagnostics" in content_lower, (
        "SKILL.md must explain that 'valid' files produce no diagnostics"
    )
    # Must explain what invalid means (diagnostics)
    assert re.search(r'invalid.*diagnostics|diagnostics.*invalid', content_lower), (
        "SKILL.md must explain that 'invalid' files produce diagnostics"
    )


# [config_edit] fail_to_pass

    When testing multiple cases in folders, names should be prefixed with
    valid/invalid (e.g. validResolutionReact, invalidResolutionReact).
    """
    content = SKILL_MD.read_text()

    # Must show folder prefix convention examples
    has_prefix_example = (
        "validResolution" in content
        or "invalidResolution" in content
        or re.search(r'valid[A-Z]\w+/', content) is not None
        or "prefix" in content.lower()
    )
    assert has_prefix_example, (
        "SKILL.md must document folder naming with valid/invalid prefix convention"
    )

    # Must mention folder naming explicitly
    content_lower = content.lower()
    assert "folder" in content_lower and ("naming" in content_lower or "convention" in content_lower or "prefix" in content_lower), (
        "SKILL.md must explicitly discuss folder naming conventions"
    )
