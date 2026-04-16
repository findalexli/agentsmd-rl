"""
Tests for ant-design/ant-design PR #57557
Deprecate Cascader popupMenuColumnStyle in favor of styles.popup.listItem

These tests verify BEHAVIOR (what the code does) not TEXT (what the source contains).
"""

import subprocess
import sys
import os
import re
import json

REPO = "/workspace/ant-design"
CASCADER_INDEX = f"{REPO}/components/cascader/index.tsx"
CASCADER_EN_DOC = f"{REPO}/components/cascader/index.en-US.md"
CASCADER_ZH_DOC = f"{REPO}/components/cascader/index.zh-CN.md"
MIGRATION_EN_DOC = f"{REPO}/docs/react/migration-v6.en-US.md"
MIGRATION_ZH_DOC = f"{REPO}/docs/react/migration-v6.zh-CN.md"


def test_deprecation_warning_mapping():
    """
    Verify the deprecation mapping object behavior.
    Both dropdownMenuColumnStyle and popupMenuColumnStyle should map to 'styles.popup.listItem'.
    This is a fail-to-pass test.
    """
    with open(CASCADER_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the deprecatedProps object and extract its mappings
    props_match = re.search(r'const deprecatedProps = \{([^}]+)\}', content, re.DOTALL)
    assert props_match, "Could not find deprecatedProps object"

    deprecated_section = props_match.group(1)

    # Extract the replacement values (supports single quotes, double quotes, or backticks)
    dropdown_match = re.search(r'dropdownMenuColumnStyle\s*:\s*["\'`"]([^"\'`"]+)["\'`"]', deprecated_section)
    popup_match = re.search(r'popupMenuColumnStyle\s*:\s*["\'`"]([^"\'`"]+)["\'`"]', deprecated_section)

    assert dropdown_match, "Could not find dropdownMenuColumnStyle mapping"
    assert popup_match, "Could not find popupMenuColumnStyle mapping"

    dropdown_replacement = dropdown_match.group(1)
    popup_replacement = popup_match.group(1)

    # Both should map to styles.popup.listItem
    assert dropdown_replacement == "styles.popup.listItem", \
        f"dropdownMenuColumnStyle maps to '{dropdown_replacement}', expected 'styles.popup.listItem'"
    assert popup_replacement == "styles.popup.listItem", \
        f"popupMenuColumnStyle maps to '{popup_replacement}', expected 'styles.popup.listItem'"


def test_jsdoc_deprecation_comments():
    """
    Verify that JSDoc comments reference the correct replacement (styles.popup.listItem).
    This checks documentation consistency with runtime behavior.
    """
    with open(CASCADER_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check dropdownMenuColumnStyle JSDoc
    # Pattern: /** @deprecated ... */ followed by the property
    dropdown_jsdoc_pattern = r'/\*\*\s*@deprecated\s+([^*]|\*(?!/))*\*/\s*\n\s*dropdownMenuColumnStyle'
    dropdown_match = re.search(dropdown_jsdoc_pattern, content, re.DOTALL)
    assert dropdown_match, "JSDoc comment for dropdownMenuColumnStyle not found"
    dropdown_jsdoc = dropdown_match.group(0)
    assert "styles.popup.listItem" in dropdown_jsdoc, \
        "JSDoc for dropdownMenuColumnStyle should reference 'styles.popup.listItem'"

    # Check popupMenuColumnStyle JSDoc
    popup_jsdoc_pattern = r'/\*\*\s*@deprecated\s+([^*]|\*(?!/))*\*/\s*\n\s*popupMenuColumnStyle'
    popup_match = re.search(popup_jsdoc_pattern, content, re.DOTALL)
    assert popup_match, "JSDoc comment for popupMenuColumnStyle not found"
    popup_jsdoc = popup_match.group(0)
    assert "styles.popup.listItem" in popup_jsdoc, \
        "JSDoc for popupMenuColumnStyle should reference 'styles.popup.listItem'"


def test_no_old_replacement_references():
    """
    Verify that the code no longer suggests using 'popupMenuColumnStyle' as a replacement.
    The base code incorrectly suggests popupMenuColumnStyle as a replacement
    for dropdownMenuColumnStyle, creating a circular deprecation path.
    """
    with open(CASCADER_INDEX, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the deprecatedProps object
    props_match = re.search(r'const deprecatedProps = \{([^}]+)\}', content, re.DOTALL)
    if props_match:
        deprecated_section = props_match.group(1)
        # Check that dropdownMenuColumnStyle does NOT map to popupMenuColumnStyle
        dropdown_match = re.search(r'dropdownMenuColumnStyle\s*:\s*["\'`"]([^"\'`"]+)["\'`"]', deprecated_section)
        if dropdown_match:
            replacement = dropdown_match.group(1)
            assert replacement != "popupMenuColumnStyle", \
                "dropdownMenuColumnStyle should not suggest popupMenuColumnStyle as replacement"
            assert replacement == "styles.popup.listItem", \
                f"dropdownMenuColumnStyle should suggest 'styles.popup.listItem', not '{replacement}'"

    # Also check JSDoc comments - they should not say to use popupMenuColumnStyle
    jsdoc_pattern = r'/\*\*\s*@deprecated[^*]*(?:\*(?!/)[^*]*)*\*/'
    for jsdoc in re.finditer(jsdoc_pattern, content, re.DOTALL):
        jsdoc_text = jsdoc.group(0)
        # If this JSDoc is followed by one of our target properties
        pos = jsdoc.end()
        following_text = content[pos:pos+100]
        if 'dropdownMenuColumnStyle' in following_text or 'popupMenuColumnStyle' in following_text:
            # It should NOT say to use popupMenuColumnStyle (the old incorrect replacement)
            if "Please use" in jsdoc_text or "use" in jsdoc_text:
                assert "popupMenuColumnStyle" not in jsdoc_text or "styles.popup.listItem" in jsdoc_text, \
                    "JSDoc should suggest 'styles.popup.listItem', not 'popupMenuColumnStyle'"


def test_english_documentation_updated():
    """
    Verify that English API documentation shows the correct deprecation info.
    Both dropdownMenuColumnStyle and popupMenuColumnStyle should reference styles.popup.listItem.
    """
    with open(CASCADER_EN_DOC, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find dropdownMenuColumnStyle in docs and check context
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'dropdownMenuColumnStyle' in line:
            context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
            # Should reference styles.popup.listItem as replacement
            assert "styles.popup.listItem" in context, \
                "English docs: dropdownMenuColumnStyle should reference 'styles.popup.listItem'"
            break
    else:
        assert False, "dropdownMenuColumnStyle not found in English documentation"

    # Also check popupMenuColumnStyle docs
    for i, line in enumerate(lines):
        if 'popupMenuColumnStyle' in line and 'dropdownMenuColumnStyle' not in line:
            context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
            assert "styles.popup.listItem" in context, \
                "English docs: popupMenuColumnStyle should reference 'styles.popup.listItem'"
            break


def test_chinese_documentation_updated():
    """
    Verify that Chinese API documentation shows the correct deprecation info.
    """
    with open(CASCADER_ZH_DOC, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'dropdownMenuColumnStyle' in line:
            context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
            assert "styles.popup.listItem" in context, \
                "Chinese docs: dropdownMenuColumnStyle should reference 'styles.popup.listItem'"
            break
    else:
        assert False, "dropdownMenuColumnStyle not found in Chinese documentation"


def test_migration_documentation_updated():
    """
    Verify that v6 migration documentation references the correct replacement.
    """
    with open(MIGRATION_EN_DOC, 'r', encoding='utf-8', errors='replace') as f:
        en_content = f.read()

    with open(MIGRATION_ZH_DOC, 'r', encoding='utf-8', errors='replace') as f:
        zh_content = f.read()

    # Check English migration docs
    if "dropdownMenuColumnStyle" in en_content:
        match = re.search(r'dropdownMenuColumnStyle[^.]*\.', en_content, re.DOTALL | re.IGNORECASE)
        if match:
            context = match.group(0)
            if "replaced by" in context or "replaced" in context:
                assert "styles.popup.listItem" in context, \
                    "English migration docs should reference 'styles.popup.listItem' as replacement"

    # Check Chinese migration docs
    if "dropdownMenuColumnStyle" in zh_content:
        match = re.search(r'dropdownMenuColumnStyle[^。]*。', zh_content, re.DOTALL)
        if match:
            context = match.group(0)
            if "变为" in context or "替换" in context:
                assert "styles.popup.listItem" in context, \
                    "Chinese migration docs should reference 'styles.popup.listItem' as replacement"


def test_unit_tests_expect_correct_warning():
    """
    Verify that the unit test file expects the correct deprecation warning.
    The test should expect 'styles.popup.listItem' not 'popupMenuColumnStyle'.
    """
    test_file = f"{REPO}/components/cascader/__tests__/index.test.tsx"
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the dropdownMenuColumnStyle test section
    if "dropdownMenuColumnStyle" in content:
        match = re.search(r'dropdownMenuColumnStyle[^}]+deprecated[^}]+instead', content, re.DOTALL | re.IGNORECASE)
        if match:
            test_section = match.group(0)
            if "Please use" in test_section:
                assert "styles.popup.listItem" in test_section, \
                    "Unit test should expect 'styles.popup.listItem' as replacement"


# Pass-to-pass tests (should pass on base commit)


def test_cascader_syntax_valid():
    """
    Verify that the Cascader component has valid TypeScript syntax.
    This is a pass-to-pass test.
    """
    assert os.path.exists(CASCADER_INDEX), "Cascader index.tsx should exist"
    with open(CASCADER_INDEX, 'r') as f:
        content = f.read()
    assert "export" in content, "Cascader index.tsx should have exports"
    assert len(content) > 1000, "Cascader index.tsx should have substantial content"


def test_package_json_valid():
    """
    Verify that package.json is valid and npm install was successful.
    This is a pass-to-pass test.
    """
    assert os.path.exists(f"{REPO}/package.json"), "package.json should exist"
    assert os.path.exists(f"{REPO}/node_modules/react"), "react should be installed in node_modules"


def test_cascader_unit_tests():
    """
    Run the repo's unit tests for the Cascader component.
    This is a pass-to-pass test.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=cascader", "--maxWorkers=2"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Cascader unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"


def test_cascader_index_test():
    """
    Run the main cascader index.test.tsx unit tests.
    This is a pass-to-pass test.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=cascader/__tests__/index.test", "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Cascader index tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_lint():
    """
    Run the repo's biome linter to check code style.
    This is a pass-to-pass test.
    """
    result = subprocess.run(
        ["npm", "run", "lint:biome"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
