"""Behavioral tests for opencode#23216 — migrating Server + Layout config to Effect Schema."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path("/workspace/opencode")
CONFIG_DIR = REPO_ROOT / "packages" / "opencode" / "src" / "config"
LAYOUT_TS = CONFIG_DIR / "layout.ts"
SERVER_TS = CONFIG_DIR / "server.ts"
CONFIG_TS = CONFIG_DIR / "config.ts"
PROVIDER_TS = CONFIG_DIR / "provider.ts"

SCHEMA_RESULTS = Path("/tmp/schema_results.json")
VALIDATE_SCRIPT = "/test-sandbox/validate_schemas.ts"


_RESULTS_CACHE: dict[str, dict] | None = None


def _run_validator() -> dict[str, dict]:
    """Run the bun validator once per pytest invocation and cache the result map."""
    global _RESULTS_CACHE
    if _RESULTS_CACHE is not None:
        return _RESULTS_CACHE
    SCHEMA_RESULTS.unlink(missing_ok=True)
    proc = subprocess.run(
        ["bun", "run", VALIDATE_SCRIPT],
        cwd="/test-sandbox",
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Parse stdout (the validator prints JSON either way)
    try:
        if SCHEMA_RESULTS.exists():
            data = json.loads(SCHEMA_RESULTS.read_text())
        else:
            data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(
            f"validate_schemas.ts produced no JSON.\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    _RESULTS_CACHE = {entry["id"]: entry for entry in data}
    return _RESULTS_CACHE


def _check(name: str) -> None:
    results = _run_validator()
    if name not in results:
        raise AssertionError(f"Validator did not produce check {name!r}; results: {list(results)}")
    entry = results[name]
    assert entry["ok"], f"{name} failed: {entry.get('detail', '')}"


# ---------------------------------------------------------------------------
# Module structure (fail-to-pass)
# ---------------------------------------------------------------------------

def test_layout_module_imports():
    """packages/opencode/src/config/layout.ts must exist and import successfully."""
    _check("layout_module_imports")


def test_server_module_imports():
    """packages/opencode/src/config/server.ts must exist and import successfully."""
    _check("server_module_imports")


def test_layout_namespace_export():
    """layout.ts must export a `ConfigLayout` namespace (e.g. `export * as ConfigLayout`)."""
    _check("layout_namespace_export")


def test_server_namespace_export():
    """server.ts must export a `ConfigServer` namespace (e.g. `export * as ConfigServer`)."""
    _check("server_namespace_export")


def test_layout_schema_present():
    """`ConfigLayout.Layout` must be exported."""
    _check("layout_schema_present")


def test_server_schema_present():
    """`ConfigServer.Server` must be exported."""
    _check("server_schema_present")


def test_layout_zod_accessor():
    """`ConfigLayout.Layout.zod` must be a usable zod schema."""
    _check("layout_zod_accessor")


def test_server_zod_accessor():
    """`ConfigServer.Server.zod` must be a usable zod schema."""
    _check("server_zod_accessor")


# ---------------------------------------------------------------------------
# Layout schema validation behavior (fail-to-pass)
# ---------------------------------------------------------------------------

def test_layout_accepts_auto():
    _check("layout_accepts_auto")


def test_layout_accepts_stretch():
    _check("layout_accepts_stretch")


def test_layout_rejects_invalid_value():
    _check("layout_rejects_invalid")


def test_layout_rejects_empty_string():
    _check("layout_rejects_empty")


# ---------------------------------------------------------------------------
# Server schema validation behavior (fail-to-pass)
# ---------------------------------------------------------------------------

def test_server_accepts_empty_object():
    """All fields are optional, so an empty object must validate."""
    _check("server_accepts_empty")


def test_server_accepts_full_config():
    """A complete server config with all fields populated must validate."""
    _check("server_accepts_full")


def test_server_rejects_negative_port():
    """Port must be a positive integer."""
    _check("server_rejects_negative_port")


def test_server_rejects_zero_port():
    """Port must be strictly greater than zero."""
    _check("server_rejects_zero_port")


def test_server_rejects_float_port():
    """Port must be an integer."""
    _check("server_rejects_float_port")


def test_server_rejects_non_string_hostname():
    _check("server_rejects_bad_hostname")


def test_server_rejects_non_array_cors():
    _check("server_rejects_bad_cors")


# ---------------------------------------------------------------------------
# config.ts re-export wiring (fail-to-pass)
# ---------------------------------------------------------------------------

def test_config_imports_configserver():
    """config.ts must `import { ConfigServer } from "./server"`."""
    _check("config_imports_configserver")


def test_config_imports_configlayout():
    """config.ts must `import { ConfigLayout } from "./layout"`."""
    _check("config_imports_configlayout")


def test_config_reexports_server_via_zod():
    """config.ts's exported `Server` must be `ConfigServer.Server.zod` (not an inline z.object)."""
    _check("config_reexports_server_via_zod")


def test_config_reexports_layout_via_zod():
    """config.ts's exported `Layout` must be `ConfigLayout.Layout.zod` (not an inline z.enum)."""
    _check("config_reexports_layout_via_zod")


def test_config_no_inline_layout_enum():
    """The legacy `z.enum(["auto", "stretch"])` must be removed from config.ts."""
    _check("config_no_inline_layout_enum")


# ---------------------------------------------------------------------------
# provider.ts cleanup (fail-to-pass)
# ---------------------------------------------------------------------------

def test_provider_comment_removed():
    """The stale `// Positive integer: emits JSON Schema ...` comment in provider.ts is removed."""
    src = PROVIDER_TS.read_text()
    assert (
        "Positive integer: emits JSON Schema" not in src
    ), "stale comment block above PositiveInt was not removed from provider.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass sanity checks (must succeed at base too)
# ---------------------------------------------------------------------------

def test_repo_checkout_intact():
    """The cloned opencode repo is at the expected base commit before any agent edits."""
    r = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, r.stderr
    # We don't pin to base SHA because the agent may have committed; just verify git works.
    assert len(r.stdout.strip()) == 40


def test_bun_runtime_available():
    """Bun is installed in the test environment (pass_to_pass)."""
    r = subprocess.run(["bun", "--version"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip().startswith("1."), r.stdout


def test_provider_module_still_imports():
    """provider.ts (existing module the PR also touches) must continue to load
    successfully through bun's TypeScript loader, both before and after the
    migration. This guards against the agent breaking provider.ts while
    cleaning up its stale comment."""
    r = subprocess.run(
        ["bun", "-e", f"await import('{PROVIDER_TS}'); console.log('OK')"],
        cwd="/test-sandbox",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"provider.ts failed to import:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    assert "OK" in r.stdout, r.stdout

# === CI-mined test (taskforge.ci_check_miner) ===
def test_ci_smoke_bun_test():
    """pass_to_pass | Run bun test on smoke suite to verify effect+zod toolchain."""
    r = subprocess.run(
        ["bash", "-lc", "bun test /test-sandbox/smoke.test.ts"],
        cwd="/test-sandbox",
        capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, (
        f"bun test smoke suite failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")