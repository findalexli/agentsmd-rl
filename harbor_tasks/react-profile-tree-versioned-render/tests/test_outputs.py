"""
Task: react-profile-tree-versioned-render
Repo: facebook/react @ 2a879cdc95228b1b3b4cdc81cfc04599716b5562

Migrate profilingCommitTreeBuilder-test.js from the deprecated
getLegacyRenderImplementation/getModernRenderImplementation helpers to the
unified getVersionedRenderImplementation, removing duplicated test cases.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
TEST_FILE = REPO + "/packages/react-devtools-shared/src/__tests__/profilingCommitTreeBuilder-test.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Test file must parse as valid JavaScript."""
    r = subprocess.run(["node", "--check", TEST_FILE], capture_output=True, timeout=30)
    assert r.returncode == 0, (
        f"Syntax error in {TEST_FILE}:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core migration checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_versioned_render_imported():
    """Test file imports getVersionedRenderImplementation from utils."""
    content = Path(TEST_FILE).read_text()
    # Must import the unified helper
    assert "getVersionedRenderImplementation" in content, (
        "Missing import of getVersionedRenderImplementation — old API not replaced"
    )
    # Verify it's a proper import statement, not just a comment
    assert re.search(
        r"import\s*\{[^}]*getVersionedRenderImplementation[^}]*\}\s*from\s+['\"]\.\/utils['\"]",
        content,
    ), "getVersionedRenderImplementation must be imported from './utils'"


# [pr_diff] fail_to_pass
def test_old_render_helpers_removed():
    """Deprecated getLegacyRenderImplementation and getModernRenderImplementation are gone."""
    content = Path(TEST_FILE).read_text()
    assert "getLegacyRenderImplementation" not in content, (
        "getLegacyRenderImplementation should be removed"
    )
    assert "getModernRenderImplementation" not in content, (
        "getModernRenderImplementation should be removed"
    )


# [pr_diff] fail_to_pass
def test_no_legacy_modern_render_vars():
    """Variables legacyRender and modernRender must not appear in the file."""
    content = Path(TEST_FILE).read_text()
    assert "legacyRender" not in content, (
        "legacyRender variable should be removed"
    )
    assert "modernRender" not in content, (
        "modernRender variable should be removed"
    )


# [pr_diff] fail_to_pass
def test_duplicate_tests_removed():
    """Duplicate legacy/createRoot test variants are consolidated — test count reduced from 6 to 3."""
    content = Path(TEST_FILE).read_text()
    # Base has 6 it('should...) entries (3 legacy + 3 createRoot); fix merges to 3
    test_cases = re.findall(r"\bit\s*\(\s*['\"]should", content)
    assert len(test_cases) <= 4, (
        f"Expected ≤4 test cases after deduplication, found {len(test_cases)}. "
        "Duplicate legacy/createRoot variants may not have been removed."
    )
    assert len(test_cases) >= 2, (
        f"Expected at least 2 test cases, found {len(test_cases)}. "
        "Tests may have been over-removed."
    )


# [pr_diff] fail_to_pass
def test_version_upper_bound_annotation_removed():
    """Version upper bound annotations (@reactVersion <= 18.2) must be removed."""
    content = Path(TEST_FILE).read_text()
    assert "@reactVersion <= 18.2" not in content, (
        "Upper-bound version annotation '@reactVersion <= 18.2' should be removed "
        "after merging legacy/createRoot variants into versioned render"
    )


# [pr_diff] fail_to_pass
def test_unified_render_used_in_tests():
    """The unified render() function is actually called in test bodies (not just imported)."""
    content = Path(TEST_FILE).read_text()
    # Must destructure render from getVersionedRenderImplementation
    assert re.search(r"const\s*\{[^}]*render[^}]*\}\s*=\s*getVersionedRenderImplementation\(\)", content), (
        "Must destructure render from getVersionedRenderImplementation()"
    )
    # render() must be called in test bodies (not just declared)
    render_calls = re.findall(r"\brender\s*\(<", content)
    assert len(render_calls) >= 3, (
        f"Expected render() called at least 3 times in tests, found {len(render_calls)}. "
        "The unified render must replace all legacyRender/modernRender calls."
    )


# ---------------------------------------------------------------------------
# Behavioral (pr_diff) — actually run the test suite
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jest_suite_passes():
    """The profilingCommitTreeBuilder test suite passes with the migrated code."""
    r = subprocess.run(
        [
            "yarn", "test", "--no-watchman", "--silent",
            "profilingCommitTreeBuilder",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    stdout = r.stdout.decode(errors="replace")
    stderr = r.stderr.decode(errors="replace")
    # Jest exits 0 on pass; any test failure or crash = non-zero
    assert r.returncode == 0, (
        f"Jest test suite failed (exit {r.returncode}):\n"
        f"STDOUT:\n{stdout[-2000:]}\n"
        f"STDERR:\n{stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Test file has substantial content — render function is actually invoked in tests."""
    content = Path(TEST_FILE).read_text()
    # Verify the file has real test content, not just an empty skeleton
    assert len(content) > 1500, "File appears too short — may be a stub"
    assert "describe(" in content, "Missing describe() block"
    assert "expect(" in content, "Missing expect() assertions"
    # Must have toMatchInlineSnapshot assertions (core of these tests)
    snapshot_count = len(re.findall(r"toMatchInlineSnapshot", content))
    assert snapshot_count >= 4, (
        f"Expected at least 4 inline snapshot assertions, found {snapshot_count}"
    )
