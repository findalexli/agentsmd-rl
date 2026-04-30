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


def _run_node(code: str, *args, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run a Node.js script, passing *args as process.argv[2..], clean up temp file."""
    script = Path(REPO) / "_eval_tmp.js"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script), *args],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass (static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must have valid syntax (balanced braces, non-empty)."""
    ts_files = [CONSTANTS_TS, RUNNER_TS, MINIMIZE_TS, RUNNER_WATCH_TS, RUNNER_WORKER_TS]
    for ts_file in ts_files:
        content = Path(ts_file).read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, (
            f"{ts_file}: brace mismatch ({opens} opens, {closes} closes)"
        )
        assert len(content) > 100, f"{ts_file}: file is suspiciously short"


# ---------------------------------------------------------------------------
# pass_to_pass (repo CI tests) - run on both base and gold commits
# All CI checks run in a single test to share yarn install (expensive)
# ---------------------------------------------------------------------------

COMPILER_DIR = f"{REPO}/compiler"
BABEL_PLUGIN_DIR = f"{COMPILER_DIR}/packages/babel-plugin-react-compiler"
SNAP_DIR = f"{COMPILER_DIR}/packages/snap"
YARN_INSTALL_TIMEOUT = 180
CI_TIMEOUT = 120


def test_repo_ci_checks():
    """Repo's CI checks pass - build, lint, jest, typecheck (pass_to_pass)."""
    errors = []

    # Run yarn install once
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=YARN_INSTALL_TIMEOUT, cwd=COMPILER_DIR,
    )
    if r.returncode != 0:
        errors.append(f"yarn install failed: {r.stderr[-500:]}")
        assert False, "; ".join(errors)

    # Test 1: babel-plugin build
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "build"],
        capture_output=True, text=True, timeout=CI_TIMEOUT, cwd=COMPILER_DIR,
    )
    if r.returncode != 0:
        errors.append(f"babel-plugin build failed: {r.stderr[-500:]}")

    # Test 2: babel-plugin lint
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "lint"],
        capture_output=True, text=True, timeout=CI_TIMEOUT, cwd=COMPILER_DIR,
    )
    if r.returncode != 0:
        errors.append(f"babel-plugin lint failed: {r.stderr[-500:]}")

    # Test 3: babel-plugin jest
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "jest"],
        capture_output=True, text=True, timeout=CI_TIMEOUT, cwd=COMPILER_DIR,
    )
    if r.returncode != 0:
        errors.append(f"babel-plugin jest failed: {r.stderr[-500:]}")

    # Test 4: babel-plugin typecheck
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=CI_TIMEOUT, cwd=BABEL_PLUGIN_DIR,
    )
    if r.returncode != 0:
        errors.append(f"babel-plugin typecheck failed: {r.stderr[-500:]}")

    # Test 5: snap typecheck
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=CI_TIMEOUT, cwd=SNAP_DIR,
    )
    if r.returncode != 0:
        errors.append(f"snap typecheck failed: {r.stderr[-500:]}")

    if errors:
        assert False, "; ".join(errors)


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests using Node subprocess
# ---------------------------------------------------------------------------

def test_constants_separation():
    """Root path constant resolves to compiler/ dir (2 levels up), not babel-plugin subdir."""
    r = _run_node(r"""
const fs = require('fs');
const path = require('path');
const content = fs.readFileSync(process.argv[2], 'utf8');

// Find the first exported const using process.cwd() for a root path
const pattern = /export\s+const\s+(\w+)\s*=\s*([^;]*process\.cwd\(\)[^;]*);/s;
const match = content.match(pattern);
if (!match) {
    console.error('FAIL: No exported path constant using process.cwd()');
    process.exit(1);
}

const name = match[1];
const expr = match[2];

// Simulate cwd as the snap package directory and evaluate the path expression
const fakeCwd = '/sim/compiler/packages/snap';
const evalExpr = expr.replace(/process\.cwd\(\)/g, "'" + fakeCwd + "'");

let result;
try {
    result = path.normalize(eval(evalExpr));
} catch(e) {
    console.error('FAIL: Could not evaluate path expression: ' + e.message);
    process.exit(1);
}

// Must resolve to compiler root (2 dirs up from snap), NOT babel-plugin subdir
const compilerRoot = path.normalize(path.join(fakeCwd, '..', '..'));
if (result === compilerRoot) {
    console.log('PASS: ' + name + ' = ' + result);
} else {
    console.error('FAIL: ' + name + ' = ' + result + ' (expected ' + compilerRoot + ')');
    process.exit(1);
}
""", CONSTANTS_TS)
    assert r.returncode == 0, f"Root constant wrong: {r.stderr}"
    assert "PASS" in r.stdout


def test_compile_command_registered():
    """runner.ts registers a 'compile' subcommand via yargs with path and debug options."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');
const errors = [];

// Must register a compile command with yargs .command()
if (!content.includes("'compile") && !content.includes('"compile')) {
    errors.push('No compile command string in yargs chain');
}

// Must have a handler function for compilation
if (!/(?:async\s+)?function\s+\w*[Cc]ompile/.test(content)) {
    errors.push('No compile handler function');
}

// compile command must accept a path argument
if (!content.includes('compile <path>') &&
    !/compile[\s\S]{0,500}\.positional/.test(content)) {
    errors.push('compile must accept a path argument');
}

if (errors.length > 0) {
    console.error('FAIL: ' + errors.join('; '));
    process.exit(1);
}
console.log('PASS');
""", RUNNER_TS)
    assert r.returncode == 0, f"Compile command missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_minimize_positional_path():
    """minimize command accepts path as a positional argument, not --path option."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

// Must have 'minimize <path>' (yargs positional syntax)
if (!/'minimize\s+<path>'/.test(content) && !/"minimize\s+<path>"/.test(content)) {
    console.error('FAIL: minimize must use positional <path> syntax');
    process.exit(1);
}
console.log('PASS');
""", RUNNER_TS)
    assert r.returncode == 0, f"minimize path not positional: {r.stderr}"
    assert "PASS" in r.stdout


def test_path_resolution_not_cwd():
    """path.resolve calls in runner.ts must NOT use process.cwd() directly."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

// Find all path.resolve(...) calls
const resolves = content.match(/path\.resolve\([^)]*\)/g) || [];
const bad = resolves.filter(r => r.includes('process.cwd()'));

if (bad.length > 0) {
    console.error('FAIL: path.resolve still uses process.cwd(): ' + bad[0]);
    process.exit(1);
}
console.log('PASS');
""", RUNNER_TS)
    assert r.returncode == 0, f"path.resolve uses process.cwd(): {r.stderr}"
    assert "PASS" in r.stdout


def test_runner_watch_uses_plugin_root():
    """runner-watch.ts must import the babel plugin root constant, not PROJECT_ROOT."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

// Check import lines from constants module
const lines = content.split('\n');
for (const line of lines) {
    if (line.includes('from') && line.includes('constants')) {
        if (/\bPROJECT_ROOT\b/.test(line)) {
            console.error('FAIL: runner-watch.ts imports PROJECT_ROOT — should use babel plugin root');
            process.exit(1);
        }
    }
}
console.log('PASS');
""", RUNNER_WATCH_TS)
    assert r.returncode == 0, f"runner-watch.ts uses wrong constant: {r.stderr}"
    assert "PASS" in r.stdout


def test_compile_handler_not_stub():
    """Compile command handler must have real logic — file reading, compilation, output."""
    r = _run_node(r"""
const fs = require('fs');
const content = fs.readFileSync(process.argv[2], 'utf8');

const fnMatch = content.match(/(?:async\s+)?function\s+(\w*[Cc]ompile\w*)\s*\(/);
if (!fnMatch) {
    console.error('FAIL: No compile handler function found');
    process.exit(1);
}

const fnName = fnMatch[1];
const fnBody = content.substring(fnMatch.index, fnMatch.index + 3000);

const checks = [
    [/readFileSync|readFile/.test(fnBody), 'must read the input file'],
    [/BABEL_PLUGIN|BabelPlugin|require\(/.test(fnBody), 'must load the compiler'],
    [/debug/i.test(fnBody), 'must handle debug option'],
    [/console\.|stdout|print/.test(fnBody), 'must produce output'],
];

const failures = checks.filter(c => !c[0]).map(c => c[1]);
if (failures.length > 0) {
    console.error('FAIL: ' + fnName + ': ' + failures.join('; '));
    process.exit(1);
}
console.log('PASS: ' + fnName + ' has real logic');
""", RUNNER_TS)
    assert r.returncode == 0, f"Compile handler is stub: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — documentation updates
# ---------------------------------------------------------------------------

def test_claude_md_documents_compile():
    """compiler/CLAUDE.md must document the 'yarn snap compile' command."""
    content = Path(CLAUDE_MD).read_text()
    assert "snap compile" in content, (
        "CLAUDE.md should document 'yarn snap compile'"
    )
    assert "--debug" in content or "debug" in content.lower(), (
        "CLAUDE.md should mention the debug option for compile"
    )


def test_dev_guide_documents_commands():
    """compiler/docs/DEVELOPMENT_GUIDE.md must document compile and minimize commands."""
    content = Path(DEV_GUIDE).read_text()
    assert "snap compile" in content, (
        "DEVELOPMENT_GUIDE.md should document 'yarn snap compile'"
    )
    assert "snap minimize" in content, (
        "DEVELOPMENT_GUIDE.md should document 'yarn snap minimize'"
    )
