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


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code using Node.js (CommonJS mode)."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_check():
    """Modified pages-handler.ts must parse without syntax errors."""
    target_file = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"
    assert target_file.exists(), f"Target file not found: {target_file}"

    r = subprocess.run(
        ["node", "--check", str(target_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax errors in pages-handler.ts:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_render_result_isDynamic_behavior():
    """Execute the actual RenderResult class: string->isDynamic=false, Buffer->isDynamic=true.

    The fix removes Buffer.from() wrappers so RenderResult receives strings.
    When isDynamic=false (string response), Content-Length and ETag headers
    are added to the response. This test verifies that core mechanism by
    transpiling and executing the real RenderResult class from the repo.
    """
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');

// Read and transpile the actual render-result.ts to JavaScript
const source = fs.readFileSync('packages/next/src/server/render-result.ts', 'utf8');
const { outputText } = ts.transpileModule(source, {
  compilerOptions: { module: 1 /* CommonJS */, target: 9 /* ES2022 */ }
});

// Stub external imports so the class can be instantiated standalone
let js = outputText;
js = js.replaceAll(
  'require("./stream-utils/node-web-streams-helper")',
  '({ chainStreams: (...a) => a[0], streamFromBuffer: () => new ReadableStream(), streamFromString: () => new ReadableStream(), streamToString: async () => "" })'
);
js = js.replaceAll(
  'require("./pipe-readable")',
  '({ isAbortError: () => false, pipeToNodeResponse: async () => {} })'
);
js = js.replaceAll(
  'require("../shared/lib/invariant-error")',
  '({ InvariantError: class InvariantError extends Error {} })'
);

// Execute in a module sandbox
const moduleExports = {};
const moduleObj = { exports: moduleExports };
const fn = new Function('module', 'exports', 'require', 'Buffer', 'ReadableStream', js);
fn(moduleObj, moduleExports, require, Buffer, ReadableStream);

const RenderResult = moduleObj.exports.default || moduleExports.default;

// Test: string response should be non-dynamic (enables Content-Length/ETag)
const strResult = new RenderResult('{"page":"data"}', { contentType: null, metadata: {} });
// Test: Buffer response should be dynamic (skips Content-Length/ETag)
const bufResult = new RenderResult(Buffer.from('{"page":"data"}'), { contentType: null, metadata: {} });

console.log(JSON.stringify({
  stringIsDynamic: strResult.isDynamic,
  bufferIsDynamic: bufResult.isDynamic,
}));
""")
    assert r.returncode == 0, f"Failed to execute RenderResult: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["stringIsDynamic"] is False, \
        "RenderResult with string should have isDynamic=false (enables Content-Length/ETag headers)"
    assert data["bufferIsDynamic"] is True, \
        "RenderResult with Buffer should have isDynamic=true (skips Content-Length/ETag headers)"


# [pr_diff] fail_to_pass
def test_pages_handler_no_buffer_wrapping():
    """Verify pages-handler.ts does not wrap RenderResult args with Buffer.from().

    Uses TypeScript AST analysis (not regex) to find any
    new RenderResult(Buffer.from(...)) patterns. This is robust to code
    formatting, variable naming, and alternative fix structures.
    """
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');

const source = fs.readFileSync(
  'packages/next/src/server/route-modules/pages/pages-handler.ts', 'utf8'
);
const sourceFile = ts.createSourceFile(
  'pages-handler.ts', source, ts.ScriptTarget.Latest, true
);

const issues = [];

function visit(node) {
  // Find: new RenderResult(Buffer.from(...), ...)
  if (ts.isNewExpression(node) &&
      ts.isIdentifier(node.expression) &&
      node.expression.text === 'RenderResult' &&
      node.arguments && node.arguments.length > 0) {
    const firstArg = node.arguments[0];
    if (ts.isCallExpression(firstArg) &&
        ts.isPropertyAccessExpression(firstArg.expression) &&
        ts.isIdentifier(firstArg.expression.expression) &&
        firstArg.expression.expression.text === 'Buffer' &&
        firstArg.expression.name.text === 'from') {
      const { line } = sourceFile.getLineAndCharacterOfPosition(node.getStart());
      issues.push(line + 1);
    }
  }
  ts.forEachChild(node, visit);
}

visit(sourceFile);
console.log(JSON.stringify({ count: issues.length, lines: issues }));
""")
    assert r.returncode == 0, f"AST analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] == 0, \
        f"pages-handler.ts still wraps RenderResult first argument with Buffer.from() " \
        f"at line(s) {data['lines']}. Wrapping with Buffer.from() causes " \
        f"RenderResult.isDynamic=true, which prevents Content-Length and ETag headers " \
        f"from being set on the response."


# [pr_diff] fail_to_pass
def test_agents_md_new_test_syntax_fixed():
    """AGENTS.md must show correct pnpm new-test syntax with '-- --args' separator."""
    agents_file = Path(REPO) / "AGENTS.md"
    assert agents_file.exists(), "AGENTS.md not found"

    content = agents_file.read_text()

    assert "pnpm new-test -- --args" in content, \
        "AGENTS.md NOT UPDATED: Missing correct 'pnpm new-test -- --args' syntax. " \
        "The command needs '--' separator to properly forward args to the script."


# [pr_diff] fail_to_pass
def test_agents_md_no_bare_args_flag():
    """AGENTS.md should NOT show the incorrect bare '--args' without separator."""
    agents_file = Path(REPO) / "AGENTS.md"
    content = agents_file.read_text()

    import re
    bare_args_pattern = r'pnpm\s+new-test\s+--args\s'
    matches = re.findall(bare_args_pattern, content)

    assert len(matches) == 0, \
        f"AGENTS.md HAS INCORRECT SYNTAX: Found {len(matches)} instance(s) of bare " \
        f"'pnpm new-test --args' without '--' separator. " \
        f"The correct syntax is 'pnpm new-test -- --args ...'"


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
    import re
    content_errors = re.findall(r'^\s*error:.*$', r.stderr, re.MULTILINE | re.IGNORECASE)
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


# [repo_tests] pass_to_pass
def test_repo_tsc_pages_handler():
    """TypeScript compilation check on pages-handler.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "packages/next/src/server/route-modules/pages/pages-handler.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0 or "pages-handler.ts" not in r.stderr, \
        f"TypeScript check failed on pages-handler.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tsc_render_result():
    """TypeScript compilation check on render-result.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "packages/next/src/server/render-result.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0 or "render-result.ts" not in r.stderr, \
        f"TypeScript check failed on render-result.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
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

    lines = content.split('\n')
    non_empty = [l for l in lines if l.strip() and not l.strip().startswith('//')]
    assert len(non_empty) > 50, "Handler file appears to be a stub or empty"

    assert "export const getHandler" in content, "Missing getHandler export"
    assert "RenderResult" in content, "Missing RenderResult usage"
