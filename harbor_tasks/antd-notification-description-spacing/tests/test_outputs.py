#!/usr/bin/env python3
"""Test outputs for antd-notification-description-spacing task.

Tests verify:
1. CSS fix: description as first-child has marginInlineEnd reserved for close button
2. Component fix: PureContent conditionally renders title only when provided
3. Existing repo tests still pass
"""

import subprocess
import sys
import re
import os

REPO = "/workspace/ant-design"
NOTIFICATION_DIR = f"{REPO}/components/notification"

def test_css_description_first_child_spacing():
    """FAIL-TO-PASS: Description element has marginInlineEnd when it's the first child.

    This prevents close button from overlapping description-only notifications.
    """
    style_file = f"{NOTIFICATION_DIR}/style/index.ts"
    with open(style_file, 'r') as f:
        content = f.read()

    # Check that the fix is present: &:first-child rule with marginInlineEnd
    # This is the key CSS change that reserves space for close button
    pattern = r"['\"]&:first-child['\"]:\s*\{[^}]*marginInlineEnd:\s*token\.marginSM"
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, (
        "CSS fix not found: description '&:first-child' should have marginInlineEnd "
        "to reserve space for close button. Expected pattern: '&:first-child { marginTop: 0, marginInlineEnd: token.marginSM }'"
    )

def test_pure_content_conditional_title_rendering():
    """FAIL-TO-PASS: PureContent conditionally renders title only when provided.

    When title is null/undefined, the title div should not be rendered,
    allowing description to be the first child and receive proper spacing.
    """
    pure_panel_file = f"{NOTIFICATION_DIR}/PurePanel.tsx"
    with open(pure_panel_file, 'r') as f:
        content = f.read()

    # Check for conditional rendering pattern: {title && (...)} or {title && (
    # This allows description to become first-child when title is absent
    pattern = r"\{\s*title\s*&&\s*\("
    match = re.search(pattern, content, re.MULTILINE)

    assert match is not None, (
        "Component fix not found: title should be conditionally rendered with 'title &&' "
        "pattern so that description can be first-child when title is absent. "
        "The title div should be wrapped in a conditional like: {title && (<div>...</div>)}"
    )

def test_notification_unit_tests():
    """PASS-TO-PASS: Repo notification unit tests pass.

    Run the existing notification test suite to ensure no regressions.
    """
    result = subprocess.run(
        ["npm", "test", "--", "components/notification"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Notification unit tests failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )

def test_lint_passes():
    """PASS-TO-PASS: ESLint passes on notification files.

    Code style should follow repo conventions.
    """
    result = subprocess.run(
        ["npx", "eslint", "components/notification/", "--ext", ".ts,.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"ESLint failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_biome_lint_passes():
    """PASS-TO-PASS: Biome lint passes on notification files.

    Repo uses Biome for additional linting and formatting.
    """
    result = subprocess.run(
        ["npx", "biome", "lint", "components/notification/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Biome lint failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_notification_hooks_tests():
    """PASS-TO-PASS: Notification hooks tests pass.

    Run the hooks test suite to verify notification hook functionality.
    """
    # First generate version file
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/hooks",
         "--maxWorkers=1", "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Notification hooks tests failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_notification_placement_tests():
    """PASS-TO-PASS: Notification placement tests pass.

    Run the placement test suite to verify notification placement functionality.
    """
    # First generate version file
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/placement",
         "--maxWorkers=1", "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Notification placement tests failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )


def test_notification_config_tests():
    """PASS-TO-PASS: Notification config tests pass.

    Run the config test suite to verify notification config functionality.
    """
    # First generate version file
    subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/config",
         "--maxWorkers=1", "--no-cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Notification config tests failed:\n{result.stderr[-2000:]}\n{result.stdout[-2000:]}"
    )

if __name__ == "__main__":
    # Run tests with pytest if available, else run directly
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
