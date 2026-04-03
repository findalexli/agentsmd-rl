"""
Task: trigger.dev-prisma-6140-upgrade
Repo: triggerdotdev/trigger.dev @ 688b108ec3283fc738a416a6a44ab4abb0ab1fd5
PR:   2444

Prisma 5.4.1 → 6.14.0 upgrade: generated client output directory,
import path migration, query performance monitoring, cursor rules update.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — schema.prisma changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_schema_output_to_generated():
    """schema.prisma must configure output to ../generated/prisma directory."""
    schema = Path(REPO) / "internal-packages" / "database" / "prisma" / "schema.prisma"
    content = schema.read_text()
    # Prisma 6 requires explicit output directory for generated client
    assert re.search(r'output\s*=\s*"../generated/prisma"', content), (
        "schema.prisma must set output = \"../generated/prisma\" in the generator block"
    )


# [pr_diff] fail_to_pass
def test_schema_tracing_preview_removed():
    """schema.prisma previewFeatures must not include 'tracing' (removed in Prisma 6)."""
    schema = Path(REPO) / "internal-packages" / "database" / "prisma" / "schema.prisma"
    content = schema.read_text()
    # Extract previewFeatures value
    match = re.search(r'previewFeatures\s*=\s*\[([^\]]*)\]', content)
    assert match is not None, "schema.prisma must have a previewFeatures line"
    features = match.group(1)
    assert "tracing" not in features.lower(), (
        f"previewFeatures must not include 'tracing' (deprecated in Prisma 6), got: [{features}]"
    )
    # metrics should still be present
    assert "metrics" in features.lower(), (
        f"previewFeatures should still include 'metrics', got: [{features}]"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — import path migration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_database_exports_from_generated():
    """database/src/index.ts must export from ../generated/prisma, not @prisma/client."""
    index = Path(REPO) / "internal-packages" / "database" / "src" / "index.ts"
    content = index.read_text()
    assert "generated/prisma" in content, (
        "index.ts must export from the generated prisma directory"
    )
    # Must NOT still export from @prisma/client directly
    lines = [l.strip() for l in content.splitlines() if l.strip().startswith("export")]
    client_exports = [l for l in lines if "@prisma/client" in l and "generated" not in l]
    assert len(client_exports) == 0, (
        f"index.ts should not have direct @prisma/client exports: {client_exports}"
    )


# [pr_diff] fail_to_pass
def test_transaction_imports_from_generated():
    """transaction.ts must import PrismaClient from generated path, not @prisma/client."""
    tx = Path(REPO) / "internal-packages" / "database" / "src" / "transaction.ts"
    content = tx.read_text()
    # Must import PrismaClient from generated directory
    assert re.search(r'import\s*\{[^}]*PrismaClient[^}]*\}\s*from\s*"[^"]*generated/prisma"', content), (
        "transaction.ts must import PrismaClient from ../generated/prisma"
    )
    # Must import Decimal from decimal.js (not from Prisma namespace)
    assert re.search(r'import\s*\{[^}]*Decimal[^}]*\}\s*from\s*"decimal\.js"', content), (
        "transaction.ts must import Decimal from 'decimal.js'"
    )
    # Must NOT use Prisma.Decimal or Prisma.TransactionIsolationLevel
    assert "Prisma.Decimal" not in content, (
        "transaction.ts must not use Prisma.Decimal (use decimal.js import instead)"
    )
    assert "Prisma.TransactionIsolationLevel" not in content, (
        "transaction.ts must not use Prisma.TransactionIsolationLevel (define locally)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — new query performance monitor
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_query_performance_monitor():
    """queryPerformanceMonitor.server.ts must exist with QueryPerformanceMonitor class."""
    qpm = Path(REPO) / "apps" / "webapp" / "app" / "utils" / "queryPerformanceMonitor.server.ts"
    assert qpm.exists(), "queryPerformanceMonitor.server.ts must exist"
    content = qpm.read_text()
    # Must have the class
    assert "class QueryPerformanceMonitor" in content, (
        "File must define a QueryPerformanceMonitor class"
    )
    # Must have onQuery method that accepts duration and query
    assert "onQuery" in content, (
        "QueryPerformanceMonitor must have an onQuery method"
    )
    # Must reference a slow query threshold
    assert "verySlowQueryThreshold" in content or "slowQueryThreshold" in content, (
        "QueryPerformanceMonitor must use a slow query threshold configuration"
    )
    # Must log slow queries
    assert "logger.error" in content or "logger.warn" in content, (
        "QueryPerformanceMonitor must log slow queries"
    )


# [pr_diff] fail_to_pass
def test_env_slow_query_threshold():
    """env.server.ts must define VERY_SLOW_QUERY_THRESHOLD_MS environment variable."""
    env_file = Path(REPO) / "apps" / "webapp" / "app" / "env.server.ts"
    content = env_file.read_text()
    assert "VERY_SLOW_QUERY_THRESHOLD_MS" in content, (
        "env.server.ts must define VERY_SLOW_QUERY_THRESHOLD_MS"
    )
    # Should be optional (not required) since it's for monitoring
    assert re.search(r'VERY_SLOW_QUERY_THRESHOLD_MS.*optional', content), (
        "VERY_SLOW_QUERY_THRESHOLD_MS should be optional"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — cursor rules update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — package version consistency
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prisma_client_version_upgraded():
    """database/package.json must have @prisma/client >= 6.0.0."""
    pkg_path = Path(REPO) / "internal-packages" / "database" / "package.json"
    pkg = json.loads(pkg_path.read_text())
    version = pkg.get("dependencies", {}).get("@prisma/client", "0.0.0")
    # Extract major version number
    major = int(version.lstrip("^~").split(".")[0])
    assert major >= 6, (
        f"@prisma/client must be >= 6.0.0, got {version}"
    )
