"""
Task: react-compiler-remove-dead-code
Repo: facebook/react @ ab18f33d46171ed1963ae1ac955c5110bb1eb199
PR:   35827

Dead-code removal in the React Compiler: delete ValidateNoUntransformedReferences,
remove CompileProgramMetadata type, strip retryErrors from ProgramContext, remove
client-no-memo output mode, and make compileProgram return void.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react/compiler/packages/babel-plugin-react-compiler"
SRC = Path(REPO) / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_build():
    """TypeScript compilation must succeed after changes."""
    r = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"TypeScript build failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_no_untransformed_references_deleted():
    """ValidateNoUntransformedReferences.ts must be deleted (unused pass)."""
    dead_file = SRC / "Entrypoint" / "ValidateNoUntransformedReferences.ts"
    assert not dead_file.exists(), (
        "ValidateNoUntransformedReferences.ts still exists but should be deleted"
    )


# [pr_diff] fail_to_pass
def test_validate_no_untransformed_references_not_imported():
    """BabelPlugin.ts must not import the deleted validateNoUntransformedReferences."""
    babel_plugin = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert "validateNoUntransformedReferences" not in babel_plugin, (
        "BabelPlugin.ts still imports validateNoUntransformedReferences"
    )


# [pr_diff] fail_to_pass
def test_compile_program_metadata_type_removed():
    """CompileProgramMetadata type must be removed from Program.ts."""
    program_ts = (SRC / "Entrypoint" / "Program.ts").read_text()
    assert "export type CompileProgramMetadata" not in program_ts, (
        "CompileProgramMetadata type is still exported from Program.ts"
    )


# [pr_diff] fail_to_pass
def test_compile_program_returns_void():
    """compileProgram must return void, not CompileProgramMetadata | null."""
    program_ts = (SRC / "Entrypoint" / "Program.ts").read_text()
    assert "): CompileProgramMetadata | null" not in program_ts, (
        "compileProgram still has CompileProgramMetadata | null return type"
    )


# [pr_diff] fail_to_pass
def test_retry_errors_field_removed():
    """retryErrors field must be removed from ProgramContext in Imports.ts."""
    imports_ts = (SRC / "Entrypoint" / "Imports.ts").read_text()
    assert "retryErrors: Array" not in imports_ts, (
        "retryErrors field is still present in ProgramContext (Imports.ts)"
    )


# [pr_diff] fail_to_pass
def test_client_no_memo_removed_from_options():
    """'client-no-memo' enum value must be removed from CompilerOutputModeSchema."""
    options_ts = (SRC / "Entrypoint" / "Options.ts").read_text()
    assert "'client-no-memo'" not in options_ts, (
        "'client-no-memo' option is still present in Options.ts"
    )


# [pr_diff] fail_to_pass
def test_client_no_memo_removed_from_environment():
    """'client-no-memo' case must be removed from Environment.ts switch statements."""
    env_ts = (SRC / "HIR" / "Environment.ts").read_text()
    assert "'client-no-memo'" not in env_ts, (
        "'client-no-memo' case is still present in Environment.ts"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_compiler_tests_pass():
    """Upstream compiler test suite still passes after dead code removal."""
    r = subprocess.run(
        ["npm", "test"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Compiler tests failed:\n{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )
