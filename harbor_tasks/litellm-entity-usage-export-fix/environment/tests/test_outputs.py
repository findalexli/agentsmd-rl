"""
Test harness for litellm EntityUsageExport fix (BerriAI/litellm#25153).

Bug: entity usage exports for non-team entity types (tags, orgs, customers,
agents, users) display wrong entity ID/alias values. The code extracts
team_id from api_key_breakdown metadata instead of using the entity key
directly, causing team names to appear in non-team exports.

Fix: replace extractTeamIdFromApiKeyBreakdown with resolveEntityDisplay
which uses entity key directly.
"""

import subprocess
import os

REPO = "/workspace/litellm-dashboard"


def run_vitest(pattern=None, reporter="verbose"):
    """Run vitest with optional test-name pattern filter."""
    cmd = ["pnpm", "vitest", "run",
           "src/components/EntityUsageExport/utils.test.ts",
           f"--reporter={reporter}"]
    if pattern:
        cmd.extend(["--test-name-pattern", pattern])
    result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=300)
    return result


# ---------------------------------------------------------------------------
# Structural f2p: verify the patch was applied (these fail on base, pass after fix)
# ---------------------------------------------------------------------------

def test_extract_team_id_from_api_key_breakdown_removed():
    """
    The buggy extractTeamIdFromApiKeyBreakdown function must be removed by the fix.
    Base commit: function exists → test FAILS.
    After fix: function removed → test PASSES.
    """
    utils_path = os.path.join(REPO, "src/components/EntityUsageExport/utils.ts")
    with open(utils_path) as f:
        content = f.read()
    assert "extractTeamIdFromApiKeyBreakdown" not in content, \
        "extractTeamIdFromApiKeyBreakdown still present - fix not applied"


def test_resolve_entity_display_added():
    """
    The fix adds resolveEntityDisplay function. It must be present after fix.
    Base commit: function NOT present → test FAILS.
    After fix: function exists → test PASSES.
    """
    utils_path = os.path.join(REPO, "src/components/EntityUsageExport/utils.ts")
    with open(utils_path) as f:
        content = f.read()
    assert "resolveEntityDisplay" in content, \
        "resolveEntityDisplay not found - fix not applied"


def test_entity_usage_export_test_file_updated():
    """
    The test file must be updated to match fixed behavior. In base commit,
    'should use dash when team id is not available' exists; after fix,
    'should fall back to the entity key when there is no team alias mapping' exists.
    Base commit: old test name present, new absent → test FAILS.
    After fix: new test name present → test PASSES.
    """
    test_path = os.path.join(REPO, "src/components/EntityUsageExport/utils.test.ts")
    with open(test_path) as f:
        content = f.read()
    assert "should fall back to the entity key when there is no team alias mapping" in content, \
        "New test name not found in test file - fix may not include test updates"


def test_test_file_uses_entity_keys_not_entity1_entity2():
    """
    The test data changed entity keys from 'entity1'/'entity2' to 'team-1'/'team-2'.
    After fix, the test file should use 'team-1' and 'team-2' as entity keys.
    This ensures the test data reflects the new behavior where entity key = display ID.
    """
    test_path = os.path.join(REPO, "src/components/EntityUsageExport/utils.test.ts")
    with open(test_path) as f:
        content = f.read()
    # After fix, mockSpendData uses "team-1" and "team-2" as entity keys
    assert '"team-1"' in content and '"team-2"' in content, \
        "Test data not updated to use entity keys 'team-1'/'team-2'"


# ---------------------------------------------------------------------------
# Behavioral f2p: run vitest with new test name - fails on base (0 tests found),
# passes after fix (tests found and pass)
# ---------------------------------------------------------------------------

def test_new_fallback_test_runs_and_passes():
    """
    The fix renamed 'should use dash when team id is not available' to
    'should fall back to the entity key when there is no team alias mapping'.

    Base commit: this test name doesn't exist → vitest reports 0 tests → FAILS.
    After fix: this test exists and runs → PASSES.
    """
    result = run_vitest(pattern="should fall back to the entity key when there is no team alias mapping")
    output = result.stdout + result.stderr

    # Check that tests were actually found and ran
    # vitest outputs "0 tests found" if no matches - we need tests to have run
    assert "0 tests found" not in output, \
        f"New test name not found - test file may not be updated:\n{output[-1000:]}"
    # vitest returns non-zero when tests fail
    assert result.returncode == 0, \
        f"Test failed (new test ran but assertions didn't pass):\n{output[-2000:]}"


def test_alias_test_runs_and_passes():
    """
    The test 'should use entity key as alias when no team alias map is provided'
    replaces 'should use key alias when available'. After fix, running with
    the new test name should find and run tests successfully.

    Base commit: new test name doesn't exist → vitest 0 tests → FAILS.
    After fix: test exists and passes → PASSES.
    """
    result = run_vitest(pattern="should use entity key as alias when no team alias map is provided")
    output = result.stdout + result.stderr
    assert "0 tests found" not in output, \
        f"New alias test not found:\n{output[-1000:]}"
    assert result.returncode == 0, \
        f"Test failed:\n{output[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: vitest suite must run and pass after fix
# ---------------------------------------------------------------------------

def test_vitest_suite_passes():
    """
    Full vitest suite for EntityUsageExport passes after fix.
    This is a p2p sanity check - on base commit the tests would fail because
    the test expectations don't match the buggy code.
    """
    result = run_vitest()
    output = result.stdout + result.stderr
    assert result.returncode == 0, \
        f"Vitest suite failed:\n{output[-2000:]}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])