"""
Tests for the get_chart_type_schema MCP tool.

These tests verify that the tool:
1. Returns JSON schemas for valid chart types
2. Returns examples when include_examples=True (default)
3. Returns error information for invalid chart types
4. Omits examples when include_examples=False
5. Includes all expected chart types (xy, table, pie, pivot_table, mixed_timeseries, handlebars, big_number)
"""

import pytest
import subprocess
import sys

# Path to the superset repo
REPO_PATH = "/workspace/superset"
sys.path.insert(0, REPO_PATH)


class TestGetChartTypeSchema:
    """Test suite for get_chart_type_schema MCP tool."""

    def test_tool_module_exists(self):
        """FAIL-TO-PASS: The tool module must exist."""
        try:
            from superset.mcp_service.chart.tool.get_chart_type_schema import (
                _get_chart_type_schema_impl,
                get_chart_type_schema,
                VALID_CHART_TYPES,
            )
        except ImportError as e:
            pytest.fail(f"get_chart_type_schema module cannot be imported: {e}")

    def test_valid_chart_types_constant_exists(self):
        """FAIL-TO-PASS: VALID_CHART_TYPES must be defined with 7 chart types."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import VALID_CHART_TYPES

        # Must have exactly 7 chart types
        assert len(VALID_CHART_TYPES) == 7, f"Expected 7 chart types, got {len(VALID_CHART_TYPES)}"

        # Must contain all expected types
        expected_types = ["xy", "table", "pie", "pivot_table", "mixed_timeseries", "handlebars", "big_number"]
        for chart_type in expected_types:
            assert chart_type in VALID_CHART_TYPES, f"Missing chart type: {chart_type}"

    @pytest.mark.parametrize("chart_type", ["xy", "table", "pie", "pivot_table", "mixed_timeseries", "handlebars", "big_number"])
    def test_valid_chart_type_returns_schema(self, chart_type):
        """FAIL-TO-PASS: Valid chart types must return a schema dict with properties."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl(chart_type)

        # Must not have error
        assert "error" not in result, f"Got error for valid chart type {chart_type}: {result.get('error')}"

        # Must have chart_type in result
        assert result.get("chart_type") == chart_type, f"Expected chart_type='{chart_type}', got '{result.get('chart_type')}'"

        # Must have schema
        assert "schema" in result, f"Missing 'schema' key in result for {chart_type}"
        schema = result["schema"]
        assert isinstance(schema, dict), f"Schema should be a dict, got {type(schema)}"

        # Schema must have properties
        assert "properties" in schema, f"Schema must have 'properties' for {chart_type}"
        assert isinstance(schema["properties"], dict), f"Schema properties should be a dict"

    @pytest.mark.parametrize("chart_type", ["xy", "pie", "big_number"])
    def test_valid_chart_type_returns_examples(self, chart_type):
        """FAIL-TO-PASS: Valid chart types must return examples by default."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl(chart_type, include_examples=True)

        # Must have examples
        assert "examples" in result, f"Missing 'examples' key for {chart_type}"
        examples = result["examples"]
        assert isinstance(examples, list), f"Examples should be a list, got {type(examples)}"
        assert len(examples) >= 1, f"Should have at least one example for {chart_type}"

        # Each example must have chart_type matching the requested type
        for example in examples:
            assert example.get("chart_type") == chart_type, \
                f"Example chart_type mismatch: expected {chart_type}, got {example.get('chart_type')}"

    def test_include_examples_false_omits_examples(self):
        """FAIL-TO-PASS: When include_examples=False, examples should be omitted."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl("xy", include_examples=False)

        # Must have schema
        assert "schema" in result, "Missing 'schema' key"

        # Must NOT have examples
        assert "examples" not in result, "Should not have 'examples' key when include_examples=False"

    def test_invalid_chart_type_returns_error(self):
        """FAIL-TO-PASS: Invalid chart types must return error with valid_chart_types list."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import (
            _get_chart_type_schema_impl,
            VALID_CHART_TYPES,
        )

        result = _get_chart_type_schema_impl("nonexistent_chart_type")

        # Must have error
        assert "error" in result, "Should have 'error' key for invalid chart type"
        assert "nonexistent_chart_type" in result["error"], f"Error message should mention invalid type: {result['error']}"

        # Must have valid_chart_types
        assert "valid_chart_types" in result, "Should have 'valid_chart_types' key"
        assert result["valid_chart_types"] == VALID_CHART_TYPES, \
            f"valid_chart_types should match VALID_CHART_TYPES constant"

    def test_xy_schema_has_expected_fields(self):
        """PASS-TO-PASS: XY chart schema should have x, y, kind fields."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl("xy")
        schema = result["schema"]
        props = schema["properties"]

        assert "x" in props, "XY schema should have 'x' field"
        assert "y" in props, "XY schema should have 'y' field"
        assert "kind" in props, "XY schema should have 'kind' field"

    def test_table_schema_has_columns(self):
        """PASS-TO-PASS: Table chart schema should have columns field."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl("table")
        schema = result["schema"]
        props = schema["properties"]

        assert "columns" in props, "Table schema should have 'columns' field"

    def test_pie_schema_has_dimension_metric(self):
        """PASS-TO-PASS: Pie chart schema should have dimension and metric fields."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl("pie")
        schema = result["schema"]
        props = schema["properties"]

        assert "dimension" in props, "Pie schema should have 'dimension' field"
        assert "metric" in props, "Pie schema should have 'metric' field"

    def test_big_number_schema_has_metric(self):
        """PASS-TO-PASS: Big number chart schema should have metric field."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import _get_chart_type_schema_impl

        result = _get_chart_type_schema_impl("big_number")
        schema = result["schema"]
        props = schema["properties"]

        assert "metric" in props, "Big number schema should have 'metric' field"

    def test_decorated_tool_function_exists(self):
        """PASS-TO-PASS: The decorated tool function should exist with proper attributes."""
        from superset.mcp_service.chart.tool.get_chart_type_schema import get_chart_type_schema

        # Function should be callable
        assert callable(get_chart_type_schema), "get_chart_type_schema should be callable"

    def test_module_has_license_header(self):
        """PASS-TO-PASS: Module should have Apache license header."""
        import os

        module_path = os.path.join(REPO_PATH, "superset/mcp_service/chart/tool/get_chart_type_schema.py")

        # File must exist
        assert os.path.exists(module_path), f"Module file should exist at {module_path}"

        # Read and check for license header
        with open(module_path, "r") as f:
            content = f.read()

        assert "Licensed to the Apache Software Foundation" in content, \
            "Module should have Apache license header"
        assert "http://www.apache.org/licenses/LICENSE-2.0" in content, \
            "Module should reference Apache License 2.0"


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD tests that should pass on both base and fixed
# =============================================================================

class TestRepoP2P:
    """Pass-to-pass tests: verify repo CI/CD checks pass on both base and after fix."""

    def test_mcp_chart_schemas(self):
        """PASS-TO-PASS: MCP chart schema unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_chart_schemas.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP chart schema tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_chart_utils(self):
        """PASS-TO-PASS: MCP chart utils unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_chart_utils.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP chart utils tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_new_chart_types(self):
        """PASS-TO-PASS: MCP new chart types unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_new_chart_types.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP new chart types tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_big_number_chart(self):
        """PASS-TO-PASS: MCP big number chart unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_big_number_chart.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP big number chart tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_handlebars_chart(self):
        """PASS-TO-PASS: MCP handlebars chart unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_handlebars_chart.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP handlebars chart tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_preview_utils(self):
        """PASS-TO-PASS: MCP preview utils unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/test_preview_utils.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP preview utils tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_caching(self):
        """PASS-TO-PASS: MCP caching unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/test_mcp_caching.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP caching tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_storage(self):
        """PASS-TO-PASS: MCP storage unit tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/test_mcp_storage.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP storage tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_chart_validation_column_normalization(self):
        """PASS-TO-PASS: Chart validation column name normalization tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/validation/test_column_name_normalization.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"Column name normalization tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_chart_validation_runtime(self):
        """PASS-TO-PASS: Chart validation runtime validator tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/chart/validation/test_runtime_validator.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"Runtime validator tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"

    def test_mcp_core_system_tool(self):
        """PASS-TO-PASS: MCP core system tool tests must pass."""
        r = subprocess.run(
            ["python", "-m", "pytest", "tests/unit_tests/mcp_service/system/tool/test_mcp_core.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO_PATH,
        )
        assert r.returncode == 0, f"MCP core system tool tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"
