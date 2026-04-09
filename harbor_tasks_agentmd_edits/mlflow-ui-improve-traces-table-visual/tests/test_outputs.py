"""
Task: mlflow-ui-improve-traces-table-visual
Repo: mlflow/mlflow @ bc59a546e39cd15f9ae92d32a3766b0892c40007
PR:   20437

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/mlflow"
COLUMN_SELECTOR = Path(REPO) / "mlflow/server/js/src/shared/web-shared/genai-traces-table/components/EvaluationsOverviewColumnSelectorGrouped.tsx"
GENAI_TRACES_TABLE = Path(REPO) / "mlflow/server/js/src/shared/web-shared/genai-traces-table/GenAITracesTable.tsx"


def _read_file(path: Path) -> str:
    """Read file contents, fail if not found."""
    assert path.exists(), f"File not found: {path}"
    return path.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - TypeScript compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    js_dir = Path(REPO) / "mlflow/server/js"
    r = subprocess.run(
        ["yarn", "tsc", "--noEmit", "--skipLibCheck"],
        cwd=js_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Ignore lib check errors, focus on our files
    stderr_filtered = "\n".join(
        line for line in r.stderr.split("\n")
        if "error TS" in line and "genai-traces-table" in line
    ) if r.stderr else ""
    assert not stderr_filtered, f"TypeScript errors in modified files:\n{stderr_filtered}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - Core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tree_component_imported():
    """Column selector must import and use Tree component from design system."""
    source = _read_file(COLUMN_SELECTOR)
    # Check Tree is imported
    assert "Tree," in source or "import { Tree }" in source or "Tree }" in source, \
        "Tree component not imported from @databricks/design-system"
    # Check Tree is used in JSX
    assert "<Tree" in source, "Tree component not used in JSX"


# [pr_diff] fail_to_pass
def test_usecallback_for_handlers():
    """Event handlers must be memoized with useCallback for performance."""
    source = _read_file(COLUMN_SELECTOR)
    assert "useCallback" in source, "useCallback not imported or used"
    # Check handleCheck uses useCallback
    assert "const handleCheck = useCallback(" in source, \
        "handleCheck handler not wrapped in useCallback"


# [pr_diff] fail_to_pass
def test_search_functionality_implemented():
    """Search input with SearchIcon must be present for filtering columns."""
    source = _read_file(COLUMN_SELECTOR)
    # Check SearchIcon is imported
    assert "SearchIcon," in source or "SearchIcon }" in source, \
        "SearchIcon not imported from @databricks/design-system"
    # Check Input component is imported
    assert "Input," in source or "Input }" in source, \
        "Input not imported from @databricks/design-system"
    # Check search state exists
    assert "setSearch" in source, "setSearch state setter not found"
    # Check search input is rendered
    assert 'prefix={<SearchIcon />}' in source or "prefix={<SearchIcon" in source, \
        "SearchIcon not used as Input prefix"


# [pr_diff] fail_to_pass
def test_dropdown_replaces_dialog_combobox():
    """DialogCombobox must be replaced with Dropdown component."""
    source = _read_file(COLUMN_SELECTOR)
    # Dropdown should be imported
    assert "Dropdown," in source or "Dropdown }" in source, \
        "Dropdown not imported from @databricks/design-system"
    # DialogCombobox components should not be present
    assert "DialogCombobox" not in source, \
        "DialogCombobox still used (should be replaced with Dropdown)"
    # Dropdown should be used
    assert "<Dropdown" in source, "Dropdown component not used in JSX"


# [pr_diff] fail_to_pass
def test_tree_performance_optimized():
    """Tree must have motion disabled for performance (motion: null)."""
    source = _read_file(COLUMN_SELECTOR)
    # Check motion is disabled in dangerouslySetAntdProps
    assert "motion: null" in source, \
        "Tree animations not disabled (motion: null required for performance)"


# [pr_diff] fail_to_pass
def test_group_selection_logic():
    """Tree must handle group-level selection/deselection via GROUP- keys."""
    source = _read_file(COLUMN_SELECTOR)
    # Check for GROUP- key prefix handling
    assert "GROUP-" in source, "GROUP- prefix not used for group keys"
    # Check for group key detection
    assert "key.startsWith('GROUP-')" in source or 'key.startsWith("GROUP-")' in source, \
        "Group selection logic not implemented (key.startsWith('GROUP-'))"


# [pr_diff] fail_to_pass
def test_genai_traces_table_uses_grouped_selector():
    """GenAITracesTable must use EvaluationsOverviewColumnSelectorGrouped instead of flat selector."""
    source = _read_file(GENAI_TRACES_TABLE)
    # Should import the grouped selector
    assert "EvaluationsOverviewColumnSelectorGrouped" in source, \
        "EvaluationsOverviewColumnSelectorGrouped not imported"
    # Should NOT import the old flat selector
    assert "EvaluationsOverviewColumnSelector }" not in source and \
           "EvaluationsOverviewColumnSelector," not in source, \
        "Old EvaluationsOverviewColumnSelector still imported"
    # Should use the grouped selector in JSX
    assert "<EvaluationsOverviewColumnSelectorGrouped" in source, \
        "EvaluationsOverviewColumnSelectorGrouped not used in JSX"


# [pr_diff] fail_to_pass
def test_correct_props_passed_to_selector():
    """GenAITracesTable must pass correct props (toggleColumns, setSelectedColumns) to selector."""
    source = _read_file(GENAI_TRACES_TABLE)
    # Check for toggleColumns prop
    assert "toggleColumns={toggleColumns}" in source, \
        "toggleColumns prop not passed to column selector"
    # Check for setSelectedColumns prop
    assert "setSelectedColumns={setSelectedColumns}" in source, \
        "setSelectedColumns prop not passed to column selector"
    # Old prop should not be present
    assert "setSelectedColumnsWithHiddenColumns" not in source, \
        "Old setSelectedColumnsWithHiddenColumns prop still used"


# [pr_diff] fail_to_pass
def test_search_highlighting_implemented():
    """createHighlightedNode function must exist for search result highlighting."""
    source = _read_file(COLUMN_SELECTOR)
    assert "createHighlightedNode" in source, \
        "createHighlightedNode function not defined"
    # Check it wraps matching text with <strong>
    assert "<strong>" in source and "</strong>" in source, \
        "createHighlightedNode doesn't wrap matches with <strong> tags"


# [pr_diff] fail_to_pass
def test_memoized_dropdown_content():
    """Dropdown content must be memoized with useMemo to prevent re-renders."""
    source = _read_file(COLUMN_SELECTOR)
    # Check dropdownContent uses useMemo
    assert "const dropdownContent = useMemo(" in source, \
        "dropdownContent not memoized with useMemo"


# [pr_diff] fail_to_pass
def test_dropdown_visibility_state():
    """Dropdown visibility must be controlled with dropdownVisible state."""
    source = _read_file(COLUMN_SELECTOR)
    assert "dropdownVisible" in source, "dropdownVisible state not found"
    assert "setDropdownVisible" in source, "setDropdownVisible not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - Regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_component_exports_preserved():
    """Component must still export EvaluationsOverviewColumnSelectorGrouped."""
    source = _read_file(COLUMN_SELECTOR)
    assert "export const EvaluationsOverviewColumnSelectorGrouped" in source, \
        "Component export missing or renamed"


# [static] pass_to_pass
def test_props_interface_preserved():
    """Component Props interface must have required properties."""
    source = _read_file(COLUMN_SELECTOR)
    # Check interface Props exists
    assert "interface Props" in source, "Props interface not defined"
    # Check required props exist
    assert "columns" in source, "columns prop not in interface"
    assert "selectedColumns" in source, "selectedColumns prop not in interface"
    assert "toggleColumns" in source, "toggleColumns prop not in interface"
    assert "setSelectedColumns" in source, "setSelectedColumns prop not in interface"
