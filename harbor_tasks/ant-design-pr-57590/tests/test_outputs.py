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
import re

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
        Verify title element is conditionally rendered based on title prop.

        The fix makes the title div not render when title is null/undefined.
        This test verifies that the title rendering uses conditional logic
        (either && or ternary ?: or if statement) so empty title doesn't
        create an empty div element in the layout.
        """
        test_code = """
const fs = require('fs');
const path = require('path');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

// Find the title div line and check if it's preceded by conditional
// The fix prevents empty title div from affecting layout by making it conditional

const lines = source.split('\\n');

// Find the line with the title div element
let titleDivLineIdx = -1;
for (let i = 0; i < lines.length; i++) {
  // Looking for <div ...className...title...> pattern for the title div
  if (lines[i].includes('<div') &&
      (lines[i].includes('className') || lines[i].includes('class')) &&
      lines[i].includes('title')) {
    titleDivLineIdx = i;
    break;
  }
}

if (titleDivLineIdx === -1) {
  console.log('FAIL: Cannot find title div element');
  process.exit(1);
}

// Look backwards for conditional patterns: && or ? or if(
// These are the standard React patterns for conditional rendering
let foundConditional = false;
const conditionalPatterns = [/title\\s*&&/, /title\\s*\\?/, /if\\s*\\(\\s*title/];

for (let j = titleDivLineIdx - 1; j >= Math.max(0, titleDivLineIdx - 5); j--) {
  for (const pattern of conditionalPatterns) {
    if (pattern.test(lines[j])) {
      foundConditional = true;
      break;
    }
  }
  if (foundConditional) break;
}

if (foundConditional) {
  console.log('PASS');
  process.exit(0);
} else {
  console.log('FAIL: Title div should be conditionally rendered to prevent empty div in layout');
  process.exit(1);
}
"""
        result = _run_js(test_code)
        assert result.returncode == 0, (
            "Title conditional rendering check failed: " + result.stdout
        )


class TestDescriptionSpacing:
    """Tests that description has proper spacing when title is absent (fail_to_pass)."""

    def test_description_spacing_from_close_button(self):
        """
        Verify description has proper spacing from close button when it's first content.

        When title is absent, description becomes the first content element and needs
        proper spacing from the close button. The fix adds a first-child rule to CSS.
        """
        test_code = """
const fs = require('fs');
const path = require('path');

const stylePath = path.join(process.cwd(), 'components/notification/style/index.ts');
const source = fs.readFileSync(stylePath, 'utf8');

// The fix adds &:first-child rule to description styles
// Check for this pattern in the CSS
const hasFirstChild = source.includes('&:first-child');

// Find description section and verify spacing around it
const descIdx = source.indexOf('description');
if (descIdx === -1) {
  console.log('FAIL: description selector not found in CSS');
  process.exit(1);
}

// Check the description section and surrounding context for spacing rules
// The fix should add spacing specifically for when description is first child
const sectionStart = Math.max(0, descIdx - 200);
const sectionEnd = Math.min(source.length, descIdx + 500);
const section = source.substring(sectionStart, sectionEnd);

const hasEndSpacing = section.includes('marginInlineEnd') ||
                     section.includes('marginRight') ||
                     section.includes('paddingInlineEnd') ||
                     section.includes('paddingRight');

const hasFirstChildRule = section.includes('&:first-child') || source.includes('&:first-child');

if (hasFirstChildRule && hasEndSpacing) {
  console.log('PASS');
  process.exit(0);
} else {
  console.log('FAIL: Description needs first-child spacing rule for close button clearance');
  process.exit(1);
}
"""
        result = _run_js(test_code)
        assert result.returncode == 0, (
            "Description spacing CSS not found. "
            "Expected &:first-child rule with marginInlineEnd or similar."
        )


class TestLayoutBehavior:
    """Tests that verify the notification layout works correctly (fail_to_pass)."""

    def test_component_has_conditional_title_and_description(self):
        """
        Verify notification component properly handles title and description conditionally.

        This test ensures both title and description use conditional rendering,
        which is necessary for proper layout when either is absent.
        """
        test_code = """
const fs = require('fs');
const path = require('path');

const purePanelPath = path.join(process.cwd(), 'components/notification/PurePanel.tsx');
const source = fs.readFileSync(purePanelPath, 'utf8');

// Both title and description should be conditionally rendered
// This prevents empty elements from affecting layout
const hasPureContent = source.includes('export const PureContent');
const hasDescriptionCond = /description\\s*&&/.test(source);
// Match JSX conditional: {title && ( or {title ? x : y
// Avoid matching "title ??" nullish coalescing in const mergedTitle = title ?? message
const hasTitleCond = /\\{title\\s*&&|\\{title\\s*\\?/.test(source);

if (hasPureContent && hasDescriptionCond && hasTitleCond) {
  console.log('PASS');
  process.exit(0);
} else {
  console.log('FAIL: Component should have conditional rendering for both title and description');
  console.log('hasPureContent:', hasPureContent);
  console.log('hasDescriptionCond:', hasDescriptionCond);
  console.log('hasTitleCond:', hasTitleCond);
  process.exit(1);
}
"""
        result = _run_js(test_code)
        assert result.returncode == 0, "Component structure test failed: " + result.stdout


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && "$EVENT" == "pull_request" ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")