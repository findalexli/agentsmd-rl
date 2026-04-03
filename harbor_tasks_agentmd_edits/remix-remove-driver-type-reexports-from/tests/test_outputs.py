"""
Task: remix-remove-driver-type-reexports-from
Repo: remix-run/remix @ 1c0176eae3dd77d18e293c53d54237357ffc8efd
PR:   11160

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"

MYSQL_INDEX = f"{REPO}/packages/data-table-mysql/src/index.ts"
MYSQL_ADAPTER = f"{REPO}/packages/data-table-mysql/src/lib/adapter.ts"
MYSQL_README = f"{REPO}/packages/data-table-mysql/README.md"

PG_INDEX = f"{REPO}/packages/data-table-postgres/src/index.ts"
PG_ADAPTER = f"{REPO}/packages/data-table-postgres/src/lib/adapter.ts"
PG_README = f"{REPO}/packages/data-table-postgres/README.md"

SQLITE_INDEX = f"{REPO}/packages/data-table-sqlite/src/index.ts"
SQLITE_ADAPTER = f"{REPO}/packages/data-table-sqlite/src/lib/adapter.ts"
SQLITE_README = f"{REPO}/packages/data-table-sqlite/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified TypeScript files must be valid (no obvious syntax errors)."""
    for path in [MYSQL_INDEX, MYSQL_ADAPTER, PG_INDEX, PG_ADAPTER, SQLITE_INDEX, SQLITE_ADAPTER]:
        src = Path(path).read_text()
        # Basic check: file is non-empty and has balanced braces
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — driver type re-exports removed from index.ts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mysql_driver_types_not_reexported():
    """MySQL index.ts must NOT re-export driver-shaped types like MysqlDatabasePool."""
    src = Path(MYSQL_INDEX).read_text()
    removed_types = [
        "MysqlDatabaseConnection",
        "MysqlDatabasePool",
        "MysqlQueryResponse",
        "MysqlQueryResultHeader",
        "MysqlQueryRows",
    ]
    for typ in removed_types:
        assert typ not in src, (
            f"index.ts still exports '{typ}' — driver types should not be re-exported"
        )
    # MysqlDatabaseAdapterOptions should still be exported
    assert "MysqlDatabaseAdapterOptions" in src, (
        "MysqlDatabaseAdapterOptions must remain exported"
    )


# [pr_diff] fail_to_pass
def test_postgres_driver_types_not_reexported():
    """Postgres index.ts must NOT re-export driver-shaped types like PostgresDatabasePool."""
    src = Path(PG_INDEX).read_text()
    removed_types = [
        "PostgresDatabaseClient",
        "PostgresDatabasePool",
        "PostgresQueryResult",
        "PostgresTransactionClient",
    ]
    for typ in removed_types:
        assert typ not in src, (
            f"index.ts still exports '{typ}' — driver types should not be re-exported"
        )
    # PostgresDatabaseAdapterOptions should still be exported
    assert "PostgresDatabaseAdapterOptions" in src, (
        "PostgresDatabaseAdapterOptions must remain exported"
    )


# [pr_diff] fail_to_pass
def test_sqlite_driver_type_not_reexported():
    """SQLite index.ts must NOT re-export SqliteDatabaseConnection."""
    src = Path(SQLITE_INDEX).read_text()
    assert "SqliteDatabaseConnection" not in src, (
        "index.ts still exports 'SqliteDatabaseConnection' — driver types should not be re-exported"
    )
    # SqliteDatabaseAdapterOptions should still be exported
    assert "SqliteDatabaseAdapterOptions" in src, (
        "SqliteDatabaseAdapterOptions must remain exported"
    )


# [pr_diff] fail_to_pass
def test_mysql_adapter_uses_driver_types():
    """MySQL adapter must import types from mysql2/promise instead of defining its own."""
    src = Path(MYSQL_ADAPTER).read_text()
    # Must import from the driver package
    assert "from 'mysql2/promise'" in src or 'from "mysql2/promise"' in src, (
        "Adapter should import types from mysql2/promise"
    )
    # The old custom type definitions should be gone
    assert "export type MysqlDatabasePool" not in src, (
        "Old MysqlDatabasePool type definition should be removed"
    )
    assert "export type MysqlDatabaseConnection" not in src, (
        "Old MysqlDatabaseConnection type definition should be removed"
    )


# [pr_diff] fail_to_pass
def test_postgres_adapter_uses_driver_types():
    """Postgres adapter must import types from pg instead of defining its own."""
    src = Path(PG_ADAPTER).read_text()
    # Must import from the driver package
    assert "from 'pg'" in src or 'from "pg"' in src, (
        "Adapter should import types from pg"
    )
    # The old custom type definitions should be gone
    assert "export type PostgresDatabasePool" not in src, (
        "Old PostgresDatabasePool type definition should be removed"
    )
    assert "export type PostgresDatabaseClient" not in src, (
        "Old PostgresDatabaseClient type definition should be removed"
    )


# [pr_diff] fail_to_pass
def test_mysql_adapter_has_pool_connection_guard():
    """MySQL adapter must have a type guard for pool connections (isMysqlPoolConnection)."""
    src = Path(MYSQL_ADAPTER).read_text()
    # There should be a function that distinguishes pool connections
    # (needed because release() should only be called on pool connections)
    assert re.search(r"function\s+isMysqlPoolConnection", src), (
        "Adapter should have an isMysqlPoolConnection type guard function"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — adapter classes still exported
# ---------------------------------------------------------------------------

# [static] pass_to_pass

    pg_src = Path(PG_INDEX).read_text()
    assert "createPostgresDatabaseAdapter" in pg_src, "createPostgresDatabaseAdapter must be exported"
    assert "PostgresDatabaseAdapter" in pg_src, "PostgresDatabaseAdapter must be exported"

    sqlite_src = Path(SQLITE_INDEX).read_text()
    assert "createSqliteDatabaseAdapter" in sqlite_src, "createSqliteDatabaseAdapter must be exported"
    assert "SqliteDatabaseAdapter" in sqlite_src, "SqliteDatabaseAdapter must be exported"


# ---------------------------------------------------------------------------
# Agent config (agent_config) — cross-package boundary rule from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:12 @ 1c0176eae3dd77d18e293c53d54237357ffc8efd
