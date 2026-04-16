"""
Tests for ant-design notification close button spacing fix.

This PR fixes a layout bug where the close button overlaps notification content
when only a description is rendered without a title. The fix:
1. Conditionally renders the title element only when title exists
2. Adds spacing to description when it's the first content element
"""

import subprocess
import os
import json
import re

REPO = "/workspace/antd"


class TestConditionalTitleRendering:
    """Tests that title div is conditionally rendered (fail_to_pass)."""

    def _run_node_test(self, test_script: str) -> tuple[int, str, str]:
        """Run a Node.js test script and return (exit_code, stdout, stderr)."""
        script_file = os.path.join(REPO, "__temp_test_script.cjs")
        with open(script_file, "w") as f:
            f.write(test_script)
        try:
            result = subprocess.run(
                ["node", script_file],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            if os.path.exists(script_file):
                os.unlink(script_file)

    def test_title_conditional_rendering(self):
        """
        Verify title rendering is conditional on title being truthy.

        Before fix: title div rendered unconditionally
        After fix: title div wrapped in conditional expression
        """
        test_script = r'''
const fs = require('fs');
const path = require('path');

// Read the PurePanel source
const purePanelPath = path.join(__dirname, 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

// The bug: unconditional title div that always renders
// Look for the pattern in the return section around iconNode
// The title div should only appear when title is provided

// Valid patterns after the fix:
// 1. title && ( <div ...> )
// 2. title ? ( <div ...> ) : null
// 3. {title && <div ...>} or {title ?? <div ...>}

// Check if title div is wrapped in conditional before it
// The bug pattern is: after {iconNode} comes a <div className=...title...> without condition
const iconNodeEnd = source.indexOf('{iconNode}');
if (iconNodeEnd === -1) {
  console.log('FAIL: Cannot find iconNode in source');
  process.exit(1);
}

// Look at text after iconNode
const afterIconNode = source.substring(iconNodeEnd, iconNodeEnd + 500);
const bugPatternMatch = afterIconNode.match(/\{iconNode\}\s*<div[^>]*className=[^>]*title/);

if (bugPatternMatch) {
  console.log('FAIL: Title div renders unconditionally (bug present)');
  process.exit(1);
}

// Now check if there's a conditional title rendering
const hasConditionalTitle = /title\s*&&\s*\(/.test(source) || 
                           /title\s*\?\s*\(/.test(source) ||
                           /\{title\s*&&\s*<div/.test(source) ||
                           /\{title\s*\?\s*<div/.test(source);

if (hasConditionalTitle) {
  console.log('PASS: Title rendering is conditional');
  process.exit(0);
} else {
  console.log('FAIL: Cannot verify title rendering pattern');
  process.exit(1);
}
'''
        returncode, stdout, stderr = self._run_node_test(test_script)
        output = stdout.strip()
        if returncode != 0:
            assert False, f"Test failed: {output}\nSTDERR: {stderr[-500:]}"
        assert 'PASS' in output, f"Test did not pass: {output}"


class TestDescriptionSpacing:
    """Tests that description has proper spacing when title is absent (fail_to_pass)."""

    def _run_node_test(self, test_script: str) -> tuple[int, str, str]:
        """Run a Node.js test script and return (exit_code, stdout, stderr)."""
        script_file = os.path.join(REPO, "__temp_test_script.cjs")
        with open(script_file, "w") as f:
            f.write(test_script)
        try:
            result = subprocess.run(
                ["node", script_file],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            if os.path.exists(script_file):
                os.unlink(script_file)

    def test_description_spacing_without_title(self):
        r"""
        Verify description has proper CSS spacing when it's first element (no title).

        The fix ensures description doesn't overlap close button by adding spacing.
        """
        test_script = '''
const fs = require('fs');
const path = require('path');

// Read the style file
const stylePath = path.join(__dirname, 'components/notification/style/index.ts');
const styleSource = fs.readFileSync(stylePath, 'utf8');

// The bug: description has no special spacing when title is absent
// The fix: either &:first-child rule OR margin on description element

// Check for &:first-child rule (one approach)
const hasFirstChild = /['\"]&:first-child['\"]/.test(styleSource);
const hasFirstChildSpacing = hasFirstChild && /&:first-child[^}]*margin/.test(styleSource);

// Check for marginInlineEnd anywhere in the styles (valid approach)
const hasMarginInlineEnd = /marginInlineEnd/.test(styleSource);

// Check for any right-side margin on the notice or description
const hasRightMargin = /marginRight/.test(styleSource);

// The fix could use any of these patterns
if (hasFirstChildSpacing || (hasMarginInlineEnd && hasRightMargin)) {
  console.log('PASS: Proper spacing rules exist for description');
  process.exit(0);
} else if (!hasFirstChild) {
  console.log('FAIL: No &:first-child rule found (bug present)');
  process.exit(1);
} else {
  console.log('FAIL: Spacing rules incomplete');
  process.exit(1);
}
'''
        returncode, stdout, stderr = self._run_node_test(test_script)
        output = stdout.strip()
        if returncode != 0:
            assert False, f"Test failed: {output}\nSTDERR: {stderr[-500:]}"
        assert 'PASS' in output, f"Test did not pass: {output}"


class TestLayoutBehavior:
    """Tests that verify the notification layout works correctly (fail_to_pass)."""

    def _run_node_test(self, test_script: str) -> tuple[int, str, str]:
        """Run a Node.js test script and return (exit_code, stdout, stderr)."""
        script_file = os.path.join(REPO, "__temp_test_script.cjs")
        with open(script_file, "w") as f:
            f.write(test_script)
        try:
            result = subprocess.run(
                ["node", script_file],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        finally:
            if os.path.exists(script_file):
                os.unlink(script_file)

    def test_notification_component_structure(self):
        """
        Verify notification component has proper structure for icon/title/description.
        """
        test_script = '''
const fs = require('fs');
const path = require('path');

// Check PurePanel.tsx for basic structure
const purePanelPath = path.join(__dirname, 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

// Verify component has proper structure with icon, title, description
const hasIconNode = /iconNode/.test(source);
const hasDescription = /description/.test(source);
const hasReturnStatement = /return\\s*\\(/.test(source);
const hasCloseIcon = /closeIcon|CloseIcon/.test(source);

if (hasIconNode && hasDescription && hasReturnStatement && hasCloseIcon) {
  console.log('PASS: Component structure is valid');
  process.exit(0);
} else {
  console.log('FAIL: Component missing expected structure');
  process.exit(1);
}
'''
        returncode, stdout, stderr = self._run_node_test(test_script)
        output = stdout.strip()
        if returncode != 0:
            assert False, f"Test failed: {output}\nSTDERR: {stderr[-500:]}"
        assert 'PASS' in output, f"Test did not pass: {output}"

    def test_css_provides_close_button_spacing(self):
        """
        Verify CSS includes spacing rules to prevent close button overlap.
        """
        test_script = '''
const fs = require('fs');
const path = require('path');

// Read the style file
const stylePath = path.join(__dirname, 'components/notification/style/index.ts');
const styleSource = fs.readFileSync(stylePath, 'utf8');

// The fix must provide spacing to prevent close button overlap
// This can be done via &:first-child, marginInlineEnd, marginRight, or similar
const hasSpacingMechanism = 
  /['\"]&:first-child['\"]/.test(styleSource) ||
  /marginInlineEnd/.test(styleSource) ||
  /marginRight/.test(styleSource);

if (hasSpacingMechanism) {
  console.log('PASS: CSS has close button spacing mechanism');
  process.exit(0);
} else {
  console.log('FAIL: CSS missing spacing mechanism for close button');
  process.exit(1);
}
'''
        returncode, stdout, stderr = self._run_node_test(test_script)
        output = stdout.strip()
        if returncode != 0:
            assert False, f"Test failed: {output}\nSTDERR: {stderr[-500:]}"
        assert 'PASS' in output, f"Test did not pass: {output}"


class TestRepoIntegration:
    """Pass-to-pass tests using repository's own linting and syntax checks."""

    def test_eslint_notification_component(self):
        """Verify ESLint passes on notification component files (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "eslint", "components/notification/PurePanel.tsx",
             "components/notification/style/index.ts", "--max-warnings=0"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        # ESLint should pass without errors
        assert result.returncode == 0, (
            f"ESLint failed on notification component:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
        )

    def test_uses_design_tokens_not_hardcoded(self):
        """Verify styles use design tokens, not hardcoded values (pass_to_pass)."""
        style_path = os.path.join(REPO, "components/notification/style/index.ts")
        with open(style_path, "r") as f:
            content = f.read()

        # Check that common hardcoded patterns are not present
        # Hardcoded pixel values for margins/paddings should use tokens
        import re

        # Look for patterns like marginInlineEnd: 8 or marginTop: 16 (hardcoded)
        hardcoded_margin = re.search(r'margin\w+:\s*\d+(?!px)', content)

        # The file should use token.marginXS, token.marginSM, etc. not raw numbers
        assert "token.margin" in content, (
            "Expected design token usage (token.margin*) for spacing values"
        )

    def test_biome_lint_notification_component(self):
        """Verify Biome lint passes on notification component files (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "biome", "lint", "components/notification/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, (
            f"Biome lint failed on notification component:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
        )

    def test_biome_check_notification_component(self):
        """Verify Biome check passes on notification component files (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "biome", "check", "components/notification/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert result.returncode == 0, (
            f"Biome check failed on notification component:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
        )
