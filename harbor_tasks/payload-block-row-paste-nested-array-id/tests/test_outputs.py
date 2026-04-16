"""
test_outputs.py - Verify block row paste with nested array ID regeneration

Tests the fix for: when copying a block row containing an array field and pasting it
into a new block, array items appeared doubled in the UI. The root cause was that
`clipboardPath.endsWith('.id')` was too broad - it skipped ALL .id paths including
nested array item IDs (e.g., ctas.0.buttons.0.id), causing missing ID form state
entries and server-side row duplication on merge.

The fix changes the condition from:
  clipboardPath.endsWith('.id')
to:
  clipboardPath === `${pathToReplace}.id`
So only the direct block row ID is skipped, not nested array item IDs.
"""

import subprocess
import sys

REPO_ROOT = "/workspace/payload"

def test_skip_condition_uses_exact_match():
    """
    Fail-to-pass: The skip condition must use exact path match (===), not .endsWith('.id').

    On base commit: skip condition has `clipboardPath.endsWith('.id')` which is too broad
    On fixed commit: skip condition has `clipboardPath === `${pathToReplace}.id`` (exact match)

    This is the PRIMARY fail-to-pass test - it fails on base commit and passes on fixed commit.
    """
    r = subprocess.run(
        ["sed", "-n", "117,123p", "packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.ts"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )

    skip_block = r.stdout + r.stderr

    # The fixed version uses === for exact path match in the skip condition
    # The buggy version uses .endsWith('.id')
    has_fixed = "clipboardPath ===" in skip_block
    has_buggy = ".endsWith('.id')" in skip_block

    assert has_fixed, f"Fix not applied - skip condition should use 'clipboardPath ===' but found:\n{skip_block}"
    assert not has_buggy, f"Bug still present - skip condition should NOT use '.endsWith('.id')' but found:\n{skip_block}"


def test_no_endsWith_in_skip_logic():
    """
    Fail-to-pass: The skip condition block must not contain .endsWith('.id').

    On base commit: .endsWith('.id') appears in the skip condition (BUG)
    On fixed commit: .endsWith('.id') is replaced with === comparison (FIXED)

    This ensures the fix was properly applied.
    """
    r = subprocess.run(
        ["grep", "-n", ".endsWith", "packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.ts"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )

    output = r.stdout + r.stderr

    # Count occurrences of .endsWith('.id')
    # Line 119 is the skip condition - should be === on fixed commit
    # Line 131 is the ID regeneration logic - correctly uses .endsWith on both versions
    lines_with_endsWith = [l for l in output.split('\n') if ".endsWith('.id')" in l]
    skip_condition_line = None
    regeneration_line = None

    for line in lines_with_endsWith:
        if ':' in line:
            num = int(line.split(':')[0])
            if num == 119:
                skip_condition_line = line
            elif num == 131:
                regeneration_line = line

    # The skip condition (line 119) should NOT have .endsWith on fixed commit
    # The regeneration logic (line 131) correctly uses .endsWith on both versions
    assert skip_condition_line is None or "clipboardPath ===" in skip_condition_line, \
        f"Skip condition still has buggy .endsWith('.id'): {skip_condition_line}"


def test_all_existing_tests_pass():
    """
    Pass-to-pass: All existing unit tests pass.

    On both base commit and fixed commit, all 8 existing tests should pass.
    The fix doesn't break any existing functionality.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run",
         "--config", "vitest.config.ts",
         "packages/ui/src/elements/ClipboardAction/mergeFormStateFromClipboard.spec.ts",
         "--reporter=verbose"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = r.stdout + r.stderr

    # All 8 existing tests should pass on both base and fixed commits
    assert r.returncode == 0, f"Tests failed:\n{output[-1500:]}"
    assert "8 passed" in output, f"Expected 8 passed tests but got:\n{output[-500:]}"


def test_repo_eslint_clipboard_action():
    """
    Pass-to-pass: ESLint passes for the ClipboardAction module.

    On both base commit and fixed commit, ESLint should pass with no errors.
    The fix doesn't introduce any new lint issues.
    """
    r = subprocess.run(
        ["npx", "eslint", "packages/ui/src/elements/ClipboardAction/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = r.stdout + r.stderr

    # ESLint should pass with exit 0
    assert r.returncode == 0, f"ESLint failed:\n{output[-1000:]}"


def test_repo_scss_lint():
    """
    Pass-to-pass: SCSS linting passes for the UI package.

    On both base commit and fixed commit, Stylelint should pass with no errors.
    The fix doesn't introduce any new SCSS lint issues.
    """
    r = subprocess.run(
        ["pnpm", "lint:scss"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120
    )

    output = r.stdout + r.stderr

    # SCSS lint should pass with exit 0
    assert r.returncode == 0, f"SCSS lint failed:\n{output[-500:]}"


if __name__ == "__main__":
    tests = [
        test_skip_condition_uses_exact_match,
        test_no_endsWith_in_skip_logic,
        test_all_existing_tests_pass,
        test_repo_eslint_clipboard_action,
        test_repo_scss_lint,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", file=sys.stderr)
            test()
            print(f"  PASS: {test.__name__}", file=sys.stderr)
        except AssertionError as e:
            print(f"  FAIL: {test.__name__} - {e}", file=sys.stderr)
            failed.append(test.__name__)
        except Exception as e:
            print(f"  ERROR: {test.__name__} - {e}", file=sys.stderr)
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} test(s) failed", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAll {len(tests)} tests passed", file=sys.stderr)
        sys.exit(0)