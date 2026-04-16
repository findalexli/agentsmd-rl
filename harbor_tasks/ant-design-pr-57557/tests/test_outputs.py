"""
Tests for ant-design/ant-design#57557
Deprecate Cascader popupMenuColumnStyle in favor of styles.popup.listItem

These tests verify BEHAVIOR by running the actual test suite and verifying
that deprecation warnings are correctly emitted with the right replacement API.
"""
import subprocess
import os
import re

REPO = "/workspace/antd"


def run_cascader_tests_and_check_deprecation(test_filter=None):
    """
    Run Cascader tests and verify deprecation warning behavior.
    Returns (passed, output) where passed=True means the deprecation tests worked.
    """
    cmd = ["npm", "run", "test", "--", "components/cascader/__tests__/index.test.tsx"]
    if test_filter:
        cmd.extend(["-t", test_filter])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO
    )
    output = result.stdout + result.stderr

    # Check if test exists (not skipped due to no match)
    if "Test Suites: 1 skipped" in output or "No tests matched" in output.lower():
        return False, f"Test did not run (skipped or no match):\n{output[-2000:]}"

    # For filtered runs, check pass/fail
    if test_filter:
        if result.returncode != 0:
            return False, f"Test failed:\n{output[-2000:]}"
        return True, output

    # For full runs, check exit code
    if result.returncode != 0:
        return False, f"Tests failed:\n{output[-2000:]}"
    return True, output


def test_dropdown_deprecation_warns_about_styles_popup_listitem():
    """
    Fail-to-pass: dropdownMenuColumnStyle deprecation warning should reference
    styles.popup.listItem as the replacement (not popupMenuColumnStyle).

    Verifies behavior by running the legacy dropdownMenuColumnStyle test.
    The test checks the deprecation warning message emitted at runtime.
    """
    passed, output = run_cascader_tests_and_check_deprecation(
        test_filter="legacy dropdownMenuColumnStyle"
    )
    assert passed, f"Legacy dropdownMenuColumnStyle test should pass with correct warning message:\n{output}"


def test_popup_menu_column_style_is_deprecated():
    """
    Fail-to-pass: popupMenuColumnStyle should be deprecated and emit a warning
    pointing to styles.popup.listItem.

    Verifies behavior by running the popupMenuColumnStyle deprecation test.
    """
    passed, output = run_cascader_tests_and_check_deprecation(
        test_filter="deprecated popupMenuColumnStyle"
    )
    assert passed, f"popupMenuColumnStyle deprecation test should pass:\n{output}"


def test_styles_popup_listitem_precedence():
    """
    Fail-to-pass: styles.popup.listItem should take precedence over
    popupMenuColumnStyle when both are provided.

    Verifies behavior by running the override test.
    """
    passed, output = run_cascader_tests_and_check_deprecation(
        test_filter="styles.popup.listItem should override"
    )
    assert passed, f"Override precedence test should pass:\n{output}"


def test_all_cascader_tests_pass():
    """
    Fail-to-pass: All Cascader tests should pass after the fix is applied.
    This is a comprehensive check that the fix doesn't break anything.

    In NOP state, the test for legacy dropdownMenuColumnStyle will fail
    because the warning message still says to use popupMenuColumnStyle.
    In GOLD state, all tests pass.
    """
    passed, output = run_cascader_tests_and_check_deprecation()
    assert passed, f"Not all Cascader tests passed:\n{output[-3000:]}"


def test_cascader_component_syntax():
    """
    Pass-to-pass: The Cascader component file should have valid TypeScript syntax.
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
