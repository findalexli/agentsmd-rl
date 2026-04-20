"""Tests for mantinedev/mantine#8777 - HeatmapChart equal values bug fix."""

from __future__ import annotations

import subprocess
import os
import math

REPO = os.environ.get("REPO", "/workspace/mantine_repo")


def test_get_heat_color_equal_values_direct():
    """When max equals min (all values identical), getHeatColor must return a valid color, not NaN.

    The bug: (value - min) / (max - min) produces NaN when max === min.
    The fix: return some valid color from the array when max === min.
    """
    # Run a small node script that imports and calls getHeatColor
    code = """
const { getHeatColor } = require('./packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts');
const colors = ['1', '2', '3', '4'];
const result = getHeatColor({ value: 5, min: 5, max: 5, colors });
console.log('RESULT:', result);
if (!colors.includes(result)) {
  console.error('FAIL: result', result, 'is not in colors array');
  process.exit(1);
}
if (typeof result !== 'string' || result.length === 0) {
  console.error('FAIL: result is not a valid non-empty string');
  process.exit(1);
}
console.log('PASS');
"""
    r = subprocess.run(
        ["node", "--experimental-strip-types", "-e", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"getHeatColor equal-values test failed:\n{output}"


def test_get_heat_color_normal_values():
    """Normal operation still works - values spread across range."""
    code = """
const { getHeatColor } = require('./packages/@mantine/charts/src/Heatmap/get-heat-color/get-heat-color.ts');
const colors = ['1', '2', '3', '4'];
const tests = [
  { value: 1, min: 1, max: 4, expected: '1' },
  { value: 2, min: 1, max: 4, expected: '2' },
  { value: 3, min: 1, max: 4, expected: '3' },
  { value: 4, min: 1, max: 4, expected: '4' },
];
for (const t of tests) {
  const result = getHeatColor({ value: t.value, min: t.min, max: t.max, colors });
  if (result !== t.expected) {
    console.error('FAIL at', t, 'got', result);
    process.exit(1);
  }
}
console.log('PASS');
"""
    r = subprocess.run(
        ["node", "--experimental-strip-types", "-e", code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0, f"getHeatColor normal-values test failed:\n{output}"


def test_repo_heatmap_tests_pass():
    """All existing Heatmap tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "jest", "packages/@mantine/charts/src/Heatmap/", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Heatmap tests suite failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_repo_heatmap_eslint():
    """ESLint passes on Heatmap source files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/charts/src/Heatmap/", "--cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_heatmap_prettier():
    """Prettier code style check passes on Heatmap files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/charts/src/Heatmap/**/*.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
