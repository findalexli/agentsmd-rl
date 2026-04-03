"""
Task: posthog-featmcp-allow-listing-tools-by
Repo: PostHog/posthog @ 6ffa23dc367bd7935376dde246fdd7b986ebf8b8
PR:   53158

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
MCP_DIR = f"{REPO}/services/mcp"

# Custom vitest test file written once, shared by behavioral tests
_CUSTOM_TEST_FILE = Path(f"{MCP_DIR}/tests/unit/_custom_tools_filter.test.ts")

_CUSTOM_TEST_CODE = """\
import { describe, it, expect } from 'vitest'
import { getToolsForFeatures } from '@/tools/toolDefinitions'

describe('Custom: tools name filtering', () => {
    it('filters_by_exact_tool_names', () => {
        const result = getToolsForFeatures({ tools: ['dashboard-get', 'dashboard-create'] })
        expect(result).toContain('dashboard-get')
        expect(result).toContain('dashboard-create')
        expect(result).toHaveLength(2)
    })

    it('composes_features_and_tools_as_union', () => {
        const result = getToolsForFeatures({ features: ['flags'], tools: ['dashboard-get'] })
        // Should include flag tools
        expect(result).toContain('feature-flag-get-all')
        // Should include the explicitly named tool from a different category
        expect(result).toContain('dashboard-get')
        // Should NOT include unrelated tools
        expect(result).not.toContain('insights-get-all')
    })

    it('returns_empty_for_nonexistent_tool', () => {
        const result = getToolsForFeatures({ tools: ['nonexistent-tool-xyz-999'] })
        expect(result).toEqual([])
    })
})
"""


def _ensure_custom_test_file():
    """Write the custom vitest test file if not already present."""
    if not _CUSTOM_TEST_FILE.exists():
        _CUSTOM_TEST_FILE.write_text(_CUSTOM_TEST_CODE)


def _run_vitest(test_file: str, test_pattern: str | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run vitest on a specific test file, optionally filtering by test name."""
    cmd = ["npx", "vitest", "run", test_file, "--reporter=verbose"]
    if test_pattern:
        cmd.extend(["-t", test_pattern])
    return subprocess.run(cmd, cwd=MCP_DIR, capture_output=True, timeout=timeout)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_exports():
    """getToolsForFeatures is exported and has filtering logic."""
    src = Path(f"{MCP_DIR}/src/tools/toolDefinitions.ts").read_text()
    assert "export function getToolsForFeatures" in src, \
        "getToolsForFeatures must be exported from toolDefinitions.ts"
    assert "entries.filter(" in src, \
        "getToolsForFeatures must filter tool entries"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via vitest
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tools_filter_by_name():
    """getToolsForFeatures({tools: [...]}) returns only named tools."""
    _ensure_custom_test_file()
    r = _run_vitest(
        "tests/unit/_custom_tools_filter.test.ts",
        "filters_by_exact_tool_names",
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Tools filter-by-name test failed (rc={r.returncode}):\n"
        f"{stdout[-2000:]}\n{stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_tools_union_with_features():
    """features + tools compose as OR union."""
    _ensure_custom_test_file()
    r = _run_vitest(
        "tests/unit/_custom_tools_filter.test.ts",
        "composes_features_and_tools_as_union",
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Tools union test failed (rc={r.returncode}):\n"
        f"{stdout[-2000:]}\n{stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_nonexistent_tool_returns_empty():
    """Nonexistent tool name yields empty result when tools param is set."""
    _ensure_custom_test_file()
    r = _run_vitest(
        "tests/unit/_custom_tools_filter.test.ts",
        "returns_empty_for_nonexistent_tool",
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Nonexistent tool test failed (rc={r.returncode}):\n"
        f"{stdout[-2000:]}\n{stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config file update (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention the tools query parameter
    assert "tools" in content_lower and "query parameter" in content_lower, \
        "README should document the 'tools' query parameter"

    # Must explain the union/OR composition with features
    assert "union" in content_lower or (" or " in content_lower and "feature" in content_lower), \
        "README should explain that features and tools compose as a union (OR)"

    # Must include a usage example with the tools param
    assert "?tools=" in content or "&tools=" in content, \
        "README should include a URL example with ?tools= parameter"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — existing feature filtering still works
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_feature_filtering():
    """Existing feature-based filtering tests still pass."""
    r = _run_vitest(
        "tests/unit/tool-filtering.test.ts",
        "Tool Filtering - Features",
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    assert r.returncode == 0, (
        f"Existing feature filtering tests failed (rc={r.returncode}):\n"
        f"{stdout[-2000:]}\n{stderr[-2000:]}"
    )
