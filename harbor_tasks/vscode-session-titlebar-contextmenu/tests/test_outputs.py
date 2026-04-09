"""
Task: vscode-session-titlebar-contextmenu
Repo: microsoft/vscode @ 6a7e1b4bd33c970a4c5275ab90dbfd6a3cb91aa0
PR:   306419

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Tests use the TypeScript compiler API via Node.js subprocess to verify
AST-level code structure rather than grep-based string matching.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TITLEBAR = "src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts"
PROVIDER = "src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsProvider.ts"


def _run_node(code: str, file_rel: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js, passing file_rel as argv[2]."""
    script = Path(f"{REPO}/_eval_tmp.cjs")
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script), file_rel],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_files_exist():
    """Both modified TypeScript files are present in the workspace."""
    assert (Path(REPO) / TITLEBAR).exists(), f"Missing: {TITLEBAR}"
    assert (Path(REPO) / PROVIDER).exists(), f"Missing: {PROVIDER}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — verified via TS compiler API
# ---------------------------------------------------------------------------

def test_new_session_guard():
    """Context menu suppressed for new/unsaved sessions via IsNewChatSessionContext early-return guard."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

// 1. IsNewChatSessionContext must be imported from sessionsManagementService
let imported = false;
ts.forEachChild(sf, n => {
    if (ts.isImportDeclaration(n)) {
        const mod = n.moduleSpecifier.getText(sf);
        if (mod.includes('sessionsManagementService')) {
            const clause = n.importClause;
            if (clause && clause.namedBindings) {
                ts.forEachChild(clause.namedBindings, c => {
                    if (ts.isImportSpecifier(c) && c.name.text === 'IsNewChatSessionContext') imported = true;
                });
            }
        }
    }
});
if (!imported) { process.stderr.write('IsNewChatSessionContext not imported\\n'); process.exit(1); }

// 2. An if-statement referencing IsNewChatSessionContext must contain a return
let foundGuard = false;
function walk(n) {
    if (ts.isIfStatement(n)) {
        const cond = n.expression.getText(sf);
        if (cond.includes('IsNewChatSessionContext')) {
            const then = n.thenStatement;
            const stmts = ts.isBlock(then) ? Array.from(then.statements) : [then];
            if (stmts.some(s => ts.isReturnStatement(s))) foundGuard = true;
        }
    }
    ts.forEachChild(n, walk);
}
ts.forEachChild(sf, walk);
if (!foundGuard) { process.stderr.write('No IsNewChatSessionContext guard with return\\n'); process.exit(1); }
console.log('PASS');
""",
        TITLEBAR,
    )
    assert r.returncode == 0, f"New session guard check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pinned_state_not_hardcoded():
    """IsSessionPinnedContext.key is no longer hardcoded to false."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

// Walk AST looking for [IsSessionPinnedContext.key, false] pattern
let found = false;
function walk(n) {
    if (ts.isArrayLiteralExpression(n)) {
        for (const elem of n.elements) {
            if (ts.isArrayLiteralExpression(elem)) {
                const parts = Array.from(elem.elements);
                if (parts.length >= 2) {
                    const key = parts[0].getText(sf);
                    const val = parts[1];
                    if (key.includes('IsSessionPinnedContext.key') && val.kind === ts.SyntaxKind.FalseKeyword) {
                        found = true;
                    }
                }
            }
        }
    }
    ts.forEachChild(n, walk);
}
ts.forEachChild(sf, walk);
if (found) { process.stderr.write('IsSessionPinnedContext.key still hardcoded to false\\n'); process.exit(1); }
console.log('PASS');
""",
        TITLEBAR,
    )
    assert r.returncode == 0, f"Pinned state hardcoded check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_pinned_state_dynamic():
    """Pinned state resolved dynamically via IViewsService + isSessionPinned()."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

// 1. IViewsService must be imported from viewsService module
let viewsImported = false;
ts.forEachChild(sf, n => {
    if (ts.isImportDeclaration(n)) {
        const mod = n.moduleSpecifier.getText(sf);
        if (mod.includes('viewsService')) {
            const clause = n.importClause;
            if (clause && clause.namedBindings) {
                ts.forEachChild(clause.namedBindings, c => {
                    if (ts.isImportSpecifier(c) && c.name.text === 'IViewsService') viewsImported = true;
                });
            }
        }
    }
});
if (!viewsImported) { process.stderr.write('IViewsService not imported\\n'); process.exit(1); }

// 2. isSessionPinned() must be called somewhere
if (!src.includes('isSessionPinned(')) { process.stderr.write('isSessionPinned() not called\\n'); process.exit(1); }

// 3. IViewsService must be a constructor parameter (dependency injection)
let foundInjection = false;
function walk(n) {
    if (ts.isConstructorDeclaration(n)) {
        for (const p of n.parameters) {
            if (p.type && p.type.getText(sf).includes('IViewsService')) foundInjection = true;
        }
    }
    ts.forEachChild(n, walk);
}
ts.forEachChild(sf, walk);
if (!foundInjection) { process.stderr.write('IViewsService not injected as constructor param\\n'); process.exit(1); }
console.log('PASS');
""",
        TITLEBAR,
    )
    assert r.returncode == 0, f"Dynamic pinned state check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_session_type_icon_method_exists():
    """Private _getSessionTypeIcon method with switch on providerType covering Background and Cloud."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let foundMethod = false, hasSwitch = false, hasBackground = false, hasCloud = false;
function walk(n) {
    if (ts.isMethodDeclaration(n) && n.name.getText(sf) === '_getSessionTypeIcon') {
        foundMethod = true;
        function walkMethod(m) {
            if (ts.isSwitchStatement(m) && m.expression.getText(sf).includes('providerType')) {
                hasSwitch = true;
                for (const cl of m.caseBlock.clauses) {
                    const t = cl.getText(sf);
                    if (t.includes('Background')) hasBackground = true;
                    if (t.includes('Cloud')) hasCloud = true;
                }
            }
            ts.forEachChild(m, walkMethod);
        }
        if (n.body) ts.forEachChild(n.body, walkMethod);
    }
    ts.forEachChild(n, walk);
}
ts.forEachChild(sf, walk);
if (!foundMethod) { process.stderr.write('_getSessionTypeIcon method not found\\n'); process.exit(1); }
if (!hasSwitch) { process.stderr.write('No switch(providerType) in method\\n'); process.exit(1); }
if (!hasBackground) { process.stderr.write('Background case missing\\n'); process.exit(1); }
if (!hasCloud) { process.stderr.write('Cloud case missing\\n'); process.exit(1); }
console.log('PASS');
""",
        PROVIDER,
    )
    assert r.returncode == 0, f"Session type icon method check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_session_icon_uses_method():
    """this.icon assigned via this._getSessionTypeIcon() instead of direct session.icon."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(process.argv[2], 'utf8');
const sf = ts.createSourceFile('f.ts', src, ts.ScriptTarget.Latest, true);

let directAssign = false, methodAssign = false;
function walk(n) {
    if (ts.isBinaryExpression(n) && n.operatorToken.kind === ts.SyntaxKind.EqualsToken) {
        const left = n.left.getText(sf);
        if (left === 'this.icon') {
            const right = n.right.getText(sf);
            if (right === 'session.icon') directAssign = true;
            if (right.includes('_getSessionTypeIcon')) methodAssign = true;
        }
    }
    ts.forEachChild(n, walk);
}
ts.forEachChild(sf, walk);
if (directAssign) { process.stderr.write('this.icon = session.icon still present\\n'); process.exit(1); }
if (!methodAssign) { process.stderr.write('this._getSessionTypeIcon() not used for icon assignment\\n'); process.exit(1); }
console.log('PASS');
""",
        PROVIDER,
    )
    assert r.returncode == 0, f"Session icon method usage check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - No additional repo-wide checks
# VS Code is a large monorepo with complex build requirements.
# The core fix tests above are sufficient.
# ---------------------------------------------------------------------------
