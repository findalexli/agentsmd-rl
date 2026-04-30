"""
Task: remix-bookstore-db-context
Repo: remix-run/remix @ b29fc874293468babb25b90e95edc208f1d652be
PR:   remix-run/remix#11186

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")
DEMO = REPO / "demos/bookstore"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = DEMO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _ensure_pnpm_and_deps() -> None:
    """Ensure pnpm is installed globally and dependencies are installed."""
    # Check if pnpm is available
    result = subprocess.run(
        ["which", "pnpm"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        subprocess.run(
            ["npm", "install", "-g", "pnpm@10.32.1"],
            capture_output=True, text=True, check=True
        )
    # Check if node_modules exists in repo
    if not (REPO / "node_modules").exists():
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            capture_output=True, text=True, timeout=300, cwd=str(REPO), check=True
        )


# ---------------------------------------------------------------------------
# pass_to_pass / static
# ---------------------------------------------------------------------------

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
# pass_to_pass / repo_tests — CI/CD gates
# ---------------------------------------------------------------------------

def test_repo_typecheck():
    """Repo TypeScript typecheck passes (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_lint():
    """Repo ESLint passes (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=180, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_format():
    """Repo Prettier format check passes (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_bookstore_tests():
    """Bookstore demo tests pass (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "test"],
        capture_output=True, text=True, timeout=180, cwd=str(DEMO),
    )
    assert r.returncode == 0, f"Bookstore tests failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_bookstore_handler_tests():
    """Bookstore handler tests (books, cart) pass (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "test", "app/books.test.ts", "app/cart.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=str(DEMO),
    )
    assert r.returncode == 0, f"Bookstore handler tests failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_bookstore_auth_tests():
    """Bookstore auth tests (middleware) pass (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "test", "app/auth.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=str(DEMO),
    )
    assert r.returncode == 0, f"Bookstore auth tests failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_bookstore_account_tests():
    """Bookstore account handler tests pass (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "test", "app/account.test.ts"],
        capture_output=True, text=True, timeout=180, cwd=str(DEMO),
    )
    assert r.returncode == 0, f"Bookstore account tests failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


def test_repo_data_table_tests():
    """Data-table package unit tests pass (pass_to_pass)."""
    _ensure_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "test"],
        capture_output=True, text=True, timeout=180, cwd=str(REPO / "packages/data-table"),
    )
    assert r.returncode == 0, f"Data-table tests failed:\n{r.stderr[-500:] or r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# fail_to_pass / pr_diff — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_database_middleware_context_api():
    """database middleware uses context.set(Database, db) with proper import from remix/data-table."""
    r = _run_node("""
import { readFileSync } from 'fs';

const content = readFileSync('demos/bookstore/app/middleware/database.ts', 'utf8');
const errors = [];

// Must import Database from remix/data-table
if (!/import\\s+.*\\bDatabase\\b.*\\s+from\\s+['"]remix\\/data-table['"]/.test(content)) {
  errors.push("database.ts: missing Database import from remix/data-table");
}

// Must call context.set(Database, ...)
if (!/context\\.set\\(\\s*Database\\s*,/.test(content)) {
  errors.push("database.ts: missing context.set(Database, ...) call");
}

// Must NOT use old context.db = ... assignment
if (/context\\.db\\s*=/.test(content)) {
  errors.push("database.ts: still uses old context.db = ... pattern");
}

if (errors.length > 0) {
  console.error(errors.join("\\n"));
  process.exit(1);
}
console.log("PASS");
""")
    assert r.returncode == 0, f"database middleware validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_handlers_use_get_database_pattern():
    """handler files import Database from remix/data-table and use get(Database) instead of destructuring db."""
    r = _run_node("""
import { readFileSync } from 'fs';

const handlers = [
  'demos/bookstore/app/books.tsx',
  'demos/bookstore/app/cart.tsx',
  'demos/bookstore/app/admin.books.tsx',
];
const errors = [];

for (const file of handlers) {
  const content = readFileSync(file, 'utf8');
  const name = file.split('/').pop();

  // Must import Database from remix/data-table
  if (!/import\\s+.*\\bDatabase\\b.*\\s+from\\s+['"]remix\\/data-table['"]/.test(content)) {
    errors.push(name + ": missing Database import from remix/data-table");
  }

  // Must use get(Database) to access the db handle
  if (!content.includes('get(Database)')) {
    errors.push(name + ": missing get(Database) usage");
  }

  // Action functions must NOT destructure db from the context parameter
  // Matches patterns like: async index({ db }) or async show({ db, params })
  const dbDestructure = /async\\s+\\w+\\s*\\(\\s*\\{[^}]*\\bdb\\b[^}]*\\}\\s*\\)/;
  if (dbDestructure.test(content)) {
    errors.push(name + ": still destructures 'db' from action parameter");
  }
}

if (errors.length > 0) {
  console.error(errors.join("\\n"));
  process.exit(1);
}
console.log("PASS");
""")
    assert r.returncode == 0, f"handler validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_auth_middleware_uses_get_database():
    """auth middleware imports Database and uses get(Database) instead of destructuring db."""
    r = _run_node("""
import { readFileSync } from 'fs';

const content = readFileSync('demos/bookstore/app/middleware/auth.ts', 'utf8');
const errors = [];

// Must import Database from remix/data-table
if (!/import\\s+.*\\bDatabase\\b.*\\s+from\\s+['"]remix\\/data-table['"]/.test(content)) {
  errors.push("auth.ts: missing Database import from remix/data-table");
}

// Must use get(Database) pattern
if (!content.includes('get(Database)')) {
  errors.push("auth.ts: missing get(Database) usage");
}

// Arrow middleware functions must not destructure db from parameter
// Matches: async ({ db, get }) => or async ({ db }) =>
const arrowDbDestructure = /async\\s*\\(\\s*\\{[^}]*\\bdb\\b[^}]*\\}\\s*\\)/;
if (arrowDbDestructure.test(content)) {
  errors.push("auth.ts: still destructures 'db' from middleware parameter");
}

if (errors.length > 0) {
  console.error(errors.join("\\n"));
  process.exit(1);
}
console.log("PASS");
""")
    assert r.returncode == 0, f"auth middleware validation failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_no_module_augmentation():
    """the context.db module augmentation file must be deleted."""
    augmentation = DEMO / "app/types/context.db.ts"
    assert not augmentation.exists(), \
        "types/context.db.ts module augmentation must be removed"


# ---------------------------------------------------------------------------
# fail_to_pass / pr_diff — README documentation checks
# ---------------------------------------------------------------------------

def test_readme_documents_new_pattern():
    """README documents the context.set(Database) / get(Database) pattern."""
    readme = (DEMO / "README.md").read_text()
    has_new_pattern = (
        "get(Database)" in readme
        or "context.set(Database" in readme
    )
    assert has_new_pattern, \
        "README must document the get(Database) / context.set(Database) pattern"


def test_readme_no_old_context_db():
    """README must not describe old context.db pattern in database middleware section."""
    readme = (DEMO / "README.md").read_text()
    lines = readme.split("\n")
    db_middleware_lines = [
        (i, line) for i, line in enumerate(lines)
        if "middleware/database" in line.lower()
    ]
    assert len(db_middleware_lines) > 0, \
        "README should still reference the database middleware file"
    for i, line in db_middleware_lines:
        assert "context.db" not in line.lower(), \
            f"README line {i} still references old context.db pattern: {line.strip()}"
