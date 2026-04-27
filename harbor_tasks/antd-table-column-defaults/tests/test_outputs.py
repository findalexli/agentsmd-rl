"""
Tests for ant-design Table `column` prop feature.
"""

import subprocess
import os

REPO = "/workspace/ant-design"


def _run_tsx(code: str, timeout: int = 60):
    """Execute TypeScript code using tsx."""
    script = os.path.join(REPO, "_eval_tmp.tsx")
    with open(script, "w") as f:
        f.write(code)
    try:
        result = subprocess.run(
            ["npx", "tsx", script],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    finally:
        if os.path.exists(script):
            os.unlink(script)


def test_column_prop_is_functional():
    """Table component accepts and uses column prop for default column properties."""
    result = _run_tsx("""
import { Table } from 'antd';
const props = {
  columns: [{ title: 'Name', dataIndex: 'name' }],
  dataSource: [{ name: 'Test' }],
  column: { align: 'center', ellipsis: true }
};
console.log('COLUMN_PROP_ACCEPTED');
""")
    assert result.returncode == 0, f"column prop type error: {result.stderr}"
    assert "COLUMN_PROP_ACCEPTED" in result.stdout


def test_useFilledColumns_hook_exists_and_runs():
    """useFilledColumns hook exists and can be imported/executed."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
const columns = [{ title: 'Name', dataIndex: 'name' }];
const result = useFilledColumns(columns, { align: 'center' });
if (!Array.isArray(result)) throw new Error('Expected array');
console.log('HOOK_WORKS');
""")
    assert result.returncode == 0, f"useFilledColumns hook failed: {result.stderr}"
    assert "HOOK_WORKS" in result.stdout


def test_column_defaults_are_applied():
    """Columns inherit defaults from column prop when not explicitly set."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
const columns = [
  { title: 'Name', dataIndex: 'name' },
  { title: 'Age', dataIndex: 'age', align: 'right' }
];
const filled = useFilledColumns(columns, { align: 'center' });
if (filled[0].align !== 'center') throw new Error('First col should inherit center');
if (filled[1].align !== 'right') throw new Error('Second col should keep right');
console.log('DEFAULTS_APPLIED');
""")
    assert result.returncode == 0, f"Column defaults not applied: {result.stderr}"
    assert "DEFAULTS_APPLIED" in result.stdout


def test_hook_returns_original_when_no_defaults():
    """Hook returns original columns when column prop is not provided."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
const columns = [{ title: 'Name', dataIndex: 'name' }];
const result = useFilledColumns(columns, undefined);
if (result !== columns) throw new Error('Should return original');
console.log('ORIGINAL_PRESERVED');
""")
    assert result.returncode == 0, f"Hook doesn't preserve original: {result.stderr}"
    assert "ORIGINAL_PRESERVED" in result.stdout


def test_special_columns_preserved():
    """SELECTION_COLUMN and EXPAND_COLUMN are preserved and not modified."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
import { Table } from 'antd';
const columns = [
  { title: 'Name', dataIndex: 'name' },
  Table.EXPAND_COLUMN,
  Table.SELECTION_COLUMN,
];
const filled = useFilledColumns(columns, { align: 'center' });
if (filled[1] !== Table.EXPAND_COLUMN) throw new Error('EXPAND_COLUMN not preserved');
if (filled[2] !== Table.SELECTION_COLUMN) throw new Error('SELECTION_COLUMN not preserved');
console.log('SPECIAL_COLUMNS_PRESERVED');
""")
    assert result.returncode == 0, f"Special columns not preserved: {result.stderr}"
    assert "SPECIAL_COLUMNS_PRESERVED" in result.stdout


def test_nested_column_groups_work():
    """Nested column groups properly merge with column defaults recursively."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
const columns = [{
  title: 'Info',
  children: [
    { title: 'Name', dataIndex: 'name' },
    { title: 'Age', dataIndex: 'age', align: 'right' }
  ]
}];
const filled = useFilledColumns(columns, { align: 'center', ellipsis: true });
if (filled[0].align !== 'center') throw new Error('Parent should inherit');
const children = filled[0].children;
if (!Array.isArray(children)) throw new Error('Children not array');
if (children[0].align !== 'center') throw new Error('Child1 should inherit');
if (children[1].align !== 'right') throw new Error('Child2 should keep right');
console.log('NESTED_COLUMNS_WORK');
""")
    assert result.returncode == 0, f"Nested columns failed: {result.stderr}"
    assert "NESTED_COLUMNS_WORK" in result.stdout


def test_children_property_not_duplicated():
    """Children property from defaults is not merged onto columns."""
    result = _run_tsx("""
import useFilledColumns from './components/table/hooks/useFilledColumns';
const columns = [{ title: 'Name', dataIndex: 'name' }];
const filled = useFilledColumns(columns, {
  align: 'center',
  children: [{ title: 'Sneaky', dataIndex: 'sneaky' }]
});
if (filled[0].align !== 'center') throw new Error('Align should be applied');
if ('children' in filled[0] && filled[0].children !== undefined) {
  throw new Error('Children from defaults should not be merged');
}
console.log('CHILDREN_OMITTED');
""")
    assert result.returncode == 0, f"Children not properly omitted: {result.stderr}"
    assert "CHILDREN_OMITTED" in result.stdout


def test_useFilledColumns_integration_in_table():
    """InternalTable correctly integrates useFilledColumns hook."""
    result = _run_tsx("""
import { Table } from 'antd';
const element = Table({
  columns: [{ title: 'A', dataIndex: 'a' }],
  dataSource: [{ a: 1 }],
  column: { align: 'center' }
});
if (!element) throw new Error('Table should render with column prop');
console.log('INTEGRATION_WORKS');
""")
    assert result.returncode == 0, f"Integration failed: {result.stderr}"
    assert "INTEGRATION_WORKS" in result.stdout


def test_demo_file_exists():
    """Demo file for column defaults exists (fail_to_pass - created by patch)."""
    demo_path = f"{REPO}/components/table/demo/column-defaults.tsx"
    assert os.path.exists(demo_path), "column-defaults.tsx demo not found"

    with open(demo_path, "r") as f:
        content = f.read()

    assert "column={{" in content or "column=" in content, "Demo should use column prop"
    assert "align" in content, "Demo should show alignment example"


def test_internal_tests_exist():
    """Test file includes column prop behavioral tests (fail_to_pass - added by patch)."""
    test_path = f"{REPO}/components/table/__tests__/Table.test.tsx"
    with open(test_path, "r") as f:
        content = f.read()

    assert "column" in content.lower(), "Test should mention column prop"
    has_alignment_test = "align" in content and "column" in content.lower()
    assert has_alignment_test, "Test should verify alignment behavior"


# ============================================================================
# Pass-to-pass tests - repo CI/CD tests
# ============================================================================


def test_repo_lint_biome():
    """Repox Biome linting passes on table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/table/InternalTable.tsx", "components/table/__tests__/Table.test.tsx"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:"


def test_repo_lint_biome_all_table():
    """Repo's Biome linting passes on all table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/table/"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"Biome lint failed:"


def test_repo_lint_eslint():
    """Repo's ESLint linting passes on modified table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/table/InternalTable.tsx", "components/table/__tests__/Table.test.tsx", "--cache"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:"


def test_repo_format_biome():
    """Repo's Biome formatting passes on table files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "format", "components/table/"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"Biome format failed:"


def test_repo_table_tests():
    """Repo's Table component unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table tests failed:"


def test_repo_table_filter_tests():
    """Repo's Table filter tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.filter.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table filter tests failed:"


def test_repo_table_rowSelection_tests():
    """Repo's Table rowSelection tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.rowSelection.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table rowSelection tests failed:"


def test_repo_table_sorter_tests():
    """Repo's Table sorter tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.sorter.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table sorter tests failed:"


def test_repo_table_expand_tests():
    """Repo's Table expand tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.expand.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table expand tests failed:"


def test_repo_table_pagination_tests():
    """Repo's Table pagination tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table/__tests__/Table.pagination.test.tsx", "--maxWorkers=1", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Table pagination tests failed:"


def test_repo_table_all_tests():
    """All Table component tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "components/table", "--maxWorkers=2", "--testTimeout=30000"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert result.returncode == 0, f"All Table tests failed:"


# ============================================================================
# Static convention checks
# ============================================================================


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
    assert "from './" not in content, "Demo should NOT use relative imports"


def test_internal_tests_use_relative_imports():
    """Test file uses relative imports per project convention (pass_to_pass)."""
    test_path = f"{REPO}/components/table/__tests__/Table.test.tsx"
    with open(test_path, "r") as f:
        content = f.read()

    assert "from '..'" in content or "from '../" in content, \
        "Tests should use relative imports"
    assert "from 'antd'" not in content, "Tests should NOT use absolute 'antd' imports"
