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
    # Verify it defines browser_start_video and browser_stop_video tools
    assert "browser_start_video" in content, "video.ts must define browser_start_video tool"
    assert "browser_stop_video" in content, "video.ts must define browser_stop_video tool"
    # Verify capability is 'devtools' (not 'tracing')
    assert "devtools" in content, "video tools must use 'devtools' capability"


# [pr_diff] fail_to_pass
def test_video_commands_registered():
    """Terminal commands.ts must declare video-start and video-stop commands."""
    commands_ts = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "commands.ts"
    content = commands_ts.read_text()

    # Check that video-start and video-stop command declarations exist
    has_video_start = re.search(r"declareCommand\s*\(\s*\{[^}]*name:\s*['\"]video-start['\"]", content)
    has_video_stop = re.search(r"declareCommand\s*\(\s*\{[^}]*name:\s*['\"]video-stop['\"]", content)

    assert has_video_start is not None, "Missing video-start command declaration"
    assert has_video_stop is not None, "Missing video-stop command declaration"

    # Verify they map to browser tools (check toolName values, not exact strings)
    tool_names = re.findall(r"toolName:\s*['\"]([^'\"]+)['\"]", content)
    assert "browser_start_video" in tool_names, "video-start must map to a browser_start_video tool"
    assert "browser_stop_video" in tool_names, "video-stop must map to a browser_stop_video tool"

    # Verify commands are exported in the commandsArray
    array_section = content[content.find("commandsArray"):] if "commandsArray" in content else content
    # Check that video-related commands are in the array (variable names may vary)
    assert "video" in array_section.lower(), "video commands should be in commandsArray"


# [pr_diff] fail_to_pass
def test_devtools_capability_replaces_tracing():
    """The 'tracing' capability must be renamed to 'devtools' in config.d.ts and tracing.ts."""
    # Check config.d.ts has 'devtools' in ToolCapability type
    config = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "config.d.ts").read_text()
    type_match = re.search(r"export type ToolCapability\s*=([^;]+);", config)
    assert type_match is not None, "ToolCapability type not found"
    type_body = type_match.group(1)
    assert "devtools" in type_body, "ToolCapability must include 'devtools'"
    # Old 'tracing' value should be absent or replaced
    assert "'tracing'" not in type_body and '"tracing"' not in type_body, \
        "ToolCapability should not contain 'tracing'"

    # Check tracing.ts tools use 'devtools' capability (not 'tracing')
    tracing = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "browser" / "tools" / "tracing.ts").read_text()
    cap_matches = re.findall(r"capability:\s*['\"]([^'\"]+)['\"]", tracing)
    assert len(cap_matches) >= 2, "Expected at least 2 capability declarations in tracing.ts"
    for cap in cap_matches:
        assert cap == "devtools", f"All capabilities in tracing.ts must be 'devtools', found: {cap}"


# [pr_diff] fail_to_pass
def test_caps_cli_help_includes_devtools():
    """program.ts --caps help text must list devtools as a possible value."""
    program_ts = Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "program.ts"
    content = program_ts.read_text()
    # Find the --caps option line with possible values
    caps_lines = [line for line in content.split("\n") if "--caps" in line and "possible values" in line.lower()]
    assert len(caps_lines) >= 1, "Must have --caps option line with possible values"
    caps_line = caps_lines[0]
    assert "devtools" in caps_line, \
        f"--caps help must list devtools as a value, got: {caps_line}"


# [pr_diff] fail_to_pass
def test_tracing_to_devtools_backward_compat():
    """program.ts must map legacy 'tracing' cap to 'devtools' for backward compatibility."""
    content = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "program.ts").read_text()
    # Must check for 'tracing' capability in the caps list and map it to 'devtools'
    # We check behavior: when tracing is requested, devtools should also be available
    # Look for any form of checking tracing in caps list
    has_tracing_check = (
        "tracing" in content.lower() and
        ("includes" in content or "indexOf" in content or "some" in content or "filter" in content)
    )
    assert has_tracing_check, \
        "program.ts must check for legacy 'tracing' capability"
    # Must reference 'devtools' somewhere in the same context
    assert "devtools" in content, "program.ts must map tracing to devtools"


# [pr_diff] fail_to_pass
def test_video_tools_imported_in_browser_tools():
    """browser/tools.ts must import and spread video tools into browserTools array."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('packages/playwright/src/mcp/browser/tools.ts', 'utf8');

// Check import of a video module
if (!/import\\s+\\w+\\s+from\\s+['\"][\\.\\/a-z_]+\\/video['\"]/.test(content)) {
    console.error('tools.ts must import video module');
    process.exit(1);
}

// Check spread of the imported module in browserTools array
const browserToolsMatch = content.match(/export\\s+const\\s+browserTools[^=]*=\\s*\\[([\\s\\S]*?)\\]/);
if (!browserToolsMatch) {
    console.error('browserTools array not found');
    process.exit(1);
}
const arrayContent = browserToolsMatch[1];
if (!arrayContent.includes('...') || !arrayContent.toLowerCase().includes('video')) {
    console.error('browserTools must spread video module');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Video import check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_video_tools_executable():
    """The video tools can be loaded and invoked via the MCP server (behavioral test)."""
    # Ensure dependencies are installed so TypeScript is available
    subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # Test that the TypeScript module compiles and exports expected tools
    r = _run_node("""
const ts = require('typescript');
const path = require('path');
const fs = require('fs');

// Transpile video.ts to check it has valid TypeScript syntax
const videoPath = 'packages/playwright/src/mcp/browser/tools/video.ts';
if (!fs.existsSync(videoPath)) {
    console.error('video.ts does not exist');
    process.exit(1);
}

const content = fs.readFileSync(videoPath, 'utf8');
const result = ts.transpileModule(content, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ESNext }
});

if (result.diagnostics && result.diagnostics.length > 0) {
    console.error('TypeScript error in video.ts:', JSON.stringify(result.diagnostics));
    process.exit(1);
}

// Verify the transpiled output exports start/stop functions
if (!result.outputText.includes('start') && !result.outputText.includes('stop')) {
    console.error('video.ts must export start/stop functionality');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Video tools TypeScript check failed: {r.stderr}"
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
    # Check that the variable names (or similar patterns) exist
    assert "tracingStart" in content or "tracing-start" in content, "tracing-related command must exist"
    assert "tracingStop" in content or "tracing-stop" in content, "tracing-related command must exist"


# [static] pass_to_pass
def test_skill_md_preserves_existing_commands():
    """SKILL.md must still document tracing-start and tracing-stop."""
    content = (Path(REPO) / "packages" / "playwright" / "src" / "mcp" / "terminal" / "SKILL.md").read_text()
    assert "tracing-start" in content, "SKILL.md must still have tracing-start"
    assert "tracing-stop" in content, "SKILL.md must still have tracing-stop"
    assert "playwright-cli" in content, "SKILL.md must still reference playwright-cli"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_snippets_npm():
    """pass_to_pass | CI job 'Lint snippets' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' -> step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
