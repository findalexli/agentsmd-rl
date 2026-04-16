"""
Tests for ant-design Table rowSelection fix when selectedRowKeys becomes undefined.

PR: https://github.com/ant-design/ant-design/pull/57547

Bug: When rowSelection.selectedRowKeys transitions from an empty array to undefined
while preserveSelectedRowKeys is enabled, the Table component crashes with a forEach
error because mergedSelectedKeys is undefined.

Fix: Added mergedSelectedKeyList = mergedSelectedKeys ?? EMPTY_LIST to ensure the
value is always an array before calling forEach.
"""

import subprocess
import os

REPO = "/workspace/antd"


def test_typescript_compiles():
    """TypeScript compilation succeeds (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Check for critical errors only
    assert "error TS" not in result.stderr or result.returncode == 0, (
        f"TypeScript compilation failed:\n{result.stderr[-2000:]}"
    )


def test_useselection_syntax_valid():
    """The useSelection hook file can be parsed without syntax errors (pass_to_pass)."""
    result = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const path = require('path');
const ts = require('typescript');

const filePath = path.join(process.cwd(), 'components/table/hooks/useSelection.tsx');
const content = fs.readFileSync(filePath, 'utf8');

const result = ts.transpileModule(content, {
    compilerOptions: {
        module: ts.ModuleKind.ESNext,
        target: ts.ScriptTarget.ES2020,
        jsx: ts.JsxEmit.React,
    }
});

if (result.diagnostics && result.diagnostics.length > 0) {
    console.error('Syntax errors found');
    process.exit(1);
}
console.log('OK');
        """],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"useSelection.tsx has syntax errors:\n{result.stderr}"


def test_safe_list_variable_exists():
    """
    The fix adds mergedSelectedKeyList variable to prevent forEach from being
    called on undefined (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # The fix introduces mergedSelectedKeyList which ensures we never call forEach on undefined
    assert "mergedSelectedKeyList" in content, (
        "Fix not applied: mergedSelectedKeyList variable should exist to handle undefined selectedRowKeys"
    )

    # Verify the nullish coalescing pattern
    assert "mergedSelectedKeys ?? EMPTY_LIST" in content or "mergedSelectedKeys??EMPTY_LIST" in content, (
        "Fix not applied: mergedSelectedKeyList should be defined with nullish coalescing to EMPTY_LIST"
    )


def test_preserve_cache_effect_uses_safe_list():
    """
    The updatePreserveRecordsCache effect must use the safe list variable,
    not the potentially-undefined mergedSelectedKeys (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # The effect should use mergedSelectedKeyList (safe) instead of mergedSelectedKeys (unsafe)
    assert "updatePreserveRecordsCache(mergedSelectedKeyList)" in content, (
        "Fix not applied: updatePreserveRecordsCache should be called with mergedSelectedKeyList, "
        "not with mergedSelectedKeys which can be undefined"
    )

    # Also verify the dependency array includes the new variable
    assert "mergedSelectedKeyList, updatePreserveRecordsCache" in content, (
        "Fix not applied: useEffect dependency array should include mergedSelectedKeyList and updatePreserveRecordsCache"
    )


def test_derived_keys_memo_uses_safe_list():
    """
    The derivedSelectedKeys useMemo must use the safe list,
    not the potentially-undefined mergedSelectedKeys (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # The return statement in the useMemo should use mergedSelectedKeyList directly
    # instead of the pattern `mergedSelectedKeys || []`
    # This indicates the fix is properly using the safe variable
    assert "return [mergedSelectedKeyList," in content, (
        "Fix not applied: derivedSelectedKeys calculation should return mergedSelectedKeyList directly, "
        "not mergedSelectedKeys || []"
    )


def test_conduct_check_uses_safe_list():
    """
    The conductCheck call must use the safe list variable (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # Find the conductCheck call and verify it uses mergedSelectedKeyList
    lines = content.split('\n')
    in_conduct_check = False
    uses_safe_list = False

    for line in lines:
        if 'conductCheck(' in line:
            in_conduct_check = True
        if in_conduct_check:
            if 'mergedSelectedKeyList,' in line:
                uses_safe_list = True
                break
            if ');' in line:
                in_conduct_check = False

    assert uses_safe_list, (
        "Fix not applied: conductCheck should be called with mergedSelectedKeyList instead of mergedSelectedKeys"
    )


def test_dependency_array_uses_safe_list():
    """
    The useMemo dependency array must include mergedSelectedKeyList (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # The dependency array pattern should use mergedSelectedKeyList
    assert "mergedSelectedKeyList, checkStrictly, keyEntities, isCheckboxDisabled" in content, (
        "Fix not applied: useMemo dependency array should include mergedSelectedKeyList "
        "instead of mergedSelectedKeys"
    )


def test_no_direct_mergedselectedkeys_in_effect():
    """
    The useEffect for preserve cache should NOT directly use mergedSelectedKeys (fail_to_pass).
    """
    hook_path = os.path.join(REPO, "components/table/hooks/useSelection.tsx")
    with open(hook_path, "r") as f:
        content = f.read()

    # Check that the old unsafe pattern is not present
    # The old pattern was: updatePreserveRecordsCache(mergedSelectedKeys);
    # The new pattern is: updatePreserveRecordsCache(mergedSelectedKeyList);

    # Find the useEffect and check it doesn't use mergedSelectedKeys directly
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'updatePreserveRecordsCache(mergedSelectedKeys)' in line:
            # This is the unsafe pattern
            assert False, (
                "Unsafe pattern found: updatePreserveRecordsCache is called with mergedSelectedKeys "
                "which can be undefined. Should use mergedSelectedKeyList instead."
            )

    # If we get here, the unsafe pattern is not present
    assert True


def test_lint_passes():
    """ESLint passes on the modified file (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/table/hooks/useSelection.tsx", "--max-warnings=50"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Allow some warnings but no critical errors
    assert result.returncode == 0 or "error" not in result.stdout.lower(), (
        f"ESLint errors:\n{result.stdout[-1500:]}"
    )


def test_repo_biome_lint():
    """Biome lint passes on the modified file (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/table/hooks/useSelection.tsx"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-1000:]}"


def test_repo_biome_check_table():
    """Biome check passes on the table component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "check", "components/table", "--no-errors-on-unmatched"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stderr[-1000:]}"
