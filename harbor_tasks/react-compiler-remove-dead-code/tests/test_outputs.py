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

import re
from pathlib import Path

REPO = "/workspace/react/compiler/packages/babel-plugin-react-compiler"
SRC = Path(REPO) / "src"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_validate_file_deleted():
    """ValidateNoUntransformedReferences.ts must be deleted (unused validation pass)."""
    dead_file = SRC / "Entrypoint" / "ValidateNoUntransformedReferences.ts"
    assert not dead_file.exists(), (
        "ValidateNoUntransformedReferences.ts still exists but should be deleted"
    )


# [pr_diff] fail_to_pass
def test_validate_not_imported():
    """BabelPlugin.ts must not import or call validateNoUntransformedReferences."""
    babel_plugin = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert "ValidateNoUntransformedReferences" not in babel_plugin, (
        "BabelPlugin.ts still references ValidateNoUntransformedReferences"
    )
    assert "validateNoUntransformedReferences" not in babel_plugin, (
        "BabelPlugin.ts still references validateNoUntransformedReferences"
    )


# [pr_diff] fail_to_pass
def test_compile_program_metadata_removed():
    """CompileProgramMetadata type must be removed from Program.ts."""
    program_ts = (SRC / "Entrypoint" / "Program.ts").read_text()
    assert "CompileProgramMetadata" not in program_ts, (
        "CompileProgramMetadata type is still present in Program.ts"
    )


# [pr_diff] fail_to_pass
def test_compile_program_returns_void():
    """compileProgram must return void, not CompileProgramMetadata | null."""
    program_ts = (SRC / "Entrypoint" / "Program.ts").read_text()
    # The function signature should have ): void { not ): SomeType {
    # Find the compileProgram function signature
    assert "CompileProgramMetadata" not in program_ts, (
        "compileProgram still references CompileProgramMetadata return type"
    )
    # The function should not return an object with retryErrors
    assert "retryErrors: programContext.retryErrors" not in program_ts, (
        "compileProgram still returns retryErrors object"
    )


# [pr_diff] fail_to_pass
def test_retry_errors_field_removed():
    """retryErrors field must be removed from ProgramContext in Imports.ts."""
    imports_ts = (SRC / "Entrypoint" / "Imports.ts").read_text()
    assert "retryErrors" not in imports_ts, (
        "retryErrors is still referenced in Imports.ts"
    )


# [pr_diff] fail_to_pass
def test_babel_fn_import_removed():
    """BabelFn must no longer be imported in Imports.ts (was only used by retryErrors)."""
    imports_ts = (SRC / "Entrypoint" / "Imports.ts").read_text()
    # Check that BabelFn is not imported from Program
    program_import_lines = [
        line for line in imports_ts.splitlines()
        if "from" in line and "Program" in line
    ]
    for line in program_import_lines:
        assert "BabelFn" not in line, (
            f"BabelFn is still imported from Program in Imports.ts: {line.strip()}"
        )


# [pr_diff] fail_to_pass
def test_client_no_memo_removed_options():
    """'client-no-memo' enum value must be removed from CompilerOutputModeSchema."""
    options_ts = (SRC / "Entrypoint" / "Options.ts").read_text()
    assert "client-no-memo" not in options_ts, (
        "'client-no-memo' option is still present in Options.ts"
    )


# [pr_diff] fail_to_pass
def test_client_no_memo_removed_environment():
    """'client-no-memo' case must be removed from Environment.ts switch statements."""
    env_ts = (SRC / "HIR" / "Environment.ts").read_text()
    assert "client-no-memo" not in env_ts, (
        "'client-no-memo' case is still present in Environment.ts"
    )


# [pr_diff] fail_to_pass
def test_compile_result_not_captured():
    """BabelPlugin.ts must not capture the return value of compileProgram."""
    babel_plugin = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    # Should not have "const result = compileProgram" or similar
    assert not re.search(
        r"(const|let|var)\s+\w+\s*=\s*compileProgram\s*\(", babel_plugin
    ), (
        "BabelPlugin.ts still captures the return value of compileProgram"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — files intact, not accidentally deleted or hollowed
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_core_files_intact():
    """Key source files still exist and contain their essential content."""
    # BabelPlugin.ts must still call compileProgram
    babel = (SRC / "Babel" / "BabelPlugin.ts").read_text()
    assert "compileProgram(" in babel, (
        "BabelPlugin.ts is missing compileProgram call"
    )
    assert "BabelPluginReactCompiler" in babel, (
        "BabelPlugin.ts is missing BabelPluginReactCompiler export"
    )

    # Program.ts must still export compileProgram
    program = (SRC / "Entrypoint" / "Program.ts").read_text()
    assert "export function compileProgram" in program, (
        "Program.ts is missing compileProgram export"
    )

    # Imports.ts must still have ProgramContext class
    imports = (SRC / "Entrypoint" / "Imports.ts").read_text()
    assert "class ProgramContext" in imports, (
        "Imports.ts is missing ProgramContext class"
    )

    # Options.ts must still have CompilerOutputModeSchema with valid modes
    options = (SRC / "Entrypoint" / "Options.ts").read_text()
    assert "'client'" in options, "Options.ts is missing 'client' mode"
    assert "'ssr'" in options, "Options.ts is missing 'ssr' mode"

    # Environment.ts must still have the Environment class
    env = (SRC / "HIR" / "Environment.ts").read_text()
    assert "class Environment" in env, (
        "Environment.ts is missing Environment class"
    )
