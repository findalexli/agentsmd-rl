"""
Task: playwright-chorecli-allow-both-selectors-and
Repo: playwright @ 35f853d5c293c901ea66a9aa3f56f6879a94e66a
PR:   39708

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
TAB_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/tab.ts"
SKILL_MD = Path(REPO) / "packages/playwright-core/src/tools/cli-client/skill/SKILL.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tab_imports_locator_parser():
    """tab.ts must import locatorOrSelectorAsSelector from locatorParser."""
    content = TAB_TS.read_text()
    assert "locatorOrSelectorAsSelector" in content, \
        "tab.ts should import locatorOrSelectorAsSelector"
    assert "locatorParser" in content, \
        "tab.ts should import from locatorParser module"


# [pr_diff] fail_to_pass
def test_tab_converts_selector_through_parser():
    """tab.ts must convert the selector input through locatorOrSelectorAsSelector."""
    content = TAB_TS.read_text()
    # The function must be called with the language, raw selector, and testIdAttribute
    assert "locatorOrSelectorAsSelector(" in content, \
        "tab.ts should call locatorOrSelectorAsSelector to convert selectors"
    assert "testIdAttribute" in content, \
        "tab.ts should pass testIdAttribute to locatorOrSelectorAsSelector"


# [pr_diff] fail_to_pass
def test_tab_checks_element_via_query_selector():
    """tab.ts must use page.$() for element existence check instead of isVisible()."""
    content = TAB_TS.read_text()
    # Find the selector handling block (between 'if (param.selector)' and the else)
    sel_start = content.find("if (param.selector)")
    assert sel_start != -1, "tab.ts should have param.selector check"
    sel_block = content[sel_start:sel_start + 600]
    # Should use page.$() not locator.isVisible()
    assert "page.$(selector)" in sel_block or "this.page.$(selector)" in sel_block, \
        "Should use page.$() for element existence check in selector branch"
    assert "isVisible()" not in sel_block, \
        "Should not use isVisible() for element existence check"


# [pr_diff] fail_to_pass
def test_tab_error_message_quoted_format():
    """Error message must use quoted format without 'Selector' prefix."""
    content = TAB_TS.read_text()
    sel_start = content.find("if (param.selector)")
    assert sel_start != -1
    sel_block = content[sel_start:sel_start + 600]
    # New format: `"${param.selector}" does not match`
    # Old format: `Selector ${param.selector} does not match`
    assert '"${param.selector}" does not match' in sel_block or \
           '`"${param.selector}" does not match' in sel_block, \
        "Error message should use quoted selector format"
    assert "Selector ${param.selector}" not in sel_block, \
        "Error message should not use old 'Selector' prefix format"


# [pr_diff] fail_to_pass
def test_tab_locator_parser_integration():
    """tab.ts must import locatorOrSelectorAsSelector and the parser must handle locator inputs."""
    script = r"""
const fs = require('fs');
const path = require('path');

// 1. Verify tab.ts imports locatorOrSelectorAsSelector
const tabSrc = fs.readFileSync(
    path.join(process.cwd(), 'packages/playwright-core/src/tools/backend/tab.ts'),
    'utf8'
);
const hasImport = /import\s*\{[^}]*locatorOrSelectorAsSelector/.test(tabSrc);
if (!hasImport) {
    console.log(JSON.stringify({ error: 'tab.ts does not import locatorOrSelectorAsSelector' }));
    process.exit(1);
}

// 2. Verify the parser handles both CSS selectors and Playwright locators
const { locatorOrSelectorAsSelector } = require('/tmp/locatorParser.cjs');
const tests = [
    { input: "getByRole('button', { name: 'Submit' })", desc: "getByRole locator" },
    { input: "getByTestId('my-id')", desc: "getByTestId locator" },
    { input: "#main > button", desc: "CSS selector" },
];

const results = tests.map(t => ({
    desc: t.desc,
    input: t.input,
    selector: locatorOrSelectorAsSelector('javascript', t.input, 'data-testid'),
    pass: locatorOrSelectorAsSelector('javascript', t.input, 'data-testid').length > 0,
}));

console.log(JSON.stringify({ hasImport, results }));
"""
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15, cwd=REPO,
    )
    assert result.returncode == 0, f"Node script failed: {result.stderr}"
    data = json.loads(result.stdout.strip().split("\n")[-1])
    assert data["hasImport"], "tab.ts should import locatorOrSelectorAsSelector"
    for r in data["results"]:
        assert r["pass"], \
            f"Parser failed for {r['desc']}: '{r['input']}' returned empty selector"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/playwright-dev/tools.md:399-401
def test_skill_md_documents_locator_syntax():
    """SKILL.md must document Playwright locator syntax, not just old-style selectors."""
    content = SKILL_MD.read_text()
    content_lower = content.lower()
    # Must mention "locator" concept (not just "selector")
    assert "locator" in content_lower, \
        "SKILL.md should mention Playwright locators"
    # The old phrasing was "css or role selectors"
    # The new phrasing should reference Playwright locators
    assert "playwright locator" in content_lower or "role locator" in content_lower, \
        "SKILL.md should specifically reference Playwright locator syntax"


# [pr_diff] fail_to_pass
def test_skill_md_getbyrole_example():
    """SKILL.md must show a getByRole locator example."""
    content = SKILL_MD.read_text()
    assert "getByRole" in content, \
        "SKILL.md should show getByRole locator example"
    # Should show realistic usage with role and name
    assert "button" in content and "getByRole" in content, \
        "SKILL.md getByRole example should demonstrate role-based targeting"


# [pr_diff] fail_to_pass
def test_skill_md_getbytestid_example():
    """SKILL.md must show a getByTestId locator example."""
    content = SKILL_MD.read_text()
    assert "getByTestId" in content, \
        "SKILL.md should show getByTestId locator example"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_tab_still_handles_ref_path():
    """tab.ts must still handle the ref-based (aria-ref) element targeting."""
    content = TAB_TS.read_text()
    assert "aria-ref=" in content, \
        "tab.ts should still handle ref-based targeting via aria-ref"
    assert "param.ref" in content, \
        "tab.ts should still reference param.ref"


# [static] pass_to_pass
def test_skill_md_preserves_ref_and_css_examples():
    """SKILL.md must still show ref-based and CSS selector examples."""
    content = SKILL_MD.read_text()
    # Ref examples (e.g., 'click e15')
    assert "click e15" in content or "click e3" in content, \
        "SKILL.md should still show ref-based click example"
    # CSS selector example
    assert "#main" in content or "button.submit" in content, \
        "SKILL.md should still show CSS selector example"
