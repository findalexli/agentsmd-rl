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
    # Use the typescript package directly to parse the file
    # Just parsing successfully means the file has valid syntax
    parse_script = """
const ts = require('typescript');
const fs = require('fs');

const filePath = 'components/table/hooks/useSelection.tsx';
const sourceText = fs.readFileSync(filePath, 'utf8');

try {
    // Parse with TypeScript - this will throw/have parseDiagnostics on syntax errors
    const sourceFile = ts.createSourceFile(
        filePath,
        sourceText,
        ts.ScriptTarget.Latest,
        true,
        ts.ScriptKind.TSX
    );

    // Check for parse errors (syntax errors)
    if (sourceFile.parseDiagnostics && sourceFile.parseDiagnostics.length > 0) {
        sourceFile.parseDiagnostics.forEach(err => {
            const { line, character } = ts.getLineAndCharacterOfPosition(sourceFile, err.start);
            console.error(`Syntax error at ${line + 1}:${character + 1}: ${ts.flattenDiagnosticMessageText(err.messageText, '\\n')}`);
        });
        process.exit(1);
    } else {
        console.log('No syntax errors found');
        process.exit(0);
    }
} catch (err) {
    console.error(`Parse error: ${err.message}`);
    process.exit(1);
}
"""
    # Write and run the parse script
    script_path = f"{REPO}/check_syntax.js"
    with open(script_path, "w") as f:
        f.write(parse_script)

    result = subprocess.run(
        ["node", "check_syntax.js"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )

    # Cleanup
    os.remove(script_path)

    assert result.returncode == 0, f"TypeScript syntax error:\n{result.stdout}\n{result.stderr}"


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

    # Verify the cache update in useEffect uses mergedSelectedKeyList (not raw mergedSelectedKeys)
    assert "updatePreserveRecordsCache(mergedSelectedKeyList)" in content, \
        "Cache update should use mergedSelectedKeyList"

    # Check that updatePreserveRecordsCache in the useEffect is NOT called with raw mergedSelectedKeys
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "updatePreserveRecordsCache(" in line and "mergedSelectedKeyList" not in line:
            # Allow the effect dependency array line
            if "updatePreserveRecordsCache" in line and ("[" in line or "]" in line):
                continue
            # Allow setSelectedKeys callback which passes 'keys' parameter (different context)
            context_lines = lines[max(0, i-10):i+1]
            context = "\n".join(context_lines)
            if "setSelectedKeys" in context and "keys)" in line:
                continue
            assert False, f"Line {i+1} calls updatePreserveRecordsCache without mergedSelectedKeyList: {line}"


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
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=Table.rowSelection",
         "--testNamePatterns=receive selectedRowKeys from",
         "--no-coverage", "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    # Check that the test passed
    assert result.returncode == 0, \
        f"Upstream unit test failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_no_crash_on_undefined_selected_row_keys():
    """
    Integration test: Verify no crash when selectedRowKeys becomes undefined
    with preserveSelectedRowKeys enabled.

    Uses TypeScript test file with tsx/ts-node for proper JSX/TS support.
    """
    # Create a TypeScript test script that reproduces the crash
    test_script = """
import * as React from 'react';
import * as ReactDOMServer from 'react-dom/server';
import Table from './components/table';

// Test: Render with selectedRowKeys=[], then rerender with undefined + preserveSelectedRowKeys
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

    # Write and run test script
    test_file = f"{REPO}/test_crash_ts.ts"
    with open(test_file, "w") as f:
        f.write(test_script)

    result = subprocess.run(
        ["npx", "tsx", "test_crash_ts.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
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
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=Table.rowSelection",
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
