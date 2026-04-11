"""
Tests for ant-design Table `column` prop feature.

This tests that:
1. Table supports a `column` prop for shared column defaults
2. Columns inherit from `column` when they don't declare a property
3. Columns can override `column` defaults with their own values
4. Special columns (EXPAND_COLUMN, SELECTION_COLUMN) are preserved
5. Nested column groups work correctly with column defaults
"""

import subprocess
import sys
import os

REPO = "/workspace/ant-design"


def test_column_prop_types_exist():
    """TableProps interface includes column prop type definition."""
    with open(f"{REPO}/components/table/InternalTable.tsx", "r") as f:
        content = f.read()
    assert "column?: Partial<ColumnType<RecordType>>" in content, "column prop type not found in TableProps"


def test_useFilledColumns_hook_exists():
    """useFilledColumns hook is implemented."""
    hook_path = f"{REPO}/components/table/hooks/useFilledColumns.ts"
    assert os.path.exists(hook_path), "useFilledColumns.ts hook not found"

    with open(hook_path, "r") as f:
        content = f.read()

    assert "mergeProps" in content, "useFilledColumns should use mergeProps"
    assert "SELECTION_COLUMN" in content, "Should handle SELECTION_COLUMN"
    assert "EXPAND_COLUMN" in content, "Should handle EXPAND_COLUMN"
    assert "fillColumns" in content, "Should implement fillColumns function"


def test_useFilledColumns_imported():
    """useFilledColumns is imported and used in InternalTable."""
    with open(f"{REPO}/components/table/InternalTable.tsx", "r") as f:
        content = f.read()

    assert "import useFilledColumns from './hooks/useFilledColumns'" in content, \
        "useFilledColumns import not found"
    assert "useFilledColumns(rawColumns, column)" in content, \
        "useFilledColumns hook usage not found"


def test_column_prop_passed_to_hook():
    """column prop is destructured and passed to useFilledColumns."""
    with open(f"{REPO}/components/table/InternalTable.tsx", "r") as f:
        content = f.read()

    assert "column," in content, "column prop should be destructured"
    assert "rawColumns" in content, "rawColumns should be defined"


def test_column_omitted_from_table_props():
    """column prop is omitted from rc-table props to avoid passing through."""
    with open(f"{REPO}/components/table/InternalTable.tsx", "r") as f:
        content = f.read()

    assert "'column'," in content, "column should be omitted from tableProps"


def test_column_default_inheritance_logic():
    """Columns inherit defaults from column prop when not explicitly set."""
    hook_path = f"{REPO}/components/table/hooks/useFilledColumns.ts"
    with open(hook_path, "r") as f:
        content = f.read()

    assert "if (!column)" in content, "Should handle case when column is undefined"
    assert "return columns" in content, "Should return original columns when no defaults"
    assert "mergeProps(" in content, "Should use mergeProps for prop merging"


def test_special_columns_preserved():
    """SELECTION_COLUMN and EXPAND_COLUMN are preserved and not modified."""
    hook_path = f"{REPO}/components/table/hooks/useFilledColumns.ts"
    with open(hook_path, "r") as f:
        content = f.read()

    assert "col === SELECTION_COLUMN || col === EXPAND_COLUMN" in content, \
        "Should check for special columns and return them unchanged"


def test_nested_column_groups():
    """Nested column groups properly merge with column defaults recursively."""
    hook_path = f"{REPO}/components/table/hooks/useFilledColumns.ts"
    with open(hook_path, "r") as f:
        content = f.read()

    assert "'children' in col" in content, "Should check for children in column"
    assert "Array.isArray(col.children)" in content, "Should check if children is array"
    assert "fillColumns(col.children)" in content, "Should recursively fill children"


def test_children_omitted_from_merge():
    """children property is omitted when merging to avoid duplication issues."""
    hook_path = f"{REPO}/components/table/hooks/useFilledColumns.ts"
    with open(hook_path, "r") as f:
        content = f.read()

    assert "omit(column" in content, "Should omit children from column before merge"
    assert "'children'" in content, "Should omit children property"


# ============================================================================
# Pass-to-pass tests - repo CI/CD tests (verified working in Docker)
# ============================================================================


def test_repo_lint_biome():
    """Repo's Biome linting passes on table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/table/InternalTable.tsx", "components/table/__tests__/Table.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-500:]}"


def test_repo_lint_biome_all_table():
    """Repo's Biome linting passes on all table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/table/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint on table dir failed:\n{result.stderr[-500:]}"


def test_repo_lint_eslint():
    """Repo's ESLint linting passes on modified table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/table/InternalTable.tsx", "components/table/__tests__/Table.test.tsx", "--cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_repo_table_tests():
    """Repo's Table component unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table tests failed:\n{result.stderr[-500:]}"


def test_repo_table_filter_tests():
    """Repo's Table filter tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.filter.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table filter tests failed:\n{result.stderr[-500:]}"


def test_repo_table_rowSelection_tests():
    """Repo's Table rowSelection tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.rowSelection.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table rowSelection tests failed:\n{result.stderr[-500:]}"


def test_repo_table_sorter_tests():
    """Repo's Table sorter tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.sorter.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table sorter tests failed:\n{result.stderr[-500:]}"


def test_repo_table_expand_tests():
    """Repo's Table expand tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.expand.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table expand tests failed:\n{result.stderr[-500:]}"


def test_repo_table_pagination_tests():
    """Repo's Table pagination tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.pagination.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Table pagination tests failed:\n{result.stderr[-500:]}"


# ============================================================================
# Static checks (file content/structure checks)
# ============================================================================


def test_demo_file_exists():
    """Demo file for column defaults exists (fail_to_pass - created by patch)."""
    demo_path = f"{REPO}/components/table/demo/column-defaults.tsx"
    assert os.path.exists(demo_path), "column-defaults.tsx demo not found"

    with open(demo_path, "r") as f:
        content = f.read()

    assert "column={{" in content, "Demo should use column prop"
    assert "align:" in content, "Demo should show alignment example"


def test_demo_uses_absolute_imports():
    """Demo file uses absolute imports per project convention (pass_to_pass)."""
    demo_path = f"{REPO}/components/table/demo/column-defaults.tsx"
    if not os.path.exists(demo_path):
        return

    with open(demo_path, "r") as f:
        content = f.read()

    assert "from 'antd'" in content or "from 'antd/" in content, \
        "Demo should use absolute imports from 'antd'"
    assert "from '../" not in content, "Demo should NOT use relative imports"
    assert "from './" not in content, "Demo should NOT use relative imports for components"


def test_internal_test_file_exists():
    """Test file exists with column prop tests (fail_to_pass - added by patch)."""
    test_path = f"{REPO}/components/table/__tests__/Table.test.tsx"
    with open(test_path, "r") as f:
        content = f.read()

    assert "supports column align with per-column override" in content, \
        "Test for column prop not found"


def test_internal_tests_use_relative_imports():
    """Test file uses relative imports per project convention (pass_to_pass)."""
    test_path = f"{REPO}/components/table/__tests__/Table.test.tsx"
    with open(test_path, "r") as f:
        content = f.read()

    assert "from '..'" in content or "from '../" in content, \
        "Tests should use relative imports"
    assert "from 'antd'" not in content, "Tests should NOT use absolute 'antd' imports"
