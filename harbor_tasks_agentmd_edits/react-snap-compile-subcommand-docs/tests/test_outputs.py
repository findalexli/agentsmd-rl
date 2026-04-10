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
# pass_to_pass (repo_tests) — CI tests
# ---------------------------------------------------------------------------

def test_repo_tsc_check_babel_plugin():
    """TypeScript typecheck passes for babel-plugin-react-compiler (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["node_modules/.bin/tsc", "--noEmit", "--project", "packages/babel-plugin-react-compiler/tsconfig.json"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_tsc_check_snap():
    """TypeScript typecheck passes for snap package (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["node_modules/.bin/tsc", "--noEmit", "--project", "packages/snap/tsconfig.json"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_tsc_build_snap():
    """TypeScript build succeeds for snap package (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["node_modules/.bin/tsc", "--build", "packages/snap/tsconfig.json"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"TypeScript build failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's linter passes for babel-plugin-react-compiler (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "lint"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_jest():
    """Repo's Jest tests pass for babel-plugin-react-compiler (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"yarn install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "jest"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/compiler",
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# pass_to_pass (static) — syntax sanity
# ---------------------------------------------------------------------------

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
        assert content.count("{") == content.count("}"), (
            f"{f.name} has unbalanced braces"
        )


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def test_constants_evaluate_with_babel_plugin_exports():
    """Transpile and evaluate constants.ts; verify BABEL_PLUGIN_ROOT/SRC are defined."""
    code = r"""const fs = require("fs");
const path = require("path");

const src = fs.readFileSync("compiler/packages/snap/src/constants.ts", "utf8");

// Minimal TS->JS: remove import statement, strip export keyword
let js = src.replace(/import\s+path\s+from\s+['\"]path['\"];?/g, "");
js = js.replace(/export\s+/g, "");

// Build a function that evaluates the JS and returns the constants
const body = js + "\n"
  + "return {\n"
  + "  BABEL_PLUGIN_ROOT: typeof BABEL_PLUGIN_ROOT !== 'undefined' ? BABEL_PLUGIN_ROOT : null,\n"
  + "  BABEL_PLUGIN_SRC: typeof BABEL_PLUGIN_SRC !== 'undefined' ? BABEL_PLUGIN_SRC : null,\n"
  + "};\n";

const fn = new Function("path", "process", body);
const result = fn(path, process);

if (!result.BABEL_PLUGIN_ROOT || !result.BABEL_PLUGIN_ROOT.includes("babel-plugin-react-compiler")) {
  console.error("FAIL: BABEL_PLUGIN_ROOT missing or invalid:", result.BABEL_PLUGIN_ROOT);
  process.exit(1);
}
if (!result.BABEL_PLUGIN_SRC || !result.BABEL_PLUGIN_SRC.includes("dist/index.js")) {
  console.error("FAIL: BABEL_PLUGIN_SRC missing or invalid:", result.BABEL_PLUGIN_SRC);
  process.exit(1);
}
console.log("PASS");
"""
    r = _run_node(code)
    assert r.returncode == 0, f"Eval failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_compile_command_in_yargs():
    """Parse runner.ts with Node and verify 'compile <path>' is registered."""
    code = r"""const fs = require("fs");

const src = fs.readFileSync("compiler/packages/snap/src/runner.ts", "utf8");

// Extract yargs .command() first arguments
const cmdPattern = /\.command\(\s*(?:\[([^\]]+)\]|['\"]([^'\"]*)['\"])/g;
const commands = [];
let m;
while ((m = cmdPattern.exec(src)) !== null) {
  commands.push(m[1] || m[2]);
}

const compileCmd = commands.find(c => c && c.startsWith("compile"));
if (!compileCmd) {
  console.error("FAIL: No compile command found. Commands:", JSON.stringify(commands));
  process.exit(1);
}
if (!compileCmd.includes("<path>") && !compileCmd.includes("[path]")) {
  console.error("FAIL: compile command missing path parameter:", compileCmd);
  process.exit(1);
}
console.log("PASS: found command:", compileCmd);
"""
    r = _run_node(code)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — structural tests
# ---------------------------------------------------------------------------

def test_minimize_positional_path():
    """minimize command should accept path as a positional arg, not --path flag."""
    src = (SNAP_SRC / "runner.ts").read_text()
    assert re.search(r'["\x27]minimize <path>["\x27]', src), (
        "minimize command should use positional <path> syntax"
    )


def test_path_resolution_uses_project_root():
    """minimize and compile should resolve relative paths from PROJECT_ROOT."""
    src = (SNAP_SRC / "runner.ts").read_text()
    resolve_calls = re.findall(r"path\.resolve\(([^,]+),\s*opts\.path\)", src)
    assert len(resolve_calls) >= 1, "Should have path.resolve calls for opts.path"
    for call in resolve_calls:
        assert "PROJECT_ROOT" in call, (
            f"Path resolution should use PROJECT_ROOT, not {call.strip()}"
        )


def test_consumer_files_use_renamed_constants():
    """Files that imported PROJECT_ROOT/PROJECT_SRC should now use
    BABEL_PLUGIN_ROOT/BABEL_PLUGIN_SRC."""
    worker_src = (SNAP_SRC / "runner-worker.ts").read_text()
    assert "BABEL_PLUGIN_SRC" in worker_src, (
        "runner-worker.ts should import BABEL_PLUGIN_SRC"
    )
    assert "PROJECT_SRC" not in worker_src, (
        "runner-worker.ts should not reference old PROJECT_SRC"
    )

    watch_src = (SNAP_SRC / "runner-watch.ts").read_text()
    assert "BABEL_PLUGIN_ROOT" in watch_src, (
        "runner-watch.ts should import BABEL_PLUGIN_ROOT"
    )

    minimize_src = (SNAP_SRC / "minimize.ts").read_text()
    assert "BABEL_PLUGIN_SRC" in minimize_src, (
        "minimize.ts should import BABEL_PLUGIN_SRC"
    )
    assert "PROJECT_SRC" not in minimize_src, (
        "minimize.ts should not reference old PROJECT_SRC"
    )


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — documentation tests
# ---------------------------------------------------------------------------

def test_claude_md_documents_compile():
    """compiler/CLAUDE.md must document the yarn snap compile command."""
    claude_md = Path(REPO) / "compiler" / "CLAUDE.md"
    assert claude_md.exists(), "compiler/CLAUDE.md not found"
    content = claude_md.read_text()
    assert "yarn snap compile" in content, (
        "CLAUDE.md should document yarn snap compile"
    )


def test_claude_md_documents_minimize():
    """compiler/CLAUDE.md must document the yarn snap minimize command."""
    claude_md = Path(REPO) / "compiler" / "CLAUDE.md"
    content = claude_md.read_text()
    assert "yarn snap minimize" in content, (
        "CLAUDE.md should document yarn snap minimize"
    )


def test_dev_guide_documents_commands():
    """DEVELOPMENT_GUIDE.md must document compile and minimize commands."""
    guide = Path(REPO) / "compiler" / "docs" / "DEVELOPMENT_GUIDE.md"
    assert guide.exists(), "compiler/docs/DEVELOPMENT_GUIDE.md not found"
    content = guide.read_text()
    assert "yarn snap compile" in content, (
        "DEVELOPMENT_GUIDE.md should document yarn snap compile"
    )
    assert "yarn snap minimize" in content, (
        "DEVELOPMENT_GUIDE.md should document yarn snap minimize"
    )
