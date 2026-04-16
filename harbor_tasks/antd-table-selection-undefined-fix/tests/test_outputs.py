"""
Tests for ant-design Table rowSelection crash fix.

This validates that the Table component does not crash when selectedRowKeys
becomes undefined while preserveSelectedRowKeys is enabled.
"""

import json
import os
import subprocess
import sys

REPO = "/workspace/ant-design"


def test_tsc_no_errors():
    """TypeScript compiles without errors (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert r.returncode == 0, f"TypeScript errors:\n{r.stdout}\n{r.stderr}"


def test_eslint_no_errors():
    """ESLint passes without errors on the table directory (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:script", "--", "components/table/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"ESLint errors:\n{r.stdout}\n{r.stderr}"


def test_biome_lint():
    """Biome lint passes without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stdout}\n{r.stderr}"


def test_lint_md():
    """Markdown lint passes without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Markdown lint failed:\n{r.stdout}\n{r.stderr}"


def test_lint_changelog():
    """Component changelog lint passes without errors (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:changelog"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Changelog lint failed:\n{r.stdout}\n{r.stderr}"


def test_node_tests():
    """Node.js specific tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test:node"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Node tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_table_rowSelection_unit():
    """Table rowSelection unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "npm", "test", "--",
            "--testPathPatterns=Table.rowSelection",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, f"Table rowSelection tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_table_all_unit():
    """All Table component unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "npm", "test", "--",
            "--testPathPatterns=Table\\.",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Table tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_useSelection_file_exists():
    """The useSelection hook file exists at expected path."""
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    assert os.path.exists(hook_path), f"useSelection.tsx not found at {hook_path}"


def test_mergedSelectedKeys_fix_behavioral():
    """
    Behavioral test: The fix should ensure mergedSelectedKeys is treated as array.
    
    This test verifies the fix by checking the compiled output handles undefined
    selectedRowKeys with preserveSelectedRowKeys correctly. It runs a specific
    Jest test that exercises the preserveSelectedRowKeys cache behavior.
    """
    # Run the specific preserveSelectedRowKeys cache test
    r = subprocess.run(
        [
            "npm", "test", "--",
            "Table.rowSelection.test.tsx",
            "--testNamePattern",
            "cache with preserveSelectedRowKeys",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"preserveSelectedRowKeys cache test failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"
    
    # Also verify the fix pattern exists in source (secondary check)
    # This is behavioral in that it runs AFTER the npm test above
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()
    
    # The fix introduces mergedSelectedKeyList to safely handle undefined
    assert "mergedSelectedKeyList" in content, \
        "Fix variable mergedSelectedKeyList not found - fix may not be applied"


def test_receive_undefined_selectedRowKeys():
    """
    Test that Table handles selectedRowKeys going from defined to undefined.
    This is the scenario that triggers the bug without the fix.
    """
    r = subprocess.run(
        [
            "npm", "test", "--",
            "Table.rowSelection.test.tsx",
            "--testNamePattern",
            "receive selectedRowKeys from .* to undefined",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"selectedRowKeys undefined transition test failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"
