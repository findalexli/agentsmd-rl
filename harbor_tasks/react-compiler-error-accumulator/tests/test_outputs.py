"""
Task: react-compiler-error-accumulator
Repo: facebook/react @ 0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
PR:   35873

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react/compiler/packages/babel-plugin-react-compiler"
ENV_FILE = f"{REPO}/src/HIR/Environment.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — TypeScript compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Environment.ts and its imports must compile without TypeScript errors."""
    # AST-only because: TypeScript cannot be imported directly in Python;
    # tsc --noEmit is the authoritative check for type correctness
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_errors_field_initialized():
    """Environment class must have a private #errors field initialized to a new CompilerError."""
    # AST-only because: TypeScript class with complex BabelScope/constructor deps
    # cannot be instantiated in Python without the full Babel environment
    src = Path(ENV_FILE).read_text()
    # Match either typed or inferred: `#errors: CompilerError = new CompilerError()` or `#errors = new CompilerError()`
    assert re.search(r"#errors\b.*=\s*new CompilerError\(\)", src), (
        "#errors field initialized to new CompilerError() not found"
    )


# [pr_diff] fail_to_pass
def test_record_error_method_signature():
    """recordError must accept CompilerDiagnostic | CompilerErrorDetail and return void."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert re.search(
        r"recordError\s*\(\s*error\s*:\s*CompilerDiagnostic\s*\|\s*CompilerErrorDetail\s*\)\s*:\s*void",
        src,
    ), "recordError(error: CompilerDiagnostic | CompilerErrorDetail): void not found"


# [pr_diff] fail_to_pass
def test_record_error_throws_invariants():
    """recordError must throw immediately when error category is Invariant."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    # Verify the Invariant check is present (not just anywhere — in a throw context)
    assert re.search(r"ErrorCategory\.Invariant", src), (
        "recordError must check ErrorCategory.Invariant and throw"
    )
    # Verify a throw follows the Invariant check
    assert re.search(r"ErrorCategory\.Invariant[\s\S]{0,200}throw ", src), (
        "recordError must throw when error is ErrorCategory.Invariant"
    )


# [pr_diff] fail_to_pass
def test_record_errors_iterates_details():
    """recordErrors must iterate over error.details and record each one."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert re.search(r"recordErrors\s*\(\s*error\s*:\s*CompilerError\s*\)\s*:\s*void", src), (
        "recordErrors(error: CompilerError): void not found"
    )
    assert re.search(r"for\s*\(.*error\.details", src), (
        "recordErrors must iterate over error.details with a for loop"
    )


# [pr_diff] fail_to_pass
def test_has_errors_method():
    """hasErrors() must return boolean, delegating to #errors.hasAnyErrors()."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert re.search(r"hasErrors\s*\(\s*\)\s*:\s*boolean", src), (
        "hasErrors(): boolean not found"
    )
    assert "hasAnyErrors" in src, (
        "hasErrors() must call this.#errors.hasAnyErrors()"
    )


# [pr_diff] fail_to_pass
def test_aggregate_errors_method():
    """aggregateErrors() must return CompilerError (the accumulated #errors field)."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert re.search(r"aggregateErrors\s*\(\s*\)\s*:\s*CompilerError", src), (
        "aggregateErrors(): CompilerError not found"
    )
    # Must return the #errors field
    assert re.search(r"aggregateErrors[\s\S]{0,150}return\s+this\.#errors", src), (
        "aggregateErrors() must return this.#errors"
    )


# [pr_diff] fail_to_pass
def test_try_record_method_signature():
    """tryRecord must accept a void callback and return void."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert re.search(r"tryRecord\s*\(\s*fn\s*:\s*\(\s*\)\s*=>\s*void\s*\)\s*:\s*void", src), (
        "tryRecord(fn: () => void): void not found"
    )


# [pr_diff] fail_to_pass
def test_try_record_rethrows_non_compiler_errors():
    """tryRecord must re-throw exceptions that are not CompilerError instances."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    # Must check instanceof CompilerError before deciding to record vs rethrow
    assert re.search(r"instanceof\s+CompilerError", src), (
        "tryRecord must check instanceof CompilerError to distinguish error types"
    )
    # Must re-throw (throw err / throw error) for non-CompilerError exceptions
    assert re.search(r"else\s*\{[\s\S]{0,50}throw\s+\w+", src), (
        "tryRecord must re-throw non-CompilerError exceptions"
    )


# [pr_diff] fail_to_pass
def test_required_imports():
    """CompilerDiagnostic, CompilerErrorDetail, and ErrorCategory must be imported."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    for symbol in ("CompilerDiagnostic", "CompilerErrorDetail", "ErrorCategory"):
        assert symbol in src, f"{symbol} must be imported from CompilerError"
    # Must be explicit named import (not wildcard)
    assert re.search(
        r"import\s*\{[^}]*CompilerDiagnostic[^}]*\}\s*from", src
    ), "CompilerDiagnostic must be a named import (not wildcard)"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — rules from compiler/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — compiler/CLAUDE.md:232-248 @ 0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
def test_invariant_check_in_both_methods():
    """
    Invariant errors are hard failures and must never be silently accumulated.
    Per compiler/CLAUDE.md:232-248: 'Invariant errors are hard failures indicating
    unexpected/invalid states.'
    Both recordError and tryRecord must explicitly check for and throw Invariant errors.
    """
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    # ErrorCategory.Invariant must appear at least twice: once in recordError, once in tryRecord
    count = len(re.findall(r"ErrorCategory\.Invariant", src))
    assert count >= 2, (
        f"ErrorCategory.Invariant must be checked in both recordError and tryRecord "
        f"(found {count} occurrence(s)); invariants must never be silently accumulated"
    )


# [agent_config] fail_to_pass — compiler/CLAUDE.md:232-248 @ 0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
def test_private_field_uses_hash_prefix():
    """Private error field must use TypeScript # prefix (not underscore _ prefix)."""
    # AST-only because: TypeScript
    src = Path(ENV_FILE).read_text()
    assert "#errors" in src, (
        "Private error accumulation field must use # prefix (e.g. #errors), not _errors"
    )
    # Negatively: no underscore-prefixed private errors field
    assert not re.search(r"\b_errors\s*[:=]", src), (
        "Must use TypeScript # private field syntax, not _errors convention"
    )
