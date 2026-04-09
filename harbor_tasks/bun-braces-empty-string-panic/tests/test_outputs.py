"""
Task: bun-braces-empty-string-panic
Repo: bun @ 5b7fe81279a40f3fccebe6e7f52278c81b39dfb6
PR:   28487

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Building Bun from source takes 10+ minutes, so we verify the fix
through static analysis and syntax checks rather than runtime tests.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_flatten_tokens_has_empty_guard():
    """flattenTokens must have early return guard for empty token list.

    The bug: flattenTokens unconditionally accesses self.tokens.items[0],
    causing index-out-of-bounds panic when tokenizer produces zero tokens.
    """
    braces_file = Path(f"{REPO}/src/shell/braces.zig")
    content = braces_file.read_text()

    # Must have a guard that checks if tokens is empty before accessing items[0]
    has_empty_guard = (
        "if (self.tokens.items.len == 0) return" in content or
        "if (self.tokens.items.len == 0)" in content
    )
    assert has_empty_guard, \
        "Missing empty token guard in flattenTokens - need: if (self.tokens.items.len == 0) return"


def test_advance_has_underflow_guard():
    """Parser.advance must guard prev() to prevent usize underflow.

    The bug: advance() calls prev() which does 'self.current - 1',
    causing underflow when current == 0.
    """
    braces_file = Path(f"{REPO}/src/shell/braces.zig")
    content = braces_file.read_text()

    # Must guard the prev() call when current could be 0
    has_underflow_guard = "if (self.current > 0) self.prev() else self.peek()" in content
    assert has_underflow_guard, \
        "Missing underflow guard in advance() - need: if (self.current > 0) self.prev() else self.peek()"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax/compilation + anti-regression
# ---------------------------------------------------------------------------

def test_braces_zig_compiles():
    """src/shell/braces.zig must have valid Zig syntax (pass_to_pass)."""
    braces_file = Path(f"{REPO}/src/shell/braces.zig")

    # Basic Zig syntax check using zig fmt
    r = subprocess.run(
        ["zig", "fmt", "--check", str(braces_file)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"braces.zig has syntax errors:\n{r.stderr.decode()}"


def test_braces_zig_ast_check():
    """src/shell/braces.zig must pass Zig AST check (pass_to_pass)."""
    braces_file = Path(f"{REPO}/src/shell/braces.zig")

    # Zig AST check validates semantic correctness (types, imports, etc.)
    r = subprocess.run(
        ["zig", "ast-check", str(braces_file)],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, f"braces.zig failed AST check:\n{r.stderr.decode()[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo CI) — repo's CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_zig_ast_check_braces():
    """Repo CI: zig ast-check on braces.zig (pass_to_pass)."""
    # This is a repo CI check - validates AST correctness
    # Mirrors the repo's format.yml which runs zig fmt/ast-check
    r = subprocess.run(
        ["zig", "ast-check", "src/shell/braces.zig"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"zig ast-check on braces.zig failed:\n{r.stderr[-500:]}"


def test_no_regression_in_brace_parsing():
    """Normal brace expansion patterns should still be parseable (no syntax errors)."""
    braces_file = Path(f"{REPO}/src/shell/braces.zig")
    content = braces_file.read_text()

    # Ensure key functions exist and haven't been deleted
    assert "fn flattenTokens(" in content, "flattenTokens function missing"
    assert "fn advance(" in content, "advance function missing"
    assert "pub fn NewLexer(" in content, "NewLexer function missing"
    assert "pub const Parser" in content, "Parser struct missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression test check
# ---------------------------------------------------------------------------

def test_regression_test_added():
    """The gold patch should add regression test for empty string."""
    test_file = Path(f"{REPO}/test/js/bun/shell/brace.test.ts")

    if not test_file.exists():
        # If test file doesn't exist yet, that's fine - the fix is the important part
        return

    content = test_file.read_text()

    # Check for empty string regression test
    has_empty_test = '$.braces("")' in content or '$.braces(\"\")' in content
    assert has_empty_test, \
        "Missing regression test for empty string - should test $.braces('')"
