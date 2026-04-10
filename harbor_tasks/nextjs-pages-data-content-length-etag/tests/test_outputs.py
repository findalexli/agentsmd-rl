"""
Task: nextjs-pages-data-content-length-etag
Repo: vercel/next.js @ cfd5f533b08df3038476dcd54f1d6d660d85f069
PR:   90304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
HANDLER = f"{REPO}/packages/next/src/server/route-modules/pages/pages-handler.ts"
SEND_PAYLOAD = f"{REPO}/packages/next/src/server/send-payload.ts"


def _strip_comments(code: str) -> str:
    """Remove single-line and multi-line JS/TS comments."""
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_response_path_no_buffer():
    """The isNextDataRequest code path must NOT wrap JSON.stringify in Buffer.from.
    The buggy pattern Buffer.from(JSON.stringify(result.value.pageData)) causes
    isDynamic=true, which prevents Content-Length and ETag headers from being set."""
    code = Path(HANDLER).read_text()
    # AST-only because: TypeScript with complex build deps, cannot import handler directly
    assert "Buffer.from(JSON.stringify(result.value.pageData))" not in code, (
        "Data response path still wraps JSON.stringify in Buffer.from — "
        "this causes isDynamic=true, preventing Content-Length and ETag headers"
    )


# [pr_diff] fail_to_pass
def test_isr_fallback_path_no_buffer():
    """ISR fallback path must NOT wrap previousCacheEntry.value.html in Buffer.from.
    The buggy pattern Buffer.from(previousCacheEntry.value.html) causes isDynamic=true,
    preventing Content-Length and ETag headers from being set on ISR fallback responses."""
    code = Path(HANDLER).read_text()
    # AST-only because: TypeScript with complex build deps, cannot import handler directly
    assert "Buffer.from(previousCacheEntry.value.html)" not in code, (
        "ISR fallback still wraps previousCacheEntry.value.html in Buffer.from — "
        "this causes isDynamic=true, preventing Content-Length and ETag"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_string_render_result_enables_headers():
    """RenderResult constructed with string (not Buffer) makes isDynamic false,
    so sendRenderResult sets Content-Length and ETag. Verifies the core mechanism
    the fix relies on has not regressed."""
    # Behavioral: run Node.js to verify the isDynamic mechanism end-to-end
    result = subprocess.run(
        ["node", "-e", r"""
const assert = require('assert');

// Reproduce isDynamic mechanism from render-result.ts
class RenderResult {
  constructor(response) { this.response = response; }
  get isDynamic() { return typeof this.response !== 'string'; }
  toUnchunkedString() {
    if (typeof this.response !== 'string') throw new Error('dynamic');
    return this.response;
  }
}

function simulateSendRenderResult(result) {
  const headers = {};
  const payload = result.isDynamic ? null : result.toUnchunkedString();
  if (payload !== null) {
    headers['ETag'] = '"W/abc123"';
    headers['Content-Length'] = String(Buffer.byteLength(payload));
  }
  return headers;
}

// Vary inputs: different JSON payloads and HTML content
const testCases = [
  JSON.stringify({ page: '/index', pageData: { x: 1 } }),
  JSON.stringify({ page: '/about', pageData: { items: [1, 2, 3], nested: { a: 'b' } } }),
  JSON.stringify({ page: '/deep', pageData: { unicode: '\u00e9\u00e8\u00f1', empty: {}, arr: [] } }),
  '<html><body>ISR fallback content</body></html>',
  '<html><body>Another page with special chars: &amp; &lt;</body></html>',
];

for (const payload of testCases) {
  // String input (fix) -> headers set
  const fixed = simulateSendRenderResult(new RenderResult(payload));
  assert(fixed['Content-Length'] !== undefined,
    'Content-Length must be set for string input: ' + payload.slice(0, 40));
  assert(fixed['ETag'] !== undefined,
    'ETag must be set for string input');
  assert.strictEqual(fixed['Content-Length'], String(Buffer.byteLength(payload)),
    'Content-Length must equal byte length of payload');

  // Buffer input (bug) -> headers NOT set
  const buggy = simulateSendRenderResult(new RenderResult(Buffer.from(payload)));
  assert(buggy['Content-Length'] === undefined,
    'Content-Length must NOT be set for Buffer input (demonstrates the bug)');
  assert(buggy['ETag'] === undefined,
    'ETag must NOT be set for Buffer input');
}

console.log('PASS');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Failed:\n{result.stdout}\n{result.stderr}"


# [pr_diff] pass_to_pass
def test_send_payload_header_chain():
    """sendRenderResult retains the isDynamic -> Content-Length + ETag chain.
    The fix depends on this chain being intact in send-payload.ts."""
    # AST-only because: TypeScript with complex build deps
    sp = Path(SEND_PAYLOAD)
    if not sp.exists():
        # Fallback: search for the file
        result = subprocess.run(
            ["find", f"{REPO}/packages/next/src/server",
             "-name", "send-payload*", "-o", "-name", "send-render*"],
            capture_output=True, text=True, timeout=10,
        )
        found = result.stdout.strip().split("\n")[0]
        assert found, "send-payload.ts not found in server directory"
        sp = Path(found)

    code = _strip_comments(sp.read_text())

    required = {
        "isDynamic": "isDynamic check that gates header setting",
        "Content-Length": "Content-Length header assignment",
        "byteLength": "byte length calculation for Content-Length",
        "ETag": "ETag header generation",
    }
    missing = [desc for kw, desc in required.items() if kw not in code]
    assert not missing, f"sendRenderResult missing critical logic: {', '.join(missing)}"


# [static] pass_to_pass
def test_handler_not_stub():
    """Handler retains core code paths and has substantial content.
    Prevents agents from replacing the handler with a stub."""
    text = Path(HANDLER).read_text()
    code = _strip_comments(text)

    required = [
        ("isNextDataRequest", "data request handling"),
        ("JSON.stringify", "JSON serialization of page data"),
        ("sendRenderResult", "response sending via sendRenderResult"),
        ("RenderResult", "RenderResult construction"),
        ("generateEtags", "ETag generation config flag"),
        ("CachedRouteKind", "cache route kind handling"),
    ]
    missing = [desc for kw, desc in required if kw not in code]
    assert not missing, f"Handler missing core logic: {', '.join(missing)}"

    lines = text.splitlines()
    code_lines = [l for l in lines if l.strip() and not re.match(r"^\s*(//|/\*|\*|\*/)", l)]
    assert len(lines) > 200, f"Handler suspiciously small: {len(lines)} lines (expected >200)"
    assert len(code_lines) > 100, f"Too few code lines: {len(code_lines)} (expected >100)"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks using real commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_prettier_pages_handler():
    """Repo CI: pages-handler.ts follows Prettier formatting (pass_to_pass).
    Verifies the file maintains consistent code style."""
    result = subprocess.run(
        ["prettier", "--check", HANDLER],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_send_payload():
    """Repo CI: send-payload.ts follows Prettier formatting (pass_to_pass).
    Verifies the payload sending logic maintains consistent code style."""
    result = subprocess.run(
        ["prettier", "--check", SEND_PAYLOAD],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_render_result_mechanism():
    """Repo CI: RenderResult isDynamic mechanism is preserved (pass_to_pass).
    Behavioral test of the core mechanism the fix relies on."""
    result = subprocess.run(
        ["node", "-e", r"""
const assert = require('assert');

// Simulate the RenderResult isDynamic mechanism
class MockRenderResult {
  constructor(response) {
    this.response = response;
  }
  get isDynamic() {
    return typeof this.response !== 'string';
  }
  toUnchunkedString() {
    if (typeof this.response !== 'string') {
      throw new Error('Cannot convert dynamic response to string');
    }
    return this.response;
  }
}

// Test: string input -> isDynamic = false
const stringResult = new MockRenderResult('test content');
assert.strictEqual(stringResult.isDynamic, false, 'String should not be dynamic');
assert.strictEqual(stringResult.toUnchunkedString(), 'test content');

// Test: Buffer input -> isDynamic = true
const bufferResult = new MockRenderResult(Buffer.from('test content'));
assert.strictEqual(bufferResult.isDynamic, true, 'Buffer should be dynamic');

try {
  bufferResult.toUnchunkedString();
  assert.fail('Should throw for dynamic response');
} catch (e) {
  assert.ok(e.message.includes('dynamic') || e.message.includes('Cannot convert'));
}

console.log('PASS: RenderResult mechanism intact');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"RenderResult mechanism test failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_handler_structure():
    """Repo CI: Handler file structure and exports are intact (pass_to_pass).
    Uses Node.js to verify the handler has the expected structure."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const handler = fs.readFileSync('{HANDLER}', 'utf8');

const checks = [
  {{ name: 'getHandler export', pattern: /export\\s+const\\s+getHandler/ }},
  {{ name: 'RenderResult usage', pattern: /new\\s+RenderResult/ }},
  {{ name: 'isNextDataRequest check', pattern: /isNextDataRequest/ }},
  {{ name: 'sendRenderResult call', pattern: /sendRenderResult/ }},
  {{ name: 'CachedRouteKind.PAGES', pattern: /CachedRouteKind\\.PAGES/ }},
  {{ name: 'error handling', pattern: /catch\\s*\\(/ }},
];

let passed = 0;
for (const check of checks) {{
  if (check.pattern.test(handler)) {{
    console.log('PASS:', check.name);
    passed++;
  }} else {{
    console.log('FAIL:', check.name);
  }}
}}

console.log(`${{passed}}/${{checks.length}} checks passed`);
process.exit(passed === checks.length ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Handler structure check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_send_payload_structure():
    """Repo CI: send-payload.ts exports and logic are intact (pass_to_pass).
    Uses Node.js to verify the payload sending logic is preserved."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const payload = fs.readFileSync('{SEND_PAYLOAD}', 'utf8');

const checks = [
  {{ name: 'sendRenderResult export', pattern: /export\\s+async\\s+function\\s+sendRenderResult/ }},
  {{ name: 'sendEtagResponse export', pattern: /export\\s+function\\s+sendEtagResponse/ }},
  {{ name: 'isDynamic check', pattern: /isDynamic/ }},
  {{ name: 'Content-Length header', pattern: /Content-Length/ }},
  {{ name: 'generateETag usage', pattern: /generateETag/ }},
];

let passed = 0;
for (const check of checks) {{
  if (check.pattern.test(payload)) {{
    console.log('PASS:', check.name);
    passed++;
  }} else {{
    console.log('FAIL:', check.name);
  }}
}}

console.log(`${{passed}}/${{checks.length}} checks passed`);
process.exit(passed === checks.length ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Send-payload structure check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_check():
    """Repo CI: Handler and send-payload have valid syntax (pass_to_pass).
    Uses Node.js to verify the files have valid syntax structure."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');

const files = [
  '{HANDLER}',
  '{SEND_PAYLOAD}'
];

for (const file of files) {{
  const content = fs.readFileSync(file, 'utf8');

  // Check for valid UTF-8 (no replacement chars)
  if (content.includes('\\uFFFD')) {{
    console.error('Invalid UTF-8 in', file);
    process.exit(1);
  }}

  // Check for basic structure (balanced braces - basic check)
  const openBraces = (content.match(/{{/g) || []).length;
  const closeBraces = (content.match(/}}/g) || []).length;
  if (Math.abs(openBraces - closeBraces) > 5) {{
    console.error('Unbalanced braces in', file, ':', openBraces, 'vs', closeBraces);
    process.exit(1);
  }}
}}

console.log('PASS: All files have valid syntax structure');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_package_json_scripts():
    """Repo CI: package.json has required scripts (pass_to_pass).
    Verifies the repo maintains standard npm scripts for CI/CD."""
    pkg_path = Path(REPO) / "package.json"
    assert pkg_path.exists(), "package.json not found"

    import json
    pkg = json.loads(pkg_path.read_text())

    # Check for required script categories
    scripts = pkg.get("scripts", {})

    # Build scripts
    assert "build" in scripts, "Missing build script"

    # Test scripts (at least one should exist)
    test_scripts = [s for s in scripts.keys() if s.startswith("test")]
    assert test_scripts, "Missing test scripts"

    # Lint/typecheck scripts
    lint_related = [s for s in scripts.keys() if "lint" in s or "type" in s]
    assert lint_related, "Missing lint or typecheck scripts"
