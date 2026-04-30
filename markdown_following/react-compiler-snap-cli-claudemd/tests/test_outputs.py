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


def test_babel_plugin_lint():
    """babel-plugin-react-compiler lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "lint"],
        capture_output=True, text=True, timeout=300, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_babel_plugin_jest():
    """babel-plugin-react-compiler Jest tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "babel-plugin-react-compiler", "jest"],
        capture_output=True, text=True, timeout=300, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stderr[-500:]}"


def test_eslint_plugin_build():
    """eslint-plugin-react-compiler builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "eslint-plugin-react-compiler", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"ESLint plugin build failed:\n{r.stderr[-500:]}"


def test_eslint_plugin_test():
    """eslint-plugin-react-compiler tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "eslint-plugin-react-compiler", "test"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert r.returncode == 0, f"ESLint plugin tests failed:\n{r.stderr[-500:]}"


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
    """CLI defines --debug / -d flag and it appears in help output."""
    # Build snap package first so we can run the CLI
    build = subprocess.run(
        ["yarn", "workspace", "snap", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO + "/compiler",
    )
    assert build.returncode == 0, f"Snap build failed: {build.stderr[-500:]}"

    # Run CLI with --help and check that -d/--debug is listed
    r = subprocess.run(
        ["node", "packages/snap/dist/runner.js", "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO + "/compiler",
    )
    help_text = r.stdout + r.stderr
    assert '-d' in help_text or '--debug' in help_text, \
        f"Help output does not show -d/--debug flag. Got:\n{help_text[:500]}"
    print("PASS: debug flag present in CLI help")


def test_interactive_watch_mode():
    """Watch runner supports interactive keyboard control for pattern and debug."""
    r = _node("""
const fs = require('fs');
const watch = fs.readFileSync(
    'compiler/packages/snap/src/runner-watch.ts', 'utf8');

const errors = [];

// Watch runner must handle keyboard events for interactive control
const hasKeyHandler = /key\\s*&&\\s*key\\.name/.test(watch) ||
                      /key\\.name\\s*===/.test(watch) ||
                      /onKey.*key.*name/i.test(watch);
if (!hasKeyHandler) {
    errors.push('watch runner missing keyboard key handling');
}

// Must support pattern/toggle behavior (not specific variable names)
if (!watch.includes('pattern')) {
    errors.push('watch runner missing pattern support');
}

// Must support debug toggle via keyboard
if (!watch.includes('debug')) {
    errors.push('watch runner missing debug toggle support');
}

// subscribeFilterFile must be removed (file-based mechanism gone)
if (watch.includes('subscribeFilterFile')) {
    errors.push('subscribeFilterFile function not removed');
}

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Interactive watch mode not implemented: {r.stderr}"
    assert "PASS" in r.stdout


def test_watch_runner_signature_updated():
    """Watch runner accepts boolean debug and string pattern parameters from CLI."""
    r = _node("""
const fs = require('fs');
const watch = fs.readFileSync(
    'compiler/packages/snap/src/runner-watch.ts', 'utf8');

const errors = [];

// Watch runner function must accept a boolean debug parameter
// (flexible on exact name - just check it exists and is boolean-typed)
const hasBooleanDebugParam = /:\\s*boolean/.test(watch);
if (!hasBooleanDebugParam) {
    errors.push('watch runner missing boolean debug parameter');
}

// Must accept some kind of pattern/filter string parameter
// (flexible on exact name)
const hasPatternParam = /initialPattern|filter|pattern.*string|string.*pattern/i.test(watch);
if (!hasPatternParam) {
    errors.push('watch runner missing pattern string parameter');
}

// readTestFilter must not be used (file-based mechanism removed)
if (watch.includes('readTestFilter')) {
    errors.push('watch runner still uses readTestFilter');
}

if (errors.length > 0) {
    console.error(errors.join('\\n'));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Watch runner signature not updated: {r.stderr}"
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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_playground_yarn():
    """pass_to_pass | CI job 'Test playground' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn install --frozen-lockfile'], cwd=os.path.join(REPO, 'compiler'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_playground_check_playwright_version():
    """pass_to_pass | CI job 'Test playground' → step 'Check Playwright version'"""
    r = subprocess.run(
        ["bash", "-lc", 'echo "playwright_version=$(npm ls @playwright/test | grep @playwright | sed \'s/.*@//\' | head -1)" >> "$GITHUB_OUTPUT"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Playwright version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_playground_npx():
    """pass_to_pass | CI job 'Test playground' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps chromium'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_flags_ensure_clean_build_directory():
    """pass_to_pass | CI job 'Check flags' → step 'Ensure clean build directory'"""
    r = subprocess.run(
        ["bash", "-lc", 'rm -rf build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Ensure clean build directory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_flags_yarn():
    """pass_to_pass | CI job 'Check flags' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn flags'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_eslint_plugin_react_hooks_scripts_react_compiler_build_compiler_sh():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/react-compiler/build-compiler.sh && ./scripts/react-compiler/link-compiler.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_eslint_plugin_react_hooks_yarn():
    """pass_to_pass | CI job 'Test eslint-plugin-react-hooks' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn workspace eslint-plugin-react-hooks test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")