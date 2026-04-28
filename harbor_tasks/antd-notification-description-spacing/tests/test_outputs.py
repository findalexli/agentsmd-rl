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

_EVAL_DOM_TEST_CODE = r"""
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

describe('Description-only notification DOM structure', () => {
  it('title element is not rendered when title is absent', () => {
    const { container } = render(<PurePanel description="Test description" />);
    const titleEl = container.querySelector('[class*="notice-title"]');
    expect(titleEl).toBeFalsy();
  });

  it('description is first child of content area when no title', () => {
    const { container } = render(<PurePanel description="Test description" />);
    const alertEl = container.querySelector('[role="alert"]');
    expect(alertEl).toBeTruthy();
    const firstChild = alertEl!.firstElementChild;
    expect(firstChild!.className).toMatch(/description/);
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

_EVAL_CSS_TEST_CODE = r"""
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

describe('Description-only notification CSS', () => {
  it('generated CSS includes inline-end spacing for first-child description', () => {
    render(<PurePanel description="Test description" />);
    const allCSS = Array.from(document.querySelectorAll('style'))
      .map(s => s.textContent || '')
      .join('');
    const hasSpacing = /(first-child|only-child|first-of-type)[\s\S]*?margin-inline-end/.test(allCSS);
    expect(hasSpacing).toBe(true);
  });
});
"""


def _run_injected_jest(test_code, test_name):
    """Write a temporary jest test file, run it, and clean up."""
    test_file = os.path.join(
        NOTIFICATION_DIR, "__tests__", f"_eval_{test_name}.test.tsx"
    )
    try:
        with open(test_file, "w") as f:
            f.write(test_code)
        subprocess.run(
            ["npm", "run", "version"],
            cwd=REPO, capture_output=True, text=True, timeout=60,
        )
        return subprocess.run(
            [
                "npx", "jest", "--config", ".jest.js",
                f"--testPathPatterns=notification/__tests__/_eval_{test_name}",
                "--maxWorkers=1", "--no-cache",
            ],
            cwd=REPO, capture_output=True, text=True, timeout=120,
        )
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_description_only_dom_structure():
    """f2p: When title absent, title div must not appear and description
    must be first child. When title IS provided, title still renders normally."""
    r = _run_injected_jest(_EVAL_DOM_TEST_CODE, "dom")
    assert r.returncode == 0, (
        "DOM structure test failed:\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )


def test_description_only_css_inline_spacing():
    """f2p: CSS must include margin-inline-end spacing for first-child description."""
    r = _run_injected_jest(_EVAL_CSS_TEST_CODE, "css")
    assert r.returncode == 0, (
        "CSS spacing test failed:\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )


def test_notification_unit_tests():
    r = subprocess.run([
        "bash", "-lc", "cd /workspace/ant-design && npm test -- components/notification"
    ], capture_output=True, text=True, timeout=300)
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