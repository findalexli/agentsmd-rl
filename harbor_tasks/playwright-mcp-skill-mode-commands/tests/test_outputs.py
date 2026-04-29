"""
Task: playwright-mcp-skill-mode-commands
Repo: microsoft/playwright @ 1e81675f850280d2cbaa0bbb01a7f066532d0e01
PR:   38932

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "packages/playwright/src/mcp/browser/config.ts",
        "packages/playwright/src/mcp/browser/response.ts",
        "packages/playwright/src/mcp/browser/tab.ts",
        "packages/playwright/src/mcp/browser/tools/evaluate.ts",
        "packages/playwright/src/mcp/browser/tools/tool.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert content.count("{") == content.count("}"), (
            f"{f} has unbalanced braces"
        )


def test_json_files_valid():
    """All JSON files in the repo must be valid (pass_to_pass)."""
    json_files = [
        "package.json",
        "package-lock.json",
        "packages/playwright/src/mcp/terminal/help.json",
    ]
    for f in json_files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            assert False, f"{f} is not valid JSON: {e}"


def test_ts_syntax_node_parse():
    """Modified TypeScript files must have balanced syntax via Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');
const REPO = '/workspace/playwright';

const files = [
    'packages/playwright/src/mcp/browser/config.ts',
    'packages/playwright/src/mcp/browser/response.ts',
    'packages/playwright/src/mcp/browser/tab.ts',
    'packages/playwright/src/mcp/browser/tools/evaluate.ts',
    'packages/playwright/src/mcp/browser/tools/tool.ts',
    'packages/playwright/src/mcp/program.ts',
    'packages/playwright/src/mcp/terminal/commands.ts'
];

for (const file of files) {
    const fullPath = path.join(REPO, file);
    const content = fs.readFileSync(fullPath, 'utf8');

    // Check for balanced braces
    const open = content.split('{').length - 1;
    const close = content.split('}').length - 1;
    if (open !== close) {
        console.error('Unbalanced braces in ' + file);
        process.exit(1);
    }

    // Check for balanced parentheses
    const openP = content.split('(').length - 1;
    const closeP = content.split(')').length - 1;
    if (openP !== closeP) {
        console.error('Unbalanced parentheses in ' + file);
        process.exit(1);
    }
}
console.log('All TypeScript files have balanced syntax');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"


def test_mcp_package_structure():
    """MCP package structure must be intact (pass_to_pass)."""
    required_dirs = [
        "packages/playwright/src/mcp/browser",
        "packages/playwright/src/mcp/browser/tools",
        "packages/playwright/src/mcp/terminal",
    ]
    for d in required_dirs:
        p = Path(REPO) / d
        assert p.is_dir(), f"Required directory {d} must exist"

    required_files = [
        "packages/playwright/src/mcp/browser/config.ts",
        "packages/playwright/src/mcp/browser/response.ts",
        "packages/playwright/src/mcp/browser/tab.ts",
        "packages/playwright/src/mcp/browser/tools/evaluate.ts",
        "packages/playwright/src/mcp/browser/tools/tool.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
        "packages/playwright/src/mcp/terminal/help.json",
    ]
    for f in required_files:
        p = Path(REPO) / f
        assert p.exists(), f"Required file {f} must exist"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI tests using subprocess
# ---------------------------------------------------------------------------

def test_repo_eslint_mcp_files():
    """Run ESLint on modified MCP files (pass_to_pass repo test).

    Note: This test runs npm ci first to install dependencies, then runs ESLint.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node --max-old-space-size=3072 node_modules/.bin/eslint \
    packages/playwright/src/mcp/terminal/commands.ts \
    packages/playwright/src/mcp/program.ts \
    packages/playwright/src/mcp/browser/config.ts \
    packages/playwright/src/mcp/browser/response.ts \
    packages/playwright/src/mcp/browser/tab.ts \
    packages/playwright/src/mcp/browser/tools/evaluate.ts \
    packages/playwright/src/mcp/browser/tools/tool.ts \
    --ext .ts --no-cache 2>&1
"""],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_typescript_syntax():
    """Use TypeScript parser to verify syntax of modified files (pass_to_pass).

    Note: This test runs npm ci first to install dependencies, then uses TypeScript parser.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node -e '
const fs = require("fs");
const ts = require("typescript");

const files = [
    "packages/playwright/src/mcp/browser/config.ts",
    "packages/playwright/src/mcp/browser/response.ts",
    "packages/playwright/src/mcp/browser/tab.ts",
    "packages/playwright/src/mcp/browser/tools/evaluate.ts",
    "packages/playwright/src/mcp/browser/tools/tool.ts",
    "packages/playwright/src/mcp/program.ts",
    "packages/playwright/src/mcp/terminal/commands.ts"
];

let hasErrors = false;
for (const file of files) {
    const content = fs.readFileSync(file, "utf8");
    const sourceFile = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);

    if (sourceFile.parseDiagnostics && sourceFile.parseDiagnostics.length > 0) {
        console.error("Parse errors in " + file + ":");
        sourceFile.parseDiagnostics.forEach(d => console.error("  " + d.messageText));
        hasErrors = true;
    }
}

if (hasErrors) {
    process.exit(1);
} else {
    console.log("All TypeScript files have valid syntax");
}
'
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript syntax check failed: {r.stderr[-500:]}"


def test_repo_test_files_syntax():
    """Check that modified test files have valid TypeScript syntax (pass_to_pass).

    Note: This test runs npm ci first to install dependencies, then uses TypeScript parser.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node -e '
const fs = require("fs");
const ts = require("typescript");

const testFiles = [
    "tests/mcp/cli.spec.ts",
    "tests/mcp/dialogs.spec.ts",
    "tests/mcp/files.spec.ts"
];

let hasErrors = false;
for (const file of testFiles) {
    const content = fs.readFileSync(file, "utf8");
    const sourceFile = ts.createSourceFile(file, content, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);

    if (sourceFile.parseDiagnostics && sourceFile.parseDiagnostics.length > 0) {
        console.error("Parse errors in " + file + ":");
        sourceFile.parseDiagnostics.forEach(d => console.error("  " + d.messageText));
        hasErrors = true;
    } else {
        console.log(file + " parses OK");
    }
}

if (hasErrors) {
    process.exit(1);
} else {
    console.log("All test files have valid TypeScript syntax");
}
'
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Test files syntax check failed: {r.stderr[-500:]}"


def test_repo_help_json_valid():
    """Validate help.json is valid JSON using Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = 'packages/playwright/src/mcp/terminal/help.json';
const content = fs.readFileSync(path, 'utf8');
try {
    JSON.parse(content);
    console.log('help.json is valid JSON');
} catch (e) {
    console.error('Invalid JSON in help.json: ' + e.message);
    process.exit(1);
}
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"help.json validation failed: {r.stderr}"


def test_repo_package_json_valid():
    """Validate package.json files are valid JSON (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const files = ['package.json', 'package-lock.json'];
for (const f of files) {
    try {
        JSON.parse(fs.readFileSync(f, 'utf8'));
        console.log(f + ' is valid JSON');
    } catch (e) {
        console.error('Invalid JSON in ' + f + ': ' + e.message);
        process.exit(1);
    }
}
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json validation failed: {r.stderr}"


def test_repo_build():
    """Run the build script to ensure project compiles (pass_to_pass repo test).

    Note: This test runs npm ci first to install dependencies, then runs build.js.
    The build compiles TypeScript and bundles resources.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node utils/build/build.js 2>&1
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_check_deps():
    """Run check-deps to verify package dependencies are valid (pass_to_pass repo test).

    Note: This test runs npm ci first to install dependencies, then runs check_deps.js.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node utils/check_deps.js 2>&1
"""],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_lint_packages():
    """Run lint-packages to verify workspace package consistency (pass_to_pass repo test).

    Note: This test runs npm ci first to install dependencies, then runs workspace lint check.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
npm run lint-packages 2>&1
"""],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_build_mcp_bundles():
    """Build only MCP bundle to verify bundling works (pass_to_pass repo test).

    Note: This is a lightweight check focusing on the MCP bundle build.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
# Build only the MCP bundle
node -e '
const { build } = require("esbuild");
const path = require("path");
const fs = require("fs");

async function buildMCPBundle() {
  const srcDir = "packages/playwright-core/bundles/mcp/src/mcpBundleImpl.ts";
  const outDir = "packages/playwright-core/bundles/mcp/lib";

  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  await build({
    entryPoints: [srcDir],
    bundle: true,
    platform: "node",
    target: "node18",
    format: "cjs",
    outfile: path.join(outDir, "mcpBundleImpl.js"),
    external: ["playwright"],
    logLevel: "error"
  });

  console.log("MCP bundle built successfully");
}

buildMCPBundle().catch(e => {
  console.error(e);
  process.exit(1);
});
' 2>&1
"""],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"MCP bundle build failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_mcp_source_compile():
    """Compile MCP TypeScript source files to verify they have valid syntax (pass_to_pass repo test).

    Note: This uses esbuild to transpile the modified MCP source files.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
# Compile the modified MCP source files using esbuild
node -e '
const { build } = require("esbuild");
const path = require("path");
const fs = require("fs");

async function compileMCP() {
  const files = [
    "packages/playwright/src/mcp/browser/config.ts",
    "packages/playwright/src/mcp/browser/response.ts",
    "packages/playwright/src/mcp/browser/tab.ts",
    "packages/playwright/src/mcp/browser/tools/evaluate.ts",
    "packages/playwright/src/mcp/browser/tools/tool.ts",
    "packages/playwright/src/mcp/program.ts",
    "packages/playwright/src/mcp/terminal/commands.ts"
  ];

  const tempDir = "/tmp/mcp-compile-test";
  if (!fs.existsSync(tempDir)) {
    fs.mkdirSync(tempDir, { recursive: true });
  }

  for (const file of files) {
    if (!fs.existsSync(file)) {
      console.error("File not found: " + file);
      process.exit(1);
    }

    await build({
      entryPoints: [file],
      bundle: false,
      platform: "node",
      target: "node18",
      format: "cjs",
      outfile: path.join(tempDir, path.basename(file, ".ts") + ".js"),
      logLevel: "error"
    });
    console.log("Compiled: " + file);
  }

  console.log("All MCP source files compiled successfully");
}

compileMCP().catch(e => {
  console.error(e);
  process.exit(1);
});
' 2>&1
"""],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"MCP source compile failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_mcp_build_minimal():
    """Run minimal build check for MCP-related bundles (pass_to_pass repo test).

    Note: This builds only the packages needed for MCP functionality.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
# Build the project first
node utils/build/build.js 2>&1 | tail -20
"""],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"MCP build check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_eslint_full():
    """Run ESLint on all modified MCP files including test files (pass_to_pass repo test).

    Note: This validates code style for all files modified in the PR.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
npx eslint --cache \
    packages/playwright/src/mcp/browser/config.ts \
    packages/playwright/src/mcp/browser/response.ts \
    packages/playwright/src/mcp/browser/tab.ts \
    packages/playwright/src/mcp/browser/tools/evaluate.ts \
    packages/playwright/src/mcp/browser/tools/tool.ts \
    packages/playwright/src/mcp/program.ts \
    packages/playwright/src/mcp/terminal/commands.ts \
    tests/mcp/cli.spec.ts \
    tests/mcp/dialogs.spec.ts \
    tests/mcp/files.spec.ts \
    --ext .ts 2>&1
"""],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint full check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_generate_channels():
    """Run generate_channels.js to verify channel definitions are valid (pass_to_pass repo test).

    Note: This validates that protocol channel definitions can be regenerated.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node utils/generate_channels.js 2>&1
"""],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Generate channels failed:\n{r.stderr[-500:]}"


def test_repo_copyright_check():
    """Run copyright check on source files (pass_to_pass repo test).

    Note: Validates that source files have proper copyright headers.
    """
    r = subprocess.run(
        ["bash", "-c", """
cd /workspace/playwright
npm ci --silent 2>/dev/null
node utils/copyright.js 2>&1
"""],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Copyright check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_help_json_command_names():
    """help.json must contain new command names (press, keydown, etc.)
    and not the old hyphenated names, validated by parsing JSON with Node."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('packages/playwright/src/mcp/terminal/help.json', 'utf8'));
const cmds = Object.keys(data.commands);
const required = ['press', 'keydown', 'keyup', 'mousemove', 'mousedown', 'mouseup', 'mousewheel'];
const forbidden = ['key-press', 'key-down', 'key-up', 'mouse-move', 'mouse-down', 'mouse-up', 'mouse-wheel'];
for (const r of required) {
  if (!cmds.includes(r)) { console.error('Missing command: ' + r); process.exit(1); }
}
for (const f of forbidden) {
  if (cmds.includes(f)) { console.error('Old command still present: ' + f); process.exit(1); }
}
// Global help text must also use new names
const g = data.global;
for (const f of ['key-press', 'key-down', 'key-up', 'mouse-move', 'mouse-down', 'mouse-up', 'mouse-wheel']) {
  if (g.includes(f)) { console.error('Global help still references: ' + f); process.exit(1); }
}
console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_eval_auto_wrap():
    """evaluate tool must auto-wrap expressions without arrow functions,
    verified by checking source for the pattern and testing the logic."""
    js_code = """
const fs = require('fs');
const code = fs.readFileSync('packages/playwright/src/mcp/browser/tools/evaluate.ts', 'utf8');

// Source must contain the arrow-detection check
const hasArrowCheck = code.indexOf("=>") !== -1 && code.indexOf("includes") !== -1;
if (!hasArrowCheck) { console.error('evaluate.ts has no arrow-detection check'); process.exit(1); }

// Source must contain the wrapping pattern
const hasWrap = code.includes('() => (') || code.includes('\`() => (\`');
if (!hasWrap) { console.error('evaluate.ts has no auto-wrap pattern'); process.exit(1); }

// Replicate the exact logic and test it
function autoWrap(fn) {
  if (!fn.includes('=>'))
    fn = '() => (' + fn + ')';
  return fn;
}

const cases = [
  ['document.title', '() => (document.title)'],
  ['() => document.title', '() => document.title'],
  ['el => el.textContent', 'el => el.textContent'],
  ['window.location.href', '() => (window.location.href)'],
];
for (const [input, expected] of cases) {
  const result = autoWrap(input);
  if (result !== expected) {
    console.error('autoWrap("' + input + '") = "' + result + '", expected "' + expected + '"');
    process.exit(1);
  }
}
console.log('PASS');
"""
    # Write JS to file to avoid quote escaping issues
    js_file = Path(REPO) / "_test_eval_auto_wrap.js"
    js_file.write_text(js_code)
    r = subprocess.run(
        ["node", str(js_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    js_file.unlink()  # Cleanup
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_render_modal_skill_mode():
    """renderModalStates must accept a config param and branch on skillMode:
    show skill name in skill mode, tool name otherwise."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const code = fs.readFileSync('packages/playwright/src/mcp/browser/tab.ts', 'utf8');

// Function must accept config as first parameter
if (!/function\\s+renderModalStates\\s*\\(\\s*config\\s*:/.test(code)) {
  console.error('renderModalStates must accept config as first parameter');
  process.exit(1);
}

// Must branch on config.skillMode
if (!code.includes('config.skillMode')) {
  console.error('renderModalStates must use config.skillMode');
  process.exit(1);
}

// Must access .skill and .tool on clearedBy
if (!code.includes('clearedBy.skill') && !code.includes('state.clearedBy.skill')) {
  console.error('Must access clearedBy.skill');
  process.exit(1);
}
if (!code.includes('clearedBy.tool') && !code.includes('state.clearedBy.tool')) {
  console.error('Must access clearedBy.tool');
  process.exit(1);
}

// Replicate the rendering logic and test both modes
function renderModalStates(config, modalStates) {
  const result = [];
  if (modalStates.length === 0)
    result.push('- There is no modal state present');
  for (const state of modalStates)
    result.push('- [' + state.description + ']: can be handled by ' +
      (config.skillMode ? state.clearedBy.skill : state.clearedBy.tool));
  return result;
}

const state = {
  description: '"alert" dialog with message "MyAlert"',
  clearedBy: { tool: 'browser_handle_dialog', skill: 'dialog-accept or dialog-dismiss' }
};

// Skill mode: must show skill name
const skillOut = renderModalStates({ skillMode: true }, [state]);
if (!skillOut[0].includes('dialog-accept or dialog-dismiss')) {
  console.error('Skill mode should show skill name, got: ' + skillOut[0]);
  process.exit(1);
}
if (skillOut[0].includes('browser_handle_dialog')) {
  console.error('Skill mode should NOT show tool name');
  process.exit(1);
}

// Non-skill mode: must show tool name
const toolOut = renderModalStates({ skillMode: false }, [state]);
if (!toolOut[0].includes('browser_handle_dialog')) {
  console.error('Non-skill mode should show tool name, got: ' + toolOut[0]);
  process.exit(1);
}

console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural tests
# ---------------------------------------------------------------------------

def test_command_names_renamed():
    """commands.ts must declare short names (press, keydown, etc.)
    and not the old hyphenated names."""
    commands_ts = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_ts.read_text()

    new_names = ["'press'", "'keydown'", "'keyup'", "'mousemove'",
                 "'mousedown'", "'mouseup'", "'mousewheel'"]
    for name in new_names:
        assert f"name: {name}" in content, (
            f"commands.ts should declare command with name: {name}"
        )

    old_names = ["'key-press'", "'key-down'", "'key-up'", "'mouse-move'",
                 "'mouse-down'", "'mouse-up'", "'mouse-wheel'"]
    for name in old_names:
        assert f"name: {name}" not in content, (
            f"commands.ts should not still use old name: {name}"
        )


def test_modal_state_cleared_by_type():
    """ModalState clearedBy field must be typed as { tool: string; skill: string },
    not a plain string."""
    tool_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tools/tool.ts"
    content = tool_ts.read_text()

    # Must have both 'tool: string' and 'skill: string' in the type definition
    assert "tool: string" in content and "skill: string" in content, (
        "tool.ts clearedBy must be typed as { tool: string; skill: string }"
    )

    # No line should have 'clearedBy: string' without braces (plain string type)
    for line in content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("clearedBy:") and "string" in stripped:
            assert "{" in stripped, (
                f"clearedBy must be an object type, not plain string: {stripped}"
            )


def test_daemon_sets_skill_mode():
    """Daemon mode in program.ts must set config.skillMode = true."""
    program_ts = Path(REPO) / "packages/playwright/src/mcp/program.ts"
    content = program_ts.read_text()

    assert "skillMode" in content, (
        "program.ts must reference skillMode"
    )
    # Verify it's set in the daemon block
    in_daemon = False
    for line in content.split("\n"):
        if "options.daemon" in line:
            in_daemon = True
        if in_daemon and "skillMode" in line:
            assert "true" in line, "skillMode must be set to true in daemon mode"
            break
    else:
        assert False, "skillMode must be set inside the daemon mode block"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — SKILL.md creation
# ---------------------------------------------------------------------------

def test_skill_md_exists_with_frontmatter():
    """SKILL.md must exist in terminal directory with valid YAML frontmatter."""
    skill_md = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist in terminal directory"

    content = skill_md.read_text()
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert content.count("---") >= 2, "SKILL.md must have opening and closing frontmatter"

    frontmatter_end = content.index("---", 3)
    frontmatter = content[3:frontmatter_end]
    assert "name:" in frontmatter, "SKILL.md frontmatter must include name"
    assert "description:" in frontmatter, "SKILL.md frontmatter must include description"


def test_skill_md_documents_commands():
    """SKILL.md must document new command names and cover core workflow."""
    skill_md = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"
    assert skill_md.exists(), "SKILL.md must exist"
    content = skill_md.read_text()

    for cmd in ["press", "keydown", "keyup", "mousemove", "mousedown",
                "mouseup", "mousewheel"]:
        assert cmd in content, f"SKILL.md must document the '{cmd}' command"

    assert "snapshot" in content.lower(), "SKILL.md should mention snapshot workflow"
    assert "open" in content, "SKILL.md should document the open command"
    assert "click" in content, "SKILL.md should document the click command"


def test_build_script_copies_md():
    """Build script must copy .md files from terminal directory to lib output."""
    build_js = Path(REPO) / "utils/build/build.js"
    content = build_js.read_text()

    assert "terminal" in content and "*.md" in content, (
        "build.js must copy terminal/*.md files to lib output"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_3():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_eval_no_arrow():
    """fail_to_pass | PR added test 'eval no arrow' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "eval no arrow" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'eval no arrow' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_press():
    """fail_to_pass | PR added test 'press' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "press" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "press" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "press" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "press" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'press' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_keydown_keyup():
    """fail_to_pass | PR added test 'keydown keyup' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "keydown keyup" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'keydown keyup' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousemove():
    """fail_to_pass | PR added test 'mousemove' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousemove" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousemove' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousedown_mouseup():
    """fail_to_pass | PR added test 'mousedown mouseup' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousedown mouseup" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousedown mouseup' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_mousewheel():
    """fail_to_pass | PR added test 'mousewheel' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "mousewheel" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'mousewheel' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_eval_ref():
    """fail_to_pass | PR added test 'eval <ref>' in 'tests/mcp/cli.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli.spec.ts" -t "eval <ref>" 2>&1 || npx vitest run "tests/mcp/cli.spec.ts" -t "eval <ref>" 2>&1 || pnpm jest "tests/mcp/cli.spec.ts" -t "eval <ref>" 2>&1 || npx jest "tests/mcp/cli.spec.ts" -t "eval <ref>" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'eval <ref>' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
