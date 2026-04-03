"""
Task: react-snap-compile-cmd-path-resolution
Repo: facebook/react @ cd0c4879a2959db91f9bd51a09dafefedd95fb17
PR:   35688

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = f"{REPO}/compiler/packages/snap/src"
CONSTANTS_TS = f"{SNAP_SRC}/constants.ts"
RUNNER_TS = f"{SNAP_SRC}/runner.ts"
MINIMIZE_TS = f"{SNAP_SRC}/minimize.ts"
RUNNER_WATCH_TS = f"{SNAP_SRC}/runner-watch.ts"
RUNNER_WORKER_TS = f"{SNAP_SRC}/runner-worker.ts"
CLAUDE_MD = f"{REPO}/compiler/CLAUDE.md"
DEV_GUIDE = f"{REPO}/compiler/docs/DEVELOPMENT_GUIDE.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must have valid syntax (no unterminated strings, missing brackets, etc.)."""
    ts_files = [CONSTANTS_TS, RUNNER_TS, MINIMIZE_TS, RUNNER_WATCH_TS, RUNNER_WORKER_TS]
    for ts_file in ts_files:
        content = Path(ts_file).read_text()
        # Basic syntax sanity: balanced braces
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, (
            f"{ts_file}: brace mismatch ({opens} opens, {closes} closes)"
        )
        # File must have content
        assert len(content) > 100, f"{ts_file}: file is suspiciously short"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_constants_separation():
    """constants.ts must separate compiler root from babel-plugin-react-compiler path into two distinct constants."""
    content = Path(CONSTANTS_TS).read_text()

    # Must have a constant for the compiler root (two levels up from snap package)
    # This could be PROJECT_ROOT, COMPILER_ROOT, etc.
    # Key: must have path.join(process.cwd(), '..', '..') or equivalent going 2 dirs up
    assert re.search(r"""path\.(join|resolve)\(process\.cwd\(\).*['"]\.\.['"].*['"]\.\.['"]""", content), (
        "constants.ts must define a root constant pointing two directories up from cwd"
    )

    # Must have a separate constant for the babel-plugin-react-compiler path
    # On base commit, PROJECT_ROOT directly pointed to babel-plugin-react-compiler.
    # After fix, there must be a separate constant for it.
    exports = re.findall(r"export\s+const\s+(\w+)\s*=", content)
    assert len(exports) >= 2, "constants.ts must export at least 2 path constants (root + plugin)"

    # babel-plugin-react-compiler must be referenced in a DIFFERENT constant than the root
    root_const = None
    plugin_const = None
    for match in re.finditer(r"export\s+const\s+(\w+)\s*=\s*(.*?)(?:;|\n)", content, re.DOTALL):
        name = match.group(1)
        val = match.group(2)
        if "process.cwd()" in val and "'..'," in val:
            root_const = name
        if "babel-plugin-react-compiler" in val:
            plugin_const = name

    # The plugin path could also be constructed by joining root + 'packages' + 'babel-plugin-react-compiler'
    if plugin_const is None:
        # Check multi-line path.join with the root constant
        assert re.search(
            r"path\.(join|normalize)\(\s*\w+.*babel-plugin-react-compiler", content, re.DOTALL
        ) or re.search(
            r"path\.(join|normalize)\(\s*\w+.*packages.*babel-plugin", content, re.DOTALL
        ), "Must have a constant resolving to the babel-plugin-react-compiler directory"

    assert root_const is not None, (
        "Must export a root constant derived from process.cwd() going up 2 directories"
    )


# [pr_diff] fail_to_pass
def test_compile_command_registered():
    """runner.ts must register a 'compile' subcommand with yargs that takes a path and optional debug flag."""
    content = Path(RUNNER_TS).read_text()

    # Must have compile command registered
    assert re.search(r"""['"]compile\s*<path>['"]""", content) or \
           re.search(r"""['"]compile\b""", content), (
        "runner.ts must register a 'compile' command with yargs"
    )

    # Must have a function that handles compilation
    assert "runCompileCommand" in content or "CompileCommand" in content or \
           re.search(r"async\s+function\s+\w*[Cc]ompile", content), (
        "runner.ts must have a compile command handler function"
    )

    # Compile command must support --debug flag
    assert re.search(r"""['"]debug['"]""", content), (
        "compile command must support a --debug flag"
    )


# [pr_diff] fail_to_pass
def test_minimize_positional_path():
    """minimize command must accept path as a positional argument, not a --path option."""
    content = Path(RUNNER_TS).read_text()

    # Should have 'minimize <path>' (positional syntax)
    assert re.search(r"""['"]minimize\s+<path>['"]""", content), (
        "minimize command must use positional <path> syntax (e.g., 'minimize <path>')"
    )

    # Should NOT have the old --path / -p option pattern for minimize
    # Look specifically in the minimize command builder section
    minimize_section = ""
    in_minimize = False
    brace_depth = 0
    for line in content.split("\n"):
        if "'minimize" in line or '"minimize' in line:
            in_minimize = True
        if in_minimize:
            minimize_section += line + "\n"
            brace_depth += line.count("(") - line.count(")")
            if brace_depth <= 0 and len(minimize_section) > 50:
                break

    # The positional approach uses .positional('path', ...) not .string('path')
    assert "positional" in minimize_section.lower() or "<path>" in minimize_section, (
        "minimize command should use positional path argument"
    )


# [pr_diff] fail_to_pass
def test_path_resolution_not_cwd():
    """Minimize and compile commands must NOT resolve relative paths from process.cwd()."""
    content = Path(RUNNER_TS).read_text()

    # On the base commit, minimize resolves paths with: path.resolve(process.cwd(), opts.path)
    # After fix, it should use a project root constant instead.
    # Check that process.cwd() is NOT used for path resolution in minimize/compile handlers
    # (It's fine in constants.ts for defining the root, but not in runner.ts for resolving input paths)
    path_resolve_calls = re.findall(r"path\.resolve\((.*?)\)", content)
    for call in path_resolve_calls:
        assert "process.cwd()" not in call, (
            "path.resolve should not use process.cwd() directly — "
            "use a project root constant that accounts for the compiler/ directory structure"
        )


# [pr_diff] fail_to_pass
def test_old_project_src_removed():
    """Snap source files must not use the old PROJECT_SRC constant (should be renamed to clarify it's the babel plugin src)."""
    for ts_file in [MINIMIZE_TS, RUNNER_WORKER_TS]:
        content = Path(ts_file).read_text()
        assert "PROJECT_SRC" not in content, (
            f"{Path(ts_file).name} must not use old PROJECT_SRC constant — "
            "rename to clarify it's the babel-plugin-react-compiler dist path"
        )

    # runner-watch.ts must not use PROJECT_ROOT for build/tsconfig operations
    # (those should use the babel plugin root, not the compiler project root)
    watch_content = Path(RUNNER_WATCH_TS).read_text()
    # The build cwd should NOT use the old PROJECT_ROOT that pointed to babel-plugin
    # On base: PROJECT_ROOT pointed to babel-plugin, so {cwd: PROJECT_ROOT} was correct
    # After fix: PROJECT_ROOT points to compiler root, so build must use the new plugin constant
    build_lines = [l for l in watch_content.split("\n") if "cwd:" in l and "build" in watch_content[max(0,watch_content.find(l)-200):watch_content.find(l)+len(l)]]
    # Simpler: just check PROJECT_ROOT is no longer imported from constants in runner-watch
    imports = [l for l in watch_content.split("\n") if "from" in l and "constants" in l]
    for imp in imports:
        assert "PROJECT_ROOT" not in imp, (
            "runner-watch.ts should not import PROJECT_ROOT from constants — "
            "use the babel plugin root constant for build/tsconfig operations"
        )


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — REQUIRED for agentmd-edit tasks
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention the compile subcommand
    assert "snap compile" in content, (
        "CLAUDE.md should document the 'yarn snap compile' command"
    )

    # Must explain it can compile arbitrary files (not just fixtures)
    assert "arbitrary" in content.lower() or "any file" in content.lower() or \
           "not just fixtures" in content.lower(), (
        "CLAUDE.md should explain that compile works on any file, not just fixtures"
    )

    # Must mention the --debug flag for compile
    assert "--debug" in content or "debug" in content.lower(), (
        "CLAUDE.md should mention the debug option for the compile command"
    )


# [config_edit] fail_to_pass

    # Must mention the compile subcommand
    assert "snap compile" in content, (
        "DEVELOPMENT_GUIDE.md should document 'yarn snap compile'"
    )

    # Must mention the minimize subcommand with path syntax
    assert "snap minimize" in content, (
        "DEVELOPMENT_GUIDE.md should document 'yarn snap minimize'"
    )

    # Should have code examples
    assert "```" in content, (
        "DEVELOPMENT_GUIDE.md should include code examples"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compile_handler_not_stub():
    """The compile command handler must have real logic — file reading, compilation, output."""
    content = Path(RUNNER_TS).read_text()

    # Find the compile handler function
    compile_fn_match = re.search(
        r"(async\s+)?function\s+(\w*[Cc]ompile\w*)\s*\(", content
    )
    assert compile_fn_match, "Must have a compile handler function"

    fn_name = compile_fn_match.group(2)

    # Extract the function body (rough: from function declaration to end)
    fn_start = compile_fn_match.start()
    # Count at least some substantial lines
    fn_body = content[fn_start:fn_start + 3000]

    # Must read file contents
    assert "readFileSync" in fn_body or "readFile" in fn_body, (
        f"{fn_name} must read the input file"
    )

    # Must use the compiler (BABEL_PLUGIN_SRC or BabelPluginReactCompiler)
    assert "BABEL_PLUGIN_SRC" in fn_body or "BabelPluginReactCompiler" in fn_body or \
           "require(" in fn_body, (
        f"{fn_name} must load and use the compiler"
    )

    # Must handle the debug option
    assert "debug" in fn_body.lower(), (
        f"{fn_name} must handle the debug option"
    )

    # Must produce output
    assert "console" in fn_body or "stdout" in fn_body or "print" in fn_body, (
        f"{fn_name} must produce output"
    )
