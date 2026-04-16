"""
Tests for prisma/prisma#29285: fix: use mysql binary protocol to avoid a lossy conversion

The PR changes the MariaDB adapter to use execute (binary protocol) instead of query (text protocol)
to avoid precision loss with large decimal values.

Key changes:
- In performIO(): this.client.query() -> this.client.execute()
- Transaction operations still use query() because binary protocol doesn't support transactions
- usePhantomQuery set to true in startTransaction
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/prisma")
ADAPTER_MARIADB = REPO / "packages/adapter-mariadb"
SRC_MARIADB = ADAPTER_MARIADB / "src/mariadb.ts"


def test_adapter_uses_execute_for_queries():
    """
    Fail-to-pass: The MariaDB adapter must use execute() (binary protocol) for queries
    instead of query() (text protocol) to avoid precision loss with large decimal values.

    Before the fix: this.client.query(req, values) - causes precision loss
    After the fix:  this.client.execute(req, values) - preserves precision
    """
    content = SRC_MARIADB.read_text()

    # Find the performIO method which handles query execution
    # The fix changes: return await this.client.query(req, values)
    #             to: return await this.client.execute(req, values)

    # Check that execute is used in performIO for the main query path
    # We look for the pattern in the performIO method
    perform_io_match = re.search(
        r'async performIO\(.*?\).*?\{(.*?)\n  \}',
        content,
        re.DOTALL
    )
    assert perform_io_match, "Could not find performIO method"
    perform_io_body = perform_io_match.group(1)

    # The key change: query -> execute in performIO
    # This is the line that causes precision loss if not changed
    assert "this.client.execute(" in perform_io_body, (
        "performIO must use this.client.execute() (binary protocol) "
        "instead of this.client.query() (text protocol) to avoid precision loss"
    )

    # Verify that query is NOT used in the main execution path
    # (query is still used for transactions, but that's a different code path)
    lines = perform_io_body.split('\n')
    for line in lines:
        if 'this.client.' in line and 'execute' not in line and 'query' in line:
            # Check if this is the problematic query call (not inside a comment)
            stripped = line.strip()
            if stripped.startswith('return') or 'return await' in stripped:
                assert False, (
                    f"Found this.client.query() in performIO return statement: {line.strip()}. "
                    "This causes precision loss for large decimals. Use execute() instead."
                )


def test_lint_adapter():
    """
    Pass-to-pass: Lint checks must pass for the adapter.
    """
    r = subprocess.run(
        ["pnpm", "eslint", "src/", "--max-warnings=0"],
        cwd=str(ADAPTER_MARIADB),
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Lint errors in adapter:\n{r.stderr[-500:]}"


def test_repo_adapter_errors_test():
    """
    Pass-to-pass: Repo's error-mapping unit tests pass for adapter-mariadb.
    Runs via: pnpm run dev && pnpm exec vitest run src/errors.test.ts
    """
    r = subprocess.run(
        ["bash", "-c", "pnpm run dev && pnpm exec vitest run src/errors.test.ts"],
        cwd=str(ADAPTER_MARIADB),
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Error-mapping tests failed:\n{r.stderr[-500:]}"
