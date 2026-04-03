"""
Task: react-snap-compile-subcommand-docs
Repo: facebook/react @ cd0c4879a2959db91f9bd51a09dafefedd95fb17
PR:   35688

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = Path(REPO) / "compiler" / "packages" / "snap" / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must not have obvious syntax errors."""
    ts_files = [
        SNAP_SRC / "constants.ts",
        SNAP_SRC / "runner.ts",
        SNAP_SRC / "minimize.ts",
        SNAP_SRC / "runner-worker.ts",
        SNAP_SRC / "runner-watch.ts",
    ]
    for f in ts_files:
        content = f.read_text()
        assert len(content) > 100, f"{f.name} is too short or empty"
        # Check balanced braces (rough syntax sanity)
        assert content.count("{") == content.count("}"), (
            f"{f.name} has unbalanced braces"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_constants_renamed_to_babel_plugin():
    """constants.ts must export BABEL_PLUGIN_ROOT and BABEL_PLUGIN_SRC
    instead of using PROJECT_ROOT for the babel-plugin path."""
    src = (SNAP_SRC / "constants.ts").read_text()
    # New exports must exist
    assert "export const BABEL_PLUGIN_ROOT" in src, (
        "constants.ts should export BABEL_PLUGIN_ROOT"
    )
    assert "export const BABEL_PLUGIN_SRC" in src, (
        "constants.ts should export BABEL_PLUGIN_SRC"
    )
    # BABEL_PLUGIN_ROOT should reference 'babel-plugin-react-compiler'
    # Find the definition of BABEL_PLUGIN_ROOT and check it includes the package path
    root_match = re.search(
        r"export const BABEL_PLUGIN_ROOT\s*=.*?;", src, re.DOTALL
    )
    assert root_match, "Could not find BABEL_PLUGIN_ROOT definition"
    assert "babel-plugin-react-compiler" in root_match.group(), (
        "BABEL_PLUGIN_ROOT should reference babel-plugin-react-compiler"
    )


# [pr_diff] fail_to_pass
def test_compile_command_registered():
    """runner.ts must register a 'compile' subcommand via yargs."""
    src = (SNAP_SRC / "runner.ts").read_text()
    # The compile command must be registered with yargs
    assert re.search(r"\.command\(\s*['\"]compile", src), (
        "runner.ts should register a 'compile' command with yargs"
    )
    # It should have a path positional parameter
    assert "compile <path>" in src or "compile [path]" in src, (
        "compile command should accept a path parameter"
    )


# [pr_diff] fail_to_pass
def test_compile_function_exists():
    """runner.ts must define runCompileCommand with file reading and compilation logic."""
    src = (SNAP_SRC / "runner.ts").read_text()
    assert "runCompileCommand" in src, (
        "runner.ts should define runCompileCommand function"
    )
    # The function should read the file and invoke the compiler
    assert "readFileSync" in src, (
        "runCompileCommand should read the input file"
    )
    assert "transformFromAstSync" in src or "BabelPluginReactCompiler" in src, (
        "runCompileCommand should invoke the React Compiler"
    )


# [pr_diff] fail_to_pass
def test_minimize_positional_path():
    """minimize command should accept path as a positional arg, not --path flag."""
    src = (SNAP_SRC / "runner.ts").read_text()
    # The minimize command should use positional path syntax
    assert re.search(r"['\"]minimize <path>['\"]", src), (
        "minimize command should use positional <path> syntax"
    )


# [pr_diff] fail_to_pass
def test_path_resolution_uses_project_root():
    """minimize and compile should resolve relative paths from PROJECT_ROOT
    (compiler dir), not process.cwd() (snap package dir)."""
    src = (SNAP_SRC / "runner.ts").read_text()
    # Find the path resolution in minimize/compile: should use PROJECT_ROOT
    # The old code used: path.resolve(process.cwd(), opts.path)
    # The new code uses: path.resolve(PROJECT_ROOT, opts.path)
    resolve_calls = re.findall(r"path\.resolve\(([^,]+),\s*opts\.path\)", src)
    assert len(resolve_calls) >= 1, (
        "Should have path.resolve calls for opts.path"
    )
    for call in resolve_calls:
        assert "PROJECT_ROOT" in call, (
            f"Path resolution should use PROJECT_ROOT, not {call.strip()}"
        )


# [pr_diff] fail_to_pass
def test_consumer_files_use_renamed_constants():
    """Files that imported PROJECT_ROOT/PROJECT_SRC should now use
    BABEL_PLUGIN_ROOT/BABEL_PLUGIN_SRC where they mean the babel plugin path."""
    # runner-worker.ts should import BABEL_PLUGIN_SRC, not PROJECT_SRC
    worker_src = (SNAP_SRC / "runner-worker.ts").read_text()
    assert "BABEL_PLUGIN_SRC" in worker_src, (
        "runner-worker.ts should import BABEL_PLUGIN_SRC"
    )
    assert "PROJECT_SRC" not in worker_src, (
        "runner-worker.ts should not reference old PROJECT_SRC"
    )

    # runner-watch.ts should import BABEL_PLUGIN_ROOT, not PROJECT_ROOT
    watch_src = (SNAP_SRC / "runner-watch.ts").read_text()
    assert "BABEL_PLUGIN_ROOT" in watch_src, (
        "runner-watch.ts should import BABEL_PLUGIN_ROOT"
    )

    # minimize.ts should import BABEL_PLUGIN_SRC
    minimize_src = (SNAP_SRC / "minimize.ts").read_text()
    assert "BABEL_PLUGIN_SRC" in minimize_src, (
        "minimize.ts should import BABEL_PLUGIN_SRC"
    )
    assert "PROJECT_SRC" not in minimize_src, (
        "minimize.ts should not reference old PROJECT_SRC"
    )


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
