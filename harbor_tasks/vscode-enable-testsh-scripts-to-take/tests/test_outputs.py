"""
Task: vscode-enable-testsh-scripts-to-take
Repo: vscode @ 73b0fb29377f401a4e2b792b9065e77b9fa19e9e
PR:   microsoft/vscode#306039

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/vscode"
INDEX_JS = Path(REPO) / "test" / "unit" / "electron" / "index.js"
SKILL_MD = Path(REPO) / ".github" / "skills" / "unit-tests" / "SKILL.md"

# ---------------------------------------------------------------------------
# Node.js harness: evaluates the argument processing logic from index.js
# with controlled argv inputs. Uses the exact same minimist config as the
# real file, then checks whether the source contains bare-file conversion
# logic. Only simulates the conversion if the logic is detected so that
# the harness correctly discriminates base (no logic) from gold (logic present).
# ---------------------------------------------------------------------------
_NODE_HARNESS = r"""
const fs = require('fs');
const minimist = require('minimist');

const source = fs.readFileSync(process.env.INDEX_JS_PATH, 'utf8');
const testArgv = JSON.parse(process.env.TEST_ARGV);

// Parse with the identical minimist config from index.js
const args = minimist(testArgv, {
    string: ['grep', 'run', 'runGlob', 'reporter', 'reporter-options',
             'waitServer', 'timeout', 'crash-reporter-directory', 'tfs',
             'coveragePath', 'coverageFormats', 'testSplit'],
    boolean: ['build', 'coverage', 'help', 'dev', 'per-test-coverage'],
    alias: { 'grep': ['g', 'f'], 'runGlob': ['glob', 'runGrep'],
             'dev': ['dev-tools', 'devTools'], 'help': 'h' },
    default: { 'reporter': 'spec', 'reporter-options': '' }
});

const bareFiles = (args._ || []).filter(a => typeof a === 'string' && (a.endsWith('.ts') || a.endsWith('.js')));

// Detect whether the source contains bare-file-to---run conversion logic.
// Only simulate the conversion if the logic is present (so nop != gold).
const hasConversionLogic = (function() {
    const patterns = [
        /args\.run\s*=.*bareFiles?/i,
        /bareFiles?.*\.filter.*\.ts/i,
        /\.filter.*\.endsWith\(['"]\.ts['"]\)/i,
        /positional.*--run/i,
        /bare.*\.ts.*positional/i,
    ];
    return patterns.some(p => p.test(source));
})();

if (hasConversionLogic && bareFiles.length > 0) {
    const existing = !args.run ? [] : Array.isArray(args.run) ? args.run : [args.run];
    args.run = [...existing, ...bareFiles];
    args._ = (args._ || []).filter(a => !bareFiles.includes(a));
}

console.log(JSON.stringify({
    run: args.run === undefined ? null : args.run,
    _: args._,
    hasConversionLogic: hasConversionLogic,
}));
"""


def _run_arg_test(test_argv: list) -> dict:
    """Run the Node.js harness with given argv, return parsed result."""
    r = subprocess.run(
        ["node", "-e", _NODE_HARNESS],
        capture_output=True, timeout=30,
        cwd=REPO,
        env={
            "INDEX_JS_PATH": str(INDEX_JS),
            "TEST_ARGV": json.dumps(test_argv),
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
            "HOME": "/root",
            "NODE_PATH": "/opt/test-deps/node_modules",
        },
    )
    assert r.returncode == 0, (
        f"Node harness failed (rc={r.returncode}):\n{r.stderr.decode()}"
    )
    return json.loads(r.stdout.decode().strip())


def _normalize_run(run_val) -> list:
    """Normalize args.run to a list (it can be None, str, or list)."""
    if run_val is None:
        return []
    if isinstance(run_val, str):
        return [run_val] if run_val else []
    return run_val


# ---------------------------------------------------------------------------
# pass_to_pass - gates / regression (including repo CI tests)
# ---------------------------------------------------------------------------

def test_repo_syntax_check():
    """Repo's test/unit/electron/index.js must parse without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", str(INDEX_JS)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in repo's index.js:\n{r.stderr}"


def test_repo_unit_node_syntax():
    """Repo's test/unit/node/index.js must parse without syntax errors (pass_to_pass)."""
    node_index = Path(REPO) / "test" / "unit" / "node" / "index.js"
    r = subprocess.run(
        ["node", "--check", str(node_index)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test/unit/node/index.js:\n{r.stderr}"


def test_repo_unit_renderer_syntax():
    """Repo's test/unit/electron/renderer.js must parse without syntax errors (pass_to_pass)."""
    renderer_js = Path(REPO) / "test" / "unit" / "electron" / "renderer.js"
    r = subprocess.run(
        ["node", "--check", str(renderer_js)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test/unit/electron/renderer.js:\n{r.stderr}"


def test_repo_unit_preload_syntax():
    """Repo's test/unit/electron/preload.js must parse without syntax errors (pass_to_pass)."""
    preload_js = Path(REPO) / "test" / "unit" / "electron" / "preload.js"
    r = subprocess.run(
        ["node", "--check", str(preload_js)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test/unit/electron/preload.js:\n{r.stderr}"


def test_repo_unit_reporter_syntax():
    """Repo's test/unit/reporter.js must parse without syntax errors (pass_to_pass)."""
    reporter_js = Path(REPO) / "test" / "unit" / "reporter.js"
    r = subprocess.run(
        ["node", "--check", str(reporter_js)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test/unit/reporter.js:\n{r.stderr}"


def test_repo_test_sh_syntax():
    """Repo's scripts/test.sh must have valid shell syntax (pass_to_pass)."""
    test_sh = Path(REPO) / "scripts" / "test.sh"
    r = subprocess.run(
        ["bash", "-n", str(test_sh)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Shell syntax error in scripts/test.sh:\n{r.stderr}"


def test_repo_package_json_valid():
    """Repo's package.json must be valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('package.json', 'utf8'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json is not valid JSON:\n{r.stderr}"


def test_repo_product_json_valid():
    """Repo's product.json must be valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('product.json', 'utf8'))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"product.json is not valid JSON:\n{r.stderr}"


def test_repo_all_shell_scripts_syntax():
    """All shell scripts in scripts/ folder must have valid syntax (pass_to_pass)."""
    scripts_dir = Path(REPO) / "scripts"
    sh_files = list(scripts_dir.glob("*.sh"))
    assert sh_files, f"No .sh files found in {scripts_dir}"

    for sh_file in sh_files:
        r = subprocess.run(
            ["bash", "-n", str(sh_file)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Shell syntax error in {sh_file}:\n{r.stderr}"


def test_repo_git_sanity():
    """Git repo must have at least one commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git sanity check failed:\n{r.stderr}"
    assert r.stdout.strip(), "Git log should return at least one commit"


def test_syntax_check():
    """Modified JS file must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(INDEX_JS)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in index.js:\n{r.stderr.decode()}"
    )


def test_existing_run_flag_preserved():
    """Explicit --run flag must still route to args.run."""
    result = _run_arg_test(["--run", "src/vs/editor/test/common/model.test.ts"])
    run = _normalize_run(result["run"])
    assert "src/vs/editor/test/common/model.test.ts" in run, (
        f"--run flag should still populate args.run, got: {result['run']}"
    )


def test_non_ts_bare_args_not_converted():
    """Non-.ts/.js bare arguments must stay in positional args, not become --run."""
    result = _run_arg_test(["--grep", "foo", "some-random-arg"])
    run = _normalize_run(result["run"])
    assert "some-random-arg" not in run, (
        f"Non-.ts/.js args should not become --run values, got run={result['run']}"
    )
    assert "some-random-arg" in result["_"], (
        "Non-.ts/.js bare args should remain in positional args (_)"
    )


# ---------------------------------------------------------------------------
# fail_to_pass - core behavioral changes from the PR
# ---------------------------------------------------------------------------

def test_bare_ts_file_becomes_run_arg():
    """A bare .ts file passed as a positional arg must be converted to --run."""
    result = _run_arg_test(["src/vs/editor/test/common/model.test.ts"])

    # The source must contain bare-file conversion logic (fails on base, passes on gold)
    assert result["hasConversionLogic"], (
        "Source must contain bare-file-to---run conversion logic"
    )

    run = _normalize_run(result["run"])
    assert "src/vs/editor/test/common/model.test.ts" in run, (
        f"Bare .ts file should end up in args.run, got: {result['run']}"
    )
    assert "src/vs/editor/test/common/model.test.ts" not in result["_"], (
        "Converted bare file should be removed from args._"
    )


def test_multiple_bare_files_all_converted():
    """Multiple bare .ts/.js files must all end up in args.run."""
    result = _run_arg_test([
        "src/vs/editor/test/common/model.test.ts",
        "src/vs/base/test/common/arrays.test.js",
    ])

    assert result["hasConversionLogic"], (
        "Source must contain bare-file-to---run conversion logic"
    )

    run = _normalize_run(result["run"])
    assert len(run) >= 2, (
        f"Both bare files should be in args.run, got: {result['run']}"
    )
    assert "src/vs/editor/test/common/model.test.ts" in run
    assert "src/vs/base/test/common/arrays.test.js" in run


def test_bare_files_merge_with_explicit_run():
    """Bare files must merge with an explicit --run flag, not replace it."""
    result = _run_arg_test([
        "--run", "src/vs/existing/file.test.ts",
        "src/vs/editor/test/common/model.test.ts",
    ])

    assert result["hasConversionLogic"], (
        "Source must contain bare-file-to---run conversion logic"
    )

    run = _normalize_run(result["run"])
    assert len(run) >= 2, (
        f"Should have both explicit --run and bare file, got: {result['run']}"
    )
    assert "src/vs/existing/file.test.ts" in run, (
        "Explicit --run value must be preserved"
    )
    assert "src/vs/editor/test/common/model.test.ts" in run, (
        "Bare file must be appended to --run"
    )


def test_help_text_mentions_positional_files():
    """Help text must document that bare file paths work as positional args."""
    content = INDEX_JS.read_text()
    # The usage line should show [file...] to indicate positional file support
    assert "[file" in content, (
        "Usage line should include [file...] for positional file arguments"
    )
    # Help should explain the connection between bare files and --run
    assert ("--run arguments" in content or "--run values" in content), (
        "Help text should explain bare files are treated as --run arguments"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_compile_install_build_tools():
    """pass_to_pass | CI job 'Compile' → step 'Install build tools'"""
    r = subprocess.run(
        ["bash", "-lc", 'sudo apt update -y && sudo apt install -y build-essential pkg-config libx11-dev libx11-xcb-dev libxkbfile-dev libnotify-bin libkrb5-dev'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Install build tools' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_compile_create_node_modules_archive():
    """pass_to_pass | CI job 'Compile' → step 'Create node_modules archive'"""
    r = subprocess.run(
        ["bash", "-lc", 'node build/azure-pipelines/common/listNodeModules.ts .build/node_modules_list.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Create node_modules archive' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")