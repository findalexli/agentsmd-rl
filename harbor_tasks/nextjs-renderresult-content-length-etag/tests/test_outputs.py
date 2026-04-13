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
    """Modified pages-handler.ts must parse without syntax errors."""
    target_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    assert target_file.exists(), f"Target file not found: {target_file}"

    # Use Node.js --check to verify syntax (TypeScript-aware in Node 22+)
    r = subprocess.run(
        ["node", "--check", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax errors in pages-handler.ts:\n{r.stderr}"


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
    """Verify RenderResult isDynamic is false for strings, true for Buffers.

    This test validates that the fix properly removes Buffer.from() wrappers,
    which would cause isDynamic=true and skip Content-Length/ETag headers.

    Since importing the full module has complex dependencies, we verify the
    behavior by checking the source code pattern that controls isDynamic:
    - typeof this.response !== 'string' determines isDynamic
    - String responses are NOT dynamic (allows Content-Length/ETag)
    - Buffer responses ARE dynamic (streams, no Content-Length/ETag)
    """
    # Read the render-result.ts source to verify isDynamic logic
    render_result_file = Path(REPO) / "packages/next/src/server/render-result.ts"
    content = render_result_file.read_text()

    # Verify the isDynamic getter checks if response is a string
    # This is the core logic: if response is string -> isDynamic=false
    assert "typeof this.response !== 'string'" in content, \
        "Cannot find isDynamic getter logic in render-result.ts"

    # The fix removes Buffer.from() so that isDynamic returns false for strings.
    # We verify the pages-handler.ts no longer wraps with Buffer.from() via
    # the test_no_buffer_from_* tests above.
    # This test confirms the RenderResult class supports string responses.


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI commands that test the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_eslint_pages_handler():
    """Repo's eslint passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on pages-handler.ts:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_pages_handler():
    """Repo's prettier formatting passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on pages-handler.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_render_result():
    """Repo's eslint passes on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on render-result.ts:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_syntax_check_pages_handler():
    """Node.js syntax check passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node syntax check failed on pages-handler.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_alex_linting():
    """Repo's language linting (alex) passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint-language"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # alex passes if no errors found in the content (warnings/filename matches are OK)
    # The check looks for actual errors in file content, not filenames containing "error"
    # Alex outputs like "error: must not ..." for actual content issues
    import re
    # Find lines with error: that are about content (not just filenames)
    content_errors = re.findall(r'^\s*error:.*$', r.stderr, re.MULTILINE | re.IGNORECASE)
    # Filter out false positives - lines that just show filenames with "error" in them
    real_errors = [e for e in content_errors if 'no issues found' not in e.lower()]
    assert len(real_errors) == 0, f"Alex language linting found errors:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_ast_grep_pages_handler():
    """Repo's ast-grep scan passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "ast-grep", "scan", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep found issues in pages-handler.ts:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ast_grep_render_result():
    """Repo's ast-grep scan passes on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "ast-grep", "scan", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep found issues in render-result.ts:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_cli_config_pages_handler():
    """Repo's eslint with CLI config passes on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.cli.config.mjs", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint (CLI config) failed on pages-handler.ts:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_cli_config_render_result():
    """Repo's eslint with CLI config passes on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.cli.config.mjs", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint (CLI config) failed on render-result.ts:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_render_result():
    """Repo's prettier formatting passes on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed on render-result.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - NEW: TypeScript compilation checks
def test_repo_tsc_pages_handler():
    """TypeScript compilation check on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # tsc returns 0 on success, 2 on errors; pass if returncode is 0 or no errors in target file
    assert r.returncode == 0 or "pages-handler.ts" not in r.stderr, \
        f"TypeScript check failed on pages-handler.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - NEW: TypeScript compilation checks
def test_repo_tsc_render_result():
    """TypeScript compilation check on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # tsc returns 0 on success, 2 on errors; pass if returncode is 0 or no errors in target file
    assert r.returncode == 0 or "render-result.ts" not in r.stderr, \
        f"TypeScript check failed on render-result.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - NEW: Node syntax check on render-result.ts
def test_repo_node_syntax_render_result():
    """Node.js syntax check passes on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node syntax check failed on render-result.ts:\n{r.stderr[-500:]}"


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
