"""
Task: vscode-sessiondb-mem-tests
Repo: microsoft/vscode @ c1f3775929102459145d7a93175005e7e90b216e

Make SessionDatabase members accessible for test subclassing:
- Export runMigrations function
- Change _dbPromise, _closed, _ensureDb from private to protected

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only (all checks): TypeScript private/protected is a compile-time
# distinction only — at JS runtime there is no access enforcement, so
# calling the code cannot detect whether a member is private or protected.
# Similarly, `export` on a function only affects module resolution at build
# time, not runtime behaviour of the function itself.

import re
from pathlib import Path

REPO = "/workspace/vscode"
SESSION_DB = Path(REPO) / "src/vs/platform/agentHost/node/sessionDatabase.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_session_database_class_exported():
    """SessionDatabase class must still be exported (regression guard)."""
    src = SESSION_DB.read_text()
    assert "export class SessionDatabase" in src, \
        "SessionDatabase class is no longer exported — regression"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_run_migrations_exported():
    """runMigrations must be exported so test subclasses can call it."""
    src = SESSION_DB.read_text()
    assert "export async function runMigrations" in src, \
        "runMigrations is not exported — test subclasses cannot call it directly"


# [pr_diff] fail_to_pass
def test_db_promise_protected():
    """_dbPromise must be protected (not private) for subclass access."""
    src = SESSION_DB.read_text()
    assert "protected _dbPromise:" in src, \
        "_dbPromise is not protected — subclasses cannot access the db promise"
    assert "private _dbPromise:" not in src, \
        "_dbPromise is still declared private"


# [pr_diff] fail_to_pass
def test_closed_protected():
    """_closed must be protected (not private) for subclass access."""
    src = SESSION_DB.read_text()
    assert "protected _closed:" in src, \
        "_closed is not protected — subclasses cannot read the closed flag"
    assert "private _closed:" not in src, \
        "_closed is still declared private"


# [pr_diff] fail_to_pass
def test_ensure_db_protected():
    """_ensureDb must be protected (not private) for subclass override/access."""
    src = SESSION_DB.read_text()
    assert re.search(r"protected _ensureDb\(\)", src), \
        "_ensureDb is not protected — subclasses cannot call or override it"
    assert not re.search(r"private _ensureDb\(\)", src), \
        "_ensureDb is still declared private"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """runMigrations still contains real migration logic, not a stub."""
    src = SESSION_DB.read_text()
    assert "PRAGMA foreign_keys = ON" in src, \
        "runMigrations body is missing — function appears to be a stub"
    assert "PRAGMA user_version" in src, \
        "Migration versioning logic is missing from runMigrations"
