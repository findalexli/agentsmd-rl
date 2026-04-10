"""
Tests for antd Table rowSelection crash fix.
Verifies the fix for: https://github.com/ant-design/ant-design/issues/57416
"""

import subprocess
import sys
import os

REPO = "/workspace/ant-design"


def test_file_syntax():
    """Verify useSelection.tsx has valid TypeScript syntax."""
    # Use the repo's typecheck command instead of running tsc directly on a single file
    # Running tsc on a single file without tsconfig.json causes JSX/module resolution errors
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert result.returncode == 0, f"TypeScript syntax error:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_merged_selected_keys_coalescing():
    """
    Verify that mergedSelectedKeys is coalesced to EMPTY_LIST.
    This prevents undefined from flowing into cache update logic.
    """
    # Read the file
    with open(f"{REPO}/components/table/hooks/useSelection.tsx", "r") as f:
        content = f.read()

    # Check for the coalescing fix
    assert "mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST" in content, \
        "Missing coalescing fix: should define mergedSelectedKeyList with nullish coalescing"

    # Verify all usages of mergedSelectedKeys are replaced with mergedSelectedKeyList
    # in the critical sections (cache update and derived keys)
    assert "updatePreserveRecordsCache(mergedSelectedKeyList)" in content, \
        "Cache update should use mergedSelectedKeyList"

    # Check that updatePreserveRecordsCache is NOT called with raw mergedSelectedKeys
    # (only in the effect that updates the cache - other calls with different args are OK)
    assert "updatePreserveRecordsCache(mergedSelectedKeys)" not in content, \
        "Cache update should NOT use raw mergedSelectedKeys - use mergedSelectedKeyList instead"


def test_derived_keys_use_coalesced_list():
    """
    Verify that derivedSelectedKeys calculation uses mergedSelectedKeyList.
    """
    with open(f"{REPO}/components/table/hooks/useSelection.tsx", "r") as f:
        content = f.read()

    # Check for conductCheck using mergedSelectedKeyList
    assert "conductCheck(\n      mergedSelectedKeyList," in content, \
        "conductCheck should use mergedSelectedKeyList instead of mergedSelectedKeys"

    # Check for checkStrictly branch using mergedSelectedKeyList
    assert "return [mergedSelectedKeyList, []]" in content, \
        "checkStrictly branch should return mergedSelectedKeyList"

    # Verify dependency array uses mergedSelectedKeyList
    assert "[mergedSelectedKeyList, checkStrictly, keyEntities, isCheckboxDisabled]" in content, \
        "useMemo dependency array should use mergedSelectedKeyList"


def test_upstream_unit_tests_pass():
    """Run the upstream regression test for this specific bug."""
    # Run jest directly instead of npm test to avoid option parsing issues
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "Table.rowSelection",
         "--testNamePattern=works with preserveSelectedRowKeys after receive selectedRowKeys from",
         "--no-coverage", "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    # Check that the test passed
    assert result.returncode == 0, \
        f"Upstream unit test failed:\nSTDOUT:\n{result.stdout[-2000:]}\nSTDERR:\n{result.stderr[-500:]}"


def test_no_crash_on_undefined_selected_row_keys():
    """
    Integration test: Verify no crash when selectedRowKeys becomes undefined
    with preserveSelectedRowKeys enabled.

    Uses tsx to run TypeScript directly without building.
    """
    # Create a TypeScript test script that reproduces the crash
    test_script = """
import * as React from "react";
import * as ReactDOMServer from "react-dom/server";
import Table from "./components/table";

// Test: Render with selectedRowKeys, then rerender with undefined + preserveSelectedRowKeys
function testNoCrash(): boolean {
  try {
    // First render with selectedRowKeys
    const elem1 = React.createElement(Table, {
      dataSource: [{ name: "Jack" }],
      rowSelection: { selectedRowKeys: ["Jack"] },
      rowKey: "name"
    });
    ReactDOMServer.renderToString(elem1);

    // Second render with selectedRowKeys as empty array
    const elem2 = React.createElement(Table, {
      dataSource: [{ name: "Jack" }],
      rowSelection: { selectedRowKeys: [] },
      rowKey: "name"
    });
    ReactDOMServer.renderToString(elem2);

    // Third render with undefined selectedRowKeys and preserveSelectedRowKeys
    // This is where the crash occurs without the fix
    const elem3 = React.createElement(Table, {
      dataSource: [{ name: "Jack" }],
      rowSelection: { preserveSelectedRowKeys: true },
      rowKey: "name"
    });
    ReactDOMServer.renderToString(elem3);

    console.log("SUCCESS: No crash occurred");
    return true;
  } catch (err: any) {
    console.error("FAILED:", err.message);
    return false;
  }
}

process.exit(testNoCrash() ? 0 : 1);
"""

    # Write and run test script with tsx
    test_file = f"{REPO}/test_crash.tsx"
    with open(test_file, "w") as f:
        f.write(test_script)

    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    result = subprocess.run(
        ["npx", "tsx", "test_crash.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )

    # Cleanup
    os.remove(test_file)

    assert result.returncode == 0, \
        f"Crash test failed - the bug is not fixed:\n{result.stdout}\n{result.stderr}"


def test_effect_dependencies_updated():
    """
    Verify the useEffect dependency array was updated to include updatePreserveRecordsCache.
    This ensures the cache is properly invalidated when the update function changes.
    """
    with open(f"{REPO}/components/table/hooks/useSelection.tsx", "r") as f:
        content = f.read()

    # Check for the updated dependency array
    assert "[mergedSelectedKeyList, updatePreserveRecordsCache]" in content, \
        "useEffect dependency array should include both mergedSelectedKeyList and updatePreserveRecordsCache"


# ======================== pass_to_pass tests ========================
# These CI checks should pass on BOTH the base commit AND after the fix.


def test_repo_lint_script():
    """Repo ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_biome_lint():
    """Repo Biome lint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_rowselection_tests():
    """Table rowSelection unit tests pass (pass_to_pass)."""
    # Run jest directly instead of npm test to avoid option parsing issues
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "Table.rowSelection",
         "--no-coverage", "--maxWorkers=1"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Table rowSelection tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_test_node():
    """Node.js compatibility test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test:node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Node tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_tsc():
    """Repo TypeScript typecheck passes (pass_to_pass)."""
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=600, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
