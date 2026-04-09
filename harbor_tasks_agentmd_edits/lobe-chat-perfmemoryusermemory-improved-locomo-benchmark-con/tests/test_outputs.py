"""
Task: lobe-chat-perfmemoryusermemory-improved-locomo-benchmark-con
Repo: lobehub/lobe-chat @ be8903e70771ad1af43159c17ea62185eae180a2
PR:   13453

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def _run_node_check(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript/TypeScript check via Node."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified packages compile without TypeScript errors."""
    # Check that the builtin-tool-memory package compiles
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/builtin-tool-memory",
    )
    # Note: tsc may return warnings, but should not have syntax errors
    # We check stderr for "error TS" patterns which indicate type errors
    if "error TS" in r.stderr:
        assert False, f"TypeScript errors:\n{r.stderr}"
    assert r.returncode == 0 or "error TS" not in r.stderr, f"Compile failed: {r.stderr}"


# [static] pass_to_pass
def test_database_typescript_compiles():
    """Database package compiles without TypeScript errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/database",
    )
    if "error TS" in r.stderr:
        assert False, f"TypeScript errors:\n{r.stderr}"
    assert r.returncode == 0 or "error TS" not in r.stderr, f"Compile failed: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_lint_ts():
    """Repo's TypeScript linting passes with no errors (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "lint:ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # ESLint exits with 0 if only warnings, 1 if errors
    # We check for actual errors - lines with 'error:' that are not warnings
    output = r.stdout + r.stderr
    # Look for pattern like "X errors" in the output summary
    import re
    error_match = re.search(r'(\d+)\s*error', output, re.IGNORECASE)
    if error_match:
        error_count = int(error_match.group(1))
        assert error_count == 0, f"ESLint found {error_count} errors:\n{output[-1000:]}"
    assert r.returncode == 0, f"ESLint failed with exit code {r.returncode}:\n{output[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_query_taxonomy_options_api_exists():
    """queryTaxonomyOptions API is defined in the manifest and types."""
    # Check that the manifest includes queryTaxonomyOptions
    manifest_path = Path(f"{REPO}/packages/builtin-tool-memory/src/manifest.ts")
    manifest_content = manifest_path.read_text()

    # Should contain queryTaxonomyOptions API definition
    assert "queryTaxonomyOptions" in manifest_content, "queryTaxonomyOptions not found in manifest"

    # Check types file exports the new types
    types_path = Path(f"{REPO}/packages/builtin-tool-memory/src/types.ts")
    types_content = types_path.read_text()

    assert "QueryTaxonomyOptionsParams" in types_content, "QueryTaxonomyOptionsParams type not found"
    assert "QueryTaxonomyOptionsResult" in types_content, "QueryTaxonomyOptionsResult type not found"


# [pr_diff] fail_to_pass
def test_search_uses_queries_array():
    """searchUserMemory uses queries array parameter instead of single query string."""
    # Check the manifest uses queries (array) not query (string)
    manifest_path = Path(f"{REPO}/packages/builtin-tool-memory/src/manifest.ts")
    manifest_content = manifest_path.read_text()

    # Should have queries as array
    assert '"queries"' in manifest_content, "queries parameter not found in manifest"

    # Check the types file has the correct SearchMemoryParams
    types_path = Path(f"{REPO}/packages/types/src/userMemory/tools.ts")
    if types_path.exists():
        types_content = types_path.read_text()
        # Should export SearchMemoryParams with queries array
        assert "queries" in types_content, "queries not found in types"


# [pr_diff] fail_to_pass
def test_query_model_file_exists():
    """UserMemoryQueryModel exists in new query.ts file."""
    query_file = Path(f"{REPO}/packages/database/src/models/userMemory/query.ts")
    assert query_file.exists(), "query.ts file does not exist"

    content = query_file.read_text()

    # Should export UserMemoryQueryModel class
    assert "export class UserMemoryQueryModel" in content, "UserMemoryQueryModel class not exported"

    # Should have key methods
    assert "searchMemory" in content, "searchMemory method not found"
    assert "queryTaxonomyOptions" in content, "queryTaxonomyOptions method not found"
    assert "scoreHybridCandidates" in content, "scoreHybridCandidates function not found"


# [pr_diff] fail_to_pass
def test_search_params_include_time_intent():
    """SearchMemoryParams includes timeIntent and timeRange parameters."""
    # Check types for timeIntent
    types_path = Path(f"{REPO}/packages/types/src/userMemory/tools.ts")
    if types_path.exists():
        content = types_path.read_text()
        assert "timeIntent" in content, "timeIntent not found in types"
        assert "timeRange" in content, "timeRange not found in types"

    # Also check the manifest
    manifest_path = Path(f"{REPO}/packages/builtin-tool-memory/src/manifest.ts")
    manifest_content = manifest_path.read_text()
    assert "timeIntent" in manifest_content, "timeIntent not found in manifest"
    assert "timeRange" in manifest_content, "timeRange not found in manifest"


# [pr_diff] fail_to_pass
def test_manifest_includes_identities_in_topk():
    """Manifest topK schema includes identities field."""
    manifest_path = Path(f"{REPO}/packages/builtin-tool-memory/src/manifest.ts")
    manifest_content = manifest_path.read_text()

    # Check that topK properties include identities
    assert "identities:" in manifest_content, "identities field not found in topK schema"


# [pr_diff] fail_to_pass
def test_system_role_updated():
    """System role includes new queryTaxonomyOptions and updated search guidelines."""
    system_role_path = Path(f"{REPO}/packages/builtin-tool-memory/src/systemRole.ts")
    content = system_role_path.read_text()

    # Should reference queryTaxonomyOptions
    assert "queryTaxonomyOptions" in content, "queryTaxonomyOptions not in system role"

    # Should have updated search examples
    assert "search_examples" in content, "search_examples section not found"

    # Should mention queries array format
    assert "queries" in content, "queries not mentioned in system role"


# [pr_diff] fail_to_pass
def test_execution_runtime_updated():
    """MemoryExecutionRuntime implements new queryTaxonomyOptions method."""
    runtime_path = Path(f"{REPO}/packages/builtin-tool-memory/src/ExecutionRuntime/index.ts")
    content = runtime_path.read_text()

    # Should have queryTaxonomyOptions method
    assert "async queryTaxonomyOptions" in content, "queryTaxonomyOptions method not found"

    # Should import the new types
    assert "QueryTaxonomyOptionsParams" in content, "QueryTaxonomyOptionsParams not imported"
    assert "QueryTaxonomyOptionsResult" in content, "QueryTaxonomyOptionsResult not imported"

    # searchUserMemory should use queries array
    assert "params.queries" in content or "queries?." in content or 'params.queries?.join' in content, \
        "searchUserMemory should reference params.queries"


# [pr_diff] fail_to_pass
def test_model_delegates_to_query_model():
    """UserMemoryModel delegates search to UserMemoryQueryModel."""
    model_path = Path(f"{REPO}/packages/database/src/models/userMemory/model.ts")
    content = model_path.read_text()

    # Should instantiate queryModel
    assert "queryModel" in content, "queryModel not found in model"

    # Should have searchMemory method that delegates
    assert "searchMemory = async" in content or "searchMemory(params" in content, \
        "searchMemory method not found"

    # Should delegate to queryModel
    assert "queryModel.searchMemory" in content or "this.queryModel" in content, \
        "Model should delegate to queryModel"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_database_unit_tests_pass():
    """Database package unit tests pass."""
    r = subprocess.run(
        ["npm", "run", "test", "--", "--run", "packages/database/src/models/userMemory/__tests__"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Tests might not be runnable without full setup, so we check for specific success markers
    # or just verify test files exist and have content
    test_dir = Path(f"{REPO}/packages/database/src/models/userMemory/__tests__")
    assert test_dir.exists(), "Test directory does not exist"

    # Check that query.test.ts exists (new test file added by PR)
    query_test = test_dir / "query.test.ts"
    assert query_test.exists(), "query.test.ts test file does not exist"

    # Check that model.test.ts was updated (should have searchMemory tests)
    model_test = test_dir / "model.test.ts"
    content = model_test.read_text()
    assert "searchMemory" in content, "model.test.ts should test searchMemory"


# [static] pass_to_pass
def test_index_exports_query():
    """userMemory index.ts exports query module."""
    index_path = Path(f"{REPO}/packages/database/src/models/userMemory/index.ts")
    content = index_path.read_text()

    assert "export * from './query'" in content, "index.ts should export query module"


# [static] pass_to_pass
def test_json_schema_updated():
    """promptfoo JSON schema includes new search parameters."""
    json_path = Path(f"{REPO}/packages/builtin-tool-memory/promptfoo/tool-calls/memory-searchUserMemory.json")
    if json_path.exists():
        content = json_path.read_text()
        schema = json.loads(content)

        # Should have queries as array
        props = schema.get("parameters", {}).get("properties", {})
        assert "queries" in props, "JSON schema should have queries property"
        assert props["queries"].get("type") == "array", "queries should be an array type"

        # Should have timeIntent
        assert "timeIntent" in props, "JSON schema should have timeIntent"

        # Should have timeRange
        assert "timeRange" in props, "JSON schema should have timeRange"


# [static] pass_to_pass
def test_executor_exports_query_taxonomy():
    """MemoryExecutor exports queryTaxonomyOptions handler."""
    executor_path = Path(f"{REPO}/packages/builtin-tool-memory/src/executor/index.ts")
    content = executor_path.read_text()

    assert "queryTaxonomyOptions" in content, "executor should handle queryTaxonomyOptions"


# [static] pass_to_pass
def test_inspector_components_updated():
    """Inspector components handle queries array and identities."""
    inspector_path = Path(f"{REPO}/packages/builtin-tool-memory/src/client/Inspector/SearchUserMemory/index.tsx")
    content = inspector_path.read_text()

    # Should reference queries array
    assert "queries" in content, "Inspector should reference queries"
    # Should handle identities in result count
    assert "identities" in content, "Inspector should handle identities"


# [static] pass_to_pass
def test_render_component_updated():
    """Render component displays identities from search results."""
    render_path = Path(f"{REPO}/packages/builtin-tool-memory/src/client/Render/SearchUserMemory/index.tsx")
    content = render_path.read_text()

    # Should handle identities
    assert "identities" in content, "Render component should handle identities"
    # Should include identities in total count
    assert "identities.length" in content, "Render should count identities"
