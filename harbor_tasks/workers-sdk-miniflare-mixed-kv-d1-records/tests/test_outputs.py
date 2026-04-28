"""
Behavioral tests for cloudflare/workers-sdk PR #12986.

The PR loosens the Miniflare Zod schema so that `kvNamespaces` and
`d1Databases` records may freely mix plain string entries (referring to a
local namespace name) and object entries (with `id`/`remoteProxyConnectionString`).

We exercise this by running short Node scripts inside the container that
import the freshly-built miniflare and observe whether constructing
`new Miniflare({ ... })` with a mixed record throws a Zod validation error.

Construction is synchronous — Zod validation runs in the constructor and
throws before workerd is fully started, so we don't need a working network.
We always call `mf.dispose()` afterwards so the process exits cleanly.
"""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/workers-sdk")
MINIFLARE_DIST = REPO / "packages/miniflare/dist/src/index.js"
KV_SRC = REPO / "packages/miniflare/src/plugins/kv/index.ts"
D1_SRC = REPO / "packages/miniflare/src/plugins/d1/index.ts"


def run_node(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a Node.js snippet inside the container with a timeout."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO),
    )


def construct_and_dispose(options_json: str) -> subprocess.CompletedProcess:
    """
    Build a Node script that constructs a Miniflare with the given options,
    awaits dispose(), then exits 0. If construction throws synchronously, the
    script exits non-zero and prints the error to stderr.
    """
    script = textwrap.dedent(f"""
        const {{ Miniflare }} = require({json.dumps(str(MINIFLARE_DIST))});
        (async () => {{
            const options = Object.assign(
                {{ modules: true, script: 'export default {{ fetch: () => new Response("hi") }};' }},
                {options_json}
            );
            let mf;
            try {{
                mf = new Miniflare(options);
            }} catch (e) {{
                console.error('CONSTRUCT_THREW:', e && e.message ? e.message : e);
                process.exit(2);
            }}
            try {{
                await mf.dispose();
            }} catch (e) {{
                console.error('DISPOSE_THREW:', e && e.message ? e.message : e);
                process.exit(3);
            }}
            console.log('OK');
            process.exit(0);
        }})().catch(e => {{
            console.error('UNCAUGHT:', e && e.message ? e.message : e);
            process.exit(4);
        }});
    """)
    return run_node(script, timeout=90)


# ---------------------------------------------------------------------------
# Fail-to-pass: the actual bug fix
# ---------------------------------------------------------------------------

def test_kv_namespaces_mixed_string_and_object():
    """Mixed kvNamespaces record (string + object values) must be accepted."""
    options = json.dumps({
        "kvNamespaces": {
            "LOCAL_NS": "local-ns",
            "REMOTE_NS": {"id": "remote-ns"},
        },
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, (
        f"Expected mixed kvNamespaces record to be accepted; "
        f"node exited {r.returncode}.\nstderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    assert "OK" in r.stdout, f"unexpected stdout: {r.stdout}"


def test_d1_databases_mixed_string_and_object():
    """Mixed d1Databases record (string + object values) must be accepted."""
    options = json.dumps({
        "d1Databases": {
            "LOCAL_DB": "local-db",
            "REMOTE_DB": {"id": "remote-db"},
        },
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, (
        f"Expected mixed d1Databases record to be accepted; "
        f"node exited {r.returncode}.\nstderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    assert "OK" in r.stdout, f"unexpected stdout: {r.stdout}"


def test_kv_namespaces_object_first_then_string():
    """Order independence: object first, string second."""
    options = json.dumps({
        "kvNamespaces": {
            "FIRST_NS": {"id": "first-ns"},
            "SECOND_NS": "second-ns",
        },
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, (
        f"Expected object-then-string kvNamespaces to be accepted; "
        f"node exited {r.returncode}.\nstderr:\n{r.stderr}"
    )


def test_d1_databases_three_way_mix():
    """A larger mixed record (3 string + 2 object) must validate."""
    options = json.dumps({
        "d1Databases": {
            "DB_A": "db-a",
            "DB_B": {"id": "db-b"},
            "DB_C": "db-c",
            "DB_D": {"id": "db-d"},
            "DB_E": "db-e",
        },
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"three-way mix rejected: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass: pre-existing valid forms must keep working
# ---------------------------------------------------------------------------

def test_kv_namespaces_all_strings():
    """All-string record (the most common case) keeps working."""
    options = json.dumps({
        "kvNamespaces": {"NS1": "ns-one", "NS2": "ns-two"},
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"all-string kvNamespaces rejected: {r.stderr}"


def test_kv_namespaces_all_objects():
    """All-object record keeps working."""
    options = json.dumps({
        "kvNamespaces": {
            "NS1": {"id": "id-one"},
            "NS2": {"id": "id-two"},
        },
    })
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"all-object kvNamespaces rejected: {r.stderr}"


def test_kv_namespaces_string_array():
    """String-array form keeps working."""
    options = json.dumps({"kvNamespaces": ["A", "B", "C"]})
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"string-array kvNamespaces rejected: {r.stderr}"


def test_d1_databases_all_strings():
    options = json.dumps({"d1Databases": {"DB1": "one", "DB2": "two"}})
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"all-string d1Databases rejected: {r.stderr}"


def test_d1_databases_string_array():
    options = json.dumps({"d1Databases": ["DB1", "DB2"]})
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"string-array d1Databases rejected: {r.stderr}"


def test_no_bindings_at_all():
    """Constructing with no kv/d1 options at all is unaffected."""
    options = json.dumps({})
    r = construct_and_dispose(options)
    assert r.returncode == 0, f"empty config rejected: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass: invalid input is still rejected (regression guard)
# ---------------------------------------------------------------------------

def test_kv_namespaces_rejects_garbage_value():
    """A number value (neither string nor object) must still be rejected."""
    script = textwrap.dedent(f"""
        const {{ Miniflare }} = require({json.dumps(str(MINIFLARE_DIST))});
        let threw = false;
        try {{
            new Miniflare({{
                modules: true,
                script: '',
                kvNamespaces: {{ BAD: 42 }},
            }});
        }} catch (e) {{
            threw = true;
        }}
        process.exit(threw ? 0 : 1);
    """)
    r = run_node(script)
    assert r.returncode == 0, "expected schema to still reject numeric value"


def test_d1_databases_rejects_object_without_id():
    """Object form without `id` field must still be rejected."""
    script = textwrap.dedent(f"""
        const {{ Miniflare }} = require({json.dumps(str(MINIFLARE_DIST))});
        let threw = false;
        try {{
            new Miniflare({{
                modules: true,
                script: '',
                d1Databases: {{ BAD: {{ notAnId: 'x' }} }},
            }});
        }} catch (e) {{
            threw = true;
        }}
        process.exit(threw ? 0 : 1);
    """)
    r = run_node(script)
    assert r.returncode == 0, "expected schema to still reject object missing `id`"


# ---------------------------------------------------------------------------
# Pass-to-pass from the repo's own CI: miniflare's tsc typecheck must
# continue to succeed after the patch.
# ---------------------------------------------------------------------------

def test_miniflare_typecheck():
    """Repo's own `pnpm --filter miniflare run check:type` must still pass."""
    r = subprocess.run(
        ["pnpm", "--filter", "miniflare", "run", "check:type"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"miniflare typecheck failed:\n"
        f"--- stdout ---\n{r.stdout[-1500:]}\n"
        f"--- stderr ---\n{r.stderr[-1500:]}"
    )

# === pass-to-pass from the repo's own test suite ===

def test_repo_vitest_index_spec():
    """Repo's vitest suite for test/index.spec.ts must continue to pass."""
    r = subprocess.run(
        ["bash", "-lc", "pnpm --filter miniflare exec vitest run test/index.spec.ts"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"vitest index.spec.ts failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build --filter="./packages/*"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_upload_packages():
    """pass_to_pass | CI job 'build' → step 'Upload packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register .github/prereleases/upload.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Upload packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cleanup_test_projects_cleanup_e2e_test_projects():
    """pass_to_pass | CI job 'Cleanup Test Projects' → step 'Cleanup E2E test projects'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register tools/e2e/e2eCleanup.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Cleanup E2E test projects' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")