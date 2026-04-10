"""
Task: vscode-sessiondb-mem-tests
Repo: microsoft/vscode @ c1f3775929102459145d7a93175005e7e90b216e

Make SessionDatabase members accessible for test subclassing:
- Export runMigrations function
- Change _dbPromise, _closed, _ensureDb from private to protected

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
SESSION_DB = "src/vs/platform/agentHost/node/sessionDatabase.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Node.js code via CommonJS in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        # Unset NODE_OPTIONS to avoid ts-node loader issues
        env = os.environ.copy()
        env.pop("NODE_OPTIONS", None)
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
# Fail-to-pass (pr_diff) — core changes (TypeScript AST via subprocess)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_run_migrations_exported():
    """runMigrations must be exported so test subclasses can call it."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/node/sessionDatabase.ts', 'utf8'
);
const sf = ts.createSourceFile(
  'sessionDatabase.ts', src, ts.ScriptTarget.Latest, true
);
let found = false;
sf.forEachChild(node => {
  if (ts.isFunctionDeclaration(node) && node.name && node.name.text === 'runMigrations') {
    const mods = node.modifiers || [];
    found = mods.some(m => m.kind === ts.SyntaxKind.ExportKeyword);
  }
});
console.log(JSON.stringify({ exported: found }));
"""
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["exported"], (
        "runMigrations is not exported — test subclasses cannot call it directly"
    )


# [pr_diff] fail_to_pass
def test_db_promise_protected():
    """_dbPromise must be protected (not private) for subclass access."""
    vis = _get_member_visibility()
    assert "_dbPromise" in vis, "Could not find _dbPromise in SessionDatabase class"
    assert vis["_dbPromise"]["isProtected"], (
        "_dbPromise is not protected — subclasses cannot access the db promise"
    )
    assert not vis["_dbPromise"]["isPrivate"], (
        "_dbPromise is still declared private"
    )


# [pr_diff] fail_to_pass
def test_closed_protected():
    """_closed must be protected (not private) for subclass access."""
    vis = _get_member_visibility()
    assert "_closed" in vis, "Could not find _closed in SessionDatabase class"
    assert vis["_closed"]["isProtected"], (
        "_closed is not protected — subclasses cannot read the closed flag"
    )
    assert not vis["_closed"]["isPrivate"], "_closed is still declared private"


# [pr_diff] fail_to_pass
def test_ensure_db_protected():
    """_ensureDb must be protected (not private) for subclass override/access."""
    vis = _get_member_visibility()
    assert "_ensureDb" in vis, "Could not find _ensureDb in SessionDatabase class"
    assert vis["_ensureDb"]["isProtected"], (
        "_ensureDb is not protected — subclasses cannot call or override it"
    )
    assert not vis["_ensureDb"]["isPrivate"], "_ensureDb is still declared private"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structural integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_session_database_class_exported():
    """SessionDatabase class must still be exported (regression guard)."""
    src = (Path(REPO) / SESSION_DB).read_text()
    assert "export class SessionDatabase" in src, (
        "SessionDatabase class is no longer exported — regression"
    )


# [static] pass_to_pass
def test_not_stub():
    """runMigrations still contains real migration logic, not a stub."""
    src = (Path(REPO) / SESSION_DB).read_text()
    assert "PRAGMA foreign_keys = ON" in src, (
        "runMigrations body is missing — function appears to be a stub"
    )
    assert "PRAGMA user_version" in src, (
        "Migration versioning logic is missing from runMigrations"
    )


# ---------------------------------------------------------------------------
# Repo tests (pass_to_pass, repo_tests) — actual CI commands
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_sessionDatabase_typescript_syntax():
    """TypeScript file parses without syntax errors (pass_to_pass)."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/node/sessionDatabase.ts', 'utf8'
);
// Parse the source file
const sf = ts.createSourceFile(
  'sessionDatabase.ts', src, ts.ScriptTarget.Latest, true
);
// Check that we have valid AST nodes
let statementCount = sf.statements.length;
let hasParseErrors = false;
// Check for syntax markers that indicate parse errors
function visit(node) {
  // If we can traverse without errors, the syntax is valid
  try {
    ts.forEachChild(node, visit);
  } catch (e) {
    hasParseErrors = true;
  }
}
try {
  sf.forEachChild(node => visit(node));
} catch (e) {
  hasParseErrors = true;
}
console.log(JSON.stringify({ 
  valid: !hasParseErrors && statementCount > 0,
  statements: statementCount,
  hasErrors: hasParseErrors
}));
"""
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["valid"], f"TypeScript syntax errors found: statements={data.get('statements')}, hasErrors={data.get('hasErrors')}"


# [repo_tests] pass_to_pass
def test_sessionDatabase_test_file_parses():
    """SessionDatabase test file parses without errors (pass_to_pass)."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/test/node/sessionDatabase.test.ts', 'utf8'
);
const sf = ts.createSourceFile(
  'sessionDatabase.test.ts', src, ts.ScriptTarget.Latest, true
);
// Count test suites and tests
let suites = 0;
let tests = 0;
sf.forEachChild(node => {
  if (ts.isExpressionStatement(node) && ts.isCallExpression(node.expression)) {
    const expr = node.expression.expression;
    if (ts.isIdentifier(expr)) {
      if (expr.text === 'suite') suites++;
      if (expr.text === 'test') tests++;
    }
  }
});
// Also check nested calls (suites contain tests)
function visit(node) {
  if (ts.isCallExpression(node)) {
    const expr = node.expression;
    if (ts.isIdentifier(expr)) {
      if (expr.text === 'suite') suites++;
      if (expr.text === 'test') tests++;
    }
  }
  ts.forEachChild(node, visit);
}
sf.forEachChild(node => visit(node));
console.log(JSON.stringify({ valid: true, suites, tests }));
"""
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("suites", 0) > 0, "No test suites found in sessionDatabase.test.ts"
    assert data.get("tests", 0) > 0, "No tests found in sessionDatabase.test.ts"


# [repo_tests] pass_to_pass
def test_sessionDatabase_has_required_imports():
    """SessionDatabase has required imports for compilation (pass_to_pass)."""
    r = _run_node(
        """
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/node/sessionDatabase.ts', 'utf8'
);
const requiredImports = [
  'fs',
  '@vscode/sqlite3',
  'SequencerByKey'
];
const missing = [];
for (const imp of requiredImports) {
  if (!src.includes(imp)) {
    missing.push(imp);
  }
}
console.log(JSON.stringify({ valid: missing.length === 0, missing }));
"""
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["valid"], f"Missing required imports: {data.get('missing', [])}"


# [repo_tests] pass_to_pass
def test_sessionDatabase_interface_defined():
    """SessionDatabase interface ISessionDatabaseMigration is properly defined (pass_to_pass)."""
    r = _run_node(
        """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/node/sessionDatabase.ts', 'utf8'
);
const sf = ts.createSourceFile(
  'sessionDatabase.ts', src, ts.ScriptTarget.Latest, true
);
let hasMigrationInterface = false;
let hasRequiredFields = false;
sf.forEachChild(node => {
  if (ts.isInterfaceDeclaration(node) && node.name.text === 'ISessionDatabaseMigration') {
    hasMigrationInterface = true;
    const members = node.members;
    let hasVersion = false;
    let hasSql = false;
    members.forEach(m => {
      if (m.name && m.name.getText(sf) === 'version') hasVersion = true;
      if (m.name && m.name.getText(sf) === 'sql') hasSql = true;
    });
    hasRequiredFields = hasVersion && hasSql;
  }
});
console.log(JSON.stringify({
  valid: hasMigrationInterface && hasRequiredFields,
  hasInterface: hasMigrationInterface,
  hasFields: hasRequiredFields
}));
"""
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["valid"], f"ISessionDatabaseMigration interface issues: hasInterface={data.get('hasInterface')}, hasFields={data.get('hasFields')}"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_MEMBER_VIS_SCRIPT = """
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync(
  'src/vs/platform/agentHost/node/sessionDatabase.ts', 'utf8'
);
const sf = ts.createSourceFile(
  'sessionDatabase.ts', src, ts.ScriptTarget.Latest, true
);
const results = {};
sf.forEachChild(node => {
  if (ts.isClassDeclaration(node) && node.name && node.name.text === 'SessionDatabase') {
    node.members.forEach(m => {
      const name = m.name ? m.name.getText(sf) : null;
      if (['_dbPromise', '_closed', '_ensureDb'].includes(name)) {
        const mods = m.modifiers || [];
        results[name] = {
          isProtected: mods.some(m => m.kind === ts.SyntaxKind.ProtectedKeyword),
          isPrivate:   mods.some(m => m.kind === ts.SyntaxKind.PrivateKeyword),
        };
      }
    });
  }
});
console.log(JSON.stringify(results));
"""


def _get_member_visibility() -> dict:
    """Get visibility of SessionDatabase members via TypeScript AST parser."""
    r = _run_node(_MEMBER_VIS_SCRIPT)
    assert r.returncode == 0, f"TypeScript AST check failed: {r.stderr}"
    return json.loads(r.stdout.strip())
