"""Behavioral tests for remix-run/remix PR #11027.

The PR fixes vitest benchmark files in packages/route-pattern/bench/.
The bug: vitest re-runs bench() callbacks many times during calibration,
causing matchers inside bench() to accumulate duplicate route entries.
The fix: move matcher initialization to the appropriate scope (fresh in setup
benchmarks, once in match benchmarks) and add TrieMatcher benchmarks.

All AST checks use the TypeScript compiler API via Node.js subprocess
since the benchmark files are vitest-specific configurations that cannot
be imported as regular modules.
"""

import json
import subprocess

REPO = "/workspace/remix"
BENCH_FILES = [
    "packages/route-pattern/bench/simple.bench.ts",
    "packages/route-pattern/bench/pathological.bench.ts",
]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _ts_check(check_js_body: str) -> dict:
    """Run a TypeScript AST check across all benchmark files.

    check_js_body is JavaScript that runs inside a for-of loop over files.
    It has access to: sf (SourceFile), f (file path), results (accumulator dict).
    Set results[f] = true/false for each file.
    """
    script = f"""
    const ts = require('typescript');
    const fs = require('fs');
    const files = {json.dumps(BENCH_FILES)};
    const results = {{}};
    for (const f of files) {{
        const src = fs.readFileSync(f, 'utf8');
        const sf = ts.createSourceFile(f, src, ts.ScriptTarget.Latest, true);
        {check_js_body}
    }}
    console.log(JSON.stringify(results));
    """
    r = subprocess.run(
        ["node", "--no-warnings", "-e", script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"TypeScript AST check failed:\n{r.stderr}")
    return json.loads(r.stdout)


def _assert_all(results: dict, msg: str) -> None:
    failures = {f: v for f, v in results.items() if not v}
    assert not failures, f"{msg}: {failures}"


# ---------------------------------------------------------------------------
# fail_to_pass tests
# ---------------------------------------------------------------------------

def test_trie_matcher_imported():
    """TrieMatcher is imported alongside ArrayMatcher in both benchmark files."""
    results = _ts_check("""
        let hasTrie = false;
        ts.forEachChild(sf, (node) => {
            if (ts.isImportDeclaration(node) &&
                node.moduleSpecifier.text === '@remix-run/route-pattern') {
                const clause = node.importClause;
                if (clause && clause.namedBindings && ts.isNamedImports(clause.namedBindings)) {
                    for (const el of clause.namedBindings.elements) {
                        if (el.name.text === 'TrieMatcher') hasTrie = true;
                    }
                }
            }
        });
        results[f] = hasTrie;
    """)
    _assert_all(results, "TrieMatcher not imported from @remix-run/route-pattern")


def test_no_matchers_module_variable():
    """The old 'matchers' module-level variable with ArrayMatcher is removed."""
    results = _ts_check("""
        let hasOldVar = false;
        ts.forEachChild(sf, (node) => {
            if (ts.isVariableStatement(node)) {
                for (const decl of node.declarationList.declarations) {
                    if (ts.isIdentifier(decl.name) && decl.name.text === 'matchers') {
                        const init = decl.initializer;
                        if (init && ts.isArrayLiteralExpression(init)) {
                            hasOldVar = true;
                        }
                    }
                }
            }
        });
        results[f] = !hasOldVar;
    """)
    _assert_all(results, "Old 'matchers' variable still present")


def test_no_destructure_for_of_in_describe():
    """No for-of loop destructuring matchers inside describe() blocks."""
    results = _ts_check("""
        let hasBadPattern = false;
        function walk(node) {
            if (ts.isCallExpression(node) &&
                ts.isIdentifier(node.expression) && node.expression.text === 'describe') {
                // Inside a describe() call, check for for-of with destructuring
                const body = node.arguments[1];
                if (body) {
                    findForOf(body);
                }
            }
            ts.forEachChild(node, walk);
        }
        function findForOf(node) {
            if (ts.isForOfStatement(node) &&
                ts.isVariableDeclarationList(node.initializer)) {
                const decl = node.initializer.declarations[0];
                if (decl && ts.isObjectBindingPattern(decl.name)) {
                    for (const el of decl.name.elements) {
                        if (ts.isIdentifier(el.name) && el.name.text === 'matcher') {
                            hasBadPattern = true;
                            return;
                        }
                    }
                }
            }
            ts.forEachChild(node, findForOf);
        }
        walk(sf);
        results[f] = !hasBadPattern;
    """)
    _assert_all(results, "For-of loop destructuring 'matcher' inside describe() still present")


# ---------------------------------------------------------------------------
# pass_to_pass tests
# ---------------------------------------------------------------------------

def test_prettier_format():
    """Benchmark files pass prettier format check."""
    for f in BENCH_FILES:
        r = subprocess.run(
            ["npx", "prettier", "--check", f],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed for {f}:\n{r.stderr[-300:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")