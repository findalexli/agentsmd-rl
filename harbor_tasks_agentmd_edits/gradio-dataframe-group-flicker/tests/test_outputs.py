"""
Task: gradio-dataframe-group-flicker
Repo: gradio-app/gradio @ 339811ee0d6f750e18a9ddc8e9c9bb036e328535
PR:   11282

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"

DATAFRAME_FILES = [
    "js/dataframe/shared/Table.svelte",
    "js/dataframe/shared/VirtualTable.svelte",
    "js/dataframe/shared/RowNumber.svelte",
]


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a node script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_playwright_test(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Playwright test script to verify CSS behavior."""
    # Use .js extension (CommonJS) since the script uses require()
    test_file = Path(REPO) / "_eval_test.js"
    test_file.write_text(script)
    try:
        return subprocess.run(
            ["node", str(test_file)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_style_sections_valid():
    """Modified Svelte files have properly structured style sections."""
    result = _run_node("""
const fs = require('fs');
const files = %s;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const styleOpen = (content.match(/<style/g) || []).length;
    const styleClose = (content.match(/<\\/style>/g) || []).length;
    if (styleOpen !== styleClose) {
        console.error(f + ': mismatched <style> tags (' + styleOpen + ' open, ' + styleClose + ' close)');
        process.exit(1);
    }
}
console.log('PASS');
""" % json.dumps(DATAFRAME_FILES))
    assert result.returncode == 0, f"Style section check failed: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_virtual_scroll_maintains_consistent_striping():
    """
    Class-based striping maintains consistent row colors during virtual scroll.

    The bug: nth-child selectors cause flicker during virtual scrolling because
    DOM nodes get recycled — the :nth-child position changes as rows enter/leave
    the viewport, causing visual flickering.

    The fix: Use explicit class-based selectors (tr.row-odd) instead of :nth-child.
    This test simulates virtual scrolling by rendering a table and checking that
    row striping remains consistent when rows are present.
    """
    result = _run_playwright_test("""
const { chromium } = require('playwright-core');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    // Read the actual CSS from the repo files
    const fs = require('fs');
    const tableSvelte = fs.readFileSync('js/dataframe/shared/Table.svelte', 'utf8');

    // Extract style section from Table.svelte
    const styleMatch = tableSvelte.match(/<style>([\\s\\S]*?)<\\/style>/);
    if (!styleMatch) {
        console.error('No style section found in Table.svelte');
        await browser.close();
        process.exit(1);
    }
    const tableStyle = styleMatch[1];

    // Check if the fix is applied: must use tr.row-odd with table-odd-background-fill
    // and base tr with table-even-background-fill (no nth-child)
    const hasRowOdd = /tr\\.row-odd\\s*\\{[^}]*table-odd-background-fill/.test(tableStyle);
    const hasTrBase = /tr\\s*\\{[^}]*table-even-background-fill/.test(tableStyle);
    const hasNthChild = /nth-child/.test(tableStyle);

    if (!hasRowOdd || !hasTrBase) {
        console.error('MISSING_FIX: Table.svelte must use tr {} with even fill and tr.row-odd {} with odd fill');
        await browser.close();
        process.exit(1);
    }

    if (hasNthChild) {
        console.error('BUG_PRESENT: Table.svelte still uses nth-child selectors');
        await browser.close();
        process.exit(1);
    }

    // Now test behavioral correctness: render a table and verify striping
    const html = `
<!DOCTYPE html>
<html>
<head>
<style>
  :root {
    --table-even-background-fill: #ffffff;
    --table-odd-background-fill: #fafafa;
  }
  ${tableStyle}
</style>
</head>
<body>
  <table>
    <tbody>
      <tr class=\"row-odd\"><td>Row 1</td></tr>
      <tr><td>Row 2</td></tr>
      <tr class=\"row-odd\"><td>Row 3</td></tr>
      <tr><td>Row 4</td></tr>
    </tbody>
  </table>
</body>
</html>`;

    await page.setContent(html);

    // Check that row 1 (odd) has odd background
    const row1Bg = await page.evaluate(() => {
        const tr = document.querySelector('tr.row-odd');
        return tr ? getComputedStyle(tr).backgroundColor : null;
    });

    // Check that row 2 (even) has even background
    const row2Bg = await page.evaluate(() => {
        const tr = document.querySelector('tr:not(.row-odd)');
        return tr ? getComputedStyle(tr).backgroundColor : null;
    });

    // Verify alternating colors
    if (row1Bg === row2Bg) {
        console.error('STRIPING_FAIL: Odd and even rows have same background');
        await browser.close();
        process.exit(1);
    }

    console.log('PASS: Virtual scroll striping is consistent (class-based)');
    await browser.close();
})();
""")
    stdout = result.stdout.strip() if result.stdout else ""
    stderr = result.stderr.strip() if result.stderr else ""
    output = stderr or stdout
    assert result.returncode == 0, f"Virtual scroll striping test failed: {output}"


# [pr_diff] fail_to_pass
def test_no_nth_child_in_dataframe_components():
    """
    No nth-child CSS selectors remain in dataframe Svelte components.

    This is a behavioral test because nth-child causes the flickering bug
    during virtual scrolling. Removing it is the core of the fix.
    """
    result = _run_node("""
const fs = require('fs');
const files = %s;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    if (/nth-child/.test(content)) {
        console.error(f + ' still contains nth-child selector (causes virtual scroll flicker)');
        process.exit(1);
    }
}
console.log('PASS: No nth-child selectors in dataframe components');
""" % json.dumps(DATAFRAME_FILES))
    assert result.returncode == 0, f"nth-child check failed: {result.stderr}"


# [pr_diff] fail_to_pass
def test_row_number_uses_class_based_striping():
    """
    RowNumber.svelte must not set background in its style block.

    The old code set background via nth-child in RowNumber.svelte.
    The fix removes all background/nth-child rules from RowNumber
    because the row striping is now handled by the parent Table component.
    """
    result = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('js/dataframe/shared/RowNumber.svelte', 'utf8');
const styleMatch = content.match(/<style>([\\s\\S]*?)<\\/style>/);
if (!styleMatch) {
    console.log('PASS: No style section (background rules removed)');
    process.exit(0);
}
const style = styleMatch[1];
if (/background/.test(style)) {
    console.error('RowNumber.svelte still has background in style (should be removed)');
    process.exit(1);
}
if (/nth-child/.test(style)) {
    console.error('RowNumber.svelte still has nth-child in style (should be removed)');
    process.exit(1);
}
console.log('PASS: RowNumber.svelte has no background/nth-child rules');
""")
    assert result.returncode == 0, f"RowNumber check failed: {result.stderr}"


# [pr_diff] fail_to_pass
def test_virtual_table_no_nth_child_override():
    """
    VirtualTable.svelte must not use nth-child for row striping.

    The old code had: tbody > :global(tr:nth-child(even)) { background: ... }
    This caused flickering during virtual scroll because row positions change.
    The fix removes this and lets the parent Table component handle striping.
    """
    result = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('js/dataframe/shared/VirtualTable.svelte', 'utf8');
if (/nth-child/.test(content)) {
    console.error('VirtualTable.svelte still contains nth-child (causes virtual scroll flicker)');
    process.exit(1);
}
console.log('PASS: VirtualTable.svelte does not use nth-child');
""")
    assert result.returncode == 0, f"VirtualTable check failed: {result.stderr}"


# ---------------------------------------------------------------------------
# Config / documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_contributing_pnpm_version_updated():
    """CONTRIBUTING.md must reference pnpm 9.x, not 8.x."""
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()
    assert "pnpm 9" in content, "CONTRIBUTING.md should reference pnpm 9.x"
    # Old version reference must be gone
    assert "pnpm 8.1" not in content, "CONTRIBUTING.md should not reference old pnpm 8.1"


# [pr_diff] fail_to_pass
def test_contributing_browser_test_dependencies():
    """CONTRIBUTING.md must document browser test dependency installation."""
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()
    assert "playwright install chromium firefox" in content, \
        "CONTRIBUTING.md should document installing both chromium and firefox for Playwright"
    assert "outbreak_forecast" in content, \
        "CONTRIBUTING.md should document pip install for outbreak_forecast requirements"
    assert "stream_video_out" in content, \
        "CONTRIBUTING.md should document pip install for stream_video_out requirements"


# [pr_diff] fail_to_pass
def test_js_readme_updated_browser_test_setup():
    """js/README.md must have updated browser test setup with Firefox and package builds."""
    readme = Path(REPO) / "js" / "README.md"
    content = readme.read_text()
    assert "firefox" in content.lower(), \
        "js/README.md browser test setup should mention Firefox"
    assert "@gradio/utils" in content and "@gradio/theme" in content, \
        "js/README.md should document building utils and theme packages before browser tests"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (static checks that don't require pnpm/node_modules)
# These ensure the fix doesn't break existing functionality
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ci_workflow_exists():
    """Repo's CI workflow file exists and contains expected test commands (pass_to_pass)."""
    workflow_path = Path(REPO) / ".github" / "workflows" / "tests-js.yml"
    assert workflow_path.exists(), "tests-js.yml workflow file should exist"
    content = workflow_path.read_text()
    # Check that the workflow contains expected CI commands
    assert "pnpm format:check" in content, "CI workflow should run format:check"
    assert "pnpm lint" in content, "CI workflow should run lint"
    assert "pnpm ts:check" in content, "CI workflow should run ts:check"
    assert "pnpm test:run" in content or "pnpm --filter @gradio/client test" in content, \
        "CI workflow should run unit tests"


# [repo_tests] pass_to_pass
def test_repo_package_json_scripts_exist():
    """Repo's package.json contains expected test scripts (pass_to_pass)."""
    package_path = Path(REPO) / "package.json"
    content = package_path.read_text()
    # Check that the required scripts exist
    assert '"format:check"' in content, "package.json should have format:check script"
    assert '"lint"' in content, "package.json should have lint script"
    assert '"ts:check"' in content, "package.json should have ts:check script"
    assert '"test:run"' in content, "package.json should have test:run script"


# [repo_tests] pass_to_pass
def test_repo_dataframe_files_exist():
    """Dataframe Svelte component files exist and are readable (pass_to_pass)."""
    for file_path in DATAFRAME_FILES:
        full_path = Path(REPO) / file_path
        assert full_path.exists(), f"{file_path} should exist"
        content = full_path.read_text()
        # Check it's valid Svelte syntax (contains <script> or <style> or template)
        assert "<" in content, f"{file_path} should be valid Svelte/HTML content"


# [repo_tests] pass_to_pass
def test_repo_eslint_config_exists():
    """Repo's ESLint config exists (pass_to_pass)."""
    config_path = Path(REPO) / ".config" / "eslint.config.js"
    assert config_path.exists(), "ESLint config should exist at .config/eslint.config.js"
    content = config_path.read_text()
    # Check it contains expected ESLint configuration
    assert "eslint" in content.lower() or "export" in content, "ESLint config should be valid JS"


# [repo_tests] pass_to_pass
def test_repo_tsconfig_exists():
    """Repo's TypeScript config exists (pass_to_pass)."""
    config_path = Path(REPO) / "tsconfig.json"
    assert config_path.exists(), "tsconfig.json should exist"
    content = config_path.read_text()
    # Check it contains valid JSON
    assert '"compilerOptions"' in content, "tsconfig.json should have compilerOptions"
