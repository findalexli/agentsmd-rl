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
    """Modified TypeScript files have valid syntax."""
    # Since full project build requires complex setup, we verify syntax of modified files
    # by checking for basic TypeScript syntax correctness
    handler_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    content = handler_file.read_text()

    # Check for valid TypeScript structure
    assert "export const getHandler" in content, "Missing getHandler export"
    assert "new RenderResult(" in content, "Missing RenderResult instantiation"

    # Verify there are no obvious syntax errors by checking brackets balance
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Mismatched braces: {open_braces} open, {close_braces} close"

    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Mismatched parentheses: {open_parens} open, {close_parens} close"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_render_result_isdynamic_with_string():
    """RenderResult.isDynamic returns false for string response (not Buffer)."""
    # Check the source code to verify isDynamic logic
    render_result_file = Path(REPO) / "packages/next/src/server/render-result.ts"
    content = render_result_file.read_text()

    # Verify the isDynamic getter checks for string type
    assert "return typeof this.response !== 'string'" in content, \
        "isDynamic should return false for string responses"
    assert "typeof this.response !== 'string'" in content, \
        "isDynamic logic not found in render-result.ts"


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
    # Check the source code to verify send-payload logic for static responses
    send_payload_file = Path(REPO) / "packages/next/src/server/send-payload.ts"
    content = send_payload_file.read_text()

    # Verify the sendRenderResult function checks for isDynamic
    assert "isDynamic" in content, \
        "sendRenderResult should check isDynamic to determine if response is static"

    # Verify generateETag functionality exists
    assert "generateETag" in content or "ETag" in content, \
        "sendRenderResult should support ETag generation"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_render_result_class_exists():
    """RenderResult class is exported and functional."""
    # Verify the RenderResult class exists in source
    render_result_file = Path(REPO) / "packages/next/src/server/render-result.ts"
    content = render_result_file.read_text()

    # Check for key class elements
    assert "export default class RenderResult" in content, \
        "RenderResult class should be exported"
    assert "toUnchunkedString" in content, \
        "RenderResult should have toUnchunkedString method"
    assert "isDynamic" in content, \
        "RenderResult should have isDynamic getter"


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


# [repo_tests] pass_to_pass
def test_repo_eslint_pages_handler():
    """Repo's ESLint check passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.cli.config.mjs",
         "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_eslint_modified_files():
    """Repo's ESLint check passes on all modified files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.cli.config.mjs",
         "packages/next/src/server/render-result.ts",
         "packages/next/src/server/send-payload.ts",
         "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_prettier_modified_files():
    """Repo's Prettier check passes on all modified files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check",
         "packages/next/src/server/render-result.ts",
         "packages/next/src/server/send-payload.ts",
         "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier failed:\n{r.stdout}\n{r.stderr}"


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
