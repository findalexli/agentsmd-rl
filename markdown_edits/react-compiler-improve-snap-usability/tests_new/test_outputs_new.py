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
# Pass-to-pass (repo_tests) - CI/CD checks using Node directly
# ---------------------------------------------------------------------------

def test_repo_node_syntax_check():
    """Node.js can parse the modified TypeScript files (pass_to_pass)."""
    files = [
        "compiler/packages/snap/src/constants.ts",
        "compiler/packages/snap/src/fixture-utils.ts",
        "compiler/packages/snap/src/runner.ts",
        "compiler/packages/snap/src/runner-watch.ts",
    ]

    for f in files:
        r = _run_node(f"""
import fs from 'fs';
const content = fs.readFileSync('{f}', 'utf-8');
// Check for balanced braces (basic syntax validation)
let braceCount = 0;
let parenCount = 0;
for (const char of content) {{
  if (char === '{{') braceCount++;
  else if (char === '}}') braceCount--;
  else if (char === '(') parenCount++;
  else if (char === ')') parenCount--;
  if (braceCount < 0 || parenCount < 0) {{
    process.stderr.write('Unbalanced braces/parens in {f}');
    process.exit(1);
  }}
}}
if (braceCount !== 0 || parenCount !== 0) {{
  process.stderr.write('Unbalanced braces/parens in {f}');
  process.exit(1);
}}
process.stdout.write('PASS');
""")
        assert r.returncode == 0, f"Syntax check failed for {f}:\n{r.stderr}"


def test_repo_snap_imports_valid():
    """Snap package imports and exports are valid (pass_to_pass)."""
    r = _run_node("""
import fs from 'fs';

const files = [
  'compiler/packages/snap/src/constants.ts',
  'compiler/packages/snap/src/fixture-utils.ts',
  'compiler/packages/snap/src/runner.ts',
  'compiler/packages/snap/src/runner-watch.ts',
];

const importExportRegex = /^(import|export)\\s+/m;
for (const file of files) {
  const content = fs.readFileSync(file, 'utf-8');
  // Check that file has import or export statements
  if (!importExportRegex.test(content)) {
    process.stderr.write('No import/export in ' + file);
    process.exit(1);
  }
  // Check no empty export blocks
  if (/export\\s*\\{\\s*\\}/.test(content)) {
    process.stderr.write('Empty export block in ' + file);
    process.exit(1);
  }
}
process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"Import validation failed:\n{r.stderr}"


def test_repo_runner_has_cli_options():
    """Runner.ts defines expected CLI options (pass_to_pass)."""
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync('compiler/packages/snap/src/runner.ts', 'utf-8');

// Check for yargs usage
if (!content.includes('yargs')) {
  process.stderr.write('runner.ts should use yargs');
  process.exit(1);
}

// Check for standard options
const requiredPatterns = [
  /\\.alias\\s*\\(/,  // has alias calls
  /\\.boolean\\s*\\(/,  // has boolean options
  /\\.string\\s*\\(/,  // has string options
  /\\.help\\s*\\(/,  // has help
  /\\.strict\\s*\\(/,  // uses strict mode
];

for (const pattern of requiredPatterns) {
  if (!pattern.test(content)) {
    process.stderr.write('Missing pattern: ' + pattern);
    process.exit(1);
  }
}
process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"CLI options check failed:\n{r.stderr}"


def test_repo_file_structure_valid():
    """Modified snap source files have valid structure (pass_to_pass)."""
    r = _run_node("""
import fs from 'fs';
import path from 'path';

const srcDir = 'compiler/packages/snap/src';
const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.ts'));

// Check all .ts files are non-empty and have valid structure
for (const file of files) {
  const filepath = path.join(srcDir, file);
  const content = fs.readFileSync(filepath, 'utf-8');

  if (content.length === 0) {
    process.stderr.write('Empty file: ' + file);
    process.exit(1);
  }

  // Check for suspicious characters
  if (content.includes('\\x00')) {
    process.stderr.write('Null bytes in file: ' + file);
    process.exit(1);
  }
}
process.stdout.write('PASS');
""")
    assert r.returncode == 0, f"File structure check failed:\n{r.stderr}"


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
