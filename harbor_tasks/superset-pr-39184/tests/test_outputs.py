"""
Tests for apache/superset#39184: Replace react-icons with antd icons

This PR removes the react-icons dependency (83MB) and replaces the sort icons
with equivalent antd icons from @ant-design/icons.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
FRONTEND = REPO / "superset-frontend"
TABLE_CHART = FRONTEND / "plugins/plugin-chart-table/src/TableChart.tsx"
PIVOT_TABLE = FRONTEND / "plugins/plugin-chart-pivot-table/src/react-pivottable/TableRenderers.tsx"
TABLE_PKG = FRONTEND / "plugins/plugin-chart-table/package.json"
PIVOT_PKG = FRONTEND / "plugins/plugin-chart-pivot-table/package.json"


def test_table_chart_uses_antd_icons():
    """TableChart.tsx imports sort icons from @ant-design/icons (fail_to_pass)."""
    content = TABLE_CHART.read_text()

    # Must import from @ant-design/icons
    assert "@ant-design/icons" in content, (
        "TableChart.tsx must import icons from @ant-design/icons"
    )

    # Must import all three required icons
    assert "CaretUpOutlined" in content, "Missing CaretUpOutlined import"
    assert "CaretDownOutlined" in content, "Missing CaretDownOutlined import"
    assert "ColumnHeightOutlined" in content, "Missing ColumnHeightOutlined import"


def test_table_chart_no_react_icons():
    """TableChart.tsx does not import from react-icons (fail_to_pass)."""
    content = TABLE_CHART.read_text()

    # Must NOT import from react-icons
    assert "react-icons" not in content, (
        "TableChart.tsx must not import from react-icons"
    )
    assert "FaSort" not in content, "FaSort from react-icons should be removed"


def test_pivot_table_uses_antd_icons():
    """TableRenderers.tsx imports sort icons from @ant-design/icons (fail_to_pass)."""
    content = PIVOT_TABLE.read_text()

    # Must import from @ant-design/icons
    assert "@ant-design/icons" in content, (
        "TableRenderers.tsx must import icons from @ant-design/icons"
    )

    # Must import all three required icons
    assert "CaretUpOutlined" in content, "Missing CaretUpOutlined import"
    assert "CaretDownOutlined" in content, "Missing CaretDownOutlined import"
    assert "ColumnHeightOutlined" in content, "Missing ColumnHeightOutlined import"


def test_pivot_table_no_react_icons():
    """TableRenderers.tsx does not import from react-icons (fail_to_pass)."""
    content = PIVOT_TABLE.read_text()

    # Must NOT import from react-icons
    assert "react-icons" not in content, (
        "TableRenderers.tsx must not import from react-icons"
    )
    assert "FaSort" not in content, "FaSort from react-icons should be removed"


def test_sort_icon_logic_table_chart():
    """SortIcon function uses correct icon for each sort state (fail_to_pass)."""
    content = TABLE_CHART.read_text()

    # Find the SortIcon function and check the icon assignments
    # Default (unsorted) should use ColumnHeightOutlined
    assert "ColumnHeightOutlined" in content, "Default icon should be ColumnHeightOutlined"

    # Check that ascending uses CaretUpOutlined and descending uses CaretDownOutlined
    # The logic: isSortedDesc ? CaretDownOutlined : CaretUpOutlined
    assert re.search(r"isSortedDesc\s*\?\s*<CaretDownOutlined", content), (
        "Descending sort should use CaretDownOutlined"
    )
    assert re.search(r":\s*<CaretUpOutlined", content), (
        "Ascending sort should use CaretUpOutlined"
    )


def test_sort_icon_logic_pivot_table():
    """TableRenderers uses correct icon for each sort state (fail_to_pass)."""
    content = PIVOT_TABLE.read_text()

    # Default (unsorted) should use ColumnHeightOutlined
    assert "<ColumnHeightOutlined" in content, "Default icon should be ColumnHeightOutlined"

    # Check ascending/descending logic
    # The logic: sortingOrder[key] === 'asc' ? CaretUpOutlined : CaretDownOutlined
    assert re.search(r"===\s*'asc'\s*\?\s*CaretUpOutlined\s*:\s*CaretDownOutlined", content), (
        "Sort icon should use CaretUpOutlined for asc and CaretDownOutlined for desc"
    )


def test_table_package_no_react_icons_dep():
    """plugin-chart-table/package.json does not have react-icons dependency (fail_to_pass)."""
    content = TABLE_PKG.read_text()

    assert "react-icons" not in content, (
        "plugin-chart-table/package.json should not list react-icons as dependency"
    )


def test_pivot_package_no_react_icons_dep():
    """plugin-chart-pivot-table/package.json does not have react-icons dependency (fail_to_pass)."""
    content = PIVOT_PKG.read_text()

    assert "react-icons" not in content, (
        "plugin-chart-pivot-table/package.json should not list react-icons as dependency"
    )


def test_valid_import_syntax():
    """Import statement uses valid syntax with destructuring (pass_to_pass)."""
    content = TABLE_CHART.read_text()

    # Either the old react-icons imports or new antd imports should be syntactically valid
    # This verifies the file has valid import structure
    has_react_icons = "from 'react-icons/fa'" in content
    has_antd_icons = "from '@ant-design/icons'" in content

    # File should have one or the other
    assert has_react_icons or has_antd_icons, (
        "File must have valid icon imports (either react-icons or @ant-design/icons)"
    )


def test_sort_icon_function_exists():
    """SortIcon function exists and handles column sorting (pass_to_pass)."""
    content = TABLE_CHART.read_text()

    # SortIcon function should exist
    assert "function SortIcon" in content, "SortIcon function must exist"

    # It should use isSorted and isSortedDesc for column state
    assert "isSorted" in content, "SortIcon must check isSorted state"
    assert "isSortedDesc" in content, "SortIcon must check isSortedDesc state"


# =============================================================================
# Pass-to-pass tests: Repo CI commands (must use subprocess.run)
# =============================================================================

FRONTEND = REPO / "superset-frontend"


def test_repo_oxlint_table_plugin():
    """Oxlint passes on plugin-chart-table (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "oxlint",
            "--config", "oxlint.json",
            "--quiet",
            "plugins/plugin-chart-table/src/",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND,
    )
    assert r.returncode == 0, f"Oxlint failed:\n{r.stderr[-1000:]}"


def test_repo_oxlint_pivot_plugin():
    """Oxlint passes on plugin-chart-pivot-table (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "oxlint",
            "--config", "oxlint.json",
            "--quiet",
            "plugins/plugin-chart-pivot-table/src/",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=FRONTEND,
    )
    assert r.returncode == 0, f"Oxlint failed:\n{r.stderr[-1000:]}"


def test_repo_jest_table_chart():
    """Jest tests pass for TableChart component (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "jest",
            "plugins/plugin-chart-table/test/TableChart.test.tsx",
            "--passWithNoTests",
            "--silent",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=FRONTEND,
        env={
            **__import__("os").environ,
            "NODE_OPTIONS": "--max-old-space-size=4096",
        },
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"


def test_repo_jest_pivot_renderers():
    """Jest tests pass for pivot table renderers (pass_to_pass)."""
    r = subprocess.run(
        [
            "npx", "jest",
            "plugins/plugin-chart-pivot-table/test/react-pivottable/tableRenders.test.tsx",
            "--passWithNoTests",
            "--silent",
        ],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=FRONTEND,
        env={
            **__import__("os").environ,
            "NODE_OPTIONS": "--max-old-space-size=4096",
        },
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-1000:]}"
