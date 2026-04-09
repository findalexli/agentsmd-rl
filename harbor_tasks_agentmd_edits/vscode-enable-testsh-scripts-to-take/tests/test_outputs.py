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
# real file, then extracts and applies the bareFiles conversion block
# (if present) from the actual source. Returns processed args as JSON.
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

// Find and apply the bareFiles conversion block from the actual source.
// On the base commit this block doesn't exist, so bareFiles stay unconverted.
const blockStart = source.indexOf('// Treat bare');
let applied = false;
if (blockStart !== -1) {
    // Walk forward to find the closing brace of the if-block
    let braceCount = 0, foundBrace = false, blockEnd = blockStart;
    for (let i = blockStart; i < source.length; i++) {
        if (source[i] === '{') { braceCount++; foundBrace = true; }
        if (source[i] === '}') { braceCount--; }
        if (foundBrace && braceCount === 0) { blockEnd = i + 1; break; }
    }
    const block = source.substring(blockStart, blockEnd);
    eval(block);  // mutates args in this scope
    applied = true;
}

console.log(JSON.stringify({
    run: args.run === undefined ? null : args.run,
    _: args._,
    applied: applied,
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
    assert result["applied"], (
        "index.js must have bare-file conversion logic (// Treat bear ...)"
    )
    run = _normalize_run(result["run"])
    assert "src/vs/editor/test/common/model.test.ts" in run, (
        f"Bare .ts file should end up in args.run, got: {result['run']}"
    )
    # The bare file should be removed from positional args
    assert "src/vs/editor/test/common/model.test.ts" not in result["_"], (
        "Converted bare file should be removed from args._"
    )


def test_multiple_bare_files_all_converted():
    """Multiple bare .ts/.js files must all end up in args.run."""
    result = _run_arg_test([
        "src/vs/editor/test/common/model.test.ts",
        "src/vs/base/test/common/arrays.test.js",
    ])
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
