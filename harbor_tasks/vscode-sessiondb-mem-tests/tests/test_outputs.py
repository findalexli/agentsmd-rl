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
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
SESSION_DB = "src/vs/platform/agentHost/node/sessionDatabase.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Node.js code via CommonJS in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
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
