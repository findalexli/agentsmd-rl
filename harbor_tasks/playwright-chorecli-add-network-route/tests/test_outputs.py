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


def _ensure_built():
    """Build the project once (idempotent via sentinel file)."""
    sentinel = Path(REPO) / ".eval_built"
    if sentinel.exists():
        return
    subprocess.run(
        ["npm", "ci"], capture_output=True, text=True, timeout=300, cwd=REPO
    )
    r = subprocess.run(
        ["npm", "run", "build"], capture_output=True, text=True, timeout=300, cwd=REPO
    )
    if r.returncode == 0:
        sentinel.write_text("ok")


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
# Fail-to-pass (agent_config) — tool module per SKILL.md line 9
# ---------------------------------------------------------------------------

def test_route_tool_definition():
    """Route tool module must export browser_route tool with correct schema fields."""
    _ensure_built()
    r = _run_node("""
const routeModule = require('./packages/playwright/lib/mcp/browser/tools/route');
const tools = routeModule.default || (Array.isArray(routeModule) ? routeModule : null);
if (!tools || !Array.isArray(tools)) {
    console.error('FAIL: route module must export an array of tool definitions');
    process.exit(1);
}

const browserRoute = tools.find(t => t.schema && t.schema.name === 'browser_route');
if (!browserRoute) {
    console.error('FAIL: browser_route tool not found in exports');
    process.exit(1);
}

// Verify schema has required input fields
const shape = browserRoute.schema.inputSchema.shape;
const requiredFields = ['pattern', 'status', 'body', 'contentType', 'headers', 'removeHeaders'];
for (const field of requiredFields) {
    if (!(field in shape)) {
        console.error('FAIL: schema missing field: ' + field);
        process.exit(1);
    }
}

if (typeof browserRoute.handle !== 'function') {
    console.error('FAIL: browser_route must have a handle function');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_route_fulfill_and_continue():
    """browser_route handler must call fulfill for body/status, continue for headers."""
    _ensure_built()
    r = _run_node("""
const routeModule = require('./packages/playwright/lib/mcp/browser/tools/route');
const contextModule = require('./packages/playwright/lib/mcp/browser/context');
const tools = routeModule.default || routeModule;
const routeTool = tools.find(t => t.schema && t.schema.name === 'browser_route');
if (!routeTool) {
    console.error('FAIL: browser_route tool not found');
    process.exit(1);
}

// Discover route methods from Context prototype (flexible naming)
const proto = contextModule.Context.prototype;
const methods = Object.getOwnPropertyNames(proto).filter(n => typeof proto[n] === 'function');
const routeMethods = methods.filter(n => /route/i.test(n));
const listMethod = routeMethods.find(n => /^(get)?routes?$/i.test(n) || /^list/i.test(n));
const removeMethod = routeMethods.find(n => /remove|delete|un/i.test(n));
const addMethod = routeMethods.find(n => n !== listMethod && n !== removeMethod);
if (!addMethod) {
    console.error('FAIL: Context must have a method to add routes');
    process.exit(1);
}

(async () => {
    let capturedEntry = null;
    const mockContext = {};
    mockContext[addMethod] = (entry) => { capturedEntry = entry; return Promise.resolve(); };
    const mockResponse = { addTextResult: () => {}, addCode: () => {} };

    // Test 1: fulfill path (body + status provided)
    await routeTool.handle(mockContext, { pattern: '**/test', body: 'hello', status: 200 }, mockResponse);
    if (!capturedEntry || typeof capturedEntry.handler !== 'function') {
        console.error('FAIL: handle must create a route entry with a handler function');
        process.exit(1);
    }

    let fulfillCalled = false;
    let continueCalled = false;
    const mockRoute = {
        fulfill: (opts) => { fulfillCalled = true; return Promise.resolve(); },
        continue: (opts) => { continueCalled = true; return Promise.resolve(); },
        request: () => ({ headers: () => ({}) }),
    };

    await capturedEntry.handler(mockRoute);
    if (!fulfillCalled) {
        console.error('FAIL: handler must call fulfill when body/status are provided');
        process.exit(1);
    }

    // Test 2: continue path (only headers, no body/status)
    capturedEntry = null;
    fulfillCalled = false;
    continueCalled = false;
    await routeTool.handle(mockContext, { pattern: '**/test2', headers: ['X-Custom: value'] }, mockResponse);
    if (!capturedEntry || typeof capturedEntry.handler !== 'function') {
        console.error('FAIL: handle must create a route entry for header modification');
        process.exit(1);
    }
    await capturedEntry.handler(mockRoute);
    if (!continueCalled) {
        console.error('FAIL: handler must call continue when only headers are specified');
        process.exit(1);
    }

    console.log('PASS');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_route_list_and_unroute_tools():
    """browser_route_list and browser_unroute tools must behave correctly."""
    _ensure_built()
    r = _run_node("""
const routeModule = require('./packages/playwright/lib/mcp/browser/tools/route');
const contextModule = require('./packages/playwright/lib/mcp/browser/context');
const tools = routeModule.default || routeModule;

const listTool = tools.find(t => t.schema && t.schema.name === 'browser_route_list');
if (!listTool) { console.error('FAIL: browser_route_list not defined'); process.exit(1); }
const unrouteTool = tools.find(t => t.schema && t.schema.name === 'browser_unroute');
if (!unrouteTool) { console.error('FAIL: browser_unroute not defined'); process.exit(1); }

// Discover method names from Context prototype (flexible naming)
const proto = contextModule.Context.prototype;
const methods = Object.getOwnPropertyNames(proto).filter(n => typeof proto[n] === 'function');
const routeMethods = methods.filter(n => /route/i.test(n));
const listMethod = routeMethods.find(n => /^(get)?routes?$/i.test(n) || /^list/i.test(n));
const removeMethod = routeMethods.find(n => /remove|delete|un/i.test(n));

if (!listMethod || !removeMethod) {
    console.error('FAIL: Context must have routes listing and removal methods');
    process.exit(1);
}

(async () => {
    // Test: route_list with empty routes returns "No active routes"
    let resultText = '';
    const mockResponse = { addTextResult: (t) => { resultText = t; }, addCode: () => {} };
    const emptyContext = {};
    emptyContext[listMethod] = () => [];
    await listTool.handle(emptyContext, {}, mockResponse);
    if (!resultText.includes('No active routes')) {
        console.error('FAIL: route_list should return "No active routes" when empty, got: ' + resultText);
        process.exit(1);
    }

    // Test: unroute reports removal count
    resultText = '';
    const removeContext = {};
    removeContext[removeMethod] = () => Promise.resolve(2);
    await unrouteTool.handle(removeContext, {}, mockResponse);
    if (!resultText.includes('Removed') || !resultText.includes('2')) {
        console.error('FAIL: unroute should report removal count, got: ' + resultText);
        process.exit(1);
    }

    console.log('PASS');
})().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_context_route_management():
    """Context class must have route management capabilities."""
    _ensure_built()
    r = _run_node("""
const contextModule = require('./packages/playwright/lib/mcp/browser/context');

if (!contextModule.Context) {
    console.error('FAIL: Context class not found in exports');
    process.exit(1);
}

const proto = contextModule.Context.prototype;
const methods = Object.getOwnPropertyNames(proto).filter(
    n => typeof proto[n] === 'function'
);

// Must have at least 3 route-related methods (add, remove, list)
const routeMethods = methods.filter(n => /route/i.test(n));
if (routeMethods.length < 3) {
    console.error('FAIL: Context must have at least 3 route management methods, found: ' + routeMethods.join(', '));
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — registration per SKILL.md
# ---------------------------------------------------------------------------

def test_route_tools_registered():
    """Route tools must be registered in the main browserTools array."""
    _ensure_built()
    r = _run_node("""
const { browserTools } = require('./packages/playwright/lib/mcp/browser/tools');
if (!Array.isArray(browserTools)) {
    console.error('FAIL: browserTools must be an array');
    process.exit(1);
}

const toolNames = browserTools.map(t => t.schema.name);
for (const name of ['browser_route', 'browser_route_list', 'browser_unroute']) {
    if (!toolNames.includes(name)) {
        console.error('FAIL: browserTools missing tool: ' + name);
        process.exit(1);
    }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_network_category_and_help():
    """Help system must include network category with Network title."""
    _ensure_built()
    r = _run_node("""
const helpModule = require('./packages/playwright/lib/mcp/terminal/helpGenerator');
const cmdsModule = require('./packages/playwright/lib/mcp/terminal/commands');

const helpText = helpModule.generateHelp(cmdsModule.commands);
if (!helpText.includes('Network')) {
    console.error('FAIL: help output must include Network category title');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_cli_commands_registered():
    """Commands module must declare route, route-list, unroute CLI commands."""
    _ensure_built()
    r = _run_node("""
const cmdsModule = require('./packages/playwright/lib/mcp/terminal/commands');
const cmds = cmdsModule.commands;
if (!cmds || typeof cmds !== 'object') {
    console.error('FAIL: commands must export a commands object');
    process.exit(1);
}

for (const name of ['route', 'route-list', 'unroute']) {
    if (!cmds[name]) {
        console.error('FAIL: missing CLI command: ' + name);
        process.exit(1);
    }
}

// Route commands must use network category
for (const name of ['route', 'route-list', 'unroute']) {
    if (cmds[name].category !== 'network') {
        console.error('FAIL: ' + name + ' must have network category, got: ' + cmds[name].category);
        process.exit(1);
    }
}

// route must map to browser_route tool
if (cmds['route'].toolName !== 'browser_route') {
    console.error('FAIL: route command must map to browser_route tool');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Config update tests (pr_diff)
# ---------------------------------------------------------------------------

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

def test_repo_typecheck():
    """Repo TypeScript compilation passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["npm", "run", "tsc"], capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-1000:]}"


def test_repo_lint_packages():
    """Repo package consistency check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package consistency check failed:\n{r.stderr[-1000:]}"


def test_repo_build():
    """Repo build passes (pass_to_pass)."""
    _ensure_built()
    lib_mcp = Path(REPO) / "packages" / "playwright" / "lib" / "mcp"
    assert lib_mcp.is_dir(), f"Build output not found at {lib_mcp}"
    tools_js = lib_mcp / "browser" / "tools.js"
    assert tools_js.exists(), "Compiled tools.js not found after build"


def test_repo_test_types():
    """Repo test types check passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["npm", "run", "test-types"], capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Test types check failed:\n{r.stderr[-1000:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_playwright_driver_npm():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_playwright_driver_npm_2():
    """pass_to_pass | CI job 'build-playwright-driver' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
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

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_route_list_shows_no_routes_when_empty():
    """fail_to_pass | PR added test 'route-list shows no routes when empty' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "route-list shows no routes when empty" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "route-list shows no routes when empty" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "route-list shows no routes when empty" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "route-list shows no routes when empty" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'route-list shows no routes when empty' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_route_adds_a_mock_and_route_list_shows_it():
    """fail_to_pass | PR added test 'route adds a mock and route-list shows it' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "route adds a mock and route-list shows it" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "route adds a mock and route-list shows it" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "route adds a mock and route-list shows it" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "route adds a mock and route-list shows it" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'route adds a mock and route-list shows it' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_route_with_content_type():
    """fail_to_pass | PR added test 'route with content-type' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "route with content-type" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "route with content-type" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "route with content-type" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "route with content-type" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'route with content-type' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_route_with_header():
    """fail_to_pass | PR added test 'route with header' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "route with header" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "route with header" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "route with header" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "route with header" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'route with header' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_unroute_removes_specific_route():
    """fail_to_pass | PR added test 'unroute removes specific route' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "unroute removes specific route" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "unroute removes specific route" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "unroute removes specific route" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "unroute removes specific route" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'unroute removes specific route' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_unroute_removes_all_routes():
    """fail_to_pass | PR added test 'unroute removes all routes' in 'tests/mcp/cli-route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/cli-route.spec.ts" -t "unroute removes all routes" 2>&1 || npx vitest run "tests/mcp/cli-route.spec.ts" -t "unroute removes all routes" 2>&1 || pnpm jest "tests/mcp/cli-route.spec.ts" -t "unroute removes all routes" 2>&1 || npx jest "tests/mcp/cli-route.spec.ts" -t "unroute removes all routes" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'unroute removes all routes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_route_mocks_response_with_JSON_body():
    """fail_to_pass | PR added test 'browser_route mocks response with JSON body' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_route mocks response with JSON body" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_route mocks response with JSON body" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_route mocks response with JSON body" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_route mocks response with JSON body" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_route mocks response with JSON body' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_route_mocks_response_with_custom_status():
    """fail_to_pass | PR added test 'browser_route mocks response with custom status' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_route mocks response with custom status" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_route mocks response with custom status" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_route mocks response with custom status" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_route mocks response with custom status" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_route mocks response with custom status' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_route_modifies_request_headers():
    """fail_to_pass | PR added test 'browser_route modifies request headers' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_route modifies request headers" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_route modifies request headers" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_route modifies request headers" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_route modifies request headers" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_route modifies request headers' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_route_list_shows_active_routes():
    """fail_to_pass | PR added test 'browser_route_list shows active routes' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_route_list shows active routes" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_route_list shows active routes" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_route_list shows active routes" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_route_list shows active routes" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_route_list shows active routes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_unroute_removes_specific_route():
    """fail_to_pass | PR added test 'browser_unroute removes specific route' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_unroute removes specific route" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_unroute removes specific route" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_unroute removes specific route" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_unroute removes specific route" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_unroute removes specific route' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_browser_unroute_removes_all_routes():
    """fail_to_pass | PR added test 'browser_unroute removes all routes' in 'tests/mcp/route.spec.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "tests/mcp/route.spec.ts" -t "browser_unroute removes all routes" 2>&1 || npx vitest run "tests/mcp/route.spec.ts" -t "browser_unroute removes all routes" 2>&1 || pnpm jest "tests/mcp/route.spec.ts" -t "browser_unroute removes all routes" 2>&1 || npx jest "tests/mcp/route.spec.ts" -t "browser_unroute removes all routes" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'browser_unroute removes all routes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
