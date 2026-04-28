"""
Task: supabase-chore-studio-update-cursor-rule-queryoptions
Repo: supabase/supabase @ 11d4da6c4b6d282c1d829a4786a342468472a698
PR:   42446

Refactor third-party auth integrations query from useXQuery hook pattern to
queryOptions factory pattern, and update the Cursor rule to recommend it.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_query_file_exports_query_options():
    """integrations-query.ts must export thirdPartyAuthIntegrationsQueryOptions
    using queryOptions from @tanstack/react-query (not useQuery hook pattern)."""
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(
    'apps/studio/data/third-party-auth/integrations-query.ts', 'utf8'
);
const hasExport = /export\s+const\s+thirdPartyAuthIntegrationsQueryOptions/.test(content);
const importsQueryOptions = /import\s*\{[^}]*queryOptions[^}]*\}\s*from\s*['"]@tanstack\/react-query['"]/.test(content);
const result = { hasExport, importsQueryOptions };
console.log(JSON.stringify(result));
if (!hasExport || !importsQueryOptions) process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Query options export check failed: {r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasExport"], "Must export thirdPartyAuthIntegrationsQueryOptions"
    assert data["importsQueryOptions"], "Must import queryOptions from @tanstack/react-query"


# [pr_diff] fail_to_pass
def test_get_function_is_private():
    """getThirdPartyAuthIntegrations must NOT be exported (private fetch fn)."""
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(
    'apps/studio/data/third-party-auth/integrations-query.ts', 'utf8'
);
// Function should exist but not be exported
const hasFunction = /async function getThirdPartyAuthIntegrations/.test(content);
const isExported = /export\s+(async\s+)?function\s+getThirdPartyAuthIntegrations/.test(content);
console.log(JSON.stringify({ hasFunction, isExported }));
if (!hasFunction || isExported) process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Private function check failed: {r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["hasFunction"], "getThirdPartyAuthIntegrations function must exist"
    assert not data["isExported"], "getThirdPartyAuthIntegrations must NOT be exported"


# [pr_diff] fail_to_pass
def test_component_uses_query_options_pattern():
    """ThirdPartyAuthForm must use thirdPartyAuthIntegrationsQueryOptions
    with useQuery, not the old useThirdPartyAuthIntegrationsQuery hook."""
    script = r"""
const fs = require('fs');
const content = fs.readFileSync(
    'apps/studio/components/interfaces/Auth/ThirdPartyAuthForm/index.tsx', 'utf8'
);
const usesNewPattern = content.includes('thirdPartyAuthIntegrationsQueryOptions');
const usesOldHook = content.includes('useThirdPartyAuthIntegrationsQuery');
const importsUseQuery = /import\s*\{[^}]*useQuery[^}]*\}\s*from\s*['"]@tanstack\/react-query['"]/.test(content);
console.log(JSON.stringify({ usesNewPattern, usesOldHook, importsUseQuery }));
if (!usesNewPattern || usesOldHook || !importsUseQuery) process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Component pattern check failed: {r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["usesNewPattern"], "Component must use thirdPartyAuthIntegrationsQueryOptions"
    assert not data["usesOldHook"], "Component must NOT use useThirdPartyAuthIntegrationsQuery"
    assert data["importsUseQuery"], "Component must import useQuery from @tanstack/react-query"


# [pr_diff] fail_to_pass
def test_deprecated_custom_mutation_type():
    """UseCustomMutationOptions in react-query.ts must have @deprecated comment."""
    script = r"""
const fs = require('fs');
const content = fs.readFileSync('apps/studio/types/react-query.ts', 'utf8');
const lines = content.split('\n');
let typeExists = false;
let foundDeprecated = false;
for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('UseCustomMutationOptions') && lines[i].includes('export type')) {
        typeExists = true;
        const context = lines.slice(Math.max(0, i - 3), i + 1).join('\n');
        if (context.includes('@deprecated')) {
            foundDeprecated = true;
        }
        break;
    }
}
console.log(JSON.stringify({ typeExists, foundDeprecated }));
if (!typeExists || !foundDeprecated) process.exit(1);
"""
    r = subprocess.run(
        ["node", "-e", script], cwd=REPO,
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Deprecated type check failed: {r.stdout}\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["typeExists"], "UseCustomMutationOptions type must still be exported"
    assert data["foundDeprecated"], "UseCustomMutationOptions must have a @deprecated comment"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/instruction file update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rule_md_recommends_query_options():
    """Cursor rule RULE.md must recommend queryOptions pattern, not useXQuery hooks."""
    content = Path(REPO, ".cursor/rules/studio/queries/RULE.md").read_text()
    # Section heading must say "query options", not "query hook"
    assert re.search(r"##\s+Write query options", content), (
        "RULE.md must have a '## Write query options' section heading"
    )
    # Must mention xQueryOptions as the export pattern
    assert "xQueryOptions" in content, (
        "RULE.md must reference xQueryOptions as the recommended export name"
    )
    # getX function should be described as private
    assert "private" in content.lower() or "should NOT be exported" in content, (
        "RULE.md must describe getX as a private/non-exported function"
    )


# [pr_diff] fail_to_pass
def test_rule_md_documents_imperative_fetching():
    """Cursor rule must document imperative fetching with queryClient.fetchQuery()."""
    content = Path(REPO, ".cursor/rules/studio/queries/RULE.md").read_text()
    assert "fetchQuery" in content, (
        "RULE.md must mention fetchQuery for imperative fetching"
    )
    assert re.search(r"[Ii]mperative\s+fetch", content), (
        "RULE.md must have a section about imperative fetching"
    )
    assert "queryClient" in content, (
        "RULE.md must reference queryClient for imperative use"
    )


# [pr_diff] fail_to_pass
def test_rule_md_documents_component_usage_with_query_options():
    """Cursor rule must show how to use query options in components with useQuery."""
    content = Path(REPO, ".cursor/rules/studio/queries/RULE.md").read_text()
    # Must have a section about using query options in components
    assert re.search(r"[Uu]sing query options in components", content), (
        "RULE.md must have a section on using query options in components"
    )
    # Must show useQuery with xQueryOptions
    assert "useQuery" in content, "RULE.md must reference useQuery"
    # The template should import from @tanstack/react-query
    assert "from '@tanstack/react-query'" in content or \
           'from "@tanstack/react-query"' in content, (
        "RULE.md template must import from @tanstack/react-query"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — existing rules that must remain satisfied
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .cursor/rules/studio/queries/RULE.md:46 @ 11d4da6c
def test_query_gates_with_enabled():
    """Query function must gate with `enabled` (existing Cursor rule requirement)."""
    content = Path(
        REPO, "apps/studio/data/third-party-auth/integrations-query.ts"
    ).read_text()
    assert "enabled" in content, (
        "Query must use `enabled` gating per Cursor rule requirement"
    )
    # Verify enabled is used in the queryOptions return value
    assert re.search(r"enabled\s*:", content), (
        "Query options must include an `enabled:` property"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI tests that must pass at base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Studio unit tests pass (pass_to_pass)."""
    # First install dependencies at root
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    # Run tests
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/supabase/apps/studio && NODE_OPTIONS='--max-old-space-size=3072' pnpm run test:ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Studio ESLint passes (pass_to_pass)."""
    # First install dependencies at root (idempotent if already installed)
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    # Run lint
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/supabase/apps/studio && pnpm run lint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_ratchet():
    """Studio ESLint ratchet check passes (pass_to_pass)."""
    # First install dependencies at root (idempotent if already installed)
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    # Run lint ratchet
    r = subprocess.run(
        ["bash", "-c", "pnpm --filter studio run lint:ratchet"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint ratchet failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo Prettier formatting check passes (pass_to_pass)."""
    # First install dependencies at root (idempotent if already installed)
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    # Run prettier check
    r = subprocess.run(
        ["bash", "-c", "pnpm test:prettier"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run Tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:ci'], cwd=os.path.join(REPO, './apps/studio'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")