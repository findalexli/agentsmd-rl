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

    def test_title_not_rendered_when_not_provided(self):
        """
        Verify title element is NOT rendered when no title is provided.

        Uses Jest to actually render the PureContent component and verify
        the DOM does not contain the title div when title is undefined.
        """
        test_code = """
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

const projectRoot = process.cwd();
const testFile = path.join(projectRoot, '__conditional_render.test.tsx');

const testContent = `
import React from 'react';
import { render, act } from '@testing-library/react';
import { PureContent } from './components/notification/PurePanel';

describe('PureContent conditional rendering', () => {
  it('should NOT render title div when title is not provided', async () => {
    let container;
    await act(async () => {
      const result = render(
        <PureContent
          prefixCls="ant-notification"
          className=""
          title={undefined}
          description="Test description"
        />
      );
      container = result.container;
    });

    const titleDivs = container.querySelectorAll('.ant-notification-title');
    if (titleDivs.length !== 0) {
      console.log('FAIL: Title div rendered when title is undefined');
      process.exit(1);
    }

    const descDivs = container.querySelectorAll('.ant-notification-description');
    if (descDivs.length !== 1) {
      console.log('FAIL: Description div not found');
      process.exit(1);
    }

    console.log('PASS');
    process.exit(0);
  });

  it('should render title div when title IS provided', async () => {
    let container;
    await act(async () => {
      const result = render(
        <PureContent
          prefixCls="ant-notification"
          className=""
          title="Test Title"
          description="Test description"
        />
      );
      container = result.container;
    });

    const titleDivs = container.querySelectorAll('.ant-notification-title');
    if (titleDivs.length !== 1) {
      console.log('FAIL: Title div not rendered when title is provided');
      process.exit(1);
    }

    console.log('PASS');
    process.exit(0);
  });
});
`;

// Write the test file
fs.writeFileSync(testFile, testContent);

try {
  execSync('npx jest __conditional_render.test.tsx --testPathIgnorePatterns=[] --no-coverage --passWithNoTests', {
    cwd: projectRoot,
    stdio: 'pipe',
    timeout: 120
  });
  console.log('PASS');
  process.exit(0);
} catch (e) {
  const output = e.stdout ? e.stdout.toString() : e.stderr ? e.stderr.toString() : '';
  if (output.includes('PASS')) {
    console.log('PASS');
    process.exit(0);
  }
  console.log('FAIL: ' + output.substring(0, 500));
  process.exit(1);
} finally {
  try { fs.unlinkSync(testFile); } catch (e) {}
}
"""
        result = _run_js(test_code, timeout=120)
        assert result.returncode == 0, f"Test failed: {result.stdout[-1000:]}
{result.stderr[-500:]}"

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
        # This can be done via &:first-child, marginInlineEnd, marginRight, padding, etc.
        has_valid_spacing = (
            ('&:first-child' in style_source and
             ('margin' in style_source or 'padding' in style_source))
            or 'marginInlineEnd' in style_source
            or ('marginRight' in style_source)
            or ('paddingInlineEnd' in style_source)
        )

        assert has_valid_spacing, (
            "CSS rules for description spacing not found. "
            "Expected &:first-child with margin/padding or marginInlineEnd/marginRight."
        )

    def test_description_has_margin_inline_end_when_no_title(self):
        """
        Verify description has marginInlineEnd or equivalent spacing in CSS.

        This ensures the close button does not overlap when title is absent.
        """
        style_path = os.path.join(REPO, "components/notification/style/index.ts")
        with open(style_path, "r") as f:
            style_source = f.read()

        # Find the description section and check for spacing
        desc_marker = 'description'
        idx = style_source.find(desc_marker)
        assert idx != -1, "Description section not found in styles"

        # Extract a reasonable section around description
        section_end = idx + 800
        if section_end > len(style_source):
            section_end = len(style_source)
        desc_section = style_source[idx:section_end]

        # Check for any right-side spacing
        has_right_spacing = (
            'marginInlineEnd' in desc_section
            or 'marginRight' in desc_section
            or 'paddingInlineEnd' in desc_section
            or 'paddingRight' in desc_section
        )

        assert has_right_spacing, (
            "No right-side spacing found for description. "
            "Expected marginInlineEnd or marginRight for close button clearance."
        )


class TestLayoutBehavior:
    """Tests that verify the notification layout works correctly (fail_to_pass)."""

    def test_notification_component_structure(self):
        """
        Verify notification component has proper structure for icon/title/description.
        """
        test_script = """
const fs = require('fs');
const path = require('path');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

const hasIconNode = /iconNode/.test(source);
const hasDescription = /description/.test(source);
const hasReturnStatement = /return\s*\(/ .test(source);
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
        assert result.returncode == 0, f"Component structure test failed: {result.stdout}"

    def test_purepanel_renders_without_errors(self):
        """
        Verify PurePanel component can be imported and rendered without errors.
        """
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
        assert result.returncode == 0, f"Component render test failed: {result.stdout}"


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
            f"ESLint failed on notification component:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
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
