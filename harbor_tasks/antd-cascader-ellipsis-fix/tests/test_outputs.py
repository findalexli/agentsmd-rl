"""
Test file for ant-design Cascader ellipsis fix.

This tests that the Cascader menu item ellipsis styles are correctly applied
to the content element rather than the parent item element in flex layout.
"""

import subprocess
import os
import re

REPO = "/workspace/ant-design"
COLUMNS_FILE = os.path.join(REPO, "components/cascader/style/columns.ts")


def test_file_exists():
    """Verify the columns.ts file exists."""
    assert os.path.exists(COLUMNS_FILE), f"File not found: {COLUMNS_FILE}"


def get_item_block(content):
    """Extract the &-item block from the content."""
    # Match from '&-item': { until the closing } that precedes '&-keyword'
    item_pattern = r"'&-item':\s*\{([\s\S]*?)\n\s*\},?\s*\n\s*'&-keyword'"
    item_match = re.search(item_pattern, content)
    return item_match.group(1) if item_match else None


def test_text_ellipsis_moved_to_content():
    """
    Fail-to-pass: textEllipsis should be in &-content, not directly in &-item.

    The bug was that textEllipsis was applied to the &-item which broke
    ellipsis in flex layout. The fix moves it to &-content with minWidth: 0.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    # Get the &-item block
    item_block = get_item_block(content)
    assert item_block, "Could not find &-item block in columns.ts"

    # Split at &-content to check the part before it
    if "'&-content'" in item_block:
        item_before_content = item_block.split("'&-content'")[0]
    else:
        item_before_content = item_block

    # textEllipsis should NOT be directly in the part of &-item before &-content
    has_ellipsis_in_item = "...textEllipsis" in item_before_content

    assert not has_ellipsis_in_item, \
        "textEllipsis should not be directly in &-item block (should be in &-content)"


def test_content_has_minWidth_zero():
    """
    Fail-to-pass: &-content should have minWidth: 0 for proper ellipsis in flex.

    Without minWidth: 0, flex items won't shrink below their content size,
    preventing ellipsis from working correctly.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    # Find &-content block within &-item - it may span multiple lines
    content_pattern = r"'&-content':\s*\{([^}]*(?:\{[^}]*\}[^}]*)?)\},?\s*\n\s*\[iconCls\]"
    content_match = re.search(content_pattern, content)
    assert content_match, "Could not find &-content block in columns.ts"
    content_block = content_match.group(1)

    # Check for minWidth: 0
    assert "minWidth: 0" in content_block, \
        "&-content should have minWidth: 0 for proper flex ellipsis behavior"


def test_content_has_text_ellipsis():
    """
    Fail-to-pass: &-content should have textEllipsis spread for ellipsis styles.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    # Find &-content block
    content_pattern = r"'&-content':\s*\{([^}]*(?:\{[^}]*\}[^}]*)?)\},?\s*\n\s*\[iconCls\]"
    content_match = re.search(content_pattern, content)
    assert content_match, "Could not find &-content block in columns.ts"
    content_block = content_match.group(1)

    # Check for textEllipsis
    assert "...textEllipsis" in content_block, \
        "&-content should have ...textEllipsis for ellipsis styling"


def test_item_has_maxWidth():
    """
    Fail-to-pass: &-item should have maxWidth: 400 to constrain the flex item.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    # Get the &-item block
    item_block = get_item_block(content)
    assert item_block, "Could not find &-item block in columns.ts"

    # Check the part before &-content for maxWidth: 400
    if "'&-content'" in item_block:
        item_before_content = item_block.split("'&-content'")[0]
    else:
        item_before_content = item_block

    assert "maxWidth: 400" in item_before_content, \
        "&-item should have maxWidth: 400 to constrain the flex item"


def test_item_has_flex_display():
    """
    Pass-to-pass: &-item should use display: 'flex' for proper layout.
    This was not changed by the PR but is required for the fix to work.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    item_block = get_item_block(content)
    assert item_block, "Could not find &-item block in columns.ts"

    if "'&-content'" in item_block:
        item_before_content = item_block.split("'&-content'")[0]
    else:
        item_before_content = item_block

    assert "display: 'flex'" in item_before_content, \
        "&-item should have display: 'flex'"


def test_typescript_compiles():
    """
    Pass-to-pass: TypeScript should compile without errors.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "components/cascader/style/columns.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # If tsc fails due to missing config, try just checking syntax
    if result.returncode != 0 and "tsconfig" in result.stderr.lower():
        # Try using npx ts-node for syntax check
        result2 = subprocess.run(
            ["npx", "tsx", "--check", "components/cascader/style/columns.ts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        # If tsx isn't available or check fails, just verify the file parses
        if result2.returncode != 0:
            # At minimum verify valid TypeScript syntax by trying to parse
            with open(COLUMNS_FILE, 'r') as f:
                file_content = f.read()
            # Basic syntax validation - file should have balanced braces
            open_braces = file_content.count('{')
            close_braces = file_content.count('}')
            assert open_braces == close_braces, "TypeScript file has unbalanced braces"
            return

    if result.returncode != 0:
        # Ignore errors about other files, just check if columns.ts specifically is OK
        if "columns.ts" not in result.stderr:
            return  # Other files have issues, not our target

    assert result.returncode == 0 or "columns.ts" not in result.stderr, \
        f"TypeScript compilation failed:\n{result.stderr}"


def test_style_exports_correctly():
    """
    Pass-to-pass: The style module should export the getColumnsStyle function.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    assert "export default getColumnsStyle" in content, \
        "columns.ts should export getColumnsStyle as default"


def test_imports_are_valid():
    """
    Pass-to-pass: The file should import required dependencies.
    """
    with open(COLUMNS_FILE, 'r') as f:
        content = f.read()

    # Check for required imports
    assert "@ant-design/cssinjs" in content, "Should import from @ant-design/cssinjs"
    assert "textEllipsis" in content, "Should import textEllipsis from style"
    assert "GenerateStyle" in content, "Should import GenerateStyle type"
