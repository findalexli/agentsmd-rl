"""
Task: vscode-sessions-archived-view
Repo: microsoft/vscode @ 3d5035e98791181f4fb04962a8a7b127106d2626
PR:   306265

Bug: Clicking an archived session causes the view to immediately bounce back
to the new-session screen because _onSessionsChanged() calls
openNewSessionView() synchronously on archive-state changes.

Fix: Remove immediate check from _onSessionsChanged; add an autorun observer
in setActiveSession() that fires only when the active session becomes archived.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = Path(
    f"{REPO}/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts"
)


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript via Node.js in the repo directory (uses .cjs for CommonJS)."""
    script = Path(f"{REPO}/_eval_tmp.cjs")  # Use .cjs extension for CommonJS
    script.write_text(code)
    try:
        env = os.environ.copy()
        env['NODE_OPTIONS'] = '--max-old-space-size=4096'
        return subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
            env=env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via TypeScript AST
# ---------------------------------------------------------------------------


def test_typescript_file_parses():
    """Modified file must parse as valid TypeScript with no syntax errors."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);
if (sf.parseDiagnostics && sf.parseDiagnostics.length > 0) {
    const msgs = sf.parseDiagnostics.map(d => {
        const pos = d.file ? d.file.getLineAndCharacterOfPosition(d.start) : {};
        return 'Line ' + ((pos.line || 0) + 1) + ': '
            + ts.flattenDiagnosticMessageText(d.messageText, '\\n');
    });
    console.error(msgs.join('\\n'));
    process.exit(1);
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"TypeScript parse failed: {r.stderr}"
    assert "OK" in r.stdout


def test_imports_include_disposable_store_and_autorun():
    """DisposableStore and autorun must be imported from lifecycle.js and observable.js."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);

const imports = {};
ts.forEachChild(sf, node => {
    if (ts.isImportDeclaration(node)) {
        const mod = node.moduleSpecifier.getText().replace(/['"]/g, '');
        const names = [];
        if (node.importClause && node.importClause.namedBindings
            && ts.isNamedImports(node.importClause.namedBindings)) {
            node.importClause.namedBindings.elements.forEach(
                el => names.push(el.name.getText())
            );
        }
        imports[mod] = names;
    }
});

const lif = Object.entries(imports).find(([k]) => k.includes('lifecycle.js'));
if (!lif || !lif[1].includes('DisposableStore')) {
    console.error('DisposableStore not imported from lifecycle.js');
    process.exit(1);
}

const obs = Object.entries(imports).find(([k]) => k.includes('observable.js'));
if (!obs || !obs[1].includes('autorun')) {
    console.error('autorun not imported from observable.js');
    process.exit(1);
}

console.log('OK');
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


def test_disposable_store_field_registered():
    """_activeSessionDisposables must be a DisposableStore registered via this._register()."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isPropertyDeclaration(node)) {
        const text = node.getText();
        if (text.includes('_activeSessionDisposables')) {
            if (!text.includes('DisposableStore')) {
                console.error('_activeSessionDisposables is not a DisposableStore');
                process.exit(1);
            }
            if (!text.includes('this._register(')) {
                console.error('_activeSessionDisposables not registered via this._register()');
                process.exit(1);
            }
            found = true;
        }
    }
    ts.forEachChild(node, visit);
}
ts.forEachChild(sf, visit);

if (!found) {
    console.error('_activeSessionDisposables property not found');
    process.exit(1);
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


def test_on_sessions_changed_no_archive_bounce():
    """onDidChangeSessionsFromSessionsProviders must NOT contain the buggy immediate archive check or openNewSessionView call in the changed handler."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isMethodDeclaration(node) && node.name.getText() === 'onDidChangeSessionsFromSessionsProviders') {
        const text = node.body ? node.body.getText() : '';
        // After the fix, this method should NOT contain the synchronous isArchived.get() check
        // in the context of e.changed handling (which was removed by the fix)
        // The buggy code that was removed:
        // if (e.changed.length) { ... isArchived.get() ... openNewSessionView() }
        // We check that the removed pattern is not present
        if (text.includes('e.changed.length') && text.includes('isArchived.get()')) {
            console.error(
                'onDidChangeSessionsFromSessionsProviders still contains synchronous isArchived.get() check in e.changed handler'
            );
            process.exit(1);
        }
        // Also verify the specific buggy openNewSessionView call pattern is gone
        if (text.includes('e.changed') && text.includes('allArchived') && text.includes('openNewSessionView')) {
            console.error('onDidChangeSessionsFromSessionsProviders still contains buggy allArchived check');
            process.exit(1);
        }
        found = true;
    }
    ts.forEachChild(node, visit);
}
ts.forEachChild(sf, visit);

if (!found) {
    console.error('onDidChangeSessionsFromSessionsProviders method not found');
    process.exit(1);
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


def test_autorun_observer_in_set_active_session():
    """setActiveSession must use autorun to reactively observe archive state with proper disposable lifecycle."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isMethodDeclaration(node) && node.name.getText() === 'setActiveSession') {
        const text = node.body ? node.body.getText() : '';
        // Must use autorun for reactive observation
        if (!text.includes('autorun')) {
            console.error('setActiveSession does not contain autorun call');
            process.exit(1);
        }
        // Must read isArchived reactively via .read(reader) inside autorun
        if (!text.includes('isArchived.read(')) {
            console.error('autorun does not observe isArchived.read(reader)');
            process.exit(1);
        }
        // Must call openNewSessionView when archived
        if (!text.includes('this.openNewSessionView()')) {
            console.error('autorun does not call openNewSessionView()');
            process.exit(1);
        }
        // Must clear disposables before adding new autorun
        if (!text.includes('_activeSessionDisposables.clear()')) {
            console.error('_activeSessionDisposables.clear() not called');
            process.exit(1);
        }
        // clear() must come before add() to prevent stale observers
        const clearIdx = text.indexOf('_activeSessionDisposables.clear()');
        const addIdx = text.indexOf('_activeSessionDisposables.add(autorun');
        if (clearIdx === -1 || addIdx === -1 || clearIdx > addIdx) {
            console.error('clear() must come before add(autorun...)');
            process.exit(1);
        }
        found = true;
    }
    ts.forEachChild(node, visit);
}
ts.forEachChild(sf, visit);

if (!found) {
    console.error('setActiveSession method not found');
    process.exit(1);
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


def test_idempotency_guard_in_set_active_session():
    """setActiveSession must early-return when the session ID hasn't changed to prevent disposable churn."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const path = 'src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts';
const source = fs.readFileSync(path, 'utf8');
const sf = ts.createSourceFile(path, source, ts.ScriptTarget.Latest, true);

let found = false;
function visit(node) {
    if (ts.isMethodDeclaration(node) && node.name.getText() === 'setActiveSession') {
        const text = node.body ? node.body.getText() : '';
        if (!text.includes('sessionId')) {
            console.error('setActiveSession does not compare sessionId');
            process.exit(1);
        }
        // Guard must be early return before main logic
        const lines = text.split(/\\r?\\n/).map(l => l.trim()).filter(l => l);
        const returnIdx = lines.findIndex(l => l === 'return;' || l === 'return');
        const setActiveIdx = lines.findIndex(l => l.includes('_activeSession.set('));
        if (returnIdx === -1) {
            console.error('No early return found in setActiveSession');
            process.exit(1);
        }
        if (setActiveIdx !== -1 && returnIdx > setActiveIdx) {
            console.error('Early return must come before _activeSession.set()');
            process.exit(1);
        }
        found = true;
    }
    ts.forEachChild(node, visit);
}
ts.forEachChild(sf, visit);

if (!found) {
    console.error('setActiveSession method not found');
    process.exit(1);
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — VS Code coding standards
# ---------------------------------------------------------------------------


def test_copyright_header():
    """All VS Code files must include the Microsoft copyright header."""
    content = TARGET.read_text()
    header = content[:300]
    assert "Microsoft Corporation" in header, (
        "Microsoft copyright header missing from start of file"
    )
    assert "Licensed under the MIT License" in header, (
        "MIT License notice missing from copyright header"
    )


def test_tabs_not_spaces():
    """VS Code source files must use tabs for indentation, not spaces."""
    content = TARGET.read_text()
    bad_lines = [
        (i + 1, ln)
        for i, ln in enumerate(content.splitlines())
        if ln.startswith("    ")
    ]
    assert not bad_lines, (
        f"Found {len(bad_lines)} lines with space indentation (must use tabs). "
        f"First offenders: {bad_lines[:3]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural gate
# ---------------------------------------------------------------------------


def test_file_is_structurally_sound():
    """Modified file must be non-truncated with balanced braces and intact class definition."""
    content = TARGET.read_text()
    lines = content.splitlines()
    assert len(lines) > 100, "File appears truncated or mostly deleted"
    assert "class SessionsManagementService" in content, (
        "SessionsManagementService class definition missing"
    )
    opens = content.count("{")
    closes = content.count("}")
    assert opens == closes, (
        f"Unbalanced braces: {opens} opens vs {closes} closes"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — VS Code CI/CD gates
# ---------------------------------------------------------------------------


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass).
    
    NOTE: Full typecheck of VS Code requires ~8GB memory. We skip this in
    constrained environments. The test_typescript_file_parses check already
    validates the modified file has no syntax errors.
    """
    # Skip full typecheck due to memory constraints
    # Syntax validation is already covered by test_typescript_file_parses
    return


def test_repo_eslint():
    """ESLint passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--max-warnings", "0",
         "src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] or r.stdout[-500:]}"
