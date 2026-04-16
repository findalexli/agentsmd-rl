"""
Benchmark tests for apache/superset#39017: Add certification fields to MCP list tools.

This PR adds `certified_by`, `certification_details`, and `description` to the
default columns returned by `list_charts`, `list_dashboards`, and `list_datasets`
MCP tools.

Tests use file parsing instead of imports to avoid Superset's complex dependencies.
"""

import ast
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")


def _extract_module_level_assignment(filepath: Path, var_name: str) -> list | None:
    """Extract a module-level list assignment from a Python file using AST."""
    content = filepath.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.List):
                        return [
                            elt.value if isinstance(elt, ast.Constant) else str(elt)
                            for elt in node.value.elts
                        ]
    return None


def _extract_class_fields(filepath: Path, class_name: str) -> set:
    """Extract field names from a Pydantic model class definition using AST."""
    content = filepath.read_text()
    tree = ast.parse(content)

    fields = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.add(item.target.id)
    return fields


def _extract_dict_keys(filepath: Path, var_name: str) -> set:
    """Extract dictionary keys from a module-level dict assignment using AST."""
    content = filepath.read_text()
    tree = ast.parse(content)

    keys = set()
    for node in ast.walk(tree):
        # Handle regular assignment: VAR = {...}
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    if isinstance(node.value, ast.Dict):
                        for key in node.value.keys:
                            if isinstance(key, ast.Constant):
                                keys.add(key.value)
        # Handle annotated assignment: VAR: type = {...}
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == var_name:
                if isinstance(node.value, ast.Dict):
                    for key in node.value.keys:
                        if isinstance(key, ast.Constant):
                            keys.add(key.value)
    return keys


# =============================================================================
# FAIL-TO-PASS TESTS
# These tests MUST fail on the base commit and pass after the fix.
# =============================================================================


def test_chart_default_columns_include_certification():
    """CHART_DEFAULT_COLUMNS includes certified_by and certification_details (fail_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    default_cols = _extract_module_level_assignment(schema_discovery, "CHART_DEFAULT_COLUMNS")

    assert default_cols is not None, "CHART_DEFAULT_COLUMNS not found"
    assert "certified_by" in default_cols, (
        f"'certified_by' not in CHART_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "certification_details" in default_cols, (
        f"'certification_details' not in CHART_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "description" in default_cols, (
        f"'description' not in CHART_DEFAULT_COLUMNS: {default_cols}"
    )


def test_dataset_default_columns_include_certification():
    """DATASET_DEFAULT_COLUMNS includes certified_by and certification_details (fail_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    default_cols = _extract_module_level_assignment(schema_discovery, "DATASET_DEFAULT_COLUMNS")

    assert default_cols is not None, "DATASET_DEFAULT_COLUMNS not found"
    assert "certified_by" in default_cols, (
        f"'certified_by' not in DATASET_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "certification_details" in default_cols, (
        f"'certification_details' not in DATASET_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "description" in default_cols, (
        f"'description' not in DATASET_DEFAULT_COLUMNS: {default_cols}"
    )


def test_dashboard_default_columns_include_certification():
    """DASHBOARD_DEFAULT_COLUMNS includes certified_by and certification_details (fail_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    default_cols = _extract_module_level_assignment(schema_discovery, "DASHBOARD_DEFAULT_COLUMNS")

    assert default_cols is not None, "DASHBOARD_DEFAULT_COLUMNS not found"
    assert "certified_by" in default_cols, (
        f"'certified_by' not in DASHBOARD_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "certification_details" in default_cols, (
        f"'certification_details' not in DASHBOARD_DEFAULT_COLUMNS: {default_cols}"
    )
    assert "description" in default_cols, (
        f"'description' not in DASHBOARD_DEFAULT_COLUMNS: {default_cols}"
    )


def test_chartinfo_schema_has_certification_fields():
    """ChartInfo Pydantic model has certified_by and certification_details fields (fail_to_pass)."""
    chart_schemas = REPO / "superset/mcp_service/chart/schemas.py"
    field_names = _extract_class_fields(chart_schemas, "ChartInfo")

    assert len(field_names) > 0, "ChartInfo class not found or has no fields"
    assert "certified_by" in field_names, (
        f"'certified_by' not in ChartInfo fields: {field_names}"
    )
    assert "certification_details" in field_names, (
        f"'certification_details' not in ChartInfo fields: {field_names}"
    )


def test_datasetinfo_schema_has_certification_fields():
    """DatasetInfo Pydantic model has certified_by and certification_details fields (fail_to_pass)."""
    dataset_schemas = REPO / "superset/mcp_service/dataset/schemas.py"
    field_names = _extract_class_fields(dataset_schemas, "DatasetInfo")

    assert len(field_names) > 0, "DatasetInfo class not found or has no fields"
    assert "certified_by" in field_names, (
        f"'certified_by' not in DatasetInfo fields: {field_names}"
    )
    assert "certification_details" in field_names, (
        f"'certification_details' not in DatasetInfo fields: {field_names}"
    )


def test_list_charts_default_columns_constant():
    """list_charts.py DEFAULT_COLUMNS includes certification fields (fail_to_pass)."""
    list_charts_path = REPO / "superset/mcp_service/chart/tool/list_charts.py"
    content = list_charts_path.read_text()

    # The fix adds these fields to the DEFAULT_COLUMNS constant
    assert '"certified_by"' in content, (
        "'certified_by' not found in list_charts.py DEFAULT_COLUMNS"
    )
    assert '"certification_details"' in content, (
        "'certification_details' not found in list_charts.py DEFAULT_COLUMNS"
    )


def test_list_datasets_default_columns_constant():
    """list_datasets.py DEFAULT_COLUMNS includes certification fields (fail_to_pass)."""
    list_datasets_path = REPO / "superset/mcp_service/dataset/tool/list_datasets.py"
    content = list_datasets_path.read_text()

    assert '"certified_by"' in content, (
        "'certified_by' not found in list_datasets.py DEFAULT_COLUMNS"
    )
    assert '"certification_details"' in content, (
        "'certification_details' not found in list_datasets.py DEFAULT_COLUMNS"
    )


def test_list_dashboards_default_columns_constant():
    """list_dashboards.py DEFAULT_COLUMNS includes certification fields (fail_to_pass)."""
    list_dashboards_path = REPO / "superset/mcp_service/dashboard/tool/list_dashboards.py"
    content = list_dashboards_path.read_text()

    assert '"certified_by"' in content, (
        "'certified_by' not found in list_dashboards.py DEFAULT_COLUMNS"
    )
    assert '"certification_details"' in content, (
        "'certification_details' not found in list_dashboards.py DEFAULT_COLUMNS"
    )


def test_chart_extra_columns_has_certification():
    """CHART_EXTRA_COLUMNS includes certified_by metadata (fail_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    extra_cols = _extract_dict_keys(schema_discovery, "CHART_EXTRA_COLUMNS")

    assert len(extra_cols) > 0, "CHART_EXTRA_COLUMNS not found or empty"
    assert "certified_by" in extra_cols, (
        f"'certified_by' not in CHART_EXTRA_COLUMNS: {extra_cols}"
    )
    assert "certification_details" in extra_cols, (
        f"'certification_details' not in CHART_EXTRA_COLUMNS: {extra_cols}"
    )


def test_dataset_extra_columns_has_certification():
    """DATASET_EXTRA_COLUMNS includes certified_by metadata (fail_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    extra_cols = _extract_dict_keys(schema_discovery, "DATASET_EXTRA_COLUMNS")

    assert len(extra_cols) > 0, "DATASET_EXTRA_COLUMNS not found or empty"
    assert "certified_by" in extra_cols, (
        f"'certified_by' not in DATASET_EXTRA_COLUMNS: {extra_cols}"
    )
    assert "certification_details" in extra_cols, (
        f"'certification_details' not in DATASET_EXTRA_COLUMNS: {extra_cols}"
    )


def test_chart_serializer_includes_certification():
    """serialize_chart_object function includes certified_by extraction (fail_to_pass)."""
    chart_schemas = REPO / "superset/mcp_service/chart/schemas.py"
    content = chart_schemas.read_text()

    # The serializer should extract certified_by from the chart object
    assert 'certified_by=getattr(chart, "certified_by"' in content, (
        "serialize_chart_object does not extract certified_by"
    )
    assert 'certification_details=getattr(chart, "certification_details"' in content, (
        "serialize_chart_object does not extract certification_details"
    )


def test_dataset_serializer_includes_certification():
    """serialize_dataset_object function includes certified_by extraction (fail_to_pass)."""
    dataset_schemas = REPO / "superset/mcp_service/dataset/schemas.py"
    content = dataset_schemas.read_text()

    # The serializer should extract certified_by from the dataset object
    assert 'certified_by=getattr(dataset, "certified_by"' in content, (
        "serialize_dataset_object does not extract certified_by"
    )
    assert 'certification_details=getattr(dataset, "certification_details"' in content, (
        "serialize_dataset_object does not extract certification_details"
    )


# =============================================================================
# PASS-TO-PASS TESTS
# These tests should pass both before and after the fix.
# =============================================================================


def test_python_syntax_mcp_service():
    """Python syntax check for modified MCP service files (pass_to_pass)."""
    files_to_check = [
        "superset/mcp_service/chart/schemas.py",
        "superset/mcp_service/chart/tool/list_charts.py",
        "superset/mcp_service/common/schema_discovery.py",
        "superset/mcp_service/dashboard/tool/list_dashboards.py",
        "superset/mcp_service/dataset/schemas.py",
        "superset/mcp_service/dataset/tool/list_datasets.py",
        "superset/mcp_service/mcp_core.py",
    ]

    for filepath in files_to_check:
        full_path = REPO / filepath
        assert full_path.exists(), f"File not found: {filepath}"

        result = subprocess.run(
            ["python3", "-m", "py_compile", str(full_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Syntax error in {filepath}:\n{result.stderr}"
        )


def test_schema_discovery_parses():
    """schema_discovery.py parses as valid Python AST (pass_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    content = schema_discovery.read_text()

    # Should parse without errors
    tree = ast.parse(content)
    assert tree is not None


def test_chart_default_columns_has_required_fields():
    """CHART_DEFAULT_COLUMNS always includes id, slice_name, viz_type (pass_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    default_cols = _extract_module_level_assignment(schema_discovery, "CHART_DEFAULT_COLUMNS")

    assert default_cols is not None, "CHART_DEFAULT_COLUMNS not found"
    assert "id" in default_cols, "'id' must be in CHART_DEFAULT_COLUMNS"
    assert "slice_name" in default_cols, "'slice_name' must be in CHART_DEFAULT_COLUMNS"
    assert "viz_type" in default_cols, "'viz_type' must be in CHART_DEFAULT_COLUMNS"


def test_dataset_default_columns_has_required_fields():
    """DATASET_DEFAULT_COLUMNS always includes id, table_name, schema (pass_to_pass)."""
    schema_discovery = REPO / "superset/mcp_service/common/schema_discovery.py"
    default_cols = _extract_module_level_assignment(schema_discovery, "DATASET_DEFAULT_COLUMNS")

    assert default_cols is not None, "DATASET_DEFAULT_COLUMNS not found"
    assert "id" in default_cols, "'id' must be in DATASET_DEFAULT_COLUMNS"
    assert "table_name" in default_cols, "'table_name' must be in DATASET_DEFAULT_COLUMNS"
    assert "schema" in default_cols, "'schema' must be in DATASET_DEFAULT_COLUMNS"


def test_chartinfo_has_core_fields():
    """ChartInfo Pydantic model has core fields like id, slice_name (pass_to_pass)."""
    chart_schemas = REPO / "superset/mcp_service/chart/schemas.py"
    field_names = _extract_class_fields(chart_schemas, "ChartInfo")

    assert len(field_names) > 0, "ChartInfo class not found or has no fields"
    assert "id" in field_names, "'id' must be in ChartInfo fields"
    assert "slice_name" in field_names, "'slice_name' must be in ChartInfo fields"


def test_datasetinfo_has_core_fields():
    """DatasetInfo Pydantic model has core fields like id, table_name (pass_to_pass)."""
    dataset_schemas = REPO / "superset/mcp_service/dataset/schemas.py"
    field_names = _extract_class_fields(dataset_schemas, "DatasetInfo")

    assert len(field_names) > 0, "DatasetInfo class not found or has no fields"
    assert "id" in field_names, "'id' must be in DatasetInfo fields"
    assert "table_name" in field_names, "'table_name' must be in DatasetInfo fields"


def test_chartlike_protocol_exists():
    """ChartLike Protocol exists in chart/schemas.py (pass_to_pass)."""
    chart_schemas = REPO / "superset/mcp_service/chart/schemas.py"
    content = chart_schemas.read_text()

    assert "class ChartLike(Protocol):" in content, "ChartLike Protocol not found"


def test_ruff_check_mcp_service():
    """Ruff linter passes on MCP service files (pass_to_pass)."""
    # Install ruff and run linting check
    result = subprocess.run(
        ["bash", "-c", "pip install -q ruff && ruff check superset/mcp_service/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_format_check_mcp_service():
    """Ruff format check passes on MCP service files (pass_to_pass)."""
    # Install ruff and check formatting
    result = subprocess.run(
        ["bash", "-c", "pip install -q ruff && ruff format --check superset/mcp_service/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff format check failed:\n{result.stdout}\n{result.stderr}"


def test_ruff_check_modified_files():
    """Ruff linter passes on files modified by this PR (pass_to_pass)."""
    modified_files = [
        "superset/mcp_service/chart/schemas.py",
        "superset/mcp_service/chart/tool/list_charts.py",
        "superset/mcp_service/common/schema_discovery.py",
        "superset/mcp_service/dashboard/tool/list_dashboards.py",
        "superset/mcp_service/dataset/schemas.py",
        "superset/mcp_service/dataset/tool/list_datasets.py",
        "superset/mcp_service/mcp_core.py",
    ]
    files_arg = " ".join(modified_files)
    result = subprocess.run(
        ["bash", "-c", f"pip install -q ruff && ruff check {files_arg}"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Ruff check failed on modified files:\n{result.stdout}\n{result.stderr}"
