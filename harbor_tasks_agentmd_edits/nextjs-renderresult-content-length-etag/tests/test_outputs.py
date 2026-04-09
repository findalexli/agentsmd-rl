"""
Task: nextjs-renderresult-content-length-etag
Repo: vercel/next.js @ fb85660ab1f70e294465af0074dc7c941e3540ca
PR:   90304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/next.js"


def _run_node_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute TypeScript code using Node.js with experimental strip types."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_check():
    """Modified pages-handler.ts must parse without TypeScript errors."""
    target_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Use TypeScript compiler to check syntax (no emit)
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", str(target_file)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Ignore lib errors, focus on syntax errors in the file itself
    assert "error TS" not in r.stdout or "pages-handler.ts" not in r.stdout, \
        f"TypeScript errors in pages-handler.ts:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_buffer_from_in_data_request():
    """Data request handler should NOT wrap JSON.stringify with Buffer.from."""
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Find the isNextDataRequest && !isErrorPage && !is500Page block
    # After fix, this should use JSON.stringify directly, NOT Buffer.from(JSON.stringify(...))
    # Pattern to search for the problematic code
    import re

    # Look for the data request RenderResult construction
    # Before fix: Buffer.from(JSON.stringify(result.value.pageData))
    # After fix: JSON.stringify(result.value.pageData)
    data_request_pattern = r'isNextDataRequest[^,]+\?\s*new\s+RenderResult\(\s*(Buffer\.from\()?JSON\.stringify'
    match = re.search(data_request_pattern, content, re.DOTALL)

    if match:
        # If Buffer.from is present, the fix hasn't been applied
        has_buffer_from = match.group(1) is not None
        assert not has_buffer_from, \
            "BUG NOT FIXED: Data request still uses Buffer.from(JSON.stringify(...)) - " \
            "this causes isDynamic to return true, skipping Content-Length and ETag headers"


# [pr_diff] fail_to_pass
def test_no_buffer_from_in_cached_html():
    """Cached HTML handler should NOT wrap previousCacheEntry.value.html with Buffer.from."""
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Look for the cached HTML RenderResult construction
    # Before fix: Buffer.from(previousCacheEntry.value.html)
    # After fix: previousCacheEntry.value.html
    if "Buffer.from(previousCacheEntry.value.html)" in content:
        assert False, \
            "BUG NOT FIXED: Cached HTML handler still uses Buffer.from() - " \
            "this causes isDynamic to return true, skipping Content-Length and ETag headers"


# [pr_diff] fail_to_pass
def test_render_result_accepts_string():
    """Verify RenderResult can be constructed with a plain string (not Buffer)."""
    # Create a test script that imports RenderResult and tests string vs Buffer behavior
    script = """
// Import the RenderResult class from the compiled next package
import { RenderResult } from './packages/next/dist/server/render-result.js'

// Test 1: RenderResult with string should have isDynamic = false
const stringResult = new RenderResult(JSON.stringify({ page: "test" }), {
    contentType: 'application/json',
    metadata: {}
});
const stringIsDynamic = stringResult.isDynamic;

// Test 2: RenderResult with Buffer should have isDynamic = true (pre-fix behavior)
const bufferResult = new RenderResult(Buffer.from(JSON.stringify({ page: "test" })), {
    contentType: 'application/json',
    metadata: {}
});
const bufferIsDynamic = bufferResult.isDynamic;

console.log(JSON.stringify({
    stringIsDynamic,
    bufferIsDynamic,
    // String should NOT be dynamic (isDynamic = false)
    // Buffer should be dynamic (isDynamic = true)
    pass: stringIsDynamic === false && bufferIsDynamic === true
}));
"""
    r = _run_node_ts(script, timeout=30)
    assert r.returncode == 0, f"Script failed: {r.stderr}\n{r.stdout}"

    result = json.loads(r.stdout.strip())
    assert result.get("pass") is True, \
        f"RenderResult behavior incorrect: string isDynamic={result['stringIsDynamic']}, " \
        f"buffer isDynamic={result['bufferIsDynamic']}. " \
        f"Expected: string should NOT be dynamic (allows Content-Length/ETag), " \
        f"buffer should be dynamic."


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_has_real_logic():
    """pages-handler.ts should have meaningful implementation, not a stub."""
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Check that the file has substantial content
    lines = content.split('\n')
    non_empty = [l for l in lines if l.strip() and not l.strip().startswith('//')]
    assert len(non_empty) > 50, "Handler file appears to be a stub or empty"

    # Check for key function signatures
    assert "export const getHandler" in content, "Missing getHandler export"
    assert "RenderResult" in content, "Missing RenderResult usage"


# ---------------------------------------------------------------------------
# Config-derived (agent_config / pr_diff) — documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_new_test_syntax_fixed():
    """AGENTS.md must show correct pnpm new-test syntax with '-- --args' separator."""
    agents_file = Path(REPO) / "AGENTS.md"
    assert agents_file.exists(), "AGENTS.md not found"

    content = agents_file.read_text()

    # The fix adds '--' before '--args' in the pnpm new-test command
    # Before fix: pnpm new-test --args true my-feature e2e
    # After fix: pnpm new-test -- --args true my-feature e2e

    # Check that the correct syntax with '-- --args' is present
    if "pnpm new-test -- --args" not in content:
        assert False, \
            "AGENTS.md NOT UPDATED: Missing correct 'pnpm new-test -- --args' syntax. " \
            "The command needs '--' separator to properly forward args to the script. " \
            "Without this, users get errors when running pnpm new-test non-interactively."


# [pr_diff] fail_to_pass
def test_agents_md_no_bare_args_flag():
    """AGENTS.md should NOT show the incorrect bare '--args' without separator."""
    agents_file = Path(REPO) / "AGENTS.md"
    content = agents_file.read_text()

    # Look for instances of bare '--args' without the '--' separator
    import re
    # Pattern: pnpm new-test --args (without -- before it)
    # But allow for lines that might have comments or other contexts
    bare_args_pattern = r'pnpm\s+new-test\s+--args\s'
    matches = re.findall(bare_args_pattern, content)

    if matches:
        assert False, \
            "AGENTS.md HAS INCORRECT SYNTAX: Found bare 'pnpm new-test --args' without '--' separator. " \
            "This is the bug - the correct syntax is 'pnpm new-test -- --args ...'"
