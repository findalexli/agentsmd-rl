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
# fail_to_pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_output_option_in_types():
    """AiPrepareOptions interface must include an optional output field."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/types.ts").read_text()

    match = re.search(
        r"interface\s+AiPrepareOptions\s*\{([^}]+)\}", src
    )
    assert match, "AiPrepareOptions interface not found in types.ts"

    body = match.group(1)
    assert "output" in body, (
        "AiPrepareOptions must have an 'output' field for the --output CLI flag"
    )
    assert re.search(r"output\s*\?\s*:\s*string", body), (
        "output field should be typed as optional string (output?: string)"
    )
    # Existing fields must be preserved
    assert "configDir" in body, "AiPrepareOptions must retain configDir field"
    assert "packageManager" in body, "AiPrepareOptions must retain packageManager field"


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

// Must import from node:fs (for file writing)
if (!/from\\s+['"]node:fs/.test(src))
    errors.push('must import from node:fs or node:fs/promises for file writing');

// Must import from node:path (for path resolution)
if (!/from\\s+['"]node:path/.test(src))
    errors.push('must import from node:path for path resolution');

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
    """The CLI must register -o/--output <path> option."""
    r = _run_node("""
import { readFileSync } from 'node:fs';
const src = readFileSync('code/lib/cli-storybook/src/bin/run.ts', 'utf-8');

// Must have .option('-o, --output <path>', ...) somewhere in the CLI definition
if (!/-o,\\s*--output\\s+<[^>]+>/.test(src)) {
    console.error('FAIL: -o/--output option not registered in CLI');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"CLI flag check failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_prepare_receives_output():
    """The prepare subcommand action handler must have access to the output option."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/bin/run.ts").read_text()

    prepare_idx = src.find(".command('prepare')")
    assert prepare_idx != -1, "prepare subcommand not found"

    # Scope to the prepare subcommand section (next ~800 chars)
    prepare_section = src[prepare_idx : prepare_idx + 800]

    # Approach 1: --output defined directly on prepare subcommand
    has_output_on_prepare = bool(
        re.search(r"\.option\([^)]*--output", prepare_section)
    )

    # Approach 2: parent option forwarding in the action handler
    has_parent_forwarding = False
    action_match = re.search(
        r"\.action\(\s*async\s*\(([^)]+)\)", prepare_section
    )
    if action_match:
        params = action_match.group(1)
        if "," in params:
            # Two-parameter handler (options, cmd) — check for parent opts access
            remaining = prepare_section[action_match.end() :]
            has_parent_forwarding = (
                "parent" in remaining[:400] and "opts" in remaining[:400]
            )

    assert has_output_on_prepare or has_parent_forwarding, (
        "prepare subcommand must either define --output option directly "
        "or forward parent command options via cmd.parent?.opts()"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (static) — syntax and anti-stub checks
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
        l for l in lines[fn_start : fn_start + 80]
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
