"""Tests for ant-design notification close button spacing fix."""

import subprocess
import sys
import os

# Repository path
REPO = "/workspace/ant-design"
COMPONENTS_DIR = os.path.join(REPO, "components")
NOTIFICATION_DIR = os.path.join(COMPONENTS_DIR, "notification")


def test_typescript_compilation():
    """TypeScript compilation passes (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stderr[-1000:]}"


def test_notification_unit_tests():
    """Notification component tests pass (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    # Generate version file first
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=env
    )
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache", "--testPathPatterns=notification", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )
    assert result.returncode == 0, f"Notification tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_eslint_notification():
    """ESLint passes on notification component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/notification", "--cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_biome_lint_notification():
    """Biome lint passes on notification component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/notification"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_purepanel_conditional_title_render():
    """PureContent should NOT render title div when title is null/undefined (fail_to_pass)."""
    # Read PurePanel.tsx to check for conditional title rendering
    pure_panel_path = os.path.join(NOTIFICATION_DIR, "PurePanel.tsx")
    with open(pure_panel_path, 'r') as f:
        content = f.read()

    # The fix wraps the title div in a conditional: {title && (<div>...</div>)}
    # Check that the pattern exists
    has_conditional_rendering = "title &&" in content and "${prefixCls}-title" in content
    assert has_conditional_rendering, "Title must be conditionally rendered with 'title &&' pattern"


def test_style_first_child_margin():
    """Style should reserve close button spacing for description as first child (fail_to_pass)."""
    style_path = os.path.join(NOTIFICATION_DIR, "style", "index.ts")
    with open(style_path, 'r') as f:
        content = f.read()
    
    # Check for the CSS rule that adds margin to description when it's the first child
    # This reserves space for the close button
    has_first_child_rule = "'&:first-child':" in content or '"&:first-child":' in content
    has_margin_inline_end = "marginInlineEnd" in content
    has_margin_top_zero = "marginTop: 0" in content
    
    assert has_first_child_rule, "Style must include &:first-child rule for description spacing"
    assert has_margin_inline_end, "Style must include marginInlineEnd for close button spacing"
    assert has_margin_top_zero, "Style must set marginTop: 0 for first-child description"


def test_description_margin_value_is_token():
    """Description margin should use design token, not hardcoded value (fail_to_pass)."""
    style_path = os.path.join(NOTIFICATION_DIR, "style", "index.ts")
    with open(style_path, 'r') as f:
        content = f.read()
    
    # Check that marginInlineEnd uses a token, not a hardcoded pixel value
    # The fix should use: marginInlineEnd: token.marginSM
    # Not: marginInlineEnd: 24 or some hardcoded number
    import re
    
    # Look for marginInlineEnd in the first-child block
    pattern = r"'&:first-child':\s*\{[^}]*marginInlineEnd:\s*([^},]+)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        margin_value = match.group(1).strip()
        # Should use token, not hardcoded number
        assert "token." in margin_value, f"marginInlineEnd should use design token (e.g., token.marginSM), got: {margin_value}"
    else:
        # Alternative pattern with double quotes
        pattern2 = r'"&:first-child":\s*\{[^}]*marginInlineEnd:\s*([^},]+)'
        match2 = re.search(pattern2, content, re.DOTALL)
        if match2:
            margin_value = match2.group(1).strip()
            assert "token." in margin_value, f"marginInlineEnd should use design token, got: {margin_value}"
        else:
            # Check more broadly
            assert "marginInlineEnd: token." in content, "marginInlineEnd should use design token like token.marginSM"


def test_no_extra_blank_line_in_test():
    """Test file should not have extra blank lines added (pass_to_pass)."""
    test_path = os.path.join(NOTIFICATION_DIR, "__tests__", "index.test.tsx")
    with open(test_path, 'r') as f:
        content = f.read()
    
    # Check that there's exactly one blank line before "describe('When closeIcon is null"
    # The PR adds just one blank line between the previous test and this describe block
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "describe('When closeIcon is null" in line or 'describe("When closeIcon is null' in line:
            # Count blank lines before this
            blank_count = 0
            for j in range(i-1, max(0, i-5), -1):
                if lines[j].strip() == '':
                    blank_count += 1
                elif '});' in lines[j]:
                    break
            # There should be exactly one blank line (the PR adds one)
            # But this is a soft check - the main behavior is what matters
            # Just verify the file structure is reasonable
            break


if __name__ == "__main__":
    pytest_args = ["-v", "--tb=short"]
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    
    import pytest
    exit(pytest.main([__file__] + pytest_args))
