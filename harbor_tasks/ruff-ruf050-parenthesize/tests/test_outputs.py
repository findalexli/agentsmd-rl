"""
Task: ruff-ruf050-parenthesize
Repo: astral-sh/ruff @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
PR:   24234

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/ruff"
RUST_FILE = Path(f"{REPO}/crates/ruff_linter/src/rules/ruff/rules/unnecessary_if.rs")
FIXTURE = Path(f"{REPO}/crates/ruff_linter/resources/test/fixtures/ruff/RUF050.py")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fixture_has_multiline_expression():
    """Fixture file includes a multiline arithmetic expression test case."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = FIXTURE.read_text()
    # The PR adds a multiline if-condition with an operator across lines:
    #   if (\n    id(0)\n    + 0\n):\n    pass
    # Check for any multiline if with an arithmetic/bitwise operator on a continuation line
    assert re.search(
        r"if\s*\(\s*\n\s+\S.*\n\s+[+\-*|&^]", source
    ), "Fixture must include a multiline expression if-condition with operator across lines"


# [pr_diff] fail_to_pass
def test_fixture_has_multiline_call():
    """Fixture file includes a multiline function call test case."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = FIXTURE.read_text()
    # The PR adds a multiline function call case:
    #   if foo(\n    1,\n    2,\n):\n    pass
    # Check for a multiline if with a function call spanning lines
    assert re.search(
        r"if\s+\w+\(\s*\n\s+\d", source
    ), "Fixture must include a multiline function call if-condition"


# [pr_diff] fail_to_pass
def test_replacement_handles_multiline():
    """Replacement logic handles multiline expressions, not just walrus operators."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    # On the base commit, the ONLY conditional parenthesization is for walrus
    # operators (is_named_expr). A valid fix must add parenthesization logic
    # for multiline expressions too — via a helper function, additional
    # conditions, or using existing APIs like parenthesized_range.
    has_named_expr = "is_named_expr" in source
    additional_indicators = [
        "parenthesized_range",       # reuses existing API for paren extraction
        "has_top_level_line_break",   # gold solution's detection function
        "condition_as_expression",    # gold solution's helper function
        "line_break",                 # general line break detection variable/function
        "multiline",                  # multiline detection
        "multi_line",                 # alternative naming
        "needs_parens",              # alternative naming for paren check
        "spans_multiple",            # alternative detection
    ]
    has_multiline_logic = any(ind in source for ind in additional_indicators)

    assert has_named_expr and has_multiline_logic, (
        "Parenthesization logic must handle both walrus operators AND multiline "
        "expressions. Found is_named_expr=%s, multiline_logic=%s. "
        "The fix needs additional logic (e.g., line break detection, "
        "parenthesized_range) beyond the base commit's walrus-only handling."
        % (has_named_expr, has_multiline_logic)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_walrus_still_parenthesized():
    """Walrus operator (named expression) still gets parenthesized."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    assert "is_named_expr" in source, (
        "Walrus operator handling (is_named_expr) must be preserved"
    )
    # The format string wrapping in parens must still exist
    assert re.search(r'format!\s*\(\s*"?\(\{', source), (
        "Parenthesization format string must still exist for walrus expressions"
    )


# [static] pass_to_pass
def test_core_ruf050_logic_intact():
    """Core RUF050 rule logic is preserved (not stubbed out)."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    required = ["unnecessary_if", "StmtIf", "has_side_effects", "Edit", "Fix"]
    missing = [r for r in required if r not in source]
    assert not missing, f"Core symbols missing from unnecessary_if.rs: {missing}"
    assert len(source.splitlines()) >= 80, (
        f"File has only {len(source.splitlines())} lines — looks like a stub"
    )


# [static] pass_to_pass
def test_fixture_retains_existing_cases():
    """Fixture file retains existing RUF050 test cases (walrus, basic calls)."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = FIXTURE.read_text()
    assert "x := " in source, "Fixture must retain walrus operator test cases"
    assert "foo()" in source, "Fixture must retain basic function call test cases"
    assert "pass" in source, "Fixture must retain pass statements in if bodies"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
def test_no_panic_unwrap():
    """Avoid panic!, unreachable!, .unwrap() per AGENTS.md guidelines."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for pattern in ["panic!(", ".unwrap()", "unreachable!("]:
            if pattern in stripped:
                violations.append(f"  Line {i}: {stripped[:80]}")
    assert len(violations) <= 3, (
        f"Too many panic!/unwrap()/unreachable! in unnecessary_if.rs:\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — AGENTS.md:76 @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
def test_no_function_local_imports():
    """Rust imports should always go at the top of the file, never locally in functions."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    in_fn = False
    brace_depth = 0
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if re.match(r"(pub(\(crate\))?\s+)?fn\s+\w+", stripped):
            in_fn = True
        if in_fn:
            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth <= 0:
                in_fn = False
                brace_depth = 0
            elif stripped.startswith("use ") and not stripped.startswith("// use"):
                violations.append(f"  Line {i}: {stripped[:80]}")
    assert not violations, (
        f"Function-local imports found in unnecessary_if.rs "
        f"(AGENTS.md:76 says imports must be at top of file):\n"
        + "\n".join(violations)
    )
