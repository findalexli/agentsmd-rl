#!/usr/bin/env python3
"""Test outputs for antd-notification-description-spacing task.

Tests verify:
1. Behavioral: description-only notifications render correctly (no title div,
   description is first child, inline-end spacing CSS is generated)
2. Existing repo tests still pass
"""

import subprocess
import sys
import os

REPO = "/workspace/ant-design"
NOTIFICATION_DIR = REPO + "/components/notification"

_EVAL_TEST_CODE = r"""
import React from 'react';
import { render } from '../../../tests/utils';
import PurePanel from '../PurePanel';

jest.mock('react-dom', () => {
  const realReactDOM = jest.requireActual('react-dom');
  if (realReactDOM.version.startsWith('19')) {
    const realReactDOMClient = jest.requireActual('react-dom/client');
    realReactDOM.createRoot = realReactDOMClient.createRoot;
  }
  return realReactDOM;
});

describe('Description-only notification', () => {
  it('title element is not rendered when title is absent', () => {
    const { container } = render(<PurePanel description="Test description" />);
    // When title is not provided, the title div must not appear in the DOM
    const titleEl = container.querySelector('[class*="notice-title"]');
    expect(titleEl).toBeFalsy();
  });

  it('description is first child of content area when no title', () => {
    const { container } = render(<PurePanel description="Test description" />);
    const alertEl = container.querySelector('[role="alert"]');
    expect(alertEl).toBeTruthy();
    // With no title element, description should be the first element child
    const firstChild = alertEl!.firstElementChild;
    expect(firstChild!.className).toMatch(/description/);
  });

  it('generated CSS includes inline-end spacing for first-child description', () => {
    render(<PurePanel description="Test description" />);
    const allCSS = Array.from(document.querySelectorAll('style'))
      .map(s => s.textContent || '')
      .join('');
    // The CSS must include a rule that provides margin-inline-end spacing when
    // description is the first child (i.e., no title is present).
    const hasSpacing = /(first-child|only-child|first-of-type)[\s\S]*?margin-inline-end/.test(allCSS);
    expect(hasSpacing).toBe(true);
  });

  it('title IS rendered when title prop is provided', () => {
    const { container } = render(
      <PurePanel title="My Title" description="Test description" />
    );
    const titleEl = container.querySelector('[class*="notice-title"]');
    expect(titleEl).toBeTruthy();
    expect(titleEl!.textContent).toBe('My Title');
  });
});
"""


def _run_eval_jest():
    """Write a temporary jest test, run it, and return the result."""
    test_file = os.path.join(
        NOTIFICATION_DIR, "__tests__", "_eval_behavior.test.tsx"
    )
    try:
        with open(test_file, "w") as f:
            f.write(_EVAL_TEST_CODE)
        subprocess.run(
            ["npm", "run", "version"],
            cwd=REPO, capture_output=True, text=True, timeout=60,
        )
        return subprocess.run(
            [
                "npx", "jest", "--config", ".jest.js",
                "--testPathPatterns=notification/__tests__/_eval_behavior",
                "--maxWorkers=1", "--no-cache",
            ],
            cwd=REPO, capture_output=True, text=True, timeout=120,
        )
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_description_only_notification_behavior():
    """When no title is provided, the title element should not render,
    description should be first child, and CSS should add inline-end spacing."""
    r = _run_eval_jest()
    assert r.returncode == 0, (
        "Behavioral test failed — description-only notification should: "
        "(1) not render the title element, "
        "(2) have description as first child, "
        "(3) include inline-end spacing CSS for first-child description.\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
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
