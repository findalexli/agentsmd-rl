"""
Task: tuist-fixserver-share-clonelocal-dev-instance
Repo: tuist/tuist @ 729c4d6361931ac3612f2440bb643e340fd9e5a2
PR:   9979

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/tuist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — shell script behavioral tests
# ---------------------------------------------------------------------------

def test_dev_instance_script_generates_suffix():
    """dev_instance_env.sh creates a .tuist-dev-instance file and exports TUIST_DEV_INSTANCE."""
    script = Path(REPO) / "mise" / "utilities" / "dev_instance_env.sh"
    assert script.exists(), "mise/utilities/dev_instance_env.sh must exist"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Run the script with MISE_PROJECT_ROOT pointing to tmpdir
        result = subprocess.run(
            ["bash", "-c", f'export MISE_PROJECT_ROOT="{tmpdir}"; source "{script}"; echo "$TUIST_DEV_INSTANCE"'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        suffix = result.stdout.strip()
        assert suffix.isdigit(), f"TUIST_DEV_INSTANCE should be numeric, got: {suffix}"
        suffix_int = int(suffix)
        assert 1 <= suffix_int <= 999, f"Suffix {suffix_int} out of range [1,999]"

        instance_file = Path(tmpdir) / ".tuist-dev-instance"
        assert instance_file.exists(), ".tuist-dev-instance file not created"
        assert instance_file.read_text().strip() == suffix


def test_dev_instance_script_port_arithmetic():
    """Port env vars are computed as base_port + suffix."""
    script = Path(REPO) / "mise" / "utilities" / "dev_instance_env.sh"
    assert script.exists(), "mise/utilities/dev_instance_env.sh must exist"

    with tempfile.TemporaryDirectory() as tmpdir:
        suffix = "42"
        result = subprocess.run(
            ["bash", "-c",
             f'export MISE_PROJECT_ROOT="{tmpdir}"; export TUIST_DEV_INSTANCE="{suffix}"; '
             f'source "{script}"; '
             'echo "$TUIST_SERVER_PORT $TUIST_CACHE_PORT $TUIST_MINIO_API_PORT $TUIST_MINIO_CONSOLE_PORT"'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        ports = result.stdout.strip().split()
        assert len(ports) == 4, f"Expected 4 port values, got: {ports}"
        server_port, cache_port, minio_api, minio_console = [int(p) for p in ports]
        assert server_port == 8080 + 42, f"Server port: expected {8080+42}, got {server_port}"
        assert cache_port == 8087 + 42, f"Cache port: expected {8087+42}, got {cache_port}"
        assert minio_api == 9095 + 42, f"MinIO API port: expected {9095+42}, got {minio_api}"
        assert minio_console == 9098 + 42, f"MinIO console port: expected {9098+42}, got {minio_console}"


def test_dev_instance_script_persists_and_reuses_suffix():
    """Running the script twice produces the same suffix (reads from .tuist-dev-instance)."""
    script = Path(REPO) / "mise" / "utilities" / "dev_instance_env.sh"
    assert script.exists(), "mise/utilities/dev_instance_env.sh must exist"

    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = f'export MISE_PROJECT_ROOT="{tmpdir}"; source "{script}"; echo "$TUIST_DEV_INSTANCE"'
        r1 = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=10)
        assert r1.returncode == 0, f"First run failed: {r1.stderr}"
        suffix1 = r1.stdout.strip()

        # Unset TUIST_DEV_INSTANCE to force reading from file
        cmd2 = f'unset TUIST_DEV_INSTANCE; export MISE_PROJECT_ROOT="{tmpdir}"; source "{script}"; echo "$TUIST_DEV_INSTANCE"'
        r2 = subprocess.run(["bash", "-c", cmd2], capture_output=True, text=True, timeout=10)
        assert r2.returncode == 0, f"Second run failed: {r2.stderr}"
        suffix2 = r2.stdout.strip()

        assert suffix1 == suffix2, f"Suffix not persisted: {suffix1} != {suffix2}"


def test_dev_instance_script_validates_bad_suffix():
    """Script rejects invalid suffix values (non-numeric, out of range)."""
    script = Path(REPO) / "mise" / "utilities" / "dev_instance_env.sh"
    assert script.exists(), "mise/utilities/dev_instance_env.sh must exist"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Test non-numeric suffix
        result = subprocess.run(
            ["bash", "-c",
             f'export MISE_PROJECT_ROOT="{tmpdir}"; export TUIST_DEV_INSTANCE="abc"; source "{script}" 2>&1'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode != 0, "Script should fail on non-numeric suffix"

        # Test out-of-range suffix (0)
        result2 = subprocess.run(
            ["bash", "-c",
             f'export MISE_PROJECT_ROOT="{tmpdir}"; export TUIST_DEV_INSTANCE="0"; source "{script}" 2>&1'],
            capture_output=True, text=True, timeout=10
        )
        assert result2.returncode != 0, "Script should fail on suffix 0"


def test_dev_instance_script_db_names():
    """Database name env vars include the suffix."""
    script = Path(REPO) / "mise" / "utilities" / "dev_instance_env.sh"
    assert script.exists(), "mise/utilities/dev_instance_env.sh must exist"

    with tempfile.TemporaryDirectory() as tmpdir:
        suffix = "77"
        result = subprocess.run(
            ["bash", "-c",
             f'export MISE_PROJECT_ROOT="{tmpdir}"; export TUIST_DEV_INSTANCE="{suffix}"; '
             f'source "{script}"; '
             'echo "$TUIST_SERVER_POSTGRES_DB|$TUIST_SERVER_CLICKHOUSE_DB|$TUIST_CACHE_TEST_POSTGRES_DB"'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        pg_db, ch_db, cache_test_db = result.stdout.strip().split("|")
        assert pg_db == f"tuist_development_{suffix}", f"Postgres DB: expected tuist_development_{suffix}, got {pg_db}"
        assert ch_db == f"tuist_development_{suffix}", f"ClickHouse DB: expected tuist_development_{suffix}, got {ch_db}"
        assert cache_test_db == f"cache_test_{suffix}", f"Cache test DB: expected cache_test_{suffix}, got {cache_test_db}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config file integration tests
# ---------------------------------------------------------------------------

def test_server_runtime_reads_port_env():
    """server/config/runtime.exs reads TUIST_SERVER_PORT for dev mode."""
    runtime = Path(REPO) / "server" / "config" / "runtime.exs"
    content = runtime.read_text()
    assert "TUIST_SERVER_PORT" in content, \
        "runtime.exs must read TUIST_SERVER_PORT env var for configurable dev port"
    assert "TUIST_SERVER_POSTGRES_DB" in content, \
        "runtime.exs must read TUIST_SERVER_POSTGRES_DB for instance-scoped database"
    assert "TUIST_SERVER_CLICKHOUSE_DB" in content, \
        "runtime.exs must read TUIST_SERVER_CLICKHOUSE_DB for instance-scoped analytics DB"


def test_cache_runtime_reads_port_env():
    """cache/config/runtime.exs reads TUIST_CACHE_PORT and TUIST_CACHE_SERVER_URL for dev mode."""
    runtime = Path(REPO) / "cache" / "config" / "runtime.exs"
    content = runtime.read_text()
    assert "TUIST_CACHE_PORT" in content, \
        "cache runtime.exs must read TUIST_CACHE_PORT env var"
    assert "TUIST_CACHE_SERVER_URL" in content, \
        "cache runtime.exs must read TUIST_CACHE_SERVER_URL env var"


def test_environment_reads_minio_port():
    """server/lib/tuist/environment.ex reads TUIST_MINIO_API_PORT and TUIST_MINIO_CONSOLE_PORT."""
    env_ex = Path(REPO) / "server" / "lib" / "tuist" / "environment.ex"
    content = env_ex.read_text()
    assert "TUIST_MINIO_API_PORT" in content, \
        "environment.ex must read TUIST_MINIO_API_PORT env var"
    assert "TUIST_MINIO_CONSOLE_PORT" in content, \
        "environment.ex must read TUIST_MINIO_CONSOLE_PORT env var"


def test_environment_default_app_url_reads_server_url():
    """server/lib/tuist/environment.ex uses TUIST_SERVER_URL for the default dev app URL."""
    env_ex = Path(REPO) / "server" / "lib" / "tuist" / "environment.ex"
    content = env_ex.read_text()
    assert "TUIST_SERVER_URL" in content, \
        "environment.ex must read TUIST_SERVER_URL for dev app URL"
    # The old hardcoded pattern should be replaced with a helper that reads env
    assert "default_app_url" in content or "app_base_url" in content, \
        "environment.ex should extract URL logic into a helper function"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------





# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — gitignore update
# ---------------------------------------------------------------------------

def test_gitignore_includes_instance_file():
    """The .tuist-dev-instance state file must be listed in .gitignore."""
    gitignore = Path(REPO) / ".gitignore"
    content = gitignore.read_text()
    assert ".tuist-dev-instance" in content, \
        ".gitignore must include .tuist-dev-instance to avoid committing instance state"
