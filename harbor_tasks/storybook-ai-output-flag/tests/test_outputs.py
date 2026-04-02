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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
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
        # Quick syntax check: balanced braces
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 2, (
            f"{f} has unbalanced braces ({opens} open, {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_output_option_in_types():
    """AiPrepareOptions interface must include an 'output' field."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/types.ts").read_text()
    # Match output field in the AiPrepareOptions interface
    pattern = re.compile(
        r"interface\s+AiPrepareOptions\s*\{[^}]*\boutput\b\s*[\?:]",
        re.DOTALL,
    )
    assert pattern.search(src) is not None, (
        "AiPrepareOptions interface must declare an 'output' field "
        "(e.g. output?: string)"
    )


# [pr_diff] fail_to_pass
def test_file_write_with_output_option():
    """aiPrepare must write markdown to a file when output option is provided."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/index.ts").read_text()

    # 1. Must import writeFile from node:fs/promises
    assert re.search(
        r"import\s+\{[^}]*writeFile[^}]*\}\s+from\s+['\"]node:fs/promises['\"]",
        src,
    ), "writeFile must be imported from 'node:fs/promises'"

    # 2. Must import resolve from node:path
    assert re.search(
        r"import\s+\{[^}]*resolve[^}]*\}\s+from\s+['\"]node:path['\"]",
        src,
    ), "resolve must be imported from 'node:path'"

    # 3. Must destructure 'output' from options
    assert re.search(
        r"\{[^}]*\boutput\b[^}]*\}\s*=\s*options",
        src,
    ), "aiPrepare must destructure 'output' from options"

    # 4. Must have conditional file write when output is set
    assert re.search(
        r"if\s*\(\s*output\s*\)[\s\S]*?writeFile\s*\(",
        src,
    ), "Must write to file when output option is provided"

    # 5. Must have else branch for console output fallback
    assert re.search(
        r"\}\s*else\s*\{[\s\S]*?logger\.log",
        src,
    ), "Must fall back to logger.log when output is not provided"


# [pr_diff] fail_to_pass
def test_output_flag_registered_in_cli():
    """The ai or prepare command must register -o/--output <path> option."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/bin/run.ts").read_text()

    # Check for the specific --output option with short flag -o
    output_opt = re.search(
        r"""\.option\(\s*['"](-o,\s*)?--output\s+<[^>]+>['"]""",
        src,
    )
    assert output_opt is not None, (
        "No --output option registered. Expected "
        ".option('-o, --output <path>', ...) on the ai or prepare command"
    )


# [pr_diff] fail_to_pass
def test_prepare_receives_output_option():
    """The prepare subcommand action must have access to the output option."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/bin/run.ts").read_text()

    # The output option can reach the prepare action via two approaches:
    # 1. Parent command options merged: action((options, cmd) => ...) + cmd.parent.opts()
    # 2. --output defined directly on the prepare subcommand

    # Approach 1: parent options merging
    has_parent_merge = bool(re.search(r"parent.*?opts\s*\(\s*\)", src))
    has_cmd_arg = bool(re.search(
        r"\.action\(\s*async\s*\(\s*\w+\s*,\s*\w+\s*\)", src
    ))
    uses_parent_merge = has_parent_merge and has_cmd_arg

    # Approach 2: --output directly on prepare command chain
    # Find the prepare command definition and check if --output is chained on it
    prepare_section = re.search(
        r"command\s*\(\s*['\"]prepare['\"].*?\.action\s*\(",
        src, re.DOTALL,
    )
    has_output_on_prepare = False
    if prepare_section:
        section_text = prepare_section.group(0)
        has_output_on_prepare = bool(re.search(r"--output", section_text))

    assert uses_parent_merge or has_output_on_prepare, (
        "Prepare action must receive output option — either via parent options "
        "merge (cmd.parent?.opts()) or by defining --output on prepare directly"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """aiPrepare function must contain real logic, not a stub."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/index.ts").read_text()

    # aiPrepare must retain its core logic
    assert "getStorybookData" in src, "aiPrepare must call getStorybookData"
    assert "generateMarkdownOutput" in src, "aiPrepare must call generateMarkdownOutput"
    assert "logger" in src, "aiPrepare must use logger"

    # Count non-empty, non-comment lines in the function
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
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:242-249 @ 15180fa049e683c4a58d69615dde12e33456512c
def test_uses_storybook_logger():
    """Output messages must use storybook logger, not console.log (AGENTS.md:242-249)."""
    src = Path(f"{REPO}/code/lib/cli-storybook/src/ai/index.ts").read_text()

    # Must import logger from storybook/internal/node-logger
    assert "storybook/internal/node-logger" in src, (
        "Must import logger from 'storybook/internal/node-logger' per AGENTS.md"
    )

    # Must NOT use console.log/warn/error for user-facing output
    console_calls = re.findall(r"\bconsole\.(log|warn|error)\s*\(", src)
    assert len(console_calls) == 0, (
        f"Found console.{console_calls[0]}() — AGENTS.md requires using "
        f"storybook logger instead of raw console.* calls"
    )

    # Must use logger.log for output
    assert "logger.log(" in src, "Must use logger.log() for output per AGENTS.md"
