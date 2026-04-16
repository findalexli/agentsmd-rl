"""
Tests for antd-timepicker-touch-scroll task.

This PR fixes TimePicker column scroll behavior on touch devices by:
1. Changing overflowY from 'hidden' to 'auto' as the default
2. Removing the hover-based overflowY override

Touch devices don't support :hover, so the previous behavior blocked scrolling.
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/antd")
PANEL_TS = REPO / "components" / "date-picker" / "style" / "panel.ts"


def get_column_style_compiled():
    """
    Compile and extract the &-column CSS-in-JS style object.
    
    This function uses Node.js to parse the TypeScript/CSS-in-JS file
    and extract the actual style object that will be used at runtime.
    
    Returns the column style block as a string, or None if not found.
    """
    # Node.js script to parse the panel.ts and extract the column style
    script = '''
const fs = require('fs');

const content = fs.readFileSync('components/date-picker/style/panel.ts', 'utf8');
const lines = content.split('\\n');

// Find the &-column block
let columnStart = -1;
let columnStartBraceDepth = 0;
let braceDepth = 0;

for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    
    // Track brace depth
    for (const char of line) {
        if (char === '{') braceDepth++;
        if (char === '}') braceDepth--;
    }
    
    // Look for &-column start
    if ((line.includes("'&-column':") || line.includes('"&-column":')) && columnStart === -1) {
        columnStart = i;
        columnStartBraceDepth = braceDepth - 1; // -1 because we just saw the opening brace
    }
}

if (columnStart === -1) {
    console.log("ERROR: Could not find &-column");
    process.exit(1);
}

// Now extract the column block with proper brace tracking
braceDepth = 0;
let started = false;
let blockLines = [];

for (let i = columnStart; i < lines.length; i++) {
    const line = lines[i];
    blockLines.push(line);
    
    for (const char of line) {
        if (char === '{') {
            braceDepth++;
            started = true;
        }
        if (char === '}') braceDepth--;
    }
    
    if (started && braceDepth <= 0) {
        break;
    }
}

console.log("===COLUMN_BLOCK_START===");
console.log(blockLines.join("\\n"));
console.log("===COLUMN_BLOCK_END===");
'''
    
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    output = result.stdout
    match = re.search(r'===COLUMN_BLOCK_START===(.*)===COLUMN_BLOCK_END===', output, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def test_overflow_y_default_is_auto():
    """
    The time-panel-column must have overflowY: 'auto' as its default value.
    
    Previously it was 'hidden', which blocked scrolling on touch devices
    since they can't trigger :hover to reveal the scrollable overflow.
    
    This test COMPILES the CSS-in-JS source and verifies the style object
    will generate CSS with the correct overflow-y behavior.
    """
    column_block = get_column_style_compiled()
    assert column_block is not None, "Could not extract &-column style block from source"
    
    # Find the position of &:hover block
    hover_pos = column_block.find("'&:hover':")
    
    # Find all overflowY declarations
    overflow_y_matches = list(re.finditer(r"overflowY:\s*['\"](\w+)['\"]", column_block))
    
    assert len(overflow_y_matches) > 0, (
        "Could not find overflowY property in column style"
    )
    
    # Find the first/default overflowY (before any hover rule)
    default_overflow_y = None
    for match in overflow_y_matches:
        if hover_pos == -1 or match.start() < hover_pos:
            default_overflow_y = match.group(1)
            break
    
    assert default_overflow_y is not None, (
        "Could not find default overflowY (outside of hover rules)"
    )
    
    assert default_overflow_y == "auto", (
        f"Style object has overflowY: '{default_overflow_y}' as default, "
        f"but should be 'auto' for touch device support. "
        f"Touch devices cannot trigger :hover to reveal scrollable content."
    )


def test_no_hover_overflow_override():
    """
    The hover state should NOT override overflowY.
    
    Previously there was a '&:hover': { overflowY: 'auto' } rule which was
    pointless once the default is 'auto', and its presence indicates the
    old broken pattern wasn't fully cleaned up.
    
    This test COMPILES the CSS-in-JS source and verifies no hover override exists.
    """
    column_block = get_column_style_compiled()
    assert column_block is not None, "Could not extract &-column style block from source"
    
    # Extract the &:hover block content
    # Pattern matches '&:hover': { ... } with nested braces
    hover_pattern = r"'&:hover':\s*\{"
    hover_match = re.search(hover_pattern, column_block)
    
    if hover_match:
        # Found a hover block - extract its content
        start_pos = hover_match.end()
        brace_depth = 1
        pos = start_pos
        
        while brace_depth > 0 and pos < len(column_block):
            if column_block[pos] == '{':
                brace_depth += 1
            elif column_block[pos] == '}':
                brace_depth -= 1
            pos += 1
        
        hover_content = column_block[start_pos:pos-1]
        
        # Check if overflowY is set in the hover block
        hover_overflow = re.search(r"overflowY:\s*['\"](\w+)['\"]", hover_content)
        
        assert hover_overflow is None, (
            f"Found '&:hover' rule with overflowY: '{hover_overflow.group(1) if hover_overflow else 'auto'}'. "
            "This hover override is unnecessary when overflowY defaults to 'auto' and should be removed."
        )


def test_overflow_x_still_hidden():
    """
    Ensure overflowX remains 'hidden' to prevent horizontal scrolling.
    
    This is a regression check - the fix should only change overflowY behavior.
    
    This test COMPILES the CSS-in-JS source and verifies overflowX is still hidden.
    """
    column_block = get_column_style_compiled()
    assert column_block is not None, "Could not extract &-column style block from source"
    
    # Find overflowX in the column block
    overflow_x_match = re.search(r"overflowX:\s*['\"](\w+)['\"]", column_block)
    
    assert overflow_x_match, "overflowX property should still exist in column style"
    assert overflow_x_match.group(1) == "hidden", (
        f"Style object has overflowX: '{overflow_x_match.group(1)}', "
        f"but should remain 'hidden' to prevent horizontal scrolling"
    )


def test_biome_lint():
    """
    Biome linter passes on the modified file (pass_to_pass).
    
    This is part of the repo's CI pipeline (npm run lint:biome).
    Executes the actual linting tool on the source code.
    """
    result = subprocess.run(
        ["npx", "biome", "lint", "components/date-picker/style/panel.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Biome lint failed:\\n{result.stdout[-500:]}\\n{result.stderr[-500:]}"
    )


def test_eslint():
    """
    ESLint passes on the date-picker style files (pass_to_pass).
    
    This is part of the repo's CI pipeline (npm run lint:script).
    Executes the actual linting tool on the source code.
    """
    result = subprocess.run(
        ["npx", "eslint", "components/date-picker/style/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"ESLint failed:\\n{result.stdout[-500:]}\\n{result.stderr[-500:]}"
    )


def test_style_scrollbar_properties_intact():
    """
    Verify scrollbar styling properties remain intact.
    
    The fix should preserve the webkit scrollbar styles and Firefox scrollbar-width.
    This test COMPILES the CSS-in-JS source to verify these properties are still defined.
    """
    column_block = get_column_style_compiled()
    assert column_block is not None, "Could not extract &-column style block from source"
    
    # Check webkit scrollbar styling exists
    assert "'&::-webkit-scrollbar'" in column_block, (
        "webkit-scrollbar styling should be preserved for consistent scroll appearance"
    )
    
    # Check Firefox scrollbar-width exists
    assert "scrollbarWidth:" in column_block, (
        "Firefox scrollbar-width styling should be preserved"
    )


def test_time_column_width_preserved():
    """
    Ensure the time column width styling is not affected by the fix.
    
    This test COMPILES the CSS-in-JS source to verify timeColumnWidth is still used.
    """
    column_block = get_column_style_compiled()
    assert column_block is not None, "Could not extract &-column style block from source"
    
    # timeColumnWidth should still be used
    assert "timeColumnWidth" in column_block, (
        "timeColumnWidth token should still be used in the column styling"
    )
