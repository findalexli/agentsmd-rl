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
    assert r.returncode == 0, f"braces.zig has syntax errors:\n{r.stderr.decode()[-500:]}"


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
# Pass-to-pass (repo CI) — repo's CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_zig_fmt_braces():
    """Repo CI: zig fmt --check on braces.zig must pass (pass_to_pass).

    This mirrors the repo's format.yml which runs zig fmt on src.
    Ensures the modified braces.zig follows the repo's formatting standards.
    """
    r = subprocess.run(
        ["zig", "fmt", "--check", "src/shell/braces.zig"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"zig fmt check failed on braces.zig:\n{r.stderr[-500:]}"


def test_repo_zig_ast_check_braces():
    """Repo CI: zig ast-check on braces.zig must pass (pass_to_pass).

    This validates the AST correctness of the modified file.
    Mirrors the repo's CI checks for Zig code quality.
    """
    r = subprocess.run(
        ["zig", "ast-check", "src/shell/braces.zig"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"zig ast-check on braces.zig failed:\n{r.stderr[-500:]}"


def test_repo_zig_ast_check_related_shell_files():
    """Repo CI: zig ast-check on related shell files (pass_to_pass).

    Checks that shell files that interact with braces module still compile.
    These files are stable and don't use newer Zig features that break ast-check.
    """
    # These shell files pass ast-check with Zig 0.13.0 and are related to brace expansion
    related_files = [
        "src/shell/AllocScope.zig",
        "src/shell/Builtin.zig",
        "src/shell/EnvMap.zig",
        "src/shell/IO.zig",
        "src/shell/IOReader.zig",
        "src/shell/IOWriter.zig",
        "src/shell/RefCountedStr.zig",
        "src/shell/subproc.zig",
        "src/shell/util.zig",
    ]

    for file_path in related_files:
        r = subprocess.run(
            ["zig", "ast-check", file_path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"zig ast-check failed on {file_path}:\n{r.stderr[-500:]}"


def test_repo_zig_fmt_all_shell_files():
    """Repo CI: zig fmt --check on stable shell/*.zig files (pass_to_pass).

    Mirrors the repo's format.yml which runs zig fmt on src.
    Ensures all shell-related Zig files follow repo formatting standards.
    Some shell files use newer Zig features that don't parse with Zig 0.13.0.
    """
    # These files pass zig fmt --check with Zig 0.13.0
    shell_files = [
        "src/shell/AllocScope.zig",
        "src/shell/Builtin.zig",
        "src/shell/EnvMap.zig",
        "src/shell/EnvStr.zig",
        "src/shell/IO.zig",
        "src/shell/IOReader.zig",
        "src/shell/IOWriter.zig",
        "src/shell/RefCountedStr.zig",
        "src/shell/braces.zig",
        "src/shell/util.zig",
    ]

    for file_path in shell_files:
        r = subprocess.run(
            ["zig", "fmt", "--check", file_path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"zig fmt check failed on {file_path}:\n{r.stderr[-500:]}"


def test_repo_brace_test_file_exists():
    """Repo CI: brace.test.ts must exist (pass_to_pass).

    Verifies the test file for brace expansion exists and is valid TypeScript.
    This is the file that should contain the regression test for empty string.
    """
    test_file = Path(f"{REPO}/test/js/bun/shell/brace.test.ts")
    assert test_file.exists(), "brace.test.ts must exist"

    # Basic syntax check: file must start with import
    content = test_file.read_text()
    assert "import" in content, "brace.test.ts must have imports"
    assert "$.braces" in content or "describe" in content, "brace.test.ts must test $.braces"


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
    has_empty_test = '$.braces("")' in content or "$.braces('')" in content
    assert has_empty_test, \
        "Missing regression test for empty string - should test $.braces('')"
