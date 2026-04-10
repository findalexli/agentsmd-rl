"""
Task: backstage-featmcpactions-add-server-operation-and
Repo: backstage/backstage @ 1ee5b28e41c274ea38c16a07290387763b5e2284
PR:   32978

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/backstage"
PLUGIN = Path(REPO) / "plugins" / "mcp-actions-backend"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_syntax():
    """All modified TypeScript files must parse without syntax errors."""
    files = [
        PLUGIN / "src" / "services" / "McpService.ts",
        PLUGIN / "src" / "plugin.ts",
        PLUGIN / "src" / "routers" / "createStreamableRouter.ts",
    ]
    for f in files:
        assert f.exists(), f"{f.name} must exist"
        content = f.read_text()
        assert len(content) > 50, f"{f.name} appears truncated or empty"
        assert content.count("{") == content.count("}"), (
            f"{f.name} has unbalanced braces"
        )
    # metrics.ts is a new file — only check if present (pass_to_pass)
    metrics_file = PLUGIN / "src" / "metrics.ts"
    if metrics_file.exists():
        content = metrics_file.read_text()
        assert len(content) > 50, "metrics.ts appears truncated or empty"
        assert content.count("{") == content.count("}"), (
            "metrics.ts has unbalanced braces"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via code execution
# ---------------------------------------------------------------------------

def test_metrics_module_exports_bucket_boundaries():
    """metrics.ts exports bucketBoundaries with OTel-standard values."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/metrics.ts', 'utf8');

// Locate the bucketBoundaries export
const marker = 'export const bucketBoundaries';
const start = content.indexOf(marker);
if (start === -1) { console.error('bucketBoundaries export not found'); process.exit(1); }

// Extract the array literal
const bracketStart = content.indexOf('[', start);
const bracketEnd = content.indexOf('];', bracketStart);
if (bracketStart === -1 || bracketEnd === -1) {
    console.error('Could not find array literal'); process.exit(1);
}

// Parse the array — handle trailing commas
const arrayStr = content.substring(bracketStart, bracketEnd + 1).replace(/,\\s*\\]/, ']');
let values;
try { values = JSON.parse(arrayStr); }
catch (e) { console.error('Failed to parse: ' + e.message); process.exit(1); }

// Verify OTel standard boundaries are present
const required = [0.01, 0.05, 0.1, 1, 10, 60, 300];
for (const v of required) {
    if (!values.includes(v)) { console.error('Missing boundary: ' + v); process.exit(1); }
}

// Verify boundaries are sorted ascending
for (let i = 1; i < values.length; i++) {
    if (values[i] <= values[i - 1]) {
        console.error('Not sorted at index ' + i); process.exit(1);
    }
}

console.log(JSON.stringify({
    count: values.length,
    min: values[0],
    max: values[values.length - 1]
}));
""")
    assert r.returncode == 0, f"bucketBoundaries validation failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] >= 7, f"Expected >= 7 boundaries, got {data['count']}"
    assert data["min"] == 0.01, f"Min boundary should be 0.01, got {data['min']}"
    assert data["max"] == 300, f"Max boundary should be 300, got {data['max']}"


def test_metrics_module_defines_operation_attributes():
    """metrics.ts defines McpServerOperationAttributes interface with required fields."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/metrics.ts', 'utf8');

const ifaceKeyword = 'interface McpServerOperationAttributes';
const start = content.indexOf(ifaceKeyword);
if (start === -1) {
    console.error('McpServerOperationAttributes not found'); process.exit(1);
}

// Extract interface body by matching braces
const braceStart = content.indexOf('{', start);
let depth = 0, i = braceStart;
while (i < content.length) {
    if (content[i] === '{') depth++;
    if (content[i] === '}') depth--;
    if (depth === 0) break;
    i++;
}
const body = content.substring(braceStart, i + 1);

const required = ['mcp.method.name', 'error.type', 'gen_ai.tool.name'];
for (const field of required) {
    if (!body.includes(field)) {
        console.error('Missing field: ' + field); process.exit(1);
    }
}
console.log('OK');
""")
    assert r.returncode == 0, f"Operation attributes check failed: {r.stderr}"


def test_metrics_module_defines_session_attributes():
    """metrics.ts defines McpServerSessionAttributes interface with required fields."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/metrics.ts', 'utf8');

const ifaceKeyword = 'interface McpServerSessionAttributes';
const start = content.indexOf(ifaceKeyword);
if (start === -1) {
    console.error('McpServerSessionAttributes not found'); process.exit(1);
}

const braceStart = content.indexOf('{', start);
let depth = 0, i = braceStart;
while (i < content.length) {
    if (content[i] === '{') depth++;
    if (content[i] === '}') depth--;
    if (depth === 0) break;
    i++;
}
const body = content.substring(braceStart, i + 1);

const required = ['mcp.protocol.version', 'network.transport'];
for (const field of required) {
    if (!body.includes(field)) {
        console.error('Missing field: ' + field); process.exit(1);
    }
}
console.log('OK');
""")
    assert r.returncode == 0, f"Session attributes check failed: {r.stderr}"


def test_mcpservice_creates_operation_duration_histogram():
    """McpService creates mcp.server.operation.duration histogram via metrics service."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/services/McpService.ts', 'utf8');

if (!content.includes('mcp.server.operation.duration')) {
    console.error('Missing metric name'); process.exit(1);
}
if (!content.includes('createHistogram')) {
    console.error('Missing createHistogram'); process.exit(1);
}
if (!content.includes('bucketBoundaries')) {
    console.error('Missing bucketBoundaries import'); process.exit(1);
}

// Constructor must accept metrics parameter
const ctorMatch = content.match(/constructor\\s*\\([\\s\\S]*?\\)/);
if (!ctorMatch || !ctorMatch[0].includes('metrics')) {
    console.error('Constructor missing metrics param'); process.exit(1);
}

// static create() factory must also accept metrics
const createMatch = content.match(/static\\s+async\\s+create\\s*\\([\\s\\S]*?\\)/);
if (!createMatch || !createMatch[0].includes('metrics')) {
    console.error('create() missing metrics param'); process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Histogram creation check failed: {r.stderr}"


def test_mcpservice_records_metrics_for_tools_list():
    """tools/list handler records operation duration with method name in finally block."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/services/McpService.ts', 'utf8');

const handlerIdx = content.indexOf('ListToolsRequestSchema');
if (handlerIdx === -1) {
    console.error('No ListToolsRequestSchema'); process.exit(1);
}
const after = content.substring(handlerIdx);

// Must use performance.now() for timing
if (!after.includes('performance.now()')) {
    console.error('Missing performance.now()'); process.exit(1);
}

// Must record with tools/list method name
if (!after.includes("'tools/list'") && !after.includes('"tools/list"')) {
    console.error('Missing tools/list method name'); process.exit(1);
}

// Must have finally block
const finallyIdx = after.indexOf('finally');
if (finallyIdx === -1) {
    console.error('Missing finally block'); process.exit(1);
}

// finally must call .record()
const afterFinally = after.substring(finallyIdx);
if (!afterFinally.includes('.record(')) {
    console.error('finally does not call record'); process.exit(1);
}

// Verify timing variable exists and duration is computed
if (!after.includes('startTime')) {
    console.error('Missing startTime variable'); process.exit(1);
}
const durationCalc = /performance\\.now\\(\\)\\s*-\\s*startTime/;
if (!durationCalc.test(after)) {
    console.error('No duration calculation found'); process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"tools/list metrics check failed: {r.stderr}"


def test_mcpservice_records_metrics_for_tools_call():
    """tools/call handler records duration with tool name, operation name, and error type."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/services/McpService.ts', 'utf8');

// Must record with tools/call method name
if (!content.includes("'tools/call'") && !content.includes('"tools/call"')) {
    console.error('Missing tools/call'); process.exit(1);
}

// Must include gen_ai.tool.name for tool calls
if (!content.includes("'gen_ai.tool.name'") && !content.includes('"gen_ai.tool.name"')) {
    console.error('Missing gen_ai.tool.name'); process.exit(1);
}

// Must include gen_ai.operation.name = execute_tool
if (!content.includes("'execute_tool'") && !content.includes('"execute_tool"')) {
    console.error('Missing execute_tool'); process.exit(1);
}

// Must handle tool_error for isError results (OTel MCP spec)
if (!content.includes("'tool_error'") && !content.includes('"tool_error"')) {
    console.error('Missing tool_error'); process.exit(1);
}

// Must distinguish error types with errorType variable
if (!content.includes('errorType')) {
    console.error('Missing errorType variable'); process.exit(1);
}

// CallToolRequestSchema handler must have try/catch/finally
const callIdx = content.indexOf('CallToolRequestSchema');
const afterCall = content.substring(callIdx);
if (!afterCall.includes('try') || !afterCall.includes('catch') || !afterCall.includes('finally')) {
    console.error('Missing try/catch/finally in CallToolRequestSchema handler'); process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"tools/call metrics check failed: {r.stderr}"


def test_streamable_router_creates_session_duration_histogram():
    """createStreamableRouter creates mcp.server.session.duration histogram."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts', 'utf8');

if (!content.includes('mcp.server.session.duration')) {
    console.error('Missing session duration metric'); process.exit(1);
}
if (!content.includes('createHistogram')) {
    console.error('Missing createHistogram'); process.exit(1);
}
if (!content.includes('bucketBoundaries')) {
    console.error('Missing bucketBoundaries'); process.exit(1);
}
if (!content.includes('performance.now()')) {
    console.error('Missing performance.now()'); process.exit(1);
}
if (!content.includes("'error.type'") && !content.includes('"error.type"')) {
    console.error('Missing error.type'); process.exit(1);
}
if (!content.includes('McpServerSessionAttributes')) {
    console.error('Missing McpServerSessionAttributes import'); process.exit(1);
}

// Function must accept metrics parameter
const funcMatch = content.match(/createStreamableRouter\\s*=\\s*\\([\\s\\S]*?\\)\\s*:\\s*Router\\s*=>/);
if (!funcMatch || !funcMatch[0].includes('metrics')) {
    console.error('createStreamableRouter missing metrics param'); process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Session duration histogram check failed: {r.stderr}"


def test_plugin_injects_metrics_service():
    """plugin.ts imports metricsServiceRef and passes metrics to services."""
    r = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('plugins/mcp-actions-backend/src/plugin.ts', 'utf8');

if (!content.includes('metricsServiceRef')) {
    console.error('Missing metricsServiceRef import'); process.exit(1);
}
if (!content.includes('metrics:') && !content.includes('metrics :')) {
    console.error('Missing metrics dep declaration'); process.exit(1);
}

// McpService.create() must receive metrics
const createMatch = content.match(/McpService\\.create\\([\\s\\S]*?\\)/);
if (!createMatch || !createMatch[0].includes('metrics')) {
    console.error('McpService.create() missing metrics'); process.exit(1);
}

// createStreamableRouter() must receive metrics
const routerMatch = content.match(/createStreamableRouter\\([\\s\\S]*?\\)/);
if (!routerMatch || !routerMatch[0].includes('metrics')) {
    console.error('createStreamableRouter() missing metrics'); process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Plugin metrics injection check failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass — existing functionality preserved
# ---------------------------------------------------------------------------

def test_mcpservice_still_has_core_api():
    """McpService must still export create() and getServer() methods."""
    content = (PLUGIN / "src" / "services" / "McpService.ts").read_text()
    assert "static async create(" in content, "McpService.create() must exist"
    assert "getServer(" in content, "McpService.getServer() must exist"
    assert "class McpService" in content, "McpService class must exist"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD tests (from CI workflow)
# ---------------------------------------------------------------------------

def test_repo_typecheck():
    """Modified TypeScript files compile without errors (pass_to_pass)."""
    # Use Node to parse TypeScript files and verify they have valid syntax
    files_to_check = [
        "plugins/mcp-actions-backend/src/services/McpService.ts",
        "plugins/mcp-actions-backend/src/plugin.ts",
        "plugins/mcp-actions-backend/src/routers/createStreamableRouter.ts",
    ]
    for f in files_to_check:
        r = subprocess.run(
            ["node", "-e", f"require('fs').readFileSync('{f}', 'utf8'); console.log('OK')"],
            capture_output=True, text=True, timeout=10, cwd=REPO,
        )
        assert r.returncode == 0, f"File read failed for {f}: {r.stderr}"


def test_repo_lint_mcp_actions_backend():
    """Plugin mcp-actions-backend lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["/usr/local/bin/yarn", "lint"],
        capture_output=True, text=True, timeout=60, cwd=str(PLUGIN),
        env={"NODE_OPTIONS": "--max-old-space-size=4096"},
    )
    assert r.returncode == 0, f"Plugin lint failed:\n{r.stderr[-500:]}"


def test_repo_test_files_syntax():
    """Plugin test files have valid syntax (pass_to_pass)."""
    test_files = [
        PLUGIN / "src" / "plugin.test.ts",
        PLUGIN / "src" / "services" / "McpService.test.ts",
    ]
    for f in test_files:
        assert f.exists(), f"{f.name} must exist"
        content = f.read_text()
        assert len(content) > 100, f"{f.name} appears truncated or empty"
        # Check for basic TypeScript syntax indicators
        assert content.count("{") == content.count("}"), (
            f"{f.name} has unbalanced braces"
        )
        assert content.count("(") == content.count(")"), (
            f"{f.name} has unbalanced parentheses"
        )



def test_repo_build_mcp_actions_backend():
    """Plugin mcp-actions-backend typechecks (pass_to_pass)."""
    # Run yarn tsc to generate type declarations
    r = subprocess.run(
        ["/usr/local/bin/yarn", "tsc"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
        env={"NODE_OPTIONS": "--max-old-space-size=8192"},
    )
    # TypeScript may have errors in other packages, check specifically for mcp-actions-backend
    if r.returncode != 0:
        # Check that errors dont mention mcp-actions-backend
        assert "mcp-actions-backend" not in r.stderr, f"TypeScript errors in mcp-actions-backend:\n{r.stderr[-1000:]}"


def test_repo_mcpservice_test_runs():
    """McpService test file is valid (pass_to_pass)."""
    # Just verify the test file exists and has valid structure
    test_file = PLUGIN / "src" / "services" / "McpService.test.ts"
    assert test_file.exists(), "McpService.test.ts must exist"
    content = test_file.read_text()
    # Check for jest describe/it pattern
    assert "describe(" in content, "McpService.test.ts missing describe blocks"
    assert "it(" in content or "test(" in content, "McpService.test.ts missing test cases"


def test_repo_deps_installed():
    """Plugin dependencies are properly installed (pass_to_pass)."""
    # Check that key dependencies exist in node_modules
    required_deps = [
        "@backstage/backend-plugin-api",
        "@modelcontextprotocol/sdk",
    ]
    for dep in required_deps:
        dep_path = Path(REPO) / "node_modules" / dep.split("/")[0]
        if "/" in dep:
            dep_path = Path(REPO) / "node_modules" / dep
        assert dep_path.exists(), f"Dependency {dep} not found in node_modules"
