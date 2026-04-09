"""
Task: playwright-chorecli-add-network-route
Repo: microsoft/playwright @ 824f63da57edf990c6eeab6301d5f1b65dcb4ca8
PR:   39071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"


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

# [static] pass_to_pass
def test_syntax_check():
    """Key source files must exist."""
    files = [
        f"{REPO}/packages/playwright/src/mcp/browser/context.ts",
        f"{REPO}/packages/playwright/src/mcp/browser/tools.ts",
        f"{REPO}/packages/playwright/src/mcp/terminal/command.ts",
        f"{REPO}/packages/playwright/src/mcp/terminal/commands.ts",
        f"{REPO}/packages/playwright/src/mcp/terminal/helpGenerator.ts",
        f"{REPO}/.claude/skills/playwright-mcp-dev/SKILL.md",
    ]
    for fpath in files:
        assert Path(fpath).exists(), f"File not found: {fpath}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — tool file per SKILL.md line 9
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:9
def test_route_tool_definition():
    """route.ts must exist with browser_route tool having correct schema fields."""
    r = _run_node("""
const fs = require('fs');
const path = 'packages/playwright/src/mcp/browser/tools/route.ts';
if (!fs.existsSync(path)) {
    console.error('FAIL: route.ts does not exist');
    process.exit(1);
}
const src = fs.readFileSync(path, 'utf8');

// Must define browser_route tool
if (!src.includes("name: 'browser_route'") && !src.includes('name: "browser_route"')) {
    console.error('FAIL: browser_route tool not defined');
    process.exit(1);
}

// Schema must include key fields
const requiredFields = ['pattern', 'status', 'body', 'contentType', 'headers', 'removeHeaders'];
for (const field of requiredFields) {
    if (!src.includes(field)) {
        console.error('FAIL: schema missing field: ' + field);
        process.exit(1);
    }
}

// Must use defineTool
if (!src.includes('defineTool')) {
    console.error('FAIL: must use defineTool');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_route_fulfill_and_continue():
    """browser_route handler must call fulfill for body/status, continue for headers."""
    r = _run_node("""
const fs = require('fs');
const path = 'packages/playwright/src/mcp/browser/tools/route.ts';
if (!fs.existsSync(path)) {
    console.error('FAIL: route.ts does not exist');
    process.exit(1);
}
const src = fs.readFileSync(path, 'utf8');

// Find browser_route tool handler
const toolMatch = src.match(/name:\\s*['"]browser_route['"]/);
if (!toolMatch) {
    console.error('FAIL: browser_route tool not found');
    process.exit(1);
}

const rest = src.slice(toolMatch.index);
const handleMatch = rest.match(/handle:\\s*async/);
if (!handleMatch) {
    console.error('FAIL: handle function not found');
    process.exit(1);
}

const fromHandle = rest.slice(handleMatch.index);
const braceStart = fromHandle.indexOf('{');
let depth = 0;
let handler = '';
for (let i = braceStart; i < fromHandle.length; i++) {
    if (fromHandle[i] === '{') depth++;
    if (fromHandle[i] === '}') { depth--; if (depth === 0) { handler = fromHandle.slice(braceStart, i + 1); break; } }
}

// Must call route.fulfill for body/status case
if (!handler.includes('.fulfill(')) {
    console.error('FAIL: handler must call route.fulfill() for mock responses');
    process.exit(1);
}

// Must call route.continue for header-only modification
if (!handler.includes('.continue(')) {
    console.error('FAIL: handler must call route.continue() for header modification');
    process.exit(1);
}

// Must check body/status to decide path
if (!handler.includes('body') || !handler.includes('status')) {
    console.error('FAIL: handler must check body/status');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_route_list_and_unroute_tools():
    """route.ts must define browser_route_list and browser_unroute tools."""
    r = _run_node("""
const fs = require('fs');
const path = 'packages/playwright/src/mcp/browser/tools/route.ts';
if (!fs.existsSync(path)) {
    console.error('FAIL: route.ts does not exist');
    process.exit(1);
}
const src = fs.readFileSync(path, 'utf8');

if (!src.includes("name: 'browser_route_list'") && !src.includes('name: "browser_route_list"')) {
    console.error('FAIL: browser_route_list tool not defined');
    process.exit(1);
}

if (!src.includes("name: 'browser_unroute'") && !src.includes('name: "browser_unroute"')) {
    console.error('FAIL: browser_unroute tool not defined');
    process.exit(1);
}

// route_list should handle empty state
if (!src.includes('No active routes')) {
    console.error('FAIL: route_list should handle empty state');
    process.exit(1);
}

// unroute should report removal
if (!src.includes('Removed') && !src.includes('removed')) {
    console.error('FAIL: unroute should report removal count');
    process.exit(1);
}

// Must have default export
if (!src.includes('export default')) {
    console.error('FAIL: must have default export');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_context_route_management():
    """context.ts must export RouteEntry and have addRoute/removeRoute/routes methods."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/context.ts', 'utf8');

// Must export RouteEntry type
if (!src.includes('export type RouteEntry') && !src.includes('export interface RouteEntry')) {
    console.error('FAIL: must export RouteEntry type');
    process.exit(1);
}

// RouteEntry must have pattern and handler fields
if (!src.match(/RouteEntry[\\s\\S]*?pattern.*string/)) {
    console.error('FAIL: RouteEntry must have pattern field');
    process.exit(1);
}

// Context must have addRoute method
if (!src.includes('addRoute')) {
    console.error('FAIL: Context must have addRoute method');
    process.exit(1);
}

// Context must have removeRoute method
if (!src.includes('removeRoute')) {
    console.error('FAIL: Context must have removeRoute method');
    process.exit(1);
}

// Context must have routes() accessor
if (!src.includes('routes()')) {
    console.error('FAIL: Context must have routes() method');
    process.exit(1);
}

// addRoute must delegate to browserContext.route
if (!src.includes('browserContext.route(') && !src.includes('browserContext.route (')) {
    console.error('FAIL: addRoute must call browserContext.route');
    process.exit(1);
}

// removeRoute must call unroute
if (!src.includes('.unroute(')) {
    console.error('FAIL: removeRoute must call unroute on browserContext');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — registration per SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:10
def test_route_tools_registered():
    """tools.ts must import and spread the route module."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/browser/tools.ts', 'utf8');

// Must import route module
if (!src.match(/import\\s+\\w+\\s+from\\s+['\\.\\/"]*tools\\/route['"]/) &&
    !src.match(/import\\s+route\\s+from/)) {
    console.error('FAIL: tools.ts must import route from ./tools/route');
    process.exit(1);
}

// Must spread route into browserTools
if (!src.includes('...route')) {
    console.error('FAIL: tools.ts must spread route into browserTools array');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:22-23
def test_network_category_and_help():
    """command.ts and helpGenerator.ts must include 'network' category."""
    r = _run_node("""
const fs = require('fs');

// Check command.ts Category type
const cmdSrc = fs.readFileSync('packages/playwright/src/mcp/terminal/command.ts', 'utf8');
if (!cmdSrc.includes("'network'") && !cmdSrc.includes('"network"')) {
    console.error('FAIL: command.ts Category type must include network');
    process.exit(1);
}

// Check helpGenerator.ts
const helpSrc = fs.readFileSync('packages/playwright/src/mcp/terminal/helpGenerator.ts', 'utf8');
if (!helpSrc.includes("'network'") && !helpSrc.includes('"network"')) {
    console.error('FAIL: helpGenerator.ts must include network category');
    process.exit(1);
}

if (!helpSrc.includes('Network')) {
    console.error('FAIL: helpGenerator.ts must have Network title');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [agent_config] fail_to_pass — .claude/skills/playwright-mcp-dev/SKILL.md:24
def test_cli_commands_registered():
    """commands.ts must declare route, route-list, unroute CLI commands."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright/src/mcp/terminal/commands.ts', 'utf8');

// Must have route command
if (!src.match(/name:\\s*['"]route['"]/)) {
    console.error('FAIL: must declare route command');
    process.exit(1);
}

// Must have route-list command
if (!src.match(/name:\\s*['"]route-list['"]/)) {
    console.error('FAIL: must declare route-list command');
    process.exit(1);
}

// Must have unroute command
if (!src.match(/name:\\s*['"]unroute['"]/)) {
    console.error('FAIL: must declare unroute command');
    process.exit(1);
}

// Route must map to browser_route tool
if (!src.includes("toolName: 'browser_route'") && !src.includes('toolName: "browser_route"')) {
    console.error('FAIL: route command must map to browser_route tool');
    process.exit(1);
}

// Commands must use network category
if (!src.includes("category: 'network'") && !src.includes('category: "network"')) {
    console.error('FAIL: route commands must use network category');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config update tests (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_building_section():
    """SKILL.md must have Building sections with development guidance."""
    skill_md = Path(REPO) / ".claude" / "skills" / "playwright-mcp-dev" / "SKILL.md"
    content = skill_md.read_text()

    assert "## Building" in content, \
        "SKILL.md must have a '## Building' section"
    assert "lint" in content.lower(), \
        "Building section should mention running lint"
    assert "watch" in content.lower(), \
        "Building section should mention watch mode"


# [pr_diff] fail_to_pass
def test_skill_md_lint_command():
    """SKILL.md lint command must use 'npm run flint' (not 'flint:mcp')."""
    skill_md = Path(REPO) / ".claude" / "skills" / "playwright-mcp-dev" / "SKILL.md"
    content = skill_md.read_text()

    assert "Lint" in content, "SKILL.md must have a Lint section"
    assert "flint:mcp" not in content, \
        "Lint section must use 'npm run flint', not 'npm run flint:mcp'"


# ---------------------------------------------------------------------------
# Pass-to-pass gates from repo CI/CD
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - TypeScript compilation
def test_repo_typecheck():
    """Repo TypeScript compilation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "-p", "."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass - Dependency check
def test_repo_check_deps():
    """Repo dependency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependency check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass - ESLint on MCP files
def test_repo_lint_mcp():
    """ESLint on MCP files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--cache", "packages/playwright/src/mcp/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on MCP files failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass - Package consistency
def test_repo_lint_packages():
    """Repo package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package consistency check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass - Test linting
def test_repo_lint_tests():
    """Repo test linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test linting failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass - Build verification
def test_repo_build():
    """Repo build passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"
