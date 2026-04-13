"""
Task: playwright-chorecli-expose-video-commands
Repo: microsoft/playwright @ 8c99ff19b8e03ab21cec344d8b2f1d149d4040c7
PR:   39006

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script that inspects TypeScript source files."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — CI lint / build checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint passes on modified MCP files (pass_to_pass)."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"
    # Then run eslint on existing files (not video.ts which is added by the fix)
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--no-cache",
         "packages/playwright/src/mcp/browser/tools.ts",
         "packages/playwright/src/mcp/browser/tools/tracing.ts",
         "packages/playwright/src/mcp/program.ts",
         "packages/playwright/src/mcp/terminal/commands.ts",
         "packages/playwright/src/mcp/terminal/command.ts",
         "packages/playwright/src/mcp/config.d.ts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's workspace packages are consistent (pass_to_pass)."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"
    # Then run lint-packages
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_generate_channels():
    """Repo's generate_channels script runs without error (pass_to_pass)."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"
    # Then run generate_channels
    r = subprocess.run(
        ["node", "utils/generate_channels.js"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"generate_channels failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_typescript_syntax():
    """Key modified TypeScript files have valid syntax (balanced braces, no stray tokens)."""
    files = [
        "packages/playwright/src/mcp/browser/tools.ts",
        "packages/playwright/src/mcp/browser/tools/tracing.ts",
        "packages/playwright/src/mcp/config.d.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/command.ts",
    ]
    r = _run_node("""
const fs = require('fs');
const files = %s;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    // Check balanced braces/parens/brackets
    let braces = 0, parens = 0, brackets = 0;
    for (const ch of content) {
        if (ch === '{') braces++;
        else if (ch === '}') braces--;
        else if (ch === '(') parens++;
        else if (ch === ')') parens--;
        else if (ch === '[') brackets++;
        else if (ch === ']') brackets--;
    }
    if (braces !== 0 || parens !== 0 || brackets !== 0) {
        console.error('Unbalanced in ' + f + ': braces=' + braces + ' parens=' + parens + ' brackets=' + brackets);
        process.exit(1);
    }
}
console.log('PASS');
""" % json.dumps(files))
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_video_tool_module_exists():
    """video.ts browser tool module must exist with start/stop video tools."""
    video_ts = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "video.ts"
    assert video_ts.exists(), "video.ts tool module must exist"
    content = video_ts.read_text()
    assert "browser_start_video" in content, "video.ts must define browser_start_video tool"
    assert "browser_stop_video" in content, "video.ts must define browser_stop_video tool"
    assert "devtools" in content, "video tools must use 'devtools' capability"
    # Verify it exports both tools
    assert "startVideo" in content or "start_video" in content.lower(), \
        "video.ts must define startVideo"
    assert "stopVideo" in content or "stop_video" in content.lower(), \
        "video.ts must define stopVideo"


# [pr_diff] fail_to_pass
def test_video_commands_registered():
    """Terminal commands.ts must declare video-start and video-stop commands."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');

// Check that videoStart and videoStop command declarations exist
const hasVideoStart = /declareCommand\\(\\s*\\{[^}]*name:\\s*['"]video-start['"]/.test(content);
const hasVideoStop = /declareCommand\\(\\s*\\{[^}]*name:\\s*['"]video-stop['"]/.test(content);

if (!hasVideoStart) {
    console.error('Missing video-start command declaration');
    process.exit(1);
}
if (!hasVideoStop) {
    console.error('Missing video-stop command declaration');
    process.exit(1);
}

// Verify they map to correct browser tools
if (!content.includes("toolName: 'browser_start_video'")) {
    console.error('video-start must map to browser_start_video');
    process.exit(1);
}
if (!content.includes("toolName: 'browser_stop_video'")) {
    console.error('video-stop must map to browser_stop_video');
    process.exit(1);
}

// Verify they're in the commandsArray export
const arraySection = content.substring(content.indexOf('commandsArray'));
if (!arraySection.includes('videoStart')) {
    console.error('videoStart not in commandsArray');
    process.exit(1);
}
if (!arraySection.includes('videoStop')) {
    console.error('videoStop not in commandsArray');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Video commands check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_devtools_capability_replaces_tracing():
    """The 'tracing' capability must be renamed to 'devtools' in config.d.ts and tracing.ts."""
    r = _run_node("""
const fs = require('fs');

// Check config.d.ts has 'devtools' in ToolCapability type
const config = fs.readFileSync('packages/playwright/src/mcp/config.d.ts', 'utf8');
const typeBlock = config.substring(
    config.indexOf('export type ToolCapability'),
    config.indexOf(';', config.indexOf('export type ToolCapability'))
);
if (!typeBlock.includes("'devtools'")) {
    console.error("ToolCapability must include 'devtools'");
    process.exit(1);
}

// Check tracing.ts tools use 'devtools' capability
const tracing = fs.readFileSync('packages/playwright/src/mcp/browser/tools/tracing.ts', 'utf8');
const capMatches = tracing.match(/capability:\\s*['"]([^'"]+)['"]/g) || [];
for (const m of capMatches) {
    if (m.includes("'tracing'") || m.includes('"tracing"')) {
        console.error('tracing.ts still uses tracing capability: ' + m);
        process.exit(1);
    }
    if (!m.includes("'devtools'") && !m.includes('"devtools"')) {
        console.error('tracing.ts capability should be devtools: ' + m);
        process.exit(1);
    }
}
if (capMatches.length < 2) {
    console.error('Expected at least 2 capability declarations in tracing.ts');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Devtools capability check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_caps_cli_help_includes_devtools():
    """program.ts --caps help text must list devtools as a possible value."""
    program_ts = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "program.ts"
    content = program_ts.read_text()
    # Find the --caps option line
    caps_lines = [line for line in content.split("\n") if "--caps" in line and "possible values" in line.lower()]
    assert len(caps_lines) >= 1, "Must have --caps option line with possible values"
    caps_line = caps_lines[0]
    assert "devtools" in caps_line, \
        f"--caps help must list devtools as a value, got: {caps_line}"


# [pr_diff] fail_to_pass
def test_tracing_to_devtools_backward_compat():
    """program.ts must map legacy 'tracing' cap to 'devtools' for backward compatibility."""
    content = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "program.ts").read_text()
    # Must have code that checks for 'tracing' in caps and pushes 'devtools'
    assert "includes('tracing')" in content or 'includes("tracing")' in content, \
        "program.ts must check for legacy 'tracing' capability"
    assert "devtools" in content, "program.ts must map tracing to devtools"


# [pr_diff] fail_to_pass
def test_video_tools_imported_in_browser_tools():
    """browser/tools.ts must import and spread video tools into browserTools array."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/browser/tools.ts', 'utf8');

// Check import
if (!/import\\s+video\\s+from\\s+['\"][\\.\\/a-z_]+\\/video['\"]/.test(content)) {
    console.error('tools.ts must import video module');
    process.exit(1);
}

// Check spread in browserTools array
if (!content.includes('...video')) {
    console.error('browserTools must spread ...video');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Video import check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config-derived — SKILL.md documentation update
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_skill_md_documents_video_commands():
    """SKILL.md must document the video-start and video-stop CLI commands."""
    skill_md = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "SKILL.md"
    content = skill_md.read_text()
    assert "video-start" in content, \
        "SKILL.md must document the video-start command"
    assert "video-stop" in content, \
        "SKILL.md must document the video-stop command"
    # Should be in the DevTools section
    devtools_idx = content.lower().find("devtools")
    assert devtools_idx != -1, "SKILL.md must have a DevTools section"
    video_start_idx = content.find("video-start")
    video_stop_idx = content.find("video-stop")
    assert video_start_idx > devtools_idx, \
        "video-start should appear after the DevTools heading"
    assert video_stop_idx > devtools_idx, \
        "video-stop should appear after the DevTools heading"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_existing_tracing_commands_intact():
    """Existing tracing-start and tracing-stop commands must still be declared."""
    content = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "commands.ts").read_text()
    assert "tracing-start" in content, "tracing-start command must still exist"
    assert "tracing-stop" in content, "tracing-stop command must still exist"
    assert "tracingStart" in content, "tracingStart variable must still exist"
    assert "tracingStop" in content, "tracingStop variable must still exist"


# [static] pass_to_pass
def test_skill_md_preserves_existing_commands():
    """SKILL.md must still document tracing-start and tracing-stop."""
    content = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "SKILL.md").read_text()
    assert "tracing-start" in content, "SKILL.md must still have tracing-start"
    assert "tracing-stop" in content, "SKILL.md must still have tracing-stop"
    assert "playwright-cli" in content, "SKILL.md must still reference playwright-cli"
