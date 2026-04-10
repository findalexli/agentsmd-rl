"""
Task: gradio-dataframe-group-flicker
Repo: gradio-app/gradio @ 339811ee0d6f750e18a9ddc8e9c9bb036e328535
PR:   11282

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
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
    # Use .cjs extension since repo has "type": "module" in package.json
    test_file = Path(REPO) / "_eval_test.cjs"
    test_file.write_text(script)
    try:
        return subprocess.run(
            ["node", str(test_file)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        test_file.unlink(missing_ok=True)


def _run_pnpm_command(cmd: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a pnpm command in the repo directory, ensuring pnpm is installed."""
    # First ensure pnpm is installed
    install_result = subprocess.run(
        "npm install -g pnpm@9 2>/dev/null && pnpm install --frozen-lockfile 2>/dev/null",
        shell=True,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Run the actual command
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax / compilation checks
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
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_virtual_scroll_maintains_consistent_striping():
    """
    Class-based striping maintains consistent row colors during virtual scroll.

    The bug: nth-child selectors cause flicker during virtual scrolling because
    DOM nodes get recycled — the :nth-child position changes as rows enter/leave
    the viewport, causing visual flickering.

    The fix: Use explicit class-based selectors (tr.row-odd) instead of :nth-child.
    This test verifies that Table.svelte uses the correct class-based striping.
    """
    from playwright.sync_api import sync_playwright

    table_svelte = Path(REPO) / "js/dataframe/shared/Table.svelte"
    content = table_svelte.read_text()

    # Extract style section from Table.svelte
    style_match = re.search(r'<style>([\s\S]*?)</style>', content)
    assert style_match, "No style section found in Table.svelte"
    table_style = style_match.group(1)

    # Check if the fix is applied: must use tr.row-odd with table-odd-background-fill
    # and base tr with table-even-background-fill (no nth-child for row striping)
    has_row_odd = re.search(r'tr\.row-odd\s*\{[^}]*table-odd-background-fill', table_style)
    has_tr_base = re.search(r'tr\s*\{[^}]*table-even-background-fill', table_style)
    has_nth_child = re.search(r'tr:nth-child\([^)]*\)\s*\{[^}]*background', table_style)

    assert has_row_odd and has_tr_base, \
        "Table.svelte must use tr {} with even fill and tr.row-odd {} with odd fill"
    assert not has_nth_child, \
        "Table.svelte still uses nth-child selectors for row striping"

    # Now test behavioral correctness: render a table and verify striping
    html = f"""<!DOCTYPE html>
<html>
<head>
<style>
  :root {{
    --table-even-background-fill: #ffffff;
    --table-odd-background-fill: #fafafa;
  }}
  {table_style}
</style>
</head>
<body>
  <table>
    <tbody>
      <tr class="row-odd"><td>Row 1</td></tr>
      <tr><td>Row 2</td></tr>
      <tr class="row-odd"><td>Row 3</td></tr>
      <tr><td>Row 4</td></tr>
    </tbody>
  </table>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html)

        # Check that row-odd has different background than non-row-odd
        row1_bg = page.evaluate("""() => {
            const tr = document.querySelector('tr.row-odd');
            return tr ? getComputedStyle(tr).backgroundColor : null;
        }""")
        row2_bg = page.evaluate("""() => {
            const tr = document.querySelector('tr:not(.row-odd)');
            return tr ? getComputedStyle(tr).backgroundColor : null;
        }""")
        browser.close()

    assert row1_bg != row2_bg, \
        f"STRIPING_FAIL: Odd and even rows have same background ({row1_bg})"


# [pr_diff] fail_to_pass
def test_no_nth_child_in_dataframe_components():
    """
    No nth-child CSS selectors for row striping remain in dataframe Svelte components.

    This is a behavioral test because nth-child on table rows causes the flickering bug
    during virtual scrolling - as rows enter/leave viewport, :nth-child positions change
    causing visual flickering. The fix replaces these with class-based selectors.

    Note: nth-child on .pinned-column elements is allowed as those don't virtual scroll.
    """
    result = _run_node("""
const fs = require('fs');
const files = %s;
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    // Check for nth-child applied directly to tr elements (the problematic pattern)
    // This catches: tbody > :global(tr:nth-child(even)) { background: ... }
    // But allows: tbody :global(tr:nth-child(odd)) :global(td.pinned-column)
    if (/tr:nth-child\([^)]*\)\s*\{[^}]*background/.test(content)) {
        console.error(f + ' still contains nth-child row striping (causes virtual scroll flicker)');
        process.exit(1);
    }
}
console.log('PASS: No nth-child row striping in dataframe components');
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

    Note: nth-child rules for .pinned-column are kept as they don't virtual scroll.
    """
    result = _run_node("""
const fs = require('fs');
const content = fs.readFileSync('js/dataframe/shared/VirtualTable.svelte', 'utf8');
// Check for the specific problematic pattern: nth-child on tr elements for background
if (/tr:nth-child\([^)]*\)\s*\{[^}]*background/.test(content)) {
    console.error('VirtualTable.svelte still contains nth-child row striping (causes virtual scroll flicker)');
    process.exit(1);
}
console.log('PASS: VirtualTable.svelte does not use nth-child for row striping');
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
# Repo CI/CD pass_to_pass gates (actual CI commands via subprocess.run)
# These run the repo's actual CI commands to ensure the fix doesn't break anything
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    r = _run_pnpm_command("pnpm format:check")
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = _run_pnpm_command("pnpm lint")
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_check():
    """Repo's TypeScript check passes (pass_to_pass)."""
    r = _run_pnpm_command("pnpm ts:check")
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    r = _run_pnpm_command("pnpm test:run")
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"
