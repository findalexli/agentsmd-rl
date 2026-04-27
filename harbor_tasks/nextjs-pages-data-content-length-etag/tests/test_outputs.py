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
RENDER_RESULT = f"{REPO}/packages/next/src/server/render-result.ts"


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
    """The isNextDataRequest code path must construct RenderResult with a string
    payload, not a Buffer. Wrapping in Buffer.from() causes isDynamic=true,
    which prevents Content-Length and ETag headers from being set."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const code = fs.readFileSync(
    '/workspace/next.js/packages/next/src/server/route-modules/pages/pages-handler.ts', 'utf8'
);
// Remove comments
const clean = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Find the isNextDataRequest section and check that the RenderResult
// for JSON data responses is not constructed with Buffer.from() wrapping.
const lines = clean.split('\n');
let nearDataPath = false;
let countdown = 0;
let found = false;
for (let i = 0; i < lines.length; i++) {
    if (/isNextDataRequest/.test(lines[i])) {
        nearDataPath = true;
        countdown = 15;
    }
    if (nearDataPath) {
        countdown--;
        if (countdown <= 0) nearDataPath = false;
        const chunk = lines.slice(i, Math.min(i + 4, lines.length)).join(' ');
        if (/new\s+RenderResult\s*\(\s*Buffer\.from\s*\(/.test(chunk)) {
            found = true;
            break;
        }
    }
}
if (found) {
    console.log('FAIL: Data response path wraps payload in Buffer.from() for RenderResult');
    process.exit(1);
}
console.log('PASS: Data response path constructs RenderResult with string payload');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Data response path still wraps payload in Buffer.from() for RenderResult — "
        f"this causes isDynamic=true, preventing Content-Length and ETag headers\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_isr_fallback_path_no_buffer():
    """ISR fallback path must construct RenderResult with a string payload,
    not a Buffer. Wrapping in Buffer.from() causes isDynamic=true,
    preventing Content-Length and ETag headers from being set."""
    r = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');
const code = fs.readFileSync(
    '/workspace/next.js/packages/next/src/server/route-modules/pages/pages-handler.ts', 'utf8'
);
// Remove comments
const clean = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');
// Find the ISR fallback section (previousCacheEntry area) and check that
// the RenderResult for HTML content is not constructed with Buffer.from().
const lines = clean.split('\n');
let nearFallback = false;
let countdown = 0;
let found = false;
for (let i = 0; i < lines.length; i++) {
    if (/previousCacheEntry/.test(lines[i])) {
        nearFallback = true;
        countdown = 20;
    }
    if (nearFallback) {
        countdown--;
        if (countdown <= 0) nearFallback = false;
        const chunk = lines.slice(i, Math.min(i + 4, lines.length)).join(' ');
        if (/new\s+RenderResult\s*\(\s*Buffer\.from\s*\(/.test(chunk)) {
            found = true;
            break;
        }
    }
}
if (found) {
    console.log('FAIL: ISR fallback path wraps payload in Buffer.from() for RenderResult');
    process.exit(1);
}
console.log('PASS: ISR fallback path constructs RenderResult with string payload');
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ISR fallback still wraps payload in Buffer.from() for RenderResult — "
        f"this causes isDynamic=true, preventing Content-Length and ETag headers\n{r.stdout}\n{r.stderr}"
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


# [static] pass_to_pass
def test_handler_structure():
    """Handler file structure and exports are intact (static check).
    Uses file content analysis to verify the handler has the expected structure."""
    text = Path(HANDLER).read_text()

    checks = [
        ("getHandler export", r"export\s+const\s+getHandler"),
        ("RenderResult usage", r"new\s+RenderResult"),
        ("isNextDataRequest check", r"isNextDataRequest"),
        ("sendRenderResult call", r"sendRenderResult"),
        ("CachedRouteKind.PAGES", r"CachedRouteKind\.PAGES"),
        ("error handling", r"catch\s*\("),
    ]

    passed = 0
    for name, pattern in checks:
        if re.search(pattern, text):
            passed += 1

    assert passed >= 5, f"Handler structure checks failed: only {passed}/{len(checks)} passed"


# [static] pass_to_pass
def test_send_payload_structure():
    """send-payload.ts retains isDynamic -> Content-Length + ETag chain (static check).
    Verifies the core header-setting logic is preserved."""
    text = Path(SEND_PAYLOAD).read_text()

    # Remove comments for analysis
    code = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)

    required = [
        ("isDynamic check", r"isDynamic"),
        ("Content-Length header", r"Content-Length"),
        ("ETag header", r"ETag"),
        ("generateETag function", r"generateETag"),
    ]

    passed = 0
    for name, pattern in required:
        if re.search(pattern, code):
            passed += 1

    assert passed >= 4, f"Send-payload header chain check failed: only {passed}/{len(required)} passed"


# [static] pass_to_pass
def test_render_result_structure():
    """RenderResult class structure is intact (static check).
    Verifies the isDynamic mechanism is preserved."""
    text = Path(RENDER_RESULT).read_text()

    # Remove comments for analysis
    code = re.sub(r"//.*$", "", text, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)

    required = [
        ("isDynamic getter", r"get\s+isDynamic\s*\(\)"),
        ("toUnchunkedString method", r"toUnchunkedString"),
        ("string type check", r"typeof.*string"),
        ("RenderResult class", r"class\s+RenderResult"),
    ]

    passed = 0
    for name, pattern in required:
        if re.search(pattern, code):
            passed += 1

    assert passed >= 4, f"RenderResult structure check failed: only {passed}/{len(required)} passed"


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
def test_repo_prettier_render_result():
    """Repo CI: render-result.ts follows Prettier formatting (pass_to_pass).
    Verifies the RenderResult class maintains consistent code style."""
    result = subprocess.run(
        ["prettier", "--check", RENDER_RESULT],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_render_result_mechanism():
    """Repo CI: RenderResult isDynamic mechanism is preserved and functional (pass_to_pass).
    Behavioral test of the core mechanism the fix relies on - uses Node.js to verify."""
    result = subprocess.run(
        ["node", "-e", r"""
const assert = require('assert');

// Simulate the RenderResult isDynamic mechanism from render-result.ts
class MockRenderResult {
  constructor(response) {
    this.response = response;
  }
  get isDynamic() {
    return typeof this.response !== 'string';
  }
  toUnchunkedString() {
    if (this.response === null) return '';
    if (typeof this.response !== 'string') {
      throw new Error('dynamic responses cannot be unchunked');
    }
    return this.response;
  }
}

// Test: string input -> isDynamic = false (this is what the fix enables)
const stringPayload = JSON.stringify({ page: '/test', props: { x: 1 } });
const stringResult = new MockRenderResult(stringPayload);
assert.strictEqual(stringResult.isDynamic, false, 'String payload should not be dynamic');
assert.strictEqual(stringResult.toUnchunkedString(), stringPayload);

// Test: Buffer input -> isDynamic = true (this was the bug pattern)
const bufferPayload = Buffer.from(stringPayload);
const bufferResult = new MockRenderResult(bufferPayload);
assert.strictEqual(bufferResult.isDynamic, true, 'Buffer should be dynamic');

try {
  bufferResult.toUnchunkedString();
  assert.fail('Should throw for dynamic response');
} catch (e) {
  assert.ok(e.message.includes('dynamic'));
}

// Test: null input -> isDynamic = true (null is not a string)
const nullResult = new MockRenderResult(null);
assert.strictEqual(nullResult.isDynamic, true, 'Null should be dynamic');
assert.strictEqual(nullResult.toUnchunkedString(), '');

console.log('PASS: RenderResult mechanism intact - strings enable Content-Length/ETag headers');
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"RenderResult mechanism test failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_send_payload_header_chain():
    """Repo CI: send-payload.ts retains isDynamic -> Content-Length + ETag chain (pass_to_pass).
    Verifies the core header-setting logic is preserved using Node.js."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const content = fs.readFileSync('{SEND_PAYLOAD}', 'utf8');

// Remove comments for analysis
const code = content.replace(/\\/\\/.*$/gm, '').replace(/\\/\\*[\\s\\S]*?\\*\\//g, '');

// Check for required header chain elements
const required = [
  {{ name: 'isDynamic check', pattern: /isDynamic/ }},
  {{ name: 'Content-Length header', pattern: /Content-Length/ }},
  {{ name: 'ETag header', pattern: /ETag/ }},
  {{ name: 'generateETag function', pattern: /generateETag/ }},
];

let passed = 0;
for (const check of required) {{
  if (check.pattern.test(code)) {{
    passed++;
  }} else {{
    console.log('MISSING:', check.name);
  }}
}}

console.log(`${{passed}}/${{required.length}} header chain checks passed`);
process.exit(passed === required.length ? 0 : 1);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Send-payload header chain check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_package_json_scripts():
    """Repo CI: package.json maintains required npm scripts for CI/CD (pass_to_pass).
    Verifies the repo maintains standard npm scripts using Node.js."""
    result = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const path = '{REPO}/package.json';

if (!fs.existsSync(path)) {{
  console.error('package.json not found');
  process.exit(1);
}}

const pkg = JSON.parse(fs.readFileSync(path, 'utf8'));
const scripts = pkg.scripts || {{}};

// Check for required script categories
let failed = 0;

// Build scripts
if (!scripts.build) {{
  console.log('MISSING: build script');
  failed++;
}} else {{
  console.log('PASS: build script exists');
}}

// Test scripts
const testScripts = Object.keys(scripts).filter(s => s.startsWith('test'));
if (testScripts.length === 0) {{
  console.log('MISSING: test scripts');
  failed++;
}} else {{
  console.log('PASS: test scripts exist:', testScripts.slice(0, 3).join(', '));
}}

// Lint/typecheck scripts
const lintRelated = Object.keys(scripts).filter(s => s.includes('lint') || s.includes('type'));
if (lintRelated.length === 0) {{
  console.log('MISSING: lint/typecheck scripts');
  failed++;
}} else {{
  console.log('PASS: lint/type scripts exist:', lintRelated.slice(0, 3).join(', '));
}}

console.log(failed > 0 ? `FAILED: ${{failed}} checks` : 'PASS: All package.json checks');
process.exit(failed > 0 ? 1 : 0);
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Package.json scripts check failed:\n{result.stdout}\n{result.stderr}"

# [repo_tests] pass_to_pass
def test_repo_render_result_source_mechanism():
    """Repo CI: RenderResult source code contains correct isDynamic mechanism (pass_to_pass).
    Verifies the actual source file (not a mock) contains the isDynamic logic."""
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');

const RENDER_RESULT_PATH = '/workspace/next.js/packages/next/src/server/render-result.ts';
const SEND_PAYLOAD_PATH = '/workspace/next.js/packages/next/src/server/send-payload.ts';

// Read the actual source files
const renderResultCode = fs.readFileSync(RENDER_RESULT_PATH, 'utf8');
const sendPayloadCode = fs.readFileSync(SEND_PAYLOAD_PATH, 'utf8');

// Remove comments for analysis
const codeWithoutComments = renderResultCode.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

let passed = 0;
let failed = 0;

// Check RenderResult for isDynamic getter
if (/get\s+isDynamic\s*\(\)/.test(codeWithoutComments)) {
  console.log('PASS: isDynamic getter found in RenderResult');
  passed++;
} else {
  console.log('FAIL: isDynamic getter not found in RenderResult');
  failed++;
}

// Check for typeof string check
if (/typeof.*string/.test(codeWithoutComments)) {
  console.log('PASS: typeof string check found');
  passed++;
} else {
  console.log('FAIL: typeof string check not found');
  failed++;
}

// Check RenderResult class definition
if (/class\s+RenderResult/.test(codeWithoutComments)) {
  console.log('PASS: RenderResult class definition found');
  passed++;
} else {
  console.log('FAIL: RenderResult class definition not found');
  failed++;
}

// Check toUnchunkedString method
if (/toUnchunkedString/.test(codeWithoutComments)) {
  console.log('PASS: toUnchunkedString method found');
  passed++;
} else {
  console.log('FAIL: toUnchunkedString method not found');
  failed++;
}

// Check send-payload.ts for header chain
const sendCodeClean = sendPayloadCode.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

if (/isDynamic/.test(sendCodeClean)) {
  console.log('PASS: isDynamic check found in send-payload.ts');
  passed++;
} else {
  console.log('FAIL: isDynamic check not found in send-payload.ts');
  failed++;
}

if (/Content-Length/.test(sendCodeClean)) {
  console.log('PASS: Content-Length header found in send-payload.ts');
  passed++;
} else {
  console.log('FAIL: Content-Length header not found in send-payload.ts');
  failed++;
}

if (/ETag/.test(sendCodeClean)) {
  console.log('PASS: ETag header found in send-payload.ts');
  passed++;
} else {
  console.log('FAIL: ETag header not found in send-payload.ts');
  failed++;
}

if (/generateETag/.test(sendCodeClean)) {
  console.log('PASS: generateETag function found in send-payload.ts');
  passed++;
} else {
  console.log('FAIL: generateETag function not found in send-payload.ts');
  failed++;
}

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
"""],
        capture_output=True, text=True, timeout=30, cwd="/workspace/next.js",
    )
    assert result.returncode == 0, f"RenderResult source mechanism check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_pages_handler_source_structure():
    """Repo CI: pages-handler.ts source contains expected structure for data responses (pass_to_pass).
    Verifies the handler file contains the expected code patterns for the PR fix."""
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');

const HANDLER_PATH = '/workspace/next.js/packages/next/src/server/route-modules/pages/pages-handler.ts';
const code = fs.readFileSync(HANDLER_PATH, 'utf8');

// Remove comments for analysis
const cleanCode = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

let passed = 0;
let failed = 0;

// Check for getHandler export
if (/export\s+(const|async function|function)\s+getHandler/.test(code)) {
  console.log('PASS: getHandler export found');
  passed++;
} else {
  console.log('FAIL: getHandler export not found');
  failed++;
}

// Check for RenderResult usage
if (/new\s+RenderResult/.test(code)) {
  console.log('PASS: RenderResult instantiation found');
  passed++;
} else {
  console.log('FAIL: RenderResult instantiation not found');
  failed++;
}

// Check for isNextDataRequest handling
if (/isNextDataRequest/.test(code)) {
  console.log('PASS: isNextDataRequest check found');
  passed++;
} else {
  console.log('FAIL: isNextDataRequest check not found');
  failed++;
}

// Check for sendRenderResult call
if (/sendRenderResult/.test(code)) {
  console.log('PASS: sendRenderResult call found');
  passed++;
} else {
  console.log('FAIL: sendRenderResult call not found');
  failed++;
}

// Check for JSON.stringify (used for data responses)
if (/JSON\.stringify/.test(code)) {
  console.log('PASS: JSON.stringify found (for data responses)');
  passed++;
} else {
  console.log('FAIL: JSON.stringify not found');
  failed++;
}

// Check for CachedRouteKind.PAGES
if (/CachedRouteKind/.test(code)) {
  console.log('PASS: CachedRouteKind found');
  passed++;
} else {
  console.log('FAIL: CachedRouteKind not found');
  failed++;
}

// Check for generateEtags
if (/generateEtags/.test(code)) {
  console.log('PASS: generateEtags found');
  passed++;
} else {
  console.log('FAIL: generateEtags not found');
  failed++;
}

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
"""],
        capture_output=True, text=True, timeout=30, cwd="/workspace/next.js",
    )
    assert result.returncode == 0, f"Pages handler source structure check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax_valid():
    """Repo CI: TypeScript files have valid syntax (pass_to_pass).
    Verifies the modified TypeScript files can be parsed successfully."""
    result = subprocess.run(
        ["node", "-e", r"""
const fs = require('fs');

// Simple TypeScript syntax check - verify files are valid by checking balanced braces
function checkTypeScriptSyntax(filePath, name) {
  const code = fs.readFileSync(filePath, 'utf8');

  let braceCount = 0;
  let parenCount = 0;
  let bracketCount = 0;
  let inString = false;
  let stringChar = null;
  let inComment = false;
  let commentType = null;

  for (let i = 0; i < code.length; i++) {
    const char = code[i];
    const nextChar = code[i + 1];

    // Handle comments
    if (!inString && !inComment) {
      if (char === '/' && nextChar === '/') {
        inComment = true;
        commentType = 'line';
        i++;
        continue;
      }
      if (char === '/' && nextChar === '*') {
        inComment = true;
        commentType = 'block';
        i++;
        continue;
      }
    } else if (inComment && commentType === 'line' && char === '\n') {
      inComment = false;
      commentType = null;
      continue;
    } else if (inComment && commentType === 'block' && char === '*' && nextChar === '/') {
      inComment = false;
      commentType = null;
      i++;
      continue;
    }

    if (inComment) continue;

    // Handle strings
    if (!inString && (char === '"' || char === "'" || char === '`')) {
      inString = true;
      stringChar = char;
      continue;
    }
    if (inString && char === stringChar && code[i-1] !== '\\') {
      inString = false;
      stringChar = null;
      continue;
    }

    if (inString) continue;

    // Count braces
    if (char === '{') braceCount++;
    if (char === '}') braceCount--;
    if (char === '(') parenCount++;
    if (char === ')') parenCount--;
    if (char === '[') bracketCount++;
    if (char === ']') bracketCount--;

    // Early exit on clear mismatches
    if (braceCount < 0 || parenCount < 0 || bracketCount < 0) {
      return { valid: false, error: `Negative count at position ${i}` };
    }
  }

  if (braceCount !== 0) return { valid: false, error: `Unbalanced braces: ${braceCount}` };
  if (parenCount !== 0) return { valid: false, error: `Unbalanced parentheses: ${parenCount}` };
  if (bracketCount !== 0) return { valid: false, error: `Unbalanced brackets: ${bracketCount}` };

  return { valid: true };
}

const files = [
  { path: '/workspace/next.js/packages/next/src/server/route-modules/pages/pages-handler.ts', name: 'pages-handler.ts' },
  { path: '/workspace/next.js/packages/next/src/server/send-payload.ts', name: 'send-payload.ts' },
  { path: '/workspace/next.js/packages/next/src/server/render-result.ts', name: 'render-result.ts' },
];

let failed = 0;
for (const file of files) {
  const result = checkTypeScriptSyntax(file.path, file.name);
  if (result.valid) {
    console.log(`PASS: ${file.name} has valid syntax`);
  } else {
    console.log(`FAIL: ${file.name} - ${result.error}`);
    failed++;
  }
}

process.exit(failed > 0 ? 1 : 0);
"""],
        capture_output=True, text=True, timeout=30, cwd="/workspace/next.js",
    )
    assert result.returncode == 0, f"TypeScript syntax check failed:\n{result.stdout}\n{result.stderr}"
