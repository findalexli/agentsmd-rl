#!/usr/bin/env python3
"""Test outputs for antd-notification-description-spacing task.

Tests verify:
1. CSS fix: description as first-child has inline-end spacing reserved for close button
2. Component fix: PureContent conditionally renders title only when provided
3. Existing repo tests still pass
"""

import subprocess
import sys
import re
import os

REPO = "/workspace/ant-design"
NOTIFICATION_DIR = REPO + "/components/notification"

def _get_style_content():
    return open(NOTIFICATION_DIR + "/style/index.ts", "r").read()

def _get_purepanel_content():
    return open(NOTIFICATION_DIR + "/PurePanel.tsx", "r").read()

def test_css_description_first_child_spacing():
    content = _get_style_content()
    p = re.compile(
        r'["\']&:first-child["\']:\s*\{[^}]*(?:marginInlineEnd|marginInline-end|marginRight|margin-right)[^}]*token\.[^}]*\}',
        re.DOTALL
    )
    assert p.search(content) is not None, (
        "CSS fix not found: description needs inline-end spacing when it is the first child "
        "(no title present) to prevent close button overlap. "
        "Expected: a &:first-child CSS rule with inline-end margin using a design token."
    )

def test_pure_content_conditional_title_rendering():
    content = _get_purepanel_content()
    patterns = [
        r"\{\s*title\s*&&\s*\(",
        r"\{\s*title\s*\?\s*[^:]+\s*:",
        r"\{\s*![^}]*title",
    ]
    found = any(re.search(pat, content, re.MULTILINE) for pat in patterns)
    assert found, (
        "Component fix not found: title should be conditionally rendered so that "
        "description can be first-child when title is absent. "
        "Expected: {title && (...)} or {title ? ... : null} pattern."
    )

def test_notification_unit_tests():
    r = subprocess.run([
        "npm", "test", "--", "components/notification",
    ], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Tests failed: {r.stderr[-2000:]} {r.stdout[-2000:]}"

def test_lint_passes():
    r = subprocess.run([
        "npx", "eslint", "components/notification/", "--ext", ".ts,.tsx",
    ], cwd=REPO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"ESLint failed: {r.stderr[-2000:]}"

def test_biome_lint_passes():
    r = subprocess.run([
        "npx", "biome", "lint", "components/notification/",
    ], cwd=REPO, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, f"Biome failed: {r.stderr[-2000:]}"

def test_notification_hooks_tests():
    subprocess.run(["npm", "run", "version"], cwd=REPO, capture_output=True, text=True, timeout=60)
    r = subprocess.run([
        "npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/hooks",
        "--maxWorkers=1", "--no-cache",
    ], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Hooks tests failed: {r.stderr[-2000:]}"

def test_notification_placement_tests():
    subprocess.run(["npm", "run", "version"], cwd=REPO, capture_output=True, text=True, timeout=60)
    r = subprocess.run([
        "npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/placement",
        "--maxWorkers=1", "--no-cache",
    ], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Placement tests failed: {r.stderr[-2000:]}"

def test_notification_config_tests():
    subprocess.run(["npm", "run", "version"], cwd=REPO, capture_output=True, text=True, timeout=60)
    r = subprocess.run([
        "npx", "jest", "--config", ".jest.js", "--testPathPatterns=notification/__tests__/config",
        "--maxWorkers=1", "--no-cache",
    ], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, f"Config tests failed: {r.stderr[-2000:]}"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
