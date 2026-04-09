"""
Task: nextjs-router-act-link-accordion-deflake
Repo: vercel/next.js @ 8283b1260ba3eb187baf20727e739fbd8ba7bbf6
PR:   91492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TEST_DIR = f"{REPO}/test/e2e/app-dir/segment-cache/staleness"
PER_PAGE_DIR = f"{TEST_DIR}/app/per-page-config"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing infrastructure checks
# ---------------------------------------------------------------------------


def test_link_accordion_component_exists():
    """LinkAccordion component exists at the expected path (pre-existing fixture)."""
    component_path = Path(f"{TEST_DIR}/components/link-accordion.tsx")
    assert component_path.exists(), f"LinkAccordion component missing: {component_path}"
    content = component_path.read_text()
    assert "LinkAccordion" in content, "LinkAccordion component must export the component"
    assert "data-link-accordion" in content, "LinkAccordion must use data-link-accordion attribute"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------


def test_hub_pages_structure():
    """Hub pages (hub-a, hub-b, hub-c) exist with LinkAccordion imports, connection(), and Suspense."""
    script = r"""
const fs = require('fs');
const path = require('path');
const base = process.argv[1];
const hubs = ['hub-a', 'hub-b', 'hub-c'];
const errors = [];
for (const hub of hubs) {
    const filePath = path.join(base, hub, 'page.tsx');
    if (!fs.existsSync(filePath)) {
        errors.push('Missing hub page: ' + hub + '/page.tsx');
        continue;
    }
    const content = fs.readFileSync(filePath, 'utf-8');
    if (!content.includes('LinkAccordion')) errors.push(hub + ': missing LinkAccordion');
    if (!content.includes('await connection()')) errors.push(hub + ': missing connection()');
    if (!content.includes('<Suspense')) errors.push(hub + ': missing Suspense');
    if (!content.includes('export default function Page()')) errors.push(hub + ': missing default export');
}
if (errors.length > 0) { console.error(errors.join('\n')); process.exit(1); }
console.log('OK');
"""
    result = subprocess.run(
        ["node", "-e", script, PER_PAGE_DIR],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0, f"Hub page validation failed: {result.stderr}"
    assert result.stdout.strip() == "OK"


def test_stale_pages_link_to_hubs():
    """Dynamic stale pages have LinkAccordion links to hub pages."""
    for stale_page in ["dynamic-stale-10/page.tsx", "dynamic-stale-60/page.tsx"]:
        file_path = Path(PER_PAGE_DIR) / stale_page
        assert file_path.exists(), f"Missing stale page: {stale_page}"
        content = file_path.read_text()
        assert "LinkAccordion" in content, \
            f"{stale_page}: must import LinkAccordion for hub navigation"
        assert "hub-a" in content, \
            f"{stale_page}: must link to hub-a via LinkAccordion"
        assert "hub-b" in content or "hub-c" in content, \
            f"{stale_page}: must link to a second hub page"


def test_test_uses_hub_navigation():
    """Test file uses hub page navigation instead of browser.back()."""
    test_file = Path(f"{TEST_DIR}/segment-cache-per-page-dynamic-stale-time.test.ts")
    assert test_file.exists(), "Test file must exist"
    content = test_file.read_text()

    # Find the specific test that was deflaked (contains 'per-page value overrides global')
    # Extract the section of the test between the describe block that has the stale time test
    # Check that hub pages are referenced in the navigation pattern
    assert "/per-page-config/hub-a" in content, \
        "Test must navigate to hub-a instead of using browser.back()"
    assert "/per-page-config/hub-b" in content, \
        "Test must navigate to hub-b instead of using browser.back()"
    assert "/per-page-config/hub-c" in content, \
        "Test must navigate to hub-c instead of using browser.back()"

    # Verify browser.back() is not used in the "overrides global" test section
    # Find the test function content
    test_start = content.find("per-page value overrides global")
    assert test_start > 0, "Could not find the deflaked test"

    # Find the end of this test (next 'it(' or end of describe)
    next_test = content.find("it(", test_start + 100)
    if next_test < 0:
        test_section = content[test_start:]
    else:
        test_section = content[test_start:next_test]

    assert "browser.back()" not in test_section, \
        "Test must not use browser.back() — use hub page navigation instead"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/instruction file update tests
# ---------------------------------------------------------------------------


def test_agents_md_router_act_rule():
    """AGENTS.md must document the LinkAccordion/router-act rule."""
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must exist"
    content = agents_md.read_text()
    assert "LinkAccordion" in content, \
        "AGENTS.md must mention LinkAccordion for prefetch control"
    assert "browser.back()" in content or "BFCache" in content, \
        "AGENTS.md must warn about browser.back()/BFCache causing uncontrolled re-prefetches"
    assert "$router-act" in content or "router-act" in content, \
        "AGENTS.md must reference the router-act skill"


def test_router_act_skill_created():
    """Router act SKILL.md exists with core patterns about LinkAccordion and hub pages."""
    skill_path = Path(REPO) / ".agents/skills/router-act/SKILL.md"
    assert skill_path.exists(), "Router act skill file must exist"
    content = skill_path.read_text()

    # Check frontmatter has required fields
    assert "name: router-act" in content, "SKILL.md must have name: router-act in frontmatter"
    assert "description:" in content, "SKILL.md must have description in frontmatter"

    # Check core content patterns
    assert "LinkAccordion" in content, \
        "SKILL.md must document LinkAccordion pattern"
    assert "no-requests" in content, \
        "SKILL.md must document no-requests assertion"
    assert "hub" in content.lower(), \
        "SKILL.md must document hub page pattern"
    assert "browser.back()" in content, \
        "SKILL.md must warn about browser.back() flakiness"
    assert "BFCache" in content, \
        "SKILL.md must explain BFCache state restoration issue"


def test_skill_documents_no_requests_pattern():
    """SKILL.md documents the no-requests assertion pattern for cache verification."""
    skill_path = Path(REPO) / ".agents/skills/router-act/SKILL.md"
    content = skill_path.read_text()

    # Verify the no-requests pattern is properly documented
    assert "'no-requests'" in content, \
        "SKILL.md must document 'no-requests' string assertion"
    assert "includes" in content, \
        "SKILL.md must document includes matching"
    assert "requestIdleCallback" in content, \
        "SKILL.md must explain how act captures IntersectionObserver-triggered prefetches"
