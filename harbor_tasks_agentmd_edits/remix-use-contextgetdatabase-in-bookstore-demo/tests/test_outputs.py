"""
Task: remix-use-contextgetdatabase-in-bookstore-demo
Repo: remix-run/remix @ b29fc874293468babb25b90e95edc208f1d652be
PR:   11186

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/remix"
BOOKSTORE = Path(REPO) / "demos" / "bookstore"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files exist and are non-empty."""
    files = [
        BOOKSTORE / "app" / "middleware" / "database.ts",
        BOOKSTORE / "app" / "middleware" / "auth.ts",
        BOOKSTORE / "app" / "utils" / "context.ts",
        BOOKSTORE / "app" / "books.tsx",
        BOOKSTORE / "app" / "cart.tsx",
    ]
    for f in files:
        assert f.exists(), f"{f.name} does not exist"
        content = f.read_text()
        assert len(content) > 50, f"{f.name} is too short to be valid"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_database_middleware_uses_context_set():
    """database.ts must use context.set(Database, db) instead of context.db = db."""
    content = (BOOKSTORE / "app" / "middleware" / "database.ts").read_text()
    # Must use the typed context key pattern
    assert re.search(r'context\.set\s*\(\s*Database', content), \
        "database.ts should use context.set(Database, ...) to store the database"
    # Must not use the old direct property assignment
    assert "context.db" not in content, \
        "database.ts should not use context.db property assignment"


# [pr_diff] fail_to_pass
def test_database_imported_in_middleware():
    """database.ts must import Database from remix/data-table."""
    content = (BOOKSTORE / "app" / "middleware" / "database.ts").read_text()
    assert "Database" in content, "database.ts should reference the Database class"
    assert "remix/data-table" in content, \
        "database.ts should import from remix/data-table"


# [pr_diff] fail_to_pass
def test_handlers_use_get_database():
    """Route handlers must use get(Database) to retrieve the database."""
    handler_files = [
        BOOKSTORE / "app" / "account.tsx",
        BOOKSTORE / "app" / "admin.books.tsx",
        BOOKSTORE / "app" / "admin.orders.tsx",
        BOOKSTORE / "app" / "admin.users.tsx",
        BOOKSTORE / "app" / "books.tsx",
        BOOKSTORE / "app" / "auth.tsx",
        BOOKSTORE / "app" / "cart.tsx",
        BOOKSTORE / "app" / "checkout.tsx",
    ]
    files_with_get_database = 0
    for f in handler_files:
        if not f.exists():
            continue
        content = f.read_text()
        if "get(Database)" in content:
            files_with_get_database += 1
    assert files_with_get_database >= 5, \
        f"At least 5 handler files should use get(Database), found {files_with_get_database}"


# [pr_diff] fail_to_pass
def test_type_augmentation_removed():
    """The context.db.ts type augmentation file must be removed."""
    augmentation = BOOKSTORE / "app" / "types" / "context.db.ts"
    assert not augmentation.exists(), \
        "app/types/context.db.ts should be deleted (RequestContext augmentation no longer needed)"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_middleware_has_real_logic():
    """database.ts middleware must have real logic, not just a stub."""
    content = (BOOKSTORE / "app" / "middleware" / "database.ts").read_text()
    # Must export the loadDatabase function
    assert "loadDatabase" in content, "database.ts must export loadDatabase"
    # Must call next() to continue the middleware chain
    assert "next()" in content, "database.ts middleware must call next()"
    # Must have a return statement or implicit return
    assert "return" in content, "database.ts middleware must return the next() result"
