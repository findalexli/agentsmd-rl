"""
Task: supabase-chore-improve-e2e-tests
Repo: supabase/supabase @ 522fbeac709c449c5dc1132b1a88fcd91e28afb3
PR:   43987

Replace brittle clipboard timeouts in E2E tests with a reusable
retry-based clipboard assertion utility, and update the Cursor rule
to document the new pattern.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/supabase"

SPEC_FILES = [
    "e2e/studio/features/database.spec.ts",
    "e2e/studio/features/sql-editor.spec.ts",
    "e2e/studio/features/storage.spec.ts",
    "e2e/studio/features/table-editor.spec.ts",
]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """Key modified files must exist and be non-empty."""
    for spec in SPEC_FILES:
        p = Path(REPO) / spec
        assert p.exists(), f"Missing: {spec}"
        assert p.stat().st_size > 0, f"Empty: {spec}"

    helpers = Path(REPO) / "e2e/studio/utils/storage-helpers.ts"
    assert helpers.exists(), "Missing: storage-helpers.ts"

    rule = Path(REPO) / ".cursor/rules/testing/e2e-studio/RULE.md"
    assert rule.exists(), "Missing: RULE.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — clipboard utility creation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_clipboard_utility_created():
    """A clipboard assertion utility must exist in e2e/studio/utils/."""
    utils_dir = Path(REPO) / "e2e/studio/utils"
    # Look for any file that exports a clipboard assertion function
    found = False
    for ts_file in utils_dir.glob("*.ts"):
        content = ts_file.read_text()
        # Must export a function related to clipboard assertion/expectation
        if re.search(r"export\s+(?:const|function)\s+\w*[Cc]lipboard\w*", content):
            found = True
            break
    assert found, (
        "No clipboard assertion utility found exported from e2e/studio/utils/*.ts"
    )


# [pr_diff] fail_to_pass
def test_clipboard_utility_has_retry_mechanism():
    """The clipboard utility must use Playwright's retry mechanism, not raw timeouts."""
    utils_dir = Path(REPO) / "e2e/studio/utils"
    found_retry = False
    for ts_file in utils_dir.glob("*.ts"):
        content = ts_file.read_text()
        if not re.search(r"[Cc]lipboard", content):
            continue
        # Must use .toPass() or expect.poll() or similar retry mechanism
        if ".toPass(" in content or "expect.poll(" in content:
            found_retry = True
            break
    assert found_retry, (
        "Clipboard utility must use Playwright retry mechanism (.toPass() or expect.poll())"
    )


# [pr_diff] fail_to_pass
def test_clipboard_utility_supports_exact_and_contains():
    """The clipboard utility must support both exact match and substring containment."""
    utils_dir = Path(REPO) / "e2e/studio/utils"
    found = False
    for ts_file in utils_dir.glob("*.ts"):
        content = ts_file.read_text()
        if not re.search(r"[Cc]lipboard", content):
            continue
        # Must have both exact/equal and contain logic
        has_exact = "toEqual" in content or "toBe" in content or "exact" in content
        has_contains = "toContain" in content or "includes" in content or "contain" in content.lower()
        if has_exact and has_contains:
            found = True
            break
    assert found, (
        "Clipboard utility must support both exact match and substring containment"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — spec file migration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_specs_import_clipboard_utility():
    """At least 3 spec files must import the clipboard assertion utility."""
    import_count = 0
    for spec in SPEC_FILES:
        content = (Path(REPO) / spec).read_text()
        # Check for import of a clipboard-related utility from utils
        if re.search(r"import\s+.*[Cc]lipboard.*from\s+['\"]\.\.\/utils\/", content):
            import_count += 1
    assert import_count >= 3, (
        f"Only {import_count} spec files import the clipboard utility, expected >= 3"
    )


# [pr_diff] fail_to_pass
def test_no_raw_clipboard_read_in_specs():
    """Spec files must not directly call navigator.clipboard.readText()."""
    violations = []
    for spec in SPEC_FILES:
        content = (Path(REPO) / spec).read_text()
        if "navigator.clipboard.readText()" in content:
            violations.append(spec)
    assert not violations, (
        f"These spec files still directly call navigator.clipboard.readText(): {violations}. "
        "Use the clipboard assertion utility instead."
    )


# [pr_diff] fail_to_pass
def test_storage_helpers_no_long_upload_timeout():
    """storage-helpers.ts must not use a 15-second waitForTimeout for uploads."""
    content = (Path(REPO) / "e2e/studio/utils/storage-helpers.ts").read_text()
    assert "waitForTimeout(15_000)" not in content and "waitForTimeout(15000)" not in content, (
        "storage-helpers.ts still uses waitForTimeout(15_000) for upload waiting. "
        "Use Playwright assertions (expect visibility) instead."
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — RULE.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_clipboard_utility_not_stub():
    """The clipboard utility file must have meaningful implementation (not a stub)."""
    utils_dir = Path(REPO) / "e2e/studio/utils"
    for ts_file in utils_dir.glob("*.ts"):
        content = ts_file.read_text()
        if not re.search(r"export\s+(?:const|function)\s+\w*[Cc]lipboard\w*", content):
            continue
        # Must have actual logic: at least clipboard read + assertion
        assert "clipboard" in content.lower(), "Utility must reference clipboard API"
        assert len(content.strip().split("\n")) >= 5, "Utility is too short to be real"
        return
    assert False, "No clipboard utility file found to check for stub"
