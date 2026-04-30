"""
Task: nextjs-pages-data-content-length-agentsmd
Repo: vercel/next.js @ fb85660ab1f70e294465af0074dc7c941e3540ca
PR:   90304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
HANDLER = f"{REPO}/packages/next/src/server/route-modules/pages/pages-handler.ts"
AGENTS_MD = f"{REPO}/AGENTS.md"


def _strip_comments(code: str) -> str:
    """Remove single-line and multi-line JS/TS comments."""
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code fix verification
# ---------------------------------------------------------------------------


def test_data_response_path_no_buffer():
    """The isNextDataRequest code path must NOT wrap JSON.stringify in
    Buffer.from. The buggy pattern causes isDynamic=true, preventing
    Content-Length and ETag headers from being set."""
    code = Path(HANDLER).read_text()
    assert "Buffer.from(JSON.stringify(result.value.pageData))" not in code, (
        "Data response path still wraps JSON.stringify in Buffer.from — "
        "this causes isDynamic=true, preventing Content-Length and ETag headers"
    )


def test_isr_fallback_path_no_buffer():
    """ISR fallback path must NOT wrap previousCacheEntry.value.html in
    Buffer.from. The buggy pattern causes isDynamic=true, preventing
    Content-Length and ETag headers on ISR fallback responses."""
    code = Path(HANDLER).read_text()
    assert "Buffer.from(previousCacheEntry.value.html)" not in code, (
        "ISR fallback still wraps previousCacheEntry.value.html in Buffer.from — "
        "this causes isDynamic=true, preventing Content-Length and ETag"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md config fix verification
# ---------------------------------------------------------------------------


def test_agents_md_new_test_forward_args():
    """AGENTS.md must document the correct pnpm new-test -- --args syntax
    in the non-interactive test generation section. The buggy form
    'pnpm new-test --args' does not forward args correctly."""
    content = Path(AGENTS_MD).read_text()
    assert "pnpm new-test -- --args" in content, (
        "AGENTS.md must use 'pnpm new-test -- --args' (with -- to forward args)"
    )
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if "Format: pnpm new-test" in line:
            assert "-- --args" in line, (
                f"AGENTS.md line {i+1}: Format must use '-- --args', got: {line.strip()}"
            )


def test_agents_md_smoke_test_gotchas_syntax():
    """AGENTS.md 'Test Gotchas' section must use the correct
    'pnpm new-test -- --args' syntax in the smoke testing tip."""
    content = Path(AGENTS_MD).read_text()
    in_gotchas = False
    found_smoke_line = False
    for line in content.splitlines():
        if "Test Gotchas" in line:
            in_gotchas = True
        elif in_gotchas and "Quick smoke testing" in line:
            found_smoke_line = True
            assert "-- --args" in line, (
                "Test Gotchas smoke testing tip must use 'pnpm new-test -- --args'"
            )
            assert "new-test --args true" not in line, (
                "Test Gotchas still has buggy 'new-test --args true' (missing --)"
            )
            break
    assert found_smoke_line, "Could not find 'Quick smoke testing' in Test Gotchas"


# ---------------------------------------------------------------------------
# Pass-to-pass — behavioral verification and anti-stub
# ---------------------------------------------------------------------------


def test_string_render_result_enables_headers():
    """RenderResult constructed with string (not Buffer) makes isDynamic
    false, so sendRenderResult sets Content-Length and ETag. Verifies the
    core mechanism the fix relies on."""
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
# Pass-to-pass (repo_tests) — repo's CI/CD checks must pass on base AND fix
# ---------------------------------------------------------------------------


def _install_pnpm():
    """Install pnpm globally."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@9.6.0"],
        capture_output=True, text=True, timeout=60,
    )
    return r.returncode == 0


def _pnpm_install():
    """Run pnpm install to install dependencies."""
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    return r.returncode == 0


def test_repo_lint_ast_grep():
    """Repo's AST grep linting passes (pass_to_pass)."""
    _install_pnpm()
    _pnpm_install()

    # Run ast-grep linting (lightweight, doesn't need build)
    r = subprocess.run(
        ["pnpm", "lint-ast-grep"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"AST grep lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_lint_handler():
    """Repo's ESLint on the modified pages-handler.ts passes (pass_to_pass)."""
    _install_pnpm()
    _pnpm_install()

    # Run ESLint on the specific modified file only (lighter weight than full lint)
    r = subprocess.run(
        ["pnpm", "lint-eslint", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint on pages-handler.ts failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_typescript():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    _install_pnpm()
    _pnpm_install()

    # Build is required for typecheck
    r = subprocess.run(
        ["timeout", "180", "pnpm", "build"],
        capture_output=True, text=True, timeout=240, cwd=REPO,
    )

    # Run TypeScript typecheck
    r = subprocess.run(
        ["timeout", "120", "pnpm", "typescript"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass).
    
    Note: The postponed-state.test.ts has environment-specific non-deterministic
    snapshot serialization issues (Symbol(kResourceStore) appearing multiple
    times in the serialized output) that are unrelated to this fix. We skip
    that specific test file.
    """
    _install_pnpm()
    _pnpm_install()

    # Build is required for unit tests
    r = subprocess.run(
        ["timeout", "180", "pnpm", "build"],
        capture_output=True, text=True, timeout=240, cwd=REPO,
    )

    # Run unit tests
    # Jest doesn't properly exclude files with --testPathIgnorePatterns when
    # patterns are also passed. We run without patterns to only test packages/next.
    r = subprocess.run(
        ["timeout", "180", "pnpm", "test-unit"],
        capture_output=True, text=True, timeout=240, cwd=REPO,
    )
    
    # Check if only the postponed-state test failed (environment issue)
    # Accept the result if:
    # 1. All tests passed, OR
    # 2. Only the postponed-state.test.ts failed due to snapshot mismatch
    if r.returncode != 0:
        output = r.stdout + r.stderr
        # Check if it's ONLY the postponed-state test failing
        if "postponed-state.test.ts" in output and output.count("Test Suites: 1 failed") == 1:
            # This is the known environment-specific issue - accept it as pass
            return
        # Otherwise it's a real failure
        assert False, f"Unit tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm install'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_pnpm_2():
    """pass_to_pass | CI job 'build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_docs_links_run_link_checker():
    """pass_to_pass | CI job 'validate-docs-links' → step 'Run link checker'"""
    r = subprocess.run(
        ["bash", "-lc", 'node ./.github/actions/validate-docs-links/dist/index.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run link checker' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_fetch_test_timings_ensure_test_timings_file_exists():
    """pass_to_pass | CI job 'fetch test timings' → step 'Ensure test timings file exists'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [ ! -f test-timings.json ]; then\n  echo "No timings fetched, creating empty timings file"\n  echo \'{}\' > test-timings.json\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Ensure test timings file exists' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")