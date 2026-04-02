"""
Task: opencode-embedded-webui-serve
Repo: anomalyco/opencode @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
PR:   19299

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
from pathlib import Path

REPO = "/repo"

FLAG_TS = f"{REPO}/packages/opencode/src/flag/flag.ts"
SERVER_TS = f"{REPO}/packages/opencode/src/server/server.ts"
BUILD_TS = f"{REPO}/packages/opencode/script/build.ts"


def _bun_eval(code: str, *, cwd: str = REPO, env: dict | None = None, timeout: int = 30):
    """Run a bun eval snippet and return the CompletedProcess."""
    run_env = {**os.environ, **(env or {})}
    return subprocess.run(
        ["bun", "-e", code],
        cwd=cwd,
        capture_output=True,
        timeout=timeout,
        env=run_env,
    )


def _ts_helper():
    """Return JS preamble that loads TypeScript and the three source files."""
    return f"""
        const ts = require('typescript');
        const fs = require('fs');
        function parse(path, label) {{
            const src = fs.readFileSync(path, 'utf8');
            return ts.createSourceFile(label, src, ts.ScriptTarget.Latest, true);
        }}
    """


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_all_modified_files():
    """All three modified files must parse without TypeScript syntax errors."""
    # AST-only because: TypeScript files cannot be imported directly from Python
    for label, filepath in [("flag.ts", FLAG_TS), ("server.ts", SERVER_TS), ("build.ts", BUILD_TS)]:
        r = _bun_eval(f"""
            const ts = require('typescript');
            const src = require('fs').readFileSync('{filepath}', 'utf8');
            const sf = ts.createSourceFile('{label}', src, ts.ScriptTarget.Latest, true);
            const diags = sf.parseDiagnostics || [];
            if (diags.length > 0) throw new Error('{label} has parse errors: ' + JSON.stringify(diags));
        """)
        assert r.returncode == 0, f"{label} failed to parse:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_disable_embedded_webui_exported():
    """Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI is exported and falsy by default."""
    r = _bun_eval("""
        const { Flag } = await import('./packages/opencode/src/flag/flag.ts');
        if (typeof Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI === 'undefined')
            throw new Error('OPENCODE_DISABLE_EMBEDDED_WEB_UI not exported');
        if (Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI)
            throw new Error('Should be falsy when env var is not set');
    """)
    assert r.returncode == 0, f"Flag not exported or not falsy:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_flag_truthy_when_env_set():
    """Flag responds to OPENCODE_DISABLE_EMBEDDED_WEB_UI env var with various truthy values."""
    for val in ["1", "true", "TRUE"]:
        r = _bun_eval(
            """
            const { Flag } = await import('./packages/opencode/src/flag/flag.ts');
            if (!Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI)
                throw new Error('Should be truthy when env var is set');
            """,
            env={"OPENCODE_DISABLE_EMBEDDED_WEB_UI": val},
        )
        assert r.returncode == 0, f"Flag not truthy with value '{val}':\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_build_script_skip_embed_flag():
    """Build script recognizes --skip-embed-web-ui flag (string literal in AST, not comment)."""
    # AST-only because: build.ts is a top-level build script with side effects that triggers
    # full multi-target native binary compilation; cannot be executed in test environment
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{BUILD_TS}', 'utf8');
        const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);
        let found = false;
        function visit(node) {{
            if (ts.isStringLiteral(node) && node.text === '--skip-embed-web-ui') found = true;
            ts.forEachChild(node, visit);
        }}
        visit(sf);
        if (!found) throw new Error('No --skip-embed-web-ui string literal in build.ts');
    """)
    assert r.returncode == 0, f"--skip-embed-web-ui not found:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_build_script_asset_bundling_function():
    """Build script has an asset bundling function that scans files (Glob/scan/readdir)."""
    # AST-only because: build.ts runs a full multi-target compilation pipeline with
    # native binary generation; cannot be executed in test environment
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{BUILD_TS}', 'utf8');
        const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);
        let found = false;
        function visit(node) {{
            const isFn = ts.isFunctionDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node);
            if (isFn && node.body) {{
                let hasFileScan = false;
                let stmtCount = 0;
                function inner(n) {{
                    if (ts.isIdentifier(n) && ['Glob','glob','scan','readdir','readdirSync','fromAsync'].includes(n.text))
                        hasFileScan = true;
                    ts.forEachChild(n, inner);
                }}
                inner(node.body);
                if (ts.isBlock(node.body)) stmtCount = node.body.statements.length;
                if (hasFileScan && stmtCount >= 3) found = true;
            }}
            ts.forEachChild(node, visit);
        }}
        visit(sf);
        if (!found) throw new Error('No asset-bundling function with file scanning found');
    """)
    assert r.returncode == 0, f"Asset bundling function not found:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_build_entrypoints_include_generated_module():
    """Build config entrypoints array includes the generated web UI module."""
    # AST-only because: build.ts runs full compilation; cannot execute safely
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{BUILD_TS}', 'utf8');
        const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

        // Find an array literal containing a string with 'web-ui' or 'webui' (the generated module)
        // that also contains './src/index.ts' (the main entrypoint) — this is the entrypoints array
        let found = false;
        function visit(node) {{
            if (ts.isArrayLiteralExpression(node)) {{
                const texts = [];
                function collect(n) {{
                    if (ts.isStringLiteral(n)) texts.push(n.text);
                    if (ts.isSpreadElement(n)) {{
                        // Check spread for conditional generated module inclusion
                        let hasGenRef = false;
                        function walkSpread(s) {{
                            if (ts.isStringLiteral(s) && (s.text.includes('web-ui') || s.text.includes('webui') || s.text.includes('.gen')))
                                hasGenRef = true;
                            ts.forEachChild(s, walkSpread);
                        }}
                        walkSpread(n);
                        if (hasGenRef) texts.push('__generated__');
                    }}
                    ts.forEachChild(n, collect);
                }}
                node.elements.forEach(el => collect(el));
                const hasMain = texts.some(t => t.includes('index.ts'));
                const hasGen = texts.some(t => t.includes('web-ui') || t.includes('webui') || t.includes('.gen') || t === '__generated__');
                if (hasMain && hasGen) found = true;
            }}
            ts.forEachChild(node, visit);
        }}
        visit(sf);
        if (!found) throw new Error('Entrypoints array does not include generated web UI module alongside main entrypoint');
    """)
    assert r.returncode == 0, f"Generated module not in entrypoints:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_server_catch_all_branches_on_embedded_ui():
    """Server catch-all route (.all('/*')) has conditional branching and file-serving ops."""
    # AST-only because: server.ts requires full app context (database, auth, session layers)
    # and starts listening on a port; cannot be imported in isolation
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

        let catchAllCb = null;
        function findAll(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                if (node.expression.name.text === 'all' && node.arguments.length >= 2) {{
                    const first = node.arguments[0];
                    if (ts.isStringLiteral(first) && first.text === '/*') catchAllCb = node.arguments[1];
                }}
            }}
            ts.forEachChild(node, findAll);
        }}
        findAll(sf);
        if (!catchAllCb) throw new Error('No .all("/*") catch-all route found');

        let hasIf = false;
        function findIf(node) {{
            if (ts.isIfStatement(node) || ts.isConditionalExpression(node)) hasIf = true;
            ts.forEachChild(node, findIf);
        }}
        ts.forEachChild(catchAllCb, findIf);
        if (!hasIf) throw new Error('Catch-all has no conditional branching');

        let hasFileOp = false;
        function findFileOp(node) {{
            if (ts.isPropertyAccessExpression(node)) {{
                const n = node.name.text;
                if (['file','arrayBuffer','readFile','body','readFileSync','blob'].includes(n)) hasFileOp = true;
            }}
            ts.forEachChild(node, findFileOp);
        }}
        ts.forEachChild(catchAllCb, findFileOp);
        if (!hasFileOp) throw new Error('Catch-all has no file-serving operation');
    """)
    assert r.returncode == 0, f"Catch-all branching/file-serving not found:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_server_spa_fallback_to_index_html():
    """Server has SPA fallback: index.html used as a fallback key in the catch-all route."""
    # AST-only because: server.ts requires full app context and cannot be imported
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

        // Find the catch-all callback
        let catchAllCb = null;
        function findAll(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                if (node.expression.name.text === 'all' && node.arguments.length >= 2) {{
                    const first = node.arguments[0];
                    if (ts.isStringLiteral(first) && first.text === '/*') catchAllCb = node.arguments[1];
                }}
            }}
            ts.forEachChild(node, findAll);
        }}
        findAll(sf);
        if (!catchAllCb) throw new Error('No .all("/*") catch-all route found');

        // Check index.html is used as a fallback within the catch-all
        let hasIndexFallback = false;
        function findFallback(node) {{
            if (ts.isStringLiteral(node) && node.text === 'index.html') hasIndexFallback = true;
            ts.forEachChild(node, findFallback);
        }}
        ts.forEachChild(catchAllCb, findFallback);
        if (!hasIndexFallback) throw new Error('No index.html SPA fallback in catch-all route');
    """)
    assert r.returncode == 0, f"index.html fallback not found in catch-all:\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_server_csp_for_embedded_html():
    """Server sets Content-Security-Policy header when serving HTML from embedded UI."""
    # AST-only because: server.ts requires full app context and cannot be imported
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

        // Check for a CSP-related string literal anywhere in the file
        let hasCspString = false;
        function visit(node) {{
            if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {{
                const text = node.text || '';
                if (text.includes('Content-Security-Policy') || text.includes("default-src"))
                    hasCspString = true;
            }}
            ts.forEachChild(node, visit);
        }}
        visit(sf);
        if (!hasCspString) throw new Error('No Content-Security-Policy string found in server.ts');

        // Also verify CSP is set within the catch-all embedded UI branch
        let catchAllCb = null;
        function findAll(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                if (node.expression.name.text === 'all' && node.arguments.length >= 2) {{
                    const first = node.arguments[0];
                    if (ts.isStringLiteral(first) && first.text === '/*') catchAllCb = node.arguments[1];
                }}
            }}
            ts.forEachChild(node, findAll);
        }}
        findAll(sf);
        if (!catchAllCb) throw new Error('No .all("/*") catch-all route found');

        let hasCspInCatchAll = false;
        function findCsp(node) {{
            if (ts.isStringLiteral(node) && (node.text === 'Content-Security-Policy' || node.text.includes('default-src')))
                hasCspInCatchAll = true;
            ts.forEachChild(node, findCsp);
        }}
        ts.forEachChild(catchAllCb, findCsp);
        if (!hasCspInCatchAll) throw new Error('CSP not set within the catch-all route for embedded UI');
    """)
    assert r.returncode == 0, f"CSP header not found:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_proxy_fallback_preserved():
    """Proxy fallback to app.opencode.ai is preserved in server code."""
    # AST-only because: server.ts cannot be imported; checking source for proxy URL
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);
        let found = false;
        function visit(node) {{
            if (ts.isStringLiteral(node) && node.text.includes('app.opencode.ai')) found = true;
            if (ts.isNoSubstitutionTemplateLiteral(node) && node.text.includes('app.opencode.ai')) found = true;
            if (ts.isTemplateHead(node) && node.text.includes('app.opencode.ai')) found = true;
            ts.forEachChild(node, visit);
        }}
        visit(sf);
        if (!found) throw new Error('Proxy target app.opencode.ai not found');
    """)
    assert r.returncode == 0, f"Proxy fallback not preserved:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:12 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_dynamic_import_uses_catch_chain():
    """Dynamic import() of embedded UI module uses .catch() promise chain, not try/catch (AGENTS.md:12)."""
    # AST-only because: the dynamic import only resolves at build time; can't test at runtime
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

        // Find dynamic import() calls
        let importNodes = [];
        function findImports(node) {{
            if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword)
                importNodes.push(node);
            ts.forEachChild(node, findImports);
        }}
        findImports(sf);
        if (importNodes.length === 0) throw new Error('No dynamic import() found in server.ts');

        // At least one dynamic import must be in a .catch() chain
        let hasCatchOnImport = false;
        function findCatch(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                if (node.expression.name.text === 'catch') {{
                    let hasImport = false;
                    function walkLeft(n) {{
                        if (ts.isCallExpression(n) && n.expression.kind === ts.SyntaxKind.ImportKeyword)
                            hasImport = true;
                        ts.forEachChild(n, walkLeft);
                    }}
                    walkLeft(node.expression.expression);
                    if (hasImport) hasCatchOnImport = true;
                }}
            }}
            ts.forEachChild(node, findCatch);
        }}
        findCatch(sf);
        if (!hasCatchOnImport) throw new Error('Dynamic import not followed by .catch()');
    """)
    assert r.returncode == 0, f".catch() chain not found on import:\n{r.stderr.decode()}"


# [agent_config] fail_to_pass — AGENTS.md:15 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_server_uses_bun_file_api():
    """Server uses Bun.file() API for serving embedded files (AGENTS.md:15: Use Bun APIs)."""
    # AST-only because: server.ts requires full app context and cannot be imported
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{SERVER_TS}', 'utf8');
        const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

        // Find the catch-all route callback
        let catchAllCb = null;
        function findAll(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                if (node.expression.name.text === 'all' && node.arguments.length >= 2) {{
                    const first = node.arguments[0];
                    if (ts.isStringLiteral(first) && first.text === '/*') catchAllCb = node.arguments[1];
                }}
            }}
            ts.forEachChild(node, findAll);
        }}
        findAll(sf);
        if (!catchAllCb) throw new Error('No .all("/*") catch-all route found');

        // Check for Bun.file() usage within the catch-all
        let hasBunFile = false;
        function findBunFile(node) {{
            if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {{
                const obj = node.expression.expression;
                const prop = node.expression.name;
                if (ts.isIdentifier(obj) && obj.text === 'Bun' && prop.text === 'file')
                    hasBunFile = true;
            }}
            ts.forEachChild(node, findBunFile);
        }}
        ts.forEachChild(catchAllCb, findBunFile);
        if (!hasBunFile) throw new Error('Bun.file() not used in catch-all route for serving embedded files');
    """)
    assert r.returncode == 0, f"Bun.file() not found in catch-all:\n{r.stderr.decode()}"


# [agent_config] fail_to_pass — AGENTS.md:17 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_build_uses_functional_array_methods():
    """Asset bundling function uses functional array methods (.map/.join), not for-loops (AGENTS.md:17)."""
    # AST-only because: build.ts runs full compilation; cannot execute safely
    r = _bun_eval(f"""
        const ts = require('typescript');
        const src = require('fs').readFileSync('{BUILD_TS}', 'utf8');
        const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

        // Find the asset bundling function (has file scanning + multiple statements)
        let bundleFn = null;
        function findFn(node) {{
            const isFn = ts.isFunctionDeclaration(node) || ts.isArrowFunction(node) || ts.isFunctionExpression(node);
            if (isFn && node.body) {{
                let hasFileScan = false;
                function inner(n) {{
                    if (ts.isIdentifier(n) && ['Glob','glob','scan','readdir','readdirSync','fromAsync'].includes(n.text))
                        hasFileScan = true;
                    ts.forEachChild(n, inner);
                }}
                inner(node.body);
                if (hasFileScan) bundleFn = node;
            }}
            ts.forEachChild(node, findFn);
        }}
        findFn(sf);
        if (!bundleFn) throw new Error('No asset bundling function found');

        // Check the function uses .map() or .join()
        let hasMapOrJoin = false;
        function findMethod(node) {{
            if (ts.isPropertyAccessExpression(node) && ['map','join','flatMap','reduce'].includes(node.name.text))
                hasMapOrJoin = true;
            ts.forEachChild(node, findMethod);
        }}
        findMethod(bundleFn);
        if (!hasMapOrJoin) throw new Error('Bundling function does not use functional array methods (.map/.join)');
    """)
    assert r.returncode == 0, f"Functional array methods not found:\n{r.stderr.decode()}"
