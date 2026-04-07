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
    match = re.search(r'toolResultMaxLength.*?\.default\((\d+)\)', src)
    assert match, "Could not find toolResultMaxLength default in chatConfig.ts"
    default_val = int(match.group(1))
    assert default_val == 25000, f"Expected default 25000, got {default_val}"


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
    assert "update the `tag` field" in content, \
        "Must describe updating the tag field in _journal.json"


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
