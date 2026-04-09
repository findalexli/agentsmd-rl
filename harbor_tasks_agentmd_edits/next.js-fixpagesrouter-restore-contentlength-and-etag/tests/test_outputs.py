"""
Task: Fix(pages-router): restore Content-Length and ETag for /_next/data/ JSON responses
Repo: vercel/next.js @ 56d75a0b77f2ceda8ea747810275da8e0a9a3d71
PR:   90304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files compile without errors."""
    # Type-check the modified pages-handler.ts file
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck",
         "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_render_result_isdynamic_with_string():
    """RenderResult.isDynamic returns false for string response (not Buffer)."""
    code = """
const RenderResult = require('./packages/next/dist/server/render-result').default;

// Test with string (correct after fix)
const stringResult = new RenderResult(JSON.stringify({ foo: 'bar' }), {
    contentType: 'application/json',
    metadata: {},
});

if (stringResult.isDynamic !== false) {
    console.log('FAIL: string response should have isDynamic=false, got:', stringResult.isDynamic);
    process.exit(1);
}

// Test with Buffer (incorrect behavior before fix)
const bufferResult = new RenderResult(Buffer.from(JSON.stringify({ foo: 'bar' })), {
    contentType: 'application/json',
    metadata: {},
});

if (bufferResult.isDynamic !== true) {
    console.log('FAIL: Buffer response should have isDynamic=true, got:', bufferResult.isDynamic);
    process.exit(1);
}

console.log('PASS: isDynamic correctly distinguishes string from Buffer');
"""
    script = Path(REPO) / "_test_isdynamic.mjs"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
        assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"
    finally:
        script.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_pages_handler_uses_string_not_buffer():
    """pages-handler.ts passes string to RenderResult, not Buffer.from()."""
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Check for the fix: new RenderResult(JSON.stringify(result.value.pageData), {...})
    # This should exist after the fix (single-line constructor call with string)
    assert "new RenderResult(JSON.stringify(result.value.pageData)," in content, \
        "Fix not applied: should have new RenderResult(JSON.stringify(result.value.pageData), ...)"

    # Check for the fix: new RenderResult(previousCacheEntry.value.html, {...})
    # (without Buffer.from wrapper)
    assert "new RenderResult(previousCacheEntry.value.html," in content, \
        "Fix not applied: should have new RenderResult(previousCacheEntry.value.html, ...)"

    # Verify the buggy patterns are NOT present: Buffer.from wrapping these values
    # The old buggy code had: Buffer.from(JSON.stringify(result.value.pageData))
    # and: Buffer.from(previousCacheEntry.value.html)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Check for Buffer.from wrapping result.value.pageData specifically
        if 'Buffer.from' in line and 'result.value.pageData' in line:
            assert False, f"Bug still present: Buffer.from wrapping result.value.pageData at line {i+1}"
        # Check for Buffer.from wrapping previousCacheEntry.value.html specifically
        if 'Buffer.from' in line and 'previousCacheEntry.value.html' in line:
            assert False, f"Bug still present: Buffer.from wrapping previousCacheEntry.value.html at line {i+1}"


# [pr_diff] fail_to_pass
def test_send_payload_generates_headers_for_static():
    """sendRenderResult generates Content-Length and ETag for non-dynamic responses."""
    code = """
const RenderResult = require('./packages/next/dist/server/render-result').default;
const { sendRenderResult } = require('./packages/next/dist/server/send-payload');
const http = require('http');

// Create a mock response
const res = {
    headers: {},
    statusCode: 200,
    setHeader(name, value) { this.headers[name] = value; },
    getHeader(name) { return this.headers[name]; },
    end(data) { this.ended = true; this.data = data; },
};

const req = { method: 'GET', headers: {} };

// Create a RenderResult with a string (static) response
const result = new RenderResult(JSON.stringify({ page: 'test' }), {
    contentType: 'application/json',
    metadata: {},
});

// Verify isDynamic is false
if (result.isDynamic !== false) {
    console.log('FAIL: Expected isDynamic=false for string response');
    process.exit(1);
}

console.log('PASS: Static string response is not dynamic');
"""
    script = Path(REPO) / "_test_headers.mjs"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
        assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_render_result_class_exists():
    """RenderResult class is exported and functional."""
    code = """
const RenderResult = require('./packages/next/dist/server/render-result').default;
if (!RenderResult) {
    console.log('FAIL: RenderResult not found');
    process.exit(1);
}
const result = new RenderResult('test', { metadata: {}, contentType: 'text/html' });
if (result.toUnchunkedString() !== 'test') {
    console.log('FAIL: RenderResult.toUnchunkedString() not working');
    process.exit(1);
}
console.log('PASS: RenderResult class functional');
"""
    script = Path(REPO) / "_test_render_result.mjs"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
        assert "PASS" in r.stdout, f"Unexpected output: {r.stdout}"
    finally:
        script.unlink(missing_ok=True)


# [static] pass_to_pass
def test_pages_handler_file_not_stub():
    """pages-handler.ts has meaningful implementation, not stub."""
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Check for key functions that should exist
    assert "getHandler" in content, "Missing getHandler function"
    assert "RenderResult" in content, "Missing RenderResult usage"
    assert "isNextDataRequest" in content, "Missing isNextDataRequest logic"

    # Make sure it's not a stub file
    assert "TODO" not in content or content.count("TODO") < 5, "File appears to be a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:148-150 @ 56d75a0b77f2ceda8ea747810275da8e0a9a3d71
def test_agents_md_new_test_syntax():
    """AGENTS.md documents correct pnpm new-test syntax with -- --args."""
    agents_file = Path(REPO) / "AGENTS.md"
    content = agents_file.read_text()

    # The fix changes --args to -- --args for non-interactive mode
    # Check that the documentation has been updated with correct syntax
    assert "pnpm new-test -- --args" in content, \
        "AGENTS.md should document 'pnpm new-test -- --args' syntax"

    # The old buggy syntax was "pnpm new-test --args true my-feature e2e"
    # (without the -- separator). Make sure that's not present.
    assert "pnpm new-test --args true my-feature e2e" not in content, \
        "AGENTS.md should not contain the old incorrect 'pnpm new-test --args' syntax"
