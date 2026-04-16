"""
Tests for ant-design/ant-design#57557
Deprecate Cascader popupMenuColumnStyle in favor of styles.popup.listItem

These tests verify BEHAVIOR by running the actual test suite and checking:
1. Deprecation warnings are properly emitted at runtime
2. The runtime behavior correctly applies styles.popup.listItem
"""
import subprocess
import os

REPO = "/workspace/antd"


def run_jest_test(test_path, test_name_pattern, description):
    """
    Run a jest test and verify it actually executes (not just skips).
    Returns (success, output) tuple.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", test_path, "-t", test_name_pattern],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    output = result.stdout + result.stderr
    
    # Check that tests actually ran (not just skipped)
    # Look for patterns like "PASS" or "FAIL" with the test name
    if "Test Suites: 1 skipped" in output:
        return False, f"{description}: No tests matched pattern - test may not exist\n{output[-2000:]}"
    
    # Also check for actual test results
    if "PASS" not in output and "FAIL" not in output:
        return False, f"{description}: No test results found\n{output[-2000:]}"
    
    if result.returncode != 0:
        return False, f"{description}: Test failed\n{output[-2000:]}"
    
    return True, output


def test_dropdown_deprecation_warning_points_to_styles_popup_listitem():
    """
    Fail-to-pass: Using dropdownMenuColumnStyle should produce a deprecation
    warning pointing to styles.popup.listItem (not popupMenuColumnStyle).

    This test runs the actual Cascader test that checks the warning message.
    Verifies the runtime behavior emits correct deprecation warning.
    """
    success, output = run_jest_test(
        "components/cascader/__tests__/index.test.tsx",
        "legacy dropdownMenuColumnStyle",
        "dropdownMenuColumnStyle deprecation warning test"
    )
    assert success, output


def test_popup_menu_column_style_emits_deprecation_warning():
    """
    Fail-to-pass: Using popupMenuColumnStyle should produce a deprecation
    warning pointing to styles.popup.listItem.

    This test runs the actual Cascader test that checks the warning message.
    Verifies the runtime behavior emits correct deprecation warning.
    """
    success, output = run_jest_test(
        "components/cascader/__tests__/index.test.tsx",
        "deprecated popupMenuColumnStyle",
        "popupMenuColumnStyle deprecation warning test"
    )
    assert success, output


def test_styles_popup_listitem_overrides_popup_menu_column_style():
    """
    Fail-to-pass: styles.popup.listItem should take precedence over
    popupMenuColumnStyle at runtime.

    This test verifies the actual runtime styling behavior.
    """
    success, output = run_jest_test(
        "components/cascader/__tests__/index.test.tsx",
        "styles.popup.listItem should override popupMenuColumnStyle",
        "styles.popup.listItem override test"
    )
    assert success, output


def test_cascader_component_syntax():
    """
    Pass-to-pass: The Cascader component file should have valid TypeScript syntax.
    Uses node to parse the TypeScript file.
    """
    result = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const source = fs.readFileSync('components/cascader/index.tsx', 'utf8');
const result = ts.createSourceFile('index.tsx', source, ts.ScriptTarget.Latest, true);
if (result.parseDiagnostics && result.parseDiagnostics.length > 0) {
    console.error('Parse errors:', result.parseDiagnostics);
    process.exit(1);
}
console.log('Syntax valid');
"""],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Cascader index.tsx has syntax errors:\n{result.stderr}"
    )


def test_repo_eslint_cascader():
    """
    Pass-to-pass: ESLint check passes on cascader component files.
    """
    result = subprocess.run(
        ["npx", "eslint", "components/cascader/", "--ext", ".tsx,.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"ESLint failed on cascader files:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_biome_lint_cascader():
    """
    Pass-to-pass: Biome lint check passes on cascader index.tsx.
    """
    result = subprocess.run(
        ["npx", "biome", "lint", "components/cascader/index.tsx"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Biome lint failed on cascader:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_cascader_semantic_tests():
    """
    Pass-to-pass: Cascader semantic tests pass.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "components/cascader/__tests__/semantic.test.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Cascader semantic tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
    )


def test_repo_markdown_lint_cascader_docs():
    """
    Pass-to-pass: Markdown linting passes on cascader documentation.
    """
    result = subprocess.run(
        ["npm", "run", "lint:md", "--",
         "components/cascader/index.en-US.md",
         "components/cascader/index.zh-CN.md"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Markdown lint failed on cascader docs:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_markdown_lint_migration_docs():
    """
    Pass-to-pass: Markdown linting passes on v6 migration documentation.
    """
    result = subprocess.run(
        ["npm", "run", "lint:md", "--",
         "docs/react/migration-v6.en-US.md",
         "docs/react/migration-v6.zh-CN.md"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Markdown lint failed on migration docs:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_cascader_all_tests_pass():
    """
    Pass-to-pass: All Cascader component tests pass.
    This ensures the behavioral changes don't break existing functionality.
    """
    result = subprocess.run(
        ["npm", "run", "test", "--", "components/cascader/__tests__/index.test.tsx"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO
    )
    assert result.returncode == 0, (
        f"Cascader index tests failed:\n{result.stdout[-3000:]}\n{result.stderr[-500:]}"
    )
