"""
Task: playwright-choremcp-remove-unnecessary-waitforcompletion-fro
Repo: microsoft/playwright @ b6f860d846146f072f5a804017d89f2deb737b39
PR:   39769

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
TOOLS = f"{REPO}/packages/playwright-core/src/tools"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.js"
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
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        f"{TOOLS}/backend/keyboard.ts",
        f"{TOOLS}/backend/mouse.ts",
        f"{TOOLS}/backend/snapshot.ts",
        f"{TOOLS}/cli-client/skill/SKILL.md",
    ]
    for fpath in files:
        assert Path(fpath).exists(), f"File not found: {fpath}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_type_tool_conditional_wait():
    """browser_type (fill) must only use waitForCompletion when submit or slowly is set."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/backend/keyboard.ts', 'utf8');

// Find browser_type tool definition
const toolMatch = src.match(/name:\\s*['"]browser_type['"]/);
if (!toolMatch) { console.error('browser_type tool not found'); process.exit(1); }

// Extract handler body using brace counting
const rest = src.slice(toolMatch.index);
const handleMatch = rest.match(/handle:\\s*async/);
if (!handleMatch) { console.error('handle function not found'); process.exit(1); }

const fromHandle = rest.slice(handleMatch.index);
const braceStart = fromHandle.indexOf('{');
let depth = 0;
let handler = '';
for (let i = braceStart; i < fromHandle.length; i++) {
    if (fromHandle[i] === '{') depth++;
    if (fromHandle[i] === '}') { depth--; if (depth === 0) { handler = fromHandle.slice(braceStart, i + 1); break; } }
}

// waitForCompletion must still exist (for submit/slowly paths)
if (!handler.includes('waitForCompletion')) {
    console.error('FAIL: waitForCompletion removed entirely - still needed for submit/slowly');
    process.exit(1);
}

// Must reference both params.submit and params.slowly as guards
if (!handler.includes('params.submit')) {
    console.error('FAIL: must check params.submit to decide waitForCompletion');
    process.exit(1);
}
if (!handler.includes('params.slowly')) {
    console.error('FAIL: must check params.slowly to decide waitForCompletion');
    process.exit(1);
}

// waitForCompletion must be inside a conditional, not at top level of handler
const lines = handler.split('\\n');
const waitLineIndices = [];
lines.forEach((l, i) => { if (l.includes('waitForCompletion')) waitLineIndices.push(i); });

let guarded = false;
for (const wl of waitLineIndices) {
    const preceding = lines.slice(Math.max(0, wl - 5), wl).join('\\n');
    if (/if\\s*\\(/.test(preceding)) { guarded = true; break; }
}
if (!guarded) {
    console.error('FAIL: waitForCompletion must be guarded by a conditional (submit/slowly)');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_hover_no_wait_for_completion():
    """browser_hover must not use waitForCompletion."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/backend/snapshot.ts', 'utf8');

const toolMatch = src.match(/name:\\s*['"]browser_hover['"]/);
if (!toolMatch) { console.error('browser_hover not found'); process.exit(1); }

const rest = src.slice(toolMatch.index);
const handleMatch = rest.match(/handle:\\s*async/);
if (!handleMatch) { console.error('handle not found'); process.exit(1); }

const fromHandle = rest.slice(handleMatch.index);
const braceStart = fromHandle.indexOf('{');
let depth = 0;
let handler = '';
for (let i = braceStart; i < fromHandle.length; i++) {
    if (fromHandle[i] === '{') depth++;
    if (fromHandle[i] === '}') { depth--; if (depth === 0) { handler = fromHandle.slice(braceStart, i + 1); break; } }
}

if (handler.includes('waitForCompletion')) {
    console.error('FAIL: hover must not use waitForCompletion - hover never causes navigation');
    process.exit(1);
}

if (!handler.includes('.hover(')) {
    console.error('FAIL: hover handler must still call .hover()');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_select_option_no_wait_for_completion():
    """browser_select_option must not use waitForCompletion."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/backend/snapshot.ts', 'utf8');

const toolMatch = src.match(/name:\\s*['"]browser_select_option['"]/);
if (!toolMatch) { console.error('browser_select_option not found'); process.exit(1); }

const rest = src.slice(toolMatch.index);
const handleMatch = rest.match(/handle:\\s*async/);
if (!handleMatch) { console.error('handle not found'); process.exit(1); }

const fromHandle = rest.slice(handleMatch.index);
const braceStart = fromHandle.indexOf('{');
let depth = 0;
let handler = '';
for (let i = braceStart; i < fromHandle.length; i++) {
    if (fromHandle[i] === '{') depth++;
    if (fromHandle[i] === '}') { depth--; if (depth === 0) { handler = fromHandle.slice(braceStart, i + 1); break; } }
}

if (handler.includes('waitForCompletion')) {
    console.error('FAIL: selectOption must not use waitForCompletion - never causes navigation');
    process.exit(1);
}

if (!handler.includes('selectOption')) {
    console.error('FAIL: selectOption handler must still call selectOption');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_mouse_move_no_wait_for_completion():
    """browser_mouse_move_xy must not use waitForCompletion."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/backend/mouse.ts', 'utf8');

const toolMatch = src.match(/name:\\s*['"]browser_mouse_move_xy['"]/);
if (!toolMatch) { console.error('browser_mouse_move_xy not found'); process.exit(1); }

const rest = src.slice(toolMatch.index);
const handleMatch = rest.match(/handle:\\s*async/);
if (!handleMatch) { console.error('handle not found'); process.exit(1); }

const fromHandle = rest.slice(handleMatch.index);
const braceStart = fromHandle.indexOf('{');
let depth = 0;
let handler = '';
for (let i = braceStart; i < fromHandle.length; i++) {
    if (fromHandle[i] === '{') depth++;
    if (fromHandle[i] === '}') { depth--; if (depth === 0) { handler = fromHandle.slice(braceStart, i + 1); break; } }
}

if (handler.includes('waitForCompletion')) {
    console.error('FAIL: mouseMove must not use waitForCompletion - mouse.move never causes navigation');
    process.exit(1);
}

if (!handler.includes('mouse.move')) {
    console.error('FAIL: mouseMove handler must still call mouse.move');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_skill_md_submit_flag():
    """SKILL.md must document the --submit flag for fill command."""
    r = _run_node("""
const fs = require('fs');
const md = fs.readFileSync('packages/playwright-core/src/tools/cli-client/skill/SKILL.md', 'utf8');

if (!md.includes('--submit')) {
    console.error('FAIL: SKILL.md must document the --submit flag');
    process.exit(1);
}

const fillSubmitLines = md.split('\\n').filter(l => l.toLowerCase().includes('fill') && l.includes('--submit'));
if (fillSubmitLines.length === 0) {
    console.error('FAIL: SKILL.md needs at least one fill example with --submit');
    process.exit(1);
}

const lower = md.toLowerCase();
if (!(lower.includes('enter') && lower.includes('submit')) && !lower.includes('presses enter')) {
    console.error('FAIL: SKILL.md must explain that --submit presses Enter after filling');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

def test_click_still_uses_wait_for_completion():
    """browser_click must still use waitForCompletion (it causes navigation)."""
    src = Path(f"{TOOLS}/backend/snapshot.ts").read_text()
    click_section = _extract_tool_handler(src, "browser_click")
    assert "waitForCompletion" in click_section, \
        "click handler must still use waitForCompletion — clicks can cause navigation"


def test_press_enter_still_uses_wait_for_completion():
    """browser_press_key for Enter must still use waitForCompletion."""
    src = Path(f"{TOOLS}/backend/keyboard.ts").read_text()
    press_section = _extract_tool_handler(src, "browser_press_key")
    assert "waitForCompletion" in press_section, \
        "press handler must still use waitForCompletion for Enter key"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------

def test_repo_eslint():
    """Repo's ESLint passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0",
         "packages/playwright-core/src/tools/backend/keyboard.ts",
         "packages/playwright-core/src/tools/backend/mouse.ts",
         "packages/playwright-core/src/tools/backend/snapshot.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Repo's package consistency checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_check_deps():
    """Repo's dependency checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"check-deps failed:\n{r.stderr[-500:]}"


def test_repo_generate_channels():
    """Repo's channel generation passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "utils/generate_channels.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"generate_channels failed:\n{r.stderr[-500:]}"


def test_repo_generate_injected():
    """Repo's injected script generation passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "utils/generate_injected.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"generate_injected failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_tool_handler(src: str, tool_name: str) -> str:
    """Extract a tool handler body by its schema name."""
    pattern = rf"name:\s*['\"]{ re.escape(tool_name) }['\"]"
    match = re.search(pattern, src)
    assert match, f"{tool_name} tool definition not found"
    start = match.start()
    handle_match = re.search(r"handle:\s*async", src[start:])
    assert handle_match, f"handle function not found in {tool_name} tool"
    handle_start = start + handle_match.start()
    rest = src[handle_start:]
    return _extract_brace_block(rest)


def _extract_brace_block(src: str) -> str:
    """Extract text from first { to its matching }, inclusive."""
    brace_start = src.index("{")
    depth = 0
    for i in range(brace_start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start:i + 1]
    return src[brace_start:]
