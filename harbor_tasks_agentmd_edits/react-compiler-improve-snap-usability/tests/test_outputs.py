"""
Task: react-compiler-improve-snap-usability
Repo: facebook/react @ 2af6822c2108eabc0228d7809aa27c00bb2ebb53
PR:   35537

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
SNAP_SRC = Path(REPO) / "compiler" / "packages" / "snap" / "src"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    files = [
        SNAP_SRC / "constants.ts",
        SNAP_SRC / "fixture-utils.ts",
        SNAP_SRC / "runner.ts",
        SNAP_SRC / "runner-watch.ts",
    ]
    for f in files:
        assert f.exists(), f"{f.name} must exist"
        content = f.read_text()
        assert len(content) > 100, f"{f.name} is suspiciously short"
        assert "import" in content or "export" in content, (
            f"{f.name} must contain import/export statements"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_compiler_typecheck():
    """Repo's TypeScript typecheck for babel-plugin-react-compiler passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_compiler_lint():
    """Repo's ESLint for babel-plugin-react-compiler passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_compiler_build():
    """Repo's build for babel-plugin-react-compiler passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_snap_build():
    """Repo's build for snap package passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "snap", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Snap build failed:\n{r.stderr[-500:]}"


def test_repo_compiler_jest():
    """Repo's Jest tests for babel-plugin-react-compiler pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "jest", "--maxWorkers=2"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stderr[-500:]}"


def test_repo_root_eslint():
    """Repo's root-level ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Root ESLint failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_yargs_debug_option():
    """runner.ts defines --debug/-d boolean CLI option and removes --filter."""
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync('compiler/packages/snap/src/runner.ts', 'utf-8');

// Must have .boolean('debug') or .boolean("debug")
if (!/\\.boolean\\(\\s*['"]debug['"]\\s*\\)/.test(content)) {
    process.stderr.write('Missing .boolean("debug") in yargs config');
    process.exit(1);
}

// Must have .alias('d', 'debug') or .alias("d", "debug")
if (!/\\.alias\\(\\s*['"]d['"]\\s*,\\s*['"]debug['"]\\s*\\)/.test(content)) {
    process.stderr.write('Missing .alias("d", "debug") in yargs config');
    process.exit(1);
}

// Must NOT have .boolean('filter') - old option should be removed
if (/\\.boolean\\(\\s*['"]filter['"]\\s*\\)/.test(content)) {
    process.stderr.write('Still has .boolean("filter") - should be removed');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_filter_mechanism_removed():
    """FILTER constants and readTestFilter function removed from snap packages."""
    r = _run_node("""
import fs from 'fs';

const constants = fs.readFileSync('compiler/packages/snap/src/constants.ts', 'utf-8');
if (/export\\s+const\\s+FILTER_(FILENAME|PATH)\\b/.test(constants)) {
    process.stderr.write('constants.ts still exports FILTER_FILENAME or FILTER_PATH');
    process.exit(1);
}

const utils = fs.readFileSync('compiler/packages/snap/src/fixture-utils.ts', 'utf-8');
if (/(?:export\\s+)?(?:async\\s+)?function\\s+readTestFilter/.test(utils)) {
    process.stderr.write('fixture-utils.ts still defines readTestFilter');
    process.exit(1);
}
if (/debug\\s*:\\s*boolean/.test(utils)) {
    process.stderr.write('TestFilter type still has debug field');
    process.exit(1);
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_runner_state_interactive_fields():
    """RunnerState type includes debug, inputMode, and inputBuffer fields."""
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync('compiler/packages/snap/src/runner-watch.ts', 'utf-8');

const match = content.match(/export\\s+type\\s+RunnerState\\s*=\\s*\\{([\\s\\S]*?)\\n\\};/);
if (!match) {
    process.stderr.write('Cannot find RunnerState type definition');
    process.exit(1);
}
const body = match[1];

for (const field of ['debug', 'inputMode', 'inputBuffer']) {
    if (!new RegExp('\\\\b' + field + '\\\\s*:').test(body)) {
        process.stderr.write('RunnerState missing field: ' + field);
        process.exit(1);
    }
}

process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - CLAUDE.md creation
# ---------------------------------------------------------------------------

def test_claude_md_documents_snap_cli():
    """compiler/CLAUDE.md documents snap CLI with -p, -d, and -u flags."""
    claude_md = Path(REPO) / "compiler" / "CLAUDE.md"
    assert claude_md.exists(), "compiler/CLAUDE.md must be created"
    content = claude_md.read_text()
    assert "yarn snap" in content, "Should document 'yarn snap' command"
    assert "-p" in content, "Should document -p flag for pattern filtering"
    assert "-d" in content, "Should document -d flag for debug mode"
    assert "-u" in content or "update" in content.lower(), (
        "Should document how to update fixture outputs"
    )


def test_claude_md_documents_project_structure():
    """compiler/CLAUDE.md documents project structure and key concepts."""
    claude_md = Path(REPO) / "compiler" / "CLAUDE.md"
    assert claude_md.exists(), "compiler/CLAUDE.md must be created"
    content = claude_md.read_text()
    assert "babel-plugin-react-compiler" in content, (
        "Should reference the main compiler package"
    )
    assert "HIR" in content, (
        "Should document HIR (High-level Intermediate Representation)"
    )
    assert "fixture" in content.lower(), "Should document test fixtures"
    assert len(content) > 500, "Should have substantial documentation"
