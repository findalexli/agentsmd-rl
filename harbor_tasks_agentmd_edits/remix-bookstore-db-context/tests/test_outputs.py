"""
Task: remix-bookstore-db-context
Repo: remix-run/remix @ b29fc874293468babb25b90e95edc208f1d652be
PR:   remix-run/remix#11186

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = Path("/workspace/remix")
DEMO = REPO / "demos/bookstore"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_files_exist_and_nonempty():
    """Key modified files must exist and be non-empty."""
    files = [
        DEMO / "app/middleware/database.ts",
        DEMO / "app/middleware/auth.ts",
        DEMO / "app/books.tsx",
        DEMO / "app/cart.tsx",
        DEMO / "README.md",
    ]
    for f in files:
        assert f.exists(), f"Missing file: {f}"
        assert f.stat().st_size > 0, f"Empty file: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_middleware_uses_context_set():
    """database middleware must use context.set(Database, db) not context.db = db"""
    content = (DEMO / "app/middleware/database.ts").read_text()
    assert "context.set(Database, db)" in content, \
        "database middleware must use context.set(Database, db)"
    assert "context.db" not in content, \
        "database middleware must not use the old context.db pattern"


# [pr_diff] fail_to_pass
def test_handlers_use_get_database():
    """handler files must use get(Database) instead of destructuring db"""
    handlers = [
        DEMO / "app/books.tsx",
        DEMO / "app/cart.tsx",
        DEMO / "app/admin.books.tsx",
    ]
    for handler_file in handlers:
        content = handler_file.read_text()
        assert "get(Database)" in content, \
            f"{handler_file.name} must use get(Database) to access the database"


# [pr_diff] fail_to_pass
def test_auth_middleware_uses_get_database():
    """auth middleware must use get(Database) instead of destructuring db"""
    content = (DEMO / "app/middleware/auth.ts").read_text()
    assert "get(Database)" in content, \
        "auth middleware must use get(Database) pattern"


# [pr_diff] fail_to_pass
def test_no_module_augmentation():
    """the context.db module augmentation file must be deleted"""
    augmentation = DEMO / "app/types/context.db.ts"
    assert not augmentation.exists(), \
        "types/context.db.ts module augmentation must be removed"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_readme_documents_get_database_pattern():
    """README must document the context.get(Database) / context.set(Database) pattern"""
    readme = (DEMO / "README.md").read_text()
    has_new_pattern = (
        "get(Database)" in readme
        or "context.set(Database" in readme
    )
    assert has_new_pattern, \
        "README must document the get(Database) / context.set(Database) pattern"


# [config_edit] fail_to_pass
def test_readme_removes_old_context_db_reference():
    """README must not describe the old context.db pattern in database middleware section"""
    readme = (DEMO / "README.md").read_text()
    lines = readme.split("\n")
    # Find all lines referencing middleware/database.ts
    db_middleware_lines = [
        (i, line) for i, line in enumerate(lines)
        if "middleware/database" in line.lower()
    ]
    assert len(db_middleware_lines) > 0, \
        "README should still reference the database middleware file"
    for i, line in db_middleware_lines:
        assert "context.db" not in line.lower(), \
            f"README line {i} still references old context.db pattern: {line.strip()}"
