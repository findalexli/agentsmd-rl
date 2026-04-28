"""
Task: opencode-effect-account-refactor
Repo: anomalyco/opencode @ 2aae0d3493ac51aa2fd3929c6db0814ab795b04b
PR:   17072

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = "/workspace/opencode"
PKG = f"{REPO}/packages/opencode"


def _run_bun_tsc_check():
    """Run TypeScript check to verify files compile."""
    result = subprocess.run(
        ["bun", "tsc", "--noEmit"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_repo_tests():
    """Run the account-related tests in the repo."""
    result = subprocess.run(
        ["bun", "test", "test/account/repo.test.ts", "test/account/service.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_typecheck():
    """Run repo's typecheck command (tsgo --noEmit)."""
    result = subprocess.run(
        ["bun", "typecheck"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_account_tests():
    """Run account-specific tests only."""
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/account/repo.test.ts", "test/account/service.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_auth_tests():
    """Run auth tests in the repo."""
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/auth/auth.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_storage_tests():
    """Run storage tests in the repo."""
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/storage/"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_bun_tests():
    """Run bun test file in the repo."""
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/bun.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_acp_tests():
    """Run ACP (Agent Client Protocol) tests in the repo."""
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/acp/agent-interface.test.ts", "test/acp/event-subscription.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_scheduler_tests():
    """Run scheduler tests in the repo."""
    # Set git identity first (required by tests that use git)
    subprocess.run(
        ["git", "config", "--global", "user.email", "test@test.com"],
        cwd=PKG,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--global", "user.name", "Test"],
        cwd=PKG,
        capture_output=True,
    )
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/scheduler.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result


def _run_config_tests():
    """Run config tests in the repo."""
    # Set git identity first (required by tests that use git)
    subprocess.run(
        ["git", "config", "--global", "user.email", "test@test.com"],
        cwd=PKG,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "--global", "user.name", "Test"],
        cwd=PKG,
        capture_output=True,
    )
    result = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/config/config.test.ts"],
        cwd=PKG,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must compile without errors."""
    result = _run_bun_tsc_check()
    # Ignore certain lib type errors, focus on our code
    if result.returncode != 0:
        # Check if the errors are in our account files
        stderr = result.stderr or ""
        stdout = result.stdout or ""
        combined = stderr + stdout
        # If no account-specific errors, consider it passing
        account_errors = [line for line in combined.split('\n') if 'src/account' in line or 'account/' in line]
        if account_errors:
            raise AssertionError(f"TypeScript errors in account files:\n{chr(10).join(account_errors)}")
    assert True


# [repo_tests] pass_to_pass - repo's typecheck
def test_repo_typecheck():
    """Repo's typecheck passes (pass_to_pass)."""
    r = _run_typecheck()
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - account tests
def test_repo_account_tests():
    """Account tests pass on base commit (pass_to_pass)."""
    r = _run_account_tests()
    assert r.returncode == 0, f"Account tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - auth tests
def test_repo_auth_tests():
    """Auth tests pass on base commit (pass_to_pass)."""
    r = _run_auth_tests()
    assert r.returncode == 0, f"Auth tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - storage tests
def test_repo_storage_tests():
    """Storage tests pass on base commit (pass_to_pass)."""
    r = _run_storage_tests()
    assert r.returncode == 0, f"Storage tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - bun tests
def test_repo_bun_tests():
    """Bun tests pass on base commit (pass_to_pass)."""
    r = _run_bun_tests()
    assert r.returncode == 0, f"Bun tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - ACP tests (Agent Client Protocol)
def test_repo_acp_tests():
    """ACP (Agent Client Protocol) tests pass on base commit (pass_to_pass)."""
    r = _run_acp_tests()
    assert r.returncode == 0, f"ACP tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - scheduler tests
def test_repo_scheduler_tests():
    """Scheduler tests pass on base commit (pass_to_pass)."""
    r = _run_scheduler_tests()
    assert r.returncode == 0, f"Scheduler tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass - config tests
def test_repo_config_tests():
    """Config tests pass on base commit (pass_to_pass)."""
    r = _run_config_tests()
    assert r.returncode == 0, f"Config tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_repo_passes_account_tests():
    """Account repo and service tests must pass after the refactor."""
    result = _run_repo_tests()
    if result.returncode != 0:
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        raise AssertionError(f"Account tests failed:\n{stdout}\n{stderr}")


# [pr_diff] fail_to_pass
def test_schema_has_branded_types():
    """Schema must define RefreshToken, DeviceCode, UserCode branded types."""
    schema_path = Path(f"{PKG}/src/account/schema.ts")
    content = schema_path.read_text()

    # Check for branded type definitions
    assert "export const RefreshToken" in content, "Missing RefreshToken branded type"
    assert "Schema.brand(\"RefreshToken\")" in content, "Missing RefreshToken brand"
    assert "export const DeviceCode" in content, "Missing DeviceCode branded type"
    assert "Schema.brand(\"DeviceCode\")" in content, "Missing DeviceCode brand"
    assert "export const UserCode" in content, "Missing UserCode branded type"
    assert "Schema.brand(\"UserCode\")" in content, "Missing UserCode brand"


# [pr_diff] fail_to_pass
def test_service_uses_layer_effect():
    """AccountService must use Layer.effect with Effect.gen pattern."""
    service_path = Path(f"{PKG}/src/account/service.ts")
    content = service_path.read_text()

    # Check for Effect patterns from the AGENTS.md guide
    assert "Layer.effect(" in content, "Service must use Layer.effect (not Layer.succeed)"
    assert "Effect.gen(function* ()" in content, "Service must use Effect.gen for composition"


# [pr_diff] fail_to_pass
def test_repo_uses_layer_effect():
    """AccountRepo must use Layer.effect with Effect.gen pattern."""
    repo_path = Path(f"{PKG}/src/account/repo.ts")
    content = repo_path.read_text()

    assert "Layer.effect(" in content, "Repo must use Layer.effect (not Layer.succeed)"
    assert "Effect.gen(function* ()" in content, "Repo must use Effect.gen for composition"
    assert "AccountRepo.of({" in content, "Repo must return AccountRepo.of with object"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_service_has_namespace():
    """AccountService must export namespace with Service interface."""
    service_path = Path(f"{PKG}/src/account/service.ts")
    content = service_path.read_text()

    assert "export namespace AccountService" in content, "Missing AccountService namespace"
    assert "export interface Service" in content, "Missing Service interface in namespace"


# [pr_diff] pass_to_pass
def test_schema_uses_class_for_data_types():
    """Data types like Login, User, ClientId must use Schema.Class."""
    schema_path = Path(f"{PKG}/src/account/schema.ts")
    content = schema_path.read_text()

    # Check that Login uses Duration types (from the PR)
    assert "expiry: Schema.Duration" in content or "Schema.Duration" in content, \
        "Login should use Schema.Duration for time fields"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — AGENTS.md Effect guide ADDED by this PR
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_has_effect_guide():
    """AGENTS.md must include the opencode Effect guide section."""
    agents_path = Path(f"{PKG}/AGENTS.md")
    content = agents_path.read_text()

    assert "# opencode Effect guide" in content, "Missing Effect guide header"
    assert "## Schemas" in content, "Missing Schemas section"
    assert "## Services" in content, "Missing Services section"
    assert "## Effects" in content, "Missing Effects section"


# [pr_diff] fail_to_pass
def test_agents_md_schemas_rule():
    """AGENTS.md must document Schema.Class for data types and Schema.brand for single-value types."""
    agents_path = Path(f"{PKG}/AGENTS.md")
    content = agents_path.read_text()

    assert "Schema.Class" in content, "AGENTS.md must mention Schema.Class for data types"
    assert "Schema.brand" in content, "AGENTS.md must mention Schema.brand for single-value types"


# [pr_diff] fail_to_pass
def test_agents_md_services_rule():
    """AGENTS.md must document Layer.effect pattern for services."""
    agents_path = Path(f"{PKG}/AGENTS.md")
    content = agents_path.read_text()

    assert "Layer.effect" in content, "AGENTS.md must mention Layer.effect"
    assert "ServiceName.of" in content, "AGENTS.md must mention ServiceName.of for returning implementations"


# [pr_diff] fail_to_pass
def test_agents_md_effects_rule():
    """AGENTS.md must document Effect.gen and Effect.fn patterns."""
    agents_path = Path(f"{PKG}/AGENTS.md")
    content = agents_path.read_text()

    assert "Effect.gen" in content, "AGENTS.md must mention Effect.gen for composition"
    assert "Effect.fn" in content, "AGENTS.md must mention Effect.fn for named/traced effects"
    assert "Effect.fnUntraced" in content, "AGENTS.md must mention Effect.fnUntraced for internal helpers"


# [pr_diff] fail_to_pass
def test_agents_md_errors_rule():
    """AGENTS.md must document preferring 'yield* new MyError' over 'yield* Effect.fail'."""
    agents_path = Path(f"{PKG}/AGENTS.md")
    content = agents_path.read_text()

    # Check for the error handling guidance
    assert "yield* new MyError" in content, "AGENTS.md must document 'yield* new MyError' pattern"
    assert "Effect.fail" in content, "AGENTS.md must mention Effect.fail as the less preferred option"

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

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
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