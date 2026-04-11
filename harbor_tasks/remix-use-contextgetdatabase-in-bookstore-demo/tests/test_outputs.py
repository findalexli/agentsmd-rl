"""
Task: remix-use-contextgetdatabase-in-bookstore-demo
Repo: remix-run/remix @ b29fc874293468babb25b90e95edc208f1d652be
PR:   11186

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"
BOOKSTORE = Path(REPO) / "demos" / "bookstore"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script in the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _pnpm_cmd(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a pnpm command in the repo directory, handling corepack if needed."""
    # Ensure pnpm is available via corepack if not already in PATH
    cmd_prefix = []
    if subprocess.run(["which", "pnpm"], capture_output=True).returncode != 0:
        cmd_prefix = ["sh", "-c", "corepack enable && pnpm " + " ".join(args)]
    else:
        cmd_prefix = ["pnpm"] + args
    return subprocess.run(
        cmd_prefix,
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint lint passes (pass_to_pass)."""
    r = _pnpm_cmd(["lint"], timeout=120)
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = _pnpm_cmd(["typecheck"], timeout=120)
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = _pnpm_cmd(["format:check"], timeout=120)
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_bookstore_unit_tests():
    """Bookstore demo unit tests pass (pass_to_pass)."""
    r = _pnpm_cmd(["--filter", "bookstore-demo", "test"], timeout=120)
    assert r.returncode == 0, f"Bookstore tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


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


def test_middleware_has_real_logic():
    """database.ts middleware must have real logic, not just a stub."""
    content = (BOOKSTORE / "app" / "middleware" / "database.ts").read_text()
    assert "loadDatabase" in content, "database.ts must export loadDatabase"
    assert "next()" in content, "database.ts middleware must call next()"
    assert "return" in content, "database.ts middleware must return the next() result"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_database_middleware_uses_context_set():
    """database.ts imports Database and uses context.set(Database, db) not context.db."""
    r = _run_py("""
import sys

content = open('demos/bookstore/app/middleware/database.ts').read()

# Must import Database from remix/data-table
if 'Database' not in content or 'remix/data-table' not in content:
    print("FAIL: Database not imported from remix/data-table", file=sys.stderr)
    sys.exit(1)

# Must use context.set(Database, ...) pattern
if 'context.set(Database' not in content:
    print("FAIL: does not use context.set(Database, ...)", file=sys.stderr)
    sys.exit(1)

# Must NOT use old context.db = pattern
if 'context.db' in content:
    print("FAIL: still uses context.db assignment", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Middleware pattern check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_handlers_use_get_database():
    """Route handler files use get(Database) to retrieve the database."""
    r = _run_py("""
import sys, os

bookstore = 'demos/bookstore/app'
handler_files = [
    'account.tsx', 'admin.books.tsx', 'admin.orders.tsx',
    'admin.users.tsx', 'books.tsx', 'auth.tsx', 'cart.tsx',
    'checkout.tsx', 'fragments.tsx', 'marketing.tsx',
]

get_database_count = 0
for fname in handler_files:
    path = os.path.join(bookstore, fname)
    if not os.path.exists(path):
        continue
    content = open(path).read()
    if 'get(Database)' in content:
        get_database_count += 1

if get_database_count < 8:
    print(f"FAIL: Only {get_database_count}/10 handler files use get(Database)", file=sys.stderr)
    sys.exit(1)

print(f"PASS: {get_database_count} handler files use get(Database)")
""")
    assert r.returncode == 0, f"Handler pattern check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_type_augmentation_removed():
    """The context.db.ts type augmentation file must be removed."""
    r = _run_py("""
import os, sys

aug_file = 'demos/bookstore/app/types/context.db.ts'
if os.path.exists(aug_file):
    content = open(aug_file).read()
    print(f"FAIL: context.db.ts still exists with {len(content)} bytes", file=sys.stderr)
    sys.exit(1)
print("PASS: context.db.ts removed")
""")
    assert r.returncode == 0, f"Type augmentation not removed: {r.stderr}"
    assert "PASS" in r.stdout


def test_auth_middleware_uses_get_database():
    """auth.ts middleware imports Database and uses get(Database) not destructured db."""
    r = _run_py("""
import sys

content = open('demos/bookstore/app/middleware/auth.ts').read()

# Must import Database from remix/data-table
if 'Database' not in content or 'remix/data-table' not in content:
    print("FAIL: auth.ts does not import Database from remix/data-table", file=sys.stderr)
    sys.exit(1)

# Must use get(Database) pattern
if 'get(Database)' not in content:
    print("FAIL: auth.ts does not use get(Database)", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Auth middleware check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_documents_context_set_pattern():
    """README.md describes the context.set/get(Database) pattern without duplicates."""
    r = _run_py("""
import sys

content = open('demos/bookstore/README.md').read()

# Must mention context.set(Database
if 'context.set(Database' not in content:
    print("FAIL: README does not mention context.set(Database, ...)", file=sys.stderr)
    sys.exit(1)

# Must mention get(Database)
if 'get(Database)' not in content:
    print("FAIL: README does not mention get(Database)", file=sys.stderr)
    sys.exit(1)

# Should not have duplicate database.ts bullet entries
lines = content.split('\\n')
db_bullets = [l for l in lines if 'middleware/database.ts' in l and l.strip().startswith('-')]
if len(db_bullets) > 1:
    print(f"FAIL: README has {len(db_bullets)} database.ts bullet entries, expected 1", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"README check failed: {r.stderr}"
    assert "PASS" in r.stdout
