"""
Task: ruff-ty-type-checking-scope-field
Repo: ruff @ 4859b00bca95c004d8adb2efe93af4bdf552e110
PR:   24472

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
SCOPE_RS = Path(REPO) / "crates/ty_python_semantic/src/semantic_index/scope.rs"
INDEX_RS = Path(REPO) / "crates/ty_python_semantic/src/semantic_index.rs"
FUNCTION_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/function.rs"
OVERLOADED_RS = (
    Path(REPO)
    / "crates/ty_python_semantic/src/types/infer/builder/post_inference/overloaded_function.rs"
)
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/semantic_index/builder.rs"


def _find_rust_block(source: str, signature: str, max_chars: int = 2000) -> str:
    """Extract a Rust function/method body starting at the given signature."""
    start = source.find(signature)
    assert start != -1, f"Could not find '{signature}' in source"
    return source[start : start + max_chars]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate compiles after the refactoring."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scope_field_removed():
    """Scope struct must not contain an in_type_checking_block field."""
    source = SCOPE_RS.read_text()
    struct_start = source.find("pub(crate) struct Scope")
    assert struct_start != -1, "Scope struct not found in scope.rs"
    struct_end = source.find("\n}", struct_start)
    struct_body = source[struct_start : struct_end + 2]
    assert "in_type_checking_block" not in struct_body, (
        "in_type_checking_block field should be removed from Scope struct"
    )


# [pr_diff] fail_to_pass
def test_scope_getter_removed():
    """Scope should not expose an in_type_checking_block() getter method."""
    source = SCOPE_RS.read_text()
    assert "fn in_type_checking_block" not in source, (
        "in_type_checking_block() getter should be removed from Scope impl"
    )


# [pr_diff] fail_to_pass
def test_type_checking_uses_ancestor_iteration():
    """is_in_type_checking_block should iterate ancestor scopes, not use per-scope flag."""
    source = INDEX_RS.read_text()
    fn_body = _find_rust_block(source, "fn is_in_type_checking_block", max_chars=600)

    # Old pattern must be gone: delegating to Scope::in_type_checking_block()
    assert ".in_type_checking_block()" not in fn_body, (
        "is_in_type_checking_block should not delegate to Scope::in_type_checking_block()"
    )

    # Must still use use_def_map's range check (the core mechanism)
    assert "is_range_in_type_checking_block" in fn_body, (
        "is_in_type_checking_block must still use is_range_in_type_checking_block"
    )

    # Should iterate through multiple scopes (ancestor_scopes, parent chain, etc.)
    uses_iteration = (
        "ancestor_scopes" in fn_body
        or "parent" in fn_body
        or ".any(" in fn_body
        or "for " in fn_body
        or "loop" in fn_body
    )
    assert uses_iteration, (
        "is_in_type_checking_block should iterate parent/ancestor scopes"
    )


# [pr_diff] fail_to_pass
def test_function_callers_updated():
    """function.rs must not call .in_type_checking_block() on scope directly."""
    source = FUNCTION_RS.read_text()
    assert ".in_type_checking_block()" not in source, (
        "function.rs should use is_in_type_checking_block method, "
        "not Scope::in_type_checking_block()"
    )


# [pr_diff] fail_to_pass
def test_overloaded_function_callers_updated():
    """overloaded_function.rs must not call .in_type_checking_block() on scope directly."""
    source = OVERLOADED_RS.read_text()
    assert ".in_type_checking_block()" not in source, (
        "overloaded_function.rs should use index.is_in_type_checking_block, "
        "not Scope::in_type_checking_block()"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub: modified functions have real logic
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_is_in_type_checking_block_not_stub():
    """is_in_type_checking_block must have a real implementation, not a stub."""
    source = INDEX_RS.read_text()
    fn_body = _find_rust_block(source, "fn is_in_type_checking_block", max_chars=600)

    # Must contain the actual range-checking logic
    assert "use_def_map" in fn_body, "Function must use use_def_map (not a stub)"
    assert "is_range_in_type_checking_block" in fn_body, (
        "Function must call is_range_in_type_checking_block (not a stub)"
    )

    # Must not just be an empty body or todo
    assert "todo!()" not in fn_body.lower(), "Function body is a stub (todo!)"
    assert "unimplemented!()" not in fn_body, "Function body is a stub (unimplemented!)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 4859b00bca95c004d8adb2efe93af4bdf552e110
def test_no_panic_unwrap_in_modified():
    """No panic!/unwrap() in is_in_type_checking_block (AGENTS.md:79)."""
    source = INDEX_RS.read_text()
    fn_body = _find_rust_block(source, "fn is_in_type_checking_block", max_chars=600)
    for i, line in enumerate(fn_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, (
            f"panic! in is_in_type_checking_block at line {i}: {stripped}"
        )
        assert ".unwrap()" not in stripped, (
            f".unwrap() in is_in_type_checking_block at line {i}: {stripped}"
        )
        assert "unreachable!(" not in stripped, (
            f"unreachable! in is_in_type_checking_block at line {i}: {stripped}"
        )
