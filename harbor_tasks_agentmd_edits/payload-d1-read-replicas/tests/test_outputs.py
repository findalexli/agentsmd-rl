"""
Task: payload-d1-read-replicas
Repo: payloadcms/payload @ c135bf0a8763e738fd562e80c3a116264b868b76
PR:   14040

Adds readReplicas support ('first-primary' strategy) to the D1 SQLite adapter,
with corresponding documentation updates in sqlite.mdx and the D1 template README.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "packages/db-d1-sqlite/src/types.ts",
        "packages/db-d1-sqlite/src/connect.ts",
        "packages/db-d1-sqlite/src/index.ts",
    ]
    for f in files:
        path = Path(REPO) / f
        assert path.exists(), f"{f} does not exist"
        content = path.read_text()
        # Basic syntax: balanced braces
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 1, f"{f} has unbalanced braces ({opens} open, {closes} close)"
        # No obvious syntax corruption
        assert len(content) > 100, f"{f} appears empty or truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavior tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_args_type_has_read_replicas():
    """Args type in types.ts must include a readReplicas option."""
    types_ts = (Path(REPO) / "packages/db-d1-sqlite/src/types.ts").read_text()
    # Find the Args type block and check it contains readReplicas
    # The property should accept 'first-primary' as a value
    assert "readReplicas" in types_ts, "types.ts must define readReplicas property"
    # Verify it's in the Args type (not just anywhere)
    args_match = re.search(
        r"export\s+type\s+Args\s*=\s*\{([\s\S]*?)\}\s*&",
        types_ts,
    )
    assert args_match, "Could not find Args type definition in types.ts"
    args_body = args_match.group(1)
    assert "readReplicas" in args_body, "readReplicas must be defined in the Args type"
    assert "first-primary" in args_body, "readReplicas must accept 'first-primary' strategy"


# [pr_diff] fail_to_pass
def test_adapter_type_has_read_replicas():
    """SQLiteD1Adapter type must also include readReplicas."""
    types_ts = (Path(REPO) / "packages/db-d1-sqlite/src/types.ts").read_text()
    adapter_match = re.search(
        r"export\s+type\s+SQLiteD1Adapter\s*=\s*\{([\s\S]*?)\}\s*&",
        types_ts,
    )
    assert adapter_match, "Could not find SQLiteD1Adapter type in types.ts"
    adapter_body = adapter_match.group(1)
    assert "readReplicas" in adapter_body, (
        "SQLiteD1Adapter must include readReplicas property"
    )


# [pr_diff] fail_to_pass
def test_connect_handles_read_replicas():
    """connect.ts must use withSession when readReplicas is 'first-primary'."""
    connect_ts = (Path(REPO) / "packages/db-d1-sqlite/src/connect.ts").read_text()
    # The connect function must read readReplicas and call withSession
    assert "readReplicas" in connect_ts, (
        "connect.ts must reference readReplicas"
    )
    assert "withSession" in connect_ts, (
        "connect.ts must call withSession for read replica support"
    )
    assert "first-primary" in connect_ts, (
        "connect.ts must handle the 'first-primary' strategy"
    )


# [pr_diff] fail_to_pass
def test_index_passes_read_replicas():
    """index.ts must pass readReplicas from args to the adapter object."""
    index_ts = (Path(REPO) / "packages/db-d1-sqlite/src/index.ts").read_text()
    # Should pass args.readReplicas through to the adapter config
    assert "readReplicas" in index_ts, (
        "index.ts must pass readReplicas to the adapter"
    )
    # Check it reads from args (not hardcoded)
    assert re.search(r"args\.readReplicas", index_ts), (
        "index.ts must read readReplicas from args"
    )


# ---------------------------------------------------------------------------
# Config/doc update tests (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_connect_not_stub():
    """connect.ts must have real logic, not just an empty function."""
    connect_ts = (Path(REPO) / "packages/db-d1-sqlite/src/connect.ts").read_text()
    # Must still create a drizzle instance
    assert "drizzle" in connect_ts, "connect.ts must reference drizzle"
    # Must assign this.drizzle
    assert "this.drizzle" in connect_ts, "connect.ts must assign this.drizzle"
    # Must have meaningful length (not gutted)
    lines = [l for l in connect_ts.splitlines() if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 15, (
        f"connect.ts has only {len(lines)} non-empty non-comment lines — looks like a stub"
    )
