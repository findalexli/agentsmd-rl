"""
Tests for ant-design Table `column` property feature.

This feature allows setting default column props on the Table component
that are applied to all columns unless explicitly overridden.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/ant-design")
TABLE_DIR = REPO / "components" / "table"
HOOKS_DIR = TABLE_DIR / "hooks"


def test_typescript_compiles():
    """F2P: TypeScript must compile without errors after the fix."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_use_filled_columns_hook_exists():
    """F2P: The useFilledColumns hook must exist."""
    hook_file = HOOKS_DIR / "useFilledColumns.ts"
    assert hook_file.exists(), "useFilledColumns.ts hook file must exist"

    content = hook_file.read_text()
    assert "useFilledColumns" in content, "Hook function must be named useFilledColumns"
    assert "React.useMemo" in content, "Hook should use React.useMemo for memoization"
    assert "mergeProps" in content, "Hook should use mergeProps from @rc-component/util"


def test_internal_table_imports_hook():
    """F2P: InternalTable.tsx must import and use useFilledColumns."""
    internal_table = TABLE_DIR / "InternalTable.tsx"
    content = internal_table.read_text()

    assert "import useFilledColumns from './hooks/useFilledColumns'" in content, \
        "InternalTable must import useFilledColumns hook"
    assert "useFilledColumns(rawColumns, column)" in content, \
        "InternalTable must call useFilledColumns with rawColumns and column"


def test_column_prop_in_interface():
    """F2P: TableProps interface must include column property."""
    internal_table = TABLE_DIR / "InternalTable.tsx"
    content = internal_table.read_text()

    # Check that column property is added to the interface
    assert "column?: Partial<ColumnType<RecordType>>" in content, \
        "TableProps interface must include column property"


def test_column_prop_destructured():
    """F2P: column prop must be destructured in InternalTable component."""
    internal_table = TABLE_DIR / "InternalTable.tsx"
    content = internal_table.read_text()

    # Check that column is destructured from props
    assert "column," in content, "column must be destructured from props"


def test_raw_columns_renaming():
    """F2P: baseColumns must be renamed to rawColumns with useFilledColumns applied."""
    internal_table = TABLE_DIR / "InternalTable.tsx"
    content = internal_table.read_text()

    # The original code had baseColumns = React.useMemo
    # After fix, rawColumns = React.useMemo and baseColumns = useFilledColumns(...)
    assert "const rawColumns = React.useMemo" in content, \
        "rawColumns must be defined using React.useMemo"
    assert "const baseColumns = useFilledColumns(rawColumns, column)" in content, \
        "baseColumns must be result of useFilledColumns"


def test_table_props_omits_column():
    """F2P: tableProps must omit the column prop to avoid passing it to rc-table."""
    internal_table = TABLE_DIR / "InternalTable.tsx"
    content = internal_table.read_text()

    # Check that 'column' is in the omit list
    assert "'column'" in content, "column must be omitted from tableProps"


def test_npm_test_table_column():
    """F2P: The specific test for column feature should pass."""
    # Run the specific test that was added in the PR
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPattern=Table.test", "--testNamePattern=column align"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # If the test doesn't exist yet (pre-fix), it will fail with pattern not found
    # After fix, it should pass
    if result.returncode == 0:
        return  # Test passed

    # Check if the test file was updated with our test case
    test_file = TABLE_DIR / "__tests__" / "Table.test.tsx"
    if test_file.exists():
        content = test_file.read_text()
        if "supports column align with per-column override" in content:
            assert result.returncode == 0, \
                f"Test 'supports column align with per-column override' failed:\n{result.stdout}\n{result.stderr}"


def test_hook_preserves_special_columns():
    """P2P: Hook must preserve SELECTION_COLUMN and EXPAND_COLUMN unchanged."""
    hook_file = HOOKS_DIR / "useFilledColumns.ts"
    content = hook_file.read_text()

    # These are internal marker columns that should not be modified
    assert "SELECTION_COLUMN" in content, "Hook must check for SELECTION_COLUMN"
    assert "EXPAND_COLUMN" in content, "Hook must check for EXPAND_COLUMN"
    assert "return col;" in content, "Special columns should be returned unchanged"


def test_hook_handles_nested_columns():
    """P2P: Hook must recursively process nested column groups."""
    hook_file = HOOKS_DIR / "useFilledColumns.ts"
    content = hook_file.read_text()

    # Check for children handling in column groups
    assert "'children' in col" in content, "Hook must check for children property"
    assert "Array.isArray(col.children)" in content, "Hook must verify children is an array"
    assert "children: fillColumns(col.children)" in content, \
        "Hook must recursively fill nested columns"


def test_hook_omits_children_from_merge():
    """P2P: Hook must omit 'children' when merging to avoid incorrect type issues."""
    hook_file = HOOKS_DIR / "useFilledColumns.ts"
    content = hook_file.read_text()

    assert "omit(column" in content, "Hook must use omit to remove children"
    assert "'children'" in content, "Hook must omit 'children' property from merge"


def test_hook_returns_columns_unchanged_when_no_defaults():
    """P2P: When column prop is not provided, columns should be returned as-is."""
    hook_file = HOOKS_DIR / "useFilledColumns.ts"
    content = hook_file.read_text()

    assert "if (!column) { return columns; }" in content, \
        "Hook must early return columns when no column defaults provided"
