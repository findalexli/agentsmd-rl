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
    assert "getVersionedRenderImplementation" in content, (
        "Missing import of getVersionedRenderImplementation — old API not replaced"
    )


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
    """Duplicate legacy/createRoot test variants are consolidated — test count reduced from 6 to ~3."""
    content = Path(TEST_FILE).read_text()
    # Base has 6 it('should...) entries (3 legacy + 3 createRoot); fix merges to 3
    test_count = len(re.findall(r"it\('should", content))
    assert test_count <= 4, (
        f"Expected ≤4 test cases after deduplication, found {test_count}. "
        "Duplicate legacy/createRoot variants may not have been removed."
    )


# [pr_diff] fail_to_pass
def test_version_upper_bound_annotation_removed():
    """Version upper bound annotations (@reactVersion <= 18.2) must be removed."""
    content = Path(TEST_FILE).read_text()
    assert "@reactVersion <= 18.2" not in content, (
        "Upper-bound version annotation '@reactVersion <= 18.2' should be removed "
        "after merging legacy/createRoot variants into versioned render"
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
    # The unified render must actually be called in test bodies
    render_calls = len(re.findall(r"\brender\(", content))
    assert render_calls >= 3, (
        f"Expected render() called at least 3 times in tests, found {render_calls}"
    )
