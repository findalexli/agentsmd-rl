"""
Task: next.js-deflake-perpage-dynamic-stale-time
Repo: vercel/next.js @ 3af4cc14ea400ebc01fdc267f3d3495bfe086a7e
PR:   91492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"

# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_hub_pages_created():
    """Hub pages (hub-a, hub-b, hub-c) must exist with proper structure."""
    hub_pages = [
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx",
    ]
    for page in hub_pages:
        page_path = Path(REPO) / page
        assert page_path.exists(), f"Hub page {page} does not exist"
        content = page_path.read_text()
        assert "LinkAccordion" in content, f"{page} missing LinkAccordion import"
        assert "connection()" in content, f"{page} missing connection() call"
        assert "'input[data-link-accordion=" in content or 'input[data-link-accordion=' in content, f"{page} missing accordion data attribute"


# [static] pass_to_pass
def test_skill_file_created():
    """Router act SKILL.md must exist with proper documentation."""
    skill_path = Path(REPO) / ".agents/skills/router-act/SKILL.md"
    assert skill_path.exists(), "SKILL.md does not exist"
    content = skill_path.read_text()
    assert "---" in content[:10], "SKILL.md missing frontmatter"
    assert "router-act" in content or "LinkAccordion" in content, "SKILL.md missing key content"
    assert "browser.back()" in content, "SKILL.md should warn about browser.back()"
    assert "no-requests" in content, "SKILL.md should mention 'no-requests' assertion"


# [static] pass_to_pass
def test_dynamic_pages_updated():
    """Dynamic pages must have LinkAccordion links to hub pages."""
    pages = [
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx",
    ]
    for page in pages:
        page_path = Path(REPO) / page
        assert page_path.exists(), f"Page {page} does not exist"
        content = page_path.read_text()
        assert "LinkAccordion" in content, f"{page} missing LinkAccordion import"
        assert "hub-a" in content, f"{page} missing hub-a link"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# -----------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_test_uses_hub_navigation():
    """Test must use hub navigation instead of browser.back()."""
    test_path = Path(REPO) / "test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts"
    assert test_path.exists(), "Test file does not exist"
    content = test_path.read_text()

    # Check that hub pages are used for navigation
    assert "hub-a" in content, "Test missing hub-a navigation"
    assert "hub-b" in content, "Test missing hub-b navigation"
    assert "hub-c" in content, "Test missing hub-c navigation"

    # The fix replaces browser.back() with hub navigation
    # Check that the flaky test pattern is fixed
    # We check that the test navigates forward to hub pages
    assert "input[data-link-accordion=\"/per-page-config/hub-a\"]" in content or \
           'input[data-link-accordion="/per-page-config/hub-a"]' in content, \
           "Test missing hub-a accordion toggle"


# [pr_diff] fail_to_pass
def test_agents_md_updated():
    """AGENTS.md must contain router act rule about LinkAccordion."""
    agents_path = Path(REPO) / "AGENTS.md"
    assert agents_path.exists(), "AGENTS.md does not exist"
    content = agents_path.read_text()

    # Check for the router act rule
    assert "LinkAccordion" in content, "AGENTS.md missing LinkAccordion rule"
    assert "browser.back()" in content, "AGENTS.md missing browser.back() warning"
    assert "act" in content, "AGENTS.md missing 'act' reference"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) - regression checks
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax_valid():
    """Modified TypeScript files must have valid syntax."""
    files_to_check = [
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-10/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/dynamic-stale-60/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-a/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-b/page.tsx",
        "test/e2e/app-dir/segment-cache/staleness/app/per-page-config/hub-c/page.tsx",
    ]

    for file in files_to_check:
        file_path = Path(REPO) / file
        if file_path.exists():
            # Use tsc to check syntax
            r = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck", str(file_path)],
                capture_output=True, text=True, timeout=60, cwd=REPO,
            )
            assert r.returncode == 0, f"TypeScript syntax error in {file}: {r.stderr}"


# [static] pass_to_pass
def test_test_file_not_stub():
    """Test file must have meaningful content, not just placeholders."""
    test_path = Path(REPO) / "test/e2e/app-dir/segment-cache/staleness/segment-cache-per-page-dynamic-stale-time.test.ts"
    content = test_path.read_text()

    # Check that the test has actual test cases with act() calls
    assert "createRouterAct" in content, "Test missing createRouterAct import"
    assert "act(" in content, "Test missing act() calls"
    assert "act(" in content and content.count("act(") >= 5, "Test should have multiple act() calls"


# -----------------------------------------------------------------------------
# Config-derived (agent_config) - rules from AGENTS.md
# -----------------------------------------------------------------------------

# [agent_config] pass_to_pass - AGENTS.md:407 @ 3af4cc14ea400ebc01fdc267f3d3495bfe086a7e
def test_router_act_rule_present():
    """AGENTS.md must document router act testing patterns."""
    agents_path = Path(REPO) / "AGENTS.md"
    content = agents_path.read_text()

    # The rule should be in the Test Gotchas section
    lines = content.split("\n")
    test_gotchas_idx = None
    for i, line in enumerate(lines):
        if "Test Gotchas" in line:
            test_gotchas_idx = i
            break

    # Check for the rule about LinkAccordion and browser.back()
    found_rule = False
    for line in lines:
        if "Router act tests must use LinkAccordion to control prefetches" in line or \
           ("LinkAccordion" in line and "browser.back()" in line and "BFCache" in line):
            found_rule = True
            break

    assert found_rule, "AGENTS.md missing router act rule with LinkAccordion and BFCache warning"
