"""
Task: ruff-ruf050-parenthesize
Repo: astral-sh/ruff @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
PR:   24234

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
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
    # Parse the fixture with Python's AST and look for an if-statement whose
    # test is a BinOp (e.g. id(0) + 0).  The base fixture has BoolOps (and/or)
    # and bare Calls but no arithmetic BinOps in if-conditions.
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys

tree = ast.parse(open(sys.argv[1]).read())
found = any(
    isinstance(n, ast.If) and isinstance(n.test, ast.BinOp)
    for n in ast.walk(tree)
)
if not found:
    print("FAIL: No if-statement with BinOp condition in fixture")
    sys.exit(1)
print("PASS")
""", str(FIXTURE)],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_fixture_has_multiline_call():
    """Fixture file includes a multiline function call test case."""
    # Parse the fixture with Python's AST and look for an if-statement whose
    # test is a bare Call with >=2 integer constant arguments (e.g. foo(1, 2)).
    # The base fixture only has zero-arg calls like foo() in if-conditions.
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys

tree = ast.parse(open(sys.argv[1]).read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.If) and isinstance(node.test, ast.Call):
        call = node.test
        if (isinstance(call.func, ast.Name)
            and len(call.args) >= 2
            and all(isinstance(a, ast.Constant) and isinstance(a.value, int)
                    for a in call.args)):
            found = True
            break

if not found:
    print("FAIL: No if-statement with Call(name, [int, int, ...]) in fixture")
    sys.exit(1)
print("PASS")
""", str(FIXTURE)],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_replacement_handles_multiline():
    """Replacement logic handles multiline expressions, not just walrus operators."""
    # On the base commit the ONLY parenthesization check is is_named_expr().
    # A valid fix must add additional logic for multiline expressions — via
    # helper functions, parenthesized_range, line break detection, etc.
    r = subprocess.run(
        ["python3", "-c", """
import sys

source = open(sys.argv[1]).read()

has_named_expr = 'is_named_expr' in source
indicators = [
    'parenthesized_range', 'has_top_level_line_break',
    'condition_as_expression', 'line_break', 'multiline',
    'multi_line', 'needs_parens', 'spans_multiple', 'nesting',
]
found = [i for i in indicators if i in source]

if not has_named_expr:
    print("FAIL: is_named_expr removed (walrus handling broken)")
    sys.exit(1)
if not found:
    print("FAIL: No multiline handling beyond is_named_expr")
    sys.exit(1)
print("PASS: multiline indicators: " + str(found))
""", str(RUST_FILE)],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


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


# [agent_config] pass_to_pass — AGENTS.md:81 @ c8214d1c3b3ac051d23c03738ddb3a8e8b8e6a1e
def test_no_allow_prefer_expect():
    """Use #[expect()] instead of #[allow()] for Clippy lint suppression."""
    # AST-only because: Rust project, no cargo toolchain in test container
    source = RUST_FILE.read_text()
    violations = []
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # Check for #[allow(clippy:: — these should be #[expect(clippy:: instead
        if re.search(r"#\[allow\(clippy::", stripped):
            violations.append(f"  Line {i}: {stripped[:80]}")
    assert not violations, (
        f"Found #[allow(clippy::...)] in unnecessary_if.rs — "
        f"AGENTS.md:81 says prefer #[expect()] over #[allow()] for Clippy lints:\n"
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
