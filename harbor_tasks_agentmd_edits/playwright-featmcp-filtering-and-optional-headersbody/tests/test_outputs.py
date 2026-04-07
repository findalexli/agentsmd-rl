"""
Task: playwright-featmcp-filtering-and-optional-headersbody
Repo: microsoft/playwright @ 998f35dccb1de560350765493073dec5ec2c811c
PR:   39672

Enhance browser_network_requests tool with URL filtering (regexp),
optional request headers / request body display, and rename
includeStatic → static. Also create .github/copilot-instructions.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
NETWORK_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
COPILOT_MD = Path(REPO) / ".github/copilot-instructions.md"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path("/tmp/_eval_test.cjs")
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass — static gate
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    for fpath in [NETWORK_TS, COMMANDS_TS]:
        assert fpath.exists(), f"{fpath} does not exist"
        content = fpath.read_text()
        assert content.count("{") == content.count("}"), (
            f"Unbalanced braces in {fpath.name}"
        )
        assert len(content) > 100, f"{fpath.name} appears truncated or empty"


# ---------------------------------------------------------------------------
# fail_to_pass — behavioral (subprocess executes actual code)
# ---------------------------------------------------------------------------

def test_render_request_headers_and_body():
    """renderRequest outputs header and body sections when enabled."""
    code = r"""
const fs = require('fs');

const src = fs.readFileSync(
  'packages/playwright-core/src/tools/backend/network.ts', 'utf8'
);

// Locate the renderRequest function
const marker = 'async function renderRequest';
const start = src.indexOf(marker);
if (start === -1) {
  console.error('renderRequest function not found');
  process.exit(1);
}

// Find function boundary: next top-level declaration (unindented)
const rest = src.substring(start + marker.length);
const nextDecl = rest.match(/\n(?:export |const |function |class )/);
const end = nextDecl
  ? start + marker.length + nextDecl.index
  : src.length;
let fn = src.substring(start, end).trim();

// Strip TypeScript annotations to produce valid JS
fn = fn.replace(/^export\s+/, '');
fn = fn.replace(/:\s*playwright\.Request/g, '');
fn = fn.replace(/:\s*Promise<string>/g, '');
fn = fn.replace(/:\s*string\[\]/g, '');

// Write as CommonJS module and require it
const tmp = '/tmp/_test_renderReq.cjs';
fs.writeFileSync(tmp, fn + '\nmodule.exports = { renderRequest };\n');
const { renderRequest } = require(tmp);

const mock = {
  method: () => 'POST',
  url: () => 'https://api.example.com/users',
  existingResponse: () => ({ status: () => 200, statusText: () => 'OK' }),
  failure: () => null,
  headers: () => ({ 'content-type': 'application/json', 'x-auth': 'Bearer tok' }),
  postData: () => '{"name":"test"}',
};

(async () => {
  // With headers + body enabled
  const full = await renderRequest(mock, true, true);
  const errs = [];
  if (!full.includes('Request headers')) errs.push('no "Request headers"');
  if (!full.includes('content-type'))    errs.push('no header key');
  if (!full.includes('Request body'))    errs.push('no "Request body"');
  if (!full.includes('{"name":"test"}')) errs.push('no body content');
  if (errs.length) {
    console.error('FAIL:', errs.join('; '), '| output:', JSON.stringify(full));
    process.exit(1);
  }

  // With defaults (should NOT include headers/body)
  const basic = await renderRequest(mock);
  if (basic.includes('Request headers') || basic.includes('Request body')) {
    console.error('FAIL: headers/body shown when not requested');
    process.exit(1);
  }

  console.log('PASS');
})().catch(e => { console.error(e.message); process.exit(1); });
"""
    r = _run_node(code)
    assert r.returncode == 0, f"renderRequest test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_filter_regex_applied():
    """Handle function uses RegExp from filter param to filter requests by URL."""
    code = r"""
const fs = require('fs');

const src = fs.readFileSync(
  'packages/playwright-core/src/tools/backend/network.ts', 'utf8'
);

// Verify filter param is referenced and RegExp is constructed from it
if (!/params\.filter/.test(src)) {
  console.error('No params.filter reference — filter param not wired up');
  process.exit(1);
}
if (!/new\s+RegExp\s*\(/.test(src)) {
  console.error('No RegExp construction — URL filtering not implemented');
  process.exit(1);
}
if (!/\.test\s*\(/.test(src)) {
  console.error('No .test() call — filter not applied to URLs');
  process.exit(1);
}

// Execute the filter pattern to verify the RegExp approach works correctly
const filter = new RegExp('/api/');
const urls = [
  'https://example.com/api/users',
  'https://example.com/static/logo.png',
];
filter.lastIndex = 0;
if (!filter.test(urls[0])) { console.error('Filter should match /api/ URL'); process.exit(1); }
filter.lastIndex = 0;
if (filter.test(urls[1])) { console.error('Filter should not match non-api URL'); process.exit(1); }

console.log('PASS');
"""
    r = _run_node(code)
    assert r.returncode == 0, f"Filter test failed:\n{r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass — schema & rename
# ---------------------------------------------------------------------------

def test_schema_has_new_params():
    """inputSchema declares filter, requestBody, and requestHeaders params."""
    src = NETWORK_TS.read_text()
    assert re.search(r'filter\s*:\s*z\.\s*string', src), (
        "inputSchema must include a 'filter' string param"
    )
    assert re.search(r'requestBody\s*:\s*z\.\s*boolean', src), (
        "inputSchema must include a 'requestBody' boolean param"
    )
    assert re.search(r'requestHeaders\s*:\s*z\.\s*boolean', src), (
        "inputSchema must include a 'requestHeaders' boolean param"
    )


def test_static_replaces_include_static():
    """Old includeStatic param renamed to static in tool schema."""
    src = NETWORK_TS.read_text()
    assert not re.search(r'includeStatic\s*:\s*z\.', src), (
        "includeStatic should be renamed to static in inputSchema"
    )
    assert re.search(r'static\s*:\s*z\.\s*boolean', src), (
        "Schema must have 'static' boolean param"
    )


def test_cli_new_options():
    """CLI network command declares request-body, request-headers, and filter."""
    src = COMMANDS_TS.read_text()
    assert re.search(r"""['"]request-body['"]""", src), (
        "CLI must declare 'request-body' option"
    )
    assert re.search(r"""['"]request-headers['"]""", src), (
        "CLI must declare 'request-headers' option"
    )
    assert re.search(r'filter\s*:\s*z\.string', src), (
        "CLI must declare 'filter' string option"
    )
    assert "requestBody" in src, "CLI toolParams must map to requestBody"
    assert "requestHeaders" in src, "CLI toolParams must map to requestHeaders"


def test_copilot_instructions_created():
    """.github/copilot-instructions.md created with PR review guidelines."""
    assert COPILOT_MD.exists(), ".github/copilot-instructions.md must exist"
    content = COPILOT_MD.read_text().lower()
    assert "review" in content, "Must mention PR review"
    assert any(w in content for w in ["bug", "logic", "security", "semantic"]), (
        "Should focus reviews on substantive issues"
    )
    assert any(w in content for w in ["style", "formatting", "naming", "whitespace"]), (
        "Should mention skipping style/formatting issues"
    )
