"""
Task: react-compiler-snap-cli-claudemd
Repo: facebook/react @ 2d8e7f1ce358e8cddc3aae862007269b6bac04ba
PR:   35537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = Path(REPO) / "compiler" / "packages" / "snap" / "src"


def _node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_snap_installs():
    """Snap package dependencies install successfully (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Yarn install failed:\n{r.stderr[-500:]}"


def test_snap_typescript_compiles():
    """Snap package TypeScript compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "snap", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}"


def test_snap_builds():
    """Snap package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "snap", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Snap build failed:\n{r.stderr[-500:]}"


def test_snap_prettier_check():
    """Snap package source files follow prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "prettier", "--check", "packages/snap/src/**/*.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_typescript_files_parseable():
    """Modified TypeScript files have balanced braces (basic structural validity)."""
    files = [
        SNAP_SRC / "constants.ts",
        SNAP_SRC / "fixture-utils.ts",
        SNAP_SRC / "runner.ts",
        SNAP_SRC / "runner-watch.ts",
    ]
    for f in files:
        content = f.read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 1, (
            f"{f.name}: unbalanced braces ({opens} open, {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

def test_filter_file_mechanism_removed():
    """testfilter.txt-based filtering removed from constants.ts and fixture-utils.ts."""
    r = _node("""
const fs = require('fs');
const constants = fs.readFileSync(
    'compiler/packages/snap/src/constants.ts', 'utf8');
const fixtureUtils = fs.readFileSync(
    'compiler/packages/snap/src/fixture-utils.ts', 'utf8');

const errors = [];
if (constants.includes('FILTER_FILENAME'))
    errors.push('constants.ts still exports FILTER_FILENAME');
if (constants.includes('FILTER_PATH'))
    errors.push('constants.ts still exports FILTER_PATH');
if (constants.includes('testfilter.txt'))
    errors.push('constants.ts still references testfilter.txt');
if (fixtureUtils.includes('readTestFilter'))
    errors.push('fixture-utils.ts still has readTestFilter');
if (/debug\\s*:/.test(fixtureUtils))
    errors.push('TestFilter still has debug property');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Filter mechanism not removed: {r.stderr}"
    assert "PASS" in r.stdout


def test_filter_option_removed():
    """runner.ts removes --filter boolean option and readTestFilter/FILTER_PATH usage."""
    r = _node("""
const fs = require('fs');
const runner = fs.readFileSync(
    'compiler/packages/snap/src/runner.ts', 'utf8');

const errors = [];
if (runner.includes(".boolean('filter')") || runner.includes('.boolean("filter")'))
    errors.push('runner.ts still has --filter boolean option');
if (runner.includes('readTestFilter'))
    errors.push('runner.ts still imports readTestFilter');
if (runner.includes('FILTER_PATH'))
    errors.push('runner.ts still imports FILTER_PATH');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Old filter option not removed: {r.stderr}"
    assert "PASS" in r.stdout


def test_debug_cli_option():
    """runner.ts defines --debug / -d CLI option via yargs."""
    r = _node("""
const fs = require('fs');
const runner = fs.readFileSync(
    'compiler/packages/snap/src/runner.ts', 'utf8');

const errors = [];

// --debug boolean option must exist
if (!runner.includes(".boolean('debug')") && !runner.includes('.boolean("debug")'))
    errors.push('runner.ts missing --debug boolean option');

// -d alias must exist
if (!(/\\.alias\\(['"]d['"],\\s*['"]debug['"]\\)/.test(runner)))
    errors.push('runner.ts missing .alias("d", "debug")');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"--debug/-d option not added: {r.stderr}"
    assert "PASS" in r.stdout


def test_interactive_watch_mode():
    """runner-watch.ts supports interactive pattern entry and debug toggle via keyboard."""
    r = _node("""
const fs = require('fs');
const watch = fs.readFileSync(
    'compiler/packages/snap/src/runner-watch.ts', 'utf8');

const errors = [];

// RunnerState must have inputMode and inputBuffer for interactive pattern entry
if (!watch.includes('inputMode'))
    errors.push('missing inputMode in RunnerState');
if (!watch.includes('inputBuffer'))
    errors.push('missing inputBuffer in RunnerState');

// Must handle 'p' key for pattern entry
if (!/key\\.name\\s*===\\s*['"]p['"]/.test(watch))
    errors.push("missing 'p' key handler for pattern entry");
// Must handle 'd' key for debug toggle
if (!/key\\.name\\s*===\\s*['"]d['"]/.test(watch))
    errors.push("missing 'd' key handler for debug toggle");
// Must handle 'a' key for running all tests
if (!/key\\.name\\s*===\\s*['"]a['"]/.test(watch))
    errors.push("missing 'a' key handler to run all tests");

// subscribeFilterFile must be removed
if (watch.includes('subscribeFilterFile'))
    errors.push('subscribeFilterFile function not removed');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Interactive watch mode not implemented: {r.stderr}"
    assert "PASS" in r.stdout


def test_watch_runner_signature_updated():
    """makeWatchRunner accepts debugMode and initialPattern instead of filterMode."""
    r = _node("""
const fs = require('fs');
const watch = fs.readFileSync(
    'compiler/packages/snap/src/runner-watch.ts', 'utf8');

const errors = [];

// makeWatchRunner should accept debugMode: boolean
if (!/debugMode\\s*:\\s*boolean/.test(watch))
    errors.push('makeWatchRunner missing debugMode: boolean parameter');
// makeWatchRunner should accept initialPattern
if (!/initialPattern\\s*\\??\\s*:\\s*string/.test(watch))
    errors.push('makeWatchRunner missing initialPattern parameter');
// readTestFilter must not be used
if (watch.includes('readTestFilter'))
    errors.push('runner-watch.ts still uses readTestFilter');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"makeWatchRunner signature not updated: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CLAUDE.md creation tests
# ---------------------------------------------------------------------------

def test_claudemd_documents_cli():
    """compiler/CLAUDE.md documents snap CLI flags (-p, -d, -u)."""
    r = _node("""
const fs = require('fs');
const path = require('path');
const filePath = path.join('compiler', 'CLAUDE.md');

if (!fs.existsSync(filePath)) {
    console.error('compiler/CLAUDE.md does not exist');
    process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');
const errors = [];

if (!content.includes('yarn snap'))
    errors.push('missing yarn snap documentation');
if (!content.includes('-p') || !content.toLowerCase().includes('pattern'))
    errors.push('missing -p/--pattern flag documentation');
if (!content.includes('-d') || !content.toLowerCase().includes('debug'))
    errors.push('missing -d/--debug flag documentation');
if (!content.includes('-u'))
    errors.push('missing -u/--update flag documentation');

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"CLAUDE.md CLI docs missing: {r.stderr}"
    assert "PASS" in r.stdout


def test_claudemd_documents_project():
    """compiler/CLAUDE.md documents project structure, HIR, and fixtures."""
    r = _node("""
const fs = require('fs');
const path = require('path');
const filePath = path.join('compiler', 'CLAUDE.md');

if (!fs.existsSync(filePath)) {
    console.error('compiler/CLAUDE.md does not exist');
    process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');
const errors = [];

if (!content.includes('babel-plugin-react-compiler'))
    errors.push('missing babel-plugin-react-compiler reference');
if (!content.includes('HIR'))
    errors.push('missing HIR documentation');
if (!content.toLowerCase().includes('fixtures'))
    errors.push('missing fixtures reference');

// Must be substantial documentation (not just a stub)
if (content.length < 200) {
    errors.push('CLAUDE.md is too short (' + content.length + ' chars)');
}

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"CLAUDE.md project docs missing: {r.stderr}"
    assert "PASS" in r.stdout
