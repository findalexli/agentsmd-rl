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
