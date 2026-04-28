"""
Task: opencode-effect-account-branded-types
Repo: anomalyco/opencode @ 2aae0d3493ac51aa2fd3929c6db0814ab795b04b
PR:   17072

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"


def _run_bun_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp TypeScript file and run it with bun."""
    script_path = Path(PKG) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=PKG,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_branded_types_exported():
    """RefreshToken, DeviceCode, UserCode branded types must be exported from schema."""
    result = _run_bun_ts("""
import { RefreshToken, DeviceCode, UserCode } from "./src/account/schema"
const rt = RefreshToken.make("test-token")
const dc = DeviceCode.make("test-code")
const uc = UserCode.make("test-user")
if (!rt || !dc || !uc) throw new Error("Branded type construction failed")
console.log("ALL_BRANDED_TYPES_OK")
""")
    assert result.returncode == 0, f"Branded types not available: {result.stderr}"
    assert "ALL_BRANDED_TYPES_OK" in result.stdout


def test_schema_class_in_service():
    """service.ts must use Schema.Class for complex data types, not Schema.Struct."""
    service = Path(f"{PKG}/src/account/service.ts")
    content = service.read_text()
    # PR converts Schema.Struct to Schema.Class for multiple data types
    schema_class_count = content.count("extends Schema.Class")
    assert schema_class_count >= 5, (
        f"Expected 5+ Schema.Class usages in service.ts, found {schema_class_count}"
    )
    # Schema.Struct should no longer be used in service.ts
    assert "Schema.Struct" not in content, (
        "service.ts should use Schema.Class, not Schema.Struct"
    )


def test_login_uses_duration():
    """Login schema must use Duration fields and branded types for device/user codes."""
    schema = Path(f"{PKG}/src/account/schema.ts")
    content = schema.read_text()
    # Login should use Schema.Duration instead of Schema.Number for time fields
    assert "Schema.Duration" in content, (
        "schema.ts should use Schema.Duration for time fields"
    )
    # Branded types should be defined
    assert "RefreshToken" in content, "RefreshToken branded type should be defined"
    assert "DeviceCode" in content, "DeviceCode branded type should be defined"
    assert "UserCode" in content, "UserCode branded type should be defined"


def test_repo_uses_layer_effect():
    """AccountRepo must use Layer.effect with Effect.gen and AccountRepo.of."""
    repo = Path(f"{PKG}/src/account/repo.ts")
    content = repo.read_text()
    assert "Layer.effect" in content, (
        "repo.ts should use Layer.effect (not Layer.succeed)"
    )
    assert "AccountRepo.of" in content, (
        "repo.ts should return AccountRepo.of({...})"
    )
    assert "Effect.gen" in content, (
        "repo.ts should use Effect.gen for service composition"
    )
    assert "export namespace AccountRepo" in content, (
        "AccountRepo should export a Service namespace"
    )


# ---------------------------------------------------------------------------
# Config / instruction file update checks
# ---------------------------------------------------------------------------


def test_agents_md_has_effect_guide():
    """packages/opencode/AGENTS.md must include an Effect guide section."""
    agents_md = Path(f"{PKG}/AGENTS.md")
    content = agents_md.read_text()
    assert "Effect guide" in content, (
        "AGENTS.md should have an Effect guide section"
    )
    # Check for key subsections documenting different patterns
    lower = content.lower()
    assert "schema" in lower, "Effect guide should document Schema patterns"
    assert "service" in lower, "Effect guide should document Service patterns"
    assert "error" in lower, "Effect guide should document Error patterns"


def test_agents_md_branded_schema_rule():
    """AGENTS.md must document branded schema (Schema.brand) usage."""
    agents_md = Path(f"{PKG}/AGENTS.md")
    content = agents_md.read_text()
    assert "Schema.brand" in content, (
        "AGENTS.md should document Schema.brand for single-value types"
    )
    assert "branded" in content.lower(), (
        "AGENTS.md should mention branded schemas"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks must pass on base and after fix
# ---------------------------------------------------------------------------


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed: {r.stderr[-500:]}"


def test_repo_unit_tests_keybind():
    """Keybind unit tests pass (pass_to_pass) - fast, reliable subset."""
    r = subprocess.run(
        ["bun", "test", "test/keybind.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"Keybind tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_account_repo():
    """Account repo unit tests pass (pass_to_pass) - tests account database operations."""
    r = subprocess.run(
        ["bun", "test", "test/account/repo.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"Account repo tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_account_service():
    """Account service unit tests pass (pass_to_pass) - tests account service layer."""
    r = subprocess.run(
        ["bun", "test", "test/account/service.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"Account service tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_storage_db():
    """Storage/db unit tests pass (pass_to_pass) - tests database layer used by account module."""
    r = subprocess.run(
        ["bun", "test", "test/storage/db.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"Storage db tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_auth():
    """Auth unit tests pass (pass_to_pass) - tests auth normalization utilities."""
    r = subprocess.run(
        ["bun", "test", "test/auth/auth.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"Auth tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_acp_agent_interface():
    """ACP agent interface tests pass (pass_to_pass) - tests agent SDK compliance."""
    r = subprocess.run(
        ["bun", "test", "test/acp/agent-interface.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=PKG,
    )
    assert r.returncode == 0, f"ACP agent interface tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_acp_event_subscription():
    """ACP event subscription tests pass (pass_to_pass) - tests agent event handling."""
    r = subprocess.run(
        ["bun", "test", "test/acp/event-subscription.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=PKG,
    )
    assert r.returncode == 0, f"ACP event subscription tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_cli_github_remote():
    """CLI github remote tests pass (pass_to_pass) - tests CLI utility functions."""
    r = subprocess.run(
        ["bun", "test", "test/cli/github-remote.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"CLI github remote tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_cli_github_action():
    """CLI github action tests pass (pass_to_pass) - tests GitHub action utilities."""
    r = subprocess.run(
        ["bun", "test", "test/cli/github-action.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"CLI github action tests failed: {r.stderr[-500:]}"


def test_repo_unit_tests_cli_import():
    """CLI import tests pass (pass_to_pass) - tests share URL/import utilities."""
    r = subprocess.run(
        ["bun", "test", "test/cli/import.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=PKG,
    )
    assert r.returncode == 0, f"CLI import tests failed: {r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — existing behavior maintained
# ---------------------------------------------------------------------------


def test_drizzle_snake_case():
    """Drizzle schema field names use snake_case per root AGENTS.md convention."""
    sql_schema = Path(f"{PKG}/src/account/account.sql.ts")
    content = sql_schema.read_text()
    # Verify snake_case field names are used in Drizzle table definitions
    assert "active_account_id" in content
    assert "active_org_id" in content
    assert "access_token" in content
    assert "refresh_token" in content
    assert "token_expiry" in content

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_prepare():
    """pass_to_pass | CI job 'build-tauri' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")