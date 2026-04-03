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


def _run_ts(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Write a temporary TypeScript file and execute it with npx tsx."""
    test_file = Path(REPO) / "__test_probe.ts"
    test_file.write_text(script)
    try:
        return subprocess.run(
            ["npx", "tsx", str(test_file)],
            cwd=REPO,
            capture_output=True,
            timeout=timeout,
        )
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Environment.ts and its imports must compile without TypeScript errors."""
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
# Fail-to-pass (pr_diff) — behavioral runtime tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_all_methods_exist():
    """All 5 new methods (recordError, recordErrors, hasErrors, aggregateErrors, tryRecord)
    must exist as functions on the Environment class prototype."""
    r = _run_ts("""
import { Environment } from './src/HIR/Environment';
const proto = Environment.prototype as any;
const required = ['recordError', 'recordErrors', 'hasErrors', 'aggregateErrors', 'tryRecord'];
const missing = required.filter(m => typeof proto[m] !== 'function');
if (missing.length > 0) {
    process.stderr.write('Missing methods on Environment: ' + missing.join(', ') + '\\n');
    process.exit(1);
}
process.stdout.write('OK\\n');
""")
    assert r.returncode == 0, (
        f"Environment is missing required methods:\n{r.stderr.decode()}{r.stdout.decode()}"
    )


# [pr_diff] fail_to_pass
def test_errors_field_initialized():
    """Environment class has a private #errors field initialized to new CompilerError()."""
    # AST-only because: # private fields are inaccessible at runtime from outside the class
    src = Path(ENV_FILE).read_text()
    assert re.search(r"#errors\b.*=\s*new\s+CompilerError\s*\(\s*\)", src), (
        "#errors field initialized to new CompilerError() not found in Environment class"
    )


# [pr_diff] fail_to_pass
def test_record_error_throws_invariants():
    """recordError must immediately throw when error category is ErrorCategory.Invariant."""
    # AST-only because: cannot instantiate Environment (complex constructor deps)
    src = Path(ENV_FILE).read_text()
    # Extract a window after recordError definition
    m = re.search(r"recordError\s*\(", src)
    assert m, "recordError method not found"
    window = src[m.start():m.start() + 600]
    assert "ErrorCategory.Invariant" in window, (
        "recordError must check ErrorCategory.Invariant"
    )
    assert "throw" in window, (
        "recordError must throw when error category is Invariant"
    )


# [pr_diff] fail_to_pass
def test_record_errors_processes_details():
    """recordErrors(error: CompilerError) iterates over error details and records each."""
    # AST-only because: cannot instantiate Environment
    src = Path(ENV_FILE).read_text()
    m = re.search(r"recordErrors\s*\(", src)
    assert m, "recordErrors method not found"
    window = src[m.start():m.start() + 400]
    # Must accept CompilerError parameter
    assert "CompilerError" in window, (
        "recordErrors must accept a CompilerError parameter"
    )
    # Must process details (for-of, forEach, or similar iteration)
    assert re.search(r"(\.details|\.diagnostics)", window), (
        "recordErrors must iterate over error details"
    )
    # Must delegate to recordError or push methods
    assert re.search(r"(this\.\s*recordError|pushDiagnostic|pushErrorDetail)", window), (
        "recordErrors must record each detail individually"
    )


# [pr_diff] fail_to_pass
def test_has_errors_method():
    """hasErrors(): boolean delegates to the accumulated errors' hasAnyErrors()."""
    # AST-only because: cannot instantiate Environment
    src = Path(ENV_FILE).read_text()
    m = re.search(r"hasErrors\s*\(\s*\)", src)
    assert m, "hasErrors() method not found"
    window = src[m.start():m.start() + 200]
    assert "boolean" in window, "hasErrors() must return boolean"
    assert "hasAnyErrors" in window, (
        "hasErrors() must delegate to hasAnyErrors()"
    )


# [pr_diff] fail_to_pass
def test_aggregate_errors_method():
    """aggregateErrors(): CompilerError returns the accumulated #errors field."""
    # AST-only because: cannot instantiate Environment
    src = Path(ENV_FILE).read_text()
    m = re.search(r"aggregateErrors\s*\(\s*\)", src)
    assert m, "aggregateErrors() method not found"
    window = src[m.start():m.start() + 200]
    assert "CompilerError" in window, "aggregateErrors() must return CompilerError"
    assert re.search(r"return\s+this\.#errors", window), (
        "aggregateErrors() must return this.#errors"
    )


# [pr_diff] fail_to_pass
def test_try_record_catches_compiler_errors():
    """tryRecord wraps a callback in try/catch; records non-invariant CompilerErrors,
    re-throws non-CompilerError exceptions."""
    # AST-only because: cannot instantiate Environment
    src = Path(ENV_FILE).read_text()
    m = re.search(r"tryRecord\s*\(", src)
    assert m, "tryRecord method not found"
    window = src[m.start():m.start() + 600]
    assert "try" in window and "catch" in window, (
        "tryRecord must use try/catch"
    )
    assert "instanceof CompilerError" in window, (
        "tryRecord must check instanceof CompilerError to distinguish error types"
    )
    # Must re-throw non-CompilerError exceptions (at least one throw besides the invariant re-throw)
    throws = re.findall(r"\bthrow\s+\w+", window)
    assert len(throws) >= 1, (
        "tryRecord must re-throw non-CompilerError exceptions"
    )


# [pr_diff] fail_to_pass
def test_required_imports():
    """CompilerDiagnostic, CompilerErrorDetail, and ErrorCategory must be named imports."""
    # AST-only because: TypeScript import syntax inspection
    src = Path(ENV_FILE).read_text()
    for symbol in ("CompilerDiagnostic", "CompilerErrorDetail", "ErrorCategory"):
        assert re.search(
            rf"import\s*\{{[^}}]*\b{symbol}\b[^}}]*\}}\s*from", src
        ), f"{symbol} must be a named import from CompilerError"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — compiler/CLAUDE.md:232-245
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — compiler/CLAUDE.md:232-245 @ 0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
def test_invariant_check_in_both_methods():
    """Invariant errors are hard failures (compiler/CLAUDE.md:232-245) and must never
    be silently accumulated. Both recordError and tryRecord must check for Invariant."""
    # AST-only because: cannot instantiate Environment
    src = Path(ENV_FILE).read_text()

    # Check recordError body for Invariant handling
    re_match = re.search(r"recordError\s*\(", src)
    assert re_match, "recordError method not found"
    re_window = src[re_match.start():re_match.start() + 600]
    assert "ErrorCategory.Invariant" in re_window, (
        "recordError must check ErrorCategory.Invariant"
    )

    # Check tryRecord body for Invariant handling
    tr_match = re.search(r"tryRecord\s*\(", src)
    assert tr_match, "tryRecord method not found"
    tr_window = src[tr_match.start():tr_match.start() + 600]
    assert "ErrorCategory.Invariant" in tr_window, (
        "tryRecord must check ErrorCategory.Invariant"
    )


# [agent_config] fail_to_pass — compiler/CLAUDE.md:232-245 @ 0dbb43bc57d27a79ecf4c78508089a36bd08ef5d
def test_private_field_uses_hash_prefix():
    """Private error field must use TypeScript # prefix (not underscore _ convention).
    Per compiler/CLAUDE.md:232-245 on error handling patterns."""
    # AST-only because: # private field syntax is a source-level check
    src = Path(ENV_FILE).read_text()
    assert "#errors" in src, (
        "Private error field must use # prefix (e.g. #errors)"
    )
    assert not re.search(r"\b_errors\s*[:=]", src), (
        "Must use TypeScript # private field syntax, not _errors convention"
    )
