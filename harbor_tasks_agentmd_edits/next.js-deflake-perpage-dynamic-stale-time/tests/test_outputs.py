"""
Task: next.js-deflake-perpage-dynamic-stale-time
Repo: vercel/next.js @ 8283b1260ba3eb187baf20727e739fbd8ba7bbf6
PR:   91492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"

TEST_FILE = (
    Path(REPO)
    / "test/e2e/app-dir/segment-cache/staleness"
    / "segment-cache-per-page-dynamic-stale-time.test.ts"
)
PER_PAGE_DIR = (
    Path(REPO)
    / "test/e2e/app-dir/segment-cache/staleness/app/per-page-config"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TSX/TS files have balanced braces."""
    for tsx in PER_PAGE_DIR.rglob("page.tsx"):
        content = tsx.read_text()
        assert content.count("{") == content.count("}"), \
            f"Unbalanced curly braces in {tsx.relative_to(REPO)}"
    content = TEST_FILE.read_text()
    assert content.count("{") == content.count("}"), \
        "Unbalanced curly braces in test file"
    assert content.count("(") == content.count(")"), \
        "Unbalanced parentheses in test file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_browser_back():
    """Test must not use browser.back() which causes BFCache flakiness."""
    content = TEST_FILE.read_text()
    # Find the specific flaky test function
    match = re.search(
        r"per-page value overrides global.*?(?=\bit\(|describe\(|\Z)",
        content,
        re.DOTALL,
    )
    assert match, "Could not find the per-page override test"
    test_body = match.group(0)
    assert "browser.back()" not in test_body, \
        "Test must not use browser.back() — BFCache restores accordion state and causes flaky prefetches"


# [pr_diff] fail_to_pass
def test_intermediate_pages_created():
    """New intermediate/hub pages must exist for navigation without browser.back()."""
    original_dirs = {"dynamic-stale-10", "dynamic-stale-60"}
    all_dirs = {
        d.name
        for d in PER_PAGE_DIR.iterdir()
        if d.is_dir() and (d / "page.tsx").exists()
    }
    new_dirs = all_dirs - original_dirs
    assert len(new_dirs) >= 2, \
        f"Expected at least 2 new intermediate/hub pages, found: {new_dirs}"


# [pr_diff] fail_to_pass
def test_intermediate_pages_dynamic():
    """New intermediate pages must use connection() for dynamic rendering."""
    original_dirs = {"dynamic-stale-10", "dynamic-stale-60"}
    new_pages = [
        d / "page.tsx"
        for d in PER_PAGE_DIR.iterdir()
        if d.is_dir()
        and d.name not in original_dirs
        and (d / "page.tsx").exists()
    ]
    assert len(new_pages) >= 2
    for page in new_pages:
        content = page.read_text()
        assert "connection" in content, \
            f"{page.relative_to(REPO)} must call connection() for dynamic rendering"


# [pr_diff] fail_to_pass
def test_intermediate_pages_use_link_accordion():
    """New intermediate pages must use LinkAccordion for prefetch control."""
    original_dirs = {"dynamic-stale-10", "dynamic-stale-60"}
    new_pages = [
        d / "page.tsx"
        for d in PER_PAGE_DIR.iterdir()
        if d.is_dir()
        and d.name not in original_dirs
        and (d / "page.tsx").exists()
    ]
    assert len(new_pages) >= 2
    for page in new_pages:
        content = page.read_text()
        assert "LinkAccordion" in content, \
            f"{page.relative_to(REPO)} must use LinkAccordion"
        # Must link back to the target stale-time pages
        assert "dynamic-stale" in content or "stale" in content, \
            f"{page.relative_to(REPO)} must link to the stale-time target pages"


# [pr_diff] fail_to_pass
def test_target_pages_link_to_intermediates():
    """Existing dynamic stale time pages must have LinkAccordion links to hub pages."""
    for page_name in ["dynamic-stale-10", "dynamic-stale-60"]:
        page = PER_PAGE_DIR / page_name / "page.tsx"
        content = page.read_text()
        assert "LinkAccordion" in content, \
            f"{page_name}/page.tsx must import and use LinkAccordion"


# [pr_diff] fail_to_pass
def test_test_navigates_to_intermediates():
    """Test must navigate to intermediate/hub pages instead of using browser.back()."""
    content = TEST_FILE.read_text()
    # The test must reference at least 2 intermediate pages
    # (the original has 3 browser.back() calls needing at least 2 distinct hubs)
    original_dirs = {"dynamic-stale-10", "dynamic-stale-60"}
    all_dirs = {
        d.name
        for d in PER_PAGE_DIR.iterdir()
        if d.is_dir()
        and d.name not in original_dirs
        and (d / "page.tsx").exists()
    }
    refs = sum(1 for d in all_dirs if d in content)
    assert refs >= 2, \
        f"Test should reference at least 2 intermediate pages, found refs to: {[d for d in all_dirs if d in content]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation / config file updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
