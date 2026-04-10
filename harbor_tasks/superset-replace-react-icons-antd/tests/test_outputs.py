"""Tests for PR #39184: Replace react-icons with antd icons."""

import json
import subprocess
from pathlib import Path

# Repository paths
REPO = Path("/workspace/superset/superset-frontend")
TABLE_PLUGIN = REPO / "plugins/plugin-chart-table"
PIVOT_PLUGIN = REPO / "plugins/plugin-chart-pivot-table"


def test_table_package_no_react_icons():
    """Table plugin package.json must not have react-icons dependency (f2p)."""
    pkg_json_path = TABLE_PLUGIN / "package.json"
    with open(pkg_json_path) as f:
        pkg = json.load(f)

    deps = pkg.get("dependencies", {})
    assert "react-icons" not in deps, \
        f"react-icons should be removed from table package.json, found: {deps.get('react-icons')}"


def test_pivot_package_no_react_icons():
    """Pivot table plugin package.json must not have react-icons dependency (f2p)."""
    pkg_json_path = PIVOT_PLUGIN / "package.json"
    with open(pkg_json_path) as f:
        pkg = json.load(f)

    deps = pkg.get("dependencies", {})
    assert "react-icons" not in deps, \
        f"react-icons should be removed from pivot package.json, found: {deps.get('react-icons')}"


def test_table_chart_no_react_icons_import():
    """TableChart.tsx must not import from react-icons/fa (f2p)."""
    table_chart_path = TABLE_PLUGIN / "src/TableChart.tsx"
    content = table_chart_path.read_text()

    assert "from 'react-icons/fa'" not in content, \
        "TableChart.tsx should not import from 'react-icons/fa'"
    assert "from \"react-icons/fa\"" not in content, \
        "TableChart.tsx should not import from \"react-icons/fa\""
    assert "FaSort" not in content, \
        "TableChart.tsx should not contain FaSort references"


def test_table_chart_imports_antd_icons():
    """TableChart.tsx must import from @ant-design/icons (f2p)."""
    table_chart_path = TABLE_PLUGIN / "src/TableChart.tsx"
    content = table_chart_path.read_text()

    assert "from '@ant-design/icons'" in content, \
        "TableChart.tsx must import from '@ant-design/icons'"
    assert "CaretUpOutlined" in content, \
        "TableChart.tsx must import CaretUpOutlined"
    assert "CaretDownOutlined" in content, \
        "TableChart.tsx must import CaretDownOutlined"
    assert "ColumnHeightOutlined" in content, \
        "TableChart.tsx must import ColumnHeightOutlined"


def test_table_chart_uses_correct_icons():
    """TableChart.tsx SortIcon component must use antd icons correctly (f2p)."""
    table_chart_path = TABLE_PLUGIN / "src/TableChart.tsx"
    content = table_chart_path.read_text()

    # Pattern: let sortIcon = <ColumnHeightOutlined />;
    assert "<ColumnHeightOutlined />" in content, \
        "SortIcon must default to ColumnHeightOutlined for unsorted state"

    # Pattern: isSortedDesc ? <CaretDownOutlined /> : <CaretUpOutlined />
    assert "<CaretDownOutlined />" in content, \
        "SortIcon must use CaretDownOutlined for descending sort"
    assert "<CaretUpOutlined />" in content, \
        "SortIcon must use CaretUpOutlined for ascending sort"


def test_pivot_table_no_react_icons_import():
    """TableRenderers.tsx must not import from react-icons/fa (f2p)."""
    pivot_renderers_path = PIVOT_PLUGIN / "src/react-pivottable/TableRenderers.tsx"
    content = pivot_renderers_path.read_text()

    assert "from 'react-icons/fa'" not in content, \
        "TableRenderers.tsx should not import from 'react-icons/fa'"
    assert "from \"react-icons/fa\"" not in content, \
        "TableRenderers.tsx should not import from \"react-icons/fa\""
    assert "FaSort" not in content, \
        "TableRenderers.tsx should not contain FaSort references"


def test_pivot_table_imports_antd_icons():
    """TableRenderers.tsx must import from @ant-design/icons (f2p)."""
    pivot_renderers_path = PIVOT_PLUGIN / "src/react-pivottable/TableRenderers.tsx"
    content = pivot_renderers_path.read_text()

    assert "from '@ant-design/icons'" in content, \
        "TableRenderers.tsx must import from '@ant-design/icons'"
    assert "CaretUpOutlined" in content, \
        "TableRenderers.tsx must import CaretUpOutlined"
    assert "CaretDownOutlined" in content, \
        "TableRenderers.tsx must import CaretDownOutlined"
    assert "ColumnHeightOutlined" in content, \
        "TableRenderers.tsx must import ColumnHeightOutlined"


def test_pivot_table_uses_correct_icons():
    """Pivot table TableRenderers must use antd icons correctly (f2p)."""
    pivot_renderers_path = PIVOT_PLUGIN / "src/react-pivottable/TableRenderers.tsx"
    content = pivot_renderers_path.read_text()

    # Should use ColumnHeightOutlined for unsorted state
    assert "<ColumnHeightOutlined" in content, \
        "Pivot table must use ColumnHeightOutlined for unsorted columns"

    # Should use CaretUpOutlined/CaretDownOutlined for sorted state
    assert "CaretUpOutlined" in content, \
        "Pivot table must use CaretUpOutlined for ascending sort"
    assert "CaretDownOutlined" in content, \
        "Pivot table must use CaretDownOutlined for descending sort"

    # Should use dynamic SortIcon selection
    assert "sortingOrder[key] === 'asc' ? CaretUpOutlined : CaretDownOutlined" in content, \
        "Pivot table must select icons based on sort order"


# =============================================================================
# PASS-TO-PASS TESTS: Repository CI tests that should pass before and after fix
# =============================================================================


def test_repo_unit_tests_table_plugin():
    """Repo's unit tests for table plugin pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=plugin-chart-table", "--maxWorkers=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Table plugin unit tests failed:\n{r.stderr[-2000:]}"


def test_repo_unit_tests_pivot_table_plugin():
    """Repo's unit tests for pivot table plugin pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=plugin-chart-pivot-table", "--maxWorkers=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Pivot table plugin unit tests failed:\n{r.stderr[-2000:]}"


def test_repo_plugins_build():
    """Repo's plugins:build passes - TypeScript compiles (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "plugins:build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Plugins build failed:\n{r.stderr[-2000:]}"
