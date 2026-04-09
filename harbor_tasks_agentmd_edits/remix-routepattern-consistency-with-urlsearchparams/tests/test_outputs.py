"""
Task: remix-routepattern-consistency-with-urlsearchparams
Repo: remix-run/remix @ 92a9b9df4ef4c7096973a6d1df040f512e7ccee2
PR:   11200

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/remix"
LIB = f"{REPO}/packages/route-pattern/src/lib"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts file in the route-pattern lib dir and execute with node."""
    script_path = Path(LIB) / "_eval_test_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TS source files are non-empty and structurally valid."""
    files = [
        "packages/route-pattern/src/lib/route-pattern/parse.ts",
        "packages/route-pattern/src/lib/route-pattern/match.ts",
        "packages/route-pattern/src/lib/route-pattern/serialize.ts",
        "packages/route-pattern/src/lib/route-pattern/href.ts",
    ]
    for f in files:
        path = Path(REPO) / f
        assert path.exists(), f"{f} does not exist"
        content = path.read_text()
        assert len(content) > 50, f"{f} appears empty or truncated"
        assert "export" in content, f"{f} missing exports"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes for route-pattern (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/route-pattern",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_tests():
    """Repo's tests for route-pattern pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "test"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/route-pattern",
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_lint():
    """Repo's lint for route-pattern passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/route-pattern",
    )
    # Skip if package has no lint script (will error with missing script)
    if "missing script" in r.stderr.lower() or "missing script" in r.stdout.lower():
        return
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_key_only_and_key_equals_match_equivalently():
    """Pattern '?q=' must match URL with just '?q' (key present, no value)."""
    result = _run_ts("""
import { matchSearch } from './route-pattern/match.ts'
import { parseSearch } from './route-pattern/parse.ts'

// Pattern: ?q=
let constraints = parseSearch('q=')

// URL: ?q (key only, value is empty string per URLSearchParams)
let params = new URLSearchParams('q')

let matches = matchSearch(params, constraints)
console.log(JSON.stringify({ matches }))
""")
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["matches"] is True, \
        "Pattern '?q=' should match URL with '?q' — they're the same constraint"


def test_plus_decoded_as_space():
    """parseSearch must decode '+' as space, consistent with URLSearchParams."""
    result = _run_ts("""
import { parseSearch } from './route-pattern/parse.ts'

let constraints = parseSearch('q=a+b')
let values = [...(constraints.get('q') ?? [])]
console.log(JSON.stringify({ values }))
""")
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert "a b" in data["values"], \
        f"'+' should be decoded as space, got: {data['values']}"


def test_serialize_key_only_includes_equals():
    """Serializing a key-only constraint (?q) must produce 'q=' (with equals sign)."""
    result = _run_ts("""
import { parseSearch } from './route-pattern/parse.ts'
import { serializeSearch } from './route-pattern/serialize.ts'

// Parse '?q' (key-only) and re-serialize
let constraints = parseSearch('q')
let serialized = serializeSearch(constraints)
console.log(JSON.stringify({ serialized }))
""")
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["serialized"] == "q=", \
        f"Key-only constraint should serialize to 'q=', got: {data['serialized']}"


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------



