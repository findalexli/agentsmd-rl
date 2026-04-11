"""
Tests for ant-design Table rowSelection crash fix.

This validates that the Table component doesn't crash when selectedRowKeys
becomes undefined while preserveSelectedRowKeys is enabled.
"""

import os
import subprocess
import sys

REPO = "/workspace/ant-design"


def run_jest_test(test_pattern: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run Jest test with given pattern."""
    return subprocess.run(
        ["npm", "test", "--", test_pattern, "--testNamePattern", "preserveSelectedRowKeys"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


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


def test_rowSelection_regression_preserveSelectedRowKeys():
    r"""
    Regression test: Table should not crash when selectedRowKeys becomes
    undefined with preserveSelectedRowKeys enabled (fail_to_pass).

    This test reproduces the bug scenario:
    1. Render Table with selectedRowKeys=['Jack']
    2. Rerender with selectedRowKeys=[]
    3. Rerender with preserveSelectedRowKeys=true and selectedRowKeys undefined
    4. Click checkbox - should not crash
    """
    r = subprocess.run(
        [
            "npm", "test", "--",
            "Table.rowSelection.test.tsx",
            "--testNamePattern",
            "works with preserveSelectedRowKeys after receive selectedRowKeys from \\\[\\\] to undefined",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Regression test failed:\n{r.stdout}\n{r.stderr}"


def test_rowSelection_radio_undefined_keys():
    r"""
    Related test: selectionType radio with selectedRowKeys from [] to undefined.
    This test also validates the fix works for radio selection type (fail_to_pass).
    """
    r = subprocess.run(
        [
            "npm", "test", "--",
            "Table.rowSelection.test.tsx",
            "--testNamePattern",
            "works with selectionType radio receive selectedRowKeys from \\\[\\\] to undefined",
            "--no-coverage",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Radio selection test failed:\n{r.stdout}\n{r.stderr}"


def test_mergedSelectedKeys_uses_empty_list_fallback():
    """
    Structural check: The fix should use mergedSelectedKeys ?? EMPTY_LIST pattern.

    This verifies the specific code pattern that fixes the undefined crash.
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # The fix adds: const mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST;
    assert "mergedSelectedKeys ?? EMPTY_LIST" in content, \
        "Fix pattern 'mergedSelectedKeys ?? EMPTY_LIST' not found in useSelection.tsx"

    # Should also use mergedSelectedKeyList in the useMemo for derived keys
    assert "mergedSelectedKeyList" in content, \
        "Variable 'mergedSelectedKeyList' not used in useSelection.tsx"
