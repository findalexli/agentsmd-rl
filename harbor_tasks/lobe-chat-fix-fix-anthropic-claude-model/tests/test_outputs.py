"""
Task: lobe-chat-fix-fix-anthropic-claude-model
Repo: lobehub/lobe-chat @ 66fba601942579a3c37fe4f0abe92e20de8e1831
PR:   13206

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript script using node --experimental-strip-types."""
    script_path = Path(REPO) / "_eval_tmp.mts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_resolve_max_tokens_normal_models():
    """resolveMaxTokens returns 64000 for non-small-context models (was 8192)."""
    result = _run_ts("""
import { resolveMaxTokens } from './packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts';

const models = [
    'claude-3-5-sonnet-20241022',
    'claude-sonnet-4-20250514',
    'claude-3-5-haiku-20241022',
];

const results = [];
for (const model of models) {
    const actual = await resolveMaxTokens({ max_tokens: undefined, model, providerModels: [] });
    results.push({ model, actual });
}
console.log(JSON.stringify(results));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    for r in data:
        assert r["actual"] == 64000, \
            f"Model {r['model']}: expected 64000, got {r['actual']}"


def test_tool_result_max_length_default_25000():
    """toolResultMaxLength default should be 25000 (was 6000)."""
    src = Path(f"{REPO}/packages/types/src/agent/chatConfig.ts").read_text()
    found = False
    for line in src.splitlines():
        if "toolResultMaxLength" in line:
            assert "25000" in line, f"Expected 25000 near toolResultMaxLength, got: {line.strip()}"
            found = True
            break
    assert found, "Could not find toolResultMaxLength in chatConfig.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config / SKILL.md file update tests
# ---------------------------------------------------------------------------


def test_trpc_router_skill_exists():
    """New .agents/skills/trpc-router/SKILL.md must document router conventions."""
    skill_path = Path(f"{REPO}/.agents/skills/trpc-router/SKILL.md")
    assert skill_path.exists(), "trpc-router SKILL.md must exist"
    content = skill_path.read_text()
    assert "middleware" in content.lower(), "SKILL.md must document middleware pattern"
    assert "procedure" in content.lower(), "SKILL.md must document procedure pattern"
    assert "router" in content.lower(), "SKILL.md must mention router structure"


def test_cli_skill_documents_dev_mode():
    """CLI SKILL.md must have new dev mode and local server connection sections."""
    skill_path = Path(f"{REPO}/.agents/skills/cli/SKILL.md")
    content = skill_path.read_text()
    assert "Running in Dev Mode" in content, \
        "Must have 'Running in Dev Mode' section with LOBEHUB_CLI_HOME isolation"
    assert "Connecting to Local Dev Server" in content, \
        "Must document connecting CLI to local dev server for testing"


def test_db_migrations_skill_has_journal_tag():
    """db-migrations SKILL.md Step 4 must say 'Update Journal Tag' (not 'Regenerate Client')."""
    skill_path = Path(f"{REPO}/.agents/skills/db-migrations/SKILL.md")
    content = skill_path.read_text()
    assert "Step 4: Update Journal Tag" in content, \
        "Step 4 header should be 'Update Journal Tag' not 'Regenerate Client After SQL Edits'"
    assert "tag" in content.lower(), \
        "Must describe updating the tag field in the journal file"
    assert "journal" in content.lower(), \
        "Must mention the migrations metadata journal file"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks (should pass on both base and fixed)
# ---------------------------------------------------------------------------


def test_resolve_max_tokens_small_context_4096():
    """Small-context models (claude-3-opus, claude-3-haiku, claude-v2) still get 4096."""
    result = _run_ts("""
import { resolveMaxTokens } from './packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts';

const models = [
    'claude-3-opus-20240229',
    'claude-3-haiku-20240307',
    'claude-v2',
    'claude-v2:1',
];

const results = [];
for (const model of models) {
    const actual = await resolveMaxTokens({ max_tokens: undefined, model, providerModels: [] });
    results.push({ model, actual });
}
console.log(JSON.stringify(results));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    for r in data:
        assert r["actual"] == 4096, \
            f"Small-context model {r['model']}: expected 4096, got {r['actual']}"


def test_resolve_max_tokens_user_override_takes_priority():
    """User-provided max_tokens takes priority over default."""
    result = _run_ts("""
import { resolveMaxTokens } from './packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts';

const actual = await resolveMaxTokens({
    max_tokens: 9999,
    model: 'claude-3-5-sonnet-20241022',
    providerModels: [],
});
console.log(JSON.stringify({ actual }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["actual"] == 9999, f"User override 9999 should take priority, got {data['actual']}"


def test_resolve_max_tokens_thinking_modes():
    """Thinking enabled returns 32000, adaptive returns 64000."""
    result = _run_ts("""
import { resolveMaxTokens } from './packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts';

const enabled = await resolveMaxTokens({
    max_tokens: undefined,
    model: 'claude-3-5-sonnet-20241022',
    providerModels: [],
    thinking: { type: 'enabled' },
});

const adaptive = await resolveMaxTokens({
    max_tokens: undefined,
    model: 'claude-3-5-sonnet-20241022',
    providerModels: [],
    thinking: { type: 'adaptive' },
});

console.log(JSON.stringify({ enabled, adaptive }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["enabled"] == 32000, f"Thinking enabled: expected 32000, got {data['enabled']}"
    assert data["adaptive"] == 64000, f"Thinking adaptive: expected 64000, got {data['adaptive']}"


def test_resolve_max_tokens_provider_model_default():
    """Provider model maxOutput takes priority when no user override."""
    result = _run_ts("""
import { resolveMaxTokens } from './packages/model-runtime/src/core/anthropicCompatibleFactory/resolveMaxTokens.ts';

const actual = await resolveMaxTokens({
    max_tokens: undefined,
    model: 'claude-3-5-sonnet-20241022',
    providerModels: [{ id: 'claude-3-5-sonnet-20241022', maxOutput: 12345 }],
});
console.log(JSON.stringify({ actual }));
""")
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["actual"] == 12345, f"Provider maxOutput: expected 12345, got {data['actual']}"


# ---------------------------------------------------------------------------
# Repo CI tests — pass_to_pass gates using repo's actual test suite
# ---------------------------------------------------------------------------

def test_repo_model_runtime_tests():
    """Repo's model-runtime package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.20.0 --activate && cd /workspace/lobe-chat && pnpm install --no-frozen-lockfile && cd packages/model-runtime && pnpm test -- --run 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Model-runtime tests failed: {r.stdout[-500:]}"


def test_repo_agent_tools_engine_tests():
    """Repo's AgentToolsEngine tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "corepack enable && corepack prepare pnpm@10.20.0 --activate && cd /workspace/lobe-chat && pnpm install --no-frozen-lockfile && node_modules/.bin/vitest run --silent=passed-only src/server/modules/Mecha/AgentToolsEngine 2>&1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"AgentToolsEngine tests failed: {r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_desktop_app_build_artifact_on_macos():
    """pass_to_pass | CI job 'Build Desktop App' → step 'Build artifact on macOS'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run desktop:package:app'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build artifact on macOS' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_code_quality_check_lint():
    """pass_to_pass | CI job 'Code quality check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_web_app_run_database_migrations():
    """pass_to_pass | CI job 'Test Web App' → step 'Run database migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run db:migrate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run database migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_web_app_build_application():
    """pass_to_pass | CI job 'Test Web App' → step 'Build application'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build application' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_web_app_run_e2e_tests():
    """pass_to_pass | CI job 'Test Web App' → step 'Run E2E tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run e2e'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run E2E tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_disable_LocalSystem_when_no_device_contex():
    """fail_to_pass | PR added test 'should disable LocalSystem when no device context is provided' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when no device context is provided" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when no device context is provided" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when no device context is provided" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when no device context is provided" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable LocalSystem when no device context is provided' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_enable_LocalSystem_when_gateway_configure():
    """fail_to_pass | PR added test 'should enable LocalSystem when gateway configured, device online AND auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable LocalSystem when gateway configured, device online AND auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable LocalSystem when gateway configured, device online AND auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable LocalSystem when gateway configured, device online AND auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable LocalSystem when gateway configured, device online AND auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should enable LocalSystem when gateway configured, device online AND auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_disable_LocalSystem_when_device_online_bu():
    """fail_to_pass | PR added test 'should disable LocalSystem when device online but NOT auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when device online but NOT auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when device online but NOT auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when device online but NOT auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when device online but NOT auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable LocalSystem when device online but NOT auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_disable_LocalSystem_when_gateway_configur():
    """fail_to_pass | PR added test 'should disable LocalSystem when gateway configured but device offline' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when gateway configured but device offline" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when gateway configured but device offline" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when gateway configured but device offline" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when gateway configured but device offline" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable LocalSystem when gateway configured but device offline' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_disable_LocalSystem_when_runtimeMode_is_e():
    """fail_to_pass | PR added test 'should disable LocalSystem when runtimeMode is explicitly set to cloud' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when runtimeMode is explicitly set to cloud" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when runtimeMode is explicitly set to cloud" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when runtimeMode is explicitly set to cloud" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable LocalSystem when runtimeMode is explicitly set to cloud" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable LocalSystem when runtimeMode is explicitly set to cloud' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_enable_RemoteDevice_when_gateway_configur():
    """fail_to_pass | PR added test 'should enable RemoteDevice when gateway configured and no device auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable RemoteDevice when gateway configured and no device auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable RemoteDevice when gateway configured and no device auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable RemoteDevice when gateway configured and no device auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable RemoteDevice when gateway configured and no device auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should enable RemoteDevice when gateway configured and no device auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_disable_RemoteDevice_when_gateway_not_con():
    """fail_to_pass | PR added test 'should disable RemoteDevice when gateway not configured' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when gateway not configured" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when gateway not configured" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when gateway not configured" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when gateway not configured" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable RemoteDevice when gateway not configured' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_disable_RemoteDevice_when_device_is_alrea():
    """fail_to_pass | PR added test 'should disable RemoteDevice when device is already auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when device is already auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when device is already auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when device is already auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should disable RemoteDevice when device is already auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should disable RemoteDevice when device is already auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_enable_only_RemoteDevice_not_LocalSystem_():
    """fail_to_pass | PR added test 'should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should enable only RemoteDevice (not LocalSystem) when device online but not auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_enable_only_LocalSystem_not_RemoteDevice_():
    """fail_to_pass | PR added test 'should enable only LocalSystem (not RemoteDevice) when device auto-activated' in 'src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only LocalSystem (not RemoteDevice) when device auto-activated" 2>&1 || npx vitest run "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only LocalSystem (not RemoteDevice) when device auto-activated" 2>&1 || pnpm jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only LocalSystem (not RemoteDevice) when device auto-activated" 2>&1 || npx jest "src/server/modules/Mecha/AgentToolsEngine/__tests__/index.test.ts" -t "should enable only LocalSystem (not RemoteDevice) when device auto-activated" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should enable only LocalSystem (not RemoteDevice) when device auto-activated' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
