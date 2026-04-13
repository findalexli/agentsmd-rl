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
# Pass-to-pass (static) - existing infrastructure checks
# ---------------------------------------------------------------------------


def test_link_accordion_component_exists():
    """LinkAccordion component exists at the expected path (pre-existing fixture)."""
    component_path = Path(f"{TEST_DIR}/components/link-accordion.tsx")
    assert component_path.exists(), f"LinkAccordion component missing: {component_path}"
    content = component_path.read_text()
    assert "LinkAccordion" in content, "LinkAccordion component must export the component"
    assert "data-link-accordion" in content, "LinkAccordion must use data-link-accordion attribute"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI/CD checks
# ---------------------------------------------------------------------------


def test_repo_prettier_segment_cache():
    """Repo's Prettier check passes on segment-cache test files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check", TEST_DIR],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_deps_install():
    """Repo dependencies install cleanly (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Dependencies install failed:\n{r.stderr[-500:]}"


def test_repo_ast_grep_segment_cache():
    """Repo's ast-grep static analysis passes on segment-cache files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "ast-grep", "scan", TEST_DIR],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep scan failed:\n{r.stderr[-500:]}"


def test_repo_prettier_segment_cache_src():
    """Repo's Prettier check passes on segment-cache source TSX files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check", f"{TEST_DIR}/components", f"{TEST_DIR}/app"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on source files failed:\n{r.stderr[-500:]}"


def test_repo_alex_next_docs():
    """Repo's language linting (alex) passes on Next.js documentation (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "-q", f"{REPO}/packages/next/README.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Note: alex returns 0 if file is ignored or has no issues
    assert r.returncode == 0, f"Alex language check failed:\n{r.stderr[-500:]}"


def test_repo_check_error_codes():
    """Repo's error code check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "packages/next/check-error-codes.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Error code check failed:\n{r.stderr[-500:]}"


def test_repo_eslint_segment_cache():
    """Repo's ESLint check passes on segment-cache test files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "--config", "eslint.config.mjs",
         f"{TEST_DIR}/segment-cache-per-page-dynamic-stale-time.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


def test_repo_prettier_src():
    """Repo's Prettier check passes on segment-cache source TSX files (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/prettier", "--check",
         f"{TEST_DIR}/components",
         f"{TEST_DIR}/app"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on source files failed:\n{r.stderr[-500:]}"


def test_repo_alex_docs():
    """Repo's language linting (alex) passes on Next.js docs (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "-q", f"{REPO}/docs"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Note: alex returns 0 if files are ignored or have no issues
    assert r.returncode == 0, f"Alex language check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code behavior tests
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

    assert "/per-page-config/hub-a" in content, \
        "Test must navigate to hub-a instead of using browser.back()"
    assert "/per-page-config/hub-b" in content, \
        "Test must navigate to hub-b instead of using browser.back()"
    assert "/per-page-config/hub-c" in content, \
        "Test must navigate to hub-c instead of using browser.back()"

    # Check that the specific deflaked test (per-page value overrides global)
    # doesn't use browser.back() - it should use hub navigation instead.
    # Find the specific test and check only that section
    import re

    test_start = content.find("it('per-page value overrides global")
    assert test_start > 0, "Could not find the deflaked test 'per-page value overrides global'"

    # Find the end of this specific test (next it( or test( at same indentation level)
    # Look for patterns that indicate the next test or end of describe block
    next_test_pattern = r"\n  it\(|\n  test\(|\n}\)"
    next_match = re.search(next_test_pattern, content[test_start + 50:])
    if next_match:
        test_section = content[test_start:test_start + 50 + next_match.start()]
    else:
        test_section = content[test_start:]

    # Check for actual await browser.back() calls in this test section
    code_pattern = r'await\s+browser\.back\(\)'
    matches = re.findall(code_pattern, test_section)
    assert len(matches) == 0, \
        f"Test 'per-page value overrides global' must not use 'await browser.back()' - use hub page navigation instead. Found {len(matches)} occurrence(s)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - config/instruction file update tests
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

    assert "name: router-act" in content, "SKILL.md must have name: router-act in frontmatter"
    assert "description:" in content, "SKILL.md must have description in frontmatter"
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

    assert "'no-requests'" in content, \
        "SKILL.md must document 'no-requests' string assertion"
    assert "includes" in content, \
        "SKILL.md must document includes matching"
    assert "requestIdleCallback" in content, \
        "SKILL.md must explain how act captures IntersectionObserver-triggered prefetches"
