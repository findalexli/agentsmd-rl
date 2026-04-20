"""
test_outputs.py — prisma/prisma#29287
PrismaPgAdapterFactory must accept a plain connection string URL as its first argument.
"""

import json
import os
import subprocess
import sys

REPO = "/workspace/prisma"
ADAPTER_PG_PATH = os.path.join(REPO, "packages/adapter-pg")
DIST_PATH = os.path.join(ADAPTER_PG_PATH, "dist")


def _run_node(script: str) -> str:
    """Run a node.js snippet in the task container."""
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Node error (exit {r.returncode}): {r.stderr}")
    return r.stdout.strip()


def test_adapter_factory_accepts_string_url():
    """
    f2p: PrismaPgAdapterFactory("postgresql://...") must set config to an object
    with a connectionString property, not leave config as a raw string.

    On the base commit (buggy), factory.config is the bare string URL.
    After the fix, factory.config is { connectionString: "..." }.
    """
    out = _run_node(f"""
    const {{ PrismaPg }} = require('{DIST_PATH}/index.js');
    const url = 'postgresql://test:test@localhost:5432/test';
    const factory = new PrismaPg(url);
    const cfg = factory.config;
    const result = {{
        configType: typeof cfg,
        hasConnectionString: cfg && typeof cfg === 'object' && 'connectionString' in cfg,
        connectionString: cfg && typeof cfg === 'object' ? cfg.connectionString : cfg
    }};
    console.log(JSON.stringify(result));
    """)
    result = json.loads(out)

    assert result["configType"] == "object", (
        f"config should be an object, got {result['configType']} — "
        f"string was not normalized to {{ connectionString }}"
    )
    assert result["hasConnectionString"], (
        f"config.connectionString missing — factory.config is {result['connectionString']!r}"
    )
    assert result["connectionString"] == "postgresql://test:test@localhost:5432/test", (
        f"connectionString mismatch: got {result['connectionString']!r}"
    )


def test_factory_produces_adapter_with_correct_url():
    """
    f2p: After construction with a string, adapter.underlyingDriver().options.connectionString
    must reflect the original URL.

    On the base commit (buggy), connect() throws:
    TypeError: Cannot use 'in' operator to search for 'password' in postgresql://...
    because the raw string is passed to pg.Pool as if it were a PoolConfig object.
    """
    # Test that connect() does NOT throw the "Cannot use 'in' operator" error
    script = f"""
    const {{ PrismaPg }} = require('{DIST_PATH}/index.js');
    const url = 'postgresql://test:test@localhost:5432/test';
    const factory = new PrismaPg(url);
    const adapterPromise = factory.connect();
    adapterPromise.then(adapter => {{
        const driverOpts = adapter.underlyingDriver().options;
        console.log(JSON.stringify({{ connectionString: driverOpts.connectionString }}));
    }}).catch(err => {{
        console.log(JSON.stringify({{ error: err.message }}));
    }});
    """
    out = _run_node(script)
    result = json.loads(out)

    assert "error" not in result, (
        f"connect() threw: {result['error']} — "
        f"string URL was not handled; pg.Pool tried to use it as a PoolConfig"
    )
    assert result["connectionString"] == "postgresql://test:test@localhost:5432/test", (
        f"adapter's underlyingDriver connectionString: expected 'postgresql://test:test@localhost:5432/test', "
        f"got {result['connectionString']!r}"
    )


def test_string_url_not_treated_as_pool_config():
    """
    f2p: A string URL must not be stored as-is; it must be normalized.
    On the buggy base, config would be the bare URL string.
    After fix, config is always a PoolConfig object.
    """
    out = _run_node(f"""
    const {{ PrismaPg }} = require('{DIST_PATH}/index.js');
    const factory = new PrismaPg('postgresql://user:pass@localhost:5432/mydb');
    console.log(JSON.stringify({{ configType: typeof factory.config }}));
    """)
    result = json.loads(out)

    assert result["configType"] != "string", (
        f"config is a raw string — string was not normalized to PoolConfig {{ connectionString }}"
    )


def test_repo_tests_pass():
    """
    p2p: All existing adapter-pg tests pass (35/35).
    This ensures the string URL handling doesn't break any existing behavior.
    """
    r = subprocess.run(
        ["pnpm", "--filter", "@prisma/adapter-pg", "test", "--", "--run"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"adapter-pg tests failed (exit {r.returncode}):\n"
        f"stdout (last 500 chars):\n{r.stdout[-500:]}\n"
        f"stderr (last 500 chars):\n{r.stderr[-500:]}"
    )


def test_repo_build():
    """
    p2p: Repo's build for adapter-pg succeeds (pass_to_pass).
    Ensures the package compiles without errors after any changes.
    """
    r = subprocess.run(
        ["pnpm", "--filter", "@prisma/adapter-pg", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"adapter-pg build failed (exit {r.returncode}):\n"
        f"stdout (last 500 chars):\n{r.stdout[-500:]}\n"
        f"stderr (last 500 chars):\n{r.stderr[-500:]}"
    )


def test_repo_lint():
    """
    p2p: Repo lint passes on adapter-pg source (pass_to_pass).
    ESLint runs with warnings only (no errors on base commit).
    """
    r = subprocess.run(
        ["pnpm", "--filter", "@prisma/adapter-pg", "exec", "eslint", "src/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ESLint failed (exit {r.returncode}):\n"
        f"stdout:\n{r.stdout[-500:]}\n"
        f"stderr:\n{r.stderr[-500:]}"
    )