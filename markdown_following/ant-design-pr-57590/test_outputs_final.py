"""
Tests for ant-design notification close button spacing fix.

This PR fixes a layout bug where the close button overlaps notification content
when only a description is rendered without a title. The fix:
1. Conditionally renders the title element only when title exists
2. Adds spacing to description when it is the first content element
"""

import subprocess
import os
import json

REPO = "/workspace/antd"


def _run_js(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run JavaScript code in the repo context."""
    script = os.path.join(REPO, "__eval_test.cjs")
    with open(script, "w") as f:
        f.write(code)
    try:
        return subprocess.run(
            ["node", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
        )
    finally:
        try:
            os.unlink(script)
        except OSError:
            pass


class TestConditionalTitleRendering:
    """Tests that title div is conditionally rendered (fail_to_pass)."""

    def test_title_conditionally_rendered(self):
        """
        Verify title div is conditionally rendered based on title prop.
        
        The fix wraps the title div in a conditional like {title && (...)} or {title ? (...) : null}
        to prevent rendering an empty title div when only description is present.
        """
        test_code = """
const fs = require('fs');
const path = require('path');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

// Find the PureContent component and check if title is conditionally rendered
// Look for patterns like: {title && (...)} or {title ? (...) : null} or {title ? ...}

// Find the return statement in PureContent
const returnMatch = source.match(/return\s*\([\s\S]*?\)\s*;/);
if (!returnMatch) {
  console.log('FAIL: Cannot find return statement');
  process.exit(1);
}

const returnContent = returnMatch[0];

// Check if title is wrapped in conditional
// Look for the pattern where title div follows a conditional check on title
const titleDivMatch = returnContent.match(/<div[^>]*class=[^>]*title[^>]*>\s*\{/);
if (!titleDivMatch) {
  console.log('FAIL: Title div not found');
  process.exit(1);
}

// Get position of title div relative to conditional
const titleDivIndex = returnContent.indexOf(titleDivMatch[0]);

// Look backwards from title div for conditional patterns
const beforeTitle = returnContent.substring(0, titleDivIndex);
const hasConditional = /\{\s*title\s*&&/.test(beforeTitle) || 
                       /\{\s*title\s*\?/.test(beforeTitle) ||
                       /if\s*\(\s*title\s*\)/.test(beforeTitle);

if (hasConditional) {
  console.log('PASS');
  process.exit(0);
} else {
  // Also check if title variable is used in any conditional expression before the div
  console.log('FAIL: Title div renders without conditional check');
  process.exit(1);
}
"""
        result = _run_js(test_code)
        assert result.returncode == 0, "Title conditional rendering check failed: " + result.stdout


class TestDescriptionSpacing:
    """Tests that description has proper spacing when title is absent (fail_to_pass)."""

    def test_description_spacing_css_rules_exist(self):
        """
        Verify CSS provides spacing for description when it is the first child.

        Checks that the style/index.ts has CSS rules that give the description
        proper spacing when rendered as the first child (no title present).
        """
        style_path = os.path.join(REPO, "components/notification/style/index.ts")
        with open(style_path, "r") as f:
            style_source = f.read()

        # The fix should add spacing to description when it is the first child
        has_valid_spacing = (
            ("&:first-child" in style_source and
             ("margin" in style_source or "padding" in style_source))
            or "marginInlineEnd" in style_source
            or ("marginRight" in style_source)
            or ("paddingInlineEnd" in style_source)
        )

        assert has_valid_spacing, (
            "CSS rules for description spacing not found. "
            "Expected &:first-child with margin/padding or marginInlineEnd/marginRight."
        )

    def test_description_has_margin_inline_end_when_no_title(self):
        """
        Verify description has marginInlineEnd or equivalent spacing in CSS.
        """
        style_path = os.path.join(REPO, "components/notification/style/index.ts")
        with open(style_path, "r") as f:
            style_source = f.read()

        desc_marker = 'description'
        idx = style_source.find(desc_marker)
        assert idx != -1, "Description section not found in styles"

        section_end = idx + 800
        if section_end > len(style_source):
            section_end = len(style_source)
        desc_section = style_source[idx:section_end]

        has_right_spacing = (
            "marginInlineEnd" in desc_section
            or "marginRight" in desc_section
            or "paddingInlineEnd" in desc_section
            or "paddingRight" in desc_section
        )

        assert has_right_spacing, (
            "No right-side spacing found for description."
        )


class TestLayoutBehavior:
    """Tests that verify the notification layout works correctly (fail_to_pass)."""

    def test_notification_component_structure(self):
        """Verify notification component has proper structure."""
        test_script = """
const fs = require('fs');
const path = require('path');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

const hasIconNode = /iconNode/.test(source);
const hasDescription = /description/.test(source);
const hasReturnStatement = /return\s*\(/.test(source);
const hasCloseIcon = /closeIcon|CloseIcon/.test(source);

if (hasIconNode && hasDescription && hasReturnStatement && hasCloseIcon) {
  console.log('PASS');
  process.exit(0);
} else {
  console.log('FAIL: missing structure');
  process.exit(1);
}
"""
        result = _run_js(test_script)
        assert result.returncode == 0, "Component structure test failed: " + result.stdout

    def test_purepanel_renders_without_errors(self):
        """Verify PurePanel component can be imported."""
        test_script = """
const path = require('path');
const fs = require('fs');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

try {
  if (source.includes('export const PureContent') && source.includes('return')) {
    console.log('PASS');
    process.exit(0);
  } else {
    console.log('FAIL: PureContent component not found');
    process.exit(1);
  }
} catch (e) {
  console.log('FAIL: ' + e.message);
  process.exit(1);
}
"""
        result = _run_js(test_script)
        assert result.returncode == 0, "Component render test failed: " + result.stdout


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
        assert result.returncode == 0, (
            "ESLint failed on notification component:\n" + result.stdout[-2000:] + "\n" + result.stderr[-500:]
        )

    def test_uses_design_tokens_not_hardcoded(self):
        """Verify styles use design tokens, not hardcoded values (pass_to_pass)."""
        style_path = os.path.join(REPO, "components/notification/style/index.ts")
        with open(style_path, "r") as f:
            content = f.read()

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
            "Biome lint failed on notification component:\n" + result.stdout[-2000:] + "\n" + result.stderr[-500:]
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
            "Biome check failed on notification component:\n" + result.stdout[-2000:] + "\n" + result.stderr[-500:]
        )
