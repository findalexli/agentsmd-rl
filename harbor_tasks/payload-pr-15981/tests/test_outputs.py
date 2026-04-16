"""
Benchmark tests for payloadcms/payload#15981
fix: use latest draft version data when trashing unpublished documents
"""

import os
import subprocess
import sys

REPO = "/workspace/payload_repo"


def test_fix_applied():
    """
    Fail-to-pass: The fix line should be present in update.ts.
    Without the fix, localized field data is lost when bulk-trashing drafts.
    """
    update_ts = os.path.join(REPO, "packages/payload/src/collections/operations/update.ts")
    with open(update_ts) as f:
        content = f.read()

    # The distinctive fix: querying versions when isTrashAttempt is true
    assert "shouldSaveDraft || isTrashAttempt" in content, (
        "Fix not applied: The condition should include isTrashAttempt "
        "to query draft versions when trashing unpublished documents"
    )


def test_posts_collection_has_localized_field():
    """
    Fail-to-pass: The Posts collection should have the localizedField defined.
    This field is required for testing the bug.
    """
    posts_ts = os.path.join(REPO, "test/trash/collections/Posts/index.ts")
    with open(posts_ts) as f:
        content = f.read()

    assert "localizedField" in content, (
        "Posts collection should have localizedField defined"
    )
    assert 'localized: true' in content, (
        "localizedField should be configured as localized: true"
    )


def test_trash_config_has_localization():
    """
    Fail-to-pass: The trash test config should have localization enabled.
    """
    config_ts = os.path.join(REPO, "test/trash/config.ts")
    with open(config_ts) as f:
        content = f.read()

    assert "localization:" in content, (
        "Localization config should be present in trash test config"
    )
    assert "locales:" in content, (
        "Localization locales should be defined"
    )


def test_payload_types_include_localized_field():
    """
    Pass-to-pass: Generated types should include the localizedField in Post interface.
    """
    types_ts = os.path.join(REPO, "test/trash/payload-types.ts")
    with open(types_ts) as f:
        content = f.read()

    # Find the Post interface and check for localizedField
    assert "localizedField?: string | null" in content, (
        "Post type should include localizedField?: string | null"
    )


def test_update_ts_context():
    """
    Fail-to-pass: Verify the fix is in the correct context within update.ts.
    The fix should be near the versionsWhere assignment.
    """
    update_ts = os.path.join(REPO, "packages/payload/src/collections/operations/update.ts")
    with open(update_ts) as f:
        content = f.read()

    # First check the fix is present at all
    fix_pos = content.find("shouldSaveDraft || isTrashAttempt")
    assert fix_pos != -1, (
        "Fix not found: shouldSaveDraft || isTrashAttempt should be present in update.ts"
    )

    # Check the fix is near versionsWhere (correct context)
    assert "versionsWhere" in content, "versionsWhere should be present"
    assert "appendVersionToQueryKey" in content, "appendVersionToQueryKey should be present"

    # The fix line should be before versionsWhere
    versions_pos = content.find("versionsWhere")
    assert fix_pos < versions_pos, (
        "Fix should appear before versionsWhere assignment"
    )


def test_repo_eslint_update_ts():
    """
    Pass-to-pass: ESLint passes on the update.ts operation file (repo CI).
    """
    r = subprocess.run(
        ["npx", "eslint", "packages/payload/src/collections/operations/update.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on update.ts:\n{r.stderr[-500:]}"


def test_repo_eslint_delete_operations():
    """
    Pass-to-pass: ESLint passes on related trash operations (repo CI).
    """
    r = subprocess.run(
        ["npx", "eslint", "packages/payload/src/collections/operations/delete.ts",
         "packages/payload/src/collections/operations/deleteByID.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on delete operations:\n{r.stderr[-500:]}"


def test_repo_unit_tests():
    """
    Pass-to-pass: Unit tests pass on base commit (repo CI).
    """
    r = subprocess.run(
        ["npx", "vitest", "run", "--project", "unit"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "NODE_OPTIONS": "--no-experimental-strip-types --max-old-space-size=512"},
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run all tests
    tests = [
        test_fix_applied,
        test_posts_collection_has_localized_field,
        test_trash_config_has_localization,
        test_payload_types_include_localized_field,
        test_update_ts_context,
        test_repo_eslint_update_ts,
        test_repo_eslint_delete_operations,
        test_repo_unit_tests,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", file=sys.stderr)
            test()
            print(f"  PASSED: {test.__name__}", file=sys.stderr)
        except AssertionError as e:
            print(f"  FAILED: {test.__name__}: {e}", file=sys.stderr)
            failed.append(test.__name__)
        except Exception as e:
            print(f"  ERROR: {test.__name__}: {e}", file=sys.stderr)
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed", file=sys.stderr)
        sys.exit(0)
