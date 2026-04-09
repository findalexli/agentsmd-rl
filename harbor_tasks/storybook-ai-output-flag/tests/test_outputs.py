"""
Task: storybook-ai-output-flag
Repo: storybook @ 15180fa049e683c4a58d69615dde12e33456512c
PR:   34425

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/storybook"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/ESM code via Node in the repo directory."""
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
# fail_to_pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_output_option_typechecks():
    """AiPrepareOptions accepts 'output' field — verified by TypeScript compiler."""
    test_file = Path(REPO) / "code/lib/cli-storybook/src/ai/_eval_type_test.ts"
    test_file.write_text(
        "import type { AiPrepareOptions } from './types';\n"
        "const opts: AiPrepareOptions = { output: '/tmp/test.md' };\n"
        "export {};\n"
    )
    try:
        r = subprocess.run(
            ["npx", "tsc", "--noEmit",
             "--moduleResolution", "node",
             "--target", "ES2020",
             "--module", "ES2020",
             str(test_file)],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, (
            f"TypeScript type check failed — AiPrepareOptions must accept 'output' field:\n"
            f"{r.stdout}\n{r.stderr}"
        )
    finally:
        test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_aiPrepare_file_write_logic():
    """aiPrepare writes to file when output is specified, falls back to logger otherwise."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/lib/cli-storybook/src/ai/index.ts', 'utf-8');

const errors = [];

// Must destructure 'output' from options in aiPrepare
if (!/\\{[^}]*\\boutput\\b[^}]*\\}\\s*=\\s*options/.test(src))
    errors.push('output not destructured from options');

// Must call writeFile when output is provided
if (!/writeFile\\s*\\(/.test(src))
    errors.push('writeFile not called');

// Must have conditional on output
if (!/if\\s*\\(?\\s*output\\b/.test(src))
    errors.push('no conditional check on output');

// Must fall back to logger.log when output is not provided
if (!/\\}\\s*else\\s*\\{[\\s\\S]{0,300}?logger\\.log/.test(src))
    errors.push('no else fallback to logger.log');

if (errors.length) {
    console.error('FAIL:', errors.join('; '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"File write logic check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_output_flag_registered_in_cli():
    """The ai command registers -o/--output <path> option."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/lib/cli-storybook/src/bin/run.ts', 'utf-8');

// Must have .option('-o, --output <path>', ...) on the ai command or prepare subcommand
if (!/-o,\\s*--output\\s+<[^>]+>/.test(src)) {
    console.error('FAIL: -o/--output option not registered');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"CLI flag check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_parent_options_merged():
    """Prepare subcommand merges parent options so --output reaches aiPrepare."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/lib/cli-storybook/src/bin/run.ts', 'utf-8');

const errors = [];

// Action handler must accept both options and cmd: .action(async (options, cmd) => ...)
if (!/\\.action\\(\\s*async\\s*\\(\\s*\\w+\\s*,\\s*\\w+\\s*\\)/.test(src))
    errors.push('action handler must accept (options, cmd) arguments');

// Must access parent options via cmd.parent?.opts() or cmd.parent.opts()
if (!/parent.*?\\.?opts\\s*\\(\\s*\\)/.test(src))
    errors.push('must call parent.opts() to get parent command options');

// Must merge/spread parent and subcommand options
if (!/\\{\\s*\\.\\.\\.\\w+.*,\\s*\\.\\.\\.\\w+/.test(src))
    errors.push('must merge parent and subcommand options');

if (errors.length) {
    console.error('FAIL:', errors.join('; '));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Parent options merge check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# pass_to_pass (static) — compilation and anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "code/lib/cli-storybook/src/ai/index.ts",
        "code/lib/cli-storybook/src/ai/types.ts",
        "code/lib/cli-storybook/src/bin/run.ts",
    ]
    for f in files:
        fpath = Path(REPO) / f
        assert fpath.exists(), f"{f} does not exist"
        content = fpath.read_text()
        assert len(content) > 50, f"{f} appears to be empty or too short"
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, (
            f"{f} has unbalanced braces ({opens} open, {closes} close)"
        )


# [static] pass_to_pass
def test_not_stub():
    """aiPrepare function must contain real logic, not a stub."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/index.ts").read_text()

    assert "getStorybookData" in src, "aiPrepare must call getStorybookData"
    assert "generateMarkdownOutput" in src, "aiPrepare must call generateMarkdownOutput"
    assert "logger" in src, "aiPrepare must use logger"

    lines = src.splitlines()
    fn_start = None
    for i, line in enumerate(lines):
        if "function aiPrepare" in line:
            fn_start = i
            break
    assert fn_start is not None, "aiPrepare function not found"
    fn_lines = [
        l for l in lines[fn_start:fn_start + 80]
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(fn_lines) >= 20, (
        f"aiPrepare body too short ({len(fn_lines)} lines) — likely a stub"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:242-249 @ 15180fa049e683c4a58d69615dde12e33456512c
def test_uses_storybook_logger():
    """Output messages must use storybook logger, not console.log (AGENTS.md:242-249)."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/index.ts").read_text()

    assert "storybook/internal/node-logger" in src, (
        "Must import logger from 'storybook/internal/node-logger' per AGENTS.md"
    )

    console_calls = re.findall(r"\bconsole\.(log|warn|error)\s*\(", src)
    assert len(console_calls) == 0, (
        f"Found console.{console_calls[0]}() — AGENTS.md requires using "
        f"storybook logger instead of raw console.* calls"
    )

    assert "logger.log(" in src, "Must use logger.log() for output per AGENTS.md"
