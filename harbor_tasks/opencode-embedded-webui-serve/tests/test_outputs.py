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


def _bun_run_script(code: str, *, cwd: str = REPO, env: dict | None = None, timeout: int = 30):
    """Run a bun script from a .ts file and return the CompletedProcess."""
    run_env = {**os.environ, **(env or {})}
    script = Path(REPO) / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["bun", "run", str(script)],
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            env=run_env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_all_modified_files():
    """All three modified files must parse without TypeScript syntax errors."""
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
    code = '''
import { Flag } from "./packages/opencode/src/flag/flag.ts";

if (typeof Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI === 'undefined') {
    console.error("FAIL: OPENCODE_DISABLE_EMBEDDED_WEB_UI not exported");
    process.exit(1);
}

if (Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI) {
    console.error("FAIL: Should be falsy when env var is not set, got:", Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI);
    process.exit(1);
}

console.log("PASS: Flag exported and falsy by default");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Flag not exported or not falsy:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_flag_truthy_when_env_set():
    """Flag responds to OPENCODE_DISABLE_EMBEDDED_WEB_UI env var with various truthy values."""
    for val in ["1", "true", "TRUE"]:
        code = f'''
import {{ Flag }} from "./packages/opencode/src/flag/flag.ts";

if (!Flag.OPENCODE_DISABLE_EMBEDDED_WEB_UI) {{
    console.error("FAIL: Should be truthy when env var is set to {val}");
    process.exit(1);
}}

console.log("PASS: Flag is truthy with value {val}");
'''
        r = _bun_run_script(code, env={"OPENCODE_DISABLE_EMBEDDED_WEB_UI": val})
        assert r.returncode == 0, f"Flag not truthy with value '{val}':\n{r.stderr.decode()}\n{r.stdout.decode()}"
        assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_build_script_skip_embed_flag():
    """Build script recognizes --skip-embed-web-ui flag by parsing CLI arguments."""
    # Extract the flag parsing logic and test it executes correctly
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/script/build.ts', 'utf8');
const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

// Find the skipEmbedWebUi variable declaration with process.argv.includes
let foundFlagParsing = false;
function visit(node: ts.Node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) && node.name.text === 'skipEmbedWebUi') {
        const text = src.substring(node.pos, node.end);
        if (text.includes('--skip-embed-web-ui') && text.includes('process.argv.includes')) {
            foundFlagParsing = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!foundFlagParsing) {
    console.error("FAIL: --skip-embed-web-ui flag parsing not found");
    process.exit(1);
}

console.log("PASS: --skip-embed-web-ui flag parsing found");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"--skip-embed-web-ui flag not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_build_script_asset_bundling_function():
    """Build script has an asset bundling function that scans files and generates module code."""
    # Run Bun script to verify the asset bundling logic exists and is valid TypeScript
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/script/build.ts', 'utf8');
const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

// Find the createEmbeddedWebUIBundle function
let foundFunction = false;
let foundBody = null;

function visit(node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'createEmbeddedWebUIBundle') {
        foundFunction = true;
        if (node.initializer && (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
            foundBody = node.initializer.body;
        }
    }
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'createEmbeddedWebUIBundle') {
        foundFunction = true;
        foundBody = node.body;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!foundFunction || !foundBody) {
    console.error("FAIL: createEmbeddedWebUIBundle function not found");
    process.exit(1);
}

// Check the body for required patterns
const bodyText = src.substring(foundBody.pos, foundBody.end);

const hasGlob = bodyText.includes('Bun.Glob') || bodyText.includes('new Glob');
const hasScan = bodyText.includes('.scan(');
const hasMapGeneration = bodyText.includes('.map(') && bodyText.includes('with { type: "file" }');
const hasExportDefault = bodyText.includes('export default');

if (!hasGlob) {
    console.error("FAIL: Bun.Glob usage not found in bundling function");
    process.exit(1);
}

if (!hasScan) {
    console.error("FAIL: .scan() method call not found in bundling function");
    process.exit(1);
}

if (!hasMapGeneration) {
    console.error("FAIL: File map generation with imports not found");
    process.exit(1);
}

if (!hasExportDefault) {
    console.error("FAIL: Export default mapping not found");
    process.exit(1);
}

console.log("PASS: Asset bundling function with file scanning found");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Asset bundling function not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_build_entrypoints_include_generated_module():
    """Build config entrypoints array includes the generated web UI module."""
    # Run Bun script with TypeScript AST parsing to verify entrypoints
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/script/build.ts', 'utf8');
const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

// Find the compile configuration object with entrypoints
let foundEntrypoints = false;
let foundGenerated = false;

function visit(node) {
    // Look for entrypoints property in object literals
    if (ts.isPropertyAssignment(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'entrypoints' && ts.isArrayLiteralExpression(node.initializer)) {
        foundEntrypoints = true;

        // Check array elements
        const elements = node.initializer.elements;
        let hasMain = false;
        let hasGenerated = false;

        for (const el of elements) {
            if (ts.isStringLiteral(el)) {
                if (el.text.includes('index.ts')) hasMain = true;
                if (el.text.includes('web-ui') || el.text.includes('.gen.ts')) hasGenerated = true;
            }
            // Check for spread element: ...(embeddedFileMap ? [...] : [])
            if (ts.isSpreadElement(el)) {
                const spreadText = src.substring(el.expression.pos, el.expression.end);
                if (spreadText.includes('embeddedFileMap') && spreadText.includes('web-ui')) {
                    hasGenerated = true;
                }
            }
        }

        if (hasMain && hasGenerated) {
            foundGenerated = true;
        }
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!foundEntrypoints) {
    console.error("FAIL: entrypoints configuration not found");
    process.exit(1);
}

if (!foundGenerated) {
    console.error("FAIL: Generated web UI module not found in entrypoints alongside main entry");
    process.exit(1);
}

console.log("PASS: Entrypoints array includes generated web UI module conditionally");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Generated module not in entrypoints:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_server_catch_all_branches_on_embedded_ui():
    """Server catch-all route (.all('/*')) has conditional branching and file-serving ops."""
    # Run Bun script with TypeScript AST parsing to verify server routing logic
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');
const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

// Find embeddedUIPromise declaration
let hasEmbeddedUIPromise = false;
function findPromise(node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'embeddedUIPromise') {
        hasEmbeddedUIPromise = true;
    }
    ts.forEachChild(node, findPromise);
}
findPromise(sf);

if (!hasEmbeddedUIPromise) {
    console.error("FAIL: embeddedUIPromise not found");
    process.exit(1);
}

// Find the .all("/*") catch-all route
let catchAllHandler = null;
function findCatchAll(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        if (node.expression.name.text === 'all' && node.arguments.length >= 2) {
            const firstArg = node.arguments[0];
            if (ts.isStringLiteral(firstArg) && firstArg.text === '/*') {
                catchAllHandler = node.arguments[node.arguments.length - 1];
            }
        }
    }
    ts.forEachChild(node, findCatchAll);
}
findCatchAll(sf);

if (!catchAllHandler) {
    console.error("FAIL: .all('/*') catch-all route not found");
    process.exit(1);
}

// Check the handler for conditional branching and file operations
const handlerText = src.substring(catchAllHandler.pos, catchAllHandler.end);

const hasConditional = handlerText.includes('if (embeddedWebUI)') || handlerText.includes('if(embeddedWebUI)');
const hasBunFile = handlerText.includes('Bun.file(');
const hasFileType = handlerText.includes('file.type');
const hasArrayBuffer = handlerText.includes('.arrayBuffer()');

if (!hasConditional) {
    console.error("FAIL: Conditional branching on embeddedWebUI not found in catch-all");
    process.exit(1);
}

if (!hasBunFile) {
    console.error("FAIL: Bun.file() usage not found in catch-all");
    process.exit(1);
}

if (!hasFileType) {
    console.error("FAIL: file.type usage not found in catch-all");
    process.exit(1);
}

if (!hasArrayBuffer) {
    console.error("FAIL: file.arrayBuffer() usage not found in catch-all");
    process.exit(1);
}

console.log("PASS: Server has catch-all branching and file-serving operations");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Catch-all branching/file-serving not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_server_spa_fallback_to_index_html():
    """Server has SPA fallback: index.html used as a fallback key in the catch-all route."""
    code = '''
const fs = require('fs');
const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');

// Look for the SPA fallback pattern: embeddedWebUI[path] ?? embeddedWebUI["index.html"]
const hasIndexFallback = src.includes('embeddedWebUI["index.html"]') || src.includes("embeddedWebUI['index.html']");
const hasNullishCoalescing = src.includes('??');

if (!hasIndexFallback) {
    console.error("FAIL: index.html fallback not found in catch-all route");
    process.exit(1);
}

if (!hasNullishCoalescing) {
    console.error("FAIL: Nullish coalescing operator (??) not found for fallback logic");
    process.exit(1);
}

console.log("PASS: Server has SPA fallback to index.html");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"index.html fallback not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [pr_diff] fail_to_pass
def test_server_csp_for_embedded_html():
    """Server sets Content-Security-Policy header when serving HTML from embedded UI."""
    # Run Bun script with TypeScript AST parsing to verify CSP header logic
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');
const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

// Check for DEFAULT_CSP constant
let hasDefaultCSP = false;
function findCSPConstant(node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'DEFAULT_CSP') {
        hasDefaultCSP = true;
    }
    ts.forEachChild(node, findCSPConstant);
}
findCSPConstant(sf);

if (!hasDefaultCSP) {
    console.error("FAIL: DEFAULT_CSP constant not found");
    process.exit(1);
}

// Find the .all("/*") catch-all route and check for CSP header
let catchAllHandler = null;
function findCatchAll(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        if (node.expression.name.text === 'all' && node.arguments.length >= 2) {
            const firstArg = node.arguments[0];
            if (ts.isStringLiteral(firstArg) && firstArg.text === '/*') {
                catchAllHandler = node.arguments[node.arguments.length - 1];
            }
        }
    }
    ts.forEachChild(node, findCatchAll);
}
findCatchAll(sf);

if (!catchAllHandler) {
    console.error("FAIL: .all('/*') catch-all route not found");
    process.exit(1);
}

// Check the handler for CSP header setting
const handlerText = src.substring(catchAllHandler.pos, catchAllHandler.end);
const hasCspHeader = handlerText.includes('Content-Security-Policy');
const hasFileTypeCheck = handlerText.includes('file.type') && handlerText.includes('text/html');
const hasHeaderMethod = handlerText.includes('c.header(');

if (!hasCspHeader) {
    console.error("FAIL: Content-Security-Policy header not found in catch-all");
    process.exit(1);
}

if (!hasFileTypeCheck) {
    console.error("FAIL: file.type check for HTML not found in catch-all");
    process.exit(1);
}

if (!hasHeaderMethod) {
    console.error("FAIL: c.header() call not found in catch-all");
    process.exit(1);
}

console.log("PASS: Server sets CSP header for embedded HTML");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"CSP header not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_proxy_fallback_preserved():
    """Proxy fallback to app.opencode.ai is preserved in server code."""
    code = '''
const fs = require('fs');
const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');

// Check for proxy fallback in the else branch
const hasProxyUrl = src.includes('app.opencode.ai');
const hasElseBranch = src.includes('else {');
const hasProxyCall = src.includes('await proxy(') || src.includes('proxy(`https://app.opencode.ai');

if (!hasProxyUrl) {
    console.error("FAIL: app.opencode.ai proxy URL not found");
    process.exit(1);
}

if (!hasElseBranch) {
    console.error("FAIL: else branch for proxy fallback not found");
    process.exit(1);
}

if (!hasProxyCall) {
    console.error("FAIL: proxy() call not found");
    process.exit(1);
}

console.log("PASS: Proxy fallback preserved");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Proxy fallback not preserved:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:12 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_dynamic_import_uses_catch_chain():
    """Dynamic import() of embedded UI module uses .catch() promise chain, not try/catch (AGENTS.md:12)."""
    # Run Bun script with TypeScript AST parsing to verify dynamic import pattern
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');
const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

// Find the embeddedUIPromise declaration with dynamic import
let foundDynamicImport = false;
let hasThenChain = false;
let hasCatchNull = false;
let hasTsExpectError = false;

function findPromise(node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'embeddedUIPromise') {
        // Check for @ts-expect-error before this declaration
        const leadingRanges = ts.getLeadingCommentRanges(src, node.pos);
        if (leadingRanges) {
            for (const range of leadingRanges) {
                const comment = src.substring(range.pos, range.end);
                if (comment.includes('@ts-expect-error')) {
                    hasTsExpectError = true;
                    break;
                }
            }
        }

        // Check the initializer for import().then().catch() pattern
        if (node.initializer && ts.isConditionalExpression(node.initializer)) {
            // It's a ternary - check the "else" branch for the import
            const condExpr = node.initializer;
            const elseBranch = condExpr.whenFalse;
            // Check for @ts-expect-error in the else branch text (includes the comment before import)
            const elseBranchText = src.substring(elseBranch.pos, elseBranch.end);
            if (elseBranchText.includes('@ts-expect-error')) {
                hasTsExpectError = true;
            }
            // Also check leading comments of the else branch expression
            const elseLeadingRanges = ts.getLeadingCommentRanges(src, elseBranch.pos);
            if (elseLeadingRanges) {
                for (const range of elseLeadingRanges) {
                    const comment = src.substring(range.pos, range.end);
                    if (comment.includes('@ts-expect-error')) {
                        hasTsExpectError = true;
                        break;
                    }
                }
            }
            checkImportPattern(elseBranch);
        } else if (node.initializer) {
            checkImportPattern(node.initializer);
        }
    }
    ts.forEachChild(node, findPromise);
}

function checkImportPattern(node) {
    if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword) {
        foundDynamicImport = true;
    }

    // Check for .then().catch() chain
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        if (node.expression.name.text === 'then') {
            hasThenChain = true;
            // Check if the .then() call has a .catch() chained
            if (node.parent && ts.isCallExpression(node.parent) &&
                ts.isPropertyAccessExpression(node.parent.expression) &&
                node.parent.expression.name.text === 'catch') {
                hasCatchNull = true;
            }
        }
        // Also check if this is directly a .catch() call on the import
        if (node.expression.name.text === 'catch') {
            // Walk back to find if the base is an import
            let current = node.expression.expression;
            while (current) {
                if (ts.isCallExpression(current) && current.expression.kind === ts.SyntaxKind.ImportKeyword) {
                    hasCatchNull = true;
                    break;
                }
                if (ts.isPropertyAccessExpression(current)) {
                    current = current.expression;
                } else if (ts.isCallExpression(current)) {
                    current = current.expression;
                } else {
                    break;
                }
            }
        }
    }
    ts.forEachChild(node, checkImportPattern);
}

findPromise(sf);

// Also search for the specific pattern in source text as backup
const hasImportPattern = src.includes('import("opencode-web-ui.gen.ts")') &&
                         src.includes('.then((module) =>') &&
                         src.includes('.catch(() => null)');

if (!foundDynamicImport && !hasImportPattern) {
    console.error("FAIL: Dynamic import of opencode-web-ui.gen.ts not found");
    process.exit(1);
}

if (!hasTsExpectError) {
    console.error("FAIL: @ts-expect-error comment not found before dynamic import");
    process.exit(1);
}

console.log("PASS: Dynamic import uses .catch() promise chain with @ts-expect-error");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f".catch() chain not found on import:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [agent_config] fail_to_pass — AGENTS.md:15 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_server_uses_bun_file_api():
    """Server uses Bun.file() API for serving embedded files (AGENTS.md:15: Use Bun APIs)."""
    # Run Bun script with TypeScript AST parsing to verify Bun.file() usage
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/src/server/server.ts', 'utf8');
const sf = ts.createSourceFile('server.ts', src, ts.ScriptTarget.Latest, true);

// Find the .all("/*") catch-all route
let catchAllHandler = null;
function findCatchAll(node) {
    if (ts.isCallExpression(node) && ts.isPropertyAccessExpression(node.expression)) {
        if (node.expression.name.text === 'all' && node.arguments.length >= 2) {
            const firstArg = node.arguments[0];
            if (ts.isStringLiteral(firstArg) && firstArg.text === '/*') {
                catchAllHandler = node.arguments[node.arguments.length - 1];
            }
        }
    }
    ts.forEachChild(node, findCatchAll);
}
findCatchAll(sf);

if (!catchAllHandler) {
    console.error("FAIL: .all('/*') catch-all route not found");
    process.exit(1);
}

// Check the handler for Bun.file() usage
const handlerText = src.substring(catchAllHandler.pos, catchAllHandler.end);
const hasBunFile = handlerText.includes('Bun.file(');
const hasFileExists = handlerText.includes('.exists()');
const hasFileType = handlerText.includes('.type');
const hasArrayBuffer = handlerText.includes('.arrayBuffer()');

if (!hasBunFile) {
    console.error("FAIL: Bun.file() usage not found in catch-all");
    process.exit(1);
}

if (!hasFileExists) {
    console.error("FAIL: file.exists() check not found in catch-all");
    process.exit(1);
}

if (!hasFileType) {
    console.error("FAIL: file.type usage not found in catch-all");
    process.exit(1);
}

if (!hasArrayBuffer) {
    console.error("FAIL: file.arrayBuffer() usage not found in catch-all");
    process.exit(1);
}

console.log("PASS: Server uses Bun.file() API for serving embedded files");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Bun.file() not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"


# [agent_config] fail_to_pass — AGENTS.md:17 @ 83ed1c4414859b53c91f1e2f6985c3498bac1e84
def test_build_uses_functional_array_methods():
    """Asset bundling function uses functional array methods (.map/.join), not for-loops (AGENTS.md:17)."""
    # Run Bun script with TypeScript AST parsing to verify functional methods
    code = '''
const fs = require('fs');
const ts = require('typescript');

const src = fs.readFileSync('./packages/opencode/script/build.ts', 'utf8');
const sf = ts.createSourceFile('build.ts', src, ts.ScriptTarget.Latest, true);

// Find the createEmbeddedWebUIBundle function
let foundFunction = false;
let foundBody = null;

function visit(node) {
    if (ts.isVariableDeclaration(node) && ts.isIdentifier(node.name) &&
        node.name.text === 'createEmbeddedWebUIBundle') {
        foundFunction = true;
        if (node.initializer && (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
            foundBody = node.initializer.body;
        }
    }
    if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'createEmbeddedWebUIBundle') {
        foundFunction = true;
        foundBody = node.body;
    }
    ts.forEachChild(node, visit);
}
visit(sf);

if (!foundFunction || !foundBody) {
    console.error("FAIL: createEmbeddedWebUIBundle function not found");
    process.exit(1);
}

// Check for functional array methods in the function body
let hasMapMethod = false;
let hasJoinMethod = false;
let hasForLoop = false;

function checkBody(node) {
    // Check for .map() method calls
    if (ts.isPropertyAccessExpression(node) && node.name.text === 'map') {
        hasMapMethod = true;
    }
    // Check for .join() method calls
    if (ts.isPropertyAccessExpression(node) && node.name.text === 'join') {
        hasJoinMethod = true;
    }
    // Check for for loops (for statement, for-of, for-in)
    if (ts.isForStatement(node) || ts.isForOfStatement(node) || ts.isForInStatement(node)) {
        hasForLoop = true;
    }
    // Check for while loops
    if (ts.isWhileStatement(node) || ts.isDoStatement(node)) {
        hasForLoop = true;
    }
    ts.forEachChild(node, checkBody);
}
checkBody(foundBody);

if (!hasMapMethod) {
    console.error("FAIL: .map() method not found in bundling function");
    process.exit(1);
}

if (!hasJoinMethod) {
    console.error("FAIL: .join() method not found in bundling function");
    process.exit(1);
}

if (hasForLoop) {
    console.error("FAIL: for/while loop found in bundling function (should use functional methods)");
    process.exit(1);
}

console.log("PASS: Bundling function uses functional array methods (.map/.join)");
'''
    r = _bun_run_script(code)
    assert r.returncode == 0, f"Functional array methods not found:\n{r.stderr.decode()}\n{r.stdout.decode()}"
    assert "PASS" in r.stdout.decode(), f"Unexpected output: {r.stdout.decode()}"
